# -*- coding: utf-8 -*-
"""Main blueprint — modüler route paketi (Dalga C)."""
from flask import Blueprint

main_bp = Blueprint("main", __name__)

from main.routes import _common  # noqa: F401
from main.routes import pages  # noqa: F401
from main.routes import kurum_panel  # noqa: F401
from main.routes import strategy_api  # noqa: F401
from main.routes import projects  # noqa: F401
