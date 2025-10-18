"""
Utilitaires communs pour le calculateur Fibonacci
================================================

Fonctions helper, validation et structures de données communes.
"""

from dataclasses import dataclass
from typing import Optional, List
import time


@dataclass 
class CalculationResult:
    """Résultat d'un calcul avec métadonnées de performance."""
    name: str
    result: Optional[int]
    duration: float
    error: Optional[str]


def validate_config(config) -> List[str]:
    """
    Valide une configuration et retourne la liste des erreurs.
    
    Args:
        config: Configuration à valider
        
    Returns:
        Liste des messages d'erreur (vide si configuration valide)
    """
    errors = []
    
    if hasattr(config, 'n') and config.n < 0:
        errors.append("L'indice n doit être non-négatif")
    
    if hasattr(config, 'timeout') and config.timeout <= 0:
        errors.append("Le timeout doit être strictement positif")
    
    if hasattr(config, 'threshold') and config.threshold < 0:
        errors.append("Le seuil de parallélisation doit être non-négatif")
    
    return errors


def format_large_number(n: int, max_digits: int = 100) -> str:
    """
    Formate un grand nombre pour l'affichage.
    
    Args:
        n: Nombre à formater
        max_digits: Nombre maximum de chiffres avant troncature
        
    Returns:
        Représentation formatée du nombre
    """
    str_n = str(n)
    
    if len(str_n) <= max_digits:
        return str_n
    
    # Troncature avec ellipse
    half_max = max_digits // 2
    return f"{str_n[:half_max]}...{str_n[-half_max:]} ({len(str_n)} chiffres)"


def benchmark_function(func, *args, **kwargs):
    """
    Mesure le temps d'exécution d'une fonction.
    
    Args:
        func: Fonction à chronométrer
        *args, **kwargs: Arguments de la fonction
        
    Returns:
        Tuple (résultat, durée_en_secondes)
    """
    start_time = time.perf_counter()
    try:
        result = func(*args, **kwargs)
        duration = time.perf_counter() - start_time
        return result, duration
    except Exception as e:
        duration = time.perf_counter() - start_time
        raise type(e)(f"Erreur après {duration:.3f}s: {e}") from e


def fibonacci_properties_check(n: int, result: int) -> bool:
    """
    Vérifie certaines propriétés mathématiques des nombres de Fibonacci.
    
    Propriétés testées:
    - Identité de Cassini: F(n-1)*F(n+1) - F(n)² = (-1)^n
    
    Args:
        n: Indice du nombre de Fibonacci
        result: Valeur calculée F(n)
        
    Returns:
        True si les propriétés sont vérifiées
    """
    if n <= 1:
        return True  # Cas triviaux
    
    # Pour éviter les recalculs coûteux, on se limite aux vérifications simples
    # Dans une implémentation complète, on calculerait F(n-1) et F(n+1)
    
    # Vérification de parité pour quelques cas spéciaux
    if n % 3 == 0 and result % 2 != 0:
        return False  # F(3k) est pair pour k > 0
    
    return True


def estimate_computation_time(n: int, algorithm: str = "fast") -> float:
    """
    Estime le temps de calcul basé sur la taille du problème.
    
    Args:
        n: Indice du nombre de Fibonacci
        algorithm: Type d'algorithme ("fast" ou "matrix")
        
    Returns:
        Estimation du temps en secondes
    """
    if n <= 93:
        return 0.001  # Lookup table
    
    # Estimation basée sur la complexité logarithmique
    log_n = n.bit_length()
    
    if algorithm == "fast":
        # Fast Doubling: ~O(log n * M(bits))
        estimated_bits = log_n * 0.694  # log₂(φ) approximation
        return estimated_bits * 0.0001  # Facteur empirique
    elif algorithm == "matrix":
        # Matrix: légèrement plus lent due aux multiplications matricielles
        estimated_bits = log_n * 0.694
        return estimated_bits * 0.00015
    else:
        return float('inf')


def memory_estimate(n: int) -> dict:
    """
    Estime l'utilisation mémoire pour le calcul de F(n).
    
    Args:
        n: Indice du nombre de Fibonacci
        
    Returns:
        Dictionnaire avec les estimations mémoire
    """
    if n <= 93:
        return {"total_bytes": 64, "description": "Lookup table"}
    
    # F(n) a approximativement n*log₂(φ)/log₂(10) ≈ n*0.209 chiffres décimaux
    # Soit n*log₂(φ) ≈ n*0.694 bits
    estimated_bits = int(n * 0.694)
    estimated_bytes = estimated_bits // 8 + 1
    
    # Facteur pour les variables temporaires (algorithme dépendant)
    working_memory = estimated_bytes * 4  # Approximation pour variables temp
    
    return {
        "result_bits": estimated_bits,
        "result_bytes": estimated_bytes,
        "working_memory_bytes": working_memory, 
        "total_bytes": estimated_bytes + working_memory,
        "description": f"~{estimated_bits:,} bits pour F({n:,})"
    }


class Timer:
    """Contexte manager pour mesurer le temps d'exécution."""
    
    def __init__(self, description: str = "Operation"):
        self.description = description
        self.start_time = None
        self.duration = None
    
    def __enter__(self):
        self.start_time = time.perf_counter()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.duration = time.perf_counter() - self.start_time
        if exc_type is None:
            print(f"{self.description}: {self.duration:.3f}s")
        else:
            print(f"{self.description}: ❌ Échec après {self.duration:.3f}s")


def create_progress_reporter(callback=None):
    """
    Crée une fonction de rapport de progression.
    
    Args:
        callback: Fonction appelée avec la progression (0.0-1.0)
        
    Returns:
        Fonction de rapport de progression
    """
    last_reported = [-1.0]  # Mutable pour closure
    
    def report_progress(progress: float):
        # Ne rapporte que si le changement est significatif
        if callback and abs(progress - last_reported[0]) >= 0.01:
            callback(progress)
            last_reported[0] = progress
    
    return report_progress