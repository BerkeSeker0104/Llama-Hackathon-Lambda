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

    def handle_message(self, session_id: str, user_prompt: str) -> str:
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
        self.db.save_message(session_id, ai_message_dict)

        # 5. Agent bir tool kullanmak mı istedi?
        if ai_message_dict.get("tool_calls"):
            print("[Orchestrator Log] Tool çağrısı algılandı.")
            
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
                
                # 8. Agent'ı TEKRAR çağır: Bu sefer tool'un sonucuyla birlikte
                # Agent bu sonuca bakıp doğal bir dil yanıtı üretecek
                print("[Orchestrator Log] Tool sonucuyla agent tekrar çağrılıyor.")
                final_messages = self.db.get_chat_history(session_id)
                
                # Bu sefer tool kullanmasına gerek yok
                final_response_message = self.agent.get_response(final_messages, use_tools=False, tools=None)
                final_response_dict = final_response_message
                
                # 9. Agent'ın son nihai yanıtını DB'ye kaydet
                self.db.save_message(session_id, final_response_dict)
                
                return final_response_dict.get("content", "Bir sorun oluştu.")
            
            else:
                # Agent var olmayan bir tool çağırmaya çalışırsa
                error_content = f"Hata: '{function_name}' adında bir tool bulunamadı."
                self.db.save_message(session_id, {"role": "assistant", "content": error_content})
                return error_content
        
        else:
            # Tool çağrısı yoksa, gelen yanıtı doğrudan kullanıcıya döndür
            return ai_message_dict.get("content")
