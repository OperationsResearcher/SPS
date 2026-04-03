"""PostgreSQL sequence hizalama aracı.

Import / dump sonrası kpi_data birincil anahtar çakışması gibi hatalarda sekanslar geride kalabilir.
Bu betik MAX(id) ile hizalar.

Kullanım:
    python scripts/fix_postgres_sequences.py
"""

from app import create_app
from app.models import db
from app.utils.db_sequence import sync_many_sequences


TABLES = [
    ("processes", "id"),
    ("process_kpis", "id"),
    ("kpi_data", "id"),
    ("kpi_data_audits", "id"),
    ("process_activities", "id"),
    ("process_activity_reminders", "id"),
    ("activity_tracks", "id"),
    ("notifications", "id"),
    ("individual_performance_indicators", "id"),
    ("individual_activities", "id"),
    ("individual_kpi_data", "id"),
    ("individual_activity_tracks", "id"),
    ("individual_kpi_data_audits", "id"),
    ("project", "id"),
    ("task", "id"),
    ("raid_item", "id"),
    ("project_risk", "id"),
    ("working_day", "id"),
    ("capacity_plan", "id"),
    ("recurring_task", "id"),
    ("task_baseline", "id"),
    ("integration_hook", "id"),
    ("rule_definition", "id"),
    ("sla", "id"),
    ("strategies", "id"),
    ("sub_strategies", "id"),
]


def main() -> None:
    app = create_app()
    with app.app_context():
        result = sync_many_sequences(TABLES)
        db.session.commit()
        ok = [k for k, v in result.items() if v]
        fail = [k for k, v in result.items() if not v]
        print("Sequence sync tamamlandi.")
        print(f"Basarili: {len(ok)}")
        for k in ok:
            print(f"  + {k}")
        print(f"Atlanan/Basarisiz: {len(fail)}")
        for k in fail:
            print(f"  - {k}")


if __name__ == "__main__":
    main()
