# -*- coding: utf-8 -*-
"""Merkezi tenant izolasyonu (fablerapor Faz 1).

Sorun: tenant izolasyonu ~400+ route'ta elle yazılan `filter(tenant_id == ...)`
ile sağlanıyor; tek unutulan filtre cross-tenant veri sızıntısı demek.

Çözüm: SQLAlchemy `do_orm_execute` + `with_loader_criteria` (resmi reçete).
`TenantScopedMixin` taşıyan her modelin SELECT'ine, istek bağlamındaki
kullanıcının erişebildiği tenant id'leri otomatik AND'lenir. Mevcut elle
filtreler bozulmaz (kriter eklemeli çalışır).

Mod (config TENANT_GUARD_MODE):
    off      → dinleyici kayıt edilmez (varsayılan — kademeli devreye alma)
    enforce  → filtre uygulanır

Muafiyetler:
    - request context dışı çalışmalar (CLI, Celery, scheduler, testler app ctx)
    - anonim kullanıcı (login, marketing, demo başlangıcı)
    - platform admin (sistem_rol == 'admin')
    - tenant_id'si olmayan kullanıcı
    - `db.session.execute(stmt, execution_options={"tenant_guard_bypass": True})`
      veya query.execution_options(tenant_guard_bypass=True) ile açık bypass

Holding/bayi: kullanıcının tenant'ı holding/dealer ise alt kurum id'leri de
erişilebilir sete dahil edilir (Holding Dashboard drilldown bozulmaz).
"""
from sqlalchemy import Column, Integer, event
from sqlalchemy.orm import Session, declared_attr, with_loader_criteria


class TenantScopedMixin:
    """tenant_id kolonu taşıyan ve otomatik tenant filtresine girecek modeller
    bu mixin'i alır.

    declared_attr, with_loader_criteria lambda'sının mixin üzerinden attribute
    çözebilmesi için gerekli; modeller kendi tenant_id kolonlarını (FK'lı)
    tanımladığından bu tanım fiilen hiçbir tabloda materialize olmaz."""

    __tenant_guard__ = True

    @declared_attr
    def tenant_id(cls):
        return Column(Integer)


def _allowed_tenant_ids():
    """İstekteki kullanıcının erişebildiği tenant id seti (g üzerinde cache'li).

    None dönerse filtre uygulanmaz (muafiyet)."""
    from flask import g, has_request_context

    if not has_request_context():
        return None

    from flask_login import current_user

    # ⚠ 2026-07-21: KİLİT KENDİNİ YİYORDU — guard hiçbir zaman devreye girmiyordu.
    #
    # Eski akış: cache `g` üzerinde tutuluyordu ve özyineleme kilidi olarak
    # `g._tenant_guard_ids = None` yazılıyordu. Ama istek başında, kullanıcı
    # HENÜZ YÜKLENMEDEN (Flask-Login `current_user`'ı lazy çözer) bir ORM
    # sorgusu tetiklenince:
    #     1. _allowed_tenant_ids() çağrılır, kullanıcı anonim → ids = None
    #     2. `g._tenant_guard_ids = None` YAZILIR ve İSTEK BOYUNCA KALIR
    #     3. Sonraki her çağrı `cached is not False` → None döner → filtre YOK
    #
    # Ölçüldü: enforce modunda t16 kullanıcısı filtresiz sorguda 503 süreç
    # görüyordu (kendi kurumunda 77 var). Cache elle temizlenince 77'ye
    # düşüyordu — yani mekanizma doğru, yalnız cache mantığı bozuktu.
    #
    # Çözüm: anonim/çözümlenemeyen durum CACHE'LENMEZ; kilit AYRI bir bayrak.
    #
    # ⚠ KİLİT EN BAŞTA — `current_user`'a DOKUNMADAN ÖNCE.
    # Flask-Login `current_user`'ı LAZY çözer: `is_authenticated` okumak
    # kullanıcıyı DB'den yükleten bir ORM sorgusu tetikler, o sorgu da bu
    # dinleyiciyi yeniden çağırır. Kilit `is_authenticated`'dan sonra
    # konursa SONSUZ ÖZYİNELEME olur (RecursionError — ilk denememde
    # 26 test bu yüzden kırıldı).
    if g.get("_tenant_guard_lock", False):
        return None  # re-entrant çağrı — filtresiz geç

    cached = g.get("_tenant_guard_ids", False)
    if cached is not False:
        return cached

    g._tenant_guard_lock = True
    ids = None
    kimlikli = False
    try:
        kimlikli = getattr(current_user, "is_authenticated", False)
        if kimlikli:
            tid = getattr(current_user, "tenant_id", None)
            if tid is not None and current_user.sistem_rol != "admin":
                ids = [tid]
                tenant = getattr(current_user, "tenant", None)
                if tenant is not None and getattr(tenant, "tenant_type", "normal") in ("holding", "dealer"):
                    from app.models.core import Tenant

                    children = (
                        Session.object_session(tenant) or _fallback_session()
                    ).query(Tenant.id).filter(Tenant.parent_tenant_id == tid).all()
                    ids.extend(c[0] for c in children)
    except Exception:
        # Guard hiçbir isteği kırmamalı: karar verilemiyorsa filtre uygulanmaz,
        # mevcut elle filtreler devrede kalır.
        import logging

        logging.getLogger(__name__).warning("[tenant-guard] scope resolution failed", exc_info=True)
        ids = None
    finally:
        # Kilit MUTLAKA bırakılmalı; istisna hâlinde bile.
        g._tenant_guard_lock = False

    # Yalnız kimliği ÇÖZÜLMÜŞ kullanıcı için cache'le.
    #
    # Anonim sonucu (None) cache'lemek, kullanıcı istek ortasında
    # yüklendiğinde guard'ı İSTEK BOYUNCA devre dışı bırakırdı — eski kodun
    # hatası tam olarak buydu (ölçüm: enforce'ta bile 503 süreç sızıyordu,
    # kurumun kendi verisi 77).
    #
    # `kimlikli` yukarıda KİLİT ALTINDAYKEN hesaplandı; burada `current_user`a
    # tekrar dokunmuyoruz (yine özyineleme riski olurdu).
    if kimlikli:
        g._tenant_guard_ids = ids
    return ids


def _fallback_session():
    from extensions import db

    return db.session


_listener_registered = False


def _guard_enabled():
    """Mod çalışma anında, istek bağlamındaki app config'inden okunur.

    Dinleyici global Session sınıfına kaydolduğu için (çoklu app / test
    izolasyonu) karar kayıt anında verilemez."""
    from flask import current_app, has_request_context

    if not has_request_context():
        return False
    return (current_app.config.get("TENANT_GUARD_MODE") or "off").lower() == "enforce"


def init_tenant_guard(app, db):
    """create_app içinden çağrılır; dinleyici süreç başına bir kez kaydolur."""
    global _listener_registered
    if _listener_registered:
        return
    _listener_registered = True

    @event.listens_for(Session, "do_orm_execute")
    def _apply_tenant_criteria(execute_state):
        if not execute_state.is_select:
            return
        if execute_state.is_column_load or execute_state.is_relationship_load:
            return
        if execute_state.execution_options.get("tenant_guard_bypass", False):
            return
        if not _guard_enabled():
            return

        allowed = _allowed_tenant_ids()
        if not allowed:
            return

        execute_state.statement = execute_state.statement.options(
            with_loader_criteria(
                TenantScopedMixin,
                lambda cls: cls.tenant_id.in_(allowed),
                include_aliases=True,
                track_closure_variables=False,
            )
        )
