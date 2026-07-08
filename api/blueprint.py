# -*- coding: utf-8 -*-
"""API Blueprint tanimi — dairesel import onlemek icin ayri modul."""
from flask import Blueprint

api_bp = Blueprint('api', __name__, url_prefix='/api')
