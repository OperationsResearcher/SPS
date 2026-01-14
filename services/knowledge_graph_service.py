# -*- coding: utf-8 -*-
"""
Bilgi Grafığı Servisi
Stratejiler, süreçler, projeler arasındaki ilişkileri yönetmek için
"""
from typing import Dict, List, Optional


def build_knowledge_graph_data(strategies, processes, projects) -> Dict:
    """
    Bilgi grafığı için veri yapısı oluştur
    
    Args:
        strategies: AltStrateji listesi
        processes: Surec listesi
        projects: Project listesi
    
    Returns:
        Vis.js network için uygun veri yapısı
    """
    nodes = []
    edges = []
    
    # Node ID'leri için counter
    node_id_counter = 1
    node_id_map = {}  # (type, id) -> node_id mapping
    
    # Stratejileri node olarak ekle
    for strategy in strategies:
        node_id = node_id_counter
        node_id_map[('strategy', strategy.id)] = node_id
        nodes.append({
            'id': node_id,
            'label': strategy.alt_strateji_adi or f'Strateji {strategy.id}',
            'group': 'strategy',
            'color': '#667eea',
            'shape': 'box',
            'level': 1
        })
        node_id_counter += 1
    
    # Süreçleri node olarak ekle
    for process in processes:
        node_id = node_id_counter
        node_id_map[('process', process.id)] = node_id
        nodes.append({
            'id': node_id,
            'label': process.surec_adi or f'Süreç {process.id}',
            'group': 'process',
            'color': '#198754',
            'shape': 'ellipse',
            'level': 2
        })
        node_id_counter += 1
    
    # Projeleri node olarak ekle
    for project in projects:
        node_id = node_id_counter
        node_id_map[('project', project.id)] = node_id
        nodes.append({
            'id': node_id,
            'label': project.name or f'Proje {project.id}',
            'group': 'project',
            'color': '#fd7e14',
            'shape': 'diamond',
            'level': 3
        })
        node_id_counter += 1
    
    # İlişkileri edge olarak ekle
    # Not: Gerçek ilişkiler StrategyProcessMatrix ve project_related_processes'den alınabilir
    
    return {
        'nodes': nodes,
        'edges': edges
    }


def find_related_items(item_type: str, item_id: int, strategies=None, processes=None, projects=None) -> List[Dict]:
    """
    Bir öğeye ilişkili diğer öğeleri bul
    
    Args:
        item_type: 'strategy', 'process', veya 'project'
        item_id: Öğe ID'si
        strategies: AltStrateji listesi (opsiyonel)
        processes: Surec listesi (opsiyonel)
        projects: Project listesi (opsiyonel)
    
    Returns:
        İlişkili öğelerin listesi
    """
    related_items = []
    
    # Bu fonksiyon gerçek veritabanı sorgularıyla genişletilebilir
    # Şu an için placeholder
    
    return related_items


def calculate_centrality_metrics(nodes: List[Dict], edges: List[Dict]) -> Dict:
    """
    Graf merkezilik metrikleri hesapla
    
    Args:
        nodes: Node listesi
        edges: Edge listesi
    
    Returns:
        Merkezilik metrikleri (degree centrality, betweenness centrality, vb.)
    """
    # Basit degree centrality hesaplama
    degree_centrality = {}
    
    for node in nodes:
        node_id = node['id']
        degree = sum(1 for edge in edges if edge.get('from') == node_id or edge.get('to') == node_id)
        degree_centrality[node_id] = degree
    
    # En merkezi node'ları bul
    if degree_centrality:
        max_degree = max(degree_centrality.values())
        central_nodes = [node_id for node_id, degree in degree_centrality.items() if degree == max_degree]
    else:
        central_nodes = []
    
    return {
        'degree_centrality': degree_centrality,
        'max_degree': max(degree_centrality.values()) if degree_centrality else 0,
        'central_nodes': central_nodes
    }


def suggest_connections(strategies, processes, projects) -> List[Dict]:
    """
    Eksik ilişkiler için öneriler oluştur
    
    Args:
        strategies: AltStrateji listesi
        processes: Surec listesi
        projects: Project listesi
    
    Returns:
        Önerilen bağlantılar listesi
    """
    suggestions = []
    
    # Bu fonksiyon gerçek analizlerle genişletilebilir
    # Şu an için placeholder
    
    return suggestions




