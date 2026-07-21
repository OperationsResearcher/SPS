# -*- coding: utf-8 -*-
"""K-Radar KPR (Proje Radar) + Cross + Risk kart açıklamaları.

Yazım sözleşmesi için bkz. card_descriptions_k_radar.py başlığı.

ÖNEMLİ tespitler (koddan doğrulanmış, "Sınır:" bölümlerine yansıtıldı):
  - kpr_gantt "on_time_ratio" aslında TAMAMLANMA oranıdır; bitiş tarihi ile
    termin karşılaştırması yapılmaz.
  - kpr_cpm gerçek kritik yol hesabı yapmaz; süre/float yoktur, yalnızca
    "öncülü olmayan görevler" listelenir.
  - kpr_risk kartı proje kapsamı UYGULAMAZ (tablo project_id taşımıyor) —
    yetkisi kısıtlı kullanıcı da kurum geneli riski görür.
  - Risk eşiği iki yerde farklı: KPR özetinde rpn>=15, risk listesinde >=16.
  - cross risk ısı haritası gerçek risk kaydı OKUMAZ; radar skorlarından
    sabit tabloyla olasılık/etki üretir.
  - kaynak_kapasite "resource_load" yüzde değildir; sınırsız artabilen indeks.
"""

DESCRIPTIONS: dict[str, str] = {

    # ─────────────────────────── KPR — PROJE RADARI ───────────────────────────

    "k_radar_kpr.proje_radari": (
        "Proje portföyünüzün sağlık skorunu, bandını ve kritik proje sayısını özetler.\n"
        "\n"
        "Hesap: Her projenin sağlık skorundan, geciken görev sayısına bağlı bir ceza düşülür "
        "(görev başına 5 puan, en fazla 35 puan). Kart skoru bu düzeltilmiş proje skorlarının "
        "ortalamasıdır.\n"
        "\n"
        "Eşik: Düzeltilmiş skoru 60'ın altında kalan proje kritik sayılır. İki ve daha fazla "
        "kritik proje varsa genel bant kırmızıya döner.\n"
        "\n"
        "Yorum: Gecikme cezası tavanlıdır — 7 geciken görevle 30 geciken görev aynı cezayı alır. "
        "Bu nedenle çok sayıda gecikmesi olan projelerde skor, sorunun gerçek boyutunu tam "
        "yansıtmayabilir; görev listesine ayrıca bakın.\n"
        "\n"
        "Sınır: Arşivlenmiş projeler hesaba katılmaz. Hiç proje yoksa skor 0 ve bant kırmızı olur."
    ),

    "k_radar_kpr_evm.ozet": (
        "EVM (Kazanılmış Değer Yönetimi), projenin maliyet ve zaman performansını tek çerçevede "
        "ölçer. İki temel gösterge: CPI (maliyet) ve SPI (zaman).\n"
        "\n"
        "Hesap: CPI = Kazanılmış Değer / Fiili Maliyet. SPI = Kazanılmış Değer / Planlanan Değer. "
        "Kartta gösterilen değerler, kaydedilmiş tüm anlık görüntülerin ortalamasıdır.\n"
        "\n"
        "Eşik: 1,0 referans noktasıdır — üzeri lehte, altı aleyhtedir. Uygulamada 0,90 altı "
        "kritik kabul edilir (bu eşik sektör teamülüdür, PMBOK'ta yazılı bir norm değildir).\n"
        "\n"
        "Sınır: Değer SON anlık görüntü değil, TÜM geçmişin ortalamasıdır — yakın dönemdeki "
        "bozulma ortalama içinde sönümlenebilir. Ayrıca veri yoksa değer 0,0 gösterilir; "
        "EVM'de 0,0 'çok kötü' demektir ve 'veri yok' ile karışır.\n"
        "\n"
        "Yorum: SPI'nin bilinen bir sınırı vardır: proje tamamlanmaya yaklaştıkça kazanılmış "
        "değer zorunlu olarak planlanan değere eşitlenir ve SPI, proje gecikmeli bitse bile "
        "1,0'a yakınsar. Geç aşamalarda tek başına güvenilmez.\n"
        "\n"
        "Kaynak: PMI / PMBOK Kılavuzu."
    ),

    "k_radar_kpr_cpm.cpm_analizi": (
        "Kritik Yol Yöntemi (CPM), projedeki bağımlı görevler arasında en uzun süreli zinciri "
        "bulur. Bu zincirdeki her gecikme projenin bitişini birebir öteler.\n"
        "\n"
        "Hesap: Görev bağımlılıklarından öncül haritası kurulur ve ÖNCÜLÜ OLMAYAN görevler "
        "(zincir başlangıçları) ardıl sayısına göre sıralanır.\n"
        "\n"
        "Sınır: Bu GERÇEK BİR KRİTİK YOL HESABI DEĞİLDİR. Görev süreleri, erken/geç başlangıç "
        "ve bolluk (float) hesaplanmaz. Kart yalnızca zincirlerin nereden başladığını ve hangi "
        "başlangıcın çok sayıda işi tetiklediğini gösterir.\n"
        "\n"
        "Yorum: Yine de pratik değeri vardır: çok ardılı olan bir başlangıç görevi gecikirse "
        "etkisi geniş bir alana yayılır. Gerçek kritik yol için görev sürelerinin girilmesi "
        "gerekir.\n"
        "\n"
        "Kaynak: James E. Kelley Jr. & Morgan R. Walker, 1959."
    ),

    "k_radar_kpr_gantt.gantt_ozeti": (
        "Zaman çizelgesine bağlanmış görev sayısını ve tamamlanma oranını gösterir.\n"
        "\n"
        "Hesap: Başlangıç veya bitiş tarihi girilmiş görevler sayılır; oran, bunlar içinde "
        "tamamlanmış olanların payıdır.\n"
        "\n"
        "Sınır: Bu oran 'ZAMANINDA tamamlanma' DEĞİL, yalnızca 'tamamlanma' oranıdır. Görevin "
        "fiilen ne zaman bittiği ile termin tarihi karşılaştırılmaz — geç biten görev de "
        "tamamlanmış sayılır ve oranı yükseltir.\n"
        "\n"
        "Yorum: Gerçek zamanındalık için 'Geciken Görevler' sayısına bakın. Tarihi hiç "
        "girilmemiş görevler bu karta dahil olmaz; oran yüksekken tarihsiz görev yığını "
        "olabilir."
    ),

    "k_radar_kpr_kaynak_kapasite.ozet": (
        "Proje portföyündeki iş yükünü ve gecikme baskısını gösterir.\n"
        "\n"
        "Hesap: Aktif görev, tamamlanmamış görevlerin sayısıdır. Kaynak yükü, aktif görev "
        "sayısının proje sayısına oranının 10 katıdır.\n"
        "\n"
        "Sınır: Kaynak yükü YÜZDE DEĞİLDİR — 100'ü aşabilen bir yoğunluk indeksidir (10 projede "
        "100 aktif görev 100 değerini verir). Ayrıca kişi bazlı kapasite verisi kullanılmaz; "
        "gerçek insan kapasitesi veya iş yükü dağılımı ölçülmez.\n"
        "\n"
        "Yorum: Bu gösterge kişilerin ne kadar dolu olduğunu değil, proje başına ne kadar açık "
        "iş biriktiğini anlatır. Kişi bazlı yük için Sorumlu Analizi raporunu kullanın."
    ),

    "k_radar_kpr_risk.risk_ozeti": (
        "Açık risklerin sayısını, ortalama RPN değerini ve yüksek riskli kayıt sayısını "
        "özetler.\n"
        "\n"
        "Hesap: RPN (Risk Öncelik Sayısı) = Olasılık × Etki. Kapatılmamış (açık) riskler "
        "hesaba girer.\n"
        "\n"
        "Eşik: Bu kartta RPN 15 ve üzeri 'yüksek risk' sayılır. Not: Risk listesi ekranında "
        "farklı bir bantlama kullanılır (16 ve üzeri kritik, 10-16 yüksek). İki ekranda aynı "
        "risk farklı sınıflanabilir.\n"
        "\n"
        "Sınır: Bu kart PROJE KAPSAMI UYGULAMAZ. Risk kayıtları projeye bağlanmadığı için, "
        "yalnızca belirli projelere yetkili bir kullanıcı da burada kurum genelindeki riskleri "
        "görür.\n"
        "\n"
        "Yorum: Ortalama RPN, az sayıda çok yüksek riskin varlığını gizleyebilir — 'Yüksek Risk' "
        "sayısına ayrıca bakın."
    ),

    # ─────────────────────────── CROSS / KESİŞİM KARTLARI ───────────────────────────

    "k_radar_cross.risk_isi_haritasi": (
        "Radar bileşenlerinin (kurumsal strateji, süreç, proje, bireysel) durumunu olasılık-etki "
        "düzleminde konumlandırır.\n"
        "\n"
        "Sınır: Bu harita GERÇEK RİSK KAYITLARINIZI OKUMAZ. Her bileşenin skoruna göre sabit bir "
        "eşleme tablosundan olasılık ve etki değeri atanır (örneğin skoru 80 üzeri olan bileşen "
        "düşük-düşük, 60 altı yüksek-yüksek konumlanır). Yani kurumsal risk kaydınız olmasa da "
        "harita dolu görünür.\n"
        "\n"
        "Yorum: Bu kartı 'radar skorlarının risk diliyle ifadesi' olarak okuyun. Gerçek 5×5 risk "
        "matrisi için Risk Yönetimi sayfasındaki risk matrisi kartını kullanın — o, girilmiş risk "
        "kayıtlarını sayar."
    ),

    "k_radar_cross_rekabet.rekabet_ozeti": (
        "Rakip analizi kayıtlarının sayısını ve ortalama rekabet açığını gösterir.\n"
        "\n"
        "Hesap: Rekabet açığı, rakibin skoru ile kendi skorunuz arasındaki farkın ortalamasıdır. "
        "Pozitif değer rakibin önde olduğunu gösterir.\n"
        "\n"
        "Sınır: Kayıt yoksa değer 0,0 görünür — bu 'rakiple başabaşsınız' değil, 'karşılaştırma "
        "yapılmamış' anlamına gelir.\n"
        "\n"
        "Yorum: Rekabet açığı büyükse önce ölçüm tanımlarının aynı olup olmadığı sorgulanmalıdır; "
        "fark gerçekse rakibin uygulamasının kuruma transfer edilebilirliği araştırılır."
    ),

    "k_radar_cross_a3.a3_ozeti": (
        "A3, bir problemi tanımlamadan kalıcı çözüme kadar tek sayfada anlatan yapılandırılmış "
        "problem çözme yöntemidir. Adını sığdığı kâğıt boyutundan alır.\n"
        "\n"
        "Hesap: Kök neden kapsamı, kök neden analizi doldurulmuş raporların toplam rapora "
        "oranıdır.\n"
        "\n"
        "Yorum: Sayfa kısıtı bilinçlidir — bir problem tek sayfada anlatılamıyorsa henüz yeterince "
        "anlaşılmamıştır. A3 bir rapor formatından çok bir DÜŞÜNME DİSİPLİNİDİR. Kök neden kapsamı "
        "düşükse raporlar belirti tarif ediyor ama nedene inmiyor demektir.\n"
        "\n"
        "Tipik bölümler: arka plan, mevcut durum, hedef, kök neden analizi, karşı önlemler, etki "
        "doğrulama, takip.\n"
        "\n"
        "Kaynak: Toyota; PDCA döngüsü ile problem çözme pratiğinin birleşimi (1960'lar)."
    ),

    "k_radar_cross_anket.anket_ozeti": (
        "Paydaş anketlerinin sayısını ve ortalama memnuniyet skorunu gösterir.\n"
        "\n"
        "Hesap: Skoru girilmiş anketlerin ortalamasıdır; skorsuz kayıtlar ortalamaya katılmaz.\n"
        "\n"
        "Sınır: Anket yoksa değer 0,0 görünür — düşük memnuniyet ile ölçüm yokluğu aynı görünür.\n"
        "\n"
        "Yorum: Anket, paydaş algısını ölçen tek doğrudan kaynaktır. Süreç göstergeleri 'ne "
        "yaptığınızı', anket 'bunun nasıl karşılandığını' söyler; ikisi ayrışıyorsa iç ölçütleriniz "
        "dış beklentiyle hizalı değildir."
    ),

    "k_radar_cross_paydas.paydas_listesi": (
        "Paydaşları ad, rol, etki ve ilgi düzeyleriyle listeler.\n"
        "\n"
        "Tanım: Paydaş, kurumun amaçlarına ulaşmasını etkileyebilen ya da bundan etkilenen birey "
        "veya gruptur.\n"
        "\n"
        "Yorum — Güç/İlgi matrisi ile yönetim stratejisi:\n"
        "- Yüksek güç + yüksek ilgi: yakın yönetilecek kilit paydaş\n"
        "- Yüksek güç + düşük ilgi: memnun tutulacak\n"
        "- Düşük güç + yüksek ilgi: bilgilendirilecek\n"
        "- Düşük güç + düşük ilgi: izlenecek\n"
        "\n"
        "Kaynak: R. Edward Freeman, Strategic Management: A Stakeholder Approach, 1984. "
        "(Güç/İlgi matrisi Freeman'a ait değildir; Mendelow'un 1981 çalışmasına dayanır, bugünkü "
        "biçimini Johnson & Scholes 1993 ile almıştır.)"
    ),

    "k_radar_kp_deger_zinciri.faaliyetler": (
        "Porter değer zincirinin birincil ve destek faaliyetlerini listeler ve yönetmenizi sağlar.\n"
        "\n"
        "Birincil faaliyetler ürün/hizmeti doğrudan üretip müşteriye ulaştırır; destek "
        "faaliyetler bunları mümkün kılar (altyapı, insan kaynakları, teknoloji, tedarik).\n"
        "\n"
        "İsraf (muda) türleri: fazla üretim, bekleme, taşıma, fazla işleme, stok, hareket, hata.\n"
        "\n"
        "Yorum: Her faaliyeti bir sürece bağlamak, değer zinciri analizini performans verisiyle "
        "birleştirir — bağlanmamış faaliyetler özet kartındaki muda ve akış hesaplarına katkı "
        "verse de süreç bazlı analize giremez.\n"
        "\n"
        "Kaynak: Michael E. Porter, Competitive Advantage, 1985 (değer zinciri); israf "
        "sınıflandırması Taiichi Ohno, 1978."
    ),

    # ─────────────────────────── RİSK YÖNETİMİ ───────────────────────────

    "k_radar_risk_management.risk_matrisi": (
        "Riskleri olasılık ve etki eksenlerinde 5×5 ısı haritası olarak gösterir. Cross "
        "sayfasındaki türetilmiş haritadan farklı olarak bu kart GERÇEK risk kayıtlarınızı sayar.\n"
        "\n"
        "Hesap: Her riskin olasılık ve etki değeri 1-5 aralığına yerleştirilir; hücrelerdeki "
        "kayıt sayısı renk yoğunluğuyla gösterilir.\n"
        "\n"
        "Yorum: Matrisin sağ üst köşesi (yüksek olasılık + yüksek etki) önce ele alınacak "
        "bölgedir. Sol alt köşe izlenir. Kayıtların ortada kümelenmesi genelde değerlendirmenin "
        "ihtiyatlı yapıldığına işaret eder — herkes 3 verdiğinde matris ayrım gücünü kaybeder."
    ),

    "k_radar_risk_management.risk_listesi": (
        "Riskleri RPN ve önem seviyesiyle birlikte, şiddet ve duruma göre filtrelenebilir biçimde "
        "listeler.\n"
        "\n"
        "Hesap: RPN (Risk Öncelik Sayısı) = Olasılık × Etki.\n"
        "\n"
        "Eşik: Bu listede RPN 16 ve üzeri kritik, 10-16 arası yüksek, 5-10 arası orta, altı düşük "
        "sayılır. Not: Proje radarındaki risk özeti kartı farklı bir eşik kullanır (15 ve üzeri "
        "yüksek) — aynı risk iki ekranda farklı sınıflanabilir.\n"
        "\n"
        "Yorum: RPN sıralaması müdahale sırasını belirler ancak tek ölçüt değildir; düşük RPN'li "
        "ama tek seferde kurumu durduracak bir risk, yüksek RPN'li kronik bir riskten önce "
        "gelebilir. Sayı yargının yerine geçmez."
    ),
}
