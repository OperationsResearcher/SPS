import requests
import time
import threading

URL = "https://sps.kalitesoleni.com/auth/login" # Test edilecek adres
TOTAL_REQUESTS = 50  # Kaç kere vuracağız?
CONCURRENT_THREADS = 10 # Aynı anda kaç kişi saldıracak?

def hit_server(i):
    try:
        start = time.time()
        response = requests.get(URL)
        end = time.time()
        
        if response.status_code == 200:
            print(f"✅ İstek {i}: BAŞARILI ({end-start:.2f}sn)")
        elif response.status_code == 429:
            print(f"❌ İstek {i}: ENGELLENDİ (Rate Limit!)")
        else:
            print(f"⚠️ İstek {i}: Durum Kodu {response.status_code}")
    except Exception as e:
        print(f"🔥 İstek {i}: HATA - {e}")

print(f"🚀 SALDIRI BAŞLIYOR: {URL}")
print("-" * 30)

threads = []
for i in range(TOTAL_REQUESTS):
    t = threading.Thread(target=hit_server, args=(i,))
    threads.append(t)
    t.start()
    # Biraz bekleme payı bırakmayalım, sunucuyu zorlayalım
    if i % CONCURRENT_THREADS == 0:
        time.sleep(0.1) 

for t in threads:
    t.join()

print("-" * 30)
print("🏁 TEST TAMAMLANDI.")
