"""Stratejik Planlama — rotalar alt modüllerde kayıtlıdır."""

from micro.modules.sp import routes_pages  # noqa: F401
from micro.modules.sp import routes_strategy  # noqa: F401
from micro.modules.sp import routes_flow  # noqa: F401
from micro.modules.sp import routes_plan_year  # noqa: F401
from micro.modules.sp import routes_donemler  # noqa: F401
from micro.modules.sp import routes_sp_proje  # noqa: F401
from micro.modules.sp import routes_analysis  # noqa: F401
from micro.modules.sp import routes_initiative  # noqa: F401  Sprint 55 (Ö4)
from micro.modules.sp import routes_scenario  # noqa: F401  Sprint 56 (Ö5)
from micro.modules.sp import routes_replan_trigger  # noqa: F401  Sprint 57 (Ö8)
from micro.modules.sp import routes_exec_advisor  # noqa: F401  Sprint 58 (Exec Dashboard + AI Pivot + Templates)
from micro.modules.sp import routes_frameworks  # noqa: F401  Sprint 59-63 (Hoshin, Blue Ocean, VRIO, EVM, Digest)
from micro.modules.sp import routes_llm_quota  # noqa: F401  LLM kota & kullanım paneli
from micro.modules.sp import routes_tenant_ai  # noqa: F401  Tenant BYOK ayarları
