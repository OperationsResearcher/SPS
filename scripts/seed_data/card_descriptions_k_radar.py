# -*- coding: utf-8 -*-
"""K-Radar kart açıklamaları — zenginleştirilmiş.

YAZIM SÖZLEŞMESİ (bu dosyaya ekleme yaparken uy):
  1. Düz metin. Modal yapılandırılmış basar (base.html::renderInfoBody):
       "Başlık:" ile başlayan satır  -> kalın bölüm etiketi
       boş satır                     -> paragraf ayracı
       "- " ile başlayan satır       -> madde
  2. Bölüm sırası: [tanım paragrafı] / Hesap: / Yorum: / Sınır: (varsa) / Kaynak: (literatür)
  3. ŞEFFAFLIK ZORUNLU: Gösterge adıyla gerçekte ölçülen şey ayrışıyorsa
     "Sınır:" bölümünde açıkça yaz. Kullanıcı sayıya bakıp yanlış karar vermesin.
  4. Literatür bilgisi DOĞRULANMIŞ olmalı. Doğrulanamayan atıf yazılmaz
     (ör. SWOT için "Albert Humphrey" atfı 2023 araştırmasıyla çürütülmüştür —
     "1960'larda SRI'da SOFT olarak geliştirildi" ifadesi kullanılır).
  5. Türkçe, sen-dili değil kurumsal ton. Terim adları İngilizce kalabilir.
"""

# Tüm KP alt modüllerinde tekrarlanan ortak uyarılar — tek yerden yönetilir.
_CACHE = "Kart değerleri 5 dakika önbelleklenir; yeni veri girdikten hemen sonra değişmeyebilir."

