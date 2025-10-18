"""
Implémentation de l'algorithme d'Exponentiation Matricielle pour Fibonacci
=========================================================================

Version optimisée exploitant les symétries matricielles et la parallélisation.
Complexité: O(log n) avec optimisations avancées.

Théorie:
La relation de récurrence F(n+1) = F(n) + F(n-1) s'exprime comme:
[F(n), F(n-1)]^T = Q^(n-1) * [F(1), F(0)]^T

Où Q = [[1, 1], [1, 0]] est la matrice de Fibonacci.
Le calcul se ramène à Q^(n-1) via exponentiation binaire.
"""

import asyncio
import concurrent.futures
import multiprocessing as mp
from typing import List, Tuple
from .calculator import CoreCalculator, ProgressReporter


class Matrix2x2:
    """Matrice 2x2 optimisée pour les calculs de Fibonacci."""
    
    def __init__(self, a: int = 0, b: int = 0, c: int = 0, d: int = 0):
        self.a, self.b, self.c, self.d = a, b, c, d
    
    def copy(self) -> 'Matrix2x2':
        """Crée une copie de la matrice."""
        return Matrix2x2(self.a, self.b, self.c, self.d)
    
    def set_identity(self):
        """Configure comme matrice identité."""
        self.a, self.b, self.c, self.d = 1, 0, 0, 1
    
    def set_fibonacci_base(self):
        """Configure comme matrice de base Q = [[1, 1], [1, 0]]."""
        self.a, self.b, self.c, self.d = 1, 1, 1, 0
    
    def __repr__(self) -> str:
        return f"[[{self.a}, {self.b}], [{self.c}, {self.d}]]"


