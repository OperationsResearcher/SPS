"""
deleteOrganization fonksiyonunu bul ve replace et
"""

with open('templates/admin_panel.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Eski kodu bul
old_code = 'async function deleteOrganization(orgAd, orgId) {'

# Yeni kodu hazırla
new_function_start = '''async function deleteOrganization(orgAd, orgId) {
    // Toaster ile onay iste
    const result = await Swal.fire({
        title: 'Kurum Silme',
        html: `<strong>"${orgAd}"</strong> kurumunu silmek istediğinizden emin misiniz?<br><br>` +
              '<div class="alert alert-warning mt-2"><i class="fas fa-exclamation-triangle"></i> Bu işlem geri alınamaz ve kurumdaki tüm kullanıcılar, süreçler ve veriler silinecektir!</div>',
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#dc3545',
        cancelButtonColor: '#6c757d',
        confirmButtonText: 'Tamam',
        cancelButtonText: 'İptal',
        focusCancel: true
    });

    if (result.isConfirmed) {'''

# Fonksiyonun başlangıcını bul
start_index = content.find(old_code)
if start_index == -1:
    print("❌ Fonksiyon başlangıcı bulunamadı!")
    exit(1)

print(f"✓ Fonksiyon bulundu: pozisyon {start_index}")

# "if (confirmed) {" ifadesini bul (fonksiyon içinde)
search_start = start_index + len(old_code)
confirmed_text = 'if (confirmed) {'
confirmed_index = content.find(confirmed_text, search_start, search_start + 2000)

if confirmed_index == -1:
    # Alternatif: result.isConfirmed veya benzeri
    print("❌ 'if (confirmed)' bulunamadı, alternatifler aranıyor...")
    exit(1)

print(f"✓ 'if (confirmed)' bulundu: pozisyon {confirmed_index}")

# Eski kodu çıkar (başlangıçtan if'e kadar)
old_section = content[start_index:confirmed_index + len(confirmed_text)]
print(f"\nEski kod ({len(old_section)} karakter):")
print("="*80)
print(old_section[:500])
print("="*80)

# Yeni kod ile değiştir
new_content = content[:start_index] + new_function_start + content[confirmed_index + len(confirmed_text):]

# Kaydet
with open('templates/admin_panel.html', 'w', encoding='utf-8') as f:
    f.write(new_content)

print("\n✓ Fonksiyon güncellendi ve kaydedildi!")
