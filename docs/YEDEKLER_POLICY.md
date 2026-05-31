# Yedekler Klasörü Politikası

`Yedekler/` ve kök `*.zip` dosyaları `.gitignore` ile repoya alınmaz.

## Önerilen kullanım

| Tür | Konum | Git |
|-----|--------|-----|
| Kod anlık görüntüsü | Git dal/etiket (`19mayisyedek`) | Evet |
| DB / dosya yedeği | `Yedekler/` veya harici disk | Hayır |
| Ayarlar zip | `Yedekler/Kokpitim_Ayarlar_*.zip` | Hayır |

## Temizlik

- 90 günden eski zip’leri arşiv diske taşıyın veya silin.
- Tam set snapshot’ları tek etiket + tek zip ile sınırlayın; her commit’te kopyalamayın.

## Geri dönüş (kod)

`docs/19MAYISYEDEK_RESTORE.md` ve `scripts/ops/restore_19mayisyedek.ps1`
