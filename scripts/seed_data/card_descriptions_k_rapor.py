# -*- coding: utf-8 -*-
"""K-Rapor (rapor katmanı) kart açıklamaları — 58 kart.

Yazım sözleşmesi için bkz. card_descriptions_k_radar.py başlığı.

Koddan doğrulanmış ortak kurallar:
  - Renk bandı: >=80 yeşil, 50-80 sarı, <50 kırmızı.
  - Isı haritası AYRI bant kullanır: <25 / <50 / <75 / <95 / >=95.
  - Skor motoru (compute_pg_score) yıl içindeki TÜM ölçümleri birleştirir
    (toplama/son değer/ortalama); rapor endpoint'lerinin bir kısmı ise
    yalnız SON ölçümü kullanır — aynı gösterge iki sekmede farklı çıkabilir.
  - "lower_is_better" ölü koşulu → bkz. docs/kontrol/KART-VERI-TUTARSIZLIKLARI.md D0.
"""

DESCRIPTIONS: dict[str, str] = {

    # ─────────────────────────── KURUMSAL ───────────────────────────

    "k_rapor_kurumsal.vizyon_skoru": (
        "Kurumun vizyon başarı skorunu 0-100 ölçeğinde tek göstergede özetler.\n"
        "\n"
        "Hesap: Gösterge → süreç → alt strateji → ana strateji → vizyon zinciriyle yukarı "
        "toplanır. Süreç seviyesinde gösterge ağırlıkları kullanılır.\n"
        "\n"
        "Sınır: Süreç üstündeki katmanlarda (alt strateji, ana strateji, vizyon) ağırlık YOKTUR — "
        "düz ortalama alınır. Bir stratejiye 50 süreç, diğerine 1 süreç bağlıysa ikisi vizyon "
        "skorunda eşit ağırlıktadır. Ayrıca içi boş strateji 0 sayılır ve ortalamayı aşağı çeker.\n"
        "\n"
        "Not: Kurumunuzda K-Vektör etkinse skor bunun yerine ağırlıklı 1000 puanlık bütçe "
        "modeliyle hesaplanır. İki motor farklı sonuç verebilir.\n"
        "\n"
        "Yorum: Skoru yorumlamadan önce kaç göstergeye veri girildiğine bakın — ölçülmeyen alan "
        "skoru düşürmez, sadece görünmez kılar."
    ),

    "k_rapor_kurumsal.strateji_bazli_basari": (
        "Her ana strateji için ortalama başarıyı yatay çubuklarla karşılaştırır.\n"
        "\n"
        "Hesap: Stratejinin alt stratejilerinin, onların da bağlı süreçlerinin skorlarının "
        "ortalamasıdır. Liste skora göre azalan sıralıdır.\n"
        "\n"
        "Eşik: 80 ve üzeri yeşil, 50-80 sarı, altı kırmızı.\n"
        "\n"
        "Sınır: Ortalamalar ağırlıksızdır — az sayıda süreci olan strateji ile çok sayıda süreci "
        "olan strateji eşit muamele görür.\n"
        "\n"
        "Yorum: Alttaki stratejiler kaynak veya odak eksikliğini işaret eder. Ancak önce o "
        "stratejiye bağlı süreçlerde ölçüm olup olmadığını kontrol edin; veri yokluğu düşük "
        "performans gibi görünür."
    ),

    "k_rapor_kurumsal.en_iyi_5_surec": (
        "En yüksek performanslı ilk 5 süreci sıralı liste halinde gösterir.\n"
        "\n"
        "Hesap: Süreç skorları (göstergelerin ağırlıklı ortalaması) azalan sıralanır, ilk 5 alınır.\n"
        "\n"
        "Yorum: Bu liste iyi uygulama kaynağıdır — yüksek performanslı süreçlerin yöntemleri "
        "diğerlerine aktarılabilir. Ancak yüksek skor, göstergelerin kolay hedeflerle "
        "tanımlanmış olmasından da kaynaklanabilir; hedef zorluğunu birlikte değerlendirin."
    ),

    "k_rapor_kurumsal.en_dusuk_5_surec": (
        "En düşük performanslı 5 süreci gösterir.\n"
        "\n"
        "Hesap: Süreç skorları azalan sıralanır ve skoru tam 100 olmayanların son 5'i alınır.\n"
        "\n"
        "Sınır: Liste azalan sıranın kuyruğu olduğu için EN KÖTÜ SÜREÇ EN ALTTADIR — ilk satır "
        "en kötü değildir. Ayrıca skoru tam 100 olan süreçler elendiği için kart 5'ten az satır "
        "gösterebilir.\n"
        "\n"
        "Sınır 2: Göstergesi olmayan veya verisi girilmemiş süreçler 0 puan alır ve bu listeye "
        "düşer. Yani buradaki süreçlerin bir kısmı kötü performanslı değil, ÖLÇÜLMEMİŞ olabilir. "
        "Müdahale etmeden önce sürecin gerçekten verisi olup olmadığını kontrol edin.\n"
        "\n"
        "Yorum: Veri Durumu sekmesi hangi göstergelerin boş olduğunu gösterir."
    ),

    # ─────────────────────────── K-VEKTÖR ───────────────────────────

    "k_rapor_k_vektor.ana_strateji_agirliklari": (
        "Ana stratejilere dağıtılan ağırlık paylarını halka grafikle gösterir.\n"
        "\n"
        "Hesap: 1000 puanlık vizyon bütçesi, stratejilere girilen ham ağırlıklar oranında "
        "bölünür. Dilim yüzdesi = strateji kotası / 1000.\n"
        "\n"
        "Sınır: Ağırlık hiç girilmemişse veya toplamı sıfırsa bütçe EŞİT bölünür. Bu durumda "
        "grafikteki eşit dilimler sizin tercihiniz değil, sistemin varsayılanıdır — ağırlık "
        "tanımlamadığınız anlamına gelir.\n"
        "\n"
        "Yorum: Ağırlık, hangi stratejinin vizyona daha çok katkı verdiğini belirler. Ağırlık "
        "dağılımı kurumun beyan ettiği önceliklerle uyumsuzsa, ölçüm sistemi stratejiyi değil "
        "başka bir şeyi optimize ediyor demektir."
    ),

    "k_rapor_k_vektor.agirlik_tablosu": (
        "Ana stratejilerin ağırlık paylarını çubuk listesi olarak gösterir.\n"
        "\n"
        "Hesap: Halka grafikle aynı veriyi kullanır — 1000 puanlık bütçeden alınan pay yüzdesi.\n"
        "\n"
        "Sınır: Bu listede YALNIZCA AĞIRLIK vardır, başarı skoru gösterilmez. Ağırlık ile "
        "gerçekleşen başarıyı karşılaştırmak için Kurumsal sekmesindeki 'Strateji Bazlı Başarı' "
        "kartını birlikte kullanın.\n"
        "\n"
        "Yorum: Yüksek ağırlıklı bir stratejinin başarısı düşükse vizyon skoru üzerindeki olumsuz "
        "etkisi büyüktür — önce oraya bakılmalıdır."
    ),

    "k_rapor_k_vektor.alt_strateji_agirliklari": (
        "Alt stratejileri kod, ad ve değerleriyle listeler.\n"
        "\n"
        "Sınır — ÖNEMLİ: Tablonun üçüncü sütunu 'Ham Ağırlık' başlığını taşısa da gösterilen "
        "değer AĞIRLIK DEĞİL, alt stratejinin BAŞARI SKORUDUR (0-100). Liste de bu skora göre "
        "sıralanır. Alt strateji ham ağırlıkları bu ekranda yer almaz.\n"
        "\n"
        "Hesap: Alt strateji skoru, bağlı süreçlerin katkı yüzdeleriyle ağırlıklı ortalamasıdır. "
        "Katkı yüzdesi girilmemişse süreçler eşit pay alır.\n"
        "\n"
        "Yorum: Skoru düşük alt stratejiler, üst stratejinin başarısını aşağı çeken halkalardır."
    ),

    # ─────────────────────────── PG DAĞILIM ───────────────────────────

    "k_rapor_pg_dagilim.basari_yuzdesi_dagilimi_histogram": (
        "Göstergelerin başarı yüzdelerine göre nasıl dağıldığını histogramla gösterir.\n"
        "\n"
        "Hesap: Her göstergenin son ölçümünden başarı yüzdesi hesaplanır ve %0-10, %10-20 … "
        "%90-100 olmak üzere 10 kovaya dağıtılır. Çubuk yüksekliği o kovadaki gösterge sayısıdır.\n"
        "\n"
        "Sınır: Başarı yüzdesi 100 ile tavanlanır; hedefini aşan göstergeler de en sağdaki kovaya "
        "düşer ve aşım miktarı görünmez. Hedefi veya ölçümü olmayan göstergeler histogramda hiç "
        "yer almaz.\n"
        "\n"
        "Yorum: Sağa yığılmış dağılım genel başarıyı, sola yığılma sistemik sorunu gösterir. "
        "İki uçta kümelenme (çift tepe) ise kurumda iki farklı olgunluk seviyesinin bir arada "
        "olduğuna işaret eder — ortalama bu durumu gizler, histogram gösterir."
    ),

    "k_rapor_pg_dagilim.pg_dagilim_grafigi": (
        "Düşük performanslı göstergeleri yatay çubuklarla sıralar.\n"
        "\n"
        "Sınır: Kart adı 'dağılım grafiği' olsa da bu bir dağılım gösterimi değildir. Ekranda "
        "başarı yüzdesi EN DÜŞÜK 20 gösterge listelenir. Genel dağılımı görmek için yanındaki "
        "histogram kartını kullanın.\n"
        "\n"
        "Yorum: Uzun çubuk yüksek başarıyı gösterir; bu listede kısa çubuklar öncelikli müdahale "
        "adaylarıdır. Gösterge adları 20 karakterde kesilir."
    ),

    "k_rapor_pg_dagilim.en_dusuk_performansli_pg_ler": (
        "En düşük başarılı göstergeleri hedef ve gerçekleşen değerleriyle tablo halinde listeler.\n"
        "\n"
        "Hesap: Her göstergenin son ölçümünden başarı yüzdesi hesaplanır, artan sıralanır ve "
        "ilk 30 gösterilir.\n"
        "\n"
        "Sınır: Ölçümü girilmemiş göstergeler bu listede ÇIKMAZ — sorun görünmediği için yok "
        "sanılmamalıdır. Boş göstergeler Veri Durumu sekmesindedir.\n"
        "\n"
        "Yorum: Hedef ve gerçekleşen sütunlarını birlikte okuyun; düşük yüzde bazen performans "
        "sorunu değil, gerçekçi olmayan hedef anlamına gelir."
    ),

    # ─────────────────────────── STRATEJİ KAPSAMA ───────────────────────────

    "k_rapor_strateji_kapsama.strateji_kapsama_durumu": (
        "Stratejilerin süreçlerle kapsanma durumunu üç kategoride özetler.\n"
        "\n"
        "Kategoriler:\n"
        "- Tam kapsamlı: tüm alt stratejilere en az bir süreç bağlanmış\n"
        "- Kısmi: bazı alt stratejiler boş kalmış\n"
        "- Boş: hiçbir süreç bağlanmamış\n"
        "\n"
        "Yorum: 'Boş' stratejiler kâğıt üstünde kalmış niyetlerdir — kurum onları hayata "
        "geçirecek hiçbir süreç tanımlamamıştır. Bu, strateji belgesi ile operasyon arasındaki "
        "en büyük kopukluk göstergesidir."
    ),

    "k_rapor_strateji_kapsama.strateji_bazli_kapsama_tablosu": (
        "Her strateji için alt strateji sayısını, bağlı süreç sayısını ve boş alt stratejileri "
        "tablo halinde gösterir.\n"
        "\n"
        "Sınır: 'Bağlı Süreç Sayısı' alt stratejilerin süreç sayılarının toplamıdır. Bir süreç "
        "iki farklı alt stratejiye bağlıysa İKİ KEZ sayılır — bu sayı benzersiz süreç sayısı "
        "değildir.\n"
        "\n"
        "Yorum: 'Boş Alt Strateji' sütunu en eyleme dönük bilgidir; sıfırdan büyük her değer, "
        "tanımlanmış ama karşılığı olmayan bir hedefi işaret eder."
    ),

    "k_rapor_strateji_kapsama.stratejisiz_surecler": (
        "Hiçbir stratejiye bağlanmamış süreçleri listeler.\n"
        "\n"
        "Hesap: Tüm aktif süreçlerden, herhangi bir alt stratejiye bağlı olanlar çıkarılır.\n"
        "\n"
        "Yorum: Bu liste kaynak tüketen ama stratejik yönü belirsiz faaliyetleri gösterir. "
        "İki olasılık vardır: ya süreç gerçekten stratejiyle ilgisizdir (sorgulanmalı), ya da "
        "bağlantısı kurulmamıştır (eksik veri). İkisi de düzeltme gerektirir.\n"
        "\n"
        "Not: Liste boşsa tüm süreçler stratejilere bağlı demektir."
    ),

    # ─────────────────────────── RİSK ───────────────────────────

    "k_rapor_risk.risk_tablosu_rpn_sirali": (
        "Riskleri RPN (Risk Öncelik Sayısı) değerine göre sıralı listeler.\n"
        "\n"
        "Hesap: RPN, olasılık ve etki değerlerinin çarpımıdır. Tablo en yüksek RPN'den başlar, "
        "en fazla 50 kayıt gösterilir.\n"
        "\n"
        "Eşik: RPN 15 ve üzeri kritik, 8-15 yüksek, 4-8 orta, altı düşük.\n"
        "\n"
        "Sınır: RPN değeri kayıttan okunur, bu ekranda yeniden hesaplanmaz — olasılık × etki ile "
        "tutarlılığı doğrulanmaz. Ayrıca yıl filtresi yoktur; tüm aktif riskler listelenir.\n"
        "\n"
        "Yorum: RPN sıralaması müdahale sırası için başlangıç noktasıdır, tek ölçüt değildir. "
        "Düşük RPN'li ama kurumu tek seferde durdurabilecek bir risk, yüksek RPN'li kronik bir "
        "riskten önce ele alınabilir."
    ),

    "k_rapor_risk.darbogaz_gecmisi": (
        "Kaydedilen darboğazları tetiklenme ve çözülme tarihleriyle listeler.\n"
        "\n"
        "Hesap: En son tetiklenenden başlayarak en fazla 20 kayıt gösterilir. Çözülme sütunu "
        "boşsa darboğaz hâlâ açıktır.\n"
        "\n"
        "Yorum: Tetiklenme ile çözülme arasındaki süre, kurumun kısıtlara tepki hızını gösterir. "
        "Aynı sürecin tekrar tekrar darboğaz olması, kök nedene inilmediğine işaret eder — "
        "semptom her seferinde çözülüyor ama kaynak duruyordur."
    ),

    "k_rapor_risk.surec_olgunluk_seviyeleri": (
        "Süreçlerin olgunluk seviyelerini beş noktalı göstergeyle listeler.\n"
        "\n"
        "Seviyeler: 1 Başlangıç, 2 Yönetilen, 3 Tanımlı, 4 Sayısal Yönetilen, 5 Optimize.\n"
        "\n"
        "Sınır: Bir süreç birden fazla boyutta (örneğin Süreç, İnsan, Teknoloji) değerlendirilmişse "
        "listede AYNI SÜREÇ BİRDEN ÇOK KEZ, farklı seviyelerle görünür ve hangi boyut olduğu "
        "ekranda belirtilmez.\n"
        "\n"
        "Yorum: Seviye 3, süreçlerin kişilere değil kuruma ait olduğu eşiktir.\n"
        "\n"
        "Kaynak: CMMI, Software Engineering Institute (Carnegie Mellon Üniversitesi)."
    ),

    # ─────────────────────────── UYARI ───────────────────────────

    "k_rapor_uyari.kritik_performans_gostergeleri": (
        "Hedefinin belirgin biçimde altında kalan göstergeleri listeler.\n"
        "\n"
        "Eşik: Başarı yüzdesi 50'nin altındaki göstergeler kritik sayılır. En düşükten başlayarak "
        "ilk 20 gösterilir; üstteki sayaç toplam sayıyı verir.\n"
        "\n"
        "Sınır: Ölçümü girilmemiş veya hedefi tanımsız göstergeler bu listede ÇIKMAZ. Liste boş "
        "olması 'sorun yok' demek değildir — hiç ölçüm yapılmamış da olabilir.\n"
        "\n"
        "Yorum: Bu kart günlük müdahale listesidir. Hedef ve gerçekleşen değerleri birlikte "
        "okuyun; bazı düşük yüzdeler hatalı hedef tanımından kaynaklanır."
    ),

    "k_rapor_uyari.geciken_faaliyetler": (
        "Bitiş tarihi geçmiş ve hâlâ tamamlanmamış faaliyetleri gecikme süresiyle listeler.\n"
        "\n"
        "Hesap: Gecikme günü = bugün − bitiş tarihi. En çok gecikenden başlayarak ilk 20 "
        "gösterilir.\n"
        "\n"
        "Sınır: Bitiş tarihi GİRİLMEMİŞ faaliyetler bu listede hiç görünmez — tarihsiz bir "
        "faaliyet ne kadar beklerse beklesin gecikmiş sayılmaz. Ayrıca yıl filtresi yoktur; "
        "geçmiş yılların açık faaliyetleri de listeye girer.\n"
        "\n"
        "Yorum: Uzun süredir geciken faaliyetler genellikle terk edilmiş işlerdir; kapatılmaları "
        "ya da yeniden planlanmaları listenin güvenilirliğini artırır."
    ),

    "k_rapor_uyari.yuksek_riskler": (
        "Yüksek öncelikli riskleri RPN sırasıyla listeler.\n"
        "\n"
        "Eşik: RPN değeri 10'un üzerindeki riskler bu listeye girer. En fazla 15 kayıt gösterilir.\n"
        "\n"
        "Not: Bu eşik (10) diğer risk ekranlarındakinden farklıdır — risk tablosunda 15 ve üzeri "
        "kritik sayılır. Aynı risk iki ekranda farklı vurguyla görünebilir.\n"
        "\n"
        "Yorum: Yüksek riskler için sadece izleme yetmez; her birinin bir sahibi ve azaltma "
        "planı olmalıdır."
    ),

    # ─────────────────────────── ANOMALİ ───────────────────────────

    "k_rapor_anomalies.tarama_filtreleri": (
        "Anomali taramasının duyarlılığını ve bildirim ayarlarını belirler.\n"
        "\n"
        "Z-Score eşiği: Bir ölçümün kendi geçmiş ortalamasından kaç standart sapma uzakta "
        "olduğunu belirler. 2,0σ normal dağılımda verinin yaklaşık %95'inin dışını, 3,0σ ise "
        "%99,7'sinin dışını işaret eder. Eşik düşürüldükçe daha çok sonuç gelir.\n"
        "\n"
        "Sınır: Slack'e gönderim, ekranda seçtiğiniz eşiği DEĞİL sabit 2,0σ taramasını kullanır. "
        "Ekranda 3,0σ seçili olsa bile gönderilen liste 2,0σ ile üretilir.\n"
        "\n"
        "Yorum: Normal dağılım varsayımı yapılır ancak verinizin bu dağılıma uyup uymadığı test "
        "edilmez. Mevsimsel dalgalanan göstergelerde beklenen değişimler anomali olarak "
        "işaretlenebilir."
    ),

    "k_rapor_anomalies.ozet": (
        "Bulunan anomalileri önem derecesine göre sayar.\n"
        "\n"
        "Eşik: Önem derecesi seçtiğiniz taramadan BAĞIMSIZDIR ve sabittir — sapma 3,0σ ve üzeri "
        "yüksek, 2,0-3,0σ arası orta, altı düşük sayılır.\n"
        "\n"
        "Yorum: 1,5σ ile tarama yaptığınızda gelen sonuçların tamamı 'düşük' etiketli olur, "
        "çünkü hiçbiri 2,0σ eşiğini geçmemiştir. Bu bir hata değil, iki farklı eşiğin bir arada "
        "çalışmasının sonucudur."
    ),

    "k_rapor_anomalies.anomali_listesi": (
        "Tespit edilen her anomalinin son değerini, tarihsel ortalamasını ve sapma büyüklüğünü "
        "gösterir.\n"
        "\n"
        "Hesap: Z-Score = (son değer − tarihsel ortalama) / standart sapma. Ok yönü sapmanın "
        "yukarı mı aşağı mı olduğunu gösterir.\n"
        "\n"
        "Sınır: Son değer, karşılaştırıldığı ortalamanın İÇİNDE de sayılır. Az sayıda ölçümü olan "
        "göstergelerde bu, sapmayı olduğundan küçük gösterir.\n"
        "\n"
        "Sınır 2: Sapmanın iyi mi kötü mü yönde olduğu bu ekranda belirtilmez. Hedefe yaklaşan "
        "bir sıçrama da, uzaklaşan bir düşüş de aynı biçimde 'anomali' olarak listelenir — "
        "gösterge yönünü kendiniz değerlendirin.\n"
        "\n"
        "Yorum: Anomali bir hata değil, açıklanması gereken bir değişimdir. Kaynağı veri giriş "
        "hatası da olabilir, gerçek bir performans sıçraması da."
    ),

    "k_rapor_anomalies.bos_durum": (
        "Hiç anomali bulunamadığında gösterilen bilgi alanıdır.\n"
        "\n"
        "Sınır — ÖNEMLİ: 'Anomali bulunamadı' mesajı verinin sağlıklı olduğu anlamına GELMEZ. "
        "Aynı sonuç şu durumlarda da çıkar:\n"
        "- Hiçbir göstergede yeterli ölçüm geçmişi yok (en az 5 ölçüm gerekir)\n"
        "- Tüm değerler birbirinin aynı (standart sapma sıfır, sapma hesaplanamaz)\n"
        "- Değerler sayısal biçimde girilmemiş (virgüllü veya metin içeren kayıtlar taranmaz)\n"
        "\n"
        "Yorum: Bu mesajı görüyorsanız önce Veri Durumu sekmesinden ölçüm yoğunluğunuzu kontrol "
        "edin. Beş ölçümün altındaki göstergeler taramaya hiç girmez ve bu ekranda belirtilmez."
    ),

    # ─────────────────────────── FAALİYET ───────────────────────────

    "k_rapor_faaliyet.aylik_tamamlanan": (
        "Yıl boyunca aylara göre tamamlanan faaliyet takip kayıtlarını gösterir.\n"
        "\n"
        "Sınır: Bu grafik faaliyetleri değil, FAALİYET TAKİP KAYITLARINI sayar. Bir faaliyet "
        "birden çok ay 'tamamlandı' işaretlenmişse her ay ayrı sayılır. Bu nedenle çubukların "
        "toplamı, üstteki 'Tamamlanan' sayacıyla tutmaz — ikisi farklı şeyleri ölçer.\n"
        "\n"
        "Yorum: Grafiği aylık iş yoğunluğunun ritmi olarak okuyun. Yıl sonuna yığılma, "
        "planlamanın gerçekçi olmadığına veya kayıtların toplu girildiğine işaret eder."
    ),

    "k_rapor_faaliyet.geciken_faaliyetler": (
        "Bitiş tarihi geçmiş ve tamamlanmamış faaliyetleri listeler.\n"
        "\n"
        "Hesap: Bitiş tarihi bugünden önce olan, durumu 'Tamamlandı' veya 'İptal' olmayan "
        "faaliyetler; en yakın tarihten başlayarak ilk 20.\n"
        "\n"
        "Sınır: Bu sekmedeki faaliyet sayaçlarında YIL FİLTRESİ YOKTUR — gösterilen toplam, "
        "tamamlanan ve geciken sayıları tüm zamanların rakamıdır. Yıl seçimini değiştirmek bu "
        "sayıları değiştirmez.\n"
        "\n"
        "Yorum: Gecikme süresini görmek için Uyarı sekmesindeki geciken faaliyetler kartını "
        "kullanın; orada gün bazlı gecikme hesaplanır."
    ),

    "k_rapor_faaliyet.proje_portfoy_durumu": (
        "Plan projelerinin durumunu ve ilerleme yüzdelerini listeler.\n"
        "\n"
        "Hesap: İlerleme yüzdesine göre azalan sıralı, ilk 15 proje. Geciken proje, bitiş tarihi "
        "geçmiş ve tamamlanmamış olandır.\n"
        "\n"
        "Sınır: Seçili yıl için plan yılı tanımlı değilse kart sessizce boş görünür — hata mesajı "
        "verilmez. Proje yoksa üstteki rozetler hiç doldurulmaz.\n"
        "\n"
        "Yorum: İlerleme yüzdesi kullanıcı beyanıdır, kazanılmış değer hesabı değildir. Gerçek "
        "maliyet ve zaman performansı için EVM sekmesini kullanın."
    ),

    # ─────────────────────────── SORUMLU ANALİZ ───────────────────────────

    "k_rapor_sorumlu_analiz.kisi_basina_faaliyet_yuku": (
        "Kişilere atanmış faaliyetleri durum kırılımıyla karşılaştırır.\n"
        "\n"
        "Hesap: Toplam faaliyet sayısına göre ilk 12 kişi gösterilir; çubuklar tamamlanan, devam "
        "eden ve geciken olarak yığılır.\n"
        "\n"
        "Sınır: Seriler birbirini dışlamaz. 'Devam ediyor' durumundaki bir faaliyet aynı zamanda "
        "gecikmiş olabilir ve İKİ SERİDE birden sayılır. Ayrıca 'Planlandı' ve 'İptal' durumları "
        "hiçbir seride yer almaz. Bu nedenle çubuk toplamı gerçek faaliyet sayısından büyük veya "
        "küçük olabilir.\n"
        "\n"
        "Yorum: Yük dağılımındaki aşırı dengesizlik, hem darboğaz hem de tükenmişlik riskidir."
    ),

    "k_rapor_sorumlu_analiz.en_cok_geciken_kisiler": (
        "En çok geciken faaliyeti bulunan kişileri sıralar.\n"
        "\n"
        "Hesap: Geciken faaliyet SAYISINA göre azalan sıralı, ilk 8 kişi.\n"
        "\n"
        "Sınır: Sıralama mutlak sayıya dayanır, orana değil. Çok sayıda faaliyeti olan kişi "
        "doğal olarak öne çıkar — 50 faaliyetin 5'i geciken kişi, 5 faaliyetin 4'ü geciken "
        "kişiden önce listelenir. Oransal bakış için detay tablosundaki gecikme yüzdesini "
        "kullanın.\n"
        "\n"
        "Yorum: Bu kartı performans değerlendirme aracı olarak kullanmadan önce iş yükü "
        "dağılımına bakın; gecikme çoğu zaman kapasite sorunudur."
    ),

    "k_rapor_sorumlu_analiz.sorumlu_detay_tablosu": (
        "Her kişi için faaliyet sayılarını, tamamlanma ve gecikme oranlarını gösterir.\n"
        "\n"
        "Hesap: Tamamlanma oranı = tamamlanan / toplam. Gecikme oranı = geciken / toplam. "
        "Gecikme oranı %20'nin üzerindeyse kırmızı gösterilir.\n"
        "\n"
        "Sınır: 'Tamamlanma %' ZAMANINDA tamamlamayı ölçmez — geç biten faaliyet de başarı "
        "sayılır ve oranı yükseltir. Ayrıca tablo yalnızca kendisine faaliyet ATANMIŞ kişileri "
        "içerir; hiç ataması olmayan kullanıcılar listede görünmez.\n"
        "\n"
        "Yorum: Tamamlanma ve gecikme oranlarını birlikte okuyun; yüksek tamamlanma ile yüksek "
        "gecikme bir arada olabilir — iş bitiyor ama geç bitiyordur."
    ),

    # ─────────────────────────── DENETİM ───────────────────────────

    "k_rapor_denetim.son_islemler": (
        "Sistemde yapılan son işlemleri kullanıcı, işlem türü ve tarihle listeler.\n"
        "\n"
        "Kapsam: Seçilen gün aralığındaki kayıtlar, en yeniden başlayarak EN FAZLA 200 işlem.\n"
        "\n"
        "Sınır: 200 kayıt sınırı bu sekmedeki tüm kartları etkiler. Seçtiğiniz dönemde 200'den "
        "fazla işlem varsa, hem bu liste hem dağılım hem de en aktif kullanıcılar yalnızca en "
        "son 200 işlemi yansıtır. Yoğun kullanımda daha kısa bir gün aralığı seçmek daha doğru "
        "sonuç verir.\n"
        "\n"
        "Yorum: Denetim kaydı, kimin neyi ne zaman değiştirdiğini gösterir; veri tutarsızlığı "
        "araştırmalarında ilk bakılacak yerdir."
    ),

    "k_rapor_denetim.islem_dagilimi": (
        "İşlem türlerinin dağılımını halka grafikle gösterir.\n"
        "\n"
        "Hesap: Son 200 işlem kaydı üzerinde işlem türü sayımı yapılır, en sık görülen 10 tür "
        "gösterilir.\n"
        "\n"
        "Sınır: 10'dan fazla işlem türü varsa kalanlar grafikte yer almaz ve 'diğer' dilimi de "
        "eklenmez — toplam, gerçek işlem sayısından az görünebilir. Ayrıca 200 kayıt sınırı "
        "burada da geçerlidir.\n"
        "\n"
        "Yorum: Silme işlemlerinin payındaki ani artış incelenmeye değerdir."
    ),

    "k_rapor_denetim.en_aktif_kullanicilar": (
        "En çok işlem yapan kullanıcıları sıralar.\n"
        "\n"
        "Hesap: Son 200 işlem kaydında kullanıcı adı sayımı; en fazla 10 kişi gösterilir. "
        "Çubuklar en yüksek değere göre orantılanır.\n"
        "\n"
        "Sınır: Kullanıcı adı denetim kaydına metin olarak yazılır. Bir kullanıcının adı "
        "değiştirilmişse eski kayıtlar ayrı bir satır olarak görünür.\n"
        "\n"
        "Yorum: Yüksek işlem sayısı verimlilik değil, yoğunluk göstergesidir; veri girişinin "
        "tek kişiye bağımlı olduğu durumları ortaya çıkarır."
    ),

    # ─────────────────────────── BİLDİRİM ANALİZ ───────────────────────────

    "k_rapor_bildirim_analiz.bildirim_turu_dagilimi": (
        "Bildirimlerin türlere göre dağılımını gösterir.\n"
        "\n"
        "Hesap: En sık görülen 10 bildirim türü sayılır.\n"
        "\n"
        "Sınır: Bu sekmede tarih veya yıl filtresi yoktur — kurumun TÜM bildirim geçmişi "
        "kapsanır. Tür adları çeviri sözlüğünde yoksa İngilizce görünür.\n"
        "\n"
        "Yorum: Tek bir türün baskın olması bildirim yorgunluğu riskidir; kullanıcılar çok "
        "tekrarlayan bildirimleri okumadan kapatmaya başlar."
    ),

    "k_rapor_bildirim_analiz.son_30_gun_bildirim_trendi": (
        "Son 30 günde oluşan bildirim sayısını günlük olarak gösterir.\n"
        "\n"
        "Hesap: Bugünden geriye 30 gün; bildirim olmayan günler sıfır olarak çizilir.\n"
        "\n"
        "Yorum: Ani sıçramalar genellikle toplu bir olaydan kaynaklanır (hedef güncellemesi, "
        "dönem kapanışı). Sürekli yüksek seyir, bildirim eşiklerinin fazla duyarlı ayarlandığına "
        "işaret edebilir."
    ),

    "k_rapor_bildirim_analiz.okunmayan_bildirimlerin_yaslanmasi": (
        "Okunmamış bildirimleri yaş aralıklarına göre gruplar.\n"
        "\n"
        "Kovalar: 0-3 gün, 4-7 gün, 8-30 gün, 30 günden eski.\n"
        "\n"
        "Sınır: Çubuk uzunlukları görelidir — en kalabalık kova her zaman tam dolu görünür. "
        "Mutlak sayılar için çubuğun yanındaki değeri okuyun. Boş kovalar listeden düşer.\n"
        "\n"
        "Yorum: 30 günü aşan okunmamış bildirim birikmesi, bildirim sisteminin fiilen devre dışı "
        "kaldığını gösterir. Bu durumda bildirim sayısını artırmak değil, azaltıp "
        "önceliklendirmek çözümdür."
    ),

    "k_rapor_bildirim_analiz.en_cok_bildirim_alan_kullanicilar": (
        "En çok bildirim alan kullanıcıları sıralar.\n"
        "\n"
        "Hesap: Kullanıcı bazında bildirim sayımı; en fazla 10 kişi. Çubuklar en yüksek değere "
        "göre orantılanır.\n"
        "\n"
        "Yorum: Aşırı bildirim alan kullanıcılar bildirim yorgunluğunun ilk kurbanlarıdır; "
        "okunma oranlarını ayrıca kontrol edin. Yüksek bildirim + düşük okunma, kritik "
        "uyarıların kaçırıldığı anlamına gelir."
    ),

    # ─────────────────────────── SWOT TREND ───────────────────────────

    "k_rapor_swot_trend.swot_madde_sayisi_trendi": (
        "SWOT analizlerindeki madde sayılarının yıllara göre değişimini gösterir.\n"
        "\n"
        "Hesap: Her yıl için güçlü yön, zayıf yön, fırsat ve tehdit maddelerinin sayımı.\n"
        "\n"
        "Sınır: Bu bir HACİM ölçüsüdür, kalite değil. Madde sayısının artması analizin "
        "derinleştiği anlamına gelmez. Plan yılına bağlanmamış analiz kayıtları grafiğe hiç "
        "girmez.\n"
        "\n"
        "Yorum: Zayıf yön ve tehdit maddelerinin zamanla azalması iyileşme değil, çoğu zaman "
        "analiz disiplininin gevşemesidir — özeleştirinin azaldığı dönemler dikkat ister."
    ),

    "k_rapor_swot_trend.tows_strateji_sayisi_trendi": (
        "TOWS matrisinde üretilen strateji sayılarının yıllara göre değişimini gösterir.\n"
        "\n"
        "Dört tür: SO (güçlü×fırsat), ST (güçlü×tehdit), WO (zayıf×fırsat), WT (zayıf×tehdit).\n"
        "\n"
        "Yorum: Dağılımın kendisi kurumun stratejik duruşunu anlatır. SO ağırlıklı bir kurum "
        "büyümeye, WT ağırlıklı bir kurum savunmaya odaklanmıştır. Yalnızca tek türde strateji "
        "üretiliyorsa analiz muhtemelen eksik yapılmıştır."
    ),

    "k_rapor_swot_trend.yillik_swot_tows_ozet_tablosu": (
        "SWOT ve TOWS madde sayılarını yıl bazında tablo halinde karşılaştırır.\n"
        "\n"
        "Sınır: Bir yılda SWOT yapılmış ama TOWS yapılmamışsa eksik taraf SIFIR olarak gösterilir. "
        "'O yıl hiç strateji üretilmedi' ile 'o yıl analiz hiç yapılmadı' bu tabloda ayırt "
        "edilemez.\n"
        "\n"
        "Yorum: SWOT sayısı yüksek ama TOWS sayısı düşük yıllar, durum tespitinin yapılıp "
        "karşılığında hamle üretilmediği dönemlerdir — analizin en sık yarım kaldığı nokta budur."
    ),

    # ─────────────────────────── STRATEJİK ANALİZ ───────────────────────────

    "k_rapor_stratejik_analiz.swot_analizi": (
        "SWOT analizindeki madde sayılarını dört kadranda özetler.\n"
        "\n"
        "Sınır: Kart yalnızca ADET gösterir, madde içerikleri burada görünmez. Ayrıca seçili "
        "yılın kaydı yoksa EN SON GÜNCELLENEN başka bir yılın kaydı gösterilir — kart "
        "başlığındaki yıl etiketi gerçek kaydın yılıdır, sayfada seçtiğiniz yıl olmayabilir.\n"
        "\n"
        "Yorum: SWOT'un değeri listede değil eşleştirmededir; dört kutuyu doldurup bırakmak "
        "yöntemin en yaygın kötü kullanımıdır. Eşleştirme TOWS matrisinde yapılır.\n"
        "\n"
        "Kaynak: 1960'larda Stanford Research Institute'ta SOFT yöntemi olarak geliştirildi."
    ),

    "k_rapor_stratejik_analiz.tows_matrisi": (
        "TOWS strateji sayılarını dört kombinasyonda özetler: SO, ST, WO, WT.\n"
        "\n"
        "Sınır: Kart adı 'matris' olsa da burada eşleştirme tablosu değil, dört sayaç yer alır. "
        "Strateji içerikleri gösterilmez. Seçili yılın kaydı yoksa başka bir yılın kaydı "
        "gösterilebilir.\n"
        "\n"
        "Yorum: SO saldırgan büyüme, ST savunma, WO iyileştirme, WT kaçınma stratejilerini "
        "temsil eder. SWOT dolu ama TOWS boşsa analiz yarım kalmıştır."
    ),

    "k_rapor_stratejik_analiz.pestel_analizi": (
        "Dış çevre faktörlerini altı boyutta madde sayısıyla gösterir: Politik, Ekonomik, "
        "Sosyal, Teknolojik, Çevresel, Yasal.\n"
        "\n"
        "Sınır: Çubuk uzunluğu madde sayısının beş katıdır ve beş maddede dolar. Beşten fazla "
        "maddesi olan boyutlar birbirinden ayırt edilemez — bu görselleştirme tercihidir, "
        "veride böyle bir üst sınır yoktur.\n"
        "\n"
        "Yorum: PESTEL'in amacı öngörülemeyeni öngörmek değil, kurumu etkileyecek dış değişimleri "
        "sistematik olarak gözden kaçırmamaktır. Boş kalan boyutlar kör noktalardır — özellikle "
        "yasal ve çevresel boyutlar çoğu kurumda ihmal edilir."
    ),

    "k_rapor_stratejik_analiz.porter_5_kuvvet": (
        "Sektör çekiciliğini beş rekabet kuvvetiyle değerlendirir: rekabet yoğunluğu, tedarikçi "
        "gücü, alıcı gücü, yeni giriş tehdidi, ikame tehdidi.\n"
        "\n"
        "ÖNEMLİ — ters yön: Bu kartta YÜKSEK SKOR KÖTÜDÜR. Yüksek değer güçlü bir tehdit veya "
        "baskı anlamına gelir ve kırmızı gösterilir. Diğer tüm kartlarda yüksek skor iyiyken "
        "burada tersidir.\n"
        "\n"
        "Eşik: 4 ve üzeri kırmızı (yüksek tehdit), 3-4 turuncu, altı yeşil. Ölçek 1-5 varsayılır.\n"
        "\n"
        "Yorum: Beş kuvvetin tümü yüksekse sektör kârlılığı yapısal olarak baskı altındadır; "
        "rekabet üstünlüğü operasyonel iyileştirmeyle değil konumlanma değişikliğiyle sağlanır.\n"
        "\n"
        "Kaynak: Michael E. Porter, Harvard Business Review, 1979."
    ),

    # ─────────────────────────── SÜREÇ-PG ISI HARİTASI ───────────────────────────

    "k_rapor_surec_pg.surec_donem_isi_haritasi": (
        "Süreçlerin dönemsel ölçüm değerlerini ısı haritası olarak gösterir. Satırlar süreç, "
        "sütunlar seçtiğiniz dönem (aylık, çeyreklik veya yıllık).\n"
        "\n"
        "Sınır — ÖNEMLİ: Hücrelerdeki değer HAM ÖLÇÜM ORTALAMASIDIR, başarı yüzdesi değildir. "
        "Hedefle karşılaştırılmaz ve gösterge yönü dikkate alınmaz. Farklı birimlerdeki "
        "göstergeler (TL, adet, gün, yüzde) aynı hücrede ortalanır ve aynı renk skalasıyla "
        "boyanır. Örneğin 'ciro 1.500.000' ile 'memnuniyet %92' aynı ortalamaya girer.\n"
        "\n"
        "Bu nedenle RENGİ PERFORMANS OLARAK OKUMAYIN. Harita, verinin hangi dönemlerde girildiğini "
        "ve büyüklük düzenini görmek için kullanışlıdır.\n"
        "\n"
        "Kapsam: Yalnızca ana süreçler satır olur; göstergesi olmayan süreçler tabloda görünmez. "
        "Süreç adına tıklandığında açılan trend grafiği, o sürecin yalnızca ilk göstergesini "
        "gösterir."
    ),

    # ─────────────────────────── EVM ───────────────────────────

    "k_rapor_evm.kazanilmis_deger_evm_proje_snapshot_tablosu": (
        "Projelerin kazanılmış değer ölçümlerini planlanan değer, kazanılmış değer, fiili maliyet "
        "ve performans endeksleriyle listeler.\n"
        "\n"
        "Göstergeler: SPI = Kazanılmış Değer / Planlanan Değer (zaman). CPI = Kazanılmış Değer / "
        "Fiili Maliyet (maliyet). 1,0 referans noktasıdır; üzeri lehte, altı aleyhtedir.\n"
        "\n"
        "Sınır: Tablo her proje için tek satır GÖSTERMEZ — son 120 ölçüm listelenir ve aynı proje "
        "birden çok kez tekrarlanır. Ayrıca 'Durum' sütunu yalnızca SPI'ye bakar; maliyet "
        "performansı (CPI) durumu etkilemez. Bütçesi patlamış ama zamanında giden bir proje "
        "'Zamanında' görünür.\n"
        "\n"
        "Sınır 2: Geçmiş bir yıl seçildiğinde tablo boş görünebilir — kayıt sınırı yıl "
        "süzmesinden önce uygulanır.\n"
        "\n"
        "Yorum: SPI proje sonuna yaklaştıkça 1,0'a yakınsar ve gecikmeyi gizler; geç aşamalarda "
        "tek başına güvenilmez.\n"
        "\n"
        "Kaynak: PMI / PMBOK Kılavuzu."
    ),

    # ─────────────────────────── BİREYSEL ───────────────────────────

    "k_rapor_bireysel.kullanici_bazli_pg_basari_tablosu": (
        "Kullanıcı bazında bireysel gösterge sayısını, veri giriş durumunu ve ortalama başarıyı "
        "gösterir.\n"
        "\n"
        "Sınır — ÖNEMLİ: Bu tabloda iki farklı 'kullanıcı' tanımı yan yana durur. 'PG Sayısı' ve "
        "'Ort. Başarı' göstergenin SAHİBİNE aittir; 'Toplam Giriş' ve 'Son Giriş' ise VERİYİ "
        "GİREN kişiye aittir. Veriyi başkası giriyorsa (asistan, yönetici) bu iki sütun aynı "
        "kişiyi tarif etmez.\n"
        "\n"
        "Hesap: Ortalama başarı, kişinin göstergelerinin en güncel başarı yüzdelerinin "
        "ortalamasıdır. Bu yüzde kayıttan okunur, bu ekranda yeniden hesaplanmaz.\n"
        "\n"
        "Yorum: 'Veri Girilmiş' oranı düşükken ortalama başarının yüksek olması, ölçümün yalnızca "
        "iyi giden göstergelerde yapıldığına işaret edebilir."
    ),

    "k_rapor_bireysel.bireysel_pg_detay_listesi": (
        "Bireysel göstergeleri kişi, hedef, gerçekleşen ve başarı yüzdesiyle listeler.\n"
        "\n"
        "Kapsam: En fazla 200 gösterge listelenir. Daha fazlası varsa gerisi görünmez ve bu "
        "ekranda belirtilmez — üstteki sağlık sayaçlarıyla tablo satır sayısı bu nedenle "
        "uyuşmayabilir.\n"
        "\n"
        "Sınır: Seçili yıl için bireysel gösterge bulunamazsa yıl filtresi tamamen kaldırılır ve "
        "TÜM yılların göstergeleri listelenir. Ekranda yine seçtiğiniz yıl yazar.\n"
        "\n"
        "Yorum: Değerler her göstergenin en güncel ölçümünden alınır."
    ),

    # ─────────────────────────── KURUM KARŞILAŞTIRMA ───────────────────────────

    "k_rapor_kurum_karsilastirma.kurum_performans_karsilastirmasi": (
        "Kurumların ortalama gösterge başarısını çubuk grafikle karşılaştırır.\n"
        "\n"
        "Yetki: Platform yöneticisi tüm kurumları görür; diğer kullanıcılar yalnızca kendi "
        "kurumunu görür (tek çubuk).\n"
        "\n"
        "Sınır: Ortalaması hesaplanamayan kurum grafikte SIFIR olarak çizilir ama tabloda tire "
        "ile gösterilir. Veri girmemiş bir kurum, grafikte 'sıfır başarılı' gibi görünür.\n"
        "\n"
        "Yorum: Karşılaştırma yapmadan önce kurumların veri giriş oranlarına bakın — az veri "
        "girmiş bir kurum yapay olarak yüksek görünebilir."
    ),

    "k_rapor_kurum_karsilastirma.kurum_detay_tablosu": (
        "Kurumları gösterge sayısı, veri giriş durumu ve başarı dağılımıyla tablo halinde "
        "karşılaştırır.\n"
        "\n"
        "Hesap: Ortalama başarı, hesaplanabilen gösterge yüzdelerinin düz ortalamasıdır. "
        "Hedefte (≥80), riskli (50-80) ve kritik (<50) sütunları bu bantlara göre sayılır.\n"
        "\n"
        "Sınır — ÖNEMLİ: Ortalama, VERİ GİRİLMEMİŞ göstergeleri hiç saymaz. 100 göstergeden "
        "yalnızca 3'üne veri girmiş ve o üçü iyi olan bir kurum tabloda BİRİNCİ SIRADA çıkar. "
        "'PG Sayısı' ve 'Veri Girilen' sütunlarını ortalamayla birlikte okumadan sıralama "
        "yorumlanmamalıdır.\n"
        "\n"
        "Sınır 2: Bu tablo vizyon skorunu kullanmaz — strateji ağırlıkları, süreç hiyerarşisi ve "
        "gösterge ağırlıkları yok sayılır; düz gösterge ortalamasıdır."
    ),

    # ─────────────────────────── PAYDAŞ ───────────────────────────

    "k_rapor_paydas.paydas_haritasi": (
        "Paydaşları rol, etki ve ilgi düzeyleriyle listeler.\n"
        "\n"
        "Sınır: Kart adı 'harita' olsa da burada etki×ilgi matrisi yoktur; iki değer yan yana "
        "gösterilir, kadran ataması yapılmaz. Ölçek 1-10 varsayılır.\n"
        "\n"
        "Yorum — Güç/İlgi matrisiyle yönetim stratejisi:\n"
        "- Yüksek etki + yüksek ilgi: yakın yönetilecek kilit paydaş\n"
        "- Yüksek etki + düşük ilgi: memnun tutulacak\n"
        "- Düşük etki + yüksek ilgi: bilgilendirilecek\n"
        "- Düşük etki + düşük ilgi: izlenecek\n"
        "\n"
        "Kaynak: R. Edward Freeman, Stakeholder Approach, 1984; Güç/İlgi matrisi Johnson & "
        "Scholes, 1993."
    ),

    "k_rapor_paydas.paydas_anket_ozeti": (
        "Paydaş anketlerinin ortalama skorlarını paydaş tipine göre gösterir.\n"
        "\n"
        "Hesap: Anketler paydaş tipine göre gruplanır, skor ortalaması alınır. Görselleştirme "
        "1-5 ölçeği varsayar.\n"
        "\n"
        "Sınır: Anket özetinde YIL FİLTRESİ YOKTUR — paydaş listesi seçili yıla göre süzülürken "
        "anket ortalamaları tüm yılların verisini kapsar. Aynı ekranda iki farklı zaman aralığı "
        "bulunur. Anketiniz 1-10 ölçeğindeyse renkler ve çubuk uzunlukları yanıltıcı olur.\n"
        "\n"
        "Yorum: Anket, paydaş algısını ölçen tek doğrudan kaynaktır. İç göstergeleriniz iyiyken "
        "anket skorları düşükse, ölçtüğünüz şey paydaşın değer verdiği şey değildir."
    ),

    # ─────────────────────────── REKABET ───────────────────────────

    "k_rapor_rekabet.rekabetci_analiz": (
        "Rakiplerle karşılaştırmalı skorları boyut bazında gösterir.\n"
        "\n"
        "Sınır: Skorlar ham gösterilir — fark hesaplanmaz, hangi tarafın önde olduğu renkle "
        "vurgulanmaz. Renkler sabittir ve üstünlüğü göstermez; iki sayıyı kendiniz "
        "karşılaştırmanız gerekir.\n"
        "\n"
        "Yorum: Rakip önde çıkan boyutlarda önce ölçüm tanımlarının aynı olduğundan emin olun. "
        "Fark gerçekse, rakibin uygulamasının kuruma transfer edilebilirliğini değerlendirin — "
        "her üstünlük taklit edilebilir değildir."
    ),

    "k_rapor_rekabet.a3_raporlari": (
        "A3 problem çözme raporlarını problem tanımı ve karşı önlemleriyle listeler.\n"
        "\n"
        "Kapsam: En son oluşturulandan başlayarak en fazla 20 rapor. Yıl filtresi yoktur.\n"
        "\n"
        "Sınır: Tabloda A3'ün yalnızca iki bölümü görünür (problem ve karşı önlem) ve metinler "
        "kesilir. Kök neden analizi, mevcut durum, hedef ve takip bölümleri bu ekranda yer almaz.\n"
        "\n"
        "Yorum: A3 bir rapor formatından çok bir düşünme disiplinidir; problem tek sayfada "
        "anlatılamıyorsa henüz yeterince anlaşılmamıştır.\n"
        "\n"
        "Kaynak: Toyota; PDCA döngüsü ile problem çözme pratiğinin birleşimi."
    ),

    # ─────────────────────────── VERİ DURUMU ───────────────────────────

    "k_rapor_veri_durumu.veri_girilen_pg_ler": (
        "Seçili yıl için en az bir ölçüm girilmiş göstergeleri, son değer ve giren kişiyle "
        "birlikte listeler.\n"
        "\n"
        "Sınır: Tablo en fazla 50 satır gösterir; üstteki sayaç ise tam sayıyı verir. Sayaç 180 "
        "derken tabloda 50 satır görmeniz normaldir — tam listeyi Excel dışa aktarımıyla "
        "alabilirsiniz.\n"
        "\n"
        "Sınır 2: 'Veri girilmiş' ölçütü o yıl EN AZ BİR satır demektir. Yılın on iki ayından "
        "yalnızca Ocak'ı girilmiş bir gösterge de bu listede yer alır. Kart güncellik veya "
        "tamlık ölçmez.\n"
        "\n"
        "Yorum: 'Giren' sütunu veri girişinin kime bağımlı olduğunu gösterir; tek kişiye "
        "yığılmışsa süreklilik riski vardır."
    ),

    "k_rapor_veri_durumu.veri_girilmeyen_pg_ler": (
        "Seçili yıl için hiç ölçüm girilmemiş göstergeleri listeler.\n"
        "\n"
        "Sınır: Tablo en fazla 50 satır gösterir; gerçek sayı üstteki 'Eksik' sayacındadır. Tam "
        "liste için Excel dışa aktarımını kullanın.\n"
        "\n"
        "Yorum: Bu liste tüm rapor katmanının güvenilirlik ölçüsüdür. Buradaki göstergeler hiçbir "
        "skora, ortalamaya veya kritik listesine girmez — yani sistemde görünmezler. Skorların "
        "yüksek çıkması, buradaki listenin kısa olmasıyla anlam kazanır. Uzun bir liste, "
        "gördüğünüz tüm skorların kurumun küçük bir kesitini temsil ettiği anlamına gelir."
    ),

    # ─────────────────────────── STRATEJİK UYUM ───────────────────────────

    "k_rapor_uyum.strateji_surec_katki_agaci": (
        "Strateji → alt strateji → süreç hiyerarşisini skorlarıyla birlikte katlanabilir ağaç "
        "olarak gösterir.\n"
        "\n"
        "Hesap: Her düğümdeki skor, vizyon skoru zincirindeki ilgili seviyenin değeridir. "
        "Renkler 80 ve üzeri yeşil, 50-80 sarı, altı kırmızı bandını izler.\n"
        "\n"
        "Sınır: Kart adı 'uyum' olsa da burada bir uyum veya hizalanma ORANI hesaplanmaz; ağaç, "
        "aynı skorların hiyerarşik gösterimidir. Gerçek kapsama analizi (boş strateji, "
        "stratejisiz süreç) Strateji Kapsama sekmesindedir.\n"
        "\n"
        "Sınır 2: Bir süreç birden çok alt stratejiye bağlıysa ağaçta birden çok yerde görünür "
        "ve skoru her dalda ayrı sayılır.\n"
        "\n"
        "Yorum: Ağacı yukarıdan aşağıya izleyerek düşük bir strateji skorunun hangi süreçten "
        "kaynaklandığını bulabilirsiniz — kök nedene inmenin en hızlı yolu budur."
    ),

    # ─────────────────────────── AKTİVİTE TAKVİMİ ───────────────────────────

    "k_rapor_aktivite_takvim.gunluk_veri_giris_aktivitesi": (
        "Yıl boyunca hangi günlerde ölçüm verisi girildiğini takvim haritasıyla gösterir.\n"
        "\n"
        "Sınır — ÖNEMLİ: Renk yoğunluğu GÖRELİDİR; o yılın en yoğun günü en koyu renk olur. "
        "Üç girişin olduğu bir yılda 3 giriş koyu, üç yüz girişli bir yılda 3 giriş açık "
        "görünür. Yıllar arasında karşılaştırma yapılamaz.\n"
        "\n"
        "Sınır 2: Günler ölçümün AİT OLDUĞU tarihe göre yerleştirilir, girişin yapıldığı tarihe "
        "göre değil. Ocak ayına ait 50 ölçüm Mart'ta girildiyse harita Ocak'ı işaretler. Bu "
        "nedenle kart 'kullanıcı ne zaman çalıştı' sorusunu yanıtlamaz.\n"
        "\n"
        "Sınır 3: Yalnızca gösterge ölçümleri sayılır; faaliyet ve görev hareketleri bu takvime "
        "girmez.\n"
        "\n"
        "Yorum: Dönem sonlarına yığılan girişler, ölçümün düzenli izleme yerine raporlama "
        "zorunluluğu olarak yapıldığını gösterir."
    ),

    "k_rapor_aktivite_takvim.son_30_gun_trend": (
        "Son 30 gündeki günlük veri giriş sayısını çizgi grafikle gösterir.\n"
        "\n"
        "Sınır: Grafik yalnızca SEÇİLİ YILIN verisini içerir. Ocak ayında bakıldığında son 30 "
        "günün büyük kısmı önceki yıla düşer ve veri olsa bile sıfır çizilir. Geçmiş bir yıl "
        "seçiliyse grafik tamamen sıfır çizgisi olur.\n"
        "\n"
        "Yorum: Düzenli veri girişi, göstergelerin karar için kullanılabilir kalmasının ön "
        "koşuludur. Uzun boşluklardan sonra gelen toplu girişler, o dönemin verisinin geriye "
        "dönük hatırlamayla doldurulduğu anlamına gelebilir."
    ),
}
