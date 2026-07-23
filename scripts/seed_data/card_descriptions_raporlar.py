# -*- coding: utf-8 -*-
"""Raporlar modülü kart açıklamaları — 94 kart (raporlar_* önekleri).

Yazım sözleşmesi için bkz. card_descriptions_k_radar.py başlığı.
Kod bağlamı 2026-07-21'de 4 paralel keşif ajanıyla route/servis/template/JS
düzeyinde çıkarıldı; formüller dosya:satır doğrulamalıdır (ajan raporları).

Koddan doğrulanmış ortak kurallar:
  - Tüm rapor route'ları @login_required + @require_module("k_rapor") korumalı.
  - AI kartları tek geçit llm_gateway.call_llm kullanır; sağlayıcı kuruma göre
    değişir (BYOK ya da sistem Gemini), anahtar yoksa deterministik şablona düşer.
  - Initiative.progress_pct MANUEL girilen alandır — hiçbir yerde KPI/faaliyet
    tamamlanmasından türetilmez; ilerleme gösteren tüm kartlar için geçerli sınır.
"""

DESCRIPTIONS: dict[str, str] = {

    # ─────────────────────────── AI COACH ───────────────────────────

    "raporlar_ai_coach.ai_onerisi": (
        "En düşük performanslı üç stratejiye yönelik, yapay zekâ ile üretilmiş serbest metin "
        "koçluk önerisi gösterir.\n"
        "\n"
        "Hesap: Öneri metninin dayandığı skorlar deterministiktir — her stratejinin skoru, bağlı "
        "süreç skorlarının düz ortalamasıdır. Metin ise yapay zekâya bu tablo verilerek yazdırılır.\n"
        "\n"
        "Sınır: Öneri metni her açılışta değişebilir — kurumunuzun yapay zekâ yapılandırmasına "
        "göre farklı modeller kullanılır, çıktı deterministik değildir. Yapay zekâ erişimi yoksa "
        "sistem sabit bir şablon metin üretir; şablon metin veri sayılarını doğru yansıtır ama "
        "özgün analiz içermez.\n"
        "\n"
        "Yorum: Öneriyi karar olarak değil tartışma başlangıcı olarak okuyun; metindeki sayısal "
        "iddiaları soldaki skor listesinden doğrulayın."
    ),

    "raporlar_ai_coach.en_dusuk_performansli_3_strateji": (
        "Skoru hesaplanabilen stratejiler arasından en düşük üçünü skor rozetiyle listeler.\n"
        "\n"
        "Hesap: Strateji skoru = stratejiye (alt stratejiler üzerinden) bağlı süreçlerin skor "
        "ortalaması. Liste artan skora göre sıralanır, ilk üç alınır.\n"
        "\n"
        "Eşik: 50 ve üzeri turuncu, 50 altı kırmızı rozet.\n"
        "\n"
        "Sınır: Hiç süreç skoru olmayan stratejiler sıralamaya HİÇ girmez — yani gerçekte en zayıf "
        "strateji, hiç ölçülmediği için bu listede görünmüyor olabilir.\n"
        "\n"
        "Yorum: Listeye girmeyen stratejilerin ölçümsüzlükten mi yoksa iyi performanstan mı "
        "görünmediğini ayırt etmek için strateji-süreç bağlarını kontrol edin."
    ),

    # ─────────────────────────── AI DANIŞMAN ───────────────────────────

    "raporlar_ai_danisman.sayfa": (
        "Sistem verisinden üretilen 3-5 strateji pivot önerisini (yeniden odaklan / sonlandır / "
        "hızlandır / yeni girişim / risk azalt) kartlar halinde sunar.\n"
        "\n"
        "Hesap: Yapay zekâ erişimi varsa öneriler kurum özet verisi + son tetikleyici olaylarla "
        "modele yazdırılır. Erişim yoksa kural tabanlı üretim devreye girer: hedefte olan oran "
        "%50'nin altındaysa, geciken iş oranı %20'yi aşarsa, kritik uyarı veya yüksek anomali "
        "varsa, süren girişimlerin ortalama ilerlemesi %30'un altındaysa ilgili öneri tetiklenir.\n"
        "\n"
        "Sınır: Yapay zekâ çıktısı deterministik değildir ve kurum yapılandırmasına göre model "
        "değişir. Hiçbir kural tetiklenmezse 'genel durum sağlıklı' önerisi gösterilir — bu, "
        "analiz yapılamadığı anlamına gelmez, eşiklerin aşılmadığı anlamına gelir.\n"
        "\n"
        "Yorum: Önerinin kaynağını (yapay zekâ mı kural mı) ayırt edemiyorsanız gerekçe metnindeki "
        "sayıları ilgili panolardan doğrulayarak ilerleyin."
    ),

    # ─────────────────────────── AI SUNUM ───────────────────────────

    "raporlar_ai_sunum.slayt_yapisi": (
        "Üretilecek sunumun slayt başlıklarını ve her slaytın içerik özetini önizleme olarak "
        "listeler.\n"
        "\n"
        "Sınır: Önizleme listesi ile gerçekte üretilen dosya AYRIŞIR — önizleme 15 slayt "
        "gösterir, indirilen PPTX şu an 8 ana slayt içerir (kapak, yönetici özeti, stratejik yıl "
        "özeti, ana stratejiler/K-Vektör, girişim portföyü, veri akışı, öneriler, kapanış). "
        "Görsel grafikler henüz dahil değildir.\n"
        "\n"
        "Yorum: Sunumu dağıtmadan önce indirip içeriğini kontrol edin; önizlemedeki her başlığın "
        "dosyada birebir karşılığı yoktur."
    ),

    "raporlar_ai_sunum.sunum_hazir": (
        "Kurum adı ve plan yılıyla başlıklandırılmış sunum dosyasını (PPTX) tek tıkla üretip "
        "indirir.\n"
        "\n"
        "Hesap: K-Vektör ağırlık yüzdeleri ham ağırlığın toplam ağırlığa oranından hesaplanır. "
        "Yönetici özeti slaytı yapay zekâ ile yazdırılır; erişim yoksa sayıları doğru yansıtan "
        "sabit şablon cümle kullanılır.\n"
        "\n"
        "Sınır: Yönetici özeti metni deterministik değildir — aynı veriyle iki üretim farklı "
        "cümleler verebilir. Sunum kitaplığı sunucuda kurulu değilse üretim hata verir.\n"
        "\n"
        "Yorum: Yapay zekâ özetindeki nitel yorumları (örn. 'başarılı bir yıl') veriye karşı "
        "kontrol etmeden yönetim sunumuna taşımayın."
    ),

    "raporlar_ai_sunum.sunumda_kullanilacak_veriler": (
        "Sunuma girecek veri hacmini beş sayaçla gösterir: strateji, süreç, stratejik girişim, "
        "çalışan ve KPI ölçüm sayısı.\n"
        "\n"
        "Hesap: Her sayaç aktif kayıtların adedidir.\n"
        "\n"
        "Sınır: Sayaçların kapsamı farklıdır — strateji ve süreç sayıları aktif plan yılına "
        "filtrelidir, KPI ölçüm sayısı ise TÜM yılları kapsar. 'Sunumda kullanılacak' ifadesine "
        "rağmen ölçüm sayacı sunumun yıl kapsamından geniştir.\n"
        "\n"
        "Yorum: Ölçüm sayısını yıl bazlı raporlarla karşılaştırırken bu kapsam farkını hesaba "
        "katın."
    ),

    # ─────────────────────────── AUDİT PAKETİ ───────────────────────────

    "raporlar_audit_paketi.denetci_icin_hazir_pdf": (
        "Dış denetçilere verilmek üzere kurumsal özet PDF'ini tek tıkla üretip indirir.\n"
        "\n"
        "Hesap: PDF'teki iki faktörlü doğrulama oranı = 2FA'sı açık kullanıcı / toplam aktif "
        "kullanıcı × 100. Diğer bölümler kayıt sayımlarıdır. Denetim günlüğü son 90 günün en "
        "yeni 50 kaydını içerir.\n"
        "\n"
        "Sınır: Dosya anlık üretilir — indirildiği andaki veriyi yansıtır, sonradan değişen "
        "veriyle güncellenmez.\n"
        "\n"
        "Yorum: Denetçiye vermeden önce üretim tarihini not edin; denetim dönemi ile 90 günlük "
        "günlük penceresinin örtüştüğünü kontrol edin."
    ),

    "raporlar_audit_paketi.kullanim_amaci": (
        "Audit paketinin hangi senaryolarda kullanılacağını açıklayan sabit bilgi kartıdır: dış "
        "denetim, ISO uyum kanıtı, yönetim brifingi ve düzenleyici raporlama.\n"
        "\n"
        "Sınır: Bu kart veri ölçmez; içeriği sabittir ve kurumunuzun verisine göre değişmez.\n"
        "\n"
        "Yorum: Paketin belirli bir standardın (örn. ISO 9001) zorunlu formatını karşıladığı "
        "iddiası yoktur — denetçinizin format beklentisini ayrıca doğrulayın."
    ),

    "raporlar_audit_paketi.pdf_bolumleri": (
        "Üretilecek PDF'in bölüm listesini gösteren sabit bilgi kartıdır.\n"
        "\n"
        "Sınır: Listede altı bölüm yazsa da üretilen PDF şu an DÖRT bölüm içerir: kurum "
        "bilgileri, stratejik plan yapısı, son 90 gün denetim günlüğü ve kullanıcı güvenlik "
        "özeti. 'KPI Özeti' ve 'Risk Özeti' bölümleri henüz dosyada üretilmemektedir.\n"
        "\n"
        "Yorum: Denetçiye KPI veya risk verisi gerekiyorsa ilgili raporları (KPI panoları, risk "
        "ısı haritası) ayrıca dışa aktarın."
    ),

    # ─────────────────────────── BI CONNECTOR ───────────────────────────

    "raporlar_bi_connector.excel_google_sheets": (
        "Excel (Veri → Web'den) ve Google Sheets (IMPORTDATA formülü) ile KPI verisine bağlanma "
        "adımlarını anlatan sabit rehber kartıdır.\n"
        "\n"
        "Sınır: Rehberin işaret ettiği CSV çıktısı en fazla 10.000 satır döndürür; sınır "
        "aşıldığında veri sessizce kırpılır ve yalnızca yanıt başlığında uyarı taşınır. Canlı "
        "bağlantı (OData) henüz yoktur; veri her içe aktarmada anlık kopyadır.\n"
        "\n"
        "Yorum: Büyük veri setlerinde satır sayınızı bilerek bağlanın; 10.000'e yakın toplamlar "
        "eksik veri şüphesiyle kontrol edilmelidir."
    ),

    "raporlar_bi_connector.power_bi_baglanti_rehberi": (
        "Power BI Desktop'ta Get Data → Web adımıyla KPI CSV'sine bağlanmayı anlatan sabit "
        "rehber kartıdır.\n"
        "\n"
        "Sınır: Yalnızca Import modu desteklenir — Direct Query çalışmaz; veri, yenileme "
        "yapılana kadar bağlandığı andaki kopyadır. CSV kaynağı en fazla 10.000 satırla "
        "sınırlıdır ve aşımda sessizce kırpılır.\n"
        "\n"
        "Yorum: Power BI raporlarınıza otomatik yenileme kurarken bu kopya-veri doğasını ve "
        "satır sınırını hesaba katın."
    ),

    "raporlar_bi_connector.tableau_baglanti_rehberi": (
        "Tableau Desktop ile KPI CSV'sine bağlanma adımlarını anlatan sabit rehber kartıdır.\n"
        "\n"
        "Sınır: Otomatik yenileme için Tableau Server gerekir; masaüstü bağlantısı anlık "
        "kopyadır. CSV kaynağı en fazla 10.000 satır döndürür, aşımda sessizce kırpılır.\n"
        "\n"
        "Yorum: Tableau panolarını dağıtmadan önce veri tazeliği beklentisini (anlık kopya mı, "
        "sunucu yenilemesi mi) netleştirin."
    ),

    # ─────────────────────────── BİREYSEL HİZALAMA ───────────────────────────

    "raporlar_bireysel_hizalama.bireysel_pg_ler": (
        "Her kullanıcının bireysel performans göstergelerinin kaçının kurum süreçlerine bağlı "
        "olduğunu ve hizalama yüzdesini listeler.\n"
        "\n"
        "Hesap: Hizalama % = kaynak süreç veya kaynak gösterge bağı DOLU olan bireysel PG sayısı "
        "/ kullanıcının toplam bireysel PG'si × 100. Genel hizalama, kullanıcı yüzdelerinin düz "
        "ortalamasıdır.\n"
        "\n"
        "Eşik: %70 ve üzeri yeşil, %40-70 turuncu, altı kırmızı.\n"
        "\n"
        "Sınır: 'Hizalama' burada içerik uyumu değil, bağ alanının dolu OLMASIDIR — yanlış "
        "sürece bağlanmış bir PG de hizalı sayılır. Hiç bireysel PG'si olmayan kullanıcılar "
        "listeye girmez; tablo en fazla 50 kullanıcı gösterir ama özet tüm PG'li kullanıcıları "
        "kapsar.\n"
        "\n"
        "Yorum: Düşük hizalama, bireysel hedeflerin kurum stratejisinden kopuk konduğunun ilk "
        "işaretidir; yüksek hizalamada ise bağların doğru sürece işaret ettiğini örneklemle "
        "kontrol edin."
    ),

    # ─────────────────────────── BİREYSEL KARNE BATCH ───────────────────────────

    "raporlar_bireysel_karne_batch.her_karne_icerigi": (
        "Toplu üretimde her çalışan karnesinin içereceği bölümleri açıklayan bilgi kartıdır: "
        "kimlik bilgileri, PG sayısı ve hizalama yüzdesi, PG detay tablosu, üretim notu.\n"
        "\n"
        "Hesap (karne içinde): hizalama % = kaynak bağı dolu PG / toplam PG × 100; PG tablosunda "
        "tip, kaynak süreç bağı varsa 'Kurumdan', yoksa 'Bireysel' yazılır.\n"
        "\n"
        "Sınır: Her karnede en fazla ilk 30 PG listelenir; daha fazlası olan çalışanlarda tablo "
        "kırpılır.\n"
        "\n"
        "Yorum: Karneyi performans değerlendirme kanıtı olarak kullanmadan önce 30 PG sınırının "
        "çalışanı eksik yansıtıp yansıtmadığına bakın."
    ),

    "raporlar_bireysel_karne_batch.toplu_uretim_zip": (
        "Bireysel PG'si olan tüm çalışanların karnelerini tek ZIP dosyasında toplu üretir; "
        "önizlemede kişi sayısı ve tahmini boyut gösterilir.\n"
        "\n"
        "Hesap: Tahmini boyut = kişi sayısı × 0,05 MB. ZIP içinde her kullanıcı için bir PDF "
        "bulunur.\n"
        "\n"
        "Sınır: Üretim en fazla 100 kullanıcıyla sınırlıdır — önizlemedeki kişi sayısı 100'ü "
        "aşsa bile ZIP yalnızca ilk 100 çalışanı içerir. Bireysel PG'si olmayan çalışanlar hiç "
        "dahil edilmez.\n"
        "\n"
        "Yorum: 100'den fazla PG'li çalışanınız varsa üretimin eksiksiz olduğunu varsaymayın; "
        "ZIP içindeki dosya sayısını kontrol edin."
    ),

    # ─────────────────────────── CARBON TREND ───────────────────────────

    "raporlar_carbon_trend.yillik_trend": (
        "Kurumun Scope 1, 2 ve 3 emisyonlarını (tCO₂e) yıllara göre yığılmış sütun grafikte "
        "gösterir.\n"
        "\n"
        "Hesap: Her yıl için üç kapsamın değerleri ayrı ayrı toplanır; yıl toplamı üçünün "
        "toplamıdır. Özetteki 'ilk yıla göre' değişim, son yıl toplamı ile ilk yıl toplamının "
        "farkıdır.\n"
        "\n"
        "Eşik: Değişim sıfır veya negatifse (azalma) yeşil, artıysa kırmızı gösterilir.\n"
        "\n"
        "Sınır: Değerler ESG modülüne girildiği gibi toplanır — birim dönüşümü YAPILMAZ; farklı "
        "birimlerle girilmiş metrikler varsa toplam yanıltıcı olur.\n"
        "\n"
        "Yorum: Trend yorumlamadan önce üç kapsamın da aynı birimle ve her yıl için eksiksiz "
        "girildiğini doğrulayın; eksik yıl girişleri sahte düşüş gibi görünür."
    ),

    # ─────────────────────────── CFO DASHBOARD ───────────────────────────

    "raporlar_cfo_dashboard.durum_dagilimi": (
        "Stratejik girişimlerin durum alanına göre adet dağılımını listeler.\n"
        "\n"
        "Hesap: Aktif girişimler durum değerine göre gruplanıp sayılır.\n"
        "\n"
        "Sınır: Durum etiketleri veritabanındaki ham değerlerdir; Türkçe karşılık eşlemesi "
        "yapılmaz.\n"
        "\n"
        "Yorum: Dağılım, portföyün yürütme evresini gösterir; 'planlandı' yığılması başlatma "
        "darboğazına, 'beklemede' yığılması kaynak sorununa işaret edebilir."
    ),

    "raporlar_cfo_dashboard.en_buyuk_5_stratejik_girisim": (
        "Toplam bütçesi en yüksek beş stratejik girişimi bütçe, harcama ve kullanım yüzdesiyle "
        "listeler.\n"
        "\n"
        "Hesap: Girişimler toplam bütçeye göre azalan sıralanır, ilk beş alınır. Kullanım % = "
        "harcanan / toplam bütçe × 100.\n"
        "\n"
        "Eşik: Kullanım %100'ü aşarsa kırmızı gösterilir.\n"
        "\n"
        "Sınır: Sıralama yalnızca toplam bütçeye göredir — harcama hızı, öncelik veya stratejik "
        "önem sıralamayı etkilemez.\n"
        "\n"
        "Yorum: 'En büyük' burada 'en pahalı' demektir; en riskli veya en önemli anlamına "
        "gelmez. Bütçe aşımı satırlarını girişim sahibiyle birlikte inceleyin."
    ),

    "raporlar_cfo_dashboard.strateji_bazli_butce_atifi": (
        "Girişim bütçelerinin bağlı oldukları ana stratejiye göre toplandığı tabloyu gösterir: "
        "strateji başına bütçe, harcama, kullanım yüzdesi ve girişim sayısı.\n"
        "\n"
        "Hesap: Her girişimin bütçesi ve harcaması strateji kimliğine göre toplanır; stratejisi "
        "olmayan girişimler '(stratejisiz)' grubunda birikir. Bütçeye göre azalan ilk 10 satır "
        "gösterilir.\n"
        "\n"
        "Eşik: Kullanım %90'ı aşarsa kırmızı.\n"
        "\n"
        "Sınır: Atıf yalnızca girişim-strateji bağı üzerinden yapılır; alt strateji veya süreç "
        "kırılımı yoktur.\n"
        "\n"
        "Yorum: '(stratejisiz)' satırı büyükse bütçenin bir kısmı stratejik plana bağlanmadan "
        "harcanıyor demektir — yönetişim açısından ilk bakılacak satır budur."
    ),

    # ─────────────────────────── CHRO DASHBOARD ───────────────────────────

    "raporlar_chro_dashboard.departman_dagilimi": (
        "Aktif kullanıcıların departmanlara göre dağılımını yatay çubuklarla gösterir.\n"
        "\n"
        "Hesap: Kullanıcılar departman alanına göre gruplanıp sayılır; en kalabalık 15 departman "
        "gösterilir.\n"
        "\n"
        "Sınır: Departmanı boş olan kullanıcılar '(belirsiz)' grubunda toplanır. 15'ten fazla "
        "departman varsa küçükler görünmez.\n"
        "\n"
        "Yorum: '(belirsiz)' çubuğu büyükse önce kullanıcı profillerindeki departman alanını "
        "tamamlatın; aksi halde tüm İK analizleri eksik veriyle çalışır."
    ),

    "raporlar_chro_dashboard.en_cok_bireysel_pg_sahibi_top_10": (
        "Bireysel performans göstergesi sayısı en yüksek 10 kullanıcıyı listeler.\n"
        "\n"
        "Hesap: Aktif kullanıcıların aktif bireysel PG'leri sayılır, azalan sıralanır, ilk 10 "
        "alınır.\n"
        "\n"
        "Sınır: Sayı, hedeflerin niteliğini söylemez — çok PG'li kullanıcı iyi yönetilen değil, "
        "aşırı yüklenmiş de olabilir.\n"
        "\n"
        "Yorum: Uç değerleri iki yönden okuyun: PG enflasyonu (çok sayıda önemsiz hedef) ve "
        "yük dengesizliği. Departman ortalamasıyla karşılaştırmak sağlıklı okuma sağlar."
    ),

    "raporlar_chro_dashboard.en_cok_surec_uyeligi_top_5": (
        "En fazla aktif sürece üye olan beş kullanıcıyı süreç sayısıyla listeler.\n"
        "\n"
        "Hesap: Süreç üyelik kayıtları kullanıcı başına sayılır; yalnızca aktif süreçlerdeki "
        "üyelikler dahildir.\n"
        "\n"
        "Sınır: Pasif süreçlerdeki üyelikler sayılmaz; üyelik, fiilî iş yükünü değil atanmışlığı "
        "gösterir.\n"
        "\n"
        "Yorum: Tepedeki kişiler kurumun 'düğüm noktaları'dır — ayrılmaları hâlinde en çok "
        "süreç etkilenir. Yedekleme planlaması için ilk bakılacak listedir."
    ),

    "raporlar_chro_dashboard.rol_dagilimi": (
        "Aktif kullanıcıların sistem rollerine göre dağılımını gösterir.\n"
        "\n"
        "Hesap: Kullanıcılar rol adına göre gruplanıp sayılır; etiketler Türkçe kanonik rol "
        "adlarıyla gösterilir.\n"
        "\n"
        "Yorum: Yönetici rollerinin oranı yetki hijyeni için izlenmelidir — geniş yetkili rol "
        "sayısının zamanla sessizce artması tipik bir güvenlik erozyonudur."
    ),

    # ─────────────────────────── INITIATIVE BUBBLE ───────────────────────────

    "raporlar_initiative_bubble.portfoy_balon_grafigi": (
        "Tüm stratejik girişimleri tek grafikte konumlandırır: yatay eksen ilerleme, dikey eksen "
        "bütçe kullanımı, balon boyutu toplam bütçe, renk öncelik.\n"
        "\n"
        "Hesap: Dört boyut da girişim kaydındaki alanlardan okunur; kadran ayrımı her iki "
        "eksenin %50 çizgisidir. Sol üst bölge (az ilerleme + çok harcama) kırmızı, sağ alt "
        "bölge (çok ilerleme + az harcama) yeşil gölgelenir.\n"
        "\n"
        "Sınır: İlerleme yüzdesi girişim kartına ELLE girilen değerdir — faaliyet veya KPI "
        "tamamlanmasından hesaplanmaz. Grafik, girilen beyana güvenir.\n"
        "\n"
        "Yorum: Sol üst kadrandaki büyük balonlar (çok bütçeli, az ilerlemiş, bütçesi tükenen "
        "girişimler) portföyün en acil gündem maddesidir."
    ),

    "raporlar_initiative_bubble.yatay_eksen_x": (
        "Grafikte yatay eksenin girişimin tamamlanma yüzdesini gösterdiğini açıklar; sağa "
        "gidildikçe iş tamamlanmaya yaklaşır.\n"
        "\n"
        "Hesap: Konum = ilerleme % / 100 (0-100 aralığına kırpılır).\n"
        "\n"
        "Sınır: İlerleme, girişim kartına elle girilen beyandır; faaliyet/KPI verisinden "
        "türetilmez. Güncellenmeyen girişim olduğundan daha geride görünür.\n"
        "\n"
        "Yorum: Eksendeki konumu okurken girişimin son güncelleme tarihini de kontrol edin."
    ),

    "raporlar_initiative_bubble.dikey_eksen_y": (
        "Grafikte dikey eksenin bütçe kullanım oranını gösterdiğini açıklar; yukarı çıkıldıkça "
        "bütçe tükenmektedir.\n"
        "\n"
        "Hesap: Bütçe kullanımı % = harcanan / toplam bütçe × 100; toplam bütçe sıfırsa 0 kabul "
        "edilir.\n"
        "\n"
        "Yorum: İlerlemeden hızlı yükselen (eğimi dik) girişimler bütçeyi işten önce tüketiyor "
        "demektir — erken uyarı olarak okuyun."
    ),

    "raporlar_initiative_bubble.daire_boyutu": (
        "Balon büyüklüğünün girişimin toplam bütçesiyle orantılı olduğunu açıklar.\n"
        "\n"
        "Hesap: Yarıçap, bütçenin portföydeki en büyük bütçeye oranının kareköküyle ölçeklenir "
        "ve 10-46 piksel aralığına kırpılır.\n"
        "\n"
        "Sınır: Karekök ölçekleme küçük bütçeleri görece büyük gösterir; iki balonun alan oranı "
        "bütçe oranıyla birebir değildir. Bütçesiz girişimler en küçük boyutta görünür.\n"
        "\n"
        "Yorum: Kesin bütçe karşılaştırması için balona değil detay tablosundaki tutarlara bakın."
    ),

    "raporlar_initiative_bubble.daire_rengi": (
        "Balon renginin girişimin öncelik seviyesini kodladığını açıklar: kırmızı kritik, "
        "turuncu yüksek, mavi orta, gri düşük. Saydamlık ayrıca durumu yansıtır (tamamlanan "
        "soluk, iptal çok soluk, süren tam renk).\n"
        "\n"
        "Sınır: Renk, hesaplanan bir risk değil kullanıcının atadığı öncelik alanıdır.\n"
        "\n"
        "Yorum: Kırmızı yoğunluğu 'her şey kritik' beyan alışkanlığından da kaynaklanabilir — "
        "öncelik dağılımının anlamlı olması için kritik etiketinin seçici kullanılması gerekir."
    ),

    "raporlar_initiative_bubble.4_kadran_nasil_yorumlanir": (
        "Grafiğin dört kadranının nasıl okunacağını açıklayan sabit bilgi kartıdır: sağ alt "
        "ideal (çok ilerleme, az harcama), sağ üst tamamlanıyor, sol alt başlangıç, sol üst "
        "riskli (az ilerleme, çok harcama).\n"
        "\n"
        "Hesap: Kadran sınırları her iki eksenin %50 orta çizgisidir.\n"
        "\n"
        "Yorum: Kadran okuması kaba bir tarama aracıdır; sınıra yakın balonlar için detay "
        "tablosundaki gerçek yüzdelere inin."
    ),

    "raporlar_initiative_bubble.detay_tablosu": (
        "Grafikteki her girişimin sayısal detayını tabloda verir: kod, ad, durum, öncelik, "
        "toplam/harcanan bütçe, kullanım yüzdesi, ilerleme ve yıl aralığı.\n"
        "\n"
        "Eşik: Bütçe kullanımı %100'ü aşan satırlar kırmızı ve kalın gösterilir.\n"
        "\n"
        "Sınır: İlerleme sütunu elle girilen beyandır (grafikle aynı sınır).\n"
        "\n"
        "Yorum: Grafikte fark edilen şüpheli balonların doğrulama adresi bu tablodur; bütçe "
        "aşımı satırlarını girişim sahibine sorulacak ilk sorular olarak listeleyin."
    ),

    # ─────────────────────────── INITIATIVE ROADMAP ───────────────────────────

    "raporlar_initiative_roadmap.stratejik_girisimler": (
        "Stratejik girişimleri çok yıllık zaman çizelgesinde (Gantt) gösterir: çubuk uzunluğu "
        "başlangıç-bitiş yılı aralığı, çubuk üzerinde ilerleme yüzdesi, renk öncelik.\n"
        "\n"
        "Hesap: Çubuk uzunluğu = bitiş yılı − başlangıç yılı + 1. Tamamlanan girişimler yarı "
        "saydam, iptal edilenler çok soluk çizilir.\n"
        "\n"
        "Sınır: İlerleme yüzdesi girişim kartına elle girilen değerdir; kilometre taşlarının "
        "tamamlanmasından HESAPLANMAZ. Yıl çözünürlüğü kabadır — ay/çeyrek planlaması "
        "gösterilmez.\n"
        "\n"
        "Yorum: Çizelgeyi kapasite okuması için kullanın: aynı yıllara yığılan çok sayıda "
        "yüksek öncelikli girişim, kaynak çakışmasının görsel kanıtıdır."
    ),

    # ─────────────────────────── KV ÇARPIKLIK ───────────────────────────

    "raporlar_kv_carpiklik.ozet_kartlari": (
        "K-Vektör ağırlığı ile fiilî performansın dengesini özetler: toplam strateji, dengeli "
        "sayısı, dengesiz sayısı ve plan yılı.\n"
        "\n"
        "Hesap: Bir strateji için çarpıklık = ağırlık yüzdesi − ortalama süreç skoru. Mutlak "
        "değeri 10 ve altındaysa 'dengeli' sayılır; +10 üstü 'ağır ama düşük performans', −10 "
        "altı 'hafif ama yüksek performans' etiketi alır.\n"
        "\n"
        "Sınır: Skoru hesaplanamayan (bağlı süreç verisi olmayan) stratejiler denge "
        "değerlendirmesine girmez.\n"
        "\n"
        "Yorum: Dengesiz sayısı yüksekse kaynak dağılımı ile sonuç üretimi ayrışıyor demektir — "
        "detay tablosundan hangi yönde ayrıştığına bakın."
    ),

    "raporlar_kv_carpiklik.agirlik_skor_karsilastirma": (
        "Her strateji için iki çubuğu yan yana gösterir: K-Vektör ağırlık payı (mor) ve bağlı "
        "süreçlerin ortalama skoru (yeşil).\n"
        "\n"
        "Hesap: Ağırlık payı = stratejinin ham ağırlığı / toplam ham ağırlık × 100. Skor, bağlı "
        "süreçlerin skor motoru ortalamasıdır.\n"
        "\n"
        "Sınır: İki çubuk FARKLI ölçülerin görsel kıyasıdır — biri kaynak payı, diğeri başarı "
        "skoru; ikisi de 0-100 ölçeğinde olduğu için yan yana konabilmektedir. Skor "
        "hesaplanamıyorsa çubuk boş ve değer '—' gösterilir.\n"
        "\n"
        "Yorum: Mor çubuğun yeşilden belirgin uzun olduğu stratejiler 'pahalı ama üretmiyor' "
        "adayıdır; tersi ise 'az kaynakla başarıyor' — ağırlık artışı tartışılabilir."
    ),

    "raporlar_kv_carpiklik.detay_tablosu": (
        "Strateji başına ağırlık yüzdesi, ortalama skor, çarpıklık değeri ve değerlendirme "
        "etiketini tablo halinde verir.\n"
        "\n"
        "Hesap: Çarpıklık = ağırlık yüzdesi − ortalama süreç skoru (basit fark).\n"
        "\n"
        "Eşik: +10 üzeri kırmızı 'ağır ama düşük performans', −10 altı mavi 'hafif ama yüksek "
        "performans', aradaki yeşil 'dengeli'.\n"
        "\n"
        "Sınır: Buradaki 'çarpıklık' istatistikteki skewness DEĞİLDİR — yalnızca iki yüzdenin "
        "farkıdır. Skor hesaplanamayan stratejilerde çarpıklık boş bırakılır.\n"
        "\n"
        "Yorum: Tabloyu K-Vektör ağırlık revizyonu öncesi hazırlık dokümanı olarak kullanın; "
        "±10 bandı kaba bir eşiktir, sınırdaki değerleri bağlamıyla değerlendirin."
    ),

    # ─────────────────────────── ML ANOMALY ───────────────────────────

    "raporlar_ml_anomaly.tespit_edilen_anomaliler": (
        "KPI ölçümlerinde makine öğrenmesiyle işaretlenen olağandışı değerleri listeler: "
        "gösterge, süreç, tarih, değer ve anomali skoru.\n"
        "\n"
        "Hesap: Gerçek bir ML modeli kullanılır — Isolation Forest (kontaminasyon 0,1; 50 "
        "ağaç). Her göstergenin son 24 ölçümü modele verilir; model, izole kalan noktaları "
        "anomali işaretler. Basit z-skoru veya eşik kuralı DEĞİLDİR.\n"
        "\n"
        "Eşik: Bir göstergenin analize girmesi için en az 8 sayısal ölçümü olmalıdır (ekrandaki "
        "'en az 6 ölçüm' notu eskidir). Kontaminasyon 0,1 — model her göstergede yaklaşık %10 "
        "anomali arar.\n"
        "\n"
        "Sınır: Analiz ilk 200 göstergeyle, sonuç listesi ilk 30 anomaliyle sınırlıdır. "
        "Kontaminasyon sabiti nedeniyle tamamen normal seyreden verilerde bile en uç noktalar "
        "anomali diye işaretlenebilir.\n"
        "\n"
        "Yorum: Anomali 'hata' demek değildir — veri giriş yanlışı, gerçek operasyonel sapma "
        "veya mevsimsel etki olabilir. Her kaydı kaynağında doğrulayın."
    ),

    # ─────────────────────────── MOBILE ───────────────────────────

    "raporlar_mobile.mobile_hub": (
        "Mobil uygulama önizlemesini telefon çerçevesi içinde gösterir: vizyon skoru ile bugün "
        "biten, geciken, 7 gün içinde bitecek faaliyet sayıları ve kişisel hedef sayısı.\n"
        "\n"
        "Hesap: Vizyon skoru kurumsal skor motorundan gelir. Geciken = bitiş tarihi geçmiş ve "
        "tamamlanmamış faaliyetler; diğer sayaçlar tarih aralığı sayımlarıdır.\n"
        "\n"
        "Eşik: Vizyon skoru 70 ve üzeri yeşil, 50-70 sarı, altı kırmızı.\n"
        "\n"
        "Sınır: Bu bir MVP önizlemesidir — gerçek mobil uygulama değildir. Faaliyet sayaçları "
        "plan yılına filtrelenmez; tüm aktif süreçlerin faaliyetlerini kapsar.\n"
        "\n"
        "Yorum: Sayaçları hızlı sabah kontrolü olarak kullanın; derin inceleme için ilgili "
        "modül ekranlarına geçin."
    ),

    # ─────────────────────────── MUDA ANALİZİ ───────────────────────────

    "raporlar_muda_analizi.7_muda_turu_bulgu_sayilari_aciklamalar": (
        "Yalın üretimin yedi israf türü çerçevesinde süreçlerdeki bulgu sayılarını ve tür "
        "açıklamalarını gösterir.\n"
        "\n"
        "Hesap: Kod şu an DÖRT türü fiilen tespit eder — Bekleme: son 90 gündeki 3 ölçümden en "
        "az 2'si hedef altındaysa (ortalama sapma %20'yi aşarsa yüksek şiddet); Hata/yeniden "
        "işleme: son 6 ölçümde değişim katsayısı %30'u aşarsa; Aşırı işleme: süreçte 10'dan "
        "fazla aktif gösterge varsa; Aşırı üretim: süreç pasif durumdaysa.\n"
        "\n"
        "Sınır: Taşıma, stok ve hareket israfları KOD tarafından hiç tespit edilmez — bu üç "
        "kart her zaman 0 bulgu gösterir ve yalnızca tanım amaçlıdır. Yedi israf çerçevesi "
        "Ohno'nun (Toyota Üretim Sistemi, 1978) sınıflandırmasıdır; buradaki tespitler bu "
        "çerçevenin KPI verisine uyarlanmış yaklaşık göstergeleridir, saha gözlemi yerine "
        "geçmez.\n"
        "\n"
        "Yorum: Bulgu sayılarını israf kanıtı değil inceleme daveti olarak okuyun; özellikle "
        "değişim katsayısı bulgusu ölçüm birimindeki tutarsızlıklardan da tetiklenebilir."
    ),

    "raporlar_muda_analizi.bulgu_saptanan_surecler": (
        "En az bir israf bulgusu saptanan süreçleri, bulgu sayısı ve ilk beş bulgu özetiyle "
        "listeler.\n"
        "\n"
        "Hesap: Her süreç israf analizinden geçirilir; bulgu üretmeyen süreçler listeye girmez.\n"
        "\n"
        "Sınır: Analiz edilen süreç sayısı yapılandırma sınırıyla kısıtlıdır ve süreç başına en "
        "fazla beş bulgu gösterilir. Analizde hata veren süreç sessizce atlanır (günlüğe "
        "yazılır).\n"
        "\n"
        "Yorum: Listede olmamak 'israfsız' demek değildir — süreç ölçümsüzse tespit edilecek "
        "veri de yoktur. Ölçümü zayıf süreçleri ayrıca değerlendirin."
    ),

    # ─────────────────────────── NLP QUERY ───────────────────────────

    "raporlar_nlp_query.hazir_sorular": (
        "Tek tıkla çalıştırılabilen sekiz hazır soruyu listeler: en yüksek/en düşük 5 gösterge, "
        "süreç sağlığı, aktif girişimler, geciken faaliyetler, ölçüm hacmi, departman kullanıcı "
        "sayısı ve yüksek riskler.\n"
        "\n"
        "Hesap: Her hazır soru önceden yazılmış deterministik bir veritabanı sorgusudur — yapay "
        "zekâya GİTMEZ, her çalıştırmada aynı veriyle aynı sonucu verir.\n"
        "\n"
        "Eşik: Gösterge sıralamalarında en az 3 ölçümü olan göstergeler dikkate alınır; risk "
        "sorusu RPN 10 ve üzerini listeler.\n"
        "\n"
        "Yorum: Güvenilir sayı gerektiğinde hazır soruları tercih edin — serbest metin "
        "kutusunun aksine bunlar gerçek veri döndürür."
    ),

    "raporlar_nlp_query.cevap": (
        "Seçilen hazır sorunun sonucunu tablo olarak, serbest metin sorusunun yanıtını ise "
        "metin olarak gösterir.\n"
        "\n"
        "Hesap: Hazır sorular deterministik sorgu çalıştırır. Serbest metin ise yapay zekâya "
        "gönderilir — ancak modele veritabanı sorgusu YAZDIRILMAZ; yalnızca 'bu soru için hangi "
        "rapora bakılabilir' türünde yönlendirici açıklama üretmesi istenir.\n"
        "\n"
        "Sınır: Serbest metin yanıtı VERİ İÇERMEZ — sayısal cevap yalnızca sekiz hazır sorudan "
        "gelir. Yapay zekâ erişimi yoksa serbest metne sabit bir yönlendirme mesajı döner.\n"
        "\n"
        "Yorum: Serbest metin yanıtındaki rapor önerisini takip edin ama içindeki herhangi bir "
        "sayıya itibar etmeyin; sayının adresi hazır sorgular ve ilgili panolardır."
    ),

    # ─────────────────────────── OKR CASCADE ───────────────────────────

    "raporlar_okr_cascade.okr_aciklama": (
        "OKR (Objective / Key Result — Amaç / Anahtar Sonuç) yönteminin ne olduğunu anlatan "
        "sabit bilgi kartıdır: Amaç niteliksel yönü, anahtar sonuçlar ölçülebilir kanıtları "
        "tanımlar.\n"
        "\n"
        "Sınır: Kart veri ölçmez; kurumunuzun OKR verisine göre değişmez.\n"
        "\n"
        "Yorum: OKR'ı mevcut PG yapısının alternatifi değil, çeyreklik odak katmanı olarak "
        "konumlandırmak iki sistemin çakışmasını önler."
    ),

    "raporlar_okr_cascade.hizalama_listesi": (
        "Amaçları (Objective) altlarındaki anahtar sonuçlarla (KR) birlikte listeler; her amacın "
        "bağlı stratejisi, çeyreği, sahibi ve ortalama ilerlemesi gösterilir.\n"
        "\n"
        "Hesap: Amaç ilerlemesi = anahtar sonuç ilerlemelerinin düz ortalaması. KR ilerlemesi "
        "kayıttaki ilerleme oranından yüzdeye çevrilir.\n"
        "\n"
        "Eşik: %70 ve üzeri yeşil, %40-70 sarı, altı kırmızı.\n"
        "\n"
        "Sınır: Ortalama ağırlıksızdır — kolay ve zor anahtar sonuçlar eşit sayılır. Strateji "
        "bağı olmayan amaçlar da listelenir; 'hizalama' bağın varlığını gösterir, niteliğini "
        "değil.\n"
        "\n"
        "Yorum: Çeyrek sonu yaklaşırken %40 altı amaçları gündeme alın; %100'e erken ulaşan "
        "amaçlar ise hedefin fazla kolay konduğuna işaret edebilir."
    ),

    # ─────────────────────────── ONAY ZİNCİRİ ───────────────────────────

    "raporlar_onay_zinciri.stratejik_girisim_ler": (
        "Stratejik girişimleri onay durumu, öncelik, sahip, bütçe ve ilerleme sütunlarıyla "
        "listeler; üstte bekleyen/onaylı/reddedilen özetleri gösterilir.\n"
        "\n"
        "Hesap: 'Onay durumu' girişimin durum alanından sabit eşlemeyle türetilir: planlandı → "
        "onay bekliyor, yürütmede → onaylanmış, tamamlandı → geçti, beklemede → beklemeye "
        "alındı, iptal → reddedildi.\n"
        "\n"
        "Sınır: Gerçek bir onay akışı (onaycı ataması, adımlar, eskalasyon) HENÜZ YOKTUR — bu "
        "ekran mevcut durum alanının onay diliyle yeniden etiketlenmiş halidir (MVP).\n"
        "\n"
        "Yorum: 'Onay bekliyor' satırlarını gerçek bir onay kuyruk listesi gibi değil, 'henüz "
        "başlatılmamış girişimler' listesi olarak okuyun."
    ),

    # ─────────────────────────── OPERASYON İSTATİSTİK ───────────────────────────

    "raporlar_operasyon_istatistik.surecler": (
        "Her süreç için bağlı gösterge (PG) sayısını ve faaliyet sayısını tek tabloda özetler.\n"
        "\n"
        "Hesap: Süreç başına benzersiz gösterge ve faaliyet kayıtları sayılır; özet satırı "
        "bunların toplamıdır.\n"
        "\n"
        "Sınır: Plan yılı filtresi uygulanır ancak yıl bilgisi olmayan eski kayıtlar her yıla "
        "dahil edilir — geçmişten kalan kayıtlar sayıları şişirebilir.\n"
        "\n"
        "Yorum: Göstergesiz veya faaliyetsiz süreçler ölçüm tasarımı eksikliğinin ilk "
        "işaretidir; 10'dan fazla göstergesi olan süreçler ise sadeleştirme adayıdır."
    ),

    # ─────────────────────────── PG PROJE ETKİ ───────────────────────────

    "raporlar_pg_proje_etki.nasil_okunur": (
        "Raporun okuma kılavuzu niteliğinde sabit bilgi kartıdır: her satır bir projedir; "
        "'hedef üstü PG yüzdesi', projeye bağlı süreçlerdeki göstergelerin ne kadarının hedefin "
        "üzerinde seyrettiğini özetler.\n"
        "\n"
        "Sınır: Kart veri ölçmez. İlişki korelasyoneldir — projenin gösterge başarısına neden "
        "olduğunu kanıtlamaz, yalnızca birlikte seyri gösterir.\n"
        "\n"
        "Yorum: Yüzdesi düşük projeleri 'başarısız' ilan etmeden önce bağlı süreçlerin ölçüm "
        "doluluğunu kontrol edin."
    ),

    "raporlar_pg_proje_etki.ozet_kartlari": (
        "Proje-gösterge bağlantısının genel fotoğrafını verir: toplam proje, göstergeye bağlı "
        "proje, bağsız proje, etkilenen gösterge sayısı ve ortalama hedef-üstü yüzdesi.\n"
        "\n"
        "Hesap: Hedef-üstü % = bağlı süreçlerdeki hedefin üzerinde seyreden gösterge / toplam "
        "gösterge × 100; ortalama, göstergeye bağlı projeler üzerinden alınır.\n"
        "\n"
        "Eşik: %75 ve üzeri yeşil, %50-75 sarı, altı kırmızı.\n"
        "\n"
        "Sınır: Hedef-üstü sayımı yalnızca PostgreSQL üzerinde gerçek hesaplanır; SQLite "
        "ortamında her zaman 0 döner. Liste en fazla 80 projeyle sınırlıdır.\n"
        "\n"
        "Yorum: 'Bağsız proje' sayısı büyükse proje portföyü ile ölçüm sistemi birbirinden "
        "kopuk yürüyor demektir — etki analizi ancak bağlar kurulunca anlamlanır."
    ),

    "raporlar_pg_proje_etki.proje_listesi": (
        "Projeleri bağlı süreç sayısı, etkilenen gösterge sayısı ve hedef-üstü yüzdesiyle "
        "listeler; satır genişletildiğinde etkilenen süreçler açılır.\n"
        "\n"
        "Hesap: Proje başına toplam gösterge = bağlı süreçlerin gösterge toplamı; hedef-üstü % "
        "= hedef üzerinde seyreden gösterge oranı.\n"
        "\n"
        "Eşik: %75 ve üzeri yeşil, %50-75 sarı, altı kırmızı; göstergesi olmayan projede '—'.\n"
        "\n"
        "Sınır: Hedef-üstü sayımı yalnızca PostgreSQL'de gerçektir (SQLite'ta 0). En fazla 80 "
        "proje listelenir.\n"
        "\n"
        "Yorum: Süreç bağı çok ama hedef-üstü oranı düşük projeler, kaynak-etki tartışmasının "
        "doğal gündemidir; tek süreçli projelerde yüzde tek göstergeyle dalgalanabilir."
    ),

    # ─────────────────────────── CMMI HEATMAP ───────────────────────────

    "raporlar_cmmi_heatmap.ortalama_olgunluk": (
        "Olgunluk kaydı girilmiş süreçlerin ortalama seviyesini (1-5) yorum bandıyla gösterir.\n"
        "\n"
        "Hesap: Her sürecin en yüksek öz değerlendirme seviyesi alınır; ortalama bu seviyelerin "
        "aritmetik ortalamasıdır. Ortanca ve 'seviye 3+' oranı da birlikte sunulur.\n"
        "\n"
        "Eşik: 4,5+ mükemmel, 3,5+ çok iyi, 2,5+ iyi, 1,5+ orta, altı düşük.\n"
        "\n"
        "Sınır: Seviyeler sıralı (ordinal) ölçektir — aritmetik ortalaması metodolojik olarak "
        "yaklaşıktır; ortanca değeri daha sağlam okuma verir. Değerler resmî bir CMMI/SCAMPI "
        "değerlendirmesi değil, kurumun ÖZ DEĞERLENDİRMESİDİR.\n"
        "\n"
        "Kaynak: Beş seviyeli olgunluk çerçevesi SEI'nin CMMI modelinden uyarlanmıştır.\n"
        "\n"
        "Yorum: Ortalamayı tek sayı olarak sunmak yerine dağılımla birlikte okuyun; iki uçtaki "
        "süreçler ortalamada birbirini gizler."
    ),

    "raporlar_cmmi_heatmap.seviye_dagilimi_ve_aciklamalar": (
        "Beş olgunluk seviyesinin her biri için süreç sayısını, yüzdesini ve seviye tanımını "
        "gösterir.\n"
        "\n"
        "Hesap: Süreçler en yüksek öz değerlendirme seviyelerine göre kovalanır; yüzde, ölçülmüş "
        "süreç sayısına oranla hesaplanır.\n"
        "\n"
        "Sınır: Seviye tanımları (Başlangıç → Optimize) CMMI aşamalı temsilinden UYARLAMADIR — "
        "resmî süreç alanı/hedef denetimi uygulanmaz. Olgunluk kaydı olmayan süreçler dağılıma "
        "girmez.\n"
        "\n"
        "Kaynak: CMMI (SEI) beş seviyeli olgunluk modeli.\n"
        "\n"
        "Yorum: Seviye 1-2 yığılması standartlaşma eksikliğini gösterir; seviye 4-5 beyanlarını "
        "ise kanıtla (ölçüm ve iyileştirme kayıtlarıyla) sorgulayın — öz değerlendirmede şişme "
        "eğilimi yaygındır."
    ),

    "raporlar_cmmi_heatmap.surec_bazli_olgunluk": (
        "Ölçülmüş her süreci seviye rozetiyle kart olarak gösterir; karta tıklayınca süreç "
        "karnesine gidilir. Olgunluk kaydı olmayan süreçler ayrıca uyarı listesinde gösterilir.\n"
        "\n"
        "Hesap: Süreç seviyesi, o sürecin kayıtlı EN YÜKSEK öz değerlendirme seviyesidir — en "
        "son kayıt değil.\n"
        "\n"
        "Sınır: Seviye düşüşleri bu seçim yüzünden görünmez: süreç bir kez 4 işaretlendiyse "
        "sonradan 2'ye gerilese de 4 görünür. Ölçülmemiş süreç listesi en fazla 20 kayıt "
        "gösterir.\n"
        "\n"
        "Yorum: Yüksek seviyeli kartları güncelleme tarihiyle birlikte değerlendirin; eski "
        "tarihli yüksek seviye, güncel durumu temsil etmeyebilir."
    ),

    # ─────────────────────────── COO DASHBOARD ───────────────────────────

    "raporlar_coo_dashboard.aktif_darbogazlar": (
        "Çözülmemiş operasyonel darboğaz kayıtlarını şiddet, not ve tetiklenme tarihiyle "
        "listeler.\n"
        "\n"
        "Hesap: Darboğaz günlüğünden çözülme tarihi boş olan kayıtlar gösterilir.\n"
        "\n"
        "Sınır: Yalnızca en son 10 darboğaz kaydı çekilir — üstteki sayaç da bu 10'luk "
        "pencereyle sınırlıdır; 10'dan fazla aktif darboğaz varsa eksik görünür.\n"
        "\n"
        "Yorum: Uzun süre 'aktif' kalan darboğazlar iki şeyden biridir: gerçekten çözülmemiş "
        "sorun ya da kapatılması unutulmuş kayıt. İkisi de yönetim dikkati ister."
    ),

    "raporlar_coo_dashboard.surec_saglik_dagilimi": (
        "Süreçleri sağlık skoru bantlarına göre dağıtır: iyi, orta, düşük ve veri yok.\n"
        "\n"
        "Hesap: Skor 70 ve üzeri iyi, 50-69 orta, 50 altı düşük; skoru hesaplanamayan süreçler "
        "'veri yok' kovasına düşer.\n"
        "\n"
        "Sınır: 'Sağlık' burada yalnızca gösterge (PG) skorlarının ağırlıklı ortalamasıdır — "
        "darboğaz sayısı, olgunluk seviyesi ve geciken faaliyetler bu skora GİRMEZ (panoda ayrı "
        "metrik olarak dururlar).\n"
        "\n"
        "Yorum: 'Veri yok' dilimi büyükse dağılımın geri kalanı kurumun gerçek fotoğrafı "
        "değildir — önce ölçüm kapsamını genişletin."
    ),

    "raporlar_coo_dashboard.surecler_saglik_skoru": (
        "Her süreci 0-100 sağlık skoru ve ağırlığıyla listeler.\n"
        "\n"
        "Hesap: Süreç skoru, aktif göstergelerinin skorlarının ağırlıklı ortalamasıdır; "
        "ağırlıklar payda 100'e normalize edilir. Alt süreci olan süreçlerde çocuk skorlarının "
        "ağırlıklı ortalaması alınır. Ölçülmemiş göstergeler hem paydan hem paydadan düşer.\n"
        "\n"
        "Eşik: 70 ve üzeri yeşil, 50-69 sarı, altı kırmızı; hesaplanamayan gri '—'.\n"
        "\n"
        "Sınır: Hiç ölçümü olmayan süreç skorsuz görünür — kötü değil, ölçümsüzdür. Skora "
        "darboğaz/olgunluk/gecikme bileşeni dahil değildir.\n"
        "\n"
        "Yorum: Skoru düşük süreçlerde önce kaç göstergenin ölçüldüğüne bakın; tek göstergeyle "
        "hesaplanan skor o göstergenin dalgalanmasını süreç geneli sanmanıza yol açar."
    ),

    # ─────────────────────────── DEPARTMAN PERFORMANS ───────────────────────────

    "raporlar_departman_performans.departman_karti": (
        "Departman bazında çalışan sayısı, bireysel gösterge toplamı, kişi başı gösterge, "
        "önemli gösterge sayısı ve iki faktörlü doğrulama oranını tablolar.\n"
        "\n"
        "Hesap: Kişi başı gösterge = departmanın aktif bireysel göstergesi / çalışan sayısı. "
        "2FA oranı = doğrulaması açık çalışan / toplam çalışan × 100.\n"
        "\n"
        "Eşik: 2FA oranı %80+ yeşil, %30-80 turuncu, altı kırmızı.\n"
        "\n"
        "Sınır: Adındaki 'performans'a rağmen bu tablo BAŞARI SKORU içermez — yalnızca gösterge "
        "SAYILARINI ölçer. Çok göstergeli departman iyi performanslı demek değildir. Departmanı "
        "boş çalışanlar '(belirsiz)' satırında toplanır.\n"
        "\n"
        "Yorum: Tabloyu hedef yaygınlığı ve güvenlik hijyeni taraması olarak kullanın; başarı "
        "kıyası için bireysel karne raporlarına gidin."
    ),

    # ─────────────────────────── EARLY WARNING ───────────────────────────

    "raporlar_early_warning.uyari_listesi": (
        "Üst üste hedef altında kalan göstergeleri erken uyarı kartları olarak listeler.\n"
        "\n"
        "Hesap: Her göstergenin son ölçümleri incelenir; en yeni ÜÇ ölçümün TÜMÜ %70'in "
        "altındaysa uyarı üretilir. Üçü de %50'nin altındaysa öncelik 'yüksek', aksi halde "
        "'orta' olur.\n"
        "\n"
        "Sınır: Tarama ilk 100 göstergeyle ve gösterge başına son 6 ölçümle sınırlıdır — çok "
        "göstergeli kurumlarda bazı göstergeler hiç taranmaz. 'Dönem' takvim dönemi değil, en "
        "yeni üç ölçüm kaydıdır; düzensiz veri girişinde aralıklar eşit olmayabilir. En fazla "
        "25 uyarı gösterilir.\n"
        "\n"
        "Yorum: Uyarı listesinin boş olması 'her şey yolunda' anlamına gelmeyebilir — üç "
        "ölçümü olmayan göstergeler değerlendirilemez. Ölçüm sıklığı düşük göstergelerde uyarı "
        "gecikmeli gelir."
    ),

    # ─────────────────────────── ESG RAPOR ───────────────────────────

    "raporlar_esg_rapor.rapor_icerigi": (
        "Üretilecek ESG PDF'inin kapsayacağı bölümleri listeleyen sabit bilgi kartıdır: kurum "
        "profili (GRI 102), emisyonlar (GRI 305), sosyal metrikler (GRI 403), yönetişim (GRI "
        "102-22) ve TCFD iklim beyanı.\n"
        "\n"
        "Sınır: Kart veri ölçmez; doluluk göstermez. Bölümlerin dosyada ne kadar dolu "
        "çıkacağı, ESG yönetim sayfasına girilmiş metrik verisine bağlıdır.\n"
        "\n"
        "Yorum: PDF üretmeden önce ESG yönetim sayfasında üç kategoride de (E/S/G) metrik "
        "tanımlı ve değer girilmiş olduğunu kontrol edin; boş kategoriler raporda 'tanımlanmamış' "
        "notuyla çıkar."
    ),

    "raporlar_esg_rapor.yatirimci_denetci_hazir_pdf": (
        "GRI ve TCFD yapısına göre düzenlenmiş ESG raporunu PDF olarak üretip indirir.\n"
        "\n"
        "Hesap: Emisyon tablosu, çevre metriklerinin yıl ve kapsam bazında toplamıdır. TCFD "
        "bölümü yönetişim metrik sayısını, hedef atanmış çevre metriklerini ve risk kayıtları "
        "içinde iklim/çevre anahtar kelimeli riskleri özetler (RPN'e göre ilk 5).\n"
        "\n"
        "Sınır: 'Yatırımcı/denetçi hazır' ifadesi içeriğin kurumca girilen veriyle sınırlı "
        "olduğu gerçeğini değiştirmez — dış doğrulama, asgari veri kontrolü veya uyumluluk "
        "denetimi YAPILMAZ. Veri girilmemiş bölümler 'tanımlanmamış' notuyla üretilir.\n"
        "\n"
        "Yorum: Raporu dışarı vermeden önce her bölümü açıp doluluğunu gözle kontrol edin; GRI "
        "başlıklı boş bölümler kurumsal görünürlükte ters etki yapar."
    ),

    "raporlar_esg_yonetim.sayfa": (
        "ESG metriklerini tanımlama ve yıllık değer girme yönetim sayfasıdır: çevre (E), "
        "sosyal (S), yönetişim (G) kategorilerinde metrik ekleme, hedef/baz yılı atama ve yıl "
        "bazlı değer girişi.\n"
        "\n"
        "Sınır: Bu sayfa analiz veya skorlama YAPMAZ — girilen veriler ESG raporunu ve karbon "
        "trend grafiğini besler. Emisyon metriklerinde birim tutarlılığı kullanıcı "
        "sorumluluğundadır; sistem dönüşüm yapmaz.\n"
        "\n"
        "Yorum: Kapsam 1-2-3 ayrımını baştan doğru kurun ve her yıl aynı birimle girin; "
        "sonradan birim değişikliği trend grafiğini geçersiz kılar."
    ),

    # ─────────────────────────── EVRİM FİLMİ ───────────────────────────

    "raporlar_evrim_filmi.yillar_arasi_evrim_filmi": (
        "Stratejik planın yıldan yıla yapısal evrimini gösterir: her plan yılı için strateji "
        "ağacı görüntüsü ve yapı sayıları (strateji, alt strateji, süreç, gösterge, ölçüm); "
        "kaydırıcı veya oynat düğmesiyle yıllar arasında geçilir.\n"
        "\n"
        "Hesap: Her yıl için yapısal kayıt sayıları toplanır; içerik anlık plan yapısının "
        "fotoğrafıdır.\n"
        "\n"
        "Sınır: Gösterilen SAYILARDIR, başarı değil — hiçbir performans skoru içermez. Ölçüm "
        "sayısı takvim yılına, diğer sayımlar plan yılına bağlanır; iki anahtar ayrışabilir.\n"
        "\n"
        "Yorum: Filmi kurumsal hafıza aracı olarak kullanın: yapının hangi yıl büyüdüğü, hangi "
        "yıl sadeleştiği stratejik yönelim değişikliklerinin izidir."
    ),

    # ─────────────────────────── HEDEF REVİZYON ───────────────────────────

    "raporlar_hedef_revizyon.revize_edilen_pg_ler": (
        "Yıl bazında hedefi, ağırlığı veya periyodu esas tanımından farklılaştırılmış "
        "göstergeleri listeler (esas değer → yıl değeri).\n"
        "\n"
        "Hesap: Göstergenin yıllık yapılandırması esas kayıtla karşılaştırılır; hedef, ağırlık "
        "veya periyottan en az biri farklıysa 'revize edilmiş' sayılır.\n"
        "\n"
        "Sınır: Bu bir gerçek DEĞİŞİKLİK GEÇMİŞİ değildir — kim, ne zaman, kaç kez değiştirdi "
        "bilgisi yoktur; yalnızca yıllık değerin esastan farklı OLDUĞU tespit edilir. Yıl içinde "
        "beş kez değişen gösterge de tek kayıt görünür. Liste en fazla 50 kayıt gösterir.\n"
        "\n"
        "Yorum: Dönem sonuna doğru yapılan hedef revizyonlarını ayrıca Hedef Değişiklik "
        "Radarı'ndan izleyin — orada zaman ve kişi bilgisi tutulur."
    ),

    "raporlar_hedef_revizyon.yillara_gore_revizyon": (
        "Her plan yılında kaç göstergenin revize edildiğini çubuk grafikle gösterir.\n"
        "\n"
        "Hesap: Yıl başına, esastan farklılaşmış yıllık gösterge yapılandırması sayılır.\n"
        "\n"
        "Sınır: 'Revizyon' yıllık farkın varlığıdır — değişiklik sıklığı veya zamanı ölçülmez "
        "(üstteki kartla aynı sınır).\n"
        "\n"
        "Yorum: Revizyon sayısının yıldan yıla artması iki şekilde okunabilir: planlama "
        "olgunlaşıyor (yıla özgü hedefler bilinçli ayarlanıyor) ya da hedef disiplini "
        "gevşiyor. Hangisi olduğunu revizyonların yönü (kolaylaştırma mı zorlaştırma mı) "
        "belirler."
    ),

    # ─────────────────────────── HİZALAMA SANKEY ───────────────────────────

    "raporlar_hizalama_sankey.akis_gorseli": (
        "Vizyon → strateji → alt strateji → süreç → gösterge zincirini beş seviyeli akış "
        "(Sankey) diyagramı olarak çizer; bant kalınlığı katkıyı, renk skoru gösterir.\n"
        "\n"
        "Hesap: Strateji bandının kalınlığı K-Vektör ağırlık payından, süreç bandı süreç-alt "
        "strateji katkı yüzdesinden gelir. Düğüm renkleri skor motorundan beslenir.\n"
        "\n"
        "Eşik: Skor 75+ yeşil (sağlıklı), 50-74 sarı (izle), 50 altı kırmızı (kritik), "
        "skorsuz gri.\n"
        "\n"
        "Sınır: Alt strateji ve gösterge bantlarının kalınlığı SABİTTİR (gerçek ağırlığı "
        "yansıtmaz). K-Vektör ağırlıkları kurulmamışsa strateji bantları orantısız görünür. "
        "Hiçbir stratejiye bağlanmamış süreçler diyagram dışında ayrıca listelenir.\n"
        "\n"
        "Yorum: Diyagramın asıl değeri kopuk akışları göstermesidir — vizyona bağlanmayan "
        "süreç ve göstergeler stratejik hizalama borcunuzdur."
    ),

    # ─────────────────────────── İKİ FA ───────────────────────────

    "raporlar_iki_fa.2fa_dagilim": (
        "Kurumdaki aktif kullanıcıların iki faktörlü doğrulama (2FA) durumunu halka grafikle "
        "gösterir: etkin ve etkin olmayan sayıları.\n"
        "\n"
        "Hesap: Etkinlik oranı = 2FA'sı açık aktif kullanıcı / toplam aktif kullanıcı × 100.\n"
        "\n"
        "Eşik: Oran %80+ yeşil, %40-80 turuncu, altı kırmızı.\n"
        "\n"
        "Yorum: 2FA, hesap ele geçirmeye karşı en etkili tek önlemdir; oranı %100'e taşımak "
        "teknik değil yönetsel bir iştir — zorunluluk politikasıyla desteklenmedikçe gönüllü "
        "benimseme genelde platoda kalır."
    ),

    "raporlar_iki_fa.2fa_si_olmayan_yoneticiler_kritik_guvenlik_acigi": (
        "İki faktörlü doğrulaması kapalı olan kurum yöneticisi hesaplarını listeler.\n"
        "\n"
        "Hesap: Aktif ve 2FA'sı kapalı kullanıcılardan rolü 'kurum yöneticisi' (tenant_admin) "
        "olanlar seçilir.\n"
        "\n"
        "Sınır: 'Yöneticiler' başlığına rağmen liste YALNIZCA kurum yöneticisi rolünü kapsar — "
        "üst düzey yönetici ve diğer yönetici rolleri bu listeye girmez; onların 2FA durumu "
        "genel dağılımda görünür.\n"
        "\n"
        "Yorum: Yönetici hesabı geniş yetki taşır; bu listedeki her satır gerçek bir saldırı "
        "yüzeyidir. Liste boşalana kadar takip edilmesi gereken bir güvenlik borcudur."
    ),

    # ─────────────────────────── QUARTERLY REVIEW ───────────────────────────

    "raporlar_quarterly_review.ceyreklik_review_toplantisi": (
        "İçinde bulunulan çeyreğin dönem bilgisini ve anlık metriklerini gösterir: bu çeyrekte "
        "girilen ölçüm sayısı, yeni başlayan ve tamamlanan girişim sayısı.\n"
        "\n"
        "Hesap: Çeyrek, içinde bulunulan aydan türetilir; sayaçlar çeyrek tarih aralığındaki "
        "kayıt sayımlarıdır.\n"
        "\n"
        "Sınır: Kart, toplantının kendisine dair veri (katılım, karar, aksiyon) içermez — "
        "toplantı HAZIRLIĞI için anlık fotoğraf sunar.\n"
        "\n"
        "Yorum: Ölçüm sayısının önceki çeyreklere göre düşmesi, toplantıdan önce konuşulması "
        "gereken ilk konudur: veri girmeyen kurum, performansını da tartışamaz."
    ),

    "raporlar_quarterly_review.ai_yonetici_ozeti": (
        "Çeyreğin sayısal fotoğrafından yapay zekâ ile üretilmiş 3-4 cümlelik yönetici özeti "
        "sunar.\n"
        "\n"
        "Hesap: Özetin dayandığı sayılar (ölçüm, yeni/tamamlanan girişim) deterministiktir; "
        "metin bu sayılarla yapay zekâya yazdırılır.\n"
        "\n"
        "Sınır: Yapay zekâ erişimi yoksa aynı sayıları içeren sabit şablon cümle gösterilir — "
        "ekranda hangisinin gösterildiği AYIRT EDİLMEZ. Yapay zekâ metni deterministik "
        "değildir; her üretimde değişebilir.\n"
        "\n"
        "Yorum: Özeti toplantı açılış paragrafı olarak kullanın ama sayıları kartlardan teyit "
        "edin; metindeki nitel yorumlar (örn. 'güçlü ivme') modelin seçimidir, ölçüm değildir."
    ),

    "raporlar_quarterly_review.onerilen_agenda": (
        "Çeyreklik değerlendirme toplantısı için süre önerili yedi maddelik gündem şablonu "
        "sunar.\n"
        "\n"
        "Sınır: Gündem kurumunuzun verisinden türetilmez — sabit bir şablondur; yalnızca "
        "yıl/çeyrek etiketi dinamiktir.\n"
        "\n"
        "Yorum: Şablonu başlangıç noktası olarak kullanıp kurumunuzun o çeyrekteki gerçek "
        "gündemine (erken uyarılar, bütçe aşımları, geciken girişimler) göre daraltın; yedi "
        "maddenin tamamını eşit süreyle işlemek nadiren doğru önceliklendirmedir."
    ),

    "raporlar_quarterly_review.on_calisma_sorulari": (
        "Katılımcıların toplantıdan önce üzerine düşünmesi için beş hazırlık sorusu listeler.\n"
        "\n"
        "Sınır: Sorular sabittir; kurumunuzun verisine göre kişiselleşmez.\n"
        "\n"
        "Yorum: Soruların toplantıdan en az birkaç gün önce sahiplerine gönderilmesi, "
        "toplantının durum aktarımından karar üretimine dönüşmesini sağlar — çeyreklik "
        "değerlendirmenin değeri hazırlıkta belirlenir."
    ),

    # ─────────────────────────── RİSK HEATMAP ───────────────────────────

    "raporlar_risk_heatmap.5_5_risk_matrisi": (
        "Riskleri olasılık (1-5) ve etki (1-5) eksenlerinde 25 hücreli matrise yerleştirir; "
        "her hücre o bölgedeki risk sayısını gösterir.\n"
        "\n"
        "Hesap: RPN = olasılık × etki (iki çarpan). Değerler risk kaydına girilen 1-5 "
        "puanlardır.\n"
        "\n"
        "Eşik: RPN 15+ kritik (kırmızı), 8-14 yüksek (turuncu), 4-7 orta (sarı), 4 altı düşük "
        "(yeşil).\n"
        "\n"
        "Sınır: Buradaki RPN, FMEA'nın üç çarpanlı RPN'i (olasılık × etki × saptanabilirlik) "
        "DEĞİLDİR — saptanabilirlik boyutu modelde yoktur. Olasılık ve etki, hesap değil "
        "kullanıcı beyanıdır.\n"
        "\n"
        "Yorum: Matris önceliklendirme aracıdır, kesinlik aracı değil — 1-5 beyanlarının "
        "kurum içinde ortak ölçekle (tanımlı kriterlerle) verilmesi matrisi anlamlı kılar."
    ),

    "raporlar_risk_heatmap.en_yuksek_rpn_ilk_10": (
        "RPN değerine göre en yüksek 10 riski başlık, olasılık, etki ve durumla listeler.\n"
        "\n"
        "Hesap: RPN = olasılık × etki; liste azalan RPN sıralıdır.\n"
        "\n"
        "Eşik: Satır renkleri matrisle aynı RPN bantlarını kullanır (15+/8+/4+/altı).\n"
        "\n"
        "Yorum: İlk 10 listesi yönetim gündeminin doğal risk sırasıdır; ancak aynı RPN'e "
        "farklı yollarla ulaşılabilir (5×2 ile 2×5 aynı sayıdır) — yüksek ETKİLİ düşük "
        "olasılıklı riskler, sayısal eşitliğe rağmen ayrı muamele ister."
    ),

    # ─────────────────────────── SABAH ÖZETİ ───────────────────────────

    "raporlar_sabah_ozeti.son_veri_girisleri": (
        "Kurumda yapılan en son KPI ölçüm girişlerini listeler: gösterge, değer, zaman ve "
        "gireni kişi.\n"
        "\n"
        "Hesap: Giriş kayıtları oluşturulma zamanına göre sıralanır; en yeni 8 kayıt "
        "gösterilir.\n"
        "\n"
        "Sınır: Liste giriş ZAMANINA göredir, ölçüm dönemine göre değil — geçmiş bir döneme "
        "ait veri bugün girilirse listede en üstte görünür.\n"
        "\n"
        "Yorum: Bu akış kurumun veri girme temposunun nabzıdır; günlerce boş kalması ölçüm "
        "disiplininin zayıfladığının en erken işaretidir."
    ),

    # ─────────────────────────── SEKTÖR BENCHMARK ───────────────────────────

    "raporlar_sektor_benchmark.sektor_otomotiv_yan_sanayi": (
        "Kurumun adını, tespit edilen veya seçilen sektörünü ve sistemde izlenen süreç, "
        "gösterge ve kullanıcı sayılarını gösterir.\n"
        "\n"
        "Hesap: Sayılar kurumun canlı kayıt sayımlarıdır. Sektör, önce kullanıcı seçimine, "
        "yoksa kurum profilindeki sektör alanına göre belirlenir.\n"
        "\n"
        "Sınır: Profildeki sektör alanı boş veya yanlışsa kurum yanlış sektörle eşleşir; bu "
        "durumda sektör el ile seçilmelidir.\n"
        "\n"
        "Yorum: Kıyasın anlamlı olması sektör eşleşmesinin doğruluğuna bağlıdır — ilk "
        "kullanımda sektör etiketini kontrol edin."
    ),

    "raporlar_sektor_benchmark.sektor_ortalamalari": (
        "Seçilen sektör için tipik metrik değerlerini (OEE, zamanında ve eksiksiz teslimat, "
        "NPS vb.) referans olarak listeler.\n"
        "\n"
        "Sınır: Bu değerler CANLI SEKTÖR VERİSİ DEĞİLDİR — koda işlenmiş sabit referans "
        "değerlerdir ve diğer kurumların verisinden hesaplanmaz (anonim kıyas için yeterli "
        "kurum sayısı oluşana dek bilinçli tasarım kararı). Ekranda da bu uyarı yer alır.\n"
        "\n"
        "Yorum: Değerleri hedef değil sohbet başlatıcı olarak kullanın: 'bu metrikleri biz "
        "ölçüyor muyuz?' sorusu, 'sektöre göre neredeyiz?' sorusundan önce gelir."
    ),

    "raporlar_sektor_benchmark.ai_sektor_degerlendirmesi": (
        "Sektör referans metrikleri üzerine yapay zekâ ile üretilen kısa değerlendirme sunar: "
        "hangi metrikler kritik, hangi veriler sisteme girilmeli.\n"
        "\n"
        "Hesap: Yapay zekâya sektörün sabit referans değerleri ile kurumun süreç/gösterge "
        "sayıları verilir; modele kurumun bu metriklerdeki yerini VARSAYMAMASI açıkça "
        "söylenir.\n"
        "\n"
        "Sınır: Kurumun gerçek metrik ölçümü değerlendirmeye GİRMEZ (henüz toplanmıyor); "
        "çıktı yönlendirme metnidir, kıyas sonucu değildir. Yapay zekâ erişimi yoksa sabit "
        "öneri metni gösterilir. Metin deterministik değildir.\n"
        "\n"
        "Yorum: Değerlendirmedeki öneri listesini (hangi PG'leri eklemeli) somut aksiyon "
        "olarak alın; sektörle sayısal kıyas iddialarını ise veri toplanana dek ihtiyatla "
        "karşılayın."
    ),

    # ─────────────────────────── SEKTÖREL DETAY ───────────────────────────

    "raporlar_sektorel_detay.ozet_istatistik": (
        "Seçilen sektör şablon paketinin içerik sayılarını gösterir: strateji, süreç, "
        "gösterge, risk, ESG metriği ve tahmini kurulum süresi.\n"
        "\n"
        "Sınır: Sayılar KURUMUNUZUN verisi değil, hazır şablon paketinin içeriğidir. Şu an üç "
        "sektör paketi mevcuttur (finans, otomotiv, sağlık).\n"
        "\n"
        "Yorum: Paketi, sıfırdan plan kurmak yerine sektörünüzün tipik yapısından başlamak "
        "için ilham kaynağı olarak inceleyin."
    ),

    "raporlar_sektorel_detay.paketi_uygula_bilgi": (
        "Sektör paketinin şu an yalnızca önizleme olduğunu, tek tıkla kuruma uygulama "
        "özelliğinin henüz gelmediğini bildiren sabit bilgi kartıdır.\n"
        "\n"
        "Sınır: 'Paketi uygula' işlevi kodda henüz YOKTUR — paket içeriği kuruma otomatik "
        "aktarılamaz.\n"
        "\n"
        "Yorum: Paketten yararlanmak isterseniz strateji ve göstergeleri ilgili modüllerden "
        "elle oluşturmanız gerekir; paketi açık bir sekmede şablon olarak tutmak işi "
        "hızlandırır."
    ),

    "raporlar_sektorel_detay.performans_gostergeleri": (
        "Sektör şablon paketindeki örnek göstergeleri listeler: kod, ad, birim, hedef, "
        "periyot ve yön.\n"
        "\n"
        "Sınır: Bunlar kurumunuzun göstergeleri değil, sektör için önerilen ŞABLON "
        "göstergelerdir; hedef değerleri örnektir.\n"
        "\n"
        "Yorum: Listeyi kendi gösterge setinizle karşılaştırın — sektörün standart saydığı "
        "ama sizde ölçülmeyen göstergeler, ölçüm kapsamı geliştirmenin en hızlı adaylarıdır."
    ),

    "raporlar_sektorel_detay.riskler": (
        "Sektör şablon paketindeki tipik riskleri olasılık, etki ve RPN değerleriyle "
        "listeler.\n"
        "\n"
        "Hesap: RPN = olasılık × etki.\n"
        "\n"
        "Eşik: RPN 15+ kırmızı, 8-14 turuncu, altı normal.\n"
        "\n"
        "Sınır: Riskler kurumunuzun risk kaydı değil, sektör için önerilen örneklerdir.\n"
        "\n"
        "Yorum: Paket risklerini kendi risk matrisinizle karşılaştırın; sektörün tipik "
        "saydığı ama sizin kaydınızda olmayan riskler kör nokta adayıdır."
    ),

    "raporlar_sektorel_detay.stratejiler": (
        "Sektör şablon paketindeki örnek stratejileri kod, başlık, ağırlık ve alt "
        "stratejileriyle listeler.\n"
        "\n"
        "Sınır: Kurumunuzun stratejileri değil, sektör şablonudur; ağırlıklar örnek "
        "değerlerdir.\n"
        "\n"
        "Yorum: Şablonu stratejik planlama çalıştayında tartışma iskeleti olarak kullanın — "
        "hazır yapıyı aynen almak yerine kurumunuzun önceliklerine göre yeniden ağırlıklandırın."
    ),

    "raporlar_sektorel_detay.surecler": (
        "Sektör şablon paketindeki örnek süreçleri kod, ad ve ağırlıkla listeler.\n"
        "\n"
        "Sınır: Kurumunuzun süreçleri değil, sektör şablonudur.\n"
        "\n"
        "Yorum: Süreç envanterinizi bu listeyle karşılaştırmak, tanımlanmamış ama sektörde "
        "standart olan süreçleri (örn. tedarikçi kalite yönetimi) görünür kılar."
    ),

    "raporlar_sektorel_detay.uyum_standartlari": (
        "Sektör şablon paketinin hangi standartlarla uyumlu tasarlandığını etiket olarak "
        "gösterir (örn. IATF 16949, ISO 9001, ISO 14001).\n"
        "\n"
        "Sınır: Etiketler paketin tasarım referansıdır — kurumunuzun bu standartlara sahip "
        "olduğu veya paketi kurunca uyum sağlayacağı anlamına GELMEZ.\n"
        "\n"
        "Yorum: Sertifikasyon hedefi varsa paket göstergeleri iyi bir başlangıç kontrol "
        "listesi sunar; resmî uyum için standardın kendi gereklilik dokümanı esastır."
    ),

    # ─────────────────────────── STRATEJİ HİKAYESİ ───────────────────────────

    "raporlar_strateji_hikayesi.hikaye": (
        "Kurumun stratejik planının yıllar içindeki evrimini yapay zekâ ile yazılmış anlatı "
        "metni olarak sunar.\n"
        "\n"
        "Hesap: Anlatının dayandığı yıllık yapı sayıları (strateji, süreç, gösterge, ölçüm) "
        "deterministiktir; metin bu sayılarla modele yazdırılır.\n"
        "\n"
        "Sınır: Yapay zekâ erişimi yoksa sayıları özetleyen sabit şablon metin gösterilir; "
        "hangisinin gösterildiği ekranda belirtilmez. Metin deterministik değildir. Anlatı "
        "yapısal sayılara dayanır — performans/başarı değerlendirmesi içermez.\n"
        "\n"
        "Yorum: Hikayeyi kuruluş sunumları için taslak olarak kullanın; metindeki nitel "
        "ifadeleri yıllık snapshot tablosundaki sayılarla teyit edin."
    ),

    "raporlar_strateji_hikayesi.yillik_snapshot": (
        "Her plan yılının yapısal fotoğrafını tablolar: strateji, süreç, gösterge ve ölçüm "
        "sayıları.\n"
        "\n"
        "Hesap: Yıl başına kayıt sayımları; ölçüm sayısı takvim yılına, diğerleri plan yılına "
        "bağlanır.\n"
        "\n"
        "Sınır: İki farklı yıl anahtarı (takvim/plan) aynı tabloda yan yanadır — plan yılı "
        "takvimden kaydırılmış kurumlarda ölçüm sütunu diğerleriyle birebir örtüşmeyebilir.\n"
        "\n"
        "Yorum: Yapı sayısının hızla büyüdüğü yıllarda ölçüm sayısı aynı oranda artmıyorsa, "
        "plan kağıt üzerinde büyüyor ama ölçüm kültürü yetişmiyor demektir."
    ),

    "raporlar_strateji_hikayesi.kirilim_noktalari": (
        "Plan yapısında belirgin değişim yaşanan yılları vurgular.\n"
        "\n"
        "Hesap: Ardışık yıllar karşılaştırılır; strateji sayısında 1 ve üzeri VEYA süreç "
        "sayısında 2 ve üzeri mutlak değişim 'kırılım' sayılır.\n"
        "\n"
        "Sınır: Kırılım yalnızca YAPI SAYISINDAN tespit edilir — performans kırılımları "
        "(skor sıçraması/çöküşü) bu kartta görünmez. Eşikler kabadır; büyük kurumda 2 süreçlik "
        "değişim gürültü olabilir.\n"
        "\n"
        "Yorum: Her kırılım yılına 'o yıl ne oldu?' sorusunu sorun — yönetim değişikliği, "
        "yeniden yapılanma veya kapsam revizyonu izleri genelde burada görünür."
    ),

    # ─────────────────────────── STRATEJİK YILLIK ───────────────────────────

    "raporlar_stratejik_yillik.bolum_yapisi": (
        "Üretilecek yıllık strateji kitabının 14 bölümlük içindekiler yapısını listeler.\n"
        "\n"
        "Sınır: Bölüm listesi sabittir; her bölümün dosyada ne kadar dolu çıkacağı kurum "
        "verisine bağlıdır.\n"
        "\n"
        "Yorum: Üretimden önce özellikle veri yoğun bölümlerin (KPI özetleri, girişim "
        "portföyü) kaynağı olan modüllerde verilerin güncel olduğunu kontrol edin."
    ),

    "raporlar_stratejik_yillik.premium_pdf_35_sayfa": (
        "Kurumun yıllık strateji kitabını PDF olarak üretip indirir; önsözü yapay zekâ ile "
        "yazdırılır.\n"
        "\n"
        "Sınır: '~35 sayfa' sabit bir tahmindir — gerçek sayfa sayısı içeriğe göre değişir ve "
        "ölçülmez. Yapay zekâ erişimi yoksa önsöz sabit şablon metinle üretilir; metin "
        "deterministik değildir.\n"
        "\n"
        "Yorum: Kitabı dağıtmadan önce baştan sona gözle kontrol edin — veri girilmemiş "
        "bölümler boş veya kısa çıkar ve dokümanın bütün ağırlığını zedeler."
    ),

    # ─────────────────────────── SUNBURST ───────────────────────────

    "raporlar_sunburst.stratejik_hiyerarsi_sunburst": (
        "Vizyon → strateji → alt strateji → süreç hiyerarşisini iç içe halkalar (sunburst) "
        "olarak gösterir.\n"
        "\n"
        "Hesap: Strateji dilimleri K-Vektör ağırlık payıyla ölçeklenir; alt stratejiler "
        "stratejinin payını EŞİT bölüşür; süreç dilimleri katkı yüzdesinden görsel ölçekle "
        "türetilir.\n"
        "\n"
        "Sınır: Alt strateji dilimlerinin eşit bölüşümü gerçek ağırlığı yansıtmaz; süreç "
        "dilim büyüklüğü de yaklaşık bir görselleştirmedir. Dilim büyüklüklerinden sayısal "
        "sonuç çıkarmayın.\n"
        "\n"
        "Yorum: Grafiğin değeri oransal kesinlik değil yapısal bakıştır: hangi strateji kaç "
        "katmanla destekleniyor, hangi dal cılız kalmış — bir bakışta görülür."
    ),

    # ─────────────────────────── VERİ KALİTESİ ───────────────────────────

    "raporlar_veri_kalitesi.kritik_pg_ler": (
        "Puanlanamayan göstergeleri listeler: hiç ölçüm girilmemiş VEYA üç ve daha fazla "
        "eksiği olan göstergeler.\n"
        "\n"
        "Hesap: Her gösterge beş kriterde denetlenir — son ölçüm var mı, ölçüm 180 günden "
        "eski mi, hedef tanımlı mı, birim tanımlı mı, başarı puan aralığı tanımlı mı. Hiç "
        "ölçüm yoksa ya da eksik sayısı 3+ ise 'kritik' sayılır.\n"
        "\n"
        "Sınır: Sınıflandırma doluluk YÜZDESİYLE değil eksik ALAN SAYISIYLA yapılır. Liste en "
        "çok eksiği olandan başlayarak ilk 20 kaydı gösterir.\n"
        "\n"
        "Yorum: Kritik listesi, skor motorunun kör noktalarıdır — bu göstergeler hiçbir "
        "kurumsal skora katkı veremez. Temizlik sırasına buradan başlayın."
    ),

    "raporlar_veri_kalitesi.orta_risk_pg_ler": (
        "Puanlanabilen ama veri kalitesi düşük göstergeleri listeler: bir veya iki eksiği "
        "olanlar.\n"
        "\n"
        "Hesap: Kritik tanımına girmeyen ama en az bir eksiği (bayat ölçüm, tanımsız hedef, "
        "birim veya puan aralığı) olan göstergeler bu gruba düşer.\n"
        "\n"
        "Sınır: Liste ilk 20 kaydı gösterir; eksik sayısı temellidir, doluluk yüzdesi değil.\n"
        "\n"
        "Yorum: Bu grup en verimli iyileştirme alanıdır — bir iki alan tamamlamayla gösterge "
        "tam sağlıklı hale gelir; kritik gruba kaymadan önce müdahale edin."
    ),

    "raporlar_veri_kalitesi.surec_bazli_doluluk": (
        "Her süreç için göstergelerinin ne kadarına ölçüm girildiğini yüzde çubuğuyla "
        "gösterir.\n"
        "\n"
        "Hesap: Doluluk % = en az bir ölçümü olan gösterge / sürecin toplam göstergesi × 100. "
        "Liste en boş süreçten başlar.\n"
        "\n"
        "Eşik: %80+ yeşil, %50-80 sarı, %50 altı kırmızı.\n"
        "\n"
        "Sınır: 'Dolu' tanımı en az BİR ölçümün varlığıdır — güncellik veya süreklilik "
        "aranmaz; yıllar önce tek ölçüm girilmiş gösterge de dolu sayılır.\n"
        "\n"
        "Yorum: Doluluğu düşük süreçlerin skorları az sayıda göstergeye yaslanır ve "
        "dalgalanır; skor kıyaslamadan önce doluluk farklarını eşitlemeye çalışın."
    ),

    # ─────────────────────────── VRIO PORTFÖY ───────────────────────────

    "raporlar_vrio_portfoy.sayfa": (
        "Kurum kaynaklarını VRIO çerçevesine göre beş rekabet konumuna sınıflar: dezavantaj, "
        "parite, geçici avantaj, kullanılmayan avantaj ve sürdürülebilir avantaj.\n"
        "\n"
        "Hesap: Sınıflama karar ağacıdır — Değerli mi? → Nadir mi? → Taklidi zor mu? → "
        "Örgütlenme var mı? sorularının ilk 'hayır' cevabı konumu belirler; dördü de 'evet' "
        "ise sürdürülebilir avantajdır.\n"
        "\n"
        "Sınır: Dört boyut da kullanıcının işaretlediği beyanlardır — sistem hesaplamaz; "
        "sınıf yalnızca bu işaretlerden türetilir.\n"
        "\n"
        "Kaynak: Barney'nin kaynak temelli görüş çerçevesi (VRIO, 1991).\n"
        "\n"
        "Yorum: Değerlendirmeyi tek kişiye bırakmayın — V/R/I/O işaretleri yönetim ekibinde "
        "tartışılarak verildiğinde çerçeve gerçek stratejik değer üretir."
    ),

    # ─────────────────────────── YATIRIMCI SUNUM ───────────────────────────

    "raporlar_yatirimci_sunum.pptx_sunum_16_9": (
        "Yatırımcılara yönelik 18 slaytlık 16:9 sunumu PPTX olarak üretip indirir.\n"
        "\n"
        "Hesap: Sunumdaki yönetici özeti yapay zekâ ile yazdırılır; erişim yoksa sabit şablon "
        "metin kullanılır.\n"
        "\n"
        "Sınır: Yapay zekâ özeti deterministik değildir. Sunum kitaplığı sunucuda kurulu "
        "değilse üretim hata verir.\n"
        "\n"
        "Yorum: Yatırımcıya gitmeden önce her slaytı gözden geçirin — özellikle yapay zekâ "
        "metnindeki nitel iddiaları sayılarla teyit edin; sunumda savunulamayan cümle "
        "kalmamalı."
    ),

    "raporlar_yatirimci_sunum.slayt_yapisi": (
        "Üretilecek yatırımcı sunumunun 18 slaytlık yapısını başlık ve içerik özetiyle "
        "listeler.\n"
        "\n"
        "Sınır: Slayt yapısı büyük ölçüde sabit şablondur — yalnızca strateji sayısı ve "
        "girişim sayısı canlı veriden gelir.\n"
        "\n"
        "Yorum: Yapıyı önceden inceleyip hangi slaytların kurumunuz için zayıf kalacağını "
        "belirleyin; o slaytların kaynak verilerini üretimden önce tamamlayın."
    ),

    # ─────────────────────────── YÖNETİCİ LİDERLİK ───────────────────────────

    "raporlar_yonetici_liderlik.yoneticiler_karti": (
        "Süreç liderlerini, liderlik ettikleri süreç sayısı ve bu süreçlerin ortalama "
        "performans skoruyla listeler.\n"
        "\n"
        "Hesap: Liderin skoru = sorumlu olduğu süreçlerin skor motorundan gelen skorlarının "
        "düz ortalaması. Liste skora göre azalan sıralıdır.\n"
        "\n"
        "Sınır: Bu bir KİŞİSEL liderlik ölçümü değildir — liderin süreçlerinin KPI "
        "başarısıdır; sürecin performansında liderin payı ile dış etkenlerin payı ayrışmaz. "
        "Süreç-lider eşleştirmesi hiç yapılmamışsa skor hesaplanamaz, yalnızca yönetici rollü "
        "kullanıcı listesi gösterilir.\n"
        "\n"
        "Yorum: Skoru performans değerlendirme girdisi yapmadan önce süreçlerin ölçüm doluluk "
        "farklarını eşitleyin — az ölçülen süreçlerin lideri tek göstergenin insafına kalır."
    ),
}
