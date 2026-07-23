# -*- coding: utf-8 -*-
"""Admin modülü kart açıklamaları — 83 kart (admin_* önekleri).

Yazım sözleşmesi için bkz. card_descriptions_k_radar.py başlığı.
Kod bağlamı 2026-07-21'de 4 paralel keşif ajanıyla çıkarıldı (dosya:satır kanıtlı).

Koddan doğrulanmış ortak notlar:
  - Yönetim paneli giriş sayaçları AuditLog'daki LOGIN kayıtlarını sayar
    (genel aktiviteyi değil); "çevrimiçi" = son 30 dk içinde giriş yapıp
    çıkış kaydı olmayan kullanıcı (heartbeat yok).
  - "Toplam kullanıcı" iki sayfada FARKLI hesaplanır: kurumlar sayfası yalnız
    aktifleri, kullanıcılar sayfası aktif+pasif hepsini sayar.
"""

DESCRIPTIONS: dict[str, str] = {

    # ─────────────────── ADMİN YÖNETİM PANELİ ───────────────────

    "admin_yonetim_paneli.bakim_modu": (
        "Sistem bakım modunu açıp kapatır (yalnız sistem yöneticisi görür).\n"
        "\n"
        "Hesap: Anahtar, veritabanındaki bakım bayrağını değiştirir. Açıkken yönetici "
        "dışındaki kullanıcılar bakım sayfası görür; giriş sayfası açık kalır, yönetici "
        "normal çalışmaya devam eder.\n"
        "\n"
        "Sınır: Sunucu ortam değişkenleri bu anahtarı EZEBİLİR — zorla-açık veya zorla-kapalı "
        "kilidi varsa kutu kilitlenir ve uyarı gösterilir.\n"
        "\n"
        "Yorum: Bakımı açmadan önce aktif kullanıcıları 'çevrimiçi' kartından kontrol edin; "
        "kaydedilmemiş çalışmalar bakım ekranına düşen kullanıcıda kalır."
    ),

    "admin_yonetim_paneli.kurum_secimi": (
        "Panel kartlarının hangi kurum için hesaplanacağını seçtirir; sistem yöneticisi "
        "'tüm kurumlar' seçeneğini de görür.\n"
        "\n"
        "Sınır: Kullanıcı durumu tablosu tek kurum seçiliyken çalışır — 'tüm kurumlar' "
        "modunda kurum seçmeniz istenir.\n"
        "\n"
        "Yorum: Sayılar beklenmedik görünüyorsa önce hangi kurumun seçili olduğunu kontrol "
        "edin."
    ),

    "admin_yonetim_paneli.cevrimici": (
        "Şu anda çevrimiçi kabul edilen tekil kullanıcı sayısını gösterir.\n"
        "\n"
        "Hesap: Son 30 dakika içinde giriş yapmış VE o girişten sonra çıkış kaydı olmayan "
        "kullanıcılar sayılır (denetim günlüğündeki giriş/çıkış kayıtlarından).\n"
        "\n"
        "Sınır: Kalp atışı (heartbeat) izlenmez — 30 dakikadan uzun süredir açık oturumlar "
        "'çevrimiçi' sayılmaz; sekmeyi kapatıp çıkış yapmayanlar 30 dakika boyunca çevrimiçi "
        "görünür.\n"
        "\n"
        "Yorum: Sayıyı anlık kesin mevcut değil, 'son yarım saatin aktif kullanıcıları' "
        "olarak okuyun."
    ),

    "admin_yonetim_paneli.aktif_hesap": (
        "Kayıtlı ve etkin (aktif) kullanıcı hesabı sayısını gösterir.\n"
        "\n"
        "Hesap: Hesabı aktif durumda olan kullanıcılar sayılır; seçili kuruma filtrelenir.\n"
        "\n"
        "Sınır: Başlıktaki 'aktif', AKTİVİTE değil hesap durumudur — kullanıcının giriş "
        "yapıp yapmadığını söylemez; o bilgi yandaki giriş sayaçlarındadır.\n"
        "\n"
        "Yorum: Bu sayı lisans/kapasite takibinin temelidir; giriş sayaçlarıyla farkı "
        "'kayıtlı ama kullanmayan' kitleyi verir."
    ),

    "admin_yonetim_paneli.son_24_saat": (
        "Son 24 saatte en az bir kez giriş yapan tekil kullanıcı sayısını gösterir.\n"
        "\n"
        "Hesap: Denetim günlüğündeki GİRİŞ kayıtlarından tekil kullanıcı sayılır.\n"
        "\n"
        "Sınır: Giriş sayılır, aktivite değil — sabah girip gün boyu çalışan kullanıcı ile "
        "girip hemen çıkan aynı ağırlıktadır.\n"
        "\n"
        "Yorum: Günlük nabız göstergesidir; hafta içi/hafta sonu farkını bilerek okuyun."
    ),

    "admin_yonetim_paneli.son_7_gun": (
        "Son 7 günde en az bir kez giriş yapan tekil kullanıcı sayısını gösterir.\n"
        "\n"
        "Hesap: Denetim günlüğündeki GİRİŞ kayıtlarından tekil kullanıcı sayılır.\n"
        "\n"
        "Yorum: Haftalık aktif kullanıcı (WAU) karşılığıdır; aktif hesap sayısına bölerek "
        "benimseme oranını izleyebilirsiniz."
    ),

    "admin_yonetim_paneli.son_30_gun": (
        "Son 30 günde en az bir kez giriş yapan tekil kullanıcı sayısını gösterir.\n"
        "\n"
        "Hesap: Denetim günlüğündeki GİRİŞ kayıtlarından tekil kullanıcı sayılır.\n"
        "\n"
        "Yorum: Aylık aktif kullanıcı (MAU) karşılığıdır — aktif hesap sayısıyla arasındaki "
        "makas, sistemin kağıt üzerinde mi fiilen mi kullanıldığının en net ölçüsüdür."
    ),

    "admin_yonetim_paneli.tum_zamanlar": (
        "Kayıtların başından bu yana en az bir kez giriş yapmış tekil kullanıcı sayısını "
        "gösterir.\n"
        "\n"
        "Hesap: Denetim günlüğündeki tüm GİRİŞ kayıtlarından tekil kullanıcı sayılır.\n"
        "\n"
        "Sınır: 'Tüm zamanlar' fiilen günlük saklama süresiyle sınırlıdır — eski kayıtlar "
        "temizlendiyse sayı gerçekte olandan düşük kalır.\n"
        "\n"
        "Yorum: Aktif hesap sayısından belirgin düşükse, hiç giriş yapmamış hesaplar "
        "birikiyor demektir — loglar sayfasındaki ilgili listeye bakın."
    ),

    "admin_yonetim_paneli.kullanici_durumu": (
        "Seçili kurumun kullanıcılarını durum tablosunda listeler: çevrimiçi rozeti, rol, "
        "son giriş, son 30 gün giriş sayısı ve son 30 gün işlem sayısı.\n"
        "\n"
        "Hesap: Çevrimiçi = son 30 dk içinde giriş yapıp çıkmamış; 30G işlem = denetim "
        "günlüğündeki tüm olaylar (güvenlik kayıtları hariç).\n"
        "\n"
        "Sınır: 'İşlem' sayacı giriş/çıkış dahil tüm günlük olaylarını sayar — saf iş "
        "aktivitesi değildir. Tablo yalnız TEK kurum seçiliyken dolar.\n"
        "\n"
        "Yorum: 'Son giriş var ama işlem yok' deseni pasif izleyici kullanıcıyı, 'hiç giriş "
        "yok' satırları eğitim/aktivasyon ihtiyacını gösterir."
    ),

    "admin_yonetim_paneli.son_aktiviteler": (
        "Sistemdeki son denetim günlüğü kayıtlarını listeler: kaynak, kullanıcı, işlem ve "
        "zaman.\n"
        "\n"
        "Hesap: En yeni kayıtlar gösterilir (varsayılan 50, en fazla 200); güvenlik tipli "
        "kayıtlar bu listeden hariç tutulur.\n"
        "\n"
        "Sınır: 'Tüm kurumlar' seçiliyken bütün kurumların aktivitesi karışık akar; güvenlik "
        "olayları (giriş denemeleri vb.) burada görünmez.\n"
        "\n"
        "Yorum: Bu akış operasyonel nabızdır; şüpheli işlem araştırması için loglar "
        "sayfasındaki filtreli görünümleri kullanın."
    ),

    # ─────────────────── ADMİN KURUMLAR ───────────────────

    "admin_tenants.toplam_kurum": (
        "Sistemdeki toplam kurum sayısını gösterir (aktif + arşivlenmiş).\n"
        "\n"
        "Sınır: Sistem yöneticisi tüm kurumları görür; kurum yöneticisi yalnızca kendi "
        "kurumunu görür (sayı 1 olur).\n"
        "\n"
        "Yorum: Aktif ve arşivlenmiş kartlarıyla birlikte okunduğunda müşteri tabanının "
        "büyüme/kayıp fotoğrafını verir."
    ),

    "admin_tenants.aktif_kurum": (
        "Aktif durumdaki kurum sayısını gösterir.\n"
        "\n"
        "Hesap: Listelenen kurumlardan hesabı etkin olanlar sayılır.\n"
        "\n"
        "Yorum: Faturalama ve kapasite planlamasının temel sayısıdır."
    ),

    "admin_tenants.arsivlenmis_kurum": (
        "Arşivlenmiş (pasif) kurum sayısını gösterir.\n"
        "\n"
        "Hesap: Listelenen kurumlardan hesabı pasif olanlar sayılır.\n"
        "\n"
        "Sınır: Arşivleme soft-delete'tir — veri silinmez, kurum erişime kapanır.\n"
        "\n"
        "Yorum: Arşiv sayısının artış hızı müşteri kaybı (churn) sinyalidir; arşivlenen "
        "kurumların verisi saklama politikanıza göre periyodik değerlendirilmelidir."
    ),

    "admin_tenants.toplam_kullanici": (
        "Listelenen kurumlardaki AKTİF kullanıcıların toplamını gösterir.\n"
        "\n"
        "Hesap: Kurum başına aktif kullanıcılar sayılıp toplanır.\n"
        "\n"
        "Sınır: Adı 'toplam' dese de PASİF kullanıcılar DAHİL DEĞİLDİR; kullanıcılar "
        "sayfasındaki aynı adlı kart ise aktif+pasif herkesi sayar — iki sayfa farklı sayı "
        "gösterebilir, ikisi de kendi tanımında doğrudur.\n"
        "\n"
        "Yorum: Kurum başına kullanıcı yoğunluğunu (toplam kullanıcı / aktif kurum) izlemek, "
        "paket üst sınırlarına yaklaşan kurumları erken gösterir."
    ),

    "admin_tenants.kurum_listesi": (
        "Kurumları tablo halinde listeler: ad, tip (holding/bayi/alt kurum), sektör, "
        "abonelik paketi, lisans bitişi, kullanıcı üst sınırı, durum ve işlemler.\n"
        "\n"
        "Sınır: Hiyerarşi alanları ve tüm kurumların görünümü yalnız sistem yöneticisine "
        "açıktır; kullanıcı üst sınırı boşsa varsayılan (5) gösterilir.\n"
        "\n"
        "Yorum: Lisans bitişi yaklaşan ve kullanıcı sınırına dayanan kurumlar, iletişime "
        "geçilecek ilk satırlardır."
    ),

    # ─────────────────── ADMİN KULLANICILAR ───────────────────

    "admin_users.arama_filtre": (
        "Kullanıcı listesini ad, e-posta, rol ve kurum bilgisi üzerinden anında filtreler; "
        "sistem yöneticisi kurum bazlı da daraltabilir.\n"
        "\n"
        "Sınır: Filtre tarayıcı tarafında, ekrana yüklenmiş liste üzerinde çalışır.\n"
        "\n"
        "Yorum: Eşleşme sayacı, aradığınız kullanıcının hiç mi yok yoksa farklı yazımla mı "
        "kayıtlı olduğunu hızlıca gösterir."
    ),

    "admin_users.toplam_kullanici": (
        "Listelenen tüm kullanıcıların sayısını gösterir — aktif ve pasif dahil.\n"
        "\n"
        "Sınır: Kurumlar sayfasındaki aynı adlı kart YALNIZ aktifleri sayar; iki sayfa "
        "arasındaki fark pasif kullanıcı sayısıdır.\n"
        "\n"
        "Yorum: Aktif/pasif kartlarıyla birlikte okunduğunda hesap yaşam döngüsünün "
        "fotoğrafını verir."
    ),

    "admin_users.aktif_kullanici": (
        "Hesabı etkin durumda olan kullanıcı sayısını gösterir.\n"
        "\n"
        "Sınır: 'Aktif' hesap durumudur — çevrimiçi olmayı veya yakın zamanda giriş yapmayı "
        "ölçmez.\n"
        "\n"
        "Yorum: Fiilî kullanım için yönetim panelindeki giriş sayaçlarına bakın."
    ),

    "admin_users.pasif_kullanici": (
        "Pasife alınmış kullanıcı hesabı sayısını gösterir.\n"
        "\n"
        "Sınır: Pasifleştirme soft-delete'tir — kullanıcının geçmiş kayıtları korunur, "
        "girişi engellenir.\n"
        "\n"
        "Yorum: Ayrılan personelin hesabını silmek yerine pasife almak, geçmiş verinin "
        "('kim girdi' izlerinin) bütünlüğünü korur."
    ),

    "admin_users.kullanici_listesi": (
        "Kullanıcıları tablo halinde listeler: ad soyad, e-posta, rol, kurum (sistem "
        "yöneticisine), durum ve işlemler; sütunlar sıralanabilir.\n"
        "\n"
        "Sınır: Düzenleme/pasife alma yetkisi role bağlıdır; atanabilir roller de yetkiye "
        "göre daralır.\n"
        "\n"
        "Yorum: Rol dağılımını ara ara gözden geçirin — geniş yetkili rol sayısının sessizce "
        "artması en yaygın güvenlik erozyonudur."
    ),

    # ─────────────────── ADMİN HİYERARŞİ ───────────────────

    "admin_hierarchy.sayfa": (
        "Platformun 4 katmanlı yapı ağacını gösteren yönetim aracıdır: Paket → Modül → "
        "Bileşen → Kart → Veri kaynağı; 'Kartları Keşfet' düğmesi ekran şablonlarını "
        "tarayıp yeni kartları kataloğa ekler.\n"
        "\n"
        "Hesap: Keşif, şablonlardaki kart işaretlerini tarar ve sonuçta kaç dosya tarandığı, "
        "kaç yeni kart ve veri kaynağı bulunduğu raporlanır.\n"
        "\n"
        "Sınır: Bu bir metrik kartı değil, kart KATALOĞUNU yöneten sistem yöneticisi "
        "aracıdır; kod deploy'u keşfi otomatik ÇALIŞTIRMAZ — yeni kart eklenen her ortamda "
        "keşif elle tetiklenmelidir.\n"
        "\n"
        "Yorum: Bir ekranda (i) butonu/kart kimliği görünmüyorsa ilk bakılacak yer burasıdır "
        "— keşif çalıştırılmamış olabilir."
    ),

    # ─────────────────── ADMİN HOLDİNG DASHBOARD ───────────────────

    "admin_holding_dashboard.ozet_skor": (
        "Holdingin aktif alt kurumlarının ortalama sağlık skorunu ve toplam kurum, "
        "kullanıcı, gösterge, girişim sayaçlarını gösterir.\n"
        "\n"
        "Hesap: Her alt kurumun sağlık skoru yönetici paneliyle AYNI formülle hesaplanır "
        "(PG hedef üstü %40, veri kapsamı %20, faaliyet zamanlaması %20, kritik risk "
        "yokluğu %10, anomali yokluğu %10); ortalama, skoru hesaplanabilen AKTİF alt "
        "kurumlar üzerinden alınır.\n"
        "\n"
        "Eşik: 75+ yeşil, 50-74 turuncu, altı kırmızı.\n"
        "\n"
        "Sınır: Kapsam yalnızca DOĞRUDAN alt kurumlardır — holdingin kendisi ve torun "
        "kurumlar dahil değildir. Pasif kurumlar sayaçlara girer ama ortalamaya girmez.\n"
        "\n"
        "Yorum: Ortalama, uçları gizler — karşılaştırma grafiğindeki dağılımla birlikte "
        "okuyun."
    ),

    "admin_holding_dashboard.kritik_risk": (
        "Tüm alt kurumlardaki kritik risklerin toplamını gösterir.\n"
        "\n"
        "Hesap: Kurum başına kritik risk (olasılık × etki ≥ 16) sayılır ve toplanır.\n"
        "\n"
        "Yorum: Toplam, hangi kurumdan geldiğini söylemez — kaynağı görmek için ilgili "
        "kurumun detay görünümüne inin."
    ),

    "admin_holding_dashboard.yuksek_anomali": (
        "Tüm alt kurumlardaki yüksek öncelikli gösterge anomalilerinin toplamını gösterir.\n"
        "\n"
        "Hesap: Her kurumda son değeri kendi geçmişinden 3 standart sapma ve üzeri sapan "
        "göstergeler 'yüksek' sayılır; toplamları alınır.\n"
        "\n"
        "Sınır: Kurum başına tarama 100 göstergeyle sınırlıdır; orta seviye (2-3σ) sapmalar "
        "bu sayıya girmez.\n"
        "\n"
        "Yorum: Holding düzeyinde anomali toplamı bir 'bakılmamış sinyal' sayacıdır — "
        "sıfırlanması hedeflenir."
    ),

    "admin_holding_dashboard.gecikmis_faaliyet": (
        "Tüm alt kurumlardaki gecikmiş faaliyetlerin toplamını gösterir.\n"
        "\n"
        "Hesap: Kurum başına, bitiş tarihi geçmiş ve tamamlanmamış faaliyetler sayılıp "
        "toplanır.\n"
        "\n"
        "Yorum: Toplamı kurum sayısına bölerek kurum başına ortalama gecikme yükünü izlemek, "
        "büyüyen holdinglerde daha adil bir kıyas verir."
    ),

    "admin_holding_dashboard.karsilastirma_grafik": (
        "Aktif alt kurumların sağlık skorlarını yan yana çubuklarla karşılaştırır.\n"
        "\n"
        "Eşik: Çubuk rengi — 75+ yeşil, 50-74 turuncu, altı kırmızı.\n"
        "\n"
        "Sınır: Pasif kurumlar grafikte görünmez; skoru hesaplanamayan aktif kurum boş "
        "değerle çizilir.\n"
        "\n"
        "Yorum: Grafiğin değeri sıralamada değil makastadır — en iyi ve en kötü kurum "
        "arasındaki fark açılıyorsa iyi uygulama transferi gündeme alınmalıdır."
    ),

    # ─────────────────── ADMİN HOLDİNG DRILLDOWN ───────────────────

    "admin_holding_drilldown.saglik_skoru": (
        "Seçilen alt kurumun strateji sağlık skorunu ve özet sayılarını gösterir.\n"
        "\n"
        "Hesap: Kurumun kendi yönetici panelindeki sağlık skoruyla BİREBİR AYNI servis ve "
        "formül kullanılır (beş bileşenli ağırlıklı skor) — iki ekran aynı sayıyı gösterir.\n"
        "\n"
        "Eşik: 75+ yeşil, 50-74 turuncu, altı kırmızı.\n"
        "\n"
        "Yorum: Holdingden bakan yönetici ile kurumun kendi yöneticisi aynı rakamı görür — "
        "bu, kurumlar arası skor tartışmasını 'hangi rakam doğru' yerine 'neden düşük' "
        "sorusuna taşır."
    ),

    "admin_holding_drilldown.kpi_hedef_ustu": (
        "Alt kurumun hedefine ulaşan gösterge ölçüm oranını ve veri kapsamını gösterir.\n"
        "\n"
        "Hesap: Hedef üstü % = gerçekleşmesi hedefe eşit/üstü sayısal ölçümler / "
        "karşılaştırılabilir ölçümler × 100.\n"
        "\n"
        "Sınır: Yalnızca sayıya çevrilebilen kayıtlar sayılır; yön farkı gözetilmez "
        "('azalması iyi' göstergeler ters okunabilir — bkz. D0 kaydı).\n"
        "\n"
        "Yorum: Oranı veri kapsamıyla birlikte okuyun — az veri giren kurumun yüksek oranı "
        "temsil gücü taşımaz."
    ),

    "admin_holding_drilldown.girisim_ortalamasi": (
        "Alt kurumun devam eden girişimlerinin ortalama ilerlemesini ve adedini gösterir.\n"
        "\n"
        "Hesap: Yalnızca 'yürütmede' durumundaki girişimlerin ilerleme yüzdeleri "
        "ortalanır.\n"
        "\n"
        "Sınır: Adı 'girişim ortalaması' olsa da planlanan/tamamlanan/bekleyen girişimler "
        "hesaba GİRMEZ; ilerleme değerleri elle girilen beyanlardır.\n"
        "\n"
        "Yorum: Devam eden sayısı 0 iken %0 görünmesi 'kötü' değil 'yürüyen girişim yok' "
        "demektir — durum dağılımına bakın."
    ),

    "admin_holding_drilldown.gecikmis_faaliyet": (
        "Alt kurumun gecikmiş faaliyet sayısını, toplam faaliyetle birlikte gösterir.\n"
        "\n"
        "Hesap: Geciken = bitiş tarihi geçmiş ve tamamlanmamış faaliyetler.\n"
        "\n"
        "Yorum: Holding özetindeki toplamın kurum kırılımı budur; gecikme oranı (geciken / "
        "toplam) kurumlar arası kıyasta mutlak sayıdan daha adildir."
    ),

    "admin_holding_drilldown.kritik_risk": (
        "Alt kurumun kritik risk sayısını ve açık risk toplamını gösterir.\n"
        "\n"
        "Hesap: Kritik = olasılık × etki ≥ 16; açık = kapatılmamış riskler.\n"
        "\n"
        "Yorum: 'Kritik' ve 'açık' farklı tanımlardır — kritik olmayan ama uzun süredir "
        "açık kalan riskler de yönetim ilgisi bekler."
    ),

    "admin_holding_drilldown.yuksek_anomali": (
        "Alt kurumun yüksek öncelikli gösterge anomalisi sayısını (ve orta seviyeyi) "
        "gösterir.\n"
        "\n"
        "Hesap: Son değeri kendi geçmişinden 3σ+ sapan göstergeler 'yüksek', 2-3σ arası "
        "'orta' sayılır (z-skoru, kural tabanlı).\n"
        "\n"
        "Yorum: Anomali kötü performans değil 'açıklanmamış sapma'dır; holding görünümünde "
        "önemi, kurumun kendi fark etmediği sinyali üst yönetimin görebilmesidir."
    ),

    "admin_holding_drilldown.kullanici_senaryo": (
        "Alt kurumun aktif kullanıcı sayısını ve senaryo (plan dalı) sayısını gösterir.\n"
        "\n"
        "Hesap: Senaryo, ana plan yılından dallanmış what-if kopyalarıdır; ana dönemler bu "
        "sayıya girmez.\n"
        "\n"
        "Yorum: Senaryo sayısı, kurumun planlama olgunluğunun küçük ama anlamlı bir "
        "işaretidir — hiç senaryo kurmayan kurum tek gelecek varsayımıyla çalışıyor "
        "demektir."
    ),

    "admin_holding_drilldown.girisimler": (
        "Alt kurumun aktif stratejik girişimlerini listeler: ad, yıl aralığı, durum, "
        "öncelik ve ilerleme.\n"
        "\n"
        "Sınır: En fazla 20 girişim gösterilir (öncelik sırasıyla) — kalabalık portföylerde "
        "düşük öncelikliler listeye girmez. İlerleme elle girilen beyandır.\n"
        "\n"
        "Yorum: Yüksek öncelikli ama düşük ilerlemeli girişimler holding-kurum görüşmesinin "
        "doğal gündemidir."
    ),

    "admin_holding_drilldown.risk_listesi": (
        "Alt kurumun risklerini skor sırasıyla listeler: başlık, olasılık, etki, skor ve "
        "durum.\n"
        "\n"
        "Hesap: Skor = olasılık × etki; 16 ve üzeri kırmızı gösterilir.\n"
        "\n"
        "Sınır: En fazla 20 risk listelenir (skor azalan).\n"
        "\n"
        "Yorum: Holding, benzer risklerin birden çok kurumda tekrarlandığını bu listelerin "
        "karşılaştırmasından görür — ortak azaltım aksiyonu ölçek ekonomisi sağlar."
    ),

    # ─────────────────── ADMİN ALT KURUMLAR ───────────────────

    "admin_sub_tenants.ozet_kart": (
        "Üst kurumun (holding/bayi) aktif alt kurum sayısını ve alt kurum kotasının "
        "doluluğunu gösterir.\n"
        "\n"
        "Hesap: Aktif alt kurumlar sayılır; kota tanımlı değilse sınırsız (∞) gösterilir.\n"
        "\n"
        "Yorum: Kota doluluğu satış/sözleşme konuşmasının erken sinyalidir — sınıra "
        "yaklaşan üst kurumla kota artışı önceden konuşulmalıdır."
    ),

    "admin_sub_tenants.alt_kurum_listesi": (
        "Üst kurumun alt kurumlarını listeler: ad, ilk yönetici e-postası, paket, "
        "kullanıcı sayısı / üst sınır, durum ve yönetim işlemleri.\n"
        "\n"
        "Hesap: 'İlk yönetici', kurumun en eski kayıtlı aktif yöneticisidir.\n"
        "\n"
        "Sınır: Liste yönetimseldir — alt kurumun içeriksel verisi (KPI, risk) burada "
        "görünmez; onun için holding detay görünümünü kullanın.\n"
        "\n"
        "Yorum: Şifre sıfırlama ve aktif/pasif işlemleri buradan yapılır; pasife almak "
        "erişimi keser, veriyi silmez."
    ),

    # ─────────────────── ADMİN ALT KURUM KULLANIMI ───────────────────

    "admin_sub_tenants_usage.ozet_toplam": (
        "Alt kurumların bu ayki toplam kullanımını özetler: kurum, kullanıcı, gösterge "
        "sayıları ile yapay zekâ çağrı ve maliyet toplamları.\n"
        "\n"
        "Hesap: Yapay zekâ tüketimi takvim ayı başından itibaren, yalnızca başarılı "
        "çağrılar üzerinden sayılır.\n"
        "\n"
        "Sınır: 'Kullanım' tek bir birleşik metrik değildir — kullanıcı kotası doluluğu, "
        "kayıt sayıları ve AI tüketimi ayrı boyutlardır.\n"
        "\n"
        "Yorum: Faturalama/yeniden fiyatlama görüşmelerinin veri temeli budur; AI maliyeti "
        "hızla büyüyen kurumlar için BYOK (kendi anahtarı) önerilebilir."
    ),

    "admin_sub_tenants_usage.paket_dagilimi": (
        "Alt kurumların abonelik paketlerine göre dağılımını gösterir (paket → kurum "
        "adedi ve yüzdesi).\n"
        "\n"
        "Sınır: Dağılım KURUM sayısı bazlıdır — kullanıcı sayısı veya gelir bazlı değil; "
        "paketsiz kurumlar '(paket yok)' grubunda toplanır.\n"
        "\n"
        "Yorum: '(paket yok)' dilimi sıfırlanması gereken bir operasyon açığıdır — paketsiz "
        "kurum, yetki/modül sınırları tanımsız çalışıyor demektir."
    ),

    "admin_sub_tenants_usage.detay_tablosu": (
        "Alt kurum başına kullanım detayını tablolar: paket, kullanıcı/üst sınır ve "
        "doluluk yüzdesi, gösterge-girişim-plan yılı sayıları, aylık yapay zekâ çağrı, "
        "token ve maliyeti; altta toplam satırı.\n"
        "\n"
        "Hesap: Doluluk % = kullanıcı sayısı / üst sınır × 100.\n"
        "\n"
        "Eşik: Doluluk %50 altı yeşil, %50-80 turuncu, %80+ kırmızı.\n"
        "\n"
        "Sınır: Gösterge/girişim/plan yılı sayıları YIL FİLTRESİZDİR (tüm aktif kayıtlar) — "
        "yönetici panelindeki yıl bazlı sayılarla birebir örtüşmeyebilir.\n"
        "\n"
        "Yorum: Kırmızı doluluk satırları kota artışı adayları; sıfır AI kullanan kurumlar "
        "ise özellik benimseme görüşmesi adaylarıdır."
    ),

    # ─────────────────── ADMİN PAKETLER ───────────────────

    "admin_packages.abonelik_paketleri": (
        "Platformdaki abonelik paketlerini listeler: ad, kod, açıklama, durum; modül atama "
        "ve düzenleme buradan yapılır.\n"
        "\n"
        "Sınır: Bu platform geneli SaaS kataloğudur (kuruma özel değil); yalnız sistem "
        "yöneticisi erişir.\n"
        "\n"
        "Yorum: Paket-modül atamaları kurumların ekranda ne gördüğünü belirler — atama "
        "değişikliği anında tüm o paketteki kurumları etkiler, mesai dışı yapmak daha "
        "güvenlidir."
    ),

    "admin_packages.sistem_modulleri": (
        "Platformdaki sistem modüllerini listeler: ad, kod, açıklama ve aktif/pasif "
        "durumu.\n"
        "\n"
        "Sınır: Bu modül ENVANTERİDİR — paket-modül eşleştirmesi ayrı panelde yönetilir.\n"
        "\n"
        "Yorum: Bir modülü pasife almak onu TÜM paketlerde kapatır — tekil kurum için "
        "kapatma paket ayarından yapılmalıdır."
    ),

    # ─────────────────── ADMİN İSTATİSTİKLER ───────────────────

    "admin_istatistikler.kurum_dagilim_tablosu": (
        "Her aktif kurumun yapı sayılarını hiyerarşik tabloda gösterir: kullanıcı, "
        "ana/alt strateji, süreç, gösterge, gösterge verisi, proje ve görev; holding "
        "gruplarında ara toplam, altta sistem toplamı.\n"
        "\n"
        "Hesap: Sayımlar kurum bazında gruplanır; grup ara toplamı kök kurum + tüm alt "
        "kurumları (çok seviyeli) kapsar.\n"
        "\n"
        "Sınır: Yalnız aktif kurumlar dahildir. Buradaki hiyerarşi toplaması çok seviyeli "
        "çalışır — holding panosunun tek seviyeli kapsamından farklıdır.\n"
        "\n"
        "Yorum: 'Gösterge var, veri yok' deseni tabloda hemen görünür — kurulumu bitmiş "
        "ama ölçüme başlamamış kurumlar aktivasyon takibinin ilk listesidir."
    ),

    # ─────────────────── ADMİN LOGLAR ───────────────────

    "admin_loglar.toplam_giris": (
        "Sistemdeki tüm kurumların toplam başarılı giriş sayısını gösterir (test kurumu "
        "hariç).\n"
        "\n"
        "Hesap: Denetim günlüğündeki oturum açma kayıtları sayılır; başarısız denemeler "
        "dahil değildir.\n"
        "\n"
        "Sınır: Kümülatif OLAY sayısıdır (tekil kullanıcı değil) ve zaman penceresi "
        "yoktur.\n"
        "\n"
        "Yorum: Tek başına büyüklüğü değil artış hızı anlamlıdır — haftalık artış, platform "
        "kullanım temposunun en basit ölçüsüdür."
    ),

    "admin_loglar.son_giris": (
        "Sisteme en son giriş yapan kişiyi, kurumunu ve zamanını gösterir.\n"
        "\n"
        "Yorum: Anlık canlılık göstergesidir; mesai saatinde saatler öncesini gösteriyorsa "
        "kullanım durmuş veya giriş kayıtları yazılamıyor demektir — ikisi de bakılmaya "
        "değer."
    ),

    "admin_loglar.son_veri_hareketi": (
        "Sistemdeki en son veri değişikliğini gösterir: ne değişti, kim yaptı, ne zaman.\n"
        "\n"
        "Hesap: İki kaynağın en yenisi alınır — denetim günlüğündeki kayıt işlemleri "
        "(oluştur/güncelle/sil) ile gösterge veri girişleri.\n"
        "\n"
        "Sınır: Salt görüntüleme 'hareket' sayılmaz; güvenlik olayları da bu karta "
        "girmez.\n"
        "\n"
        "Yorum: Giriş var ama veri hareketi yoksa kullanıcılar 'bakıyor ama işlemiyor' "
        "demektir — benimseme sorununun tipik deseni."
    ),

    "admin_loglar.hic_giris_yapmamis": (
        "Aktif olduğu hâlde sisteme hiç giriş yapmamış kullanıcı sayısını gösterir.\n"
        "\n"
        "Hesap: Denetim günlüğünde hiçbir oturum açma kaydı bulunmayan aktif hesaplar "
        "sayılır.\n"
        "\n"
        "Yorum: Bu sayı davet/aktivasyon sürecinin başarısını ölçer — hesap açılıp duyuru "
        "yapılmamış kullanıcılar burada birikir."
    ),

    "admin_loglar.hic_giris_yapmamis_kullanicilar": (
        "Hiç giriş yapmamış aktif kullanıcıları kişi kişi listeler: kurum, ad, e-posta ve "
        "rol.\n"
        "\n"
        "Yorum: Listeyi kurum yöneticileriyle paylaşıp hatırlatma turu başlatmak, en ucuz "
        "benimseme aksiyonudur; liste boşsa kutlanacak bir durum var demektir."
    ),

    "admin_loglar.kurum_bazinda": (
        "Her aktif kurum için giriş ve veri hareketi özetini tablolar: son giriş, toplam "
        "giriş, son veri hareketi ve hiç giriş yapmamış kullanıcı sayısı; satıra tıklayınca "
        "kurum detayına gidilir.\n"
        "\n"
        "Eşik: Hiç girmemiş sayısı sıfırsa yeşil, sıfırdan büyükse kırmızı.\n"
        "\n"
        "Sınır: İzole test kurumu tüm sayımlardan hariç tutulur.\n"
        "\n"
        "Yorum: 'Son veri hareketi' sütunu kurumların gerçek kullanım tazeliğini gösterir — "
        "girişi olup veri hareketi eski kurumlar pasif izleyicidir."
    ),

    "admin_loglar.son_hareketler": (
        "Tüm kurumların son giriş ve veri değişikliklerini tek akışta listeler; her satır "
        "tür rozeti (giriş / güvenlik / değişiklik / gösterge verisi) taşır.\n"
        "\n"
        "Hesap: Denetim günlüğü ile gösterge veri girişlerinin birleşiminden en yeni 25 "
        "kayıt gösterilir.\n"
        "\n"
        "Yorum: Bu akış platformun kalp atışıdır; olağan dışı yoğunluk veya sessizlik "
        "anları burada ilk göze çarpar."
    ),

    "admin_loglar.modul_kullanimi": (
        "Son 90 günde hangi modülde ne kadar İŞ yapıldığını özetler: modül başına işlem "
        "sayısı ve tekil kullanıcı.\n"
        "\n"
        "Hesap: Denetim günlüğündeki kayıt işlemleri modül (kaynak türü) bazında sayılır; "
        "güvenlik olayları hariçtir.\n"
        "\n"
        "Sınır: Sayfa GÖRÜNTÜLEME izlenmez — tablo 'hangi ekran ziyaret edildi' değil "
        "'nerede kayıt işlendi' sorusuna cevap verir; salt-okunur modüller haksız düşük "
        "görünür.\n"
        "\n"
        "Yorum: Hiç işlem görmeyen modüller ya gereksizdir ya eğitim eksiğidir — paket "
        "sadeleştirme kararlarının veri kaynağıdır."
    ),

    "admin_loglar_kurum.kategoriler": (
        "Tek kurumun denetim kayıtlarını kategori kartlarında gösterir (stratejik plan, "
        "süreç, gösterge, gösterge verisi, proje, görev): kayıt toplamı, son değişiklik ve "
        "açılınca olay listesi (oluştur/güncelle/sil).\n"
        "\n"
        "Hesap: Her kategori, ilgili kaynak türlerinin denetim kayıtlarından beslenir; son "
        "15 olay gösterilir, toplam ayrıca yazılır.\n"
        "\n"
        "Sınır: Bu detay YALNIZ denetim günlüğüne dayanır — özet sayfadaki gösterge-verisi "
        "birleşimi burada yoktur; günlüğe yazılmayan veri girişleri kategoride "
        "görünmeyebilir.\n"
        "\n"
        "Yorum: Silme olaylarının yoğunlaştığı kategori, kurumda veri disiplin sorununun "
        "veya yanlış kullanım eğitiminin işaretidir."
    ),

    # ─────────────────── ADMİN BİLDİRİMLER ───────────────────

    "admin_notifications.toplam_bildirim": (
        "Ekrana yüklenen bildirim kayıtlarının toplamını gösterir.\n"
        "\n"
        "Sınır: Görünüm en yeni 100 kayıtla sınırlıdır — bu sayı veritabanındaki gerçek "
        "toplam DEĞİLDİR; 100'de sabitlenmişse gerçek toplam daha yüksektir.\n"
        "\n"
        "Yorum: Kartı 'son dönem bildirim hacmi' olarak okuyun."
    ),

    "admin_notifications.okunmamis_bildirim": (
        "Yüklü bildirimler içinde henüz okunmamış olanların sayısını gösterir.\n"
        "\n"
        "Sınır: Son 100 kayıtlık görünüm üzerinden sayılır.\n"
        "\n"
        "Yorum: Okunmamış oranı sürekli yüksekse bildirimler ya çok ya alakasız demektir — "
        "bildirim hijyeni kullanıcı güveninin parçasıdır."
    ),

    "admin_notifications.okunmus_bildirim": (
        "Yüklü bildirimler içinde okunmuş olanların sayısını gösterir.\n"
        "\n"
        "Sınır: Son 100 kayıt üzerinden sayılır. Ayrıca 'silinen' bildirimler gerçekte "
        "okundu işaretlenir (soft-delete) — bu sayıya dahil olurlar.\n"
        "\n"
        "Yorum: Okunmuş sayısını okunmamışla birlikte oran olarak izleyin; mutlak sayı tek "
        "başına az şey söyler."
    ),

    "admin_notifications.yayin_bildirimi": (
        "Yüklü bildirimler içinde duyuru (toplu yayın) tipindekilerin sayısını gösterir.\n"
        "\n"
        "Hesap: 'Toplu bildirim gönder' işlemi, duyuruyu hedef kitledeki HER kullanıcı için "
        "ayrı bildirim satırı olarak dağıtır; bu kart o satırları sayar.\n"
        "\n"
        "Sınır: Kartın kendisi gönderim yapmaz; sayı son 100 kayıtlık görünüme tabidir.\n"
        "\n"
        "Yorum: Duyuru başına kullanıcı sayısı kadar satır oluşur — sık duyuru, listeyi "
        "hızla doldurur; duyuruyu seyrek ve öz kullanın."
    ),

    "admin_notifications.filtre": (
        "Bildirim tablosunu arama kutusu, tip ve okunma durumu seçicileriyle süzer.\n"
        "\n"
        "Sınır: Süzme tarayıcıda, ekrana yüklü son 100 kayıt üzerinde çalışır — sunucuya "
        "yeni sorgu atmaz.\n"
        "\n"
        "Yorum: Aradığınız eski bildirim son 100'ün dışında kalmış olabilir; bulunamıyorsa "
        "kayıt yok anlamına gelmez."
    ),

    "admin_notifications.bildirim_listesi": (
        "Bildirimleri tablolar: başlık, mesaj özeti, tip, alıcı, tarih, okunma durumu ve "
        "silme işlemi.\n"
        "\n"
        "Sınır: 'Sil' gerçek silme değildir — kaydı okundu işaretler (soft-delete); tablo "
        "son 100 kayıtla sınırlıdır.\n"
        "\n"
        "Yorum: Aynı başlıklı bildirimin çok sayıda alıcıda tekrarı normaldir (duyuru "
        "dağıtımı); anormal olan, kimsenin okumadığı tekrarlardır."
    ),

    # ─────────────────── ADMİN YEDEKLEME ───────────────────

    "admin_yedekleme.manuel_yedek": (
        "Anlık yedek üretip indirir: veritabanı yedeği (.dump) veya kod yedeği (.tar.gz).\n"
        "\n"
        "Hesap: Veritabanı yedeği PostgreSQL'in taşınabilir formatında alınır; kod yedeği "
        "tam arşivdir (git geçmişi, sanal ortam ve yedek klasörleri hariç; yüklenen "
        "dosyalar dahil).\n"
        "\n"
        "Sınır: İki yedek AYRI kapsamdır — DB yedeği dosyaları, kod yedeği veritabanını "
        "İÇERMEZ; tam güvence ikisini birlikte almaktır. Manuel yedek diske kalıcı "
        "yazılmaz, yalnızca indirilir.\n"
        "\n"
        "Yorum: Büyük değişiklik öncesi (toplu içe aktarma, geri yükleme) manuel DB yedeği "
        "almak ucuz bir sigortadır."
    ),

    "admin_yedekleme.otomatik_yedek_durumu": (
        "Gecelik otomatik yedek işinin durumunu gösterir: son çalışma zamanı, son tam kod "
        "yedeği ve kullanılan araç yolu; 'şimdi çalıştır' ile elle tetiklenebilir.\n"
        "\n"
        "Hesap: İş her gece 02:00'de çalışır — tam veritabanı yedeği + kod yedeği (haftada "
        "bir tam, diğer günler yalnız değişen dosyalar). Her türden son 14 yedek tutulur.\n"
        "\n"
        "Sınır: Zamanlayıcı kapatılmışsa (yapılandırma/demo modu) iş hiç koşmaz — 'son "
        "çalışma' tarihi eskiyorsa ilk bakılacak budur.\n"
        "\n"
        "Yorum: Yedeğin varlığı yetmez — arada bir geri yükleme provası yapılmayan yedek, "
        "test edilmemiş sigortadır."
    ),

    "admin_yedekleme.yedek_listesi": (
        "Otomatik üretilmiş yedek dosyalarını listeler: tür (DB tam / kod tam / kod fark), "
        "dosya adı, boyut, tarih ve indirme bağlantısı.\n"
        "\n"
        "Sınır: Yalnızca otomatik yedek klasöründeki dosyalar listelenir; manuel indirilen "
        "yedekler burada görünmez. Her türden son 14 dosya saklanır, eskileri silinir.\n"
        "\n"
        "Yorum: Liste boşsa otomatik iş hiç koşmamış demektir; boyutların ani değişimi de "
        "(çok küçük DB yedeği gibi) incelenmeye değer bir sinyaldir."
    ),

    "admin_yedekleme.db_geri_yukleme": (
        "Yüklenen yedek dosyasından veritabanını GERİ YÜKLER — mevcut verilerin üzerine "
        "yazar (yıkıcı işlem).\n"
        "\n"
        "Hesap: Dört katmanlı güvence ister: yönetici rolü + tam onay metni + yönetici "
        "şifresi + geçerli yedek dosyası (uzantı ve içerik imzası doğrulanır). Geçerse "
        "veritabanı yedekteki hâline döndürülür.\n"
        "\n"
        "Sınır: İşlem GERİ ALINAMAZ ve yalnız veritabanını kapsar (dosyalar/kod "
        "etkilenmez). Yedeğin alındığı andan sonraki tüm veri kaybolur.\n"
        "\n"
        "Yorum: Geri yüklemeden hemen önce mevcut durumun da manuel yedeğini alın — 'geri "
        "dönüşün geri dönüşü' ancak böyle mümkün olur."
    ),

    # ─────────────────── ADMİN ARAÇLAR ───────────────────

    "admin_araclar.yedekleme": (
        "Yedekleme bölümüne götüren geçiş kartıdır (otomatik gece yedeği, manuel yedekler "
        "ve geri yükleme).\n"
        "\n"
        "Sınır: Kartın kendisi yedek verisi göstermez; yalnızca yönlendirir.\n"
        "\n"
        "Yorum: Yedek durumu ve dosya listesi hedef sayfadadır."
    ),

    "admin_araclar.demo_talepleri": (
        "Demo talepleri aracına götüren geçiş kartıdır.\n"
        "\n"
        "Sınır: Kart veri göstermez; talep listesi hedef sayfadadır.\n"
        "\n"
        "Yorum: Tanıtım sitesinden gelen talepler orada bekler — düzenli kontrol satış "
        "sürecinin parçasıdır."
    ),

    "admin_araclar.demo_talepleri_liste": (
        "Tanıtım sitesindeki demo formundan gelen talepleri listeler: tarih, ad, kurum, "
        "görev, iletişim bilgileri, ilgilenilen modüller, mesaj ve e-posta gönderim "
        "durumu.\n"
        "\n"
        "Sınır: Liste filtresizdir (tüm kayıtlar, yeniden eskiye); okunmamış talepler sarı "
        "vurgulanır ve elle okundu işaretlenir.\n"
        "\n"
        "Yorum: E-posta gönderimi başarısız görünen talepler iletişim fırsatının "
        "kaçmaması için elle takip edilmelidir."
    ),

    "admin_araclar.hata_kontrolu": (
        "Hata kontrolü aracına götüren geçiş kartıdır; araç, izole test kurumu üzerinde "
        "otomatik tarayıcı testleri koşar.\n"
        "\n"
        "Sınır: Kart veri göstermez; testler yalnız Yerel ortamda çalışır.\n"
        "\n"
        "Yorum: Test ayrıntıları ve geçmiş, hedef sayfadaki kartlardadır."
    ),

    "admin_araclar.istatistikler": (
        "Kurum bazlı yapı istatistikleri sayfasına götüren geçiş kartıdır.\n"
        "\n"
        "Sınır: Kart veri göstermez; sayılar hedef sayfada hesaplanır.\n"
        "\n"
        "Yorum: Kurum dağılım tablosu, platformun büyüme ve kullanım fotoğrafıdır."
    ),

    "admin_araclar.loglar": (
        "Giriş ve veri hareketi logları sayfasına götüren geçiş kartıdır.\n"
        "\n"
        "Sınır: Kart veri göstermez; sayaçlar ve akış hedef sayfadadır.\n"
        "\n"
        "Yorum: Kullanım takibi ve benimseme analizinin merkezi orasıdır."
    ),

    "admin_araclar.yeni_arac_yer_tutucu": (
        "Gelecekte eklenecek yönetici araçları için ayrılmış boş yer tutucudur.\n"
        "\n"
        "Sınır: İşlevsizdir — veri veya bağlantı içermez.\n"
        "\n"
        "Yorum: Yeni araç ihtiyaçları bu ızgaraya eklenerek büyür."
    ),

    # ─────────────────── ADMİN HATA KONTROLÜ ───────────────────

    "admin_hata_kontrolu.izole_test_kurumu": (
        "İzole test kurumunun (tomofiltest) durumunu gösterir ve 'kur / yenile' ile "
        "sıfırdan kurulmasını sağlar; kurulunca strateji, süreç, gösterge ve ölçüm "
        "sayıları listelenir.\n"
        "\n"
        "Hesap: Test kurumu, örnek kurumun birebir veritabanı klonudur; testler bu klonun "
        "sentetik yöneticisiyle koşar — gerçek kurum verisi hiç etkilenmez.\n"
        "\n"
        "Sınır: Yenileme, çalışan bir test varken kilitlenir (aynı anda tek işlem); araç "
        "yalnız Yerel ortamda çalışır.\n"
        "\n"
        "Yorum: CRUD senaryoları yazma yaptığı için klon her senaryo koşusundan sonra "
        "otomatik tazelenir — 'kirli klon' endişesi olmadan test edilebilir."
    ),

    "admin_hata_kontrolu.kesif_taranacak_sayfalar": (
        "Otomatik testin tarayacağı güvenli sayfaların envanterini çıkarır: sayfa sayısı, "
        "modül dağılımı ve atlananlar (parametreli, kara listeli, eski yüzey).\n"
        "\n"
        "Hesap: Uygulamanın rota haritasından yalnız parametresiz GET sayfaları seçilir; "
        "çıkış/silme/indirme gibi yan etkili adresler kara listeyle atlanır.\n"
        "\n"
        "Sınır: Parametre isteyen sayfalar (ör. /surec/5) bu sürümde kapsam dışıdır — "
        "keşif sayısı toplam ekran sayısından azdır.\n"
        "\n"
        "Yorum: Keşif, taramanın kapsam sözleşmesidir — 'test edildi' demeden önce neyin "
        "taranmadığını da buradan görün."
    ),

    "admin_hata_kontrolu.otomatik_tarayici_testi": (
        "Keşfedilen her sayfayı gerçek bir tarayıcıyla (Playwright, başsız Chromium) açıp "
        "pasif sağlık taraması yapar: sonuçlar ✅/⚠️/❌/⏭️ olarak sayılır, ölü linkler ve "
        "hiçbir yerden erişilemeyen (yetim) sayfalar raporlanır.\n"
        "\n"
        "Hesap: Sınıflandırma — 500 ve üzeri veya girişe düşme: hata; konsol/JS/AJAX "
        "sorunları: uyarı; 403/404: atlandı; normal yanıt: tamam.\n"
        "\n"
        "Sınır: Tarama PASİFTİR — hiçbir form doldurmaz, veri yazmaz; etkileşimli hatalar "
        "CRUD senaryolarının işidir. Sayfa sınırı verilirse yetim analizi yapılmaz.\n"
        "\n"
        "Yorum: Uyarılar 'çalışıyor ama kirli' demektir — konsol hataları birikirse gerçek "
        "hataların sinyali gürültüde kaybolur."
    ),

    "admin_hata_kontrolu.tarama_gecmisi": (
        "Kayıtlı tarama koşularını listeler; her koşunun zaman damgası ve hata/uyarı/tamam "
        "özeti görünür, tıklayınca detay açılır.\n"
        "\n"
        "Sınır: Son 30 koşu listelenir; senaryo koşuları ayrı geçmişte tutulur.\n"
        "\n"
        "Yorum: Ardışık koşuların özetlerini karşılaştırmak regresyonu erken yakalar — "
        "hata sayısı artan koşu, son değişikliklerin faturasıdır."
    ),

    "admin_hata_kontrolu.aktif_crud_senaryolari": (
        "Gerçek kullanıcı etkileşimlerini (form doldurma, modal, kaydetme) otomatik koşan "
        "senaryo testleridir; her senaryo geçti/kaldı sonucu ve adım detayı verir.\n"
        "\n"
        "Hesap: Senaryo, tüm adımları başarılıysa geçer. Koşu izole test kurumunda yazma "
        "yapar ve bitince kurum otomatik baseline'a sıfırlanır.\n"
        "\n"
        "Sınır: Senaryo kapsamı tanımlı akışlarla sınırlıdır (şu an 5 senaryo) — geçmesi "
        "'tüm sistem sağlam' değil 'bu akışlar sağlam' demektir.\n"
        "\n"
        "Yorum: Kalan senaryolarda ilk adım hatası genelde ortam/yetki sorunudur; gerçek "
        "regresyon çoğunlukla ara adımlarda görünür."
    ),

    "admin_hata_kontrolu.senaryo_gecmisi": (
        "Kayıtlı senaryo koşularını listeler: zaman damgası ve geçti/kaldı özeti.\n"
        "\n"
        "Sınır: Tarama geçmişiyle aynı kayıt havuzunu kullanır, yalnız senaryo koşuları "
        "süzülür.\n"
        "\n"
        "Yorum: Aynı senaryonun aralıklı kalması (bazen geçip bazen kalması) kararsız "
        "test veya zamanlama sorunudur — sürekli kalmasından daha sinsi bir bulgudur."
    ),

    # ─────────────────── ADMİN KILAVUZ OLUŞTURUCU ───────────────────

    "admin_kilavuz_olusturucu.kontrol_paneli": (
        "Kullanım kılavuzu ve eğitim videosunun otonom üretimini başlatır/durdurur; "
        "ilerleme çubuğuyla adımlar izlenir.\n"
        "\n"
        "Hesap: Üretim, çalışma kurumunu sıfırlayıp gerçek tarayıcıda senaryoyu oynar; "
        "video (sesli anlatımlı), işaretli ekran görüntüleri ve PDF kılavuz üretir.\n"
        "\n"
        "Sınır: Şu an yalnız Bölüm 1 senaryosu aktiftir; araç Yerel ortamda çalışır. "
        "Durdurulursa taslak PDF yine derlenir.\n"
        "\n"
        "Yorum: Ürün ekranları değiştikçe çekimi yeniden koşmak, kılavuzu elle güncelleme "
        "yükünden kurtarır — kılavuz 'ürünle birlikte' yaşlanmaz."
    ),

    "admin_kilavuz_olusturucu.calisma_loglari": (
        "Çekim sürecinin canlı log akışını terminal görünümünde gösterir: kurum "
        "hazırlığı, tarayıcı adımları, ses üretimi, PDF derleme.\n"
        "\n"
        "Sınır: Loglar bellektedir — yeni koşu başlayınca öncekiler temizlenir.\n"
        "\n"
        "Yorum: Çekim takılırsa son log satırı sorunun adresini söyler (ör. ses üretimi "
        "SSL, ffmpeg eksikliği)."
    ),

    "admin_kilavuz_olusturucu.video_galerisi": (
        "Üretilen eğitim videolarını oynatıcıyla sunar; şu an Bölüm 1 (giriş, kurum ve "
        "kullanıcı yapılandırması) yayında.\n"
        "\n"
        "Sınır: Galeri sabit listedir — yeni bölümler üretildikçe elle eklenir; video "
        "dosyası üretilmemişse oynatıcı boş kalır.\n"
        "\n"
        "Yorum: Videolar sesli anlatımlıdır ve ekran akışını birebir gösterir — yeni "
        "kullanıcı eğitiminin en düşük maliyetli aracıdır."
    ),

    "admin_kilavuz_olusturucu.yenitomofil_durumu": (
        "Kılavuz çekimlerinde kullanılan çalışma kurumunun (YeniTomofil) durumunu "
        "gösterir: kurulu mu, strateji/süreç/gösterge/ölçüm sayıları ve yönetici "
        "e-postası.\n"
        "\n"
        "Sınır: YeniTomofil, hata kontrolündeki test klonundan FARKLIDIR — çekim için BOŞ "
        "kurulur (veri klonlanmaz) ve her çekim başında sıfırlanır.\n"
        "\n"
        "Yorum: Çekim 'boş kurumdan kuruluma' hikayesini anlattığı için kurum boş başlar; "
        "sayıların çekim sonunda dolması senaryonun çalıştığının kanıtıdır."
    ),

    "admin_kilavuz_olusturucu.kilavuz_pdf_indirme": (
        "Derlenen en güncel kullanım kılavuzu PDF'ini indirir.\n"
        "\n"
        "Sınır: Çekim tamamlanmadıysa taslak PDF inebilir; hiç üretilmemişse indirme "
        "'henüz üretilmedi' hatası verir.\n"
        "\n"
        "Yorum: PDF, çekim sırasında alınan işaretli ekran görüntüleriyle derlenir — "
        "dağıtmadan önce sayfalarına göz atın."
    ),

    # ─────────────────── ADMİN KURULUM İÇE AKTARMA ───────────────────

    "admin_setup_import.yukleme": (
        "Kurulum verilerini Excel ile içe aktarmanın ilk adımı: hazır şablonu indir, "
        "doldur, yükle.\n"
        "\n"
        "Hesap: Şablon üç sayfadır — Süreçler, PG Tanımları ve (opsiyonel) Strateji; "
        "periyot/toplama alanları açılır listeyle sınırlandırılmıştır.\n"
        "\n"
        "Sınır: Yalnız .xlsx kabul edilir, en fazla 5 MB; ağırlıklar 0-100 aralığında "
        "doğrulanır.\n"
        "\n"
        "Yorum: Şablonun örnek satırlarını silmeden üzerine yazmak en sık hatadır — kendi "
        "verinizi örneklerin YERİNE koyun."
    ),

    "admin_setup_import.onizleme": (
        "Yüklenen dosyanın uygulanmadan önce ne yapacağını gösterir: kaç kayıt eklenecek, "
        "kaç kayıt güncellenecek ve satır satır hatalar.\n"
        "\n"
        "Hesap: Ön izleme deneme modudur — HİÇBİR ŞEY YAZILMAZ. Mevcut kod eşleşirse "
        "güncelleme, yoksa ekleme planlanır. 'Hatalı satırları atla' işaretlenmeden hatalı "
        "dosya uygulanamaz.\n"
        "\n"
        "Sınır: Aktif plan yılı yoksa strateji sayfası uygulamada atlanır (ön izleme yine "
        "gösterir).\n"
        "\n"
        "Yorum: Hata listesi satır numarası verir — dosyayı düzeltip yeniden ön izlemek, "
        "atlayarak uygulamaktan her zaman daha temizdir."
    ),

    "admin_setup_import.sonuc": (
        "İçe aktarma sonucunu raporlar: kaç süreç, gösterge ve strateji eklendi ya da "
        "güncellendi; varsa uyarılar.\n"
        "\n"
        "Hesap: Uygulama TEK transaction'dır — herhangi bir hatada TAMAMI geri alınır, "
        "yarım yazma olmaz. SİLME asla yapılmaz; yalnızca ekleme ve güncelleme.\n"
        "\n"
        "Yorum: 'Hiçbir değişiklik yazılmadı' hatası korkutucu görünse de güvencenin "
        "kendisidir — dosyayı düzeltip yeniden deneyin."
    ),
}
