(function () {
"use strict";
var TOOL_INFO_DATA = {
    cpm: {
        title: 'CPM (Critical Path Method) Analizi',
        icon: 'fas fa-project-diagram',
        color: 'primary',
        sections: [
            {
                heading: 'Nasıl Kullanılır?',
                content: `<ul class="list-unstyled">
                    <li class="mb-2"><i class="fas fa-check-circle text-success me-2"></i>Görevler arasındaki bağımlılıkları (predecessor/successor) tanımlayın</li>
                    <li class="mb-2"><i class="fas fa-check-circle text-success me-2"></i>Her görev için tahmini süre girin</li>
                    <li class="mb-2"><i class="fas fa-check-circle text-success me-2"></i>Sistem otomatik olarak kritik yolu hesaplar</li>
                    <li class="mb-2"><i class="fas fa-check-circle text-success me-2"></i>Slack (boşluk) zamanlarını görüntüleyin</li>
                </ul>`
            },
            {
                heading: 'Ne Sonuçlar Elde Edersiniz?',
                content: `<ul class="list-unstyled">
                    <li class="mb-2"><i class="fas fa-chart-line text-info me-2"></i><strong>Kritik Yol:</strong> Projeyi geciktirecek görevler kırmızı ile işaretlenir</li>
                    <li class="mb-2"><i class="fas fa-clock text-warning me-2"></i><strong>Slack Zamanı:</strong> Gecikme toleransı olan görevleri belirleyin</li>
                    <li class="mb-2"><i class="fas fa-calendar-alt text-primary me-2"></i><strong>Erken/Geç Başlangıç:</strong> Her görev için optimal zaman penceresi</li>
                    <li class="mb-2"><i class="fas fa-exclamation-triangle text-danger me-2"></i><strong>Bottleneck Tespiti:</strong> Darboğaz görevleri belirleyin</li>
                </ul>`
            },
            {
                heading: 'Proje Yönetimine Katkısı',
                content: `<div class="alert alert-success mb-0">
                    <p class="mb-2"><strong>🎯 Risk Azaltma:</strong> Kritik görevlere odaklanarak gecikmeler önlenir</p>
                    <p class="mb-2"><strong>📊 Kaynak Optimizasyonu:</strong> Slack zamanı olan görevlerde esneklik sağlar</p>
                    <p class="mb-2"><strong>⏱️ Gerçekçi Planlama:</strong> En kısa proje süresini bilimsel olarak hesaplar</p>
                    <p class="mb-0"><strong>🔍 Önceliklendirme:</strong> Hangi görevlerin geciktirilmeyeceğini net gösterir</p>
                </div>`
            }
        ]
    },
    raid: {
        title: 'RAID Yönetimi',
        icon: 'fas fa-shield-alt',
        color: 'danger',
        sections: [
            {
                heading: 'Nasıl Kullanılır?',
                content: `<ul class="list-unstyled">
                    <li class="mb-2"><i class="fas fa-exclamation-triangle text-danger me-2"></i><strong>Risks (Riskler):</strong> Olasılık (1-5) ve etki (1-5) puanlayın, azaltma stratejisi belirleyin</li>
                    <li class="mb-2"><i class="fas fa-question-circle text-info me-2"></i><strong>Assumptions (Varsayımlar):</strong> Doğrulama tarihi ve notlarla varsayımlarınızı kaydedin</li>
                    <li class="mb-2"><i class="fas fa-bug text-warning me-2"></i><strong>Issues (Sorunlar):</strong> Aciliyet seviyesi (Düşük/Orta/Yüksek/Kritik) ile aktif sorunları takip edin</li>
                    <li class="mb-2"><i class="fas fa-link text-primary me-2"></i><strong>Dependencies (Bağımlılıklar):</strong> Dış bağımlılıkları ve görev ilişkilerini (FS/SS/FF/SF) yönetin</li>
                </ul>`
            },
            {
                heading: 'Ne Sonuçlar Elde Edersiniz?',
                content: `<ul class="list-unstyled">
                    <li class="mb-2"><i class="fas fa-chart-pie text-danger me-2"></i><strong>Risk Skoru:</strong> Olasılık × Etki = toplam risk değeri (max 25)</li>
                    <li class="mb-2"><i class="fas fa-list-check text-success me-2"></i><strong>Önceliklendirme:</strong> En kritik riskleri skor sıralamasıyla görebilirsiniz</li>
                    <li class="mb-2"><i class="fas fa-bell text-warning me-2"></i><strong>Varsayım Uyarıları:</strong> Doğrulama tarihi geçmiş varsayımlar vurgulanır</li>
                    <li class="mb-2"><i class="fas fa-fire text-danger me-2"></i><strong>Acil Sorunlar:</strong> Kritik ve yüksek aciliyetli sorunlar öne çıkar</li>
                </ul>`
            },
            {
                heading: 'Proje Yönetimine Katkısı',
                content: `<div class="alert alert-danger mb-0">
                    <p class="mb-2"><strong>🛡️ Proaktif Koruma:</strong> Riskler kriz olmadan önce yönetilir</p>
                    <p class="mb-2"><strong>📋 Toplantı Verimliliği:</strong> Tüm riskler, sorunlar, varsayımlar tek ekranda</p>
                    <p class="mb-2"><strong>🎯 Yanlış Varsayım Engeli:</strong> Doğrulanmamış varsayımlar planı çürütmeden yakalanır</p>
                    <p class="mb-0"><strong>🔗 Bağımlılık Şeffaflığı:</strong> Blokaj noktaları ve dış faktörler görünür olur</p>
                </div>`
            }
        ]
    },
    sla: {
        title: 'SLA (Service Level Agreement) Tanımları',
        icon: 'fas fa-clock',
        color: 'warning',
        sections: [
            {
                heading: 'Nasıl Kullanılır?',
                content: `<ul class="list-unstyled">
                    <li class="mb-2"><i class="fas fa-tag text-primary me-2"></i>Görev tiplerine göre SLA kuralları oluşturun (Bug, Feature, Task vb.)</li>
                    <li class="mb-2"><i class="fas fa-hourglass-half text-warning me-2"></i>Hedef tamamlanma süresini (saat/gün) belirleyin</li>
                    <li class="mb-2"><i class="fas fa-bell text-danger me-2"></i>Otomatik uyarı eşikleri tanımlayın (%75, %90, %100)</li>
                    <li class="mb-2"><i class="fas fa-cog text-success me-2"></i>Öncelik seviyelerine göre farklı SLA'lar atayın</li>
                </ul>`
            },
            {
                heading: 'Ne Sonuçlar Elde Edersiniz?',
                content: `<ul class="list-unstyled">
                    <li class="mb-2"><i class="fas fa-check-circle text-success me-2"></i><strong>SLA Uyum Oranı:</strong> Hedeflere uyum yüzdesi raporlanır</li>
                    <li class="mb-2"><i class="fas fa-exclamation-circle text-warning me-2"></i><strong>Yaklaşan İhlaller:</strong> Süresi dolmak üzere olan görevler vurgulanır</li>
                    <li class="mb-2"><i class="fas fa-times-circle text-danger me-2"></i><strong>İhlal Analizi:</strong> SLA'yı aşan görevler listelenir</li>
                    <li class="mb-2"><i class="fas fa-chart-bar text-info me-2"></i><strong>Performans Metrikleri:</strong> Ortalama tamamlanma süreleri grafiği</li>
                </ul>`
            },
            {
                heading: 'Proje Yönetimine Katkısı',
                content: `<div class="alert alert-warning mb-0">
                    <p class="mb-2"><strong>⏰ Zaman Yönetimi:</strong> Görevler net tamamlanma hedefleriyle yönetilir</p>
                    <p class="mb-2"><strong>📈 Performans İzleme:</strong> Ekip ve bireysel SLA uyum oranları ölçülür</p>
                    <p class="mb-2"><strong>🚨 Erken Uyarı:</strong> Gecikme riski olan görevler önceden belirlenir</p>
                    <p class="mb-0"><strong>🎯 Kalite Garantisi:</strong> Müşteri/stakeholder beklentileri karşılanır</p>
                </div>`
            }
        ]
    },
    capacity: {
        title: 'Kapasite Planlama',
        icon: 'fas fa-users-cog',
        color: 'success',
        sections: [
            {
                heading: 'Nasıl Kullanılır?',
                content: `<ul class="list-unstyled">
                    <li class="mb-2"><i class="fas fa-user text-primary me-2"></i>Ekip üyelerinin günlük/haftalık çalışma saatlerini tanımlayın</li>
                    <li class="mb-2"><i class="fas fa-calendar text-info me-2"></i>Tatil ve izin günlerini sisteme girin</li>
                    <li class="mb-2"><i class="fas fa-tasks text-warning me-2"></i>Görevlere tahmini efor (saat) atayın</li>
                    <li class="mb-2"><i class="fas fa-chart-gantt text-success me-2"></i>Zaman çizelgesinde kaynak yüklenmesini görüntüleyin</li>
                </ul>`
            },
            {
                heading: 'Ne Sonuçlar Elde Edersiniz?',
                content: `<ul class="list-unstyled">
                    <li class="mb-2"><i class="fas fa-tachometer-alt text-danger me-2"></i><strong>Yüklenme Oranı:</strong> %0-100+ aralığında kişi bazlı kullanım</li>
                    <li class="mb-2"><i class="fas fa-exclamation-triangle text-warning me-2"></i><strong>Aşırı Yüklenme Uyarısı:</strong> %100'ü aşan atamalar kırmızı ile gösterilir</li>
                    <li class="mb-2"><i class="fas fa-battery-quarter text-info me-2"></i><strong>Boş Kapasite:</strong> Atanmamış zaman dilimlerini görüntüleyin</li>
                    <li class="mb-2"><i class="fas fa-balance-scale text-success me-2"></i><strong>Kaynak Dengeleme:</strong> Görev dağılımını optimize edin</li>
                </ul>`
            },
            {
                heading: 'Proje Yönetimine Katkısı',
                content: `<div class="alert alert-success mb-0">
                    <p class="mb-2"><strong>👥 Ekip Sağlığı:</strong> Burnout riski taşıyan kişileri önceden tespit edersiniz</p>
                    <p class="mb-2"><strong>📊 Gerçekçi Planlama:</strong> Kapasite üstü iş atanmasını engellersiniz</p>
                    <p class="mb-2"><strong>🔄 Esnek Yeniden Atama:</strong> Boş kapasitedeki kişilere görev aktarılabilir</p>
                    <p class="mb-0"><strong>💰 Maliyet Optimizasyonu:</strong> Kaynak israfı önlenir, verimlilik artar</p>
                </div>`
            }
        ]
    },
    baseline: {
        title: 'Baseline (Referans) Takibi',
        icon: 'fas fa-chart-bar',
        color: 'info',
        sections: [
            {
                heading: 'Nasıl Kullanılır?',
                content: `<ul class="list-unstyled">
                    <li class="mb-2"><i class="fas fa-save text-primary me-2"></i>Proje başlangıcında veya önemli milestone'larda "Baseline Kaydet"</li>
                    <li class="mb-2"><i class="fas fa-calendar-check text-success me-2"></i>Kaydedilen baseline, o anki tüm görev tarih/efor bilgilerini dondurur</li>
                    <li class="mb-2"><i class="fas fa-chart-line text-warning me-2"></i>Gerçek ilerleme ile planlanan (baseline) karşılaştırılır</li>
                    <li class="mb-2"><i class="fas fa-edit text-info me-2"></i>Görevler değiştikçe sapma (variance) otomatik hesaplanır</li>
                </ul>`
            },
            {
                heading: 'Ne Sonuçlar Elde Edersiniz?',
                content: `<ul class="list-unstyled">
                    <li class="mb-2"><i class="fas fa-arrows-alt-h text-primary me-2"></i><strong>Tarih Sapması:</strong> Planlanan vs gerçek tarih farkı (gün)</li>
                    <li class="mb-2"><i class="fas fa-hourglass-end text-warning me-2"></i><strong>Efor Sapması:</strong> Tahmini vs harcanan efor farkı (saat)</li>
                    <li class="mb-2"><i class="fas fa-percentage text-danger me-2"></i><strong>Sapma Yüzdesi:</strong> +/- % olarak gösterilir</li>
                    <li class="mb-2"><i class="fas fa-chart-area text-success me-2"></i><strong>Trend Grafiği:</strong> Zaman içinde sapmanın nasıl değiştiği görülür</li>
                </ul>`
            },
            {
                heading: 'Proje Yönetimine Katkısı',
                content: `<div class="alert alert-info mb-0">
                    <p class="mb-2"><strong>📏 Tahmin Doğruluğu:</strong> Gelecek projeler için daha iyi efor tahmini yaparsınız</p>
                    <p class="mb-2"><strong>🔍 Sapma Analizi:</strong> Neden gecikme/aşma olduğunu retrospektif inceleyebilirsiniz</p>
                    <p class="mb-2"><strong>📊 Yönetici Raporlama:</strong> "Plan vs Gerçek" raporu stakeholder'lara sunulur</p>
                    <p class="mb-0"><strong>⚖️ PMI Uyumluluk:</strong> PMBOK standartlarındaki EVM (Earned Value Management) temelini oluşturur</p>
                </div>`
            }
        ]
    },
    dependency: {
        title: 'Bağımlılık Matrisi',
        icon: 'fas fa-sitemap',
        color: 'primary',
        sections: [
            {
                heading: 'Nasıl Kullanılır?',
                content: `<ul class="list-unstyled">
                    <li class="mb-2"><i class="fas fa-table text-primary me-2"></i>Matris formatında satır = kaynak görev, sütun = hedef görev</li>
                    <li class="mb-2"><i class="fas fa-link text-info me-2"></i>İki görev arasında bağımlılık varsa hücreye tıklayın</li>
                    <li class="mb-2"><i class="fas fa-project-diagram text-success me-2"></i>Görsel ağ grafiği ile tüm bağlantıları görüntüleyin</li>
                    <li class="mb-2"><i class="fas fa-search text-warning me-2"></i>Döngüsel bağımlılık (circular dependency) uyarıları alın</li>
                </ul>`
            },
            {
                heading: 'Ne Sonuçlar Elde Edersiniz?',
                content: `<ul class="list-unstyled">
                    <li class="mb-2"><i class="fas fa-network-wired text-primary me-2"></i><strong>Bağımlılık Haritası:</strong> Hangi görevin hangi göreve bağlı olduğu netleşir</li>
                    <li class="mb-2"><i class="fas fa-exclamation-triangle text-danger me-2"></i><strong>Döngü Tespiti:</strong> A→B→C→A gibi kısır döngüler yakalanır</li>
                    <li class="mb-2"><i class="fas fa-lock text-warning me-2"></i><strong>Blokaj Noktaları:</strong> Çok sayıda görevi bekleyen görevler vurgulanır</li>
                    <li class="mb-2"><i class="fas fa-cubes text-info me-2"></i><strong>Bağımlılık Yoğunluğu:</strong> Görev başına ortalama bağlantı sayısı</li>
                </ul>`
            },
            {
                heading: 'Proje Yönetimine Katkısı',
                content: `<div class="alert alert-primary mb-0">
                    <p class="mb-2"><strong>🧩 Kompleksite Yönetimi:</strong> Karmaşık projelerde ilişkileri görsel olarak anlamlandırırsınız</p>
                    <p class="mb-2"><strong>🚫 Döngü Engelleme:</strong> Mantıksal hatalar proje başlamadan düzeltilir</p>
                    <p class="mb-2"><strong>⚡ Paralel İş:</strong> Bağımlı olmayan görevler eş zamanlı yürütülebilir</p>
                    <p class="mb-0"><strong>🎯 Kritik Görevler:</strong> En çok bağımlılığa sahip görevler önceliklendirilir</p>
                </div>`
            }
        ]
    },
    rules: {
        title: 'Kural Motoru (Automation Engine)',
        icon: 'fas fa-cogs',
        color: 'success',
        sections: [
            {
                heading: 'Nasıl Kullanılır?',
                content: `<ul class="list-unstyled">
                    <li class="mb-2"><i class="fas fa-bolt text-warning me-2"></i><strong>Tetikleyici (Trigger):</strong> "Görev tamamlandı", "Deadline yaklaştı" gibi olaylar</li>
                    <li class="mb-2"><i class="fas fa-filter text-primary me-2"></i><strong>Koşul (Condition):</strong> "Eğer öncelik = Yüksek ise", "Eğer atama yapılmamışsa"</li>
                    <li class="mb-2"><i class="fas fa-play-circle text-success me-2"></i><strong>Aksiyon (Action):</strong> "Bildirim gönder", "Durum değiştir", "Atama yap"</li>
                    <li class="mb-2"><i class="fas fa-toggle-on text-info me-2"></i>Kuralı aktif/pasif duruma getirebilirsiniz</li>
                </ul>`
            },
            {
                heading: 'Ne Sonuçlar Elde Edersiniz?',
                content: `<ul class="list-unstyled">
                    <li class="mb-2"><i class="fas fa-robot text-primary me-2"></i><strong>Otomatik İş Akışları:</strong> Manuel müdahale gerektirmeyen süreçler</li>
                    <li class="mb-2"><i class="fas fa-bell text-warning me-2"></i><strong>Akıllı Bildirimler:</strong> Sadece gerekli durumlarda uyarı</li>
                    <li class="mb-2"><i class="fas fa-exchange-alt text-info me-2"></i><strong>Durum Otomasyonu:</strong> Görevler otomatik statü değiştirir</li>
                    <li class="mb-2"><i class="fas fa-history text-success me-2"></i><strong>Kural Çalıştırma Logu:</strong> Hangi kuralın ne zaman tetiklendiğini görün</li>
                </ul>`
            },
            {
                heading: 'Proje Yönetimine Katkısı',
                content: `<div class="alert alert-success mb-0">
                    <p class="mb-2"><strong>⏱️ Zaman Tasarrufu:</strong> Tekrarlayan manuel işler otomatikleştirilir</p>
                    <p class="mb-2"><strong>🎯 Tutarlılık:</strong> Kurallar her zaman aynı şekilde uygulanır</p>
                    <p class="mb-2"><strong>🔔 Proaktif Yönetim:</strong> Sorun oluşmadan önce otomatik aksiyon alınır</p>
                    <p class="mb-0"><strong>📈 Ölçeklenebilirlik:</strong> 10 görevde çalışan süreç 1000 görevde de çalışır</p>
                </div>`
            }
        ]
    },
    integrations: {
        title: 'Entegrasyonlar (Webhook & API)',
        icon: 'fas fa-plug',
        color: 'info',
        sections: [
            {
                heading: 'Nasıl Kullanılır?',
                content: `<ul class="list-unstyled">
                    <li class="mb-2"><i class="fab fa-slack text-purple me-2"></i><strong>Slack:</strong> Webhook URL'si ekleyin, görev güncellemeleri kanala düşsün</li>
                    <li class="mb-2"><i class="fab fa-microsoft text-primary me-2"></i><strong>MS Teams:</strong> Teams webhook URL'si ile bildirimleri Teams'e gönderin</li>
                    <li class="mb-2"><i class="fas fa-envelope text-danger me-2"></i><strong>Email:</strong> SMTP ayarları ile e-posta otomasyonu</li>
                    <li class="mb-2"><i class="fas fa-code text-success me-2"></i><strong>Custom Webhook:</strong> Kendi sisteminize JSON POST isteği gönderin</li>
                </ul>`
            },
            {
                heading: 'Ne Sonuçlar Elde Edersiniz?',
                content: `<ul class="list-unstyled">
                    <li class="mb-2"><i class="fas fa-comments text-info me-2"></i><strong>Gerçek Zamanlı Bildirimler:</strong> Takımınız kullandığı platformda anında haberdar olur</li>
                    <li class="mb-2"><i class="fas fa-sync text-primary me-2"></i><strong>Çift Yönlü Entegrasyon:</strong> Slack'ten komut göndererek görev durumu değiştirebilirsiniz</li>
                    <li class="mb-2"><i class="fas fa-chart-pie text-success me-2"></i><strong>Event Log:</strong> Hangi olayın hangi sisteme gönderildiği kayıt altında</li>
                    <li class="mb-2"><i class="fas fa-shield-alt text-warning me-2"></i><strong>Güvenlik:</strong> Webhook secret ile yetkisiz erişim engellenir</li>
                </ul>`
            },
            {
                heading: 'Proje Yönetimine Katkısı',
                content: `<div class="alert alert-info mb-0">
                    <p class="mb-2"><strong>🔗 Ekosistem Entegrasyonu:</strong> Kullandığınız diğer araçlarla senkronize çalışır</p>
                    <p class="mb-2"><strong>📢 İletişim Verimliliği:</strong> Ekip "proje aracına girmeden" güncellemeleri görür</p>
                    <p class="mb-2"><strong>🚀 Ölçeklenme:</strong> Webhook'larla binlerce kullanıcıya anında bildirim gönderilir</p>
                    <p class="mb-0"><strong>🤖 Otomasyon Zinciri:</strong> Bir olay, başka sistemde tetikleyici olabilir</p>
                </div>`
            }
        ]
    },
    recurring: {
        title: 'Tekrarlayan Görevler (Recurring Tasks)',
        icon: 'fas fa-redo',
        color: 'success',
        sections: [
            {
                heading: 'Nasıl Kullanılır?',
                content: `<ul class="list-unstyled">
                    <li class="mb-2"><i class="fas fa-calendar-alt text-primary me-2"></i>Cron ifadesi girin: <code>0 9 * * 1</code> (Her Pazartesi saat 09:00)</li>
                    <li class="mb-2"><i class="fas fa-file-alt text-info me-2"></i>Şablon görev tanımlayın (başlık, açıklama, atama, öncelik)</li>
                    <li class="mb-2"><i class="fas fa-clock text-warning me-2"></i>Başlangıç ve bitiş tarihi belirleyin (veya süresiz)</li>
                    <li class="mb-2"><i class="fas fa-toggle-on text-success me-2"></i>Aktif hale getirin; sistem otomatik görev oluşturmaya başlar</li>
                </ul>`
            },
            {
                heading: 'Ne Sonuçlar Elde Edersiniz?',
                content: `<ul class="list-unstyled">
                    <li class="mb-2"><i class="fas fa-tasks text-primary me-2"></i><strong>Otomatik Görev Üretimi:</strong> Belirlenen periyotta yeni görevler sisteme eklenir</li>
                    <li class="mb-2"><i class="fas fa-history text-info me-2"></i><strong>Oluşturma Geçmişi:</strong> Hangi tekrardan kaç görev yaratıldığı loglanır</li>
                    <li class="mb-2"><i class="fas fa-calendar-check text-success me-2"></i><strong>Esnek Zamanlama:</strong> Günlük, haftalık, aylık, custom cron destekler</li>
                    <li class="mb-2"><i class="fas fa-pause-circle text-warning me-2"></i><strong>Durdurma/Devam:</strong> İstediğiniz zaman tekrarı durdurup tekrar başlatabilirsiniz</li>
                </ul>`
            },
            {
                heading: 'Proje Yönetimine Katkısı',
                content: `<div class="alert alert-success mb-0">
                    <p class="mb-2"><strong>🔁 Rutin İşler:</strong> Haftalık rapor, aylık denetim gibi periyodik görevleri unutmazsınız</p>
                    <p class="mb-2"><strong>⏰ Zaman Yönetimi:</strong> Aynı görevi her hafta manuel oluşturma yükünden kurtulursunuz</p>
                    <p class="mb-2"><strong>📊 Tutarlılık:</strong> Şablon görev sayesinde her sefer aynı standart uygulanır</p>
                    <p class="mb-0"><strong>🎯 Compliance:</strong> Yasal/düzenleyici zorunlu periyodik görevler asla atlanmaz</p>
                </div>`
            }
        ]
    },
    workdays: {
        title: 'Çalışma Günleri & Tatil Yönetimi',
        icon: 'fas fa-calendar-check',
        color: 'secondary',
        sections: [
            {
                heading: 'Nasıl Kullanılır?',
                content: `<ul class="list-unstyled">
                    <li class="mb-2"><i class="fas fa-calendar text-primary me-2"></i>Resmi tatil günlerini takvime ekleyin</li>
                    <li class="mb-2"><i class="fas fa-clock text-warning me-2"></i>Günlük çalışma saatlerini tanımlayın (örn. 09:00-18:00, 8 saat)</li>
                    <li class="mb-2"><i class="fas fa-business-time text-success me-2"></i>Hafta içi/hafta sonu kurallarını belirleyin</li>
                    <li class="mb-2"><i class="fas fa-user-clock text-info me-2"></i>Kişi bazlı özel izin/tatil günleri girin</li>
                </ul>`
            },
            {
                heading: 'Ne Sonuçlar Elde Edersiniz?',
                content: `<ul class="list-unstyled">
                    <li class="mb-2"><i class="fas fa-calculator text-primary me-2"></i><strong>Net Çalışma Günü:</strong> Tatiller hariç gerçek iş gün sayısı hesaplanır</li>
                    <li class="mb-2"><i class="fas fa-calendar-times text-danger me-2"></i><strong>Deadline Ayarlama:</strong> Görev bitiş tarihleri tatilleri atlayarak hesaplanır</li>
                    <li class="mb-2"><i class="fas fa-chart-line text-info me-2"></i><strong>Kapasite Düzeltmesi:</strong> Tatil günlerinde 0 kapasite olarak gösterilir</li>
                    <li class="mb-2"><i class="fas fa-users text-success me-2"></i><strong>Ekip Takvimi:</strong> Kimin ne zaman izinde olduğu görünür</li>
                </ul>`
            },
            {
                heading: 'Proje Yönetimine Katkısı',
                content: `<div class="alert alert-secondary mb-0">
                    <p class="mb-2"><strong>📅 Gerçekçi Planlama:</strong> Tatiller ve izinler göz önüne alınarak deadline belirlenir</p>
                    <p class="mb-2"><strong>🌍 Global Projeler:</strong> Farklı ülkelerin resmi tatilleri tek sistemde yönetilir</p>
                    <p class="mb-2"><strong>⏳ Efor Hesabı:</strong> CPM ve baseline hesaplamalarında net çalışma günü kullanılır</p>
                    <p class="mb-0"><strong>👥 Ekip Koordinasyonu:</strong> İzinli kişiler göz önünde tutularak atama yapılır</p>
                </div>`
            }
        ]
    }
};

function closeToolInfoModal() {
  var overlay = document.getElementById("tool-info-overlay");
  if (!overlay) return;
  overlay.classList.remove("open");
  overlay.setAttribute("aria-hidden", "true");
  document.body.style.overflow = "";
}

function showToolInfo(toolKey) {
  var tool = TOOL_INFO_DATA[toolKey];
  if (!tool) return;
  var overlay = document.getElementById("tool-info-overlay");
  var titleEl = document.getElementById("toolInfoTitle");
  var bodyEl = document.getElementById("toolInfoBody");
  if (!overlay || !titleEl || !bodyEl) return;
  titleEl.innerHTML = '<i class="' + tool.icon + '"></i><span>' + tool.title + "</span>";
  var sectionsHtml = "";
  var colors = {
    primary: "#4f46e5",
    danger: "#dc2626",
    warning: "#d97706",
    success: "#16a34a",
    info: "#0284c7",
    secondary: "#64748b",
  };
  var hc = colors[tool.color] || colors.primary;
  tool.sections.forEach(function (section) {
    sectionsHtml +=
      '<div class="tool-info-section"><h5 class="tool-info-section-title" style="color:' +
      hc +
      ';"><i class="fas fa-chevron-right"></i>' +
      section.heading +
      '</h5><div class="tool-info-body-inner">' +
      section.content +
      "</div></div>";
  });
  bodyEl.innerHTML = sectionsHtml;
  overlay.classList.add("open");
  overlay.setAttribute("aria-hidden", "false");
  document.body.style.overflow = "hidden";
}

document.addEventListener("DOMContentLoaded", function () {
  var overlay = document.getElementById("tool-info-overlay");
  if (!overlay) return;
  overlay.addEventListener("click", function (e) {
    if (e.target === overlay) closeToolInfoModal();
  });
  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape" && overlay.classList.contains("open")) closeToolInfoModal();
  });
});

})();
