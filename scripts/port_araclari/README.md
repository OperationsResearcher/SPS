# port_araclari — KalDer → Kokpitim ana proje aktarım araçları

> Amaç: KalDer'de yapılan UX / erişilebilirlik / i18n işlerini **ana Kokpitim projesine** aktarırken kullanılan, şablona özel
> çıktı üreten araçlar. Çıktı (sınıf adları, çeviri listesi) şablona özel olduğu için **kopyalanmaz, hedefte yeniden üretilir**.
> Tüm araçlar **hedef projenin kök dizininden** (`cd C:\kokpitim`) çalıştırılır; yollar `ui/templates/platform/...` göreli.
> Hepsi Kokpitim ana projesinde de geçerli düzene (`ui/templates/platform`, `ui/static/platform/css`, `translations/`) göre yazıldı.

## Dosyalar
| Dosya | Ne yapar |
|---|---|
| `g_arac.py` | Statik `style="…"` → sınıf (`st-<ek>-NNN`), CSS'i `g_*.css`'e yazar, şablona `<link>` ekler. Yazar: `python g_arac.py <sablon_rel.html> <ek> <css_adi.css>` (örn. `surec/index.html st-si g_surec_index.css`). Gizli başlangıçlı (`display:none` vb.), Jinja'lı değer, `url()`, `!important` inline kalır |
| `dogrula.py` | `g_arac` çıktısını doğrular: HEAD ile (etiket, **efektif stil**) dizisi birebir eşit mi. `python dogrula.py <bu_klasor> <sablon.html> <css> [...]` |
| `g_i18n.py` | Sabit Türkçe metin / `title`/`placeholder`/`aria-label` / breadcrumb `'label'` / blok başlığını `{{ _("…") }}` ile sarar (`%` → `%%`). `python g_i18n.py <sablon_rel.html> [...]` |
| `label_hepsi.py`, `say.py` | Tüm temiz şablonlarda yalnız breadcrumb etiketlerini sar / sarılacak metin sayısını say |
| `yuzde.py` | `_()` içinde kaçışsız tek `%` arar (newstyle gettext `%` biçimlendirir → `ValueError`) |
| `yeni_msgid.py`, `map_idx.py`, `ceviri_ekle.py` | Çıkarımda yeni çıkan msgid'leri listele / çeviri eşlemesi / `.po`+`.mo`'ya ekle (HEAD+WIP güvenli) |
| `uxtest_kur.py` | Test kurumu + kullanıcıları (rastgele parola) oluşturur, `uxtest.json` yazar (**parola içerir, commit etme, işin sonunda sil**) |
| `pw_ortak.py`, `pw_tara.py`, `pw_en.py`, `pw_a11y.py`, `pw_b6.py`, `pw_b7.py` | Playwright tarayıcı kontrolleri: sayfa tarama (HTTP/konsol/404/yatay taşma, açık+koyu, mobil), EN'de Türkçe kalan metin, a11y (odak halkası, etiketsiz alan, modal), plan yılı API'leri, yükleme/XSS/oran sınırı |

## Kullanım notu (Playwright)
`pip install playwright && playwright install chromium` — `pw_*.py` ilk argüman olarak **`uxtest.json`'un bulunduğu klasörü** alır
(örn. `python scripts/port_araclari/pw_tara.py scripts/port_araclari light`). `BASE` ortam değişkeni ile sunucu adresi verilir
(varsayılan `http://127.0.0.1:5001`). Karşılaştırma için baseline'ı ayrı portta `git worktree` ile ayağa kaldırıp `OUT=eskiss` ile
ekran görüntüsü alınır.

## Tuzaklar
- Heredoc'ta `\\` / `\r\n` bozulur → ters bölü içeren betiği dosyaya `Write` ile yaz.
- Şablonların çoğu CRLF, bazıları UTF-8 BOM'lu (araçlar bunu korur).
- `pybabel update` elle koşma → `scripts/ops/i18n_cikar.py` (inline-JS `t()` ve `_l` çıkarımını da yapar).
