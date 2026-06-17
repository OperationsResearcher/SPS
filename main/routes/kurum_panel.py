# -*- coding: utf-8 -*-
# Otomatik bölüm — `python scripts/dev/split_main_routes.py`
from main.routes._common import *  # noqa: F401,F403
from main.routes import main_bp
from main.deprecated import legacy_html_to_platform


@main_bp.route('/admin/seed_db')
@login_required
def seed_db():
    """Veritabanına demo veri ekle - Sadece admin için"""
    try:
        # Sadece admin rolü için
        if current_user.sistem_rol != 'admin':
            flash('Bu işlem için yetkiniz yok.', 'error')
            return redirect(url_for('app_bp.masaustu'))
        
        from services.seeder import seed_all
        
        results = seed_all(db)
        
        if results['hata']:
            flash(f'Demo veri oluşturulurken hata oluştu: {results["hata"]}', 'error')
        else:
            flash(
                f'Demo veriler başarıyla oluşturuldu! '
                f'Kurum: {results["kurumlar"]}, Kullanıcı: {results["users"]}, '
                f'Ana Strateji: {results["ana_stratejiler"]}, Alt Strateji: {results["alt_stratejiler"]}, '
                f'Süreç: {results["surecler"]}, Proje: {results["projeler"]}, Görev: {results["gorevler"]}',
                'success'
            )
        
        return redirect(url_for('app_bp.yonetim_paneli'))
    except Exception as e:
        current_app.logger.error(f'Seed DB hatası: {e}')
        flash('Demo veri oluşturulurken bir hata oluştu.', 'error')
        return redirect(url_for('app_bp.yonetim_paneli'))


