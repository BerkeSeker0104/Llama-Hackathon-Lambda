from app.base_db import BaseDatabase
from app.groq_client import GroqAgent
from app.tools import available_tools, inject_dependencies, get_all_tools
import json

class ChatOrchestrator:
    """
    Kullanıcı girdisi, Veritabanı, Agent (LLM) ve Araçlar (Tools)
    arasındaki tüm akışı yönetir.
    """
    def __init__(self, db_client: BaseDatabase, agent_client: GroqAgent):
        self.db = db_client
        self.agent = agent_client
        print("[Orchestrator Info] ChatOrchestrator başlatıldı.")

    def handle_message(self, session_id: str, user_prompt: str) -> dict:
        """
        Bir kullanıcı mesajını işlemek için tam döngü.
        Tool kullanımını da yönetir.
        """
        
        # 0. Tools'a DB ve session_id erişimi ver
        inject_dependencies(self.db, session_id)
        
        # 0.1 LangChain tools listesini al
        langchain_tools = get_all_tools()
        
        # 1. Kullanıcının yeni mesajını 'user' rolüyle DB'ye kaydet
        self.db.save_message(session_id, {"role": "user", "content": user_prompt})
        
        # 2. Agent'a göndermek için tüm konuşma geçmişini DB'den al
        messages = self.db.get_chat_history(session_id)
        
        # 3. Agent'tan (LLM) bir yanıt iste (LangChain tools ile)
        ai_response_message = self.agent.get_response(messages, use_tools=True, tools=langchain_tools)
        
        # 4. Gelen yanıtı (bu bir tool çağrısı isteği de olsa) DB'ye kaydet
        # LangChain groq_client zaten dict döndürüyor
        ai_message_dict = ai_response_message
        

        # 5. Agent bir tool kullanmak mı istedi?
        # Check if there are tool_calls in the response OR if content contains raw JSON tool calls
        has_tool_calls = ai_message_dict.get("tool_calls") or (
            ai_message_dict.get("content") and 
            ai_message_dict["content"].strip().startswith("[") and 
            "name" in ai_message_dict["content"] and 
            "parameters" in ai_message_dict["content"]
        )
        
        if has_tool_calls:
            print("[Orchestrator Log] Tool çağrısı algılandı.")
            
            # Eğer tool_calls field'ı yoksa ama content'te raw JSON varsa, onu parse et
            if not ai_message_dict.get("tool_calls") and ai_message_dict.get("content"):
                try:
                    # Raw JSON tool calls'i parse et
                    raw_tool_calls = json.loads(ai_message_dict["content"])
                    if isinstance(raw_tool_calls, list) and len(raw_tool_calls) > 0:
                        # LangChain formatına dönüştür
                        ai_message_dict["tool_calls"] = []
                        for tool_call in raw_tool_calls:
                            if "name" in tool_call and "parameters" in tool_call:
                                ai_message_dict["tool_calls"].append({
                                    "id": f"call_{hash(str(tool_call))}",
                                    "type": "function",
                                    "function": {
                                        "name": tool_call["name"],
                                        "arguments": json.dumps(tool_call["parameters"])
                                    }
                                })
                        # Content'i temizle
                        ai_message_dict["content"] = ""
                except json.JSONDecodeError:
                    pass  # Content is not valid JSON tool calls
            
            # Tool çağrısını DB'ye kaydetme - sadece işle ve kullanıcıya anlamlı mesaj göster
            # Raw tool call'ı kullanıcıya gösterme
            
            # TODO: Birden fazla tool çağrısını yönet (şimdilik ilkini al)
            tool_call = ai_message_dict["tool_calls"][0]
            function_name = tool_call["function"]["name"]
            function_args = json.loads(tool_call["function"]["arguments"])
            
            if function_name in available_tools:
                # 6. Eşleşen aracı çalıştır (LangChain tool.invoke())
                tool_object = available_tools[function_name]
                tool_output = tool_object.invoke(function_args)
                
                # 7. Aracın çıktısını 'tool' rolüyle DB'ye kaydet
                tool_message = {
                    "role": "tool",
                    "tool_call_id": tool_call["id"],
                    "name": function_name,
                    "content": tool_output
                }
                self.db.save_message(session_id, tool_message)
                
                # 8. Tool çıktısını parse et ve onay gerekip gerekmediğini kontrol et
                try:
                    tool_result = json.loads(tool_output)
                    requires_confirmation = tool_result.get("requires_confirmation", False)
                    
                    if requires_confirmation:
                        # Onay gerektiren durum - kullanıcıya detaylı bilgi sun
                        confirmation_data = {
                            "tool_name": function_name,
                            "tool_args": function_args,
                            "tool_result": tool_result,
                            "confirmation_type": tool_result.get("confirmation_type", "general")
                        }
                        
                        # Onay mesajı oluştur
                        confirmation_message = self._create_confirmation_message(tool_result, function_name)
                        
                        # Onay gerektiren mesajı DB'ye kaydet
                        self.db.save_message(session_id, {
                            "role": "assistant", 
                            "content": confirmation_message,
                            "requires_confirmation": True,
                            "confirmation_data": confirmation_data
                        })
                        
                        return {
                            "response": confirmation_message,
                            "requires_confirmation": True,
                            "confirmation_data": confirmation_data
                        }
                    else:
                        # Onay gerektirmeyen durum - kullanıcı dostu mesaj oluştur
                        print("[Orchestrator Log] Tool başarıyla tamamlandı, kullanıcı dostu mesaj oluşturuluyor.")
                        
                        # Tool sonucuna göre kullanıcı dostu mesaj oluştur
                        user_friendly_message = self._create_user_friendly_message(tool_result, function_name)
                        
                        # Kullanıcı dostu mesajı DB'ye kaydet
                        self.db.save_message(session_id, {
                            "role": "assistant", 
                            "content": user_friendly_message
                        })
                        
                        return {
                            "response": user_friendly_message,
                            "requires_confirmation": False,
                            "confirmation_data": None
                        }
                        
                except json.JSONDecodeError:
                    # JSON parse hatası - normal akışa devam et
                    print("[Orchestrator Log] Tool çıktısı JSON parse edilemedi, normal akışa devam ediliyor.")
                    
                    # Agent'ı TEKRAR çağır: Bu sefer tool'un sonucuyla birlikte
                    print("[Orchestrator Log] Tool sonucuyla agent tekrar çağrılıyor.")
                    final_messages = self.db.get_chat_history(session_id)
                    
                    # Bu sefer tool kullanmasına gerek yok
                    final_response_message = self.agent.get_response(final_messages, use_tools=False, tools=None)
                    final_response_dict = final_response_message
                    
                    # 9. Agent'ın son nihai yanıtını DB'ye kaydet
                    self.db.save_message(session_id, final_response_dict)
                    
                    return {
                        "response": final_response_dict.get("content", "Bir sorun oluştu."),
                        "requires_confirmation": False,
                        "confirmation_data": None
                    }
            
            else:
                # Agent var olmayan bir tool çağırmaya çalışırsa
                error_content = f"Hata: '{function_name}' adında bir tool bulunamadı."
                self.db.save_message(session_id, {"role": "assistant", "content": error_content})
                return {
                    "response": error_content,
                    "requires_confirmation": False,
                    "confirmation_data": None
                }
        
        else:
            # Tool çağrısı yoksa, gelen yanıtı DB'ye kaydet ve kullanıcıya döndür
            self.db.save_message(session_id, ai_message_dict)
            return {
                "response": ai_message_dict.get("content", "Bir sorun oluştu."),
                "requires_confirmation": False,
                "confirmation_data": None
            }
    
    def _create_user_friendly_message(self, tool_result: dict, function_name: str) -> str:
        """
        Onay gerektirmeyen tool sonucu için kullanıcı dostu mesaj oluşturur.
        """
        if function_name == "assign_task_to_employee":
            if tool_result.get("status") == "success":
                task_title = tool_result.get("task_title", "Bilinmeyen Görev")
                assigned_to = tool_result.get("assigned_to", "Bilinmeyen Kişi")
                reason = tool_result.get("reason", "Belirtilmemiş")
                confidence = tool_result.get("confidence_score", 0.0)
                
                message = f"✅ **Görev Başarıyla Atandı**\n\n"
                message += f"**Görev:** {task_title}\n"
                message += f"**Atanan Kişi:** {assigned_to}\n"
                message += f"**Atama Gerekçesi:** {reason}\n"
                message += f"**Güven Skoru:** %{confidence*100:.0f}\n\n"
                message += "Görev başarıyla atandı ve ilgili kişiye bildirildi."
                
                return message
            else:
                return f"❌ Görev ataması sırasında bir hata oluştu: {tool_result.get('error', 'Bilinmeyen hata')}"
        
        elif function_name == "list_tasks":
            tasks = tool_result.get("tasks", [])
            if tasks:
                message = f"📋 **Görev Listesi** ({len(tasks)} görev)\n\n"
                for i, task in enumerate(tasks[:10], 1):  # İlk 10 görevi göster
                    status_emoji = "✅" if task.get("status") == "completed" else "⏳" if task.get("status") == "in_progress" else "📝"
                    assigned_to = task.get("assigned_to", "Atanmamış")
                    message += f"{i}. {status_emoji} **{task.get('title', 'Başlıksız')}**\n"
                    message += f"   📅 Durum: {task.get('status', 'Bilinmeyen')}\n"
                    message += f"   👤 Atanan: {assigned_to}\n"
                    if task.get('department'):
                        message += f"   🏢 Departman: {task.get('department')}\n"
                    message += "\n"
                
                if len(tasks) > 10:
                    message += f"... ve {len(tasks) - 10} görev daha"
                
                return message
            else:
                return "📋 Henüz hiç görev bulunmuyor."
        
        elif function_name == "list_employees":
            employees = tool_result.get("employees", [])
            if employees:
                message = f"👥 **Çalışan Listesi** ({len(employees)} kişi)\n\n"
                for i, emp in enumerate(employees[:10], 1):  # İlk 10 çalışanı göster
                    workload_emoji = "🟢" if emp.get("currentWorkload") == "low" else "🟡" if emp.get("currentWorkload") == "medium" else "🔴"
                    message += f"{i}. {workload_emoji} **{emp.get('firstName', '')} {emp.get('lastName', '')}**\n"
                    message += f"   🏢 Departman: {emp.get('department', 'Bilinmeyen')}\n"
                    message += f"   💼 İş Yükü: {emp.get('currentWorkload', 'Bilinmeyen')}\n"
                    if emp.get('techStack'):
                        techs = emp.get('techStack', [])[:3]  # İlk 3 teknoloji
                        message += f"   🛠️ Teknolojiler: {', '.join(techs)}\n"
                    message += "\n"
                
                if len(employees) > 10:
                    message += f"... ve {len(employees) - 10} çalışan daha"
                
                return message
            else:
                return "👥 Henüz hiç çalışan bulunmuyor."
        
        elif function_name == "list_projects":
            projects = tool_result.get("projects", [])
            if projects:
                message = f"📁 **Proje Listesi** ({len(projects)} proje)\n\n"
                for i, project in enumerate(projects, 1):
                    status_emoji = "🟢" if project.get("status") == "active" else "🔴" if project.get("status") == "completed" else "🟡"
                    message += f"{i}. {status_emoji} **{project.get('name', 'Başlıksız')}**\n"
                    message += f"   📅 Durum: {project.get('status', 'Bilinmeyen')}\n"
                    if project.get('description'):
                        message += f"   📝 Açıklama: {project.get('description')[:100]}{'...' if len(project.get('description', '')) > 100 else ''}\n"
                    message += "\n"
                
                return message
            else:
                return "📁 Henüz hiç proje bulunmuyor."
        
        else:
            # Genel durum - tool sonucunu olduğu gibi göster
            return f"✅ İşlem tamamlandı: {function_name}"
    
    def _create_confirmation_message(self, tool_result: dict, function_name: str) -> str:
        """
        Onay gerektiren tool sonucu için kullanıcı dostu mesaj oluşturur.
        """
        if function_name == "assign_task_to_employee":
            task_title = tool_result.get("task_title", "Bilinmeyen Görev")
            assigned_to = tool_result.get("assigned_to", "Bilinmeyen Kişi")
            reason = tool_result.get("reason", "Belirtilmemiş")
            confidence = tool_result.get("confidence_score", 0.0)
            alternatives = tool_result.get("alternatives", [])
            risks = tool_result.get("potential_risks", [])
            
            message = f"**Görev Ataması Önerisi**\n\n"
            message += f"**Görev:** {task_title}\n"
            message += f"**Önerilen Kişi:** {assigned_to}\n"
            message += f"**Gerekçe:** {reason}\n"
            message += f"**Güven Skoru:** %{confidence*100:.0f}\n\n"
            
            if alternatives:
                message += "**Alternatif Adaylar:**\n"
                for i, alt in enumerate(alternatives[:3], 1):
                    message += f"{i}. {alt['name']} - {alt['reason']}\n"
                message += "\n"
            
            if risks:
                message += "**Potansiyel Riskler:**\n"
                for risk in risks:
                    message += f"• {risk}\n"
                message += "\n"
            
            message += "Bu atamayı onaylıyor musunuz?"
            
        elif function_name == "reassign_task_to_employee":
            task_title = tool_result.get("task_title", "Bilinmeyen Görev")
            new_assignee = tool_result.get("new_assignee", "Bilinmeyen Kişi")
            reason = tool_result.get("reason", "Belirtilmemiş")
            cascade_risks = tool_result.get("cascade_risks", [])
            confidence = tool_result.get("confidence_score", 0.0)
            
            message = f"**Görev Yeniden Ataması Önerisi**\n\n"
            message += f"**Görev:** {task_title}\n"
            message += f"**Yeni Atanan:** {new_assignee}\n"
            message += f"**Gerekçe:** {reason}\n"
            message += f"**Güven Skoru:** %{confidence*100:.0f}\n\n"
            
            if cascade_risks:
                message += "**Cascade Etkileri:**\n"
                for risk in cascade_risks:
                    message += f"• {risk}\n"
                message += "\n"
            
            message += "Bu yeniden atamayı onaylıyor musunuz?"
            
        else:
            # Genel onay mesajı
            message = f"**Aksiyon Onayı Gerekli**\n\n"
            message += f"Yapılacak işlem: {function_name}\n"
            message += f"Detaylar: {json.dumps(tool_result, ensure_ascii=False, indent=2)}\n\n"
            message += "Bu işlemi onaylıyor musunuz?"
        
        return message
    
    def handle_confirmation(self, session_id: str, confirmation_data: dict, confirmed: bool) -> str:
        """
        Kullanıcı onayını işler ve gerekli aksiyonu gerçekleştirir.
        """
        try:
            tool_name = confirmation_data.get("tool_name")
            tool_args = confirmation_data.get("tool_args", {})
            tool_result = confirmation_data.get("tool_result", {})
            
            if confirmed:
                # Onay verildi - tool'u çalıştır
                if tool_name in available_tools:
                    tool_object = available_tools[tool_name]
                    
                    # Tool'u tekrar çalıştır (bu sefer gerçekten uygula)
                    tool_output = tool_object.invoke(tool_args)
                    
                    # Sonucu DB'ye kaydet
                    self.db.save_message(session_id, {
                        "role": "tool",
                        "name": tool_name,
                        "content": tool_output
                    })
                    
                    # Agent'a sonucu gönder ve final yanıt al
                    messages = self.db.get_chat_history(session_id)
                    final_response = self.agent.get_response(messages, use_tools=False, tools=None)
                    self.db.save_message(session_id, final_response)
                    
                    return final_response.get("content", "Aksiyon başarıyla gerçekleştirildi.")
                else:
                    return "Hata: Tool bulunamadı."
            else:
                # Onay reddedildi - alternatif öneriler sun
                if tool_name == "assign_task_to_employee":
                    alternatives = tool_result.get("alternatives", [])
                    if alternatives:
                        message = "**Görev Ataması Reddedildi**\n\n"
                        message += "Anladım, bu atamayı onaylamıyorsunuz.\n\n"
                        message += "**Alternatif Seçenekler:**\n"
                        for i, alt in enumerate(alternatives[:3], 1):
                            message += f"{i}. {alt['name']} - {alt['reason']}\n"
                        message += "\nHangi alternatifi tercih edersiniz veya başka bir öneriniz var mı?"
                    else:
                        message = "**Görev Ataması Reddedildi**\n\nAnladım, bu atamayı onaylamıyorsunuz. Başka bir yaklaşım önerebilir misiniz?"
                else:
                    message = "**Aksiyon Reddedildi**\n\nAnladım, bu işlemi onaylamıyorsunuz. Başka nasıl yardımcı olabilirim?"
                
                self.db.save_message(session_id, {"role": "assistant", "content": message})
                return message
                
        except Exception as e:
            error_message = f"Onay işleme hatası: {str(e)}"
            self.db.save_message(session_id, {"role": "assistant", "content": error_message})
            return error_message
