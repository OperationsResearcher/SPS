# -*- coding: utf-8 -*-
"""Legacy strateji tabloları — geçiş katmanı (models.strategy shim)."""
from models.strategy import (  # noqa: F401
    AnaStrateji,
    AltStrateji,
    StrategyProcessMatrix,
    StrategyMapLink,
)

# İngilizce alias (bazı servisler)
MainStrategy = AnaStrateji
SubStrategy = AltStrateji
