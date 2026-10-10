"""PERF-04 — js_i18n_map katalog dolaşımı çeviri nesnesi başına bir kez yapılır."""
from flask_babel import force_locale

from app.i18n import js_i18n_map


def test_en_haritasi_onbellekten_gelir(app):
    with app.test_request_context("/"):
        with force_locale("en"):
            ilk = js_i18n_map()
            ikinci = js_i18n_map()
    assert ilk and ilk is ikinci


def test_varsayilan_dilde_bos(app):
    with app.test_request_context("/"):
        with force_locale("tr"):
            assert js_i18n_map() == {}
