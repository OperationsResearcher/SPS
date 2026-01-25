from flask import Blueprint

v2_bp = Blueprint('v2', __name__, 
                 url_prefix='/v2',
                 template_folder='templates',
                 static_folder='static')

from . import routes
