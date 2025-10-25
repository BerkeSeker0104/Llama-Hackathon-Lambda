from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, ToolMessage
from app.config import GROQ_API_KEY, DEFAULT_MODEL
from typing import List, Dict, Any

class GroqAgent:
    """
    LangChain ChatGroq ile iletişimi yöneten sınıf.
    Daha yapılandırılmış ve temiz bir yaklaşım sunar.
    """
    def __init__(self, model: str = DEFAULT_MODEL):
        if not GROQ_API_KEY:
            raise ValueError("GROQ_API_KEY ortam değişkeni ayarlanmamış!")
        
        # LangChain ChatGroq istemcisi
        self.llm = ChatGroq(
            api_key=GROQ_API_KEY,
            model=model,
            temperature=0.7,
            max_tokens=1024
        )
        self.model = model
        print(f"[Agent Info] GroqAgent (LangChain) başlatıldı. Model: {self.model}")

    def get_response(self, messages: List[Dict[str, Any]], use_tools: bool = True, tools=None):
        """
        Mesaj geçmişini alır ve LangChain ChatGroq'tan yanıt ister.
        
        Args:
            messages: Konuşma geçmişi (dict formatında)
            use_tools: Tool kullanılıp kullanılmayacağı
            tools: LangChain tool nesneleri listesi
        
        Returns:
            Yanıt mesajı (dict formatında)
        """
        try:
            # Dict mesajlarını LangChain message nesnelerine dönüştür
            langchain_messages = self._convert_to_langchain_messages(messages)
            
            # Tool'ları bağla (eğer varsa)
            llm_with_tools = self.llm
            if use_tools and tools:
                llm_with_tools = self.llm.bind_tools(tools)
            
            # LLM'i çağır
            response = llm_with_tools.invoke(langchain_messages)
            
            # LangChain yanıtını dict formatına dönüştür (backward compatibility)
            return self._convert_to_dict(response)

        except Exception as e:
            print(f"[API Hata] LangChain ChatGroq çağrısı başarısız: {e}")
            # Hata durumunda uyumlu bir dict döndür
            return {
                "role": "assistant",
                "content": f"Üzgünüm, bir API hatası oluştu: {e}"
            }
    
    def _convert_to_langchain_messages(self, messages: List[Dict[str, Any]]) -> List:
        """
        Dict formatındaki mesajları LangChain message nesnelerine dönüştürür.
        """
        langchain_messages = []
        
        for msg in messages:
            role = msg.get("role")
            content = msg.get("content", "")
            
            if role == "system":
                langchain_messages.append(SystemMessage(content=content))
            elif role == "user":
                langchain_messages.append(HumanMessage(content=content))
            elif role == "assistant":
                # Assistant mesajında tool_calls olabilir
                if msg.get("tool_calls"):
                    # LangChain AIMessage ile tool_calls'u ekle
                    langchain_messages.append(AIMessage(
                        content=content or "",
                        additional_kwargs={"tool_calls": msg.get("tool_calls")}
                    ))
                else:
                    langchain_messages.append(AIMessage(content=content))
            elif role == "tool":
                # Tool response mesajı
                langchain_messages.append(ToolMessage(
                    content=content,
                    tool_call_id=msg.get("tool_call_id", "")
                ))
        
        return langchain_messages
    
    def _convert_to_dict(self, message) -> Dict[str, Any]:
        """
        LangChain message nesnesini dict formatına dönüştürür (backward compatibility).
        """
        result = {
            "role": "assistant",
            "content": message.content if message.content else ""
        }
        
        # Tool calls varsa ekle
        if hasattr(message, 'additional_kwargs') and message.additional_kwargs.get('tool_calls'):
            result["tool_calls"] = message.additional_kwargs['tool_calls']
        
        return result
