"""
Admin panele Silinmiş Kurumlar tab'ı ve içeriği ekle
"""
with open('templates/admin_panel.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Kurumlar tab'ından sonra Silinmiş Kurumlar tab'ı ekleyeceğiz
# Önce Kullanıcılar tab'ını bulalım
users_tab_marker = '<button class="nav-link" id="users-tab" data-bs-toggle="tab" data-bs-target="#users"'

if users_tab_marker in content:
    # Kullanıcılar tab'ından önce Silinmiş Kurumlar tab'ı ekle
    new_tab = '''                        <li class="nav-item" role="presentation">
                            <button class="nav-link" id="deleted-organizations-tab" data-bs-toggle="tab" data-bs-target="#deleted-organizations" type="button" role="tab" aria-controls="deleted-organizations" aria-selected="false">
                                <i class="fas fa-archive me-2"></i>Silinmiş Kurumlar
                            </button>
                        </li>
                        '''
    
    # Tab ekle
    insert_pos = content.find(users_tab_marker) - 100  # <li> tag'ının başına git
    # Geriye git ve <li> bul
    li_start = content.rfind('<li class="nav-item"', 0, insert_pos)
    
    content = content[:li_start] + new_tab + content[li_start:]
    print("✓ Silinmiş Kurumlar tab'ı eklendi")
    
    # Şimdi tab content'i ekleyelim - tab-pane için yer bulalım
    # #users tab-pane'inden önce ekleyelim
    users_pane_marker = '<div class="tab-pane fade" id="users"'
    
    if users_pane_marker in content:
        new_pane = '''                    <!-- Silinmiş Kurumlar Tab -->
                    <div class="tab-pane fade" id="deleted-organizations" role="tabpanel" aria-labelledby="deleted-organizations-tab">
                        <div class="d-flex justify-content-between align-items-center mb-4">
                            <h3 class="mb-0">Silinmiş Kurumlar</h3>
                            <button class="btn btn-sm btn-outline-secondary" onclick="loadDeletedOrganizations()">
                                <i class="fas fa-sync-alt me-2"></i>Yenile
                            </button>
                        </div>
                        
                        <div id="deleted-organizations-loading" class="text-center py-5">
                            <div class="spinner-border text-primary" role="status">
                                <span class="visually-hidden">Yükleniyor...</span>
                            </div>
                            <p class="mt-3">Silinmiş kurumlar yükleniyor...</p>
                        </div>
                        
                        <div id="deleted-organizations-content" style="display: none;">
                            <div class="table-responsive">
                                <table class="table table-hover">
                                    <thead>
                                        <tr>
                                            <th>Kurum Adı</th>
                                            <th>Ticari Ünvan</th>
                                            <th>Silinme Tarihi</th>
                                            <th>Silen Kişi</th>
                                            <th>Kullanıcı</th>
                                            <th>Süreç</th>
                                            <th class="text-end">İşlemler</th>
                                        </tr>
                                    </thead>
                                    <tbody id="deleted-organizations-table-body">
                                        <!-- JavaScript ile doldurulacak -->
                                    </tbody>
                                </table>
                            </div>
                            
                            <div id="deleted-organizations-empty" class="alert alert-info" style="display: none;">
                                <i class="fas fa-info-circle me-2"></i>
                                Silinmiş kurum bulunmuyor.
                            </div>
                        </div>
                    </div>

                    '''
        
        pane_insert_pos = content.find(users_pane_marker)
        content = content[:pane_insert_pos] + new_pane + content[pane_insert_pos:]
        print("✓ Silinmiş Kurumlar tab content'i eklendi")
    else:
        print("✗ users pane bulunamadı")
else:
    print("✗ users tab bulunamadı")

# Kaydet
with open('templates/admin_panel.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("✓ Dosya kaydedildi")
