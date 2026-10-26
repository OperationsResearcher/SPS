# -*- coding: utf-8 -*-
"""Proje kontrol listesi kartları — 5 kart (şablon yönetimi, proje sekmesi, proje özeti).

Yazım sözleşmesi için bkz. card_descriptions_k_radar.py başlığı.
Kartlar Kart Yönetimi keşfinden SONRA seed edilir (system_cards satırı gerekir).
"""

DESCRIPTIONS: dict[str, str] = {

    "project.kontrol_sablonu": (
        "Kurumun yıl bazlı kontrol listesi şablonunu yönetir: madde ekleme, düzenleme, "
        "silme, sıralama, Excel'den içe aktarma ve başka yıldan kopyalama.\n"
        "\n"
        "Sınır: Şablondaki değişiklik yalnızca bundan sonra açılacak projeleri etkiler; "
        "açılmış projelerin listesi o projenin Kontrol Listesi sekmesinden düzenlenir. "
        "Her yılın şablonu ayrıdır. Şablonda sorumlu tutulmaz — sorumlular proje içinde "
        "maddelere atanır.\n"
        "\n"
        "Yorum: Periyot (gün) girilen madde, atanan kişilere düzenli hatırlatma "
        "gönderir; 'Kanıt zorunlu' işaretli madde kanıtsız tamamlanamaz."
    ),

    "project.kontrol_ilerleme": (
        "Projenin kontrol listesi ilerlemesini gösterir: onaylı madde sayısı, onay "
        "bekleyenler ve aşama bazında durum; projeyi tamamlama ve Excel/PDF çıktısı "
        "buradan yapılır.\n"
        "\n"
        "Sınır: Yalnızca 'Onaylandı' durumundaki maddeler ilerlemeye sayılır — 'Yapıldı' "
        "işaretlenmiş ama onay bekleyen madde sayılmaz. Tüm maddeler onaylanmadan proje "
        "tamamlanamaz.\n"
        "\n"
        "Yorum: Çok sayıda 'onay bekliyor' maddesi, onay yetkililerinde birikme "
        "olduğunu gösterir; ilerlemeyi hızlandırmanın yolu onay kuyruğunu eritmektir."
    ),

    "project.kontrol_maddeler": (
        "Proje kontrol listesi maddelerini aşamalara göre listeler; her maddeye kişi, süreç "
        "(sürecin tüm üyeleri) ve/veya proje ekibi atanır. Atanan 'Yapıldı' işaretler, "
        "yapandan farklı bir lider/yönetici onaylar. Kanıt (dosya veya bağlantı) ve not "
        "eklenebilir.\n"
        "\n"
        "Sınır: Atamayı yalnızca proje lideri ve yöneticiler yapar; birden çok maddeyi "
        "seçip toplu atayabilirler. Maddeyi işaretleyen kişi kendi maddesini onaylayamaz "
        "(çift onay). 'Kanıt zorunlu' maddeler kanıtsız işaretlenemez. Maddeyi projeden "
        "çıkarmak denetim kaydına yazılır.\n"
        "\n"
        "Yorum: Süreç atamak, o sürecin üyeleri değiştikçe sorumluları da kendiliğinden "
        "günceller; proje ekibi için de aynısı geçerlidir. Periyot rozeti taşıyan "
        "maddeler için atananlara düzenli hatırlatma gider, onaylanınca durur."
    ),

    "project_detail.kontrol_listesi_ozeti": (
        "Proje özet sayfasında kontrol listesi ilerlemesini ve tamamlanma durumunu "
        "gösterir; ayrıntı için Kontrol Listesi sekmesine geçilir.\n"
        "\n"
        "Sınır: Kart yalnızca özet verir, madde işlemleri sekmede yapılır. Projede "
        "kontrol listesi yoksa kart görünmez.\n"
        "\n"
        "Yorum: Yüzde yalnızca onaylı maddelere göredir; proje, yüzde 100 olmadan "
        "tamamlanmış sayılmaz."
    ),
}
