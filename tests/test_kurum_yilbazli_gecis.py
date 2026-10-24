"""kurum_yilbazli_gecis.py güvenlik kilidi: yedek onayı olmadan uygulama reddedilir."""
import subprocess
import sys


def test_calistir_yedek_onaysiz_reddedilir():
    r = subprocess.run([sys.executable, "scripts/ops/kurum_yilbazli_gecis.py", "--tenant", "16", "--calistir"],
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    assert r.returncode != 0
    assert "yedek-onay" in (r.stderr + r.stdout)


def test_adim_sirasi_degismez():
    sys.path.insert(0, "scripts/ops")
    import kurum_yilbazli_gecis as g
    assert [a[1].split("/")[-1] for a in g.ADIMLAR] == [
        "yilbazli_faz1_2_clone_zinciri.py", "yilbazli_faz1_2b_karisik_pg_duzelt.py",
        "yilbazli_faz1_5_kpi_data_remap.py", "yilbazli_faz1_4_override_goc.py"]
