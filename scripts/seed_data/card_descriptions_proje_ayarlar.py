# -*- coding: utf-8 -*-
"""Proje + Ayarlar + Profil + Kurum Ayarları + tekil sayfa kart açıklamaları
— 60 kart (dilim 4, katalog tamamlanışı).

Yazım sözleşmesi için bkz. card_descriptions_k_radar.py başlığı.
Kod bağlamı 2026-07-21/22'de 3 paralel keşif ajanıyla çıkarıldı (dosya:satır kanıtlı).
"""

DESCRIPTIONS: dict[str, str] = {

    # ─────────────────── KURUM AYARLARI ───────────────────

    "kurum_ayarlar.kurum_bilgileri": (
        "Kurumun temel kimlik alanlarını düzenler: kurum adı, sektör ve vergi numarası.\n"
        "\n"
        "Sınır: Bu kart yalnızca bu üç alanı yönetir — misyon/vizyon/değerler gibi "
        "stratejik kimlik alanları Kurum Paneli'nde ayrıca düzenlenir. Boş bırakılan alan "
        "kaydetmede mevcut değeri korur.\n"
        "\n"
        "Yorum: Sektör alanını doğru doldurmak önemlidir — sektör kıyas raporu bu alandan "
        "otomatik eşleşme yapar."
    ),

    "kurum_ayarlar.iletisim": (
        "Kurumun iletişim bilgilerini düzenler: adres, telefon, e-posta ve web sitesi.\n"
        "\n"
        "Sınır: 'Adres' alanı veritabanında faaliyet alanı (activity_area) kolonunda "
        "tutulur — iki kavram aynı alanı paylaşır; raporlarda bu alanı kullanırken bunu "
        "bilin.\n"
        "\n"
        "Yorum: Bu bilgiler dışa üretilen belgelerde (audit paketi, ESG raporu) kurum "
        "kimliği olarak görünür — güncel tutmak kurumsal görünürlüğün parçasıdır."
    ),

    "kurum_ayarlar.k_vektor": (
        "K-Vektör vizyon skorlamasını kurum genelinde açıp kapatır (tek anahtar).\n"
        "\n"
        "Sınır: Bu kart AĞIRLIK AYARLAMAZ — yalnızca etkinleştirir; strateji ağırlıkları "
        "SP sayfasından, süreç katkı yüzdeleri süreç sayfasından girilir. Anahtar "
        "değişimleri denetim izine yazılır.\n"
        "\n"
        "Yorum: K-Vektör'ü açmak vizyon/strateji skorlarının HESAP YÖNTEMİNİ değiştirir "
        "(1000 puanlık bütçe modeli) — dönem ortasında açıp kapatmak skor serilerinde "
        "kırılma yaratır; dönem başında karar verin."
    ),

    "kurum_ayarlar.yillik_plan_donemleri": (
        "Plan yıllarının hangi yıldan itibaren oluşturulacağını belirler; seçilen yıldan "
        "bugüne kadarki dönemler otomatik açılır.\n"
        "\n"
        "Sınır: Yıl bazlı çalışma artık temel davranıştır — eski 'yıl bazlılığı kapat' "
        "seçeneği kaldırılmıştır; bu kart yalnız başlangıç yılını belirler.\n"
        "\n"
        "Yorum: Geçmiş yılları dahil etmek, eski verilerin dönem karşılaştırmalarında "
        "görünmesini sağlar; gereksiz eski yıllar ise dönem listesini kalabalıklaştırır — "
        "gerçek veri olan ilk yılı seçin."
    ),

    "kurum_ayarlar.kurum_logosu": (
        "Kurum logosunu görüntüler ve yenisini yükletir (en fazla 2 MB).\n"
        "\n"
        "Sınır: PNG, JPG, GIF, WEBP ve SVG kabul edilir (ekran metni SVG'yi saymasa da "
        "yüklenebilir). Yeni logo eskisinin üzerine yazılır.\n"
        "\n"
        "Yorum: Şeffaf arka planlı, yatay oranlı logo arayüzde en temiz sonucu verir."
    ),

    "kurum_ozet_kartlar": (
        "Kurum Paneli'nin üstünde üç sayacı gösterir: aktif kullanıcı, aktif süreç ve "
        "ana strateji sayısı.\n"
        "\n"
        "Sınır: Süreç sayısı kullanıcının ERİŞİM KAPSAMINDAKİ süreçleri sayar — yetkisi "
        "sınırlı kullanıcı, kurum genelinden az görebilir. Kutular ayrıca kart görünürlük "
        "izinlerine tabidir.\n"
        "\n"
        "Yorum: İki kullanıcının farklı sayı görmesi hata değil kapsam farkıdır."
    ),

    # ─────────────────── TEKİL SAYFALAR ───────────────────

    "api_docs.endpoint_listesi": (
        "REST API v1 uçlarını tablo halinde listeler: metod, adres ve açıklama.\n"
        "\n"
        "Sınır: Liste ELLE bakımlı sabit bir dokümandır — koddan otomatik üretilmez "
        "(Swagger değildir); gerçek uç kümesiyle birebir senkron olmayabilir, yeni uçlar "
        "tabloya elle eklenmelidir.\n"
        "\n"
        "Yorum: Entegrasyon geliştirirken tabloyu başlangıç haritası olarak kullanın; "
        "kesin davranışı uç üzerinde deneyerek doğrulayın."
    ),

    "bildirim.liste": (
        "Bildirimlerinizi listeler — okunmamışlar üstte; tek tek veya toplu okundu "
        "işaretlenebilir.\n"
        "\n"
        "Sınır: Liste en yeni 50 kayıtla sınırlıdır; üst çubuktaki rozet ise TÜM "
        "okunmamışları sayar — rozet sayısı listede görünenden fazla olabilir. Liste "
        "kişiseldir, kurum geneli değildir.\n"
        "\n"
        "Yorum: Bildirim disiplinini günlük tutmak (okunanı işaretlemek) önemli atama ve "
        "değişikliklerin gürültüde kaybolmasını önler."
    ),

    "calendar.kurum_takvimi": (
        "Kurum geneli takvimi gösterir: tüm süreç faaliyetleri (yeşil), kurumdaki tüm "
        "proje görevleri (mavi) ve kendi kişisel görevleriniz (turuncu).\n"
        "\n"
        "Sınır: Masaüstündeki kişisel takvimden kapsamı farklıdır — burada süreç ve proje "
        "katmanları KURUM GENELİDİR; 'kendime görev' katmanı ise her iki takvimde de "
        "yalnız size aittir (başkalarının kişisel görevleri hiçbir takvimde görünmez).\n"
        "\n"
        "Yorum: Kurum takvimi kapasite çakışmalarını (aynı haftaya yığılmış bitişleri) "
        "kurum ölçeğinde gösterir — dönem planlaması yaparken buradan başlayın."
    ),

    # ─────────────────── PROJE (LİSTE SAYFASI) ───────────────────

    "project.toplam_proje": (
        "Filtreyle eşleşen erişilebilir proje sayısını ve ortalama sağlık skorunu "
        "gösterir.\n"
        "\n"
        "Sınır: Sağlık skoru şu an CANLI HESAPLANMAYAN, kayıtta tutulan bir değerdir — "
        "elle/kurulumla girilir, görev durumundan otomatik türetilmez; ortalamayı bu "
        "bilgiyle okuyun.\n"
        "\n"
        "Yorum: Sayı, seçili filtrelere ve yetkinize göre değişir — kıyas yapmadan önce "
        "filtreleri sıfırlayın."
    ),

    "project.acik_gorev": (
        "Filtreli projelerdeki tamamlanmamış görev sayısını, toplam görevle birlikte "
        "gösterir.\n"
        "\n"
        "Hesap: 'Açık' = durumu tamamlandı sayılmayan tüm görevler (yapılacak, devam, "
        "beklemede ve durumu boş olanlar dahil).\n"
        "\n"
        "Yorum: Açık/toplam oranı portföyün yürüyüş temposudur; oran uzun süre "
        "değişmiyorsa işler açılıyor ama kapanmıyor demektir."
    ),

    "project.gecikmis_gorev": (
        "Bitiş tarihi geçmiş ve tamamlanmamış görev sayısını gösterir.\n"
        "\n"
        "Eşik: Sıfırdan büyükse kırmızı, sıfırsa yeşil.\n"
        "\n"
        "Sınır: Bu GÖREV gecikmesidir — proje PLAN gecikmesi (bitiş tarihi geçen "
        "projeler) operasyon özetinde ayrı sayılır.\n"
        "\n"
        "Yorum: Geciken görevleri projeye ve kişiye kırarak okuyun; yaygın gecikme "
        "kapasite, tekil gecikme sahiplik sorunudur."
    ),

    "project.bu_hafta_biten": (
        "Önümüzdeki 7 gün içinde bitiş tarihi gelen AÇIK görev sayısını (ve aynı "
        "penceredeki proje sayısını) gösterir.\n"
        "\n"
        "Sınır: Adı 'biten' olsa da bu kart TAMAMLANANLARI değil, VADESİ YAKLAŞANLARI "
        "sayar — haftalık iş yükü uyarısıdır.\n"
        "\n"
        "Yorum: Haftaya bu listeyle başlayın — vadesi gelen işleri önceden görmek, "
        "gecikmiş görev sayacını beslememenin tek yoludur."
    ),

    "project.acik_raid": (
        "Açık RAID kayıtlarının (risk, varsayım, sorun, bağımlılık) toplamını ve tür "
        "dağılımını mini halka grafikle gösterir.\n"
        "\n"
        "Hesap: 'Açık' = durumu kapalı/çözüldü olmayan kayıtlar.\n"
        "\n"
        "Yorum: RAID sayısının sıfır olması her zaman iyi değildir — hiç risk kaydı "
        "olmayan proje çoğu zaman risksiz değil, risk yönetmiyordur."
    ),

    "project.kritik_saglik": (
        "Sağlık skoru 50'nin altında olan proje sayısını gösterir.\n"
        "\n"
        "Eşik: Skor < 50 kritik sayılır; sayı sıfırdan büyükse kart kırmızı.\n"
        "\n"
        "Sınır: Sağlık skoru kayıtta tutulan STATİK bir değerdir — görev/gecikme "
        "verisinden canlı hesaplanmaz; güncellenmeyen skor gerçeği yansıtmayabilir.\n"
        "\n"
        "Yorum: Kritik listesindeki projelerde skorun ne zaman ve neye göre verildiğini "
        "sorgulayarak başlayın."
    ),

    "project.operasyon_ozeti": (
        "Proje operasyonunun tek bakışlık panosudur: sekiz mini sayaç (proje, açık/"
        "toplam görev, geciken, 7 gün vadeli, plan geciken, açık RAID, sağlık ortalaması) "
        "ile haftalık tamamlama trendi, görev durumu ve öncelik dağılımları, RAID halkası, "
        "4 haftalık tamamlama ısı haritası ve dikkat listesi.\n"
        "\n"
        "Hesap: 'Plan geciken' proje bitiş tarihine, 'geciken görev' görev vade tarihine "
        "bakar — iki ayrı ölçüdür. Dikkat listesi geciken görevli veya planı geçmiş "
        "projeleri toplar (en fazla 12).\n"
        "\n"
        "Yorum: Haftalık proje toplantısının açılış ekranı olarak tasarlanmıştır; her "
        "sayaç ilgili detay görünümüne açılır."
    ),

    "project.proje_listesi": (
        "Projeleri sayfalı kartlar halinde listeler: lider(ler), öncelik, sağlık rozeti "
        "ve hızlı işlemler (aç/kopyala).\n"
        "\n"
        "Sınır: Sayfa başına 20 proje gösterilir; sağlık rozeti kayıtlı statik değerdir.\n"
        "\n"
        "Yorum: Lider atanmamış projeler listede hemen fark edilir — sahipsiz proje, "
        "gecikme istatistiğinin yarınki adayıdır."
    ),

    "project_calendar.takvim": (
        "Projenin görevlerini aylık/haftalık takvimde gösterir; görevler sürükleyerek "
        "yeniden tarihlenebilir.\n"
        "\n"
        "Sınır: Yalnızca başlangıç veya bitiş tarihi olan görevler görünür — tarihsiz "
        "görevler takvimde YOKTUR.\n"
        "\n"
        "Yorum: Takvimde görünmeyen iş planlanmamış iştir; tarihsiz görevleri "
        "tarihlendirmek takvimi gerçek plana dönüştürür."
    ),

    "project_detail.geciken_gorev_uyarisi": (
        "Projede geciken görev varsa üstte uyarı bandı gösterir (adet ile).\n"
        "\n"
        "Hesap: Bitiş tarihi geçmiş ve tamamlanmamış görevler sayılır; geciken yoksa bant "
        "hiç görünmez.\n"
        "\n"
        "Yorum: Bandın görünür olması proje sayfasına her girişte küçük bir rahatsızlık "
        "yaratır — bu bilinçli bir tasarımdır; rahatsızlık kapanışla giderilir."
    ),

    "project_detail.gorev_ozeti": (
        "Görevleri dört sütunda özetler: tamamlandı, devam ediyor, beklemede, yapılacak "
        "— her sütunda adet ve görev kartları.\n"
        "\n"
        "Sınır: Tam Kanban görünümü üç sütun kullanır ve 'beklemede'yi 'devam' sütununa "
        "katar — iki ekranın sütun sayıları farklıdır.\n"
        "\n"
        "Yorum: 'Beklemede' sütununun büyümesi dış bağımlılık veya karar bekleyen iş "
        "birikimini gösterir — RAID kaydına dönüştürülmeye adaydır."
    ),

    "project_detail.proje_ozeti": (
        "Projenin kimlik kartıdır: lider(ler), öncelik, bağlı stratejik girişim, açıklama "
        "ve ekip (üyeler/gözlemciler).\n"
        "\n"
        "Yorum: Girişim bağı boşsa proje stratejik haritada görünmez — 'bu projeyi neden "
        "yapıyoruz' sorusunun cevabı bu bağla kurulur."
    ),

    "project_form.sayfa": (
        "Proje oluşturma ve düzenleme formudur: ad, açıklama, öncelik, lider/üye/gözlemci "
        "atamaları ve süreç bağlantıları.\n"
        "\n"
        "Sınır: Sağlık skoru bu formda ayarlanmaz.\n"
        "\n"
        "Yorum: Kuruluş anında en az bir lider ve bir süreç bağı vermek, projenin "
        "raporlarda ve stratejik ekranlarda görünür olmasını baştan garantiler."
    ),

    "project_gantt.gantt_semasi": (
        "Görevleri zaman çizelgesinde (Gantt) gösterir: başlangıç-bitiş barları, ilerleme "
        "ve kritik yol (CPM) vurgusu.\n"
        "\n"
        "Sınır: Yalnızca hem başlangıç hem bitiş tarihi türetilebilen görevler çizilir; "
        "kritik yol ayrı hesaplanır ve vurgulanır.\n"
        "\n"
        "Kaynak: Kritik yol, Kelley ve Walker'ın CPM yöntemine (1959) dayanır.\n"
        "\n"
        "Yorum: Kritik yoldaki bir günlük gecikme projenin bitişini bir gün öteler — "
        "hızlandırma çabasını kritik yol dışındaki işlere harcamayın."
    ),

    "project_kanban.yapilacak": (
        "Kanban panosunun 'yapılacak' sütunudur; henüz başlamamış görevler burada durur "
        "ve sürükleyince durum güncellenir.\n"
        "\n"
        "Yorum: Sütunun makul boyu ekip kapasitesiyle orantılı olmalıdır — sonsuz uzayan "
        "yapılacak listesi plan değil dilek listesidir."
    ),

    "project_kanban.devam_beklemede": (
        "Kanban panosunun orta sütunudur: devam eden VE beklemedeki görevler birlikte "
        "gösterilir.\n"
        "\n"
        "Sınır: Bu sütuna sürüklenen görev 'devam ediyor' olarak kaydedilir — 'beklemede' "
        "durumu sürüklemeyle korunmaz; beklemede işaretlemek için görev formunu kullanın.\n"
        "\n"
        "Yorum: Devam ve beklemenin aynı sütunda olması sadeleştirmedir; bekleyen işleri "
        "ayrı izlemek istiyorsanız görev özetindeki dört sütunlu görünüme bakın."
    ),

    "project_kanban.tamamlandi": (
        "Kanban panosunun 'tamamlandı' sütunudur; biten görevler tamamlanma tarihiyle "
        "listelenir.\n"
        "\n"
        "Yorum: Sütunu dönem sonlarında arşivlemek panoyu hafif tutar; tamamlanma "
        "tarihleri haftalık tamamlama trendini besler."
    ),

    "project_kapasite.sayfa": (
        "Proje ekibine haftalık kapasite (saat) ve dönem ataması yapar: kim, haftada kaç "
        "saat, hangi tarih aralığında.\n"
        "\n"
        "Sınır: Bu sayfa yalnızca PLANLANAN kapasiteyi kaydeder — gerçek iş yüküyle "
        "karşılaştırma ve aşırı yüklenme hesabı henüz YOKTUR; 'aşırı yüklenme takibi' "
        "gelecek geliştirmenin temelidir.\n"
        "\n"
        "Yorum: Aynı kişiye birden çok projede kapasite atarken toplamı elle kontrol "
        "edin — sistem şimdilik uyarmaz."
    ),

    "project_portfolio.portfoy_listesi": (
        "Projeleri stratejik skora göre sıralar: bağlı süreçler, süreç puanları ve toplam "
        "stratejik skor.\n"
        "\n"
        "Hesap: Projenin skoru, bağlı süreçlerinin strateji katkı puanlarının toplamıdır.\n"
        "\n"
        "Eşik: Skor 50+ yeşil, 30-49 sarı, altı gri.\n"
        "\n"
        "Sınır: Stratejik skor, sağlık skorundan TAMAMEN bağımsızdır — biri 'stratejiye ne "
        "kadar hizmet ediyor', diğeri 'ne kadar sağlıklı yürüyor' sorusudur.\n"
        "\n"
        "Yorum: Düşük stratejik skorlu ama kaynak tüketen projeler portföy tıraşlamasının "
        "ilk adaylarıdır."
    ),

    "project_portfolio.program_gantt": (
        "Tüm projeleri tek zaman çizelgesinde (program Gantt) gösterir.\n"
        "\n"
        "Sınır: Yalnızca başlangıç/bitiş tarihi tanımlı projeler çizilir; görev düzeyi "
        "detay yoktur (o proje Gantt'ındadır).\n"
        "\n"
        "Yorum: Program görünümü dönemsel yığılmayı gösterir — aynı çeyrekte biten çok "
        "sayıda proje, kapanış kalitesini düşüren klasik desendir."
    ),

    "project_raid.riskler": (
        "Projenin risk kayıtlarını tutar: olasılık ve etki (1-5), azaltma planı ve durum.\n"
        "\n"
        "Sınır: Bu ekranda risk skoru (olasılık × etki) HESAPLANMAZ — değerler ayrı ayrı "
        "gösterilir; kurumsal risk ısı haritası ayrı modüldür.\n"
        "\n"
        "Yorum: İyi risk kaydının ölçüsü azaltma planının somutluğudur — 'dikkat "
        "edilecek' bir plan değildir."
    ),

    "project_raid.varsayimlar": (
        "Projenin varsayım kayıtlarını tutar: doğrulama tarihi, doğrulandı işareti ve "
        "notlar.\n"
        "\n"
        "Yorum: Varsayım, doğrulanana kadar risktir — doğrulama tarihi geçmiş ve hâlâ "
        "işaretsiz varsayımlar risk listesine terfi ettirilmelidir."
    ),

    "project_raid.sorunlar": (
        "Projenin sorun (issue) kayıtlarını tutar: aciliyet ve etkilenen çalışma.\n"
        "\n"
        "Yorum: Sorun, gerçekleşmiş risktir — çözüm sahibi ve durumu güncel tutulmayan "
        "sorun kaydı, kayıt değil mezar taşıdır."
    ),

    "project_raid.bagimliliklar": (
        "Projenin bağımlılık kayıtlarını tutar: bağımlılık tipi (FS/SS/FF/SF) ve ilgili "
        "görev.\n"
        "\n"
        "Sınır: Buradaki RAID bağımlılığı, Gantt'ın kritik yol hesabındaki görev "
        "bağımlılığından AYRI bir kayıttır — RAID kaydı belgeleme amaçlıdır, çizelgeyi "
        "etkilemez.\n"
        "\n"
        "Yorum: Dış ekiplere/tedarikçilere bağımlılıkları burada belgelemek, gecikme "
        "tartışmalarında 'kim ne zaman söyledi' sorusunun cevabını hazır tutar."
    ),

    "project_strategy_detail.bagli_surecler": (
        "Projenin bağlı olduğu süreçleri ve her sürecin stratejik katkı puanını tablolar.\n"
        "\n"
        "Hesap: Süreç puanı, sürecin alt stratejilere katkı yüzdelerinin toplamından "
        "türetilir; tablo puana göre sıralıdır.\n"
        "\n"
        "Yorum: Bağlı süreç yoksa projenin stratejik skoru sıfırdır — bağ kurmak bu "
        "sayfadaki her metriğin ön koşuludur."
    ),

    "project_strategy_detail.proje_bilgisi": (
        "Projenin adını ve açıklamasını gösteren başlık kartıdır.\n"
        "\n"
        "Yorum: Açıklamayı 'ne yapılacak' değil 'neden yapılıyor' diliyle yazmak, "
        "stratejik detay sayfasının bağlamını güçlendirir."
    ),

    "project_strategy_detail.stratejik_skor": (
        "Projenin toplam stratejik skorunu ve güçlü/zayıf ilişki sayılarını gösterir.\n"
        "\n"
        "Hesap: Toplam skor, bağlı süreçlerin katkı puanlarının toplamıdır. İlişki "
        "sınıflaması süreç-alt strateji çifti başına yapılır: katkı 9+ güçlü, 3-8 zayıf "
        "sayılır.\n"
        "\n"
        "Sınır: Toplam skor PUAN toplamı, güçlü/zayıf sayıları ise ÇİFT ADEDİDİR — iki "
        "metrik farklı birimlerdedir.\n"
        "\n"
        "Yorum: Çok sayıda zayıf ilişki, tek güçlü ilişkiden daha az değerlidir — bağları "
        "yaymak yerine derinleştirmek stratejik netlik sağlar."
    ),

    "project_task_detail.sayfa": (
        "Tek görevin detay sayfasıdır: başlık, durum, öncelik, bitiş tarihi, açıklama ve "
        "bağlı performans göstergesi.\n"
        "\n"
        "Yorum: Görev-PG bağı, 'bu iş hangi ölçüme hizmet ediyor' sorusunun cevabıdır — "
        "bağlı görevler tamamlandıkça göstergenin iyileşmesi beklenir; beklenti "
        "gerçekleşmiyorsa ya bağ ya faaliyet yanlış seçilmiştir."
    ),

    "project_task_form.sayfa": (
        "Görev oluşturma ve düzenleme formudur: başlık, açıklama, durum, öncelik, atanan "
        "kişi, bitiş tarihi ve bağlı gösterge.\n"
        "\n"
        "Sınır: Öncelik değerleri sistemde İngilizce saklanır ve ekranda Türkçe "
        "gösterilir; durum Türkçe normalize edilir.\n"
        "\n"
        "Yorum: Atanansız ve tarihsiz görev, panoda görünse de takip edilemez — formu bu "
        "iki alanı doldurmadan kapatmamayı ekip alışkanlığı yapın."
    ),

    # ─────────────────── AYARLAR (GENEL) ───────────────────

    "ayarlar.kullanici_ozeti": (
        "Oturum açan kullanıcının e-postasını ve rolünü gösterir.\n"
        "\n"
        "Yorum: Rolünüz ekranda ne görebildiğinizi belirler — beklediğiniz bir menü "
        "görünmüyorsa önce buradaki role bakın."
    ),

    "ayarlar.kurum_ozeti": (
        "Bağlı olduğunuz kurumun adını ve numarasını gösterir.\n"
        "\n"
        "Yorum: Destek taleplerinde kurum numarasını paylaşmak çözümü hızlandırır."
    ),

    "ayarlar.tema_durumu": (
        "Aktif temayı (aydınlık/karanlık) gösterir.\n"
        "\n"
        "Sınır: Tema buradan DEĞİŞTİRİLMEZ — üst çubuktaki kullanıcı menüsünden değişir; "
        "tercih sunucuda saklanır ve cihazlar arasında taşınır.\n"
        "\n"
        "Yorum: Uzun ekran mesailerinde karanlık tema göz yorgunluğunu azaltır."
    ),

    "ayarlar.zamanlanmis_rapor_ozeti": (
        "Etkinleştirdiğiniz zamanlanmış rapor aboneliği sayısını gösterir.\n"
        "\n"
        "Sınır: Sayı, aboneliğin AÇIK olduğunu gösterir — gönderimin fiilen çalıştığını "
        "değil; gönderim davranışı için ilgili rapor kartlarındaki notlara bakın.\n"
        "\n"
        "Yorum: Aboneliği açtığınız hâlde e-posta gelmiyorsa kurum SMTP ayarlarını ve "
        "rapor kartlarındaki durum notlarını kontrol edin."
    ),

    "ayarlar.hesap_ayarlari": (
        "Kişisel hesap ayarları sayfasına geçiş kartıdır: bildirim tercihleri, tema, dil "
        "ve saat dilimi.\n"
        "\n"
        "Yorum: Ayarların kişisel/kurumsal ayrımına dikkat: buradakiler yalnız sizi "
        "etkiler; kurum geneli ayarlar ayrı karttadır."
    ),

    "ayarlar.profil_bilgileri": (
        "Profil sayfasına geçiş kartıdır: ad, unvan, departman ve fotoğraf.\n"
        "\n"
        "Yorum: Departman alanınızın dolu olması İK panolarının (departman dağılımı, "
        "performans) doğruluğunu doğrudan etkiler."
    ),

    "ayarlar.kurum_ayarlari": (
        "Kurum ayarları sayfasına geçiş kartıdır (yalnız kurum yöneticilerine görünür): "
        "iletişim bilgileri ve logo.\n"
        "\n"
        "Yorum: Kurum bilgileri dışa üretilen tüm belgelerde görünür — dönemsel kontrolü "
        "yönetici rutinine ekleyin."
    ),

    "ayarlar.yonetim_paneli": (
        "Yönetim paneline geçiş kartıdır (yalnız sistem yöneticisine görünür): giriş "
        "istatistikleri ve aktivite kayıtları.\n"
        "\n"
        "Yorum: Panel, kullanım ve benimseme takibinin merkezi ekranıdır."
    ),

    "ayarlar.zamanlanmis_raporlar": (
        "Zamanlanmış rapor abonelikleri sayfasına geçiş kartıdır: haftalık özet, sabah "
        "özeti, risk uyarısı ve aylık PG raporu.\n"
        "\n"
        "Yorum: Abonelikler kişiseldir — her yönetici kendi rapor setini kendisi açar."
    ),

    "ayarlar.eposta_bildirimleri": (
        "E-posta ayarları sayfasına geçiş kartıdır: kurum SMTP yapılandırması ve olay "
        "bazlı bildirim tercihleri.\n"
        "\n"
        "Yorum: Sistemden hiç e-posta gitmiyorsa ilk bakılacak yer bu sayfadaki SMTP "
        "yapılandırmasıdır."
    ),

    # ─────────────────── AYARLAR — E-POSTA ───────────────────

    "ayarlar_eposta.ozel_smtp": (
        "Kurumun kendi SMTP sunucusunu yapılandırır: sunucu, port, kimlik bilgileri, "
        "TLS/SSL, gönderici kimliği; bağlantı testi yapılabilir.\n"
        "\n"
        "Hesap: Şifre veritabanında ŞİFRELİ (Fernet) saklanır; kaydederken boş bırakılan "
        "şifre mevcut değeri korur. Özel SMTP kapalıysa sistem varsayılan posta "
        "yapılandırmasını kullanır.\n"
        "\n"
        "Sınır: Şifreleme anahtarı (ENCRYPTION_KEY) değişirse kayıtlı şifre çözülemez "
        "olur — anahtar yönetimi operasyonel bir sorumluluktur.\n"
        "\n"
        "Yorum: Kurulumdan sonra mutlaka bağlantı testi yapın ve ilk gerçek bildirimde "
        "spam klasörünü kontrol edin (SPF/DKIM ayarları sizin alan adınızın işidir)."
    ),

    "ayarlar_eposta.bildirim_tercihleri": (
        "Hangi olaylar için e-posta gideceğini seçer: sürece atama, gösterge değişikliği, "
        "faaliyet ekleme ve görev atama.\n"
        "\n"
        "Sınır: Tercihler kurum düzeyindedir ve varsayılan olarak hepsi açıktır.\n"
        "\n"
        "Yorum: Bildirim yorgunluğu gerçek bir risktir — ekip 'her şey' yerine 'atama' "
        "olaylarını açık tutarak başlayabilir."
    ),

    # ─────────────────── AYARLAR — ZAMANLANMIŞ RAPORLAR ───────────────────

    "ayarlar_zamanlanmis_raporlar.haftalik_strateji_ozeti": (
        "Haftalık strateji özeti aboneliğini yönetir: gün ve saat seçimiyle strateji "
        "sağlığı, PG performansı, gecikmeler ve riskleri içeren özet e-postası.\n"
        "\n"
        "Sınır: Mevcut sürümde gönderim zamanlaması SABİTTİR (Pazartesi 09:00) ve burada "
        "seçilen gün/saat tercihi ile PDF eki HENÜZ gönderime yansımaz — zengin içerikli "
        "PDF yalnız 'önizleme' ile elle üretilebilir; zamanlayıcının aktif olması sunucu "
        "yapılandırmasına bağlıdır.\n"
        "\n"
        "Yorum: Aboneliği açın ama ilk haftalarda e-postanın gelip gelmediğini doğrulayın; "
        "gelmiyorsa sistem yöneticinizle zamanlayıcı ayarını kontrol edin."
    ),

    "ayarlar_zamanlanmis_raporlar.sabah_operasyonel_ozeti": (
        "Sabah operasyonel özeti aboneliğini yönetir: gün başında biten/bekleyen "
        "faaliyetler ve kritik göstergeler için e-posta tercihi.\n"
        "\n"
        "Sınır: Bu abonelik için zamanlanmış GÖNDERİM HENÜZ KODLANMAMIŞTIR — seçim "
        "yalnızca tercih olarak saklanır; aynı içerik masaüstündeki 'yönetici sabah "
        "özeti' kartında canlı görülebilir.\n"
        "\n"
        "Yorum: E-posta beklemek yerine güne masaüstü sabah özetiyle başlayın; gönderim "
        "özelliği geldiğinde tercihiniz hazır olacaktır."
    ),

    "ayarlar_zamanlanmis_raporlar.risk_anomali_uyarisi": (
        "Risk ve anomali uyarı aboneliğini yönetir: kritik riskler ve yüksek öncelikli "
        "gösterge sapmaları için günlük/haftalık e-posta tercihi.\n"
        "\n"
        "Sınır: Bu abonelik için zamanlanmış GÖNDERİM HENÜZ KODLANMAMIŞTIR — tercih "
        "saklanır ama e-posta üretilmez; risk ve anomali durumu panolarda canlı izlenir.\n"
        "\n"
        "Yorum: Kritik risk takibini şimdilik yönetici paneli ve çeyreklik değerlendirme "
        "ekranlarından yapın."
    ),

    "ayarlar_zamanlanmis_raporlar.aylik_pg_raporu": (
        "Aylık gösterge raporu aboneliğini yönetir: ay sonu PG durumu (hedef üstü/altı, "
        "veri eksikleri) için gün ve saat tercihiyle Excel ekli e-posta.\n"
        "\n"
        "Sınır: Bu abonelik için zamanlanmış GÖNDERİM ve Excel üretimi HENÜZ "
        "KODLANMAMIŞTIR — tercih saklanır ama rapor gönderilmez.\n"
        "\n"
        "Yorum: Ay sonu PG durumunu şimdilik veri kalitesi ve K-Rapor ekranlarından alın; "
        "Excel ihtiyacı için BI bağlantısındaki CSV çıkışı kullanılabilir."
    ),

    # ─────────────────── PROFİL VE HESAP ───────────────────

    "auth_ayarlar.bildirim_ayarlari": (
        "Kişisel bildirim tercihlerinizi yönetir: e-posta, süreç, görev ve son tarih "
        "hatırlatmaları (varsayılan hepsi açık).\n"
        "\n"
        "Sınır: Bunlar KİŞİSEL tercihlerdir — kurum düzeyindeki e-posta olay ayarlarından "
        "ayrıdır; bir bildirimin gitmesi için iki katmanın da açık olması gerekir.\n"
        "\n"
        "Yorum: Bildirimleri tamamen kapatmak yerine kanal bazında budayın — son tarih "
        "hatırlatması çoğu kullanıcı için en değerlisidir."
    ),

    "auth_ayarlar.dil_ve_bolge": (
        "Dil, saat dilimi ve tarih formatı tercihlerinizi yönetir.\n"
        "\n"
        "Sınır: Şu an iki dil (Türkçe, İngilizce), iki saat dilimi (İstanbul, Londra) ve "
        "üç tarih formatı desteklenir.\n"
        "\n"
        "Yorum: Dil değişikliği arayüz metinlerini çevirir; kullanıcıların girdiği "
        "içerikler (strateji adları, açıklamalar) girildiği dilde kalır."
    ),

    "auth_ayarlar.gorunum": (
        "Görünüm (karanlık mod) hakkında bilgilendirme kartıdır.\n"
        "\n"
        "Sınır: Tema buradan değiştirilmez — üst çubuktaki kullanıcı menüsünden "
        "değiştirilir; kart yalnızca yönlendirir.\n"
        "\n"
        "Yorum: Tema tercihi hesabınızda saklanır ve tüm cihazlarınızda aynı görünümü "
        "sağlar."
    ),

    "auth_profil.iki_faktorlu_dogrulama": (
        "İki faktörlü doğrulamayı (2FA) yönetir: durum, kurulum (QR kod), devre dışı "
        "bırakma ve kalan yedek kod sayısı.\n"
        "\n"
        "Hesap: Doğrulama TOTP standardıyla çalışır (30 saniyelik kodlar, ±30 sn "
        "tolerans); kurulumda 10 adet tek kullanımlık yedek kod üretilir.\n"
        "\n"
        "Yorum: Yedek kodları şifre kasanıza kaydedin — telefon kaybında hesaba tek "
        "dönüş yolunuz onlardır; kalan kod sayısı azaldığında yeniden üretin."
    ),

    "auth_profil.kisisel_bilgiler": (
        "Kişisel bilgilerinizi düzenler: ad, soyad, e-posta, telefon, unvan, departman "
        "ve şifre değişikliği.\n"
        "\n"
        "Sınır: Şifre kuralı en az 8 karakter ve karmaşıklık ister (ekranda eski '6 "
        "karakter' notu kalmış olabilir — geçerli kural 8'dir).\n"
        "\n"
        "Yorum: Unvan ve departmanı güncel tutmak İK panolarını ve karne başlıklarını "
        "doğru besler."
    ),

    "auth_profil.profil_ozeti": (
        "Profil özetinizi gösterir: fotoğraf (yükleme ile), ad soyad, e-posta ve rol "
        "rozeti.\n"
        "\n"
        "Hesap: Yüklenen fotoğraf otomatik olarak 512×512 boyutuna küçültülür; fotoğraf "
        "yoksa baş harfli avatar gösterilir.\n"
        "\n"
        "Yorum: Profil fotoğrafları ekip listelerinde ve atama ekranlarında tanınırlığı "
        "artırır — küçük ama etkili bir benimseme detayıdır."
    ),
}
