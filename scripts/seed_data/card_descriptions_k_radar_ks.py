# -*- coding: utf-8 -*-
"""K-Radar KS (Kurumsal Strateji) kart açıklamaları.

Yazım sözleşmesi için bkz. card_descriptions_k_radar.py başlığı.

ÖNEMLİ — SWOT kökeni: Yaygın "Albert Humphrey / Stanford Research Institute"
atfı akademik olarak DOĞRULANAMAMIŞTIR (Puyt, Lie & Wilderom, "The origins of
SWOT analysis", Long Range Planning, 2023 — yöntemin 1960'larda SRI'da SOFT
olarak doğduğunu ve Robert Franklin Stewart tarafından yönetildiğini gösterir).
Bu yüzden metinlerde Humphrey adı KULLANILMAZ.

ÖNEMLİ — KS türetilmiş kartlar: pestle/tows/okr/bsc/efqm/hoshin/ansoff/bcg
özet kartları ilgili analiz tablolarını OKUMAZ; strateji/süreç/gösterge
sayılarından aritmetik türetir. Bu kartlarda "Sınır:" bölümü zorunludur.
Gerçek veri karşılıkları ayrı endpoint'lerdedir (get_ks_*_real).
"""

DESCRIPTIONS: dict[str, str] = {

    # ─────────────────────────── KS TEMEL SKORLAR ───────────────────────────

    "k_radar_ks.ks_skoru": (
        "Kurumsal Strateji (KS) skoru, stratejilerinizin süreçlerle ne ölçüde karşılandığını "
        "0-100 ölçeğinde özetler.\n"
        "\n"
        "Hesap: Aktif süreç sayısının aktif strateji sayısına oranıdır (en fazla 100). "
        "Yani her stratejiye karşılık kaç süreç tanımlandığını ölçer.\n"
        "\n"
        "Sınır: Bu bir SAYIM oranıdır — hangi sürecin hangi stratejiye bağlandığı kontrol "
        "edilmez. Süreçler stratejilere fiilen bağlanmamış olsa bile skor yüksek çıkabilir. "
        "Gerçek bağlantı durumu için 'Strateji Kapsamı' kartına bakın.\n"
        "\n"
        "Yorum: 80 ve üzeri yeşil, 60-80 sarı, altı kırmızı banttır. Skor 60'ın altındaysa "
        "sistem strateji-süreç hizalaması önerisi üretir.\n"
        "\n"
        "Not: Kart değerleri 5 dakika önbelleklenir; yeni veri girildikten hemen sonra değişmeyebilir."
    ),

    "k_radar_ks.strateji_kapsami": (
        "Stratejilerin süreçlerle ne ölçüde kapsandığını yüzde olarak gösterir. KS skorundan farkı, "
        "burada gerçek bağlantı kayıtlarının okunmasıdır.\n"
        "\n"
        "Hesap: Bir alt stratejiye fiilen bağlanmış süreçlerin toplam aktif sürece oranıdır. "
        "Bağlantı, süreç-alt strateji ilişki kayıtlarından okunur.\n"
        "\n"
        "Yorum: Düşük kapsama, stratejinin sahada karşılığı olmadığını gösterir — strateji yazılmış "
        "ama onu hayata geçirecek süreç tanımlanmamıştır. Kapsanmayan süreçler ise stratejiye "
        "bağlanmamış, yönü belirsiz iş yükünü işaret eder.\n"
        "\n"
        "Sınır: Seçili plan yılında strateji bulunmazsa, yıl bilgisi girilmemiş eski kayıtlar da "
        "listeye dahil edilir. Bu nedenle yıl değiştirmek bazı kayıtlarda sonucu değiştirmez."
    ),

    "k_radar_ks.toplam_strateji": (
        "Kurumda tanımlı ana strateji ve alt strateji sayısını gösterir.\n"
        "\n"
        "Hesap: Aktif (silinmemiş) strateji kayıtlarının sayımıdır.\n"
        "\n"
        "Yorum: Strateji sayısı tek başına başarı göstergesi değildir. Çok sayıda strateji, odak "
        "dağılmasına işaret edebilir; az sayıda strateji ise kurumun tüm faaliyet alanlarını "
        "kapsamıyor olabilir. Bu sayıyı 'Strateji Kapsamı' ile birlikte okuyun — kapsanmayan "
        "strateji, kâğıt üstünde kalmış demektir."
    ),

    "k_radar_ks.genel_pg_basarisi": (
        "Tüm performans göstergelerinin hedefe ulaşma ortalamasını gösterir.\n"
        "\n"
        "Hesap: Her göstergenin en son ölçümü alınır, gerçekleşen değerin hedefe oranı hesaplanır "
        "ve gösterge ağırlıklarıyla ortalanır.\n"
        "\n"
        "Sınır: Verisi girilmemiş göstergeler hesaba KATILMAZ — ortalamayı düşürmezler. Bu nedenle "
        "az sayıda göstergeye veri girilmişse ortalama yanıltıcı derecede yüksek olabilir. Kaç "
        "göstergenin fiilen hesaba girdiğini 'Hesaplanan PG' kartından teyit edin.\n"
        "\n"
        "Yorum: Hiç veri yoksa skor 0 ve bant kırmızı görünür — bu 'performans kötü' değil, "
        "'ölçüm yok' anlamına gelir. İki durum görsel olarak aynıdır."
    ),

    # ─────────────────────────── KS ANALİZ ARAÇLARI ───────────────────────────

    "k_radar_ks.swot_analizi": (
        "SWOT, kurumun içsel Güçlü/Zayıf yönleri ile dışsal Fırsat/Tehditlerini tek çerçevede "
        "karşılaştırarak strateji üretme aracıdır.\n"
        "\n"
        "Hesap: Dört kategoriye girilen maddelerin sayımı ve listesidir; türetilmiş bir skor yoktur.\n"
        "\n"
        "Sınır: Seçili yılın kaydı yoksa veya boşsa, en son güncellenen BAŞKA bir yılın kaydı "
        "gösterilir. Ekranda 2026 seçiliyken 2024 verisi görüyor olabilirsiniz — kartta belirtilen "
        "yıl, gösterilen kaydın gerçek yılıdır.\n"
        "\n"
        "Yorum: SWOT'un değeri listede değil EŞLEŞTİRMEDEDİR: güçlü yön × fırsat = büyüme hamlesi; "
        "zayıf yön × tehdit = savunma önceliği. Dört kutuyu doldurup bırakmak yöntemin en yaygın "
        "kötü kullanımıdır — TOWS matrisi bu eşleştirmeyi yapar.\n"
        "\n"
        "Kaynak: 1960'larda Stanford Research Institute'ta SOFT yöntemi olarak geliştirildi; "
        "kavramsal kökleri Harvard Business School politika geleneğine bağlanır."
    ),

    "k_radar_ks.tows_matrisi": (
        "TOWS matrisi, SWOT bulgularını eşleştirerek somut strateji seçenekleri üretir. SWOT "
        "durumu betimler, TOWS ondan aksiyon çıkarır.\n"
        "\n"
        "Dört kombinasyon:\n"
        "- SO (Güçlü × Fırsat): saldırgan büyüme — güçlü yönle fırsatı yakala\n"
        "- ST (Güçlü × Tehdit): savunma — güçlü yönle tehdidi karşıla\n"
        "- WO (Zayıf × Fırsat): iyileştirme — fırsatı kaçırmamak için zayıflığı gider\n"
        "- WT (Zayıf × Tehdit): kaçınma — hasarı sınırla, riskten uzaklaş\n"
        "\n"
        "Hesap: Girilen strateji maddelerinin dört kadrandaki sayımı ve listesidir.\n"
        "\n"
        "Yorum: SWOT dolu ama TOWS boşsa analiz yarım kalmıştır — durum tespiti yapılmış, "
        "karşılığında hamle üretilmemiştir."
    ),

    "k_radar_ks.pestle_analizi": (
        "PESTLE, kurumun kontrolü dışındaki dış çevre faktörlerini altı başlıkta tarar: Politik, "
        "Ekonomik, Sosyal, Teknolojik, Yasal, Çevresel.\n"
        "\n"
        "Sınır: Bu ÖZET kartı gerçek PESTLE kayıtlarınızı okumaz — faktör sayısı sabit 6'dır ve "
        "kapsam skoru strateji ile süreç sayınızdan türetilir. Girdiğiniz PESTLE maddelerini "
        "görmek için Stratejik Analiz raporundaki PESTEL kartını kullanın.\n"
        "\n"
        "Yorum: PESTLE'ın amacı öngörülemeyeni öngörülebilir kılmak değil, kurumu etkileyecek dış "
        "değişimleri sistematik olarak gözden kaçırmamaktır. SWOT'un 'Fırsat' ve 'Tehdit' "
        "kutularının beslendiği ana kaynaktır."
    ),

    "k_radar_ks.okr": (
        "OKR (Objectives and Key Results), niteliksel bir hedefi ölçülebilir anahtar sonuçlara "
        "bağlayan hedef yönetimi yöntemidir.\n"
        "\n"
        "Sınır: Bu kart ayrı bir OKR kaydı okumaz. Hedef sayısı olarak strateji sayınız, hizalama "
        "skoru olarak KS skorunuz gösterilir. Yani gerçek bir OKR çeyrek döngüsü takibi değil, "
        "mevcut strateji yapınızın OKR merceğinden görünümüdür.\n"
        "\n"
        "Yorum: OKR'de hedef ilham verici ve niteliksel, anahtar sonuçlar ise sayısal ve zaman "
        "sınırlı olmalıdır. Hizalama, alt seviye anahtar sonuçların üst hedefe gerçekten hizmet "
        "etmesi demektir — hizalama düşükse ekipler meşguldür ama aynı yöne çekmiyordur."
    ),

    "k_radar_ks.bsc": (
        "Balanced Scorecard (Kurumsal Karne), performansı yalnızca finansal ölçütlerle değil, "
        "birbirini besleyen dört boyutla ölçer: Finansal, Müşteri, İçsel İş Süreçleri, "
        "Yenilik ve Öğrenme.\n"
        "\n"
        "Sınır: Bu kart göstergelerinizi dört boyuta göre SINIFLANDIRMAZ. Perspektif kapsamı, "
        "gösterge sayınızdan türetilmiş yaklaşık bir değerdir. Gerçek boyut dağılımı için "
        "göstergelerin perspektif ataması yapılmalıdır.\n"
        "\n"
        "Yorum: Kaplan ve Norton'un tezi, ROI gibi finansal ölçütlerin GEÇMİŞİ raporladığı; "
        "geleceği ise müşteri, süreç ve öğrenme boyutlarının haber verdiğidir. Bir boyutta hiç "
        "ölçüm yoksa strateji o kanattan kördür.\n"
        "\n"
        "Kaynak: Robert S. Kaplan & David P. Norton, Harvard Business Review, Ocak-Şubat 1992."
    ),

    "k_radar_ks.efqm": (
        "EFQM Mükemmellik Modeli, kurumsal olgunluğu yön verme, uygulama ve sonuçlar ekseninde "
        "değerlendiren Avrupa kalite çerçevesidir.\n"
        "\n"
        "Sınır: Bu kart gerçek bir EFQM özdeğerlendirmesi yapmaz. Kriter kapsamı strateji "
        "sayınızdan, hazırlık skoru KS skorunuzdan türetilir — yaklaşık bir gösterge olarak "
        "okunmalıdır.\n"
        "\n"
        "Yorum: EFQM'in ayırt edici yanı, iyi uygulamaları değil bunların ÜRETTİĞİ SONUÇLARI "
        "sorgulamasıdır. Yüksek hazırlık skoru, resmi bir değerlendirmeye girebilecek veri "
        "olgunluğuna işaret eder; kalite seviyesinin kendisine değil."
    ),

    "k_radar_ks.gap_analizi": (
        "GAP analizi, göstergelerin hedef ile gerçekleşen arasındaki farkını süreç bazında "
        "gösterir.\n"
        "\n"
        "Hesap: Her gösterge için gerçekleşmenin hedefe oranı yüzdeye çevrilir (gösterge yönü "
        "'azalması iyi' ise oran ters çevrilir). Süreç başına ortalama başarı hesaplanır, "
        "açık = ortalama − 100'dür.\n"
        "\n"
        "Eşik: Ortalama başarı 80 ve üzeri 'hedefte', 50-80 arası 'riskli', altı 'kritik' "
        "sayılır.\n"
        "\n"
        "Yorum: Negatif açık hedefin altında kalındığını gösterir. Süreç listede hiç görünmüyorsa "
        "o süreçte ölçüm verisi yok demektir — sıfır başarı ile veri yokluğu farklı şeylerdir.\n"
        "\n"
        "Sınır: Yalnızca seçili yılın verisi hesaba katılır; yıl seçilmezse içinde bulunulan yıl "
        "kullanılır."
    ),

    "k_radar_ks.strateji_surec_kapsama_ozeti": (
        "Her ana ve alt stratejinin hangi süreçlerle kapsandığını sıralı biçimde listeler.\n"
        "\n"
        "Hesap: Süreç-alt strateji bağlantı kayıtlarından, strateji başına bağlı süreçler "
        "toplanır ve kapsama yüzdesi hesaplanır.\n"
        "\n"
        "Yorum: Bu liste iki yönlü okunur. Kapsaması sıfır olan strateji, sahada karşılığı "
        "olmayan bir niyettir. Hiçbir stratejiye bağlanmamış süreç ise kaynak tüketen ama "
        "stratejik yönü belirsiz bir faaliyettir — ikisi de düzeltme gerektirir."
    ),

    # ─────────────────────────── KP MİNİ İSTATİSTİKLER ───────────────────────────

    "k_radar_kp.toplam_skor": (
        "Süreç performansının (KP) ağırlıklı toplam skorunu gösterir.\n"
        "\n"
        "Hesap: Her aktif göstergenin YALNIZCA EN SON ölçümü alınır; gerçekleşen/hedef oranı "
        "yüzdeye çevrilir (en fazla 150 ile sınırlanır) ve gösterge ağırlıklarıyla ortalanır.\n"
        "\n"
        "Sınır: Verisi olmayan veya hedefi tanımsız göstergeler hesaba KATILMAZ. Tanımlı 50 "
        "göstergeden 4'ünde veri varsa skor o 4'ün ortalamasıdır. Hiç uygun veri yoksa skor 0 "
        "ve bant kırmızı olur — 'ölçüm yok' ile 'performans sıfır' aynı görünür.\n"
        "\n"
        "Yorum: Tek bir göstergenin son ölçümü tüm skoru etkileyebilir; trend değil anlık "
        "durumdur."
    ),

    "k_radar_kp.band": (
        "KP skorunun renk bandını gösterir: yeşil, sarı veya kırmızı.\n"
        "\n"
        "Eşik: 80 ve üzeri yeşil, 60-80 arası sarı, altı kırmızıdır.\n"
        "\n"
        "Sınır: Kritik gösterge sayısı 3'e ulaştığında bant, skor yüksek olsa bile ZORLA "
        "kırmızıya çekilir. Yani skoru 90 olan bir kurum kırmızı bantta görünebilir — bu bir "
        "hata değil, kritik gösterge birikimine karşı bilinçli bir uyarıdır.\n"
        "\n"
        "Yorum: Bant, skorun tek başına gizleyebileceği yoğunlaşmış riski görünür kılar. "
        "Ortalama iyiyken birkaç göstergenin ciddi biçimde kötü olması, ortalamanın arkasına "
        "saklanan bir sorundur."
    ),

    "k_radar_kp.kritik_pg": (
        "Hedefinin belirgin biçimde altında kalan gösterge sayısını gösterir.\n"
        "\n"
        "Eşik: Gerçekleşmesi hedefinin %70'inin altında kalan göstergeler kritik sayılır.\n"
        "\n"
        "Sınır: Verisi hiç girilmemiş göstergeler kritik SAYILMAZ. Yani bu sayının düşük olması, "
        "ölçülmeyen alanların iyi olduğu anlamına gelmez — sadece ölçülenler arasında kritik "
        "olmadığını gösterir.\n"
        "\n"
        "Yorum: Bu sayı 3'e ulaştığında genel bant kırmızıya döner ve sistem iyileştirme planı "
        "önerisi üretir."
    ),

    "k_radar_kp.hesaplanan_pg": (
        "Skora fiilen giren gösterge sayısını gösterir.\n"
        "\n"
        "Hesap: Hem aktif olan hem de hedefi tanımlı geçerli ölçümü bulunan göstergelerin "
        "sayımıdır.\n"
        "\n"
        "Yorum: Bu kart skor kartının GÜVENİLİRLİK ÖLÇÜSÜDÜR. Tanımlı gösterge sayınızla bu "
        "sayı arasındaki fark, ölçüm boşluğunuzu gösterir. 50 göstergeniz varken burada 4 "
        "yazıyorsa, gördüğünüz skor kurumun yalnızca küçük bir kesitini temsil ediyor demektir. "
        "Skoru yorumlamadan önce bu sayıya bakın."
    ),
}
