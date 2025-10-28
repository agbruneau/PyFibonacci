"""
Module définissant le contexte d'exécution pour les calculs de Fibonacci.
"""

import asyncio
from dataclasses import dataclass
from concurrent.futures import ProcessPoolExecutor
from typing import Optional


@dataclass
class CalculationContext:
    """Encapsule les paramètres et ressources partagés pour un calcul.

    Cette `dataclass` sert de conteneur pour passer de manière cohérente
    les configurations (comme le seuil de parallélisation) et les objets
    partagés (le pool de processus, la file de progression) à travers les
    différentes couches de l'application.

    Attributes:
        threshold (int): Le seuil, en nombre de chiffres décimaux, au-delà
            duquel la multiplication des grands nombres est déléguée au
            `ProcessPoolExecutor`.
        executor (Optional[ProcessPoolExecutor]): L'instance du pool de
            processus utilisée pour les calculs CPU-bound. Si `None`, toutes
            les opérations sont effectuées dans le thread principal.
        progress_queue (Optional[asyncio.Queue]): Une file asynchrone pour
            communiquer l'avancement du calcul à l'interface utilisateur,
            notamment pour la barre de progression.
    """

    threshold: int
    executor: Optional[ProcessPoolExecutor] = None
    progress_queue: Optional[asyncio.Queue] = None
