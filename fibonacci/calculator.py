"""
Module de calcul Fibonacci - Interfaces et décorateurs principaux
================================================================

Ce module définit les interfaces, contrats de communication et stratégies
d'optimisation fondamentales pour les algorithmes de Fibonacci.

Architecture basée sur les patrons Décorateur et Adaptateur avec application
des principes SOLID.
"""

import asyncio
from abc import ABC, abstractmethod
from typing import Optional, Callable
import time

# Constantes pour l'optimisation
MAX_FIB_UINT64 = 93
DEFAULT_PARALLEL_THRESHOLD = 1000

# Table de consultation pré-calculée pour les petits nombres
_fib_lookup_table = [0, 1]
for i in range(2, MAX_FIB_UINT64 + 1):
    _fib_lookup_table.append(_fib_lookup_table[i-1] + _fib_lookup_table[i-2])


class ProgressReporter:
    """Rapporteur de progression pour les algorithmes."""
    
    def __init__(self, callback: Optional[Callable[[float], None]] = None):
        self.callback = callback
    
    def report(self, progress: float):
        """Rapporte une valeur de progression entre 0.0 et 1.0."""
        if self.callback and 0.0 <= progress <= 1.0:
            self.callback(progress)


class CoreCalculator(ABC):
    """Interface pour les implémentations d'algorithmes de calcul pur."""
    
    @abstractmethod
    async def calculate_core(self, n: int, threshold: int, 
                           reporter: ProgressReporter) -> int:
        """Calcule F(n) avec l'algorithme spécifique."""
        pass
    
    @abstractmethod
    def name(self) -> str:
        """Retourne le nom de l'algorithme."""
        pass


class Calculator:
    """
    Décorateur principal qui ajoute des fonctionnalités aux algorithmes:
    - Optimisation par table de consultation (LUT)
    - Gestion de la progression
    - Validation des paramètres
    """
    
    def __init__(self, core: CoreCalculator):
        if core is None:
            raise ValueError("L'implémentation CoreCalculator ne peut être None")
        self._core = core
    
    def name(self) -> str:
        """Délègue l'appel au calculateur encapsulé."""
        return self._core.name()
    
    async def calculate(self, n: int, threshold: int = DEFAULT_PARALLEL_THRESHOLD,
                       progress_callback: Optional[Callable[[float], None]] = None) -> int:
        """
        Orchestre le calcul avec optimisations:
        1. Fast path via LUT pour les petites valeurs
        2. Délégation au noyau pour les grandes valeurs
        3. Rapport de progression
        """
        if n < 0:
            raise ValueError("n doit être non-négatif")
        
        reporter = ProgressReporter(progress_callback)
        
        # Optimisation Fast Path via LUT
        if n <= MAX_FIB_UINT64:
            reporter.report(1.0)
            return _fib_lookup_table[n]
        
        # Délégation au noyau de calcul
        try:
            result = await self._core.calculate_core(n, threshold, reporter)
            reporter.report(1.0)  # Garantit la progression finale
            return result
        except Exception as e:
            raise RuntimeError(f"Erreur dans le calcul: {e}") from e


def new_calculator(core: CoreCalculator) -> Calculator:
    """Factory pour créer un calculateur décoré."""
    return Calculator(core)