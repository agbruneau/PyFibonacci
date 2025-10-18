"""
Implémentation de l'algorithme Fast Doubling pour Fibonacci
==========================================================

Version optimisée avec parallélisation et gestion mémoire efficace.
Complexité: O(log n) avec optimisations de bas niveau.

Théorie:
L'algorithme Fast Doubling utilise les identités:
- F(2k) = F(k) * [2*F(k+1) - F(k)]  
- F(2k+1) = F(k)² + F(k+1)²

Itère sur la représentation binaire de n du MSB vers LSB.
"""

import asyncio
import concurrent.futures
import multiprocessing as mp
from typing import Tuple
from .calculator import CoreCalculator, ProgressReporter


class FastDoubling(CoreCalculator):
    """
    Implémentation optimisée de l'algorithme Fast Doubling.
    
    Caractéristiques:
    - Complexité O(log n)
    - Parallélisation adaptative des multiplications
    - Gestion mémoire optimisée
    """
    
    def name(self) -> str:
        return "Fast Doubling (O(log n), Parallèle, Optimisé)"
    
    async def calculate_core(self, n: int, threshold: int, 
                           reporter: ProgressReporter) -> int:
        """
        Calcule F(n) en utilisant l'algorithme Fast Doubling optimisé.
        
        Args:
            n: Indice du nombre de Fibonacci
            threshold: Seuil pour activer la parallélisation
            reporter: Rapporteur de progression
        
        Returns:
            Le n-ième nombre de Fibonacci
        """
        if n == 0:
            return 0
        if n == 1:
            return 1
        
        # Initialisation des variables
        f_k, f_k1 = 0, 1
        
        # Analyse de la représentation binaire
        bits = bin(n)[2:]  # Supprime le préfixe '0b'
        num_bits = len(bits)
        
        # Configuration du parallélisme
        use_parallel = mp.cpu_count() > 1 and threshold > 0
        
        # Calcul de progression pondéré
        total_work = sum(4**i for i in range(num_bits))
        work_done = 0
        
        # Itération sur les bits de n (MSB vers LSB)
        for i, bit in enumerate(bits[1:], 1):  # Skip le premier bit (toujours 1)
            # Vérification d'annulation (pour usage futur avec asyncio.Task)
            await asyncio.sleep(0)  # Yield pour permettre l'annulation
            
            # Étape de doublage: calcule F(2k) et F(2k+1)
            f_2k, f_2k1 = await self._doubling_step(f_k, f_k1, use_parallel, threshold)
            
            # Étape d'addition si le bit est 1
            if bit == '1':
                f_k, f_k1 = f_2k1, f_2k + f_2k1
            else:
                f_k, f_k1 = f_2k, f_2k1
            
            # Mise à jour de la progression
            work_done += 4**i
            if total_work > 0:
                progress = min(work_done / total_work, 1.0)
                reporter.report(progress)
        
        return f_k
    
    async def _doubling_step(self, f_k: int, f_k1: int, use_parallel: bool, 
                           threshold: int) -> Tuple[int, int]:
        """
        Exécute l'étape de doublage: calcule F(2k) et F(2k+1) depuis F(k) et F(k+1).
        
        Formules:
        - F(2k) = F(k) * [2*F(k+1) - F(k)]
        - F(2k+1) = F(k)² + F(k+1)²
        
        Args:
            f_k: F(k) 
            f_k1: F(k+1)
            use_parallel: Si la parallélisation est activée
            threshold: Seuil de taille pour la parallélisation
        
        Returns:
            Tuple (F(2k), F(2k+1))
        """
        # Calculs préliminaires
        two_fk1_minus_fk = 2 * f_k1 - f_k
        
        # Décision de parallélisation basée sur la taille des nombres
        should_parallelize = (use_parallel and 
                             max(f_k.bit_length(), f_k1.bit_length()) > threshold)
        
        if should_parallelize:
            return await self._parallel_multiply(f_k, f_k1, two_fk1_minus_fk)
        else:
            return self._sequential_multiply(f_k, f_k1, two_fk1_minus_fk)
    
    def _sequential_multiply(self, f_k: int, f_k1: int, 
                           two_fk1_minus_fk: int) -> Tuple[int, int]:
        """Calcul séquentiel des multiplications."""
        f_2k = f_k * two_fk1_minus_fk      # F(2k) = F(k) * [2*F(k+1) - F(k)]
        f_k_squared = f_k * f_k             # F(k)²
        f_k1_squared = f_k1 * f_k1          # F(k+1)²
        f_2k1 = f_k_squared + f_k1_squared  # F(2k+1) = F(k)² + F(k+1)²
        
        return f_2k, f_2k1
    
    async def _parallel_multiply(self, f_k: int, f_k1: int, 
                               two_fk1_minus_fk: int) -> Tuple[int, int]:
        """
        Calcul parallèle des multiplications indépendantes.
        
        Les trois multiplications sont indépendantes et peuvent être
        exécutées en parallèle sur des processus séparés.
        """
        loop = asyncio.get_event_loop()
        
        with concurrent.futures.ProcessPoolExecutor(max_workers=3) as executor:
            # Lancement des tâches parallèles
            future_f2k = loop.run_in_executor(
                executor, self._multiply, f_k, two_fk1_minus_fk
            )
            future_fk_sq = loop.run_in_executor(
                executor, self._multiply, f_k, f_k
            )  
            future_fk1_sq = loop.run_in_executor(
                executor, self._multiply, f_k1, f_k1
            )
            
            # Attente des résultats
            f_2k = await future_f2k
            f_k_squared = await future_fk_sq
            f_k1_squared = await future_fk1_sq
            
            f_2k1 = f_k_squared + f_k1_squared
            
            return f_2k, f_2k1
    
    @staticmethod
    def _multiply(a: int, b: int) -> int:
        """Fonction de multiplication statique pour l'exécution en parallèle."""
        return a * b