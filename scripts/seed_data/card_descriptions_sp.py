# -*- coding: utf-8 -*-
"""Stratejik Planlama (SP) modülü kart açıklamaları — 96 kart (sp* önekleri).

Yazım sözleşmesi için bkz. card_descriptions_k_radar.py başlığı.
Kod bağlamı 2026-07-21'de 4 paralel keşif ajanıyla çıkarıldı (dosya:satır kanıtlı).

Koddan doğrulanmış ortak notlar:
  - Çeyreklik review'daki "anomali" z-score istatistiğidir (2σ/3σ), ML değil.
  - "Aksiyon önerileri" kural tabanlı if-zinciridir, LLM çağrısı yok.
  - Strateji×Proje matrisinde "hizalama" = alt strateji↔süreç BAĞ SAYISI (count),
    katkı yüzdesi değil.
  - Strateji haritası hiyerarşik ilişki ağıdır (vis-network), BSC perspektif
    haritası değil.
"""

DESCRIPTIONS: dict[str, str] = {

    # ─────────────────── SP ÇEYREKLİK REVIEW ───────────────────

    "sp_ceyreklik_review.donem_secici": (
        "Değerlendirilecek yıl ve çeyreği seçtiren giriş kartıdır; 'Değerlendirme Oluştur' ile "
        "seçilen dönemin fotoğrafı üretilir.\n"
        "\n"
        "Hesap: Çeyrek ay aralıkları sabittir: Ç1 Oca-Mar, Ç2 Nis-Haz, Ç3 Tem-Eyl, Ç4 Eki-Ara.\n"
        "\n"
        "Sınır: Bazı alt kartlar (risk, anomali, geciken faaliyet) seçilen çeyreğe değil BUGÜNE "
        "göre hesaplanır — geçmiş çeyrek seçseniz de güncel durumu gösterirler.\n"
        "\n"
        "Yorum: Geçmiş dönem analizi yaparken hangi kartın döneme, hangisinin ana bağlı "
        "olduğunu ayırt ederek okuyun."
    ),

    "sp_ceyreklik_review.pg_durumu": (
        "Seçilen çeyrekte hedefinin üzerinde gerçekleşen ölçüm oranını ve veri girilmiş "
        "gösterge sayısını gösterir.\n"
        "\n"
        "Hesap: Hedef üstü % = çeyrekteki sayısal ölçümlerden gerçekleşmesi hedefe eşit veya "
        "üstünde olanlar / toplam ölçüm × 100.\n"
        "\n"
        "Sınır: Oran ÖLÇÜM başına sayılır — aynı göstergenin üç ölçümü paydada üç kez yer alır; "
        "'veri girilen PG' sayısı ise tekil gösterge sayar. İki sayı farklı granülerliktedir. "
        "Sayıya çevrilemeyen (aralık, işaretli) değerler orana girmez. Yön farkı gözetilmez — "
        "'azalması iyi' göstergelerde hedef üstü olmak başarı değildir (bkz. D0 kaydı).\n"
        "\n"
        "Yorum: Oranı tek başına değil 'veri girilen / toplam PG' kapsamıyla birlikte okuyun; "
        "az veriyle yüksek oran yanıltıcıdır."
    ),

    "sp_ceyreklik_review.strateji": (
        "Aktif ana strateji sayısını, alt strateji toplamını ve bu çeyrekte eklenen strateji "
        "sayısını gösterir.\n"
        "\n"
        "Hesap: Sayımlar aktif kayıtlar üzerinden yapılır; 'yeni', oluşturulma tarihi çeyrek "
        "aralığına düşenlerdir.\n"
        "\n"
        "Sınır: 'Yeni' sayısı plan yılı filtresine tabi değildir — yalnızca oluşturulma "
        "tarihine bakar; diğer iki sayı aktif plan yılına filtrelidir.\n"
        "\n"
        "Yorum: Çeyrek içinde strateji ekleme/çıkarma hareketliliği, planın oturmadığının veya "
        "bilinçli revizyonun izidir — hangisi olduğunu değişikliğin gerekçesi belirler."
    ),

    "sp_ceyreklik_review.okr_ilerleme": (
        "Amaçların (Objective) ortalama ilerleme yüzdesini ve amaç sayısını gösterir.\n"
        "\n"
        "Hesap: Her anahtar sonucun ilerlemesi (mevcut − başlangıç) / (hedef − başlangıç) "
        "oranından hesaplanır (0-1 aralığına kırpılır); amaç ilerlemesi anahtar sonuçların, "
        "genel değer ise amaçların düz ortalamasıdır.\n"
        "\n"
        "Sınır: İki katmanlı ortalama ağırlıksızdır — 2 anahtar sonuçlu amaç ile 8 anahtar "
        "sonuçlu amaç eşit ağırlıktadır.\n"
        "\n"
        "Yorum: Çeyrek ortasında ~%50 civarı doğal seyirdir; %100'e çok erken ulaşan amaçlar "
        "hedef kolaylığına, %10 altında kalanlar sahiplik sorununa işaret eder."
    ),

    "sp_ceyreklik_review.faaliyet": (
        "Aktif faaliyet sayısını, gecikenleri ve bu çeyrekte kapananları gösterir.\n"
        "\n"
        "Hesap: Aktif = 'Planlandı' veya 'Devam Ediyor' durumundakiler; geciken = bitiş tarihi "
        "BUGÜNÜ geçmiş ve tamamlanmamış olanlar; kapanan = tamamlanma tarihi çeyrek aralığına "
        "düşenler.\n"
        "\n"
        "Sınır: Geciken sayısı seçilen çeyreğe göre değil bugüne göre hesaplanır ve plan yılı "
        "filtresine tabi değildir — geçmiş dönem raporunda bile güncel gecikmeyi gösterir.\n"
        "\n"
        "Yorum: Kapanan/aktif oranı düşükse faaliyet listesi birikiyor demektir; geciken "
        "sayısı için süreç sayfalarındaki faaliyet listelerine inin."
    ),

    "sp_ceyreklik_review.risk": (
        "Açık risk sayısını ve kritik olanları gösterir.\n"
        "\n"
        "Hesap: Açık = kapatılmamış tüm aktif riskler; kritik = olasılık × etki değeri 16 ve "
        "üzeri olanlar.\n"
        "\n"
        "Sınır: Risk verisi döneme filtrelenmez — geçmiş çeyrek seçilse bile ANLIK açık "
        "riskler gösterilir. Olasılık ve etki kullanıcı beyanıdır.\n"
        "\n"
        "Yorum: Kritik sayısı sıfırdan büyükse çeyreklik toplantının ilk gündem maddesi "
        "hazırdır; detay risk ısı haritasında."
    ),

    "sp_ceyreklik_review.anomali": (
        "İstatistiksel olarak olağandışı seyreden göstergelerin sayısını öncelikle gösterir.\n"
        "\n"
        "Hesap: Her göstergenin son değeri, kendi geçmişinin ortalama ve standart sapmasıyla "
        "karşılaştırılır (z-skoru). Sapma 2σ'yı aşarsa anomali sayılır; 3σ üzeri 'yüksek', "
        "2-3σ arası 'orta' önceliktir. En az 5 ölçüm geçmişi gerekir.\n"
        "\n"
        "Sınır: Bu tespit KURAL TABANLI istatistiktir (z-skoru) — makine öğrenmesi değildir; "
        "bağlantı verdiği ekrandaki IsolationForest analizinden ayrı ve daha basit bir "
        "yöntemdir. Tarama döneme filtrelenmez, tüm göstergelerin son değerine bakar.\n"
        "\n"
        "Yorum: Anomali, hata değil 'açıklanması gereken sapma'dır — mevsimsellik ve veri "
        "giriş hatası en sık iki masum açıklamadır."
    ),

    "sp_ceyreklik_review.aksiyon_onerileri": (
        "Dönem metriklerine göre üretilen aksiyon önerilerini madde madde listeler.\n"
        "\n"
        "Hesap: Kural tabanlı üretim — hedef üstü oran %50'nin altındaysa, geciken faaliyet "
        "5'i aşarsa, kritik risk varsa, yüksek öncelikli anomali varsa veya göstergelerin "
        "%60'ından azına veri girilmişse ilgili öneri eklenir. Hiçbiri tetiklenmezse 'genel "
        "durum sağlıklı' mesajı gösterilir.\n"
        "\n"
        "Sınır: Öneriler YAPAY ZEKÂ ürünü değildir — sabit eşikli kural zinciridir; öncelik "
        "sıralaması yapılmaz, tetiklenen her kural listeye girer.\n"
        "\n"
        "Yorum: Listeyi kontrol listesi olarak kullanın; önerilerin göreli önemini dönem "
        "bağlamınıza göre siz sıralayın."
    ),

    # ─────────────────── SP STRATEJİ × PROJE MATRİSİ ───────────────────

    "sp_strategy_project_matrix.nasil_okunur": (
        "Matrisin okuma kılavuzu niteliğinde sabit bilgi kartıdır: her hücre, projenin o ana "
        "stratejiye kaç alt strateji↔süreç bağıyla dokunduğunu gösterir; koyu hücre güçlü "
        "ilişki, boş hücre bağlantısızlıktır.\n"
        "\n"
        "Sınır: Kart veri ölçmez; 'hizalama' burada bağ SAYISIDIR, katkı yüzdesi veya kalite "
        "ölçüsü değildir.\n"
        "\n"
        "Yorum: Matristen 'hangi proje hangi stratejiye hizmet ediyor' sorusunun haritasını "
        "çıkarın; bağın gücünü değerlendirmek ayrı bir içerik incelemesi ister."
    ),

    "sp_strategy_project_matrix.hizalama_matrisi": (
        "Ana stratejiler (satır) ile projeler (sütun) arasındaki bağlantı yoğunluğunu ısı "
        "haritası olarak gösterir; satır ve sütun toplamları kenarlarda.\n"
        "\n"
        "Hesap: Hücre değeri = proje → süreç → alt strateji → ana strateji zincirindeki bağ "
        "SAYISIDIR. Renk koyuluğu, hücrenin matristeki en büyük değere oranıyla ölçeklenir.\n"
        "\n"
        "Sınır: 'Hizalama' bağ adedidir — katkı yüzdesi veya stratejik ağırlık değildir; çok "
        "bağlı ama önemsiz ilişkiler koyu görünebilir. Matris en fazla 60 projeyi kapsar; "
        "fazlası görünmez.\n"
        "\n"
        "Yorum: Tamamen boş satırlar (projesiz stratejiler) ve boş sütunlar (stratejisiz "
        "projeler) matrisin en değerli çıktısıdır — ikisi de altta ayrıca listelenir."
    ),

    "sp_strategy_project_matrix.ozet_strateji": (
        "Matristeki ana strateji sayısını gösterir.\n"
        "\n"
        "Hesap: Aktif plan yılındaki aktif ana stratejiler sayılır.\n"
        "\n"
        "Yorum: Bu sayı matrisin satır boyutudur; strateji sayısı proje sayısına göre çok "
        "azsa matris geniş ve seyrek görünür — bu bir hata değil portföy yapınızdır."
    ),

    "sp_strategy_project_matrix.ozet_proje": (
        "Matristeki proje sayısını gösterir.\n"
        "\n"
        "Hesap: Arşivlenmemiş projeler sayılır.\n"
        "\n"
        "Sınır: En fazla 60 proje matrise dahil edilir — portföy daha büyükse sayı ve matris "
        "eksik kalır.\n"
        "\n"
        "Yorum: 60 sınırına yakın değerlerde matrisin tam portföyü temsil etmediğini bilerek "
        "okuyun."
    ),

    "sp_strategy_project_matrix.ozet_en_guclu_hizalama": (
        "Matristeki en yüksek hücre değerini — yani en çok bağla hizalanmış proje-strateji "
        "çiftinin bağ sayısını — gösterir.\n"
        "\n"
        "Hesap: Tüm hücrelerin en büyüğü alınır.\n"
        "\n"
        "Sınır: 'En güçlü' nicelik ifadesidir — en çok bağ, en stratejik ilişki anlamına "
        "gelmeyebilir.\n"
        "\n"
        "Yorum: Bu değer matrisin renk ölçeğinin tavanıdır; tek bir aşırı bağlı çift, diğer "
        "tüm hücreleri soluk gösterebilir."
    ),

    "sp_strategy_project_matrix.ozet_hizalama_kapsama": (
        "Matristeki dolu hücre oranını yüzde olarak gösterir.\n"
        "\n"
        "Hesap: Kapsama % = en az bir bağı olan hücre / toplam hücre (strateji × proje) × 100.\n"
        "\n"
        "Eşik: %70+ yeşil, %40-70 turuncu, altı kırmızı.\n"
        "\n"
        "Sınır: Kapsama bağın VARLIĞINI sayar, gücünü değil — her hücrede tek bağ olan matris "
        "%100 kapsama gösterir.\n"
        "\n"
        "Yorum: Düşük kapsama her zaman kötü değildir — her projenin her stratejiye "
        "bağlanması da hizalama değil odaksızlıktır; makul hedef, her projenin EN AZ BİR "
        "stratejiye güçlü bağıdır."
    ),

    "sp_strategy_project_matrix.hizalanmamis_projeler": (
        "Hiçbir stratejiye bağı olmayan projeleri listeler.\n"
        "\n"
        "Hesap: Tüm strateji satırlarında hücresi sıfır olan projeler seçilir; ilk 20 "
        "gösterilir.\n"
        "\n"
        "Sınır: Liste, matrise giren en fazla 60 projelik evrenden türetilir.\n"
        "\n"
        "Yorum: Bu listedeki her proje şu sorunun muhatabıdır: 'Bu işi neden yapıyoruz?' — "
        "cevap varsa bağ kurulmalı, yoksa proje sorgulanmalıdır."
    ),

    "sp_strategy_project_matrix.stratejisi_olmayan_projeler": (
        "Hiçbir projeyle desteklenmeyen ana stratejileri listeler.\n"
        "\n"
        "Hesap: Tüm proje sütunlarında hücresi sıfır olan stratejiler seçilir; ilk 20 "
        "gösterilir.\n"
        "\n"
        "Sınır: Kartın teknik kodu 'stratejisi olmayan projeler' dese de gösterilen içerik "
        "PROJESİZ STRATEJİLERDİR — matristeki kırmızı vurgulu liste budur.\n"
        "\n"
        "Yorum: Projesiz strateji, kaynak atanmamış niyettir — ya girişim/proje bağlanmalı ya "
        "da stratejinin gerçekçiliği tartışılmalıdır."
    ),

    # ─────────────────── SP STRATEJİ HARİTASI ───────────────────

    "sp_strateji_haritasi.ana_strateji": (
        "Haritada gösterilen ana strateji sayısını özetler.\n"
        "\n"
        "Hesap: Kullanıcının kapsamındaki aktif plan yılına ait aktif ana stratejiler "
        "sayılır.\n"
        "\n"
        "Yorum: Sağlıklı bir haritada bu sayı azdır (tipik 3-7) — strateji enflasyonu haritayı "
        "okunmaz, planı yönetilmez kılar."
    ),

    "sp_strateji_haritasi.alt_strateji": (
        "Haritadaki alt strateji düğümü sayısını özetler.\n"
        "\n"
        "Hesap: Aktif alt stratejiler sayılır.\n"
        "\n"
        "Yorum: Alt strateji/ana strateji oranı dengesizse (bir stratejide 10, diğerinde 1) "
        "harita üzerinde görsel olarak hemen fark edilir — dengesizlik kaynak dağılımının da "
        "habercisidir."
    ),

    "sp_strateji_haritasi.surec": (
        "Haritadaki süreç düğümü sayısını özetler.\n"
        "\n"
        "Hesap: Alt stratejilere bağlı süreç düğümleri sayılır; aynı süreç haritaya bir kez "
        "girer.\n"
        "\n"
        "Sınır: Okunabilirlik için alt strateji başına en fazla 12 süreç düğümü çizilir — "
        "sayı, gerçek süreç toplamından DÜŞÜK olabilir.\n"
        "\n"
        "Yorum: Bu sayaç haritanın kapsamını gösterir; kesin süreç envanteri için süreç "
        "modülüne bakın."
    ),

    "sp_strateji_haritasi.pg": (
        "Haritadaki performans göstergesi düğümü sayısını özetler.\n"
        "\n"
        "Hesap: Süreçlere bağlı aktif göstergeler sayılır; süreç başına en fazla 7 gösterge "
        "düğümü çizilir, fazlası '+N PG' özet düğümüne toplanır.\n"
        "\n"
        "Sınır: Sayaç haritada ÇİZİLEN düğümleri sayar — özet düğümüne katlananlar dahil "
        "değildir; gerçek gösterge toplamı daha yüksek olabilir.\n"
        "\n"
        "Yorum: Haritadaki nabız halkaları (kırmızı <50, sarı 50-80) sorunlu göstergeleri "
        "görsel olarak öne çıkarır — sayaçtan çok nabızlara bakın."
    ),

    "sp_strateji_haritasi.str_girisim": (
        "Haritadaki stratejik girişim sayısını özetler; girişim yoksa kart gizlenir.\n"
        "\n"
        "Hesap: Aktif girişimler sayılır; haritada bağlı oldukları stratejiye kesikli çizgiyle "
        "bağlanırlar.\n"
        "\n"
        "Yorum: Girişimler stratejinin 'değişim motoru'dur — haritada stratejisine bağlı "
        "girişim görünmeyen değişim hedefleri kağıt üzerinde kalma riskindedir."
    ),

    "sp_strateji_haritasi.strateji_haritasi": (
        "Vizyon → ana strateji → alt strateji → süreç/girişim → gösterge/proje zincirini "
        "etkileşimli ilişki ağı olarak çizer; tıklamayla yol vurgulama, arama ve yakınlaştırma "
        "sunar. Sorunlu göstergelerde canlı nabız halkası yanar.\n"
        "\n"
        "Eşik: Nabız — skor 50 altı kırmızı, 50-80 sarı; 80 üzeri sakin yeşil.\n"
        "\n"
        "Sınır: Bu, Kaplan-Norton tarzı dört perspektifli BSC strateji haritası DEĞİL, "
        "hiyerarşik ilişki ağıdır. Okunabilirlik sınırları vardır: alt strateji başına 12 "
        "süreç, süreç başına 7 gösterge çizilir — harita tam envanter değildir. Projeler "
        "yalnızca bir girişime bağlıysa görünür.\n"
        "\n"
        "Yorum: Haritanın asıl değeri kopuklukları göstermesidir: vizyona giden yolu olmayan "
        "dallar ve nabzı kırmızı yanan uçlar, stratejik sohbetin başlangıç noktalarıdır."
    ),

    # ─────────────────── SP ANA SAYFA ───────────────────

    "sp.ana_strateji": (
        "Aktif plan yılındaki ana strateji sayısını ve altlarındaki toplam alt strateji "
        "sayısını gösterir.\n"
        "\n"
        "Hesap: Aktif kayıtlar sayılır; seçili plan yılında hiç veri yoksa en çok kayıtlı "
        "yıla otomatik düşülür.\n"
        "\n"
        "Yorum: Stratejik plan disiplininde az sayıda ana strateji (3-7) normaldir; sayının "
        "hızla artması odak kaybının ilk işaretidir."
    ),

    "sp.akis_olgunlugu": (
        "Stratejik plan kurulumunun tamamlanma yüzdesini gösterir.\n"
        "\n"
        "Hesap: Dört adımın doluluğu sayılır — misyon, vizyon, değerler/etik ve en az bir "
        "strateji; her adım %25 katkı verir.\n"
        "\n"
        "Eşik: %75+ yeşil, %50-75 turuncu, altı mavi.\n"
        "\n"
        "Sınır: 'Olgunluk' burada yalnızca dört alanın DOLU olmasıdır — içerik kalitesini "
        "veya stratejinin skorunu ölçmez; %100, kurulumun bittiğini söyler, planın iyi "
        "olduğunu değil.\n"
        "\n"
        "Yorum: %100'e ulaştıktan sonra bu kartın işi biter; olgunluğun gerçek ölçüsü ölçüm "
        "kapsamı ve skor kartlarındadır."
    ),

    "sp.k_vektor_vizyon": (
        "K-Vektör motoruyla hesaplanan vizyon puanını 0-100 ölçeğinde gösterir.\n"
        "\n"
        "Hesap: 1000 puanlık vizyon bütçesi stratejilere ham ağırlıklarıyla dağıtılır; her "
        "birimin gerçekleşen katkısı skoruyla orantılı toplanır ve ölçülen kota üzerinden "
        "1000'lik puana, oradan 10'a bölünerek 100'lük ölçeğe çevrilir.\n"
        "\n"
        "Sınır: Kart yalnızca K-Vektör açık kurumlarda görünür. Ölçülmemiş alt stratejiler "
        "hesaba katılmaz — kota ölçülenlere yeniden dağıtılır; ölçüm kapsamı düşükken puan "
        "az sayıda ölçümün temsiline dönüşür ve kapsam bu kartta gösterilmez.\n"
        "\n"
        "Yorum: Puanı yorumlamadan önce kaç alt stratejinin fiilen ölçüldüğüne bakın; dar "
        "kapsamla gelen yüksek puan güven vermez."
    ),

    "sp.plan_donemi": (
        "İçinde çalışılan aktif plan yılını gösterir.\n"
        "\n"
        "Hesap: Oturumda seçilen yıl esas alınır; seçim yoksa içinde bulunulan takvim yılı, "
        "o da tanımlı değilse mevcut ilk uygun dönem gösterilir.\n"
        "\n"
        "Yorum: SP ekranlarındaki tüm sayılar bu döneme filtrelidir — beklenmedik bir sayı "
        "gördüğünüzde önce hangi dönemde olduğunuzu kontrol edin."
    ),

    "sp.etiketsiz_strateji": (
        "Herhangi bir plan yılına atanmamış (dönemsiz) strateji sayısını gösterir.\n"
        "\n"
        "Hesap: Yüklenen strateji listesinde plan yılı alanı boş olanlar sayılır.\n"
        "\n"
        "Eşik: Sıfırdan büyükse kırmızı, sıfırsa yeşil.\n"
        "\n"
        "Sınır: Sayım ekrana yüklenen listeyle sınırlıdır.\n"
        "\n"
        "Yorum: Etiketsiz strateji, dönem karşılaştırma ve yıl bazlı raporların dışında "
        "kalır — kırmızı görünüyorsa stratejileri ilgili döneme atayın."
    ),

    "sp.kimlik": (
        "Kurumsal kimliğin üç bileşeninin (misyon, vizyon, değerler) tanımlı olup olmadığını "
        "tik ikonlarıyla özetler.\n"
        "\n"
        "Eşik: Üst çizgi, misyon VE vizyon doluysa yeşil, aksi turuncu.\n"
        "\n"
        "Sınır: Renk yalnız misyon+vizyona bakar; değerler tiki renk kararına girmez. Etik "
        "kurallar bu kartta ayrıca gösterilmez.\n"
        "\n"
        "Yorum: Kimlik metinleri plan yılına bağlı tutulur (yıllık kimlik) — yıl değiştirip "
        "boş görünüyorsa metinler o dönem için henüz girilmemiş demektir."
    ),

    "sp.misyon": (
        "Kurumun (aktif dönem için) misyon metnini gösterir; tanımsızsa 'henüz eklenmemiş' "
        "uyarısı ve bekliyor rozeti görünür.\n"
        "\n"
        "Hesap: Metin, dönem kimliğinden okunur; dönemsel kayıt yoksa kurum profilindeki "
        "genel misyon gösterilir.\n"
        "\n"
        "Yorum: Misyon 'neden varız' sorusunun cevabıdır — tüm strateji ağacının çatısıdır; "
        "boş bırakılması alt kartların bağlamını zayıflatır."
    ),

    "sp.vizyon": (
        "Kurumun (aktif dönem için) vizyon metnini gösterir; K-Vektör açık kurumlarda "
        "vizyonun altında gerçekleşme puanı barı da yer alır.\n"
        "\n"
        "Hesap: Bar puanı K-Vektör vizyon puanıdır (1000'lik puanın 100'lük ölçeğe "
        "indirgenmiş hali).\n"
        "\n"
        "Sınır: Bar yalnızca K-Vektör etkin kurumlarda görünür; metin dönemsel kimlikten, "
        "yoksa kurum profilinden gelir.\n"
        "\n"
        "Yorum: Vizyon metni ile puanını birlikte okumak bu kartın amacıdır: iddia (metin) "
        "ve gerçekleşme (bar) aynı karede durur."
    ),

    "sp.degerler_ve_etik_kurallar": (
        "Kurumun temel değerlerini ve etik kurallarını madde listesi olarak gösterir.\n"
        "\n"
        "Hesap: Metinler satır veya noktalı virgül ayracıyla maddelere bölünerek gösterilir; "
        "'tamamlandı' rozeti, değerler VEYA etik metinden en az biri doluysa yanar.\n"
        "\n"
        "Yorum: Değerler stratejinin eleme filtresidir — bir girişim değerlerle çelişiyorsa "
        "sayısal getirisi ne olursa olsun tartışma buradan başlamalıdır."
    ),

    "sp.strateji_agirlik_skor_gorsellestirme": (
        "Her ana stratejiyi bir daireyle gösterir: dairenin boyutu K-Vektör ağırlığını, "
        "rengi mevcut skoru anlatır.\n"
        "\n"
        "Hesap: Boyut, stratejinin ham ağırlığının en büyük ağırlığa oranıyla ölçeklenir; "
        "renk K-Vektör strateji skorundan gelir.\n"
        "\n"
        "Eşik: Skor 75+ yeşil, 50-74 turuncu, 50 altı kırmızı, ölçümsüz gri.\n"
        "\n"
        "Sınır: Kart yalnızca K-Vektör etkin ve ağırlıkları atanmış kurumlarda görünür; "
        "ölçülmemiş stratejiler gri ve '—' gösterilir.\n"
        "\n"
        "Yorum: Büyük ve kırmızı daireler en kritik kombinasyondur — kuruma göre en ağır "
        "sayılan strateji düşük performansta demektir; küçük yeşil daireler ise ağırlık "
        "artırımı tartışmasına adaydır."
    ),

    "sp.strateji_listesi_ana_stratejiler_alt_stratejiler": (
        "Ana stratejileri, altlarındaki aktif alt stratejilerle birlikte listeler; K-Vektör "
        "açık kurumlarda strateji başına gerçekleşen katkı barı ve alt strateji skor barları "
        "gösterilir.\n"
        "\n"
        "Hesap: Ana strateji barı = gerçekleşen katkı / atanmış kota; alt strateji barı "
        "K-Vektör alt strateji skorudur (0-100 kırpılır).\n"
        "\n"
        "Sınır: Barlar yalnızca K-Vektör etkin kurumlarda; kota atanmamış stratejilerde "
        "katkı '—' gösterilir.\n"
        "\n"
        "Yorum: Liste, planın omurgasıdır — alt stratejisi olmayan ana stratejiler 'niyetten "
        "ibaret' kalmış dallardır; önce onları detaylandırın."
    ),

    "sp.surec_iyilestirme_faaliyetleri": (
        "Süreç iyileştirme faaliyetleri modülüne geçiş kartıdır.\n"
        "\n"
        "Sınır: Bu kart SAYI VEYA VERİ GÖSTERMEZ — adına rağmen faaliyet listesi/durumu "
        "içermez; yalnızca ilgili modüle bağlantı verir.\n"
        "\n"
        "Yorum: Faaliyet sayıları ve gecikme durumu için süreç modülünü veya çeyreklik "
        "değerlendirme ekranını kullanın."
    ),

    "sp.bireysel_hedefler": (
        "Bireysel performans modülüne geçiş kartıdır.\n"
        "\n"
        "Sınır: Bu kart SAYI VEYA VERİ GÖSTERMEZ — adına rağmen hedef sayısı/ilerlemesi "
        "içermez; yalnızca bireysel modüle bağlantı verir.\n"
        "\n"
        "Yorum: Bireysel hedeflerin kurum stratejisiyle bağını görmek için Bireysel Hedef "
        "Hizalama raporuna bakın."
    ),

    # ─────────────────── SP YÖNETİCİ PANELİ (EXEC) ───────────────────

    "sp_exec_dashboard.saglik_skoru": (
        "Stratejik planın genel sağlığını 0-100 tek skorda özetler.\n"
        "\n"
        "Hesap: Beş bileşenin ağırlıklı toplamıdır — PG hedef üstü oranı %40, PG veri "
        "kapsamı %20, faaliyet zamanlaması (100 − gecikme oranı) %20, kritik risk yokluğu "
        "%10, yüksek anomali yokluğu %10. Eksik bileşen varsa mevcutlar üzerinden normalize "
        "edilir.\n"
        "\n"
        "Eşik: 75+ sağlıklı (yeşil), 50-74 izleme (turuncu), 50 altı acil (kırmızı).\n"
        "\n"
        "Sınır: Girişim ilerlemesi skora GİRMEZ (yanında ayrı gösterilir). Bileşen "
        "eksikken skor kalan bileşenlerin temsiline daralır.\n"
        "\n"
        "Yorum: Skoru tek sayı olarak değil bileşenleriyle okuyun — %40'lık PG bileşeni "
        "veri girilmeyen dönemlerde skoru sürükler; düşüş her zaman performans değil bazen "
        "ölçüm boşluğudur."
    ),

    "sp_exec_dashboard.pg_hedef_ustu": (
        "Hedefine ulaşan gösterge ölçümlerinin oranını ve veri kapsamını gösterir.\n"
        "\n"
        "Hesap: Hedef üstü % = gerçekleşmesi hedefe eşit/üstü sayısal ölçümler / "
        "karşılaştırılabilir ölçümler × 100.\n"
        "\n"
        "Eşik: %70+ yeşil, %50-70 turuncu, altı kırmızı.\n"
        "\n"
        "Sınır: Yalnızca hem gerçekleşmesi hem hedefi sayıya çevrilebilen kayıtlar sayılır; "
        "yön farkı gözetilmez — 'azalması iyi' göstergelerde hedef üstü olmak başarı "
        "değildir (bkz. D0 kaydı).\n"
        "\n"
        "Yorum: Oranla birlikte 'veri var' kapsamını okuyun; kapsam düşükken oran kurumun "
        "değil, veri giren azınlığın fotoğrafıdır."
    ),

    "sp_exec_dashboard.girisim_sagligi": (
        "Devam etmekte olan stratejik girişimlerin ortalama ilerlemesini ve adedini "
        "gösterir.\n"
        "\n"
        "Hesap: Yıl kapsamına giren, durumu 'yürütmede' olan girişimlerin ilerleme "
        "yüzdelerinin ortalaması alınır.\n"
        "\n"
        "Sınır: Yalnızca 'yürütmede' durumundakiler hesaba girer; ilerleme yüzdesi girişim "
        "kartına ELLE girilen beyandır — faaliyet/KPI verisinden türetilmez.\n"
        "\n"
        "Yorum: Ortalama tek başına yanıltabilir; bir girişim %90, diğeri %10 iken %50 "
        "görünür — dağılım için girişim listesine inin."
    ),

    "sp_exec_dashboard.gecikmis_faaliyet": (
        "Bitiş tarihi geçmiş ve tamamlanmamış faaliyet sayısını, toplam faaliyetle birlikte "
        "gösterir.\n"
        "\n"
        "Hesap: Geciken = tamamlanmamış VE bitiş tarihi bugünden önce olan faaliyetler.\n"
        "\n"
        "Yorum: Geciken oranı %20'yi aşarsa planlama gerçekçiliği sorgulanmalıdır — sürekli "
        "gecikme çoğu zaman disiplin değil kapasite sorunudur."
    ),

    "sp_exec_dashboard.kritik_risk": (
        "Kritik risk sayısını ve toplam açık risk sayısını gösterir.\n"
        "\n"
        "Hesap: Kritik = olasılık × etki değeri 16 ve üzeri olan aktif riskler; açık = "
        "kapatılmamış riskler.\n"
        "\n"
        "Sınır: Olasılık ve etki 1-5 kullanıcı beyanıdır; 16 eşiği 5×5 matrisin 'yüksek × "
        "yüksek' bölgesine karşılık gelir.\n"
        "\n"
        "Yorum: Kritik sayısı sıfır değilse sağlık skorundan 10 puan gider — ama asıl konu "
        "puan değil, o risklerin azaltım planıdır."
    ),

    "sp_exec_dashboard.yuksek_anomali": (
        "Göstergelerde tespit edilen yüksek öncelikli istatistiksel sapma sayısını (ve orta "
        "seviyeyi) gösterir.\n"
        "\n"
        "Hesap: Her göstergenin son değeri kendi geçmişinin ortalama/sapmasıyla "
        "karşılaştırılır (z-skoru, eşik 2σ); 3σ üzeri 'yüksek' sayılır. Tarama 100 "
        "göstergeyle sınırlıdır.\n"
        "\n"
        "Sınır: Kural tabanlı istatistiktir, makine öğrenmesi değildir; en az 5 ölçüm "
        "geçmişi olmayan göstergeler taranamaz.\n"
        "\n"
        "Yorum: Yüksek anomali 'kötü haber' değil 'bakılmamış haber'dir — veri hatası da "
        "olabilir, gerçek kırılma da; ikisi de bakım ister."
    ),

    "sp_exec_dashboard.aktif_tetikleyici": (
        "Aktif yeniden planlama tetikleyicisi sayısını ve son 7 günde ateşlenenleri "
        "gösterir.\n"
        "\n"
        "Hesap: Aktif tetikleyiciler sayılır; 'ateşlenen', son ateşlenme zamanı 7 gün "
        "içinde olanlardır.\n"
        "\n"
        "Sınır: Bu kart plan yılına FİLTRELENMEZ — paneldeki diğer kartlar dönem bazlıyken "
        "tetikleyiciler kurum genelidir.\n"
        "\n"
        "Yorum: Son 7 günde ateşlenme varsa panelin geri kalanını o tetikleyicinin bağlamında "
        "okuyun — sistem size 'planı gözden geçir' sinyali vermiş demektir."
    ),

    "sp_exec_dashboard.kvektor_gelisimi": (
        "K-Vektör vizyon puanının zaman içindeki gelişimini çizgi grafikle gösterir — "
        "günlük (son 30 gün), aylık (12 ay), çeyreklik (8 çeyrek) ve yıllık (5 yıl) "
        "görünümler.\n"
        "\n"
        "Hesap: Her nokta, o tarihteki verilerle yeniden hesaplanan vizyon puanıdır "
        "(1000'lik puanın 100'e indirgenmişi).\n"
        "\n"
        "Sınır: Yalnızca K-Vektör etkin kurumlarda doludur; kapalıysa noktalar boş kalır. "
        "Geçmiş noktalar bugünkü veriyle GERİYE DÖNÜK hesaplanır — sonradan girilen veri "
        "geçmiş noktaları da değiştirir.\n"
        "\n"
        "Yorum: Eğimin yönü mutlak değerden önemlidir; ani sıçramalar genelde toplu veri "
        "girişinin izidir, gerçek performans değişiminin değil."
    ),

    "sp_exec_dashboard.aylik_saglik_trendi": (
        "Son 12 ayın aylık 'hedef üstü ölçüm oranını' çizgi grafikle ve 12 aylık değişim "
        "farkıyla gösterir.\n"
        "\n"
        "Hesap: Her ay için hedef üstü % = o ayki hedefe eşit/üstü sayısal ölçümler / "
        "karşılaştırılabilir ölçümler × 100.\n"
        "\n"
        "Sınır: Kart teknik adında 'sağlık trendi' geçse de gösterilen TEK bileşendir — "
        "beş bileşenli sağlık skorunun trendi değildir. Aylar takvim tarihine göredir, plan "
        "yılına filtrelenmez.\n"
        "\n"
        "Yorum: Aylık dalgalanma ölçüm periyotlarından etkilenir — çeyreklik ölçülen "
        "göstergeler ara aylarda seriyi inceltir; trendi üç aylık pencereyle okuyun."
    ),

    "sp_exec_dashboard.strateji_siralamasi": (
        "Stratejileri gösterge başarısına göre sıralar: en iyi 5 ve en düşük 5.\n"
        "\n"
        "Hesap: Strateji başına hedef üstü % = stratejiye (alt strateji→süreç zinciriyle) "
        "bağlı göstergelerin hedefe eşit/üstü ölçüm oranı. Yalnızca verisi olan stratejiler "
        "sıralanır.\n"
        "\n"
        "Sınır: Bu sıralama K-Vektör skoru DEĞİLDİR — ayrı ve daha basit bir hesaptır; iki "
        "ekran aynı strateji için farklı sıra verebilir. Verisiz stratejiler listede hiç "
        "görünmez.\n"
        "\n"
        "Yorum: 'En düşük 5'te olmayan bir strateji iyi durumda olmayabilir — hiç "
        "ölçülmüyor olabilir; listeye girmeyenleri ayrıca kontrol edin."
    ),

    "sp_exec_dashboard.otomatik_vurgular": (
        "Haftanın dikkat gerektiren konularını otomatik listeler.\n"
        "\n"
        "Hesap: Kural tabanlı — sağlık skoru 50'nin altındaysa, hedef üstü oran %50'nin "
        "altındaysa, geciken faaliyet 5'i aşarsa, kritik risk veya yüksek anomali varsa, son "
        "7 günde tetikleyici ateşlendiyse ya da göstergelerin %60'ından azına veri "
        "girildiyse ilgili uyarı üretilir.\n"
        "\n"
        "Sınır: Yapay zekâ KULLANILMAZ — sabit eşikli kural listesidir; hiçbir kural "
        "tetiklenmezse 'kabul edilebilir seviye' mesajı gösterilir.\n"
        "\n"
        "Yorum: Vurgular haftalık yönetim rutininin gündem taslağıdır; her maddenin detayı "
        "paneldeki ilgili kartta durur."
    ),

    "sp_exec_dashboard.ai_pivot_onerileri": (
        "Kurumun anlık fotoğrafından üretilen 3-5 stratejik pivot önerisini (yeniden "
        "odaklan / sonlandır / hızlandır / yeni girişim / risk azalt) gerekçe ve önerilen "
        "aksiyonla listeler.\n"
        "\n"
        "Hesap: Yapay zekâ erişimi varsa kurum özeti ve son tetikleyici olaylar modele "
        "verilir. Erişim yoksa kural motoru çalışır (hedef üstü <%50, gecikme oranı >%20, "
        "kritik risk, yüksek anomali, girişim ilerlemesi <%30 koşulları).\n"
        "\n"
        "Sınır: Kaynak rozetinden ayırt edilir — 'AI' gerçek model çıktısı, 'kural motoru' "
        "deterministik üretimdir; kota aşımında da kurala düşülür. Model çıktısı "
        "deterministik değildir.\n"
        "\n"
        "Yorum: Önerileri karar değil gündem maddesi olarak alın; gerekçedeki sayıları "
        "paneldeki kartlardan doğrulayın."
    ),

    "sp_exec_dashboard.ai_yonetici_ozeti": (
        "Panelin üstünde 2-3 cümlelik yönetici özeti gösterir: öne çıkan kazanım, kırmızı "
        "bayrak ve haftanın odağı.\n"
        "\n"
        "Hesap: Önce HER ZAMAN kural tabanlı özet üretilir (sağlık skoru, hedef üstü oran, "
        "eksik veri, kırmızı bayraklar); yapay zekâ erişimi varsa model bu özeti yeniden "
        "yazar ve 'AI' rozeti görünür, aksi halde 'otomatik' rozetiyle kural metni kalır.\n"
        "\n"
        "Sınır: Model metni deterministik değildir; rozet hangi kaynağın konuştuğunu "
        "gösterir.\n"
        "\n"
        "Yorum: Özet açılış cümlenizdir, kanıtınız değil — içindeki her sayı paneldeki "
        "kartlarda doğrulanabilir olmalıdır."
    ),

    # ─────────────────── SP VRIO ───────────────────

    "sp_vrio.aciklama_degerli": (
        "VRIO çerçevesinin ilk sorusunu açıklayan sabit eğitim kartıdır: kaynak, müşteri "
        "için değer üretiyor veya bir tehdidi/fırsatı karşılıyor mu?\n"
        "\n"
        "Sınır: Kart veri göstermez — kaynaklarınızın V işaretleri alttaki tabloda durur.\n"
        "\n"
        "Yorum: 'Değerli mi' sorusuna kurum içi gururla değil müşteri gözüyle cevap verin; "
        "içeride kıymetli görünen çok şey pazarda değersizdir."
    ),

    "sp_vrio.aciklama_nadir": (
        "VRIO çerçevesinin ikinci sorusunu açıklayan sabit eğitim kartıdır: kaynak "
        "rakiplerin çoğunda YOK mu?\n"
        "\n"
        "Sınır: Kart veri göstermez — işaretlemeler alttaki tabloda yapılır.\n"
        "\n"
        "Yorum: Değerli ama yaygın kaynaklar rekabet paritesi sağlar — zorunludur ama "
        "farklılaştırmaz; nadirlik iddiasını rakip analiziyle sınayın."
    ),

    "sp_vrio.aciklama_taklit_edilemez": (
        "VRIO çerçevesinin üçüncü sorusunu açıklayan sabit eğitim kartıdır: rakiplerin bu "
        "kaynağı edinmesi/kopyalaması maliyetli veya zor mu?\n"
        "\n"
        "Sınır: Kart veri göstermez.\n"
        "\n"
        "Yorum: Taklit zorluğu genelde tarihsel birikim, ilişki ağı veya kültürden gelir — "
        "satın alınabilen hiçbir şey uzun süre taklit edilemez kalmaz."
    ),

    "sp_vrio.aciklama_organize": (
        "VRIO çerçevesinin dördüncü sorusunu açıklayan sabit eğitim kartıdır: kurum bu "
        "kaynağı değere çevirecek süreç, yapı ve sistemlere sahip mi?\n"
        "\n"
        "Sınır: Kart veri göstermez.\n"
        "\n"
        "Yorum: En sık kaybedilen soru budur — değerli, nadir ve taklit edilemez kaynağı "
        "olan ama örgütleyemeyen kurum 'kullanılmayan avantaj' kovasında kalır."
    ),

    "sp_vrio.kaynak_tablosu": (
        "Kurumun kaynak ve yeteneklerini V/R/I/O işaretleriyle listeler; işaretler satırda "
        "canlı değiştirilir ve sonuç etiketi anında güncellenir.\n"
        "\n"
        "Hesap: Etiket, karar ağacından türetilir — Değerli değilse 'rekabetçi dezavantaj'; "
        "nadir değilse 'parite'; taklit edilebilirse 'geçici avantaj'; örgütlenmemişse "
        "'kullanılmayan avantaj'; dördü de evetse 'sürdürülebilir rekabet avantajı'.\n"
        "\n"
        "Sınır: Dört işaret de kullanıcı BEYANIDIR — sistem hesaplamaz. Liste plan yılına "
        "filtrelenmez; tüm yılların kayıtları birlikte görünür.\n"
        "\n"
        "Kaynak: Barney'nin kaynak temelli görüş çerçevesi (VRIO, 1991).\n"
        "\n"
        "Yorum: İşaretlemeyi yönetim ekibiyle tartışarak yapın; tek kişinin iyimserliği "
        "tüm portföyü 'sürdürülebilir avantaj'a boyar ve çerçeve değerini yitirir."
    ),

    "sp_vrio.sonuc_siniflandirmasi": (
        "Beş VRIO sonuç sınıfının renk ve anlamlarını açıklayan sabit lejant kartıdır: "
        "rekabetçi dezavantaj → parite → geçici avantaj → kullanılmayan avantaj → "
        "sürdürülebilir avantaj.\n"
        "\n"
        "Sınır: Kart sayım/dağılım göstermez — yalnızca sınıfların ne anlama geldiğini "
        "anlatır.\n"
        "\n"
        "Yorum: Portföyünüzün ağırlığı hangi sınıfta toplanıyorsa stratejik gündem odur: "
        "dezavantajlar kapatılır, kullanılmayan avantajlar örgütlenir, sürdürülebilir "
        "avantajlar savunulur."
    ),

    # ─────────────────── SP FLOW ───────────────────

    "sp_flow.ana_strateji_sayisi": (
        "Aktif plan yılındaki ana strateji sayısını gösterir.\n"
        "\n"
        "Hesap: Aktif kayıtlar sayılır; dönemsiz (eski) kayıtlar da dahil edilir.\n"
        "\n"
        "Yorum: Sayı akış ekranının kapsam özetidir; detay ve skorlar için interaktif "
        "grafiğe geçin."
    ),

    "sp_flow.alt_strateji_sayisi": (
        "Aktif plan yılındaki alt strateji sayısını gösterir.\n"
        "\n"
        "Hesap: Ana stratejisi bu dönemde olan aktif alt stratejiler sayılır.\n"
        "\n"
        "Yorum: Alt strateji, stratejiyi ölçülebilir parçalara bölen katmandır — ana "
        "strateji başına 2-5 alt strateji sağlıklı bir granülasyondur."
    ),

    "sp_flow.surec_sayisi": (
        "Aktif plan yılındaki süreç sayısını gösterir.\n"
        "\n"
        "Hesap: Aktif süreçler sayılır.\n"
        "\n"
        "Yorum: Süreçler stratejinin operasyona değdiği yerdir; bu sayı sıfırsa akış "
        "zinciri stratejide kopuyor demektir."
    ),

    "sp_flow.vizyon": (
        "Kurumun vizyon metnini akış ekranının tepesinde gösterir.\n"
        "\n"
        "Sınır: Metin kurum profilindeki GENEL vizyondur — plan yılına özgü (dönemsel) "
        "vizyon değil; vizyon boşsa kart hiç görünmez.\n"
        "\n"
        "Yorum: SP ana sayfasındaki dönemsel vizyonla bu metin farklıysa, profil vizyonu "
        "güncellenmemiş olabilir."
    ),

    "sp_flow.interaktif_grafik": (
        "Strateji-süreç-gösterge zincirini çizen interaktif grafik sayfasına geçiş "
        "kartıdır.\n"
        "\n"
        "Sınır: Kartın kendisi grafik ÇİZMEZ — yalnızca yönlendirir; grafik ayrı sayfada "
        "yüklenir.\n"
        "\n"
        "Yorum: Grafik sayfası büyük kurumlarda düğüm sınırıyla çizilir; tam envanter "
        "yerine yapısal bakış beklenmelidir."
    ),

    # ─────────────────── SP BLUE OCEAN ───────────────────

    "sp_blue_ocean.tuval_listesi": (
        "Kayıtlı strateji tuvallerini (canvas) listeler: ad, sektör, faktör sayısı, ERRC "
        "öğe sayısı ve rakipler.\n"
        "\n"
        "Sınır: Liste plan yılına filtrelenmez — tüm dönemlerin tuvalleri birlikte "
        "görünür.\n"
        "\n"
        "Yorum: Tuval sayısı değil derinliği önemlidir — 6-10 iyi seçilmiş rekabet "
        "faktörlü tek tuval, yüzeysel üç tuvalden değerlidir."
    ),

    "sp_blue_ocean.tuval_detay": (
        "Seçili tuvalin başlık, sektör ve açıklamasını gösterir; faktör ve ERRC öğesi ekleme "
        "buradan yapılır.\n"
        "\n"
        "Yorum: Tuvala başlarken sektörün 'herkesçe kabul edilmiş' rekabet faktörlerini "
        "listeleyin — ezber bozan hamle ancak ezberi yazdıktan sonra görünür."
    ),

    "sp_blue_ocean.deger_egrisi": (
        "Rekabet faktörleri üzerinde kurumun ve rakiplerin 0-10 puanlarını çizgi grafik "
        "olarak karşılaştırır (strateji tuvali).\n"
        "\n"
        "Hesap: Grafik girilen ham puanları çizer — normalizasyon veya türetilmiş 'ayrışma "
        "skoru' HESAPLANMAZ.\n"
        "\n"
        "Sınır: Puanlar tamamen kullanıcı beyanıdır; kurum KPI verisinden türetilmez.\n"
        "\n"
        "Yorum: İyi bir mavi okyanus eğrisi rakiplerle paralel gitmez — bazı faktörlerde "
        "bilinçli düşük, birkaç faktörde belirgin yüksek seyreder; her faktörde yüksek "
        "olmak strateji değil maliyettir."
    ),

    "sp_blue_ocean.errc_tablosu": (
        "Dört eylem çerçevesini (Kaldır / Azalt / Yükselt / Yarat) dört kutuda gösterir; "
        "her öğe etki etiketi (yüksek/orta/düşük) taşır.\n"
        "\n"
        "Sınır: Öğeler serbest kayıttır; etki etiketi bir skora çevrilmez ve değer "
        "eğrisiyle otomatik bağ kurulmaz.\n"
        "\n"
        "Yorum: Çerçevenin disiplini 'Kaldır' kutusundadır — hiçbir şey kaldırmayan ERRC, "
        "maliyet yapısını değiştirmeden vaat büyütür; en zor ve en değerli kararlar orada "
        "alınır."
    ),

    # ─────────────────── SP DÖNEMLER ───────────────────

    "sp_donemler.aktif_donem": (
        "Aktif plan döneminin yılını, adını ve oluşturulma tarihini gösterir; yetkili "
        "kullanıcı dönemi buradan kapatabilir (mühürler).\n"
        "\n"
        "Yorum: Dönem kapatma geri alınabilir (mühür açma) ama disiplin gereği kapanmış "
        "dönemde veri değişmemelidir — kapatmayı yıl sonu ritüeli olarak kullanın."
    ),

    "sp_donemler.bos_durum": (
        "Henüz hiç plan dönemi tanımlanmamışken görünen başlangıç kartıdır; ilk dönemi "
        "oluşturmaya yönlendirir.\n"
        "\n"
        "Sınır: Kart yalnızca dönem listesi boşken görünür; dönem açma yetkisi olmayan "
        "kullanıcılar butonu görmez.\n"
        "\n"
        "Yorum: İlk dönemi açmak yıl bazlı planlamanın kapısıdır — dönemsiz strateji "
        "kayıtları karşılaştırma ve devir özelliklerinden yararlanamaz."
    ),

    "sp_donemler.donem_karsilastir": (
        "İki plan dönemini yan yana karşılaştırır: strateji, alt strateji, süreç ve "
        "gösterge yapılarındaki farklar, kimlik (misyon/vizyon/değerler) değişimleri, "
        "girişim ve OKR sayıları.\n"
        "\n"
        "Hesap: Kayıtlar devir zincirindeki kaynak bağıyla eşleştirilir; başlık, kod, "
        "hedef, ağırlık, periyot gibi alanlardaki farklar tespit edilir (ağırlıkta 0,001 "
        "üzeri fark anlamlı sayılır).\n"
        "\n"
        "Sınır: Karşılaştırılan YAPI ve HEDEFLERDİR — gerçekleşen performans (ölçümler) "
        "kıyaslanmaz. En az iki dönem yoksa panel görünmez.\n"
        "\n"
        "Yorum: En değerli çıktı hedef değişimleridir: yıldan yıla sistematik hedef "
        "gevşetme, karşılaştırma ekranında çıplak gözle görünür."
    ),

    "sp_donemler.tum_donemler": (
        "Tüm plan dönemlerini durum rozetleriyle listeler: aktif, mühürlü veya taslak; "
        "dönem seçme ve mühürleme işlemleri buradan yapılır.\n"
        "\n"
        "Yorum: Mühürlü dönemler kurumsal hafızadır — geçmişe dönük düzeltme ihtiyacı "
        "doğarsa mührü açıp kapatmak yerine değişikliği not düşerek yapmak izlenebilirliği "
        "korur."
    ),

    # ─────────────────── SP YENİ YIL SİHİRBAZI ───────────────────

    "sp_sihirbaz_yeni_yil.yil_secimi": (
        "Yeni plan dönemine geçişin ilk adımı: verilerin taşınacağı kaynak yıl ile "
        "oluşturulacak hedef yıl seçilir.\n"
        "\n"
        "Sınır: Sihirbaz yalnızca dönem yönetme yetkisi olan kullanıcılara açıktır.\n"
        "\n"
        "Yorum: Kaynak olarak en güncel ve en düzenli dönemi seçin — taşınan yapı yeni "
        "yılın iskeleti olur; dağınıklık da aynen taşınır."
    ),

    "sp_sihirbaz_yeni_yil.onizleme": (
        "Geçişten önce taşınacak süreç ve gösterge sayısını gösterir.\n"
        "\n"
        "Sınır: Önizleme YALNIZCA süreç ve gösterge sayar — gerçek geçiş bundan fazlasını "
        "kopyalar (stratejiler, alt stratejiler, bağlar, faaliyet şablonları, bireysel "
        "göstergeler, kurum kimliği); bunlar önizlemede listelenmez.\n"
        "\n"
        "Yorum: Sayılar beklediğinizden düşükse kaynak yıl seçimini kontrol edin — yanlış "
        "yıldan devir, yeni yılı eksik iskeletle başlatır."
    ),

    "sp_sihirbaz_yeni_yil.sonuc": (
        "Yeni yıl geçişinin sonucunu gösterir ve dönemler sayfasına yönlendirir.\n"
        "\n"
        "Hesap: Geçiş; stratejileri, alt stratejileri, süreçleri (hiyerarşisiyle), "
        "süreç-strateji bağlarını, göstergeleri (önceki yıl ortalaması hesaplanarak), "
        "faaliyetleri (tarih ve durumları SIFIRLANMIŞ şablon olarak), bireysel göstergeleri "
        "ve kurum kimliğini kopyalar; SWOT/TOWS için BOŞ kayıt açılır. Yeni dönem 'taslak' "
        "durumunda doğar.\n"
        "\n"
        "Sınır: SWOT/TOWS İÇERİĞİ kopyalanmaz; VRIO ve Blue Ocean kayıtları da devire dahil "
        "değildir. Aynı yıl ikinci kez oluşturulamaz.\n"
        "\n"
        "Yorum: Geçiş sonrası ilk iş yeni dönemin hedeflerini gözden geçirmektir — kopyalanan "
        "hedefler geçen yılın hedefleridir, yeni yılın iddiası değil."
    ),

    # ─────────────────── SP ANALİZ ÇERÇEVELERİ ───────────────────

    "sp_swot.sayfa": (
        "Dönem bazlı SWOT analizini dört kutuda tutar: güçlü yönler, zayıf yönler, "
        "fırsatlar, tehditler; maddeler serbestçe eklenir.\n"
        "\n"
        "Sınır: Bu bir SERBEST KAYIT DEFTERİDİR — sistem skorlama veya otomatik analiz "
        "yapmaz; çapraz strateji türetme (TOWS) ayrı ekrandadır. Kayıtlar aktif plan yılına "
        "bağlıdır; yeni yıl devrinde içerik TAŞINMAZ, boş sayfa açılır.\n"
        "\n"
        "Kaynak: 1960'larda Stanford Research Institute'ta SOFT yöntemi olarak geliştirilen "
        "yaklaşımın yaygınlaşmış halidir.\n"
        "\n"
        "Yorum: İyi SWOT az maddeli SWOT'tur — her kutuda 3-5 gerçekten önemli madde, 15 "
        "maddelik listelerden daha çok karar üretir. İç/dış ayrımına dikkat edin: güçlü/zayıf "
        "İÇERİDEN, fırsat/tehdit DIŞARIDAN gelir."
    ),

    "sp_pestel.sayfa": (
        "Dönem bazlı PESTEL analizini altı kutuda tutar: politik, ekonomik, sosyal, "
        "teknolojik, çevresel ve yasal etkenler.\n"
        "\n"
        "Sınır: Serbest kayıt defteridir — skorlama veya otomatik analiz yapılmaz; kayıtlar "
        "plan yılına bağlıdır ve yeni yıl devrinde taşınmaz.\n"
        "\n"
        "Yorum: PESTEL'in değeri düzenli güncellemededir — yılda bir yazılan makro analiz, "
        "yazıldığı hafta eskir; çeyreklik gözden geçirmeye bağlayın ve her maddeyi 'bize "
        "etkisi ne' sorusuyla bitirin."
    ),

    "sp_porter.sayfa": (
        "Porter'ın beş rekabet gücünü dönem bazlı analiz eder: mevcut rekabet, tedarikçi "
        "gücü, alıcı gücü, yeni girenler tehdidi ve ikame tehdidi; her güce 1-5 baskı puanı "
        "ve maddeler girilir.\n"
        "\n"
        "Hesap: Güç başına 1-5 puan kullanıcı tarafından verilir; sistem BİRLEŞİK sektör "
        "çekiciliği skoru hesaplamaz.\n"
        "\n"
        "Sınır: Serbest kayıt + manuel puanlama; kurum verisinden türetilmez.\n"
        "\n"
        "Kaynak: Porter'ın beş kuvvet çerçevesi (1979).\n"
        "\n"
        "Yorum: Beş gücü ayrı ayrı puanlamak yetmez — asıl soru 'hangi gücü lehimize "
        "değiştirebiliriz'dir; en yüksek baskı puanlı güç, strateji gündeminin doğal "
        "maddesidir."
    ),

    "sp_xmatrix.sayfa": (
        "Hoshin Kanri X-Matrisini çizer: kuzeyde stratejiler, doğuda alt stratejiler, "
        "güneyde girişimler, batıda göstergeler; eksenler arası ilişkiler dolu hücrelerle "
        "gösterilir.\n"
        "\n"
        "Hesap: İlişkiler ELLE İŞARETLENMEZ — mevcut bağ tablolarından otomatik türetilir "
        "(strateji-alt strateji ebeveynliği, girişim-alt strateji bağı, strateji→süreç→"
        "gösterge zinciri). İlişki var/yok bilgisidir, ağırlık değildir.\n"
        "\n"
        "Sınır: Girişim-gösterge ilişkisi YAKLAŞIKTIR — 'aynı alt stratejinin süreçlerindeki "
        "göstergeler' varsayımıyla kurulur, gerçek bir girişim-gösterge bağı tablosu yoktur. "
        "Batı ekseni en fazla 60 göstergeyle sınırlıdır (önemli işaretliler öncelikli).\n"
        "\n"
        "Kaynak: Toyota kökenli Hoshin Kanri (politika yayılımı) yaklaşımının X-Matris "
        "gösterimi.\n"
        "\n"
        "Yorum: Matristeki boş satır/sütunlar hizalama borcudur: ilişkisiz girişim kaynak "
        "israfı, ilişkisiz gösterge sahipsiz ölçümdür."
    ),

    # ─────────────────── SP AI AYARLARI ───────────────────

    "sp_ai_settings.kaynak_modu": (
        "Yapay zekâ özelliklerinin hangi kaynakla çalışacağını seçtirir: Kokpitim sistem "
        "yapay zekâsı (ücretsiz, kotalı) veya kurumun kendi API anahtarı (BYOK).\n"
        "\n"
        "Sınır: Sistem modu kotalıdır (varsayılan günlük 50 / aylık 500 çağrı); kota "
        "dolduğunda AI kartları kural motoruna düşer. Kendi anahtar modunda maliyet "
        "sağlayıcı hesabınıza yansır.\n"
        "\n"
        "Yorum: Yoğun AI kullanımı planlıyorsanız kendi anahtarınıza geçin — sistem kotası "
        "deneme ve hafif kullanım için tasarlanmıştır."
    ),

    "sp_ai_settings.api_anahtari_bilgileri": (
        "Kendi API anahtarı modunun ayarlarını tutar: sağlayıcı (Gemini, OpenAI, Anthropic, "
        "Groq, OpenRouter), model adı, şifreli saklanan anahtar ve kişisel veri maskeleme "
        "onayı.\n"
        "\n"
        "Hesap: Anahtar veritabanında şifreli (Fernet) saklanır ve ekranda maskeli gösterilir; "
        "'Test Et' düğmesi gerçek bir deneme çağrısı yapar.\n"
        "\n"
        "Sınır: Model adı serbest metindir — sağlayıcının desteklemediği model adı girildiğinde "
        "hata ancak test/kullanım anında görünür.\n"
        "\n"
        "Yorum: Anahtarı kaydettikten sonra mutlaka test edin; KVKK maskeleme seçeneği açıkken "
        "istemlere kişisel veri karışması engellenir."
    ),

    # ─────────────────── SP BSC ───────────────────

    "sp_bsc.sayfa": (
        "Performans göstergelerini dört BSC perspektifine (finansal, müşteri, iç süreçler, "
        "öğrenme ve gelişim) dağıtır; her perspektifin ortalama performansı ve gösterge sayısı "
        "gösterilir.\n"
        "\n"
        "Hesap: Perspektif skoru = atanmış göstergelerin performans yüzdelerinin ortalaması. "
        "Gösterge performansı yön dikkate alınarak hesaplanır: artan hedefte gerçekleşme/hedef, "
        "azalan hedefte hedef/gerçekleşme (100'de kırpılır).\n"
        "\n"
        "Sınır: Atamalar plan yılına özgüdür — yeni dönemde atama tablosu boş başlar. "
        "Ölçülemeyen (hedefsiz veya sayısal olmayan) göstergeler ortalamaya girmez.\n"
        "\n"
        "Kaynak: Kaplan ve Norton'un Dengeli Karne (Balanced Scorecard) çerçevesi (1992) — "
        "dört perspektif.\n"
        "\n"
        "Yorum: Perspektifler arası denge asıl mesajdır: finansal perspektif dolu ama öğrenme "
        "perspektifi boşsa karne 'dengeli' değildir — BSC'nin varlık nedeni tam da bu "
        "dengesizliği göstermektir."
    ),

    "sp_bsc.atanmamis_gostergeler": (
        "Henüz hiçbir BSC perspektifine atanmamış göstergeleri listeler; 'otomatik "
        "sınıflandır' düğmesiyle toplu öneri alınabilir.\n"
        "\n"
        "Hesap: Otomatik sınıflandırma anahtar kelime eşlemesiyle çalışır (tam öbek +3, tam "
        "kelime +2, kısmi +1 puan); güven değeri %30'un üzerindeki öneriler uygulanır.\n"
        "\n"
        "Sınır: Otomatik sınıflandırma dil temelli bir TAHMİNDİR — gösterge adı yanıltıcıysa "
        "yanlış perspektife düşebilir; sonuçlar elle düzeltilebilir.\n"
        "\n"
        "Yorum: Otomatik atamayı başlangıç olarak kullanın, yönetim gözüyle doğrulayın — bir "
        "göstergenin perspektifi bazen kurumun stratejik niyetine göre değişir (örn. eğitim "
        "saati: öğrenme mi, iç süreç mi?)."
    ),

    # ─────────────────── SP PLACEHOLDER SAYFALAR ───────────────────

    "sp_degerler.sayfa": (
        "Değerler ve etik kurallar için ayrılmış sayfa — henüz yapım aşamasındadır.\n"
        "\n"
        "Sınır: Bu sayfada işlevsel içerik YOKTUR; değerler ve etik kurallar şu an SP ana "
        "sayfasındaki kimlik kartlarından yönetilir.\n"
        "\n"
        "Yorum: Değer/etik metinlerini görüntülemek ve düzenlemek için SP ana sayfasını "
        "kullanın."
    ),

    "sp_misyon.misyon": (
        "Misyon için ayrılmış sayfa — henüz yapım aşamasındadır.\n"
        "\n"
        "Sınır: Bu sayfada işlevsel içerik YOKTUR; misyon metni SP ana sayfasındaki kimlik "
        "kartından yönetilir.\n"
        "\n"
        "Yorum: Misyonu görüntülemek ve düzenlemek için SP ana sayfasını kullanın."
    ),

    "sp_vizyon.vizyon": (
        "Vizyon için ayrılmış sayfa — henüz yapım aşamasındadır.\n"
        "\n"
        "Sınır: Bu sayfada işlevsel içerik YOKTUR; vizyon metni ve K-Vektör vizyon puanı SP "
        "ana sayfasında gösterilir.\n"
        "\n"
        "Yorum: Vizyonu görüntülemek ve düzenlemek için SP ana sayfasını kullanın."
    ),

    # ─────────────────── SP DİNAMİK AKIŞ ───────────────────

    "sp_dynamic_flow.renk_lejandi": (
        "Strateji grafiğindeki düğüm renklerinin anlamını gösteren sabit lejanttır: vizyon, "
        "strateji, alt strateji, süreç ve gösterge her biri ayrı renkle çizilir.\n"
        "\n"
        "Sınır: Renkler düğümün TÜRÜNÜ kodlar — performansını değil; kırmızı bir düğüm 'kötü' "
        "anlamına gelmez.\n"
        "\n"
        "Yorum: Performans okuması için düğüme tıklayıp skor detayına inin."
    ),

    "sp_dynamic_flow.strateji_grafigi": (
        "Vizyon → strateji → alt strateji → süreç → gösterge zincirini hiyerarşik düğüm-bağ "
        "grafiği olarak çizer.\n"
        "\n"
        "Hesap: Düğümler aktif kayıtlardan, bağlar mevcut ilişki tablolarından üretilir; "
        "vizyon skoru skor motorundan eklenir.\n"
        "\n"
        "Sınır: Grafik varsayılan 500 düğümle sınırlıdır (50-2000 aralığında ayarlanabilir) — "
        "büyük kurumlarda bazı süreçler kırpılır, grafik tam envanter değildir.\n"
        "\n"
        "Yorum: Grafiğin değeri kopuk zincirleri göstermesidir — vizyona ulaşmayan dallar "
        "stratejik hizalama eksiğinin haritasıdır."
    ),

    # ─────────────────── SP GİRİŞİMLER ───────────────────

    "sp_initiatives.girisim_listesi": (
        "Çok yıllık stratejik girişimleri kartlar halinde listeler: öncelik, durum, yıl "
        "aralığı, kilometre taşı sayısı, bütçe, ilerleme yüzdesi ve bağlı projeler.\n"
        "\n"
        "Eşik: Bağlı proje sağlık rengi — 75+ yeşil, 50-74 sarı, altı kırmızı.\n"
        "\n"
        "Sınır: İlerleme yüzdesi kayıtta saklanan ELLE girilmiş değerdir — kilometre taşı "
        "veya proje tamamlanmasından otomatik hesaplanmaz.\n"
        "\n"
        "Yorum: Projesi ve kilometre taşı olmayan girişimler 'niyet' aşamasındadır; ilerleme "
        "beyanını bağlı projelerin sağlığıyla çapraz kontrol edin."
    ),

    # ─────────────────── SP LLM KULLANIM ───────────────────

    "sp_llm_usage.kota_ozeti": (
        "Yapay zekâ kullanım kotasının durumunu dört kartta gösterir: bugünkü çağrı, aylık "
        "çağrı, aylık maliyet ve hesap durumu.\n"
        "\n"
        "Hesap: Yüzdeler kullanılan/limit oranıdır; yalnızca başarılı çağrılar sayılır. "
        "Limitler kurum özelinde tanımlanabilir; yoksa varsayılanlar geçerlidir (günlük 50, "
        "aylık 500 çağrı, aylık 2 USD).\n"
        "\n"
        "Eşik: %80 aşımında sistem günlüğüne uyarı düşülür.\n"
        "\n"
        "Sınır: Kurum kotasının üstünde ayrıca sistem geneli günlük tavan vardır ve bu kartta "
        "gösterilmez — kurum kotanız dolu görünmese de sistem tavanı aşılmışsa çağrılar "
        "reddedilebilir.\n"
        "\n"
        "Yorum: Kota sık doluyorsa ya AI kullanımını önceliklendirin ya da kendi API "
        "anahtarınıza geçin."
    ),

    "sp_llm_usage.son_cagrilar": (
        "Kurumun son yapay zekâ çağrılarını listeler: tarih, hangi özellik (uç), model, "
        "token sayısı ve sonuç durumu.\n"
        "\n"
        "Sınır: Liste son 50 kayıtla sınırlıdır.\n"
        "\n"
        "Yorum: Hangi özelliğin kotayı tükettiğini bu listeden görürsünüz; hata durumlu "
        "çağrıların birikmesi sağlayıcı/anahtar sorununun işaretidir."
    ),

    # ─────────────────── SP OKR ───────────────────

    "sp_okr.ozet": (
        "OKR özetini üç sayıyla verir: hedef (Objective) sayısı, anahtar sonuç (KR) sayısı "
        "ve ortalama ilerleme yüzdesi.\n"
        "\n"
        "Hesap: KR ilerlemesi = (güncel − başlangıç) / (hedef − başlangıç), 0-1 aralığına "
        "kırpılıp yüzdeye çevrilir; hedef ilerlemesi KR'lerin, genel ortalama hedeflerin "
        "ortalamasıdır.\n"
        "\n"
        "Sınır: Başlangıç/hedef değeri girilmemiş KR'ler hesaba katılamaz; ortalama yalnız "
        "ölçülebilen hedefler üzerinden alınır ve ağırlıksızdır.\n"
        "\n"
        "Yorum: Ortalama ilerlemeyi çeyrek takvimine oranlayın — çeyreğin %75'i geçmişken "
        "%40 ilerleme, hedeflerin geride kaldığının açık sinyalidir."
    ),

    "sp_okr.hedef_karti": (
        "Tek bir OKR hedefini detaylarıyla gösterir: başlık, dönem (çeyrek/yıllık), sahip, "
        "bağlı strateji ve anahtar sonuç listesi (başlangıç → hedef, güncel değer, ilerleme "
        "barı).\n"
        "\n"
        "Eşik: KR ilerlemesi %70+ yeşil, %40-70 sarı, altı kırmızı.\n"
        "\n"
        "Sınır: İlerleme, KR'nin güncel değerinin elle güncellenmesine bağlıdır — "
        "güncellenmeyen KR gerçekte ilerlemiş olsa da %0 görünür.\n"
        "\n"
        "Yorum: İyi bir KR çıktı değil sonuç ölçer ('eğitim verildi' değil 'hata oranı "
        "düştü'); kırmızı KR'lerde önce değerin güncel olup olmadığını sorun."
    ),

    # ─────────────────── SP YENİDEN PLANLAMA TETİKLEYİCİLERİ ───────────────────

    "sp_replan_triggers.aktif_tetikleyiciler": (
        "Tanımlı yeniden planlama tetikleyicilerini listeler: ad, tip, eşik koşulu, ardışık "
        "dönem sayısı, kaç kez ateşlendiği ve son ateşleme zamanı.\n"
        "\n"
        "Hesap: İki tip fiilen ÇALIŞIR — 'gösterge hedef altında' (seçilen göstergenin son N "
        "döneminin TÜMÜ hedefin altındaysa ateşler) ve 'geciken faaliyet oranı' (gecikme "
        "yüzdesi, tanımlı operatör ve eşikle karşılaştırılır).\n"
        "\n"
        "Sınır: Arayüzde seçilebilen 'risk skoru' ve 'yüksek anomali' tipleri henüz "
        "değerlendirilmez — bu tiplerle kurulan tetikleyiciler HİÇ ateşlenmez.\n"
        "\n"
        "Yorum: Tetikleyiciyi alarm değil sigorta olarak kurun: az sayıda, gerçekten "
        "plan revizyonu gerektirecek koşullara bağlayın; her sapmaya tetikleyici bağlamak "
        "alarm yorgunluğu üretir."
    ),

    "sp_replan_triggers.son_ateslemeler": (
        "Tetikleyicilerin ateşlenme geçmişini listeler: zaman, tetikleyici, alınan aksiyon "
        "türü ve olay detayı.\n"
        "\n"
        "Sınır: Son 100 olay gösterilir. 'Aksiyon' alanı tetikleyiciye tanımlı NİYETİ "
        "kaydeder (bildir / pivot öner / değerlendirme aç) — aksiyonun fiilen tamamlandığını "
        "garanti etmez.\n"
        "\n"
        "Yorum: Aynı tetikleyicinin tekrar tekrar ateşlenmesi, koşulun yapısal hale "
        "geldiğinin kanıtıdır — artık bildirim değil plan revizyonu gerekir."
    ),

    # ─────────────────── SP SENARYOLAR ───────────────────

    "sp_scenarios.senaryo_olustur": (
        "Mevcut bir plan yılından senaryo kopyası oluşturur: kaynak yıl ve senaryo etiketi "
        "(temel / iyimser / kötümser) seçilir.\n"
        "\n"
        "Hesap: Oluşturma, kaynak yılın tam kopyasını alır — stratejiler, süreçler ve "
        "göstergeler senaryo dalına klonlanır.\n"
        "\n"
        "Sınır: Aynı kaynak ve etiketle ikinci senaryo oluşturulamaz.\n"
        "\n"
        "Yorum: Senaryonun değeri kopyadan sonra başlar — iyimser/kötümser dalda hedefleri "
        "gerçekten farklılaştırın; değiştirilmemiş senaryo kıyasta ana planla aynı skoru "
        "verir."
    ),

    "sp_scenarios.senaryo_listesi": (
        "Plan yıllarını ve her birinin altındaki senaryo dallarını ağaç olarak listeler; "
        "senaryolar etiket rozetiyle görünür ve buradan düzenlemeye geçilir.\n"
        "\n"
        "Sınır: Liste yapısaldır — skor veya performans göstermez; kıyas ayrı ekrandadır.\n"
        "\n"
        "Yorum: Senaryoları dönem kapanışlarında temizleyin — güncelliğini yitirmiş senaryo "
        "dalları kıyas ekranını kalabalıklaştırır."
    ),

    "sp_scenarios_kiyas.secim_listesi": (
        "Karşılaştırılacak plan yılları ve senaryoları seçtirir (2 ile 6 arası).\n"
        "\n"
        "Sınır: En az 2 seçim yapılmadan karşılaştırma çalışmaz.\n"
        "\n"
        "Yorum: En bilgilendirici kıyas, ana plan ile onun iyimser/kötümser dallarını yan "
        "yana koymaktır — birbirinden bağımsız yılları kıyaslamak dönem farklarını senaryo "
        "farkı gibi gösterebilir."
    ),

    "sp_scenarios_kiyas.vizyon_skoru_karsilastirma": (
        "Seçilen plan/senaryoların vizyon skorlarını yatay barlarla karşılaştırır; kaydırıcı "
        "ile ilk iki seçim arasında 'harmanlanmış' skor gösterilir.\n"
        "\n"
        "Hesap: Bar skorları GERÇEK skor motorundan gelir (her senaryo için salt okunur "
        "yeniden hesap; K-Vektör açıksa o motorla). Kaydırıcıdaki harman ise iki gerçek "
        "skorun DOĞRUSAL karışımıdır.\n"
        "\n"
        "Sınır: Harman değeri motor hesabı DEĞİLDİR — 'iki senaryonun %60-%40 karışımı' "
        "gerçek bir plan çalıştırması değil, aritmetik ara değerdir; karar dayanağı olarak "
        "bar skorlarını kullanın.\n"
        "\n"
        "Yorum: Senaryolar arası skor farkı küçükse senaryolar yeterince "
        "farklılaştırılmamış olabilir — önce hedef değişikliklerini kontrol edin."
    ),

    # ─────────────────── SP ŞABLONLAR ───────────────────

    "sp_templates.sablon_karti": (
        "Hazır stratejik plan şablonunu tanıtır: sektör (kamu/özel/STK), plan süresi, "
        "içerdiği strateji ve gösterge sayısı; 'uygula' ile kuruma kopyalanır.\n"
        "\n"
        "Hesap: Sayılar şablon kataloğundan gelir; uygulamada aynı kodlu mevcut kayıtlar "
        "atlanır (üzerine yazılmaz).\n"
        "\n"
        "Sınır: Şablonlar kod içinde tanımlı sabit katalogdur — kurum verinizden "
        "beslenmez.\n"
        "\n"
        "Yorum: Şablon boş sayfa korkusunu aşmak içindir; uyguladıktan sonra her strateji ve "
        "göstergeyi kurumunuza uyarlamadan plana 'bitti' muamelesi yapmayın."
    ),

    # ─────────────────── SP TV / SAVAŞ ODASI ───────────────────

    "sp_tv.sayfa": (
        "Tam ekran 'Savaş Odası' modu: yönetici metriklerini (hedef üstü oranı, veri "
        "kapsamı, geciken faaliyet, açık risk, yüksek anomali) ve strateji/süreç/proje "
        "sıralamalarını sahne sahne döndüren canlı TV görünümü. Kritik risk veya yüksek "
        "anomali varken ekran alarm moduna geçer.\n"
        "\n"
        "Eşik: Metrik renk bandı — 80+ yeşil, 50-79 sarı, 50 altı kırmızı.\n"
        "\n"
        "Sınır: SALT GÖSTERİMDİR — bu ekrandan hiçbir veri girilmez/değiştirilmez; sahne "
        "ayarları tarayıcıda saklanır (başka bilgisayarda ayarlar sıfırdan yapılır).\n"
        "\n"
        "Yorum: Ofis ekranına asılan bu mod, ölçüm kültürünün görünürlük ayağıdır — ancak "
        "alarm modunun etkisi, alarma gerçekten müdahale edildiği sürece korunur."
    ),
}
