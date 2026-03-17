# -*- coding: utf-8 -*-
from flask import Blueprint, render_template, request, jsonify, current_app, abort
from flask_login import login_required, current_user

from extensions import db
from models import AnaStrateji, StrategyMapLink, Kurum

bsc_bp = Blueprint('bsc', __name__)


PERSPECTIVE_ORDER = ['FINANSAL', 'MUSTERI', 'SUREC', 'OGRENME']
PERSPECTIVE_LABELS = {
    'FINANSAL': 'Finansal Perspektif',
    'MUSTERI': 'Müşteri Perspektifi',
    'SUREC': 'İç Süreçler',
    'OGRENME': 'Öğrenme ve Gelişim',
}


def _authorize_kurum(kurum_id: int) -> None:
    if current_user.sistem_rol != 'admin' and current_user.kurum_id != kurum_id:
        abort(403)


def _build_graph(kurum_id: int) -> dict:
    links = (StrategyMapLink.query
             .join(AnaStrateji, StrategyMapLink.source_id == AnaStrateji.id)
             .filter(AnaStrateji.kurum_id == kurum_id)
             .all())
    graph = {}
    for link in links:
        graph.setdefault(link.source_id, set()).add(link.target_id)
    return graph


def _has_path(graph: dict, start_id: int, goal_id: int) -> bool:
    if start_id == goal_id:
        return True
    visited = set()
    stack = [start_id]
    while stack:
        node = stack.pop()
        if node in visited:
            continue
        visited.add(node)
        for nxt in graph.get(node, set()):
            if nxt == goal_id:
                return True
            if nxt not in visited:
                stack.append(nxt)
    return False


@bsc_bp.route('/bsc/map/<int:kurum_id>')
@login_required
def bsc_map(kurum_id):
    _authorize_kurum(kurum_id)
    kurum = Kurum.query.get_or_404(kurum_id)

    strategies = (AnaStrateji.query
                  .filter_by(kurum_id=kurum_id)
                  .order_by(AnaStrateji.code, AnaStrateji.ad)
                  .all())

    links = (StrategyMapLink.query
             .join(AnaStrateji, StrategyMapLink.source_id == AnaStrateji.id)
             .filter(AnaStrateji.kurum_id == kurum_id)
             .all())

    links_payload = [
        {
            'id': link.id,
            'source_id': link.source_id,
            'target_id': link.target_id,
            'connection_type': link.connection_type
        }
        for link in links
    ]

    return render_template(
        'bsc/strategy_map.html',
        kurum=kurum,
        strategies=strategies,
        links=links,
        links_payload=links_payload,
        perspective_order=PERSPECTIVE_ORDER,
        perspective_labels=PERSPECTIVE_LABELS
    )


@bsc_bp.route('/api/bsc/update-perspective', methods=['POST'])
@login_required
def update_perspective():
    payload = request.get_json(silent=True) or request.form
    strategy_id = payload.get('strategy_id')
    perspective = payload.get('perspective')

    if not strategy_id or perspective not in PERSPECTIVE_ORDER:
        return jsonify({'success': False, 'message': 'Geçersiz istek.'}), 400

    strategy = AnaStrateji.query.get(strategy_id)
    if not strategy:
        return jsonify({'success': False, 'message': 'Strateji bulunamadı.'}), 404

    if current_user.sistem_rol != 'admin' and strategy.kurum_id != current_user.kurum_id:
        return jsonify({'success': False, 'message': 'Yetkiniz yok.'}), 403

    strategy.perspective = perspective
    db.session.commit()

    return jsonify({'success': True})


@bsc_bp.route('/api/bsc/link', methods=['POST'])
@login_required
def create_bsc_link():
    payload = request.get_json(silent=True) or request.form
    source_id = payload.get('source_id')
    target_id = payload.get('target_id')
    connection_type = payload.get('connection_type') or 'CAUSE_EFFECT'

    if not source_id or not target_id:
        return jsonify({'success': False, 'message': 'Eksik parametre.'}), 400

    if str(source_id) == str(target_id):
        return jsonify({'success': False, 'message': 'Aynı strateji bağlanamaz.'}), 400

    source = AnaStrateji.query.get(source_id)
    target = AnaStrateji.query.get(target_id)
    if not source or not target:
        return jsonify({'success': False, 'message': 'Strateji bulunamadı.'}), 404

    if source.kurum_id != target.kurum_id:
        return jsonify({'success': False, 'message': 'Kurum uyuşmazlığı.'}), 400

    if current_user.sistem_rol != 'admin' and source.kurum_id != current_user.kurum_id:
        return jsonify({'success': False, 'message': 'Yetkiniz yok.'}), 403

    existing = StrategyMapLink.query.filter_by(source_id=source.id, target_id=target.id).first()
    if existing:
        return jsonify({'success': True, 'link_id': existing.id})

    graph = _build_graph(source.kurum_id)
    graph.setdefault(source.id, set()).add(target.id)
    if _has_path(graph, target.id, source.id):
        return jsonify({'success': False, 'message': 'Döngüsel bağlantı engellendi.'}), 400

    link = StrategyMapLink(
        source_id=source.id,
        target_id=target.id,
        connection_type=connection_type
    )
    db.session.add(link)
    db.session.commit()

    return jsonify({'success': True, 'link_id': link.id})


@bsc_bp.route('/api/bsc/link/<int:link_id>', methods=['DELETE'])
@login_required
def delete_bsc_link(link_id):
    link = StrategyMapLink.query.get_or_404(link_id)
    source = AnaStrateji.query.get(link.source_id)
    if not source:
        return jsonify({'success': False, 'message': 'Kaynak strateji bulunamadı.'}), 404

    if current_user.sistem_rol != 'admin' and source.kurum_id != current_user.kurum_id:
        return jsonify({'success': False, 'message': 'Yetkiniz yok.'}), 403

    db.session.delete(link)
    db.session.commit()

    return jsonify({'success': True})
