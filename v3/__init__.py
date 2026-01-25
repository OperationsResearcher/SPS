from flask import Blueprint

# Blueprint tanımı
v3_bp = Blueprint('v3', __name__, url_prefix='/v3')

# Routes'u import et (circular import'u önlemek için en sonda)
from . import routes
