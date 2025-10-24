"""
Module définissant le contexte d'exécution pour les calculs de Fibonacci.
"""
import asyncio
from dataclasses import dataclass
from concurrent.futures import ProcessPoolExecutor
from typing import Optional

@dataclass
class CalculationContext:
    """Encapsule les paramètres et ressources partagés pour une session de calcul.

    Cette `dataclass` sert de conteneur pour passer de manière cohérente
    les configurations et les objets partagés (comme l'exécuteur de processus
    et la file de progression) à travers les différentes couches de
    l'application, en particulier aux fonctions de calcul qui en ont besoin.

    Attributes:
        threshold: Le seuil (en nombre de chiffres décimaux) à partir duquel
                   la multiplication doit être parallélisée.
        executor: Une instance de `ProcessPoolExecutor` pour exécuter les
                  calculs de multiplication en parallèle. Si `None`, toute
                  la multiplication est exécutée dans le processus principal.
        progress_queue: Une `asyncio.Queue` optionnelle utilisée pour envoyer
                        des mises à jour de progression depuis les algorithmes
                        vers l'interface utilisateur.
    """
    threshold: int
    executor: Optional[ProcessPoolExecutor] = None
    progress_queue: Optional[asyncio.Queue] = None
