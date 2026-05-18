"""Marketing (tanıtım) modülü — Blueprint burada tanımlanır."""
import os
from flask import Blueprint

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.abspath(os.path.join(_HERE, "..", "..", ".."))

marketing_bp = Blueprint(
    "marketing_bp",
    __name__,
    template_folder=os.path.join(_ROOT, "templates", "marketing"),
    static_folder=os.path.join(_ROOT, "static", "marketing"),
    static_url_path="/static/marketing",
)
