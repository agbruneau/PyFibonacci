"""
Module définissant le contexte d'exécution pour les calculs de Fibonacci.
"""
import asyncio
from dataclasses import dataclass
from concurrent.futures import ProcessPoolExecutor
from typing import Optional

@dataclass
class CalculationContext:
    """
    Encapsule les paramètres et les ressources partagées pour une session de calcul.

    Attributes:
        threshold: Le seuil (en nombre de chiffres décimaux) à partir duquel
                   la multiplication est déléguée à un processus externe.
        executor: Une instance de ProcessPoolExecutor pour exécuter les calculs
                  parallèles. Peut être None si le parallélisme est désactivé.
        progress_queue: Une file d'attente asyncio pour communiquer la progression à l'UI.
    """
    threshold: int
    executor: Optional[ProcessPoolExecutor] = None
    progress_queue: Optional[asyncio.Queue] = None
