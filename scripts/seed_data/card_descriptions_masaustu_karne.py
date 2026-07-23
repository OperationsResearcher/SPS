# -*- coding: utf-8 -*-
"""Masaüstü + Bireysel Karne + Süreç Karnesi + Süreç + Analiz + Yönetim Özeti
kart açıklamaları — 71 kart (dilim 3).

Yazım sözleşmesi için bkz. card_descriptions_k_radar.py başlığı.
Kod bağlamı 2026-07-21'de 4 paralel keşif ajanıyla çıkarıldı (dosya:satır kanıtlı).
"""

DESCRIPTIONS: dict[str, str] = {

    # ─────────────────── BİREYSEL KARNE ───────────────────

    "bireysel_karne.ai_ozet": (
        "Yılın kişisel performans fotoğrafından üretilen iki cümlelik özet gösterir; "
        "kaynak rozeti 'AI' veya 'otomatik' olur.\n"
        "\n"
        "Hesap: Özetin dayandığı sayılar deterministiktir — veri girilen PG oranı, aktif ve "
        "geciken faaliyet sayısı. Yapay zekâ erişimi varsa metin modele yazdırılır; yoksa "
        "aynı sayılarla kural tabanlı özet üretilir.\n"
        "\n"
        "Sınır: 'AI' rozeti yalnız gerçek model çıktısında görünür; model metni "
        "deterministik değildir.\n"
        "\n"
        "Yorum: Geciken faaliyet varsa özet 'kırmızı bayrak' diliyle uyarır — özeti "
        "okuduktan sonra ilgili faaliyet tablosuna inip ayları işaretleyin."
    ),

    "bireysel_karne.ust_bar": (
        "Karne sayfasının üst şerididir: başlık, yıl seçici ve genel skor halkasını "
        "barındırır.\n"
        "\n"
        "Sınır: Kartın kendisi hesap yapmaz — skor mantığı 'genel başarı skoru' kartındadır; "
        "yıl seçici tüm karneyi seçilen yıla göre yeniden yükler.\n"
        "\n"
        "Yorum: Sayılar beklenmedik görünüyorsa önce seçili yılı kontrol edin."
    ),

    "bireysel_karne.genel_skor": (
        "Kişisel genel başarı skorunu 1-5 ölçeğinde halka göstergeyle sunar.\n"
        "\n"
        "Hesap: Skor = başarı puanı hesaplanabilen PG'lerin AĞIRLIKLI ortalamasıdır "
        "(puan × ağırlık toplamı / ağırlık toplamı); ağırlık girilmemişse düz ortalama "
        "alınır. Her PG'nin puanı, son dolu aylık değerin tanımlı başarı aralıklarına "
        "oturtulmasıyla (1-5) bulunur.\n"
        "\n"
        "Eşik: Halka rengi puana göre — 1 kırmızı, 2 turuncu, 3 sarı, 4 açık yeşil, 5 "
        "yeşil.\n"
        "\n"
        "Sınır: Faaliyet tamamlama skora GİRMEZ — skor yalnızca PG puanlarından türetilir. "
        "Başarı aralığı yeni bant formatıyla (min-max-puan) tanımlanmış PG'ler bu hesapta "
        "puansız kalabilir ve skora katılmaz; puanı '—' görünen PG'lerde aralık tanımını "
        "kontrol edin.\n"
        "\n"
        "Yorum: Skoru veri kapsamıyla birlikte okuyun — iki PG'lik bir karnede tek ölçüm "
        "skoru sürükler."
    ),

    "bireysel_karne.ilerleme_halkalari": (
        "İki halka gösterir: PG veri kapsamı (veri girilen / toplam PG) ve faaliyet "
        "tamamlama yüzdesi.\n"
        "\n"
        "Eşik: Faaliyet halkası %75+ yeşil, %50-75 turuncu, altı kırmızı; kapsam halkası "
        "sabit renklidir.\n"
        "\n"
        "Sınır: Faaliyet yüzdesi 'en az bir ayı işaretlenmiş faaliyet' oranıdır — ay "
        "bazında ağırlıklı tamamlama DEĞİLDİR; 1 ayı işaretli faaliyet ile 12 ayı işaretli "
        "faaliyet eşit sayılır.\n"
        "\n"
        "Yorum: Kapsam halkası düşükse önce veri girin — karnenin geri kalanı ancak veriyle "
        "anlamlanır."
    ),

    "bireysel_karne.stat_toplam_pg": (
        "Kullanıcının aktif bireysel performans göstergesi sayısını gösterir.\n"
        "\n"
        "Sınır: Aktif plan yılına filtrelenir; o yılda hiç PG yoksa tüm yıllar gösterilir.\n"
        "\n"
        "Yorum: 3-7 arası kişisel PG yönetilebilir bir settir; çok daha fazlası odak "
        "dağıtır."
    ),

    "bireysel_karne.stat_veri_girilen": (
        "Seçili yılda en az bir aylık değeri girilmiş PG sayısını gösterir.\n"
        "\n"
        "Sınır: PG sayısını sayar, veri noktası sayısını değil.\n"
        "\n"
        "Yorum: Bu sayı toplam PG'ye eşitlenmeden karne 'tam' sayılmaz — veri girilmeyen "
        "gösterge skor ve analizlerin dışında kalır."
    ),

    "bireysel_karne.stat_faaliyetler": (
        "Kullanıcının aktif faaliyet sayısını gösterir.\n"
        "\n"
        "Sınır: Faaliyet listesi yıla filtrelenmez — tüm aktif faaliyetler sayılır; yalnız "
        "ay işaretleri yıl bazlıdır.\n"
        "\n"
        "Yorum: Faaliyetler PG'lerin 'nasıl' ayağıdır — hedefi olup faaliyeti olmayan "
        "karne, sonuca giden yolu tanımlamamış demektir."
    ),

    "bireysel_karne.stat_tamamlanan": (
        "En az bir ayı tamamlandı işaretlenmiş faaliyetlerin oranını yüzde olarak "
        "gösterir.\n"
        "\n"
        "Hesap: İşaretli faaliyet / toplam faaliyet × 100.\n"
        "\n"
        "Sınır: 'Tamamlanan' burada ay bazlı ilerleme yüzdesi DEĞİLDİR — tek ayı işaretli "
        "faaliyet de 'başlamış' sayılır; faaliyet durumu (Tamamlandı vb.) bu hesapta "
        "kullanılmaz.\n"
        "\n"
        "Yorum: Yüzde yüksek ama iş bitmemiş hissi varsa ay işaretlerinin gerçek "
        "tamamlanmayı mı yoksa 'dokunulmayı' mı yansıttığını sorgulayın."
    ),

    "bireysel_karne.hedef_karsilastirma": (
        "Her PG için son gerçekleşen değeri hedefe oranlayan yatay barlar çizer; hedef "
        "çizgisi işaretlidir.\n"
        "\n"
        "Hesap: Bar = son değer / hedef × 100 (gösterim %140'ta kırpılır); yön dikkate "
        "alınır — artan hedefte değer ≥ hedef, azalan hedefte değer ≤ hedef 'iyi' sayılır.\n"
        "\n"
        "Sınır: Hedefi veya değeri olmayan PG'ler grafiğe girmez; karşılaştırma yalnızca "
        "SON aylık değere bakar, ortalamaya değil.\n"
        "\n"
        "Yorum: Tek ayın değeriyle 'hedef aşıldı' demeden trend çizgisine de bakın — son "
        "ay istisna olabilir."
    ),

    "bireysel_karne.yil_ozeti": (
        "Yılın dikkat özetini üç rozetle verir: kaç ayda veri girildi, kaç PG bu yıl hiç "
        "veri almadı, kaç PG hedefe göre zayıf seyrediyor.\n"
        "\n"
        "Hesap: 'Zayıf' = son değerin hedefin %90'ının altında (artan) veya %110'unun "
        "üstünde (azalan) olması.\n"
        "\n"
        "Sınır: Bu bilgilendirme amaçlı bir ön işarettir — resmî değerlendirme ölçüsü "
        "değildir; yalnızca son değere bakar.\n"
        "\n"
        "Yorum: 'Veri almayan PG' rozeti kırmızıysa ilk iş veri girmektir; zayıf listesi "
        "ise ay sonu kişisel gözden geçirmenin gündemidir."
    ),

    "bireysel_karne.zaman_cizelgesi": (
        "Yıl içindeki kişisel hareketleri kronolojik listeler: PG veri girişleri ve "
        "tamamlanan faaliyet ayları (en yeni üstte).\n"
        "\n"
        "Sınır: Liste son 40 olayla sınırlıdır ve yalnız seçili yılı kapsar.\n"
        "\n"
        "Yorum: Çizelge, yıl sonu öz değerlendirmenin ham hafızasıdır — 'bu yıl ne yaptım' "
        "sorusunun kanıtlı cevabı burada birikir."
    ),

    "bireysel_karne.pg_tablosu": (
        "PG'leri 12 aylık değer tablosunda gösterir: hedef, birim, aylık hücreler, mini "
        "trend çizgisi ve başarı puanı rozeti; satıra tıklayınca yıllık detay açılır.\n"
        "\n"
        "Hesap: Rozet, son dolu aylık değerin başarı aralıklarına göre 1-5 puanıdır; hücre "
        "renkleri veri varlığını ve son ayın puanını yansıtır.\n"
        "\n"
        "Sınır: Tablo yalnızca AYLIK seriyi gösterir; gelecek aylar boş bırakılır. Yeni "
        "bant formatlı başarı aralıkları bu görünümde puansız kalabilir.\n"
        "\n"
        "Yorum: Boş hücre deseni (hep aynı aylar boş) veri girme alışkanlığının "
        "fotoğrafıdır — hatırlatıcıya bağlamak en kalıcı çözümdür."
    ),

    "bireysel_karne.faaliyet_isi_haritasi": (
        "Her faaliyetin 12 aylık tamamlama takvimini renkli hücrelerle gösterir.\n"
        "\n"
        "Hesap: Hücre üç durumludur — tamamlandı, gelecek ay, geçmiş-ama-işaretsiz. "
        "Yoğunluk gradyanı yoktur; işaret ikilidir.\n"
        "\n"
        "Sınır: 'Isı haritası' adına rağmen yoğunluk ölçmez — yalnızca tamamlandı/boş "
        "durumunu gösterir.\n"
        "\n"
        "Yorum: Satırda uzun boş bantlar faaliyetin fiilen durduğunun işaretidir — durumu "
        "güncellemek (askıya al/kapat) takvimi dürüst tutar."
    ),

    "bireysel_karne.faaliyet_tablosu": (
        "Faaliyetleri durumları ve 12 aylık tamamlama kutucuklarıyla listeler; kutucuğa "
        "tıklamak o ayın kaydını anında değiştirir.\n"
        "\n"
        "Sınır: Durum sütunu serbest durum metnidir; ilerleme yüzdesi kayıtta tutulsa da "
        "bu tabloda gösterilmez. Ay işaretleri seçili yıl içindir.\n"
        "\n"
        "Yorum: Ayı gerçekleştiği anda işaretlemek, yıl sonunda geriye dönük 'hatırlama "
        "arkeolojisinden' kurtarır."
    ),

    # ─────────────────── MASAÜSTÜ ───────────────────

    "masaustu.yonetici_sabah_ozeti": (
        "Kurum genelinin sabah uyarı panelidir: kritik göstergeler, geciken ve yaklaşan "
        "faaliyetler, geciken projeler (yalnız yönetici rollerine görünür).\n"
        "\n"
        "Hesap: Kritik gösterge = son değer / hedef oranı artan yönde 0,80'in altında veya "
        "azalan yönde 1,20'nin üzerinde. Yaklaşan penceresi 7 gündür.\n"
        "\n"
        "Sınır: Tamamen KURAL TABANLIDIR — yapay zekâ kullanılmaz; sayılar deterministik "
        "sorgulardır.\n"
        "\n"
        "Yorum: 'Her şey yolunda' mesajı veri yokluğundan da gelebilir — ölçüm kapsamı "
        "düşükken sessizlik iyi haber değildir."
    ),

    "masaustu.kurumsal_olgunluk_endeksi": (
        "Kurumun yapısal olgunluğunu 0-100 endeksle özetler; performans verisi girmeden, "
        "mevcut yapı verisinden hesaplanır (yalnız yönetici rollerine görünür).\n"
        "\n"
        "Hesap: Dört boyutun EŞİT ağırlıklı (%25) ortalamasıdır — Kimlik ve Strateji "
        "(kimlik alanları doluluğu + alt stratejili strateji oranı + stratejik hedefli "
        "kullanıcı oranı), Süreç Mimarisi (stratejiye bağlı süreç oranı + göstergeli süreç "
        "oranı), Olgunluk (süreç öz değerlendirme ortalaması 0-100'e çevrilir), İcra "
        "Disiplini (tamamlanan faaliyet oranı).\n"
        "\n"
        "Eşik: Boyut barları 70+ yeşil, 40-70 turuncu, altı kırmızı.\n"
        "\n"
        "Sınır: Endeks YAPI ölçer, performans değil — göstergeleriniz kötü seyrederken "
        "endeks yüksek olabilir. 'AI ile zenginleştir' düğmesi yalnız anlatım dilini "
        "yeniden yazar; bulgu ve sayılar deterministik kalır, erişim yoksa kural metnine "
        "düşülür.\n"
        "\n"
        "Yorum: Endeksi kurulum yol haritası olarak kullanın — en düşük boyut, bir sonraki "
        "yapısal yatırımın adresidir."
    ),

    "masaustu.bugunun_ozeti": (
        "Günün kişisel özetini dört sayıyla verir: okunmamış bildirim, bu ay veri "
        "girilmemiş PG, geciken faaliyet ve 7 gün içinde bitecek faaliyet.\n"
        "\n"
        "Sınır: Bu kart KİŞİSEL kapsamdadır (bireysel PG/faaliyet + bildirim); kurum geneli "
        "uyarılar 'yönetici sabah özeti'ndedir.\n"
        "\n"
        "Yorum: Güne bu dört sayıyla başlamak, işi 'hatırladıklarına' değil 'sistemin "
        "gösterdiklerine' göre önceliklendirmeyi sağlar."
    ),

    "masaustu.mini_kartlar": (
        "Dört hızlı sayacı bir arada tutan gruptur: bireysel PG, devam eden faaliyet, "
        "süreç PG ve okunmamış bildirim.\n"
        "\n"
        "Sınır: Grubun kendi hesabı yoktur — sayılar içindeki dört kartta üretilir.\n"
        "\n"
        "Yorum: Masaüstünün nabız satırıdır; detaylar ilgili kartlarda."
    ),

    "masaustu.bireysel_pg": (
        "Kullanıcının aktif bireysel performans göstergesi sayısını gösterir.\n"
        "\n"
        "Yorum: Süreç PG sayacıyla karıştırmayın — bu, kişiye tanımlı hedeflerin "
        "sayısıdır."
    ),

    "masaustu.devam_eden_faaliyet": (
        "Tamamlanmamış aktif bireysel faaliyet sayısını gösterir.\n"
        "\n"
        "Hesap: Durumu 'Tamamlandı' olmayan aktif faaliyetler sayılır.\n"
        "\n"
        "Yorum: Sayı sürekli büyüyorsa faaliyetler kapanmıyor demektir — biten işleri "
        "işaretlemek listeyi dürüst tutar."
    ),

    "masaustu.surec_pg": (
        "Kullanıcının üye veya lider olduğu süreçlerdeki toplam aktif gösterge sayısını "
        "gösterir.\n"
        "\n"
        "Sınır: Bu sayaç kurumsal süreç göstergelerini kapsar — kişisel (bireysel) "
        "göstergeler ayrı sayaçtadır. 'Süreç PG'lerim' kartı aynı kümenin yalnız son 5 "
        "kaydını listeler.\n"
        "\n"
        "Yorum: Sorumlu olduğunuz gösterge yükünün büyüklüğüdür; süreç üyeliğinizle "
        "birlikte artar."
    ),

    "masaustu.okunmamis_bildirim": (
        "Okunmamış bildirim sayısını gösterir.\n"
        "\n"
        "Yorum: Bildirim listesi kartı aynı verinin son 5 kaydını gösterir; sayıyı "
        "düzenli sıfırlamak önemli bildirimlerin gürültüde kaybolmasını önler."
    ),

    "masaustu.benim_gorevlerim": (
        "Üç kaynaktaki işleri tek listede birleştirir: proje görevleri, bireysel "
        "faaliyetler ve süreç faaliyetleri; son tarihe göre sıralar ve Tümü / Gecikmiş / "
        "Bugün / Bu hafta filtreleri sunar.\n"
        "\n"
        "Hesap: Gecikmiş = son tarihi geçmiş; bugün = bugün biten; bu hafta = 7 gün içinde "
        "biten (tamamlanmış işler listeye girmez).\n"
        "\n"
        "Sınır: Süreç faaliyeti bölümü hata durumunda sessizce atlanabilir — liste o "
        "durumda eksik kalır (günlüğe yazılır).\n"
        "\n"
        "Yorum: Günlük çalışma listesi olarak en kapsamlı görünüm budur; kırmızı rozetli "
        "satırlar günün ilk işidir."
    ),

    "masaustu.favori_ve_son_ziyaretlerim": (
        "Sabitlediğiniz sayfaları ve son ziyaret ettiklerinizi hızlı erişim çipleri olarak "
        "gösterir.\n"
        "\n"
        "Sınır: Kayıtlar TARAYICIDA saklanır (sunucuda değil) — başka cihazda veya "
        "tarayıcıda görünmez; en fazla 12 sabit ve 8 son ziyaret listelenir.\n"
        "\n"
        "Yorum: Günlük rutindeki 3-4 ekranı sabitlemek menü gezinmesini büyük ölçüde "
        "ortadan kaldırır."
    ),

    "masaustu.hizli_islemler": (
        "En sık kullanılan altı ekrana sabit kısayol sunar: bireysel karne, bildirimler, "
        "süreçler, stratejik plan, projeler ve kurum.\n"
        "\n"
        "Sınır: Liste sabittir — role veya kullanıma göre değişmez.\n"
        "\n"
        "Yorum: Kişiselleştirilebilir kısayol ihtiyacınız varsa favori/sabitleme kartını "
        "kullanın."
    ),

    "masaustu.takvimim": (
        "Kişisel takviminizi gösterir: üye/lider olduğunuz süreçlerin faaliyetleri "
        "(yeşil), proje görevleriniz (mavi) ve bireysel faaliyetleriniz (sarı); boş güne "
        "tıklayarak hızlı kayıt eklenir.\n"
        "\n"
        "Sınır: Kapsam KİŞİSELDİR — kurum geneli takvim ayrı uçtan sunulur.\n"
        "\n"
        "Yorum: Aynı haftaya yığılmış bitişler kapasite çakışmasının görsel uyarısıdır — "
        "tarihleri yaymak gecikme istatistiğini düzeltir."
    ),

    "masaustu.benim_masam": (
        "Bireysel faaliyetlerinizi üç sekmede toplar: bugün bitenler, 7 gün içinde "
        "bitenler ve gecikenler; ilerleme yüzdeleriyle.\n"
        "\n"
        "Sınır: Yalnız bireysel faaliyetler — proje/süreç işleri 'Benim Görevlerim' "
        "kartındadır.\n"
        "\n"
        "Yorum: Geciken sekmesini boşaltmadan yeni faaliyet açmamak, listeyi yönetilebilir "
        "tutmanın en basit kuralıdır."
    ),

    "masaustu.dikkat_donem_verisi": (
        "İçinde bulunulan ay için henüz VERİ GİRİLMEMİŞ bireysel göstergelerinizi uyarır "
        "ve karneye yönlendirir (ilk 12 kayıt listelenir).\n"
        "\n"
        "Sınır: Uyarı eksik VERİ GİRİŞİ içindir — hedef sapması değil; performans uyarıları "
        "başka kartlardadır.\n"
        "\n"
        "Yorum: Ay bitmeden bu listeyi boşaltmak, karnenin ve skorların ay sonunda eksiksiz "
        "olmasını garantiler."
    ),

    "masaustu.karalama_defteri": (
        "Serbest not alanıdır — hızlı düşünceler, hatırlatmalar için.\n"
        "\n"
        "Sınır: Notlar TARAYICIDA saklanır, sunucuya GÖNDERİLMEZ — başka cihazda görünmez "
        "ve yedeklenmez; tarayıcı verisi temizlenirse silinir.\n"
        "\n"
        "Yorum: Kalıcı olması gereken notları ilgili kayda (faaliyet açıklaması, PG notu) "
        "taşıyın; burası geçici zihin panosudur."
    ),

    "masaustu.ozet_listeler": (
        "İki hızlı listeyi yan yana sunar: son 5 bireysel göstergeniz (durum rozetiyle) ve "
        "devam eden son 5 bireysel faaliyetiniz (ilerleme çubuğuyla).\n"
        "\n"
        "Eşik: İlerleme çubuğu %80+ yeşil, %50-80 normal, altı sarı.\n"
        "\n"
        "Sınır: Her liste 5 kayıtla sınırlıdır; tam listeler karne sayfasındadır.\n"
        "\n"
        "Yorum: Masaüstünden karneye geçmeden önce hızlı durum turu için tasarlanmıştır."
    ),

    "masaustu.favori_pglerim": (
        "Süreç karnelerinde yıldızladığınız göstergeleri son ölçüm değeri, hedef ve durum "
        "yüzdesiyle listeler.\n"
        "\n"
        "Eşik: Durum rozeti %80+ yeşil, %50-80 sarı, altı kırmızı.\n"
        "\n"
        "Sınır: Yalnız SÜREÇ göstergeleri favorilenebilir (bireysel değil); hiç favori "
        "yoksa kart görünmez.\n"
        "\n"
        "Yorum: Sorumluluğunuzdaki kritik 3-5 göstergeyi favorileyin — masaüstü açılışında "
        "ilk bakışta durumu görürsünüz."
    ),

    "masaustu.surec_pglerim": (
        "Üye/lider olduğunuz süreçlerdeki son güncellenen 5 göstergeyi listeler (ad, "
        "süreç, hedef).\n"
        "\n"
        "Sınır: Yalnız son 5 kayıt — toplam sayı üstteki 'Süreç PG' sayacındadır; hiç kayıt "
        "yoksa kart görünmez.\n"
        "\n"
        "Yorum: Liste 'son dokunulan' göstergeleri gösterir — uzun süre listede görünmeyen "
        "sorumluluklar bakım bekliyor olabilir."
    ),

    "masaustu.bildirimler": (
        "Son 5 okunmamış bildiriminizi gösterir; satırdan doğrudan okundu "
        "işaretleyebilirsiniz.\n"
        "\n"
        "Sınır: Yalnız okunmamışlar listelenir; tam liste bildirim sayfasındadır.\n"
        "\n"
        "Yorum: Atama ve değişiklik bildirimlerini günlük temizlemek, önemli olayların "
        "kaçmamasının en basit güvencesidir."
    ),

    "masaustu.stratejik_hedefler": (
        "Kurumun ilk üç aktif stratejisini kod ve başlıkla gösterir (yalnız yönetici "
        "rollerine görünür).\n"
        "\n"
        "Sınır: Yalnız İLK 3 strateji listelenir; ilerleme/skor gösterilmez — bu bir "
        "hatırlatma kartıdır, izleme kartı değil.\n"
        "\n"
        "Yorum: Amacı, günlük operasyon ekranında stratejik çerçeveyi göz önünde tutmaktır; "
        "izleme için SP ve yönetici paneli kullanılır."
    ),

    # ─────────────────── SÜREÇ (ANA SAYFA) ───────────────────

    "process.toplam_surec": (
        "Erişiminizdeki toplam süreç sayısını gösterir; altında kök (ana) süreç sayısı "
        "yazar.\n"
        "\n"
        "Hesap: Aktif plan yılındaki (veya dönemsiz) erişilebilir süreçler sayılır — kök ve "
        "alt süreçler birlikte.\n"
        "\n"
        "Yorum: Süreç sayısı yönetim kapasitesiyle orantılı olmalıdır — herkesin süreç "
        "açtığı bir yapıda sayı büyür ama sahiplik incelir."
    ),

    "process.toplam_pg": (
        "Tüm süreçlerdeki toplam performans göstergesi sayısını gösterir; altında hiç "
        "göstergesi olmayan süreç sayısı yazar.\n"
        "\n"
        "Yorum: Göstergesiz süreç ölçülemeyen süreçtir — bu alt sayıyı sıfırlamak, skor "
        "kartlarının kurumu gerçekten temsil etmesinin ön koşuludur."
    ),

    "process.ortalama_skor": (
        "Tüm süreçlerin ortalama skorunu gösterir.\n"
        "\n"
        "Hesap: Süreç skorlarının düz ortalamasıdır.\n"
        "\n"
        "Eşik: 80+ yeşil, 50-79 turuncu, altı kırmızı.\n"
        "\n"
        "Sınır: Bu kartta skoru HESAPLANAMAYAN (verisiz) süreçler 0 sayılıp paydaya girer — "
        "skor motorunun 'ölçülmeyen ortalamaya girmez' ilkesinden FARKLIDIR; verisiz süreç "
        "oranı yüksekken ortalama olduğundan düşük görünür.\n"
        "\n"
        "Yorum: Ortalama düşükse önce 'veri yok' rozetine bakın — sorun performans değil "
        "ölçüm kapsamı olabilir."
    ),

    "process.yuksek_performans": (
        "Skoru 80 ve üzerinde olan süreç sayısını gösterir.\n"
        "\n"
        "Hesap: Ham süreç skoru 80+ olanlar sayılır; verisiz süreçler bu sayıya girmez.\n"
        "\n"
        "Yorum: Bu süreçler iyi uygulama kaynağıdır — yöntemlerinin diğer süreçlere "
        "aktarımı, en ucuz iyileştirme koludur."
    ),

    "process.kritik_surec": (
        "Skoru 50'nin altında olan süreç sayısını gösterir.\n"
        "\n"
        "Hesap: Ölçülmüş ve ham skoru 50'nin altında kalan süreçler sayılır; verisiz "
        "süreçler kritik SAYILMAZ (ayrı 'veri yok' kovasında).\n"
        "\n"
        "Eşik: Sayı sıfırdan büyükse kart kırmızı, sıfırsa yeşil.\n"
        "\n"
        "Yorum: Kritik listesi haftalık süreç gözden geçirmenin zorunlu gündemidir; kronik "
        "kritikler yapısal sorun işaretidir."
    ),

    "process.k_vektor": (
        "K-Vektör skorlama modelinin bu kurumda etkin olduğunu bildirir.\n"
        "\n"
        "Sınır: Kart yalnızca DURUM rozetidir — K-Vektör skor değeri göstermez; skorlar "
        "süreç satırlarında ve SP ekranlarında görünür. K-Vektör kapalı kurumlarda kart hiç "
        "görünmez.\n"
        "\n"
        "Yorum: K-Vektör açıkken süreç skorları ağırlıklı bütçe modeliyle hesaplanır — "
        "klasik ortalamayla kıyaslarken bunu hatırlayın."
    ),

    "process.surecler": (
        "Süreçleri ağaç veya pano (kanban) görünümünde listeler; başlıkta hedefte / risk "
        "altında / hedef dışı / veri yok sayaç rozetleri bulunur.\n"
        "\n"
        "Eşik: Hedefte 80+, risk altında 50-79, hedef dışı 50 altı; skorsuz süreçler 'veri "
        "yok' kolonundadır.\n"
        "\n"
        "Yorum: Pano görünümü durum dağılımını, ağaç görünümü hiyerarşiyi okutur — 'veri "
        "yok' kolonunu boşaltmak her iki görünümün de anlamını artırır."
    ),

    # ─────────────────── SÜREÇ KARNESİ ───────────────────

    "process_karne.surec_karnesi": (
        "Sürecin gösterge panosudur: göstergeler hedefte / risk altında / hedef dışı "
        "kolonlarında, seçili döneme göre skor saatleriyle gösterilir; dönem gezintisi, "
        "Excel ve yazdırma araçları üsttedir.\n"
        "\n"
        "Hesap: Kolon eşiği gösterge başarı yüzdesine göre: 80+ hedefte, 50-79 risk, 50 "
        "altı hedef dışı. Yüzde, seçili gösterim periyodunun (varsayılan çeyrek) "
        "değerinden hesaplanır ve yön dikkate alınır.\n"
        "\n"
        "Sınır: Periyot değiştikçe kolonlar değişebilir — çeyrek görünümde 'hedefte' olan "
        "gösterge yıllık bakışta farklı çıkabilir.\n"
        "\n"
        "Yorum: Karneyi dönem kapanışlarında ekiple birlikte okuyun; kolonlar tartışmanın "
        "gündem taslağıdır."
    ),

    "process_karne.genel_bilgiler": (
        "Sürecin genel durumunu özetler: sağlık skoru ve bandı, gösterge başarı dağılımı "
        "(halka grafik), faaliyet ilerleme çubuğu ve veri doluluk çubuğu.\n"
        "\n"
        "Hesap: Buradaki sağlık skoru, göstergelerin başarı yüzdelerinin DÜZ ortalamasıdır "
        "(hesaplanamayanlar hariç). Doluluk = dolu ay hücresi / (gösterge × 12).\n"
        "\n"
        "Eşik: Band — 85+ çok iyi, 70-84 iyi, 50-69 orta, altı geliştirilmeli. Halka "
        "kovaları: 70+ başarılı, 40-69 orta, 40 altı kritik.\n"
        "\n"
        "Sınır: Aynı sayfadaki AI özetin kullandığı sağlık skoru FARKLI bir formüldür "
        "(gösterge %70 + faaliyet %30 ağırlıklı) — iki sayı birebir örtüşmeyebilir. Band ve "
        "halka eşikleri de farklı ölçeklerdir.\n"
        "\n"
        "Yorum: Skorla birlikte doluluk çubuğuna bakın — düşük dolulukta skor az sayıda "
        "ölçümün temsilidir."
    ),

    "process_karne.ai_yonetici_ozeti": (
        "Süreç karnesinin üstünde 2-3 cümlelik yönetici özeti gösterir; kaynak rozeti "
        "'AI' veya 'otomatik' olur.\n"
        "\n"
        "Hesap: Önce her zaman kural tabanlı özet üretilir (sağlık skoru + öneriler); "
        "yapay zekâ erişimi varsa metin modele yeniden yazdırılır ve 'AI' rozeti görünür.\n"
        "\n"
        "Sınır: Model çıktısı deterministik değildir; erişim yoksa kural metni gösterilir. "
        "Özetin dayandığı sağlık skoru, gösterge %70 + faaliyet %30 ağırlıklı servis "
        "hesabıdır.\n"
        "\n"
        "Yorum: Özet iyi bir açılış cümlesidir; sayısal iddiaları karnedeki kartlardan "
        "doğrulayın."
    ),

    "process_karne.hedefte": (
        "Başarı yüzdesi 80 ve üzeri olan göstergeleri listeler.\n"
        "\n"
        "Hesap: Yüzde, seçili gösterim periyodunun değerinden yön dikkate alınarak "
        "hesaplanır.\n"
        "\n"
        "Yorum: Hedefte kolonu kalabalıksa iki ihtimal vardır: süreç gerçekten iyi ya da "
        "hedefler kolay — yıllık hedef revizyonunda ikincisini eleyin."
    ),

    "process_karne.risk_altinda": (
        "Başarı yüzdesi 50-79 arasında olan göstergeleri VE henüz ölçülemeyen (verisiz "
        "veya hedefsiz) göstergeleri listeler.\n"
        "\n"
        "Sınır: 'Risk altında' kolonu iki farklı durumu birlikte taşır — orta performans "
        "ile ölçülememe aynı kolonda birikir; verisiz göstergeler bu sayıyı ŞİŞİRİR.\n"
        "\n"
        "Yorum: Kolonu ikiye ayırarak okuyun: '—' değerli satırlar veri işi, yüzdesi olan "
        "satırlar performans işidir."
    ),

    "process_karne.hedef_disi": (
        "Başarı yüzdesi 50'nin altında olan göstergeleri listeler.\n"
        "\n"
        "Sınır: Ölçülemeyen göstergeler bu kolona DÜŞMEZ (risk kolonuna gider) — hedef "
        "dışı listesi yalnızca ölçülmüş düşük performansı içerir.\n"
        "\n"
        "Yorum: Bu kolon süreç toplantısının birincil gündemi; her satır için 'veri mi, "
        "hedef mi, icra mı' sorusunu sırayla sorun."
    ),

    "process_karne.kpi_performans_trend_analizi": (
        "Seçilen tek göstergenin yıl içindeki 12 aylık gerçekleşen değerlerini çizgi "
        "grafikle gösterir.\n"
        "\n"
        "Hesap: Takvim yılının 12 ayı sabittir; her ay o ayın toplulaştırılmış değeriyle "
        "çizilir, boş aylar atlanarak çizgi sürdürülür.\n"
        "\n"
        "Sınır: Çizilen HAM DEĞERDİR — başarı yüzdesi değil; hedef çizgisi gösterilmez. "
        "Tek gösterge çizilir, karşılaştırmalı seri yoktur.\n"
        "\n"
        "Yorum: Trendde ani sıçrama çoğu zaman birim/format değişikliğinin izidir — "
        "yorumlamadan önce veri girişini kontrol edin."
    ),

    "process_karne.surec_faaliyetleri": (
        "Sürecin faaliyetlerini pano (planlanan / devam eden / tamamlanan-iptal) veya 12 "
        "aylık takip tablosu görünümünde gösterir.\n"
        "\n"
        "Sınır: Faaliyet listesi yıla filtrelenmez (tüm aktif faaliyetler); yalnızca aylık "
        "işaretler seçili yıla aittir.\n"
        "\n"
        "Yorum: Pano durum dağılımını, tablo ay-ay temposunu okutur; ikisini birlikte "
        "kullanmak faaliyet disiplinini görünür kılar."
    ),

    "process_karne.faaliyet_toplam": (
        "Sürecin toplam aktif faaliyet sayısını gösterir.\n"
        "\n"
        "Sınır: Sayı yıldan bağımsızdır — tüm aktif faaliyetleri kapsar.\n"
        "\n"
        "Yorum: Göstergesi çok, faaliyeti az süreç 'ölçüyor ama iyileştirmiyor' "
        "profilidir; tersi de plansız koşuşturmadır — denge önemli."
    ),

    "process_karne.faaliyet_planlananlar": (
        "Henüz başlamamış (planlanan) faaliyetleri listeler.\n"
        "\n"
        "Sınır: Bu kolon 'diğerleri' kovasıdır — durumu tanınmayan veya boş bırakılmış "
        "faaliyetler de burada görünür.\n"
        "\n"
        "Yorum: Kolonda uzun süre bekleyen kayıtlar ya başlatılmalı ya da plandan "
        "çıkarılmalıdır; bekleyen plan listesi zamanla güven kaybettirir."
    ),

    "process_karne.faaliyet_devam_edenler": (
        "Devam etmekte olan faaliyetleri listeler.\n"
        "\n"
        "Hesap: Durum metni 'devam' içeren faaliyetler bu kolona düşer.\n"
        "\n"
        "Yorum: Aynı anda çok fazla 'devam eden' iş, bitirme değil başlama kültürünün "
        "işaretidir — sınırlı eşzamanlı iş ilkesi burada da geçerlidir."
    ),

    "process_karne.faaliyet_tamamlanan": (
        "Faaliyetlerin tamamlanma ORANINI yüzde olarak gösterir.\n"
        "\n"
        "Hesap: Tamamlanmış sayılan faaliyet / toplam faaliyet × 100. 'Tamamlanmış' "
        "sayılma üç yoldan olur: durum metni tamamlandı/gerçekleşti, ilerleme %100, veya "
        "en az bir aylık işaret.\n"
        "\n"
        "Sınır: Kart adı 'Tamamlanan' olsa da değer ADET değil YÜZDEDİR; ayrıca buradaki "
        "'tamamlanmış' tanımı pano kolonundakinden geniştir (tek ay işaretli faaliyet de "
        "sayılır) — iki gösterim farklı sayı verebilir.\n"
        "\n"
        "Yorum: Yüzde yüksek ama işler bitmemiş hissi varsa ay işaretlerinin gerçek "
        "tamamlanmayı mı yansıttığını sorgulayın."
    ),

    "process_karne.faaliyet_tamamlanan_iptal": (
        "Tamamlanmış veya iptal edilmiş faaliyetleri listeler.\n"
        "\n"
        "Hesap: Durum metni tamamlandı/gerçekleşti/iptal olan faaliyetler bu kolona "
        "düşer.\n"
        "\n"
        "Sınır: Sınıflama durum METNİNE bakar — ilerlemesi %100 ama durumu güncellenmemiş "
        "faaliyet bu kolona girmez (üstteki yüzde kartında ise sayılır).\n"
        "\n"
        "Yorum: Tamamlanan ve iptal edilenin aynı kolonda olması pratik bir sadeleştirmedir; "
        "iptal oranı yükseliyorsa planlama kalitesini ayrıca inceleyin."
    ),

    # ─────────────────── ANALİZ ───────────────────

    "analiz.secim_araclari": (
        "Analizin girdi çubuğudur: süreç arama ve seçimi, frekans (haftalık/aylık/"
        "çeyreklik) ve analiz tetikleme.\n"
        "\n"
        "Sınır: Kart veri ölçmez; diğer analiz kartları seçilen sürece göre dolar.\n"
        "\n"
        "Yorum: Frekans seçimi trend ve tahmini etkiler — ölçüm periyodunuzla uyumlu "
        "frekans seçin (aylık ölçülen göstergeyi haftalık analiz etmek boşluk üretir)."
    ),

    "analiz.saglik_skoru": (
        "Seçili sürecin sağlık skorunu 0-100 gösterir.\n"
        "\n"
        "Hesap: Göstergelerin başarı puanlarının AĞIRLIKLI ortalamasıdır; her göstergenin "
        "puanı en son ölçümünden, yön dikkate alınarak hesaplanır (artan: gerçekleşme/"
        "hedef; azalan: hedef/gerçekleşme; 0-100 kırpılır).\n"
        "\n"
        "Eşik: 80+ iyi (yeşil), 50-79 orta (turuncu), altı düşük (kırmızı).\n"
        "\n"
        "Sınır: Skor yalnızca SON ölçüme bakar — yıl geneli birleştirme yapılmaz; tek "
        "iyi/kötü ay skoru sürükleyebilir.\n"
        "\n"
        "Yorum: Skoru trend grafiğiyle birlikte okuyun; son ölçüm istisna olabilir."
    ),

    "analiz.trend_yonu": (
        "Seçili sürecin son dönem eğilim yönünü gösterir: artış, düşüş veya sabit.\n"
        "\n"
        "Hesap: Serinin ilk ve son değeri karşılaştırılır; %2'lik ölü bant içindeki fark "
        "'sabit' sayılır.\n"
        "\n"
        "Sınır: Yön, sürecin İLK göstergesinin serisinden türetilir — süreç genelinin "
        "bileşke trendi değildir; büyüklük değil yalnız yön verilir.\n"
        "\n"
        "Yorum: Yön okunu başlangıç noktası sayın; hangi göstergenin sürüklediğini trend "
        "grafiğindeki serilerden ayırt edin."
    ),

    "analiz.trend_grafigi": (
        "Sürecin tüm aktif göstergelerinin gerçekleşen değerlerini zaman serisi olarak "
        "çoklu çizgi grafikte gösterir; Excel'e indirilebilir.\n"
        "\n"
        "Hesap: Değerler seçilen frekansa göre dönem ortalamasıyla gruplanır.\n"
        "\n"
        "Sınır: Farklı birimli göstergeler aynı eksende çizilir — ölçek farkı küçük "
        "değerli serileri düzleştirir.\n"
        "\n"
        "Yorum: Tek seriyi incelemek için diğerlerini gösterge etiketinden geçici "
        "kapatın; birim farkı yanılgısının panzehiri budur."
    ),

    "analiz.tahmin_ozet": (
        "Bir sonraki dönem için öngörülen değeri gösterir.\n"
        "\n"
        "Hesap: Doğrusal regresyonla üretilen üç dönemlik tahminin İLK değeridir.\n"
        "\n"
        "Sınır: Tahmin, sürecin EN ÇOK ölçümü olan tek göstergesi üzerinden yapılır — "
        "süreç genelini temsil etmez; 'dönem' yaklaşık 30 gün varsayımıdır.\n"
        "\n"
        "Yorum: Tek sayıyı değil, grafikteki güven aralığıyla birlikte okuyun."
    ),

    "analiz.tahmin_grafigi": (
        "Geçmiş gerçekleşmeler ile gelecek üç dönemin tahminini birlikte çizer.\n"
        "\n"
        "Hesap: Yöntem DOĞRUSAL REGRESYONDUR (hareketli ortalama değil); son 24 ölçüm "
        "kullanılır, en az 3 sayısal nokta gerekir. Güven aralığı yaklaşık %95 düzeyinde "
        "(±1,96 standart hata) hesaplanır. Güven etiketi uyum gücüne (R²) göre verilir: "
        "0,70+ yüksek, 0,40-0,70 orta, altı düşük.\n"
        "\n"
        "Sınır: Doğrusal model mevsimselliği ve kırılmaları YAKALAMAZ; tahmin tek gösterge "
        "üzerindendir ve dönemler ~30 gün varsayımıyla türetilir.\n"
        "\n"
        "Yorum: 'Düşük güven' etiketli tahmini karar girdisi yapmayın — o etiket 'veri "
        "doğrusal seyretmiyor' demektir; önce ölçüm sıklığını artırın."
    ),

    "analiz.anomali_ozet": (
        "Taramada tespit edilen anomali sayısını gösterir.\n"
        "\n"
        "Hesap: Varsayılan yöntem z-skorudur (eşik 2,5) — son 180 günün verisi, gösterge "
        "başına en az 10 ölçüm gerekir.\n"
        "\n"
        "Yorum: Sayı yalnız kapıdır; hangi göstergede, ne zaman ve ne şiddette olduğunu "
        "yandaki listeden okuyun."
    ),

    "analiz.anomali_listesi": (
        "Tespit edilen anomalileri detaylarıyla listeler: gösterge, değer, tarih, sapma "
        "skoru ve karne bağlantısı; üstte kaç göstergenin tarandığı yazar.\n"
        "\n"
        "Hesap: Üç yöntem seçilebilir — z-skoru (varsayılan, eşik 2,5), IQR (çeyrekler "
        "arası aralık × 1,5) ve hareketli ortalama sapması. Şiddet, ortalamadan sapma "
        "yüzdesine göre: %50+ yüksek, %25-50 orta, altı düşük.\n"
        "\n"
        "Sınır: 10'dan az ölçümü olan göstergeler taranamaz ve sessizce atlanır — 'anomali "
        "yok' mesajı bu göstergeler için 'bakılamadı' demektir. Etiket her yöntemde "
        "'z-skor' yazar; IQR/hareketli ortalama seçiliyken skor farklı ölçektedir.\n"
        "\n"
        "Yorum: Anomaliyi kaynağında doğrulayın — birim değişikliği ve toplu veri girişi "
        "en sık iki yalancı pozitiftir."
    ),

    # ─────────────────── YÖNETİM ÖZETİ ───────────────────

    "yonetim_ozeti.kurum_skoru": (
        "Kurumun toplam skorunu tek sayıda gösterir; strateji, süreç, proje ve bireysel "
        "bileşen skorlarının ağırlıklı ortalamasıdır.\n"
        "\n"
        "Hesap: Varsayılan ağırlıklar — strateji 2, süreç 3, proje 3, bireysel 2 (kuruma "
        "özel ayarlanabilir).\n"
        "\n"
        "Eşik: 80+ sağlıklı (yeşil), 60-79 izlenmeli (sarı), altı kritik (kırmızı). "
        "Bileşenlerdeki kritik kalemler toplam 6'yı aşarsa band skora bakılmaksızın "
        "kırmızıya çekilir.\n"
        "\n"
        "Sınır: Skor 5 dakikalık önbellekten gelir — az önce girilen veri hemen "
        "yansımayabilir.\n"
        "\n"
        "Yorum: Tek sayı yönetim iletişimi içindir; karar için dört bileşen kartına inin."
    ),

    "yonetim_ozeti.ks_skoru": (
        "Strateji bileşen skorunu gösterir.\n"
        "\n"
        "Hesap: Süreç sayısı / strateji sayısı oranından türetilen KAPSAMA skorudur "
        "(100'de kırpılır).\n"
        "\n"
        "Eşik: 80+ yeşil, 60-79 sarı, altı kırmızı.\n"
        "\n"
        "Sınır: Başlık performans çağrıştırsa da bu YAPISAL bir orandır — stratejilerin "
        "BAŞARISINI değil, süreçlerle desteklenme düzeyini ölçer; strateji başarısı için "
        "K-Radar/K-Rapor ekranlarına bakın.\n"
        "\n"
        "Yorum: Düşük skor 'az süreçle çok strateji' demektir — ya süreç bağlayın ya "
        "strateji sadeleştirin."
    ),

    "yonetim_ozeti.kp_skoru": (
        "Süreç bileşen skorunu gösterir: süreç göstergelerinin ağırlıklı ortalama "
        "başarısı.\n"
        "\n"
        "Hesap: Her göstergenin SON ölçümü, yön dikkate alınarak 0-100 puana çevrilir; "
        "ağırlıklı ortalanır.\n"
        "\n"
        "Eşik: 80+ yeşil, 60-79 sarı, altı kırmızı; puanı 70'in altında kalan gösterge "
        "sayısı 3'ü bulursa band kırmızıya zorlanır.\n"
        "\n"
        "Sınır: Tek (son) ölçüm esaslıdır — yıl geneli birleştirme yapılmaz.\n"
        "\n"
        "Yorum: Bandı kırmızıya çeken çoğu zaman ortalama değil kritik gösterge "
        "sayısıdır — önce o listeye bakın."
    ),

    "yonetim_ozeti.kpr_skoru": (
        "Proje bileşen skorunu gösterir: projelerin gecikme cezalı sağlık ortalaması.\n"
        "\n"
        "Hesap: Proje puanı = sağlık skoru − (geciken görev × 5, en çok 35 ceza); "
        "projelerin düz ortalaması alınır.\n"
        "\n"
        "Eşik: 80+ yeşil, 60-79 sarı, altı kırmızı; puanı 60 altı proje sayısı 2'yi "
        "bulursa band kırmızıya zorlanır.\n"
        "\n"
        "Sınır: Bu bileşen YIL FİLTRESİZDİR — tüm arşivlenmemiş projeleri kapsar; hiç "
        "proje yoksa skor 0 ve band kırmızı görünür (bu 'kötü' değil 'kapsam yok' "
        "demektir).\n"
        "\n"
        "Yorum: Ceza mekanizması gecikmeyi görünür kılar — sağlığı yüksek ama cezalı "
        "projelerde sorun planlama disiplinindedir."
    ),

    "yonetim_ozeti.bireysel_skoru": (
        "Bireysel performans bileşen skorunu gösterir: kişisel göstergelerin ağırlıklı "
        "ortalama başarısı.\n"
        "\n"
        "Hesap: Her bireysel göstergenin son ölçümü yön dikkate alınarak puanlanır ve "
        "ağırlıklı ortalanır.\n"
        "\n"
        "Eşik: 80+ yeşil, 60-79 sarı, altı kırmızı; 70 altı gösterge sayısı 4'ü bulursa "
        "band kırmızıya zorlanır.\n"
        "\n"
        "Yorum: Bu skor kurumun 'kişisel hedef kültürünün' nabzıdır — düşükse önce veri "
        "girme alışkanlığına, sonra hedef kalitesine bakın."
    ),

    "yonetim_ozeti.geciken_isler": (
        "Dikkat gerektiren işleri altı sayaçla listeler: geciken görev, geciken faaliyet, "
        "süresi geçen proje, düşük sağlıklı proje, açık RAID maddesi ve 7 gün içinde "
        "bitecek görev.\n"
        "\n"
        "Eşik: Sıfırdan büyük her sayaç kırmızı gösterilir.\n"
        "\n"
        "Yorum: Bu kart 'bugün kimi arayacağım' listesidir; sayaçlar düzenli sıfırlanmıyorsa "
        "sorun operasyonel değil yapısaldır (kapasite/planlama)."
    ),

    "yonetim_ozeti.kpi_ozet": (
        "Gösterge özetini beş satırda verir: toplam gösterge, veri girilen, hedef üstü "
        "yüzdesi, açık risk ve geciken faaliyet.\n"
        "\n"
        "Hesap: Hedef üstü % = gerçekleşmesi hedefe eşit/üstü sayısal ölçümler / "
        "karşılaştırılabilir ölçümler × 100.\n"
        "\n"
        "Sınır: Bu oran yön ve ağırlık GÖZETMEZ — 'azalması iyi' göstergelerde hedef "
        "üstü olmak başarı değildir; skor kartlarındaki yön-duyarlı hesaptan farklıdır "
        "(bkz. D0 kaydı).\n"
        "\n"
        "Yorum: Hedef üstü yüzdesini kaba nabız olarak okuyun; hassas okuma bileşen skor "
        "kartlarındadır."
    ),

    "yonetim_ozeti.en_dusuk_5": (
        "Hedef üstü oranı en düşük beş stratejiyi ilerleme çubuklarıyla listeler.\n"
        "\n"
        "Hesap: Strateji başına oran = bağlı göstergelerin hedefe eşit/üstü ölçüm oranı; "
        "verisi olmayan stratejiler listeye giremez.\n"
        "\n"
        "Eşik: %70+ yeşil, %50-70 turuncu, altı kırmızı.\n"
        "\n"
        "Sınır: Hesap TAKVİM yılına sabittir (seçili plan dönemi değil) ve yön/ağırlık "
        "gözetmez; listede olmayan strateji 'iyi' değil 'ölçümsüz' olabilir.\n"
        "\n"
        "Yorum: Listeyi kaynak tartışmasının girişi yapın; ama önce her stratejinin ölçüm "
        "kapsamını doğrulayın."
    ),

    "yonetim_ozeti.hedef_radar": (
        "Hedef değişikliklerini denetler: son bir yılda kaç hedef değişti, kaçı aşağı "
        "çekildi, kaçı dönem kapanışına yakın (son 7 gün) aşağı çekildi ve hangi "
        "göstergeler birden çok kez revize edildi.\n"
        "\n"
        "Hesap: Değişiklikler hedef denetim izinden okunur; %1'in altındaki oynamalar "
        "'sabit' sayılır. 'Kapanışa yakın + aşağı' kombinasyonu en kritik sinyaldir.\n"
        "\n"
        "Sınır: Denetim izi 2026-07-15'te açıldı — öncesindeki değişiklikler KAYITSIZDIR; "
        "'değişiklik yok' geçmiş için kanıt değildir. Aralık ('90-100') ve '-' hedefleri "
        "yön hesabına girmez. Radar niyet okumaz — olguyu gösterir, gerekçe tartışması "
        "insanlara aittir.\n"
        "\n"
        "Yorum: Dönem sonuna yakın hedef düşürme her zaman manipülasyon değildir — ama her "
        "zaman AÇIKLAMA gerektirir; radarın işlevi bu konuşmayı başlatmaktır."
    ),
}