DESCRIPTIONS: dict[str, str] = {

    # ─────────────────────────── KP ALT MODÜLLERİ ───────────────────────────

    "k_radar_kp_oee.ozet": (
        "OEE (Overall Equipment Effectiveness), bir işletmenin planlı çalışma süresini ne ölçüde "
        "değerli çıktıya çevirdiğini tek sayıda özetler. Kullanılabilirlik × Performans × Kalite "
        "çarpımından oluşur.\n"
        "\n"
        "Hesap: Süreç göstergelerinizin hedefe ulaşma oranından türetilir. Ortalama gerçekleşme "
        "oranı hesaplanır, üç bileşen bu ortalamanın etrafında konumlandırılır ve çarpılır.\n"
        "\n"
        "Sınır: Bu YAKLAŞIK bir göstergedir. Gerçek OEE için makine duruş kayıtları (kullanılabilirlik), "
        "çevrim hızı (performans) ve fire oranı (kalite) ayrı ayrı ölçülmelidir. Sistem henüz bu üç "
        "veriyi ayrı toplamadığı için üç bileşen aynı performans ortalamasından üretilir; "
        "aralarındaki fark gerçek bir ölçüm farkını yansıtmaz. Gösterge verisi hiç yoksa değer "
        "genel süreç skorundan türetilir.\n"
        "\n"
        "Yorum: Dünya standardı %85'tir (kullanılabilirlik %90 × performans %95 × kalite %99). "
        "Tipik imalat ortalaması %60 dolayındadır; %40 altı ciddi kayba işaret eder.\n"
        "\n"
        "Kaynak: Seiichi Nakajima, Toplam Verimli Bakım (TPM) çerçevesi, 1988."
    ),

    "k_radar_kp_vsm.vsm_ozeti": (
        "Değer Akışı Haritalama (VSM), bir işin baştan sona akışını değer katan ve katmayan "
        "adımlarıyla görselleştirir. Akış verimliliği, toplam süre içinde gerçekten değer üretilen "
        "kısmın payıdır.\n"
        "\n"
        "Hesap: Değer zinciri faaliyetlerinizden israf (muda) etiketi taşımayanların toplam faaliyete "
        "oranıdır. İsraf baskısı bunun tümleyenidir (100 − akış verimliliği).\n"
        "\n"
        "Sınır: Gerçek VSM, çevrim süresi ile bekleme süresini saat bazında ölçer. Buradaki değer "
        "faaliyet SAYISINA dayanır, süreye değil — israfsız faaliyet oranını gösterir. Değer zinciri "
        "faaliyeti tanımlanmamışsa değer genel süreç skorundan türetilir.\n"
        "\n"
        "Yorum: Geleneksel iş süreçlerinde akış verimliliği tipik olarak %5-10 bandındadır; düşük "
        "değer sürecin kötü olduğunu değil, işin çoğu zamanı beklemede geçirdiğini gösterir. "
        "İyileştirme fırsatı genelde adımların içinde değil, adımlar arasındadır.\n"
        "\n"
        "Kaynak: Mike Rother & John Shook, Learning to See, Lean Enterprise Institute, 1998."
    ),

    "k_radar_kp_deger_zinciri.ozet": (
        "Porter değer zinciri, kurumun faaliyetlerini birincil (doğrudan değer üreten) ve destek "
        "faaliyetler olarak ayırır. Bu kart faaliyetlerinizin süreçlere ne ölçüde bağlandığını ve "
        "israf yoğunluğunu gösterir.\n"
        "\n"
        "Hesap: Muda riski, israf türü etiketlenmiş faaliyetlerin oranından hesaplanır (1,4 katsayısı "
        "ile ölçeklenir). Eşlenen süreç, değer zinciri faaliyetine bağlanmış benzersiz süreç sayısıdır.\n"
        "\n"
        "Sınır: Hiçbir faaliyet bir sürece bağlanmamışsa 'Eşlenen Süreç' alanı sıfır yerine toplam "
        "aktif süreç sayısını gösterir. Bu sayı yüksekse eşlemenin gerçekten yapıldığını 'Faaliyet "
        "Sayısı' alanından teyit edin.\n"
        "\n"
        "Yorum: Muda, müşteriye değer katmayan her faaliyettir; yedi türü vardır (fazla üretim, "
        "bekleme, taşıma, fazla işleme, stok, hareket, hata). Ohno fazla üretimi en kötü israf sayar, "
        "çünkü diğer altısını doğurur.\n"
        "\n"
        "Kaynak: Taiichi Ohno, Toyota Üretim Sistemi, 1978."
    ),

    "k_radar_kp_darbogaz.ozet": (
        "Darboğaz, sistemin toplam çıktısını sınırlayan kısıttır. Kısıtlar Teorisi'ne göre bir sistemin "
        "üretimi ancak darboğazı iyileştirilerek artar.\n"
        "\n"
        "Hesap: Kritik darboğaz, henüz çözülmemiş (açık) darboğaz kaydı sayısıdır. Şiddet endeksi, "
        "açık kayıtların şiddet ağırlıkları toplanarak 0-100 ölçeğine taşınır (düşük=1, orta=2, "
        "yüksek=3, kritik=4). Şiddeti belirtilmemiş kayıtlar 'orta' sayılır.\n"
        "\n"
        "Sınır: Hiç açık darboğaz kaydı yoksa şiddet endeksi, kritik gösterge sayısından türetilir — "
        "yani darboğaz kaydı girilmemişken de sıfırdan farklı bir değer görebilirsiniz.\n"
        "\n"
        "Yorum: Darboğaz dışındaki bir adımı iyileştirmek toplam çıktıyı artırmaz; yalnızca ara stok "
        "ve maliyet üretir. Goldratt'ın beş adımı: kısıtı belirle, sonuna kadar kullan, her şeyi ona "
        "tabi kıl, kapasitesini yükselt, kısıt yer değiştirince baştan başla.\n"
        "\n"
        "Kaynak: Eliyahu M. Goldratt, The Goal (Amaç), 1984."
    ),

    "k_radar_kp_pareto.ozet": (
        "Pareto ilkesi, sonuçların büyük çoğunluğunun nedenlerin küçük bir azınlığından doğduğunu "
        "söyler. Juran bunu kalite yönetimine uyarlayıp 'hayati azınlık' kavramını getirmiştir.\n"
        "\n"
        "Hesap: İlk dilim etkisi, açık darboğazların süreç bazında dağılımında en yoğun üç sürecin "
        "toplam içindeki payıdır.\n"
        "\n"
        "Sınır: Hiç açık darboğaz yoksa bu oran kritik gösterge sayısından türetilir. 'KPI Sayısı' "
        "alanı Pareto hesabına girmez, yalnızca bağlam sunar.\n"
        "\n"
        "Yorum: Oran yüksekse (dağılım dik) problem az sayıda süreçte yoğunlaşmıştır; oraya odaklanmak "
        "yeterlidir. Oran düşükse sorun yayılmıştır ve tekil müdahale işe yaramaz. 80/20 kesin bir "
        "yasa değil, gözlemsel eğilimdir — 70/30 da 90/10 da olabilir.\n"
        "\n"
        "Kaynak: Vilfredo Pareto (1896 gözlemi); kalite yönetimine uyarlayan Joseph M. Juran."
    ),

    "k_radar_kp_olgunluk.olgunluk_takip": (
        "Süreç olgunluğu, süreçlerinizin ne kadar tanımlı, ölçülü ve iyileştirilebilir olduğunu 1-5 "
        "arası derecelendirir. CMMI modeline dayanır.\n"
        "\n"
        "Seviyeler:\n"
        "- 1 Başlangıç: gelişigüzel, kişiye bağlı, tepkisel\n"
        "- 2 Yönetilen: planlanmış ve politikaya göre yürütülen\n"
        "- 3 Tanımlı: kurum çapında standartlaşmış, belgelenmiş\n"
        "- 4 Sayısal Yönetilen: ölçülüp istatistiksel kontrol edilen\n"
        "- 5 Optimize: sürekli iyileştirme ve yenilik odaklı\n"
        "\n"
        "Hesap: Girilen olgunluk değerlendirmelerinin ortalamasıdır. Değerlendirme hiç girilmemişse "
        "seviye genel süreç skorundan türetilir — bu durumda gösterilen seviye gerçek bir "
        "değerlendirmeye dayanmaz.\n"
        "\n"
        "Yorum: Seviye 3, süreçlerin kişilere değil kuruma ait olduğu eşiktir. Seviye 4'ten itibaren "
        "yönetim sezgiyle değil veriyle yapılır.\n"
        "\n"
        "Kaynak: Software Engineering Institute (Carnegie Mellon Üniversitesi), CMMI."
    ),

    "k_radar_kp_sla.ozet": (
        "SLA (Hizmet Seviyesi Anlaşması), taahhüt edilen ölçülebilir hedeflerin karşılanma durumunu "
        "izler. İhlal riski, hedefin altında kalan ölçümlerin payıdır.\n"
        "\n"
        "Hesap: Gerçekleşen değeri hedefinin %90'ının altında kalan gösterge ölçümlerinin, hedefi "
        "tanımlı tüm ölçümlere oranıdır.\n"
        "\n"
        "Sınır: %90 eşiği sistem genelinde sabittir; kart gerçek bir SLA sözleşme alanı okumaz. "
        "Sözleşmeye özgü eşikleriniz farklıysa bu oran onları yansıtmaz. Ayrıca ölçüm tarih filtresi "
        "olmadan tüm geçmiş veriyi kapsar.\n"
        "\n"
        "Yorum: İhlal riski göstergesinin amacı, ihlal gerçekleşmeden müdahale penceresi açmaktır — "
        "ihlal sonrası raporlama geç kalmış ölçümdür. Evrensel bir eşik yoktur; sınır sözleşmeyle "
        "belirlenir.\n"
        "\n"
        "Kaynak: ITIL, Hizmet Seviyesi Yönetimi."
    ),

    "k_radar_kp_benchmark.benchmark_ozeti": (
        "Benchmarking, performansı sektörün en iyileriyle sürekli karşılaştırma sürecidir. Anlamlı "
        "kıyas için ön koşul, verinin karşılaştırılabilir olmasıdır.\n"
        "\n"
        "Hesap: Karşılaştırılabilirlik skoru, en az 3 veri noktası bulunan göstergelerin toplam "
        "gösterge sayısına oranıdır. Yeterli geçmişi olmayan gösterge kıyasa uygun sayılmaz.\n"
        "\n"
        "Sınır: Bu skor iç veri olgunluğunu ölçer — dış kurumlarla gerçek bir kıyaslama yapmaz. "
        "Yüksek skor, verinizin kıyasa HAZIR olduğunu gösterir, iyi performansta olduğunuzu değil.\n"
        "\n"
        "Yorum: Kıyas farkı büyük çıktığında önce ölçüm tanımlarının aynı olup olmadığı sorgulanır; "
        "fark gerçekse en iyi uygulamanın kuruma transfer edilebilirliği araştırılır.\n"
        "\n"
        "Kaynak: Robert C. Camp, Benchmarking, 1989 (Xerox uygulaması, 1979)."
    ),

    "k_radar_kp_kapasite.kapasite_ozeti": (
        "Kapasite kullanımı, kaynakların ne ölçüde meşgul olduğunu gösterir. Kuyruk teorisinde "
        "kullanım ile bekleme süresi arasındaki ilişki doğrusal değildir.\n"
        "\n"
        "Hesap: Kullanım tahmini, en az bir aktif göstergesi bulunan süreçlerin toplam aktif sürece "
        "oranıdır. Kaynak baskısı, bunun tümleyenine açık darboğaz sayısı eklenerek bulunur.\n"
        "\n"
        "Sınır: Bu değer gerçek insan/makine kapasitesi kullanımı DEĞİL, gösterge kapsama oranıdır. "
        "Sistem kişi bazlı kapasite verisi tutmadığı için isim ile ölçülen şey birebir örtüşmez.\n"
        "\n"
        "Yorum: Kingman formülüne göre bekleme süresi, kullanım oranı arttıkça hiperbolik büyür: "
        "%80'den %90'a çıkış beklemeyi kabaca ikiye katlar, %90'dan %95'e çıkış yine ikiye katlar. "
        "Bu nedenle kritik kaynaklar bilinçli olarak tam doluluğun altında tutulur; boşta kapasite "
        "her zaman israf değildir, akışın tamponudur.\n"
        "\n"
        "Kaynak: John Kingman, ağır trafik altında kuyruk modeli, 1961."
    ),
}