class MatrixExponentiation(CoreCalculator):
    """
    Implémentation optimisée de l'exponentiation matricielle.
    
    Caractéristiques:
    - Complexité O(log n) 
    - Exploitation de la symétrie matricielle
    - Parallélisation adaptative des multiplications
    - Algorithme d'exponentiation binaire
    """
    
    def name(self) -> str:
        return "Exponentiation Matricielle (O(log n), Parallèle, Optimisé)"
    
    async def calculate_core(self, n: int, threshold: int,
                           reporter: ProgressReporter) -> int:
        """
        Calcule F(n) via exponentiation matricielle.
        
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
        
        # Matrices de travail
        result = Matrix2x2()
        result.set_identity()
        
        base = Matrix2x2()
        base.set_fibonacci_base()
        
        exponent = n - 1
        use_parallel = mp.cpu_count() > 1 and threshold > 0
        
        # Analyse binaire pour la progression
        bit_length = exponent.bit_length()
        
        # Exponentiation binaire
        for i in range(bit_length):
            # Vérification d'annulation
            await asyncio.sleep(0)
            
            # Si le bit courant est 1, multiplier le résultat par la base
            if (exponent >> i) & 1:
                should_parallelize = (use_parallel and 
                                    self._should_parallelize_multiply(result, base, threshold))
                result = await self._multiply_matrices(result, base, should_parallelize)
            
            # Mettre au carré la matrice de base pour la prochaine itération
            if i < bit_length - 1:
                should_parallelize = (use_parallel and 
                                    self._should_parallelize_square(base, threshold))
                base = await self._square_symmetric_matrix(base, should_parallelize)
            
            # Progression
            progress = (i + 1) / bit_length
            reporter.report(progress)
        
        return result.a  # F(n) est dans la position (0,0) de la matrice résultat
    
    def _should_parallelize_multiply(self, m1: Matrix2x2, m2: Matrix2x2, 
                                   threshold: int) -> bool:
        """Détermine si la multiplication doit être parallélisée."""
        max_bits = max(
            m1.a.bit_length(), m1.b.bit_length(), m1.c.bit_length(), m1.d.bit_length(),
            m2.a.bit_length(), m2.b.bit_length(), m2.c.bit_length(), m2.d.bit_length()
        )
        return max_bits > threshold
    
    def _should_parallelize_square(self, matrix: Matrix2x2, threshold: int) -> bool:
        """Détermine si la mise au carré doit être parallélisée."""
        max_bits = max(
            matrix.a.bit_length(), matrix.b.bit_length(),
            matrix.c.bit_length(), matrix.d.bit_length()
        )
        return max_bits > threshold
    
    async def _multiply_matrices(self, m1: Matrix2x2, m2: Matrix2x2, 
                               parallel: bool) -> Matrix2x2:
        """
        Multiplie deux matrices 2x2: result = m1 * m2.
        
        Formules standard de multiplication matricielle:
        result[i][j] = Σ(k) m1[i][k] * m2[k][j]
        """
        if parallel:
            return await self._multiply_matrices_parallel(m1, m2)
        else:
            return self._multiply_matrices_sequential(m1, m2)
    
    def _multiply_matrices_sequential(self, m1: Matrix2x2, m2: Matrix2x2) -> Matrix2x2:
        """Multiplication matricielle séquentielle."""
        return Matrix2x2(
            a=m1.a * m2.a + m1.b * m2.c,  # (0,0)
            b=m1.a * m2.b + m1.b * m2.d,  # (0,1)  
            c=m1.c * m2.a + m1.d * m2.c,  # (1,0)
            d=m1.c * m2.b + m1.d * m2.d   # (1,1)
        )
    
    async def _multiply_matrices_parallel(self, m1: Matrix2x2, m2: Matrix2x2) -> Matrix2x2:
        """
        Multiplication matricielle parallèle.
        
        Les 8 multiplications scalaires sont indépendantes et peuvent être
        exécutées en parallèle sur des processus séparés.
        """
        loop = asyncio.get_event_loop()
        
        with concurrent.futures.ProcessPoolExecutor(max_workers=4) as executor:
            # Lancement des 8 multiplications en parallèle
            tasks = [
                loop.run_in_executor(executor, self._multiply, m1.a, m2.a),
                loop.run_in_executor(executor, self._multiply, m1.b, m2.c),
                loop.run_in_executor(executor, self._multiply, m1.a, m2.b),
                loop.run_in_executor(executor, self._multiply, m1.b, m2.d),
                loop.run_in_executor(executor, self._multiply, m1.c, m2.a),
                loop.run_in_executor(executor, self._multiply, m1.d, m2.c),
                loop.run_in_executor(executor, self._multiply, m1.c, m2.b),
                loop.run_in_executor(executor, self._multiply, m1.d, m2.d),
            ]
            
            # Attente des résultats
            products = await asyncio.gather(*tasks)
            
            # Assemblage des résultats avec les additions
            return Matrix2x2(
                a=products[0] + products[1],  # m1.a*m2.a + m1.b*m2.c
                b=products[2] + products[3],  # m1.a*m2.b + m1.b*m2.d
                c=products[4] + products[5],  # m1.c*m2.a + m1.d*m2.c
                d=products[6] + products[7]   # m1.c*m2.b + m1.d*m2.d
            )
    
    async def _square_symmetric_matrix(self, matrix: Matrix2x2, 
                                     parallel: bool) -> Matrix2x2:
        """
        Met au carré une matrice symétrique en exploitant cette propriété.
        
        Pour une matrice symétrique M = [[a, b], [b, d]], 
        M² = [[a²+b², b(a+d)], [b(a+d), b²+d²]]
        
        Ceci réduit les multiplications de 8 à 4.
        """
        if parallel:
            return await self._square_symmetric_parallel(matrix)
        else:
            return self._square_symmetric_sequential(matrix)
    
    def _square_symmetric_sequential(self, matrix: Matrix2x2) -> Matrix2x2:
        """Mise au carré séquentielle d'une matrice symétrique."""
        a, b, d = matrix.a, matrix.b, matrix.d
        
        a_squared = a * a
        b_squared = b * b  
        d_squared = d * d
        b_times_a_plus_d = b * (a + d)
        
        return Matrix2x2(
            a=a_squared + b_squared,
            b=b_times_a_plus_d,
            c=b_times_a_plus_d,  # Symétrie
            d=b_squared + d_squared
        )
    
    async def _square_symmetric_parallel(self, matrix: Matrix2x2) -> Matrix2x2:
        """Mise au carré parallèle d'une matrice symétrique."""
        loop = asyncio.get_event_loop()
        a, b, d = matrix.a, matrix.b, matrix.d
        
        with concurrent.futures.ProcessPoolExecutor(max_workers=4) as executor:
            # Les 4 multiplications indépendantes
            tasks = [
                loop.run_in_executor(executor, self._multiply, a, a),          # a²
                loop.run_in_executor(executor, self._multiply, b, b),          # b²
                loop.run_in_executor(executor, self._multiply, d, d),          # d²
                loop.run_in_executor(executor, self._multiply, b, a + d),      # b*(a+d)
            ]
            
            a_sq, b_sq, d_sq, b_ad = await asyncio.gather(*tasks)
            
            return Matrix2x2(
                a=a_sq + b_sq,
                b=b_ad,
                c=b_ad,  # Symétrie
                d=b_sq + d_sq
            )
    
    @staticmethod
    def _multiply(x: int, y: int) -> int:
        """Fonction de multiplication statique pour l'exécution parallèle."""
        return x * y