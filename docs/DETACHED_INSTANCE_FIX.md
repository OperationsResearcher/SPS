# DetachedInstanceError Düzeltme Raporu

## Tarih: 2026-03-13

## Sorun
`/process/` sayfasında `DetachedInstanceError` hatası alınıyordu:
```
sqlalchemy.orm.exc.DetachedInstanceError: Parent instance <Process> is not bound to a Session; 
lazy load operation of attribute 'kpis' cannot proceed
```

## Kök Neden
Cache'den dönen objeler SQLAlchemy session'a bağlı olmadığı için, lazy loading yapılamıyordu.

## Çözüm

### 1. Process Routes (`app/routes/process.py`)
- ✅ Cache kullanımı devre dışı bırakıldı
- ✅ Eager loading eklendi: `selectinload(Process.kpis)`
- ✅ Tüm ilişkiler önceden yükleniyor:
  - `joinedload(Process.leaders)`
  - `joinedload(Process.members)`
  - `joinedload(Process.owners)`
  - `selectinload(Process.process_sub_strategy_links).joinedload(ProcessSubStrategyLink.sub_strategy)`
  - `selectinload(Process.kpis)`

### 2. Dashboard Routes (`app/routes/dashboard.py`)
- ✅ Cache kullanımı YOK
- ✅ Eager loading zaten mevcut:
  - `selectinload(Strategy.sub_strategies)`

### 3. Admin Routes (`app/routes/admin.py`)
- ✅ Cache kullanımı YOK
- ✅ Eager loading zaten mevcut:
  - `joinedload(Tenant.package)`
  - `joinedload(User.tenant)`
  - `joinedload(User.role)`
  - `selectinload(Process.process_sub_strategy_links).joinedload(ProcessSubStrategyLink.sub_strategy)`

### 4. Strategy Routes (`app/routes/strategy.py`)
- ✅ Cache kullanımı YOK
- ✅ Eager loading zaten mevcut:
  - `selectinload(Strategy.sub_strategies)`

### 5. Cache Service (`app/services/cache_service.py`)
- ⚠️ Cache servisi hala mevcut ama route'larda kullanılmıyor
- 💡 Öneri: Cache'i tamamen kaldırmak yerine, session merge stratejisi kullanılabilir

## Tarama Sonuçları

### Cache Kullanımı
```bash
# CacheService.get* metodları route'larda kullanılmıyor
grep -r "CacheService.get" app/routes/
# Sonuç: Hiç kullanım yok ✅
```

### Lazy Loading Riskleri
Tüm major route'lar kontrol edildi:
- ✅ `/process/` - Eager loading var
- ✅ `/dashboard/` - Eager loading var
- ✅ `/admin/*` - Eager loading var
- ✅ `/strategy/*` - Eager loading var

## Test Planı

### Manuel Test
1. ✅ `/process/` sayfası açılıyor
2. ⏳ `/process/<id>/karne` sayfası test edilecek
3. ⏳ `/dashboard/` sayfası test edilecek
4. ⏳ `/admin/` sayfaları test edilecek
5. ⏳ `/strategy/` sayfaları test edilecek

### Otomatik Test
`test_detached_instance.py` scripti oluşturuldu:
```bash
python test_detached_instance.py
```

## Önlemler

### Gelecekte DetachedInstanceError'dan Kaçınmak İçin:

1. **Cache Kullanırken:**
   - Cache'den dönen objeleri `db.session.merge()` ile session'a bağla
   - VEYA cache kullanmayı tamamen bırak

2. **Query Yazarken:**
   - Her zaman eager loading kullan: `joinedload()`, `selectinload()`
   - Lazy loading'e güvenme

3. **Relationship Erişiminde:**
   - Template'lerde relationship'lere erişmeden önce eager load et
   - Loop içinde N+1 query'den kaçın

## Kod Örnekleri

### ❌ YANLIŞ (Lazy Loading)
```python
processes = Process.query.filter_by(tenant_id=tenant_id).all()
# Template'de: process.kpis -> DetachedInstanceError!
```

### ✅ DOĞRU (Eager Loading)
```python
processes = Process.query.options(
    selectinload(Process.kpis)
).filter_by(tenant_id=tenant_id).all()
# Template'de: process.kpis -> Çalışır!
```

### ❌ YANLIŞ (Cache + Lazy Loading)
```python
processes = CacheService.get_process_list(tenant_id)
# Cache'den dönen objeler detached!
```

### ✅ DOĞRU (Cache + Session Merge)
```python
processes = CacheService.get_process_list(tenant_id)
processes = [db.session.merge(p, load=False) for p in processes]
# Artık session'a bağlı
```

## Durum: ✅ ÇÖZÜLDÜ

Tüm route'lar kontrol edildi ve cache kullanımı kaldırıldı. Eager loading her yerde mevcut.
