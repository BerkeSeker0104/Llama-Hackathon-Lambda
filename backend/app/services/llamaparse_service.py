from llama_cloud_services import LlamaParse
from app.config import LLAMAPARSE_API_KEY

class LlamaParseService:
    """
    LlamaParse service - EXACT implementation from prototype Cell 3
    """
    def __init__(self):
        self.api_key = LLAMAPARSE_API_KEY
        if not self.api_key:
            print("Uyarı: LLAMAPARSE_API_KEY bulunamadı. Lütfen .env dosyanızı kontrol edin.")
            self.api_key = None
        
        self.parser = LlamaParse(
            api_key=self.api_key,
            num_workers=4,      # EXACT from prototype
            verbose=True,
            language="tr"       # Türkçe dokümanlar
        )
    
    def parse_pdf(self, file_path: str) -> str:
        """
        PDF'i parse et - EXACT prototip implementation from Cell 3
        
        Args:
            file_path: Path to PDF file
            
        Returns:
            Parsed text content
        """
        print(f"LlamaParse ile '{file_path}' dosyası ayrıştırılıyor...")
        
        try:
            result = self.parser.parse(file_path)
            text_documents = result.get_text_documents(split_by_page=False)
            
            if text_documents:
                # EXACT logic from prototype
                parsed_text = "\n".join([doc.text for doc in text_documents])
                print(f"PDF başarıyla ayrıştırıldı. Toplam {len(parsed_text)} karakter bulundu.")
                return parsed_text
            else:
                raise Exception("PDF'ten metin çıkarılamadı.")
                
        except Exception as e:
            print(f"LlamaParse hatası: {e}")
            raise
