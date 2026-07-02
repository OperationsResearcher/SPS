import os
from playwright.sync_api import sync_playwright

def compile_pdf():
    html_path = os.path.abspath("docs/user_guide_master.html")
    pdf_path = os.path.abspath("docs/kokpitim_master_kullanim_kilavuzu.pdf")
    
    print("PDF derleme baslatiliyor...")
    print(f"Kaynak HTML: {html_path}")
    print(f"Hedef PDF: {pdf_path}")
    
    with sync_playwright() as p:
        print("Chromium baslatiliyor...")
        browser = p.chromium.launch(headless=True)
        try:
            page = browser.new_page()
            
            # HTML dosyasını yerel file:// protokolü üzerinden yükle
            # Windows dosya yolu formatını normalize et
            normalized_path = html_path.replace("\\", "/")
            if not normalized_path.startswith("/"):
                normalized_path = "/" + normalized_path
                
            file_url = f"file://{normalized_path}"
            print(f"Dosya yukleniyor: {file_url}")
            page.goto(file_url)
            page.wait_for_load_state("networkidle")
            
            print("PDF olusturuluyor...")
            page.pdf(
                path=pdf_path,
                format="A4",
                print_background=True,
                margin={"top": "20mm", "bottom": "20mm", "left": "15mm", "right": "15mm"}
            )
            # Hata yutma YOK: dosya gerçekten oluştu mu doğrula (yoksa çağıran 'done' demesin).
            if not os.path.exists(pdf_path) or os.path.getsize(pdf_path) == 0:
                raise RuntimeError(f"PDF derlendi ama dosya oluşmadı/boş: {pdf_path}")
            print(f"PDF basariyla olusturuldu ve kaydedildi: {pdf_path}")
        finally:
            browser.close()

if __name__ == "__main__":
    compile_pdf()