@main_bp.route('/admin/fix-bsc-schema')
@login_required
def fix_bsc_schema():
    """BSC kolonlarını ve bağlantı tablosunu veri kaybı olmadan ekler."""
    if current_user.sistem_rol != 'admin':
        flash('Bu işlem için yetkiniz yok.', 'danger')
        return redirect(url_for('main.dashboard'))

    try:
        from sqlalchemy import text

        with db.engine.connect() as conn:
            table_info = conn.execute(text("PRAGMA table_info('ana_strateji')")).fetchall()
            existing_columns = {row[1] for row in table_info}

            if 'perspective' not in existing_columns:
                conn.execute(text("ALTER TABLE ana_strateji ADD COLUMN perspective VARCHAR(20)"))
            if 'bsc_code' not in existing_columns:
                conn.execute(text("ALTER TABLE ana_strateji ADD COLUMN bsc_code VARCHAR(10)"))
            conn.commit()

        with db.engine.connect() as conn:
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS strategy_map_link (
                    id INTEGER PRIMARY KEY,
                    source_id INTEGER NOT NULL,
                    target_id INTEGER NOT NULL,
                    connection_type VARCHAR(30) NOT NULL DEFAULT 'CAUSE_EFFECT',
                    UNIQUE(source_id, target_id),
                    FOREIGN KEY(source_id) REFERENCES ana_strateji(id),
                    FOREIGN KEY(target_id) REFERENCES ana_strateji(id)
                )
            """))
            conn.commit()

        return "BSC şeması güncellendi. <a href='/bsc/map/%d'>BSC Haritası</a>" % current_user.kurum_id
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'BSC şema güncelleme hatası: {e}', exc_info=True)
        return f"Hata: {str(e)}", 500

@main_bp.route('/portfoy-ozeti')
@login_required
def portfolio_summary():
    try:
        return render_template('projects/portfolio.html')
    except Exception as e:
        current_app.logger.error(f'Portföy özeti sayfası hatası: {e}')
        return f'Hata: {str(e)}', 500


@main_bp.route('/api/strategic-planning/graph')
@login_required
def api_strategic_planning_graph():
    """Dinamik SP akışı için graf verisini döndürür (nodes/edges + skorlar)."""
    try:
        kurum = current_user.kurum

        def _normalize_score(raw_value, max_value) -> int:
            try:
                if not max_value or float(max_value) <= 0:
                    return 0
                val = int(round((float(raw_value) / float(max_value)) * 100.0))
                return max(0, min(100, val))
            except Exception:
                return 0

        main_strategies = AnaStrateji.query.filter_by(kurum_id=kurum.id).order_by(AnaStrateji.code, AnaStrateji.ad).all()
        sub_strategies = AltStrateji.query.join(AnaStrateji).filter(
            AnaStrateji.kurum_id == kurum.id
        ).order_by(AltStrateji.code, AltStrateji.ad).all()
        processes = Surec.query.filter_by(kurum_id=kurum.id, silindi=False).order_by(Surec.weight.desc(), Surec.code, Surec.ad).all()
        projects = Project.query.filter_by(kurum_id=kurum.id, is_archived=False).order_by(Project.name).all()
        kpis = SurecPerformansGostergesi.query.join(Surec).filter(
            Surec.kurum_id == kurum.id
        ).order_by(Surec.code, SurecPerformansGostergesi.kodu, SurecPerformansGostergesi.ad).all()

        matrix_relations = StrategyProcessMatrix.query.join(AltStrateji).join(AnaStrateji).filter(
            AnaStrateji.kurum_id == kurum.id
        ).all()

        relations_map = {}
        for rel in matrix_relations:
            relations_map[(rel.sub_strategy_id, rel.process_id)] = int(rel.relationship_score or 0)

        # Totals
        process_max_raw = 9 * len(sub_strategies)
        process_totals_raw = {}
        process_scores_norm = {}
        for proc in processes:
            raw_total = 0
            for sub in sub_strategies:
                raw_total += relations_map.get((sub.id, proc.id), 0)
            process_totals_raw[proc.id] = raw_total
            process_scores_norm[proc.id] = _normalize_score(raw_total, process_max_raw)

        sub_max_raw = 9 * len(processes)
        sub_totals_raw = {}
        sub_scores_norm = {}
        for sub in sub_strategies:
            raw_total = 0
            for proc in processes:
                raw_total += relations_map.get((sub.id, proc.id), 0)
            sub_totals_raw[sub.id] = raw_total
            sub_scores_norm[sub.id] = _normalize_score(raw_total, sub_max_raw)

        main_scores_norm = {}
        # main->subs mapping
        subs_by_main = {}
        for sub in sub_strategies:
            subs_by_main.setdefault(sub.ana_strateji_id, []).append(sub)
        for main in main_strategies:
            subs = subs_by_main.get(main.id, [])
            if not subs:
                main_scores_norm[main.id] = 0
                continue
            raw_total = sum(sub_totals_raw.get(s.id, 0) for s in subs)
            main_max_raw = 9 * len(processes) * len(subs)
            main_scores_norm[main.id] = _normalize_score(raw_total, main_max_raw)

        # KPI score: agirlikli_basari_puani (0-5) => 0-100
        kpi_scores_norm = {}
        for kpi in kpis:
            if kpi.agirlikli_basari_puani is None:
                continue
            kpi_scores_norm[kpi.id] = _normalize_score(kpi.agirlikli_basari_puani, 5.0)

        # Nodes / edges for vis-network
        nodes = []
        edges = []
        kurum_panel_url = url_for('main.kurum_paneli')

        def _label_with_score(prefix: str, name: str, score: int) -> str:
            base = f"{prefix} {name}".strip()
            return f"{base}\n({score}%)"

        # Vision node (top level)
        if kurum.vizyon:
            nodes.append({
                'id': 'vision',
                'group': 'vision',
                'shape': 'box',
                'color': '#8b5cf6',
                'label': f"VİZYON\n{kurum.vizyon[:80]}...",
                'title': f"<b>Vizyon</b><br/>{kurum.vizyon}",
                'url': kurum_panel_url,
                'level': 0,
                'font': {'size': 18, 'bold': True}
            })

        # Main strategy nodes
        for main in main_strategies:
            score = main_scores_norm.get(main.id, 0)
            code = (main.code or '').strip()
            prefix = f"{code}" if code else "ANA"
            nodes.append({
                'id': f"main_{main.id}",
                'group': 'main_strategy',
                'shape': 'box',
                'color': '#f97316',
                'label': _label_with_score(prefix, main.ad, score),
                'title': f"<b>{main.ad}</b><br/>Skor: <b>{score}%</b>",
                'url': kurum_panel_url,
                'level': 1,
                'score': score,
            })

        # Sub strategy nodes
        for sub in sub_strategies:
            score = sub_scores_norm.get(sub.id, 0)
            code = (sub.code or '').strip()
            prefix = f"{code}" if code else "ALT"
            nodes.append({
                'id': f"sub_{sub.id}",
                'group': 'sub_strategy',
                'shape': 'box',
                'color': '#0891b2',
                'label': _label_with_score(prefix, sub.ad, score),
                'title': f"<b>{sub.ad}</b><br/>Skor: <b>{score}%</b>",
                'url': kurum_panel_url,
                'level': 2,
                'score': score,
            })
            # main -> sub edge
            edges.append({
                'from': f"main_{sub.ana_strateji_id}",
                'to': f"sub_{sub.id}",
                'arrows': 'to',
                'color': {'color': '#94a3b8'},
                'width': 1,
                'dashes': True,
            })

        # Vision to main strategies edges
        if kurum.vizyon:
            for main in main_strategies:
                edges.append({
                    'from': 'vision',
                    'to': f"main_{main.id}",
                    'arrows': 'to',
                    'color': {'color': '#c084fc'},
                    'width': 3,
                    'dashes': False,
                })

        # Process nodes
        for proc in processes:
            score = process_scores_norm.get(proc.id, 0)
            code = (proc.code or '').strip()
            prefix = f"{code}" if code else "SR"
            nodes.append({
                'id': f"proc_{proc.id}",
                'group': 'process',
                'shape': 'ellipse',
                'color': '#059669',
                'label': _label_with_score(prefix, proc.ad, score),
                'title': f"<b>{proc.ad}</b><br/>Skor: <b>{score}%</b>",
                'url': kurum_panel_url,
                'level': 3,
                'score': score,
            })

        # Sub -> Process edges (A+B)
        for sub in sub_strategies:
            for proc in processes:
                rel_score = relations_map.get((sub.id, proc.id), 0)
                if rel_score not in (3, 9):
                    continue
                label = 'A' if rel_score == 9 else 'B'
                edges.append({
                    'from': f"sub_{sub.id}",
                    'to': f"proc_{proc.id}",
                    'arrows': 'to',
                    'label': f"{label}",
                    'title': f"İlişki Skoru: {rel_score} ({label})",
                    'color': {'color': '#16a34a' if rel_score == 9 else '#f59e0b'},
                    'width': 3 if rel_score == 9 else 1,
                })

        # KPI nodes + Process -> KPI edges
        for kpi in kpis:
            score = kpi_scores_norm.get(kpi.id)
            score_txt = f" ({score}%)" if score is not None else ""
            label = (kpi.kodu or '').strip()
            if label:
                label = f"{label}: {kpi.ad}{score_txt}"
            else:
                label = f"PG: {kpi.ad}{score_txt}"
            nodes.append({
                'id': f"kpi_{kpi.id}",
                'group': 'kpi',
                'shape': 'box',
                'color': '#7c3aed',
                'label': label,
                'title': f"<b>{kpi.ad}</b><br/>Ağırlıklı Puan: <b>{(kpi.agirlikli_basari_puani if kpi.agirlikli_basari_puani is not None else '-')}</b><br/>Skor: <b>{(str(score) + '%' if score is not None else '-')}</b>",
                'url': kurum_panel_url,
                'level': 4,
                'score': score if score is not None else None,
            })
            edges.append({
                'from': f"proc_{kpi.surec_id}",
                'to': f"kpi_{kpi.id}",
                'arrows': 'to',
                'color': {'color': '#c4b5fd'},
                'width': 1,
            })

        # Project nodes + Project -> Process edges
        for project in projects:
            related_processes = list(project.related_processes or [])
            project_raw = sum(process_totals_raw.get(p.id, 0) for p in related_processes)
            project_max = 9 * len(sub_strategies) * len(related_processes)
            project_score = _normalize_score(project_raw, project_max)
            nodes.append({
                'id': f"proj_{project.id}",
                'group': 'project',
                'shape': 'diamond',
                'color': '#f97316',
                'label': _label_with_score('PRJ', project.name, project_score),
                'title': f"<b>{project.name}</b><br/>Skor: <b>{project_score}%</b>",
                'url': kurum_panel_url,
                'level': 4,
                'score': project_score,
            })

            for proc in related_processes:
                edges.append({
                    'from': f"proj_{project.id}",
                    'to': f"proc_{proc.id}",
                    'arrows': 'to',
                    'color': {'color': '#fb923c'},
                    'width': 2,
                })

            # Derived: Project -> SubStrategy edges (only if >0)
            if related_processes:
                max_rel = 9 * len(related_processes)
                for sub in sub_strategies:
                    raw_rel = 0
                    for proc in related_processes:
                        raw_rel += relations_map.get((sub.id, proc.id), 0)
                    if raw_rel <= 0:
                        continue
                    rel_norm = _normalize_score(raw_rel, max_rel)
                    edges.append({
                        'from': f"proj_{project.id}",
                        'to': f"sub_{sub.id}",
                        'arrows': 'to',
                        'label': f"{rel_norm}%",
                        'title': f"Projeden Alt Stratejiye Türetilmiş Etki: {rel_norm}%",
                        'color': {'color': '#a855f7'},
                        'width': 1,
                        'dashes': True,
                    })

        return jsonify({
            'success': True,
            'nodes': nodes,
            'edges': edges,
            'meta': {
                'kurum_id': kurum.id,
                'main_strategies': len(main_strategies),
                'sub_strategies': len(sub_strategies),
                'processes': len(processes),
                'projects': len(projects),
                'kpis': len(kpis),
            }
        })
    except Exception as e:
        import traceback
        current_app.logger.error(f'SP graph API hatası: {e}')
        current_app.logger.error(traceback.format_exc())
        return jsonify({'success': False, 'message': str(e)}), 500


@main_bp.route('/api/ai/insights')
@login_required
def api_ai_insights():
    """AI Insight'ları getir"""
    try:
        from services.ai_service import AIService
        insights = AIService.get_insights_for_user(current_user.id, current_user.kurum_id)
        return jsonify({
            'success': True,
            'insights': insights
        })
    except Exception as e:
        current_app.logger.error(f'AI insights hatası: {e}')
        return jsonify({
            'success': False,
            'message': 'Insight\'lar yüklenemedi',
            'insights': []
        }), 500


@main_bp.route('/api/ai/ask', methods=['POST'])
@login_required
def api_ai_ask():
    """AI'ya soru sor"""
    try:
        data = request.get_json()
        question = data.get('question', '').strip()
        
        if not question:
            return jsonify({
                'success': False,
                'message': 'Lütfen bir soru girin'
            }), 400
        
        from services.ai_service import AIService
        answer = AIService.ask_question(current_user.id, question)
        
        return jsonify({
            'success': True,
            'answer': answer['answer'],
            'suggestions': answer.get('suggestions', [])
        })
    except Exception as e:
        current_app.logger.error(f'AI ask hatası: {e}')
        return jsonify({
            'success': False,
            'message': 'Soru işlenemedi'
        }), 500

        return jsonify({
            'success': False,
            'message': 'Soru işlenemedi'
        }), 500

# ==========================================
# KURUM PANELİ CRUD İŞLEMLERİ
# ==========================================

# --- Ana Strateji ---
