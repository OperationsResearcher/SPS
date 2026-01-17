# -*- coding: utf-8 -*-
"""
Monte Carlo Simülasyon Servisi
Risk analizi ve projeksiyon hesaplamaları için
"""
import random
import json
from typing import Dict, List, Optional
from datetime import datetime


def run_monte_carlo_simulation(
    variables: Dict,
    iterations: int = 10000,
    simulation_type: str = 'financial'
) -> Dict:
    """
    Monte Carlo simülasyonu çalıştır
    
    Args:
        variables: Simülasyon değişkenleri
            Örnek format:
            {
                "revenue": {"min": 100000, "max": 200000, "mean": 150000, "std": 20000},
                "costs": {"min": 80000, "max": 120000, "mean": 100000, "std": 10000}
            }
        iterations: İterasyon sayısı
        simulation_type: Simülasyon tipi ('financial', 'project', 'risk')
    
    Returns:
        Simülasyon sonuçları
    """
    try:
        results = []
        
        for i in range(iterations):
            iteration_result = {}
            total_value = 0
            
            # Her değişken için rastgele değer üret
            for var_name, var_params in variables.items():
                if isinstance(var_params, dict):
                    # Normal dağılım varsa kullan
                    if 'mean' in var_params and 'std' in var_params:
                        value = random.normalvariate(var_params['mean'], var_params['std'])
                        # Min-max sınırları içinde tut
                        value = max(var_params.get('min', value), min(var_params.get('max', value), value))
                    else:
                        # Uniform dağılım
                        value = random.uniform(
                            var_params.get('min', 0),
                            var_params.get('max', 100)
                        )
                    
                    iteration_result[var_name] = value
                    total_value += value
            
            iteration_result['total'] = total_value
            results.append(iteration_result)
        
        # İstatistiksel analiz
        totals = [r['total'] for r in results]
        totals.sort()
        
        percentile_5 = totals[int(len(totals) * 0.05)]
        percentile_25 = totals[int(len(totals) * 0.25)]
        percentile_50 = totals[int(len(totals) * 0.50)]  # Median
        percentile_75 = totals[int(len(totals) * 0.75)]
        percentile_95 = totals[int(len(totals) * 0.95)]
        
        mean = sum(totals) / len(totals)
        std_dev = (sum((x - mean) ** 2 for x in totals) / len(totals)) ** 0.5
        
        return {
            'success': True,
            'iterations': iterations,
            'simulation_type': simulation_type,
            'statistics': {
                'mean': round(mean, 2),
                'std_dev': round(std_dev, 2),
                'min': round(min(totals), 2),
                'max': round(max(totals), 2),
                'percentile_5': round(percentile_5, 2),
                'percentile_25': round(percentile_25, 2),
                'percentile_50': round(percentile_50, 2),
                'percentile_75': round(percentile_25, 2),
                'percentile_95': round(percentile_95, 2)
            },
            'distribution': {
                'percentiles': {
                    '5': percentile_5,
                    '25': percentile_25,
                    '50': percentile_50,
                    '75': percentile_75,
                    '95': percentile_95
                }
            },
            'sample_results': results[:100]  # İlk 100 sonucu örnek olarak
        }
    
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'iterations': 0,
            'statistics': {}
        }


def calculate_confidence_intervals(results: Dict, confidence_level: float = 0.95) -> Dict:
    """
    Güven aralıklarını hesapla
    
    Args:
        results: Simülasyon sonuçları
        confidence_level: Güven seviyesi (0.95 = %95)
    
    Returns:
        Güven aralıkları
    """
    if not results.get('success'):
        return {}
    
    stats = results.get('statistics', {})
    alpha = 1 - confidence_level
    
    lower_percentile = (alpha / 2) * 100
    upper_percentile = (1 - alpha / 2) * 100
    
    # Percentile değerlerini kullanarak güven aralığı
    # Bu basit bir implementasyon, daha gelişmiş istatistiksel yöntemler kullanılabilir
    
    return {
        'confidence_level': confidence_level,
        'lower_bound': stats.get('percentile_5', 0),
        'upper_bound': stats.get('percentile_95', 0),
        'interval_range': stats.get('percentile_95', 0) - stats.get('percentile_5', 0)
    }


def generate_simulation_scenario(base_variables: Dict, scenario_name: str) -> Dict:
    """
    Senaryo tabanlı simülasyon oluştur
    
    Args:
        base_variables: Temel değişkenler
        scenario_name: Senaryo adı ('optimistic', 'realistic', 'pessimistic')
    
    Returns:
        Senaryo sonuçları
    """
    # Senaryoya göre değişkenleri ayarla
    scenario_multipliers = {
        'optimistic': 1.2,
        'realistic': 1.0,
        'pessimistic': 0.8
    }
    
    multiplier = scenario_multipliers.get(scenario_name.lower(), 1.0)
    
    adjusted_variables = {}
    for var_name, var_params in base_variables.items():
        if isinstance(var_params, dict):
            adjusted = var_params.copy()
            if 'mean' in adjusted:
                adjusted['mean'] *= multiplier
            if 'max' in adjusted:
                adjusted['max'] *= multiplier
            if 'min' in adjusted:
                adjusted['min'] *= multiplier
            adjusted_variables[var_name] = adjusted
    
    return run_monte_carlo_simulation(adjusted_variables)





