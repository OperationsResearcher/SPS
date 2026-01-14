# -*- coding: utf-8 -*-
"""
Oyun Teorisi Servisi
Nash Dengesi hesaplamaları ve oyun teorisi analizleri için
"""
import json
from typing import Dict, List, Tuple, Optional


def calculate_nash_equilibrium(payoff_matrix: Dict) -> Dict:
    """
    Nash Dengesi hesapla
    
    Args:
        payoff_matrix: Kazanç matrisi (JSON formatında)
            Örnek format:
            {
                "player1_strategies": ["A", "B"],
                "player2_strategies": ["X", "Y"],
                "payoffs": {
                    "A-X": {"player1": 3, "player2": 3},
                    "A-Y": {"player1": 0, "player2": 5},
                    "B-X": {"player1": 5, "player2": 0},
                    "B-Y": {"player1": 1, "player1": 1}
                }
            }
    
    Returns:
        Nash dengesi sonuçları
    """
    try:
        if isinstance(payoff_matrix, str):
            payoff_matrix = json.loads(payoff_matrix)
        
        player1_strategies = payoff_matrix.get('player1_strategies', [])
        player2_strategies = payoff_matrix.get('player2_strategies', [])
        payoffs = payoff_matrix.get('payoffs', {})
        
        nash_equilibria = []
        
        # Tüm strateji kombinasyonlarını kontrol et
        for s1 in player1_strategies:
            for s2 in player2_strategies:
                strategy_key = f"{s1}-{s2}"
                if strategy_key not in payoffs:
                    continue
                
                current_payoff = payoffs[strategy_key]
                p1_payoff = current_payoff.get('player1', 0)
                p2_payoff = current_payoff.get('player2', 0)
                
                # Player 1 için: s2'ye karşı en iyi strateji mi?
                is_best_for_p1 = True
                for alt_s1 in player1_strategies:
                    if alt_s1 == s1:
                        continue
                    alt_key = f"{alt_s1}-{s2}"
                    if alt_key in payoffs:
                        alt_p1_payoff = payoffs[alt_key].get('player1', 0)
                        if alt_p1_payoff > p1_payoff:
                            is_best_for_p1 = False
                            break
                
                # Player 2 için: s1'e karşı en iyi strateji mi?
                is_best_for_p2 = True
                for alt_s2 in player2_strategies:
                    if alt_s2 == s2:
                        continue
                    alt_key = f"{s1}-{alt_s2}"
                    if alt_key in payoffs:
                        alt_p2_payoff = payoffs[alt_key].get('player2', 0)
                        if alt_p2_payoff > p2_payoff:
                            is_best_for_p2 = False
                            break
                
                # Nash dengesi: her iki oyuncu için de en iyi strateji
                if is_best_for_p1 and is_best_for_p2:
                    nash_equilibria.append({
                        'player1_strategy': s1,
                        'player2_strategy': s2,
                        'player1_payoff': p1_payoff,
                        'player2_payoff': p2_payoff,
                        'combined_payoff': p1_payoff + p2_payoff
                    })
        
        # En iyi Nash dengesini seç (combined payoff'a göre)
        best_equilibrium = None
        if nash_equilibria:
            best_equilibrium = max(nash_equilibria, key=lambda x: x['combined_payoff'])
        
        return {
            'equilibria': nash_equilibria,
            'best_equilibrium': best_equilibrium,
            'has_equilibrium': len(nash_equilibria) > 0,
            'equilibrium_count': len(nash_equilibria)
        }
    
    except Exception as e:
        return {
            'error': str(e),
            'equilibria': [],
            'best_equilibrium': None,
            'has_equilibrium': False,
            'equilibrium_count': 0
        }


def analyze_game_type(payoff_matrix: Dict) -> str:
    """
    Oyun tipini analiz et (Prisoner's Dilemma, Chicken Game, vb.)
    
    Args:
        payoff_matrix: Kazanç matrisi
    
    Returns:
        Oyun tipi adı
    """
    try:
        if isinstance(payoff_matrix, str):
            payoff_matrix = json.loads(payoff_matrix)
        
        payoffs = payoff_matrix.get('payoffs', {})
        
        # Basit kontrol: Prisoner's Dilemma pattern'i
        # T > R > P > S (T: Temptation, R: Reward, P: Punishment, S: Sucker)
        
        # Bu basit bir implementasyon, daha gelişmiş analiz yapılabilir
        return 'Unknown'
    
    except Exception:
        return 'Unknown'


def get_strategy_recommendation(nash_result: Dict) -> str:
    """
    Nash dengesi sonuçlarına göre strateji önerisi oluştur
    
    Args:
        nash_result: calculate_nash_equilibrium() fonksiyonunun sonucu
    
    Returns:
        Strateji önerisi metni
    """
    if not nash_result.get('has_equilibrium', False):
        return "Nash dengesi bulunamadı. Oyun kooperatif veya karmaşık stratejiler gerektirebilir."
    
    best_eq = nash_result.get('best_equilibrium')
    if not best_eq:
        return "Nash dengesi bulundu ancak optimal strateji belirlenemedi."
    
    p1_strategy = best_eq.get('player1_strategy', 'N/A')
    p2_strategy = best_eq.get('player2_strategy', 'N/A')
    p1_payoff = best_eq.get('player1_payoff', 0)
    p2_payoff = best_eq.get('player2_payoff', 0)
    
    recommendation = (
        f"Optimal Nash Dengesi Bulundu:\n"
        f"- Oyuncu 1 için önerilen strateji: {p1_strategy}\n"
        f"- Oyuncu 2 için önerilen strateji: {p2_strategy}\n"
        f"- Beklenen kazanç (Oyuncu 1): {p1_payoff}\n"
        f"- Beklenen kazanç (Oyuncu 2): {p2_payoff}\n"
        f"\n"
        f"Bu strateji kombinasyonu, her iki oyuncunun da tek taraflı sapmalarından kazançlı çıkamayacağı "
        f"bir denge noktasıdır."
    )
    
    return recommendation




