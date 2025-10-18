"""
Tests unitaires pour le calculateur Fibonacci
============================================

Suite de tests complète couvrant les algorithmes, les cas limites
et les propriétés mathématiques.
"""

import unittest
import asyncio
import time
from fibonacci.calculator import Calculator, new_calculator, MAX_FIB_UINT64
from fibonacci.fast_doubling import FastDoubling
from fibonacci.matrix_exponentiation import MatrixExponentiation
from fibonacci.utils import CalculationResult, fibonacci_properties_check


class TestFibonacciCalculators(unittest.TestCase):
    """Tests pour les algorithmes de calcul Fibonacci."""
    
    def setUp(self):
        """Configuration des tests."""
        self.fast_calc = new_calculator(FastDoubling())
        self.matrix_calc = new_calculator(MatrixExponentiation())
        
    def test_small_fibonacci_numbers(self):
        """Test des petits nombres de Fibonacci (table de consultation)."""
        expected = [0, 1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233, 377, 610]
        
        for calc in [self.fast_calc, self.matrix_calc]:
            with self.subTest(calculator=calc.name()):
                for i, expected_val in enumerate(expected):
                    result = asyncio.run(calc.calculate(i))
                    self.assertEqual(result, expected_val, 
                                   f"F({i}) should be {expected_val}, got {result}")
    
    def test_medium_fibonacci_numbers(self):
        """Test de nombres de Fibonacci moyens."""
        test_cases = [
            (20, 6765),
            (30, 832040),
            (40, 102334155),
            (50, 12586269025),
        ]
        
        for calc in [self.fast_calc, self.matrix_calc]:
            with self.subTest(calculator=calc.name()):
                for n, expected in test_cases:
                    result = asyncio.run(calc.calculate(n))
                    self.assertEqual(result, expected, 
                                   f"F({n}) should be {expected}, got {result}")
    
    def test_large_fibonacci_numbers(self):
        """Test de grands nombres de Fibonacci avec validation croisée."""
        test_indices = [100, 500, 1000, 5000]
        
        for n in test_indices:
            with self.subTest(n=n):
                # Calcul avec les deux algorithmes
                result_fast = asyncio.run(self.fast_calc.calculate(n))
                result_matrix = asyncio.run(self.matrix_calc.calculate(n))
                
                # Validation croisée
                self.assertEqual(result_fast, result_matrix,
                               f"Algorithms disagree for F({n})")
                
                # Vérification des propriétés
                self.assertTrue(fibonacci_properties_check(n, result_fast))
    
    def test_boundary_cases(self):
        """Test des cas limites."""
        boundary_cases = [0, 1, 2, MAX_FIB_UINT64, MAX_FIB_UINT64 + 1]
        
        for calc in [self.fast_calc, self.matrix_calc]:
            with self.subTest(calculator=calc.name()):
                for n in boundary_cases:
                    try:
                        result = asyncio.run(calc.calculate(n))
                        self.assertIsInstance(result, int)
                        self.assertGreaterEqual(result, 0)
                    except Exception as e:
                        self.fail(f"F({n}) raised {type(e).__name__}: {e}")
    
    def test_parallel_threshold_impact(self):
        """Test de l'impact du seuil de parallélisation."""
        n = 1000
        thresholds = [0, 100, 500, 1000, 2000]
        
        results = []
        for threshold in thresholds:
            start_time = time.perf_counter()
            result = asyncio.run(self.fast_calc.calculate(n, threshold=threshold))
            duration = time.perf_counter() - start_time
            results.append((threshold, result, duration))
        
        # Tous les résultats doivent être identiques
        first_result = results[0][1]
        for threshold, result, duration in results:
            self.assertEqual(result, first_result,
                           f"Threshold {threshold} gave different result")
    
    def test_error_handling(self):
        """Test de la gestion d'erreurs."""
        # Test avec valeurs négatives
        with self.assertRaises(ValueError):
            asyncio.run(self.fast_calc.calculate(-1))
        
        # Test avec calculateur None
        with self.assertRaises(ValueError):
            new_calculator(None)
    
    def test_progress_reporting(self):
        """Test du rapport de progression."""
        progress_values = []
        
        def capture_progress(value):
            progress_values.append(value)
        
        # Test avec un calcul de taille moyenne
        asyncio.run(self.fast_calc.calculate(1000, progress_callback=capture_progress))
        
        # Vérifications
        self.assertTrue(len(progress_values) > 0, "No progress reported")
        self.assertEqual(progress_values[-1], 1.0, "Final progress should be 1.0")
        
        # La progression doit être croissante
        for i in range(1, len(progress_values)):
            self.assertGreaterEqual(progress_values[i], progress_values[i-1],
                                  "Progress should be non-decreasing")


class TestFibonacciProperties(unittest.TestCase):
    """Tests des propriétés mathématiques des nombres de Fibonacci."""
    
    def setUp(self):
        self.calc = new_calculator(FastDoubling())
    
    def test_fibonacci_identity_small(self):
        """Test de l'identité F(n+m) = F(n)*F(m+1) + F(n-1)*F(m) pour petits n."""
        for n in range(1, 20):
            for m in range(1, 10):
                with self.subTest(n=n, m=m):
                    fn = asyncio.run(self.calc.calculate(n))
                    fm = asyncio.run(self.calc.calculate(m))
                    fn1 = asyncio.run(self.calc.calculate(n-1)) if n > 0 else 0
                    fm1 = asyncio.run(self.calc.calculate(m+1))
                    fnm = asyncio.run(self.calc.calculate(n+m))
                    
                    expected = fn * fm1 + fn1 * fm
                    self.assertEqual(fnm, expected,
                                   f"Identity failed for F({n}+{m})")
    
    def test_fibonacci_divisibility(self):
        """Test des propriétés de divisibilité."""
        # F(n) divise F(kn) pour tout k
        test_cases = [(3, 6), (4, 8), (5, 10), (6, 12)]
        
        for n, kn in test_cases:
            with self.subTest(n=n, kn=kn):
                fn = asyncio.run(self.calc.calculate(n))
                fkn = asyncio.run(self.calc.calculate(kn))
                
                if fn != 0:  # Éviter la division par zéro
                    self.assertEqual(fkn % fn, 0,
                                   f"F({kn}) should be divisible by F({n})")
    
    def test_fibonacci_gcd_property(self):
        """Test de la propriété GCD: gcd(F(m), F(n)) = F(gcd(m, n))."""
        import math
        
        test_cases = [(6, 9), (8, 12), (10, 15)]
        
        for m, n in test_cases:
            with self.subTest(m=m, n=n):
                fm = asyncio.run(self.calc.calculate(m))
                fn = asyncio.run(self.calc.calculate(n))
                fgcd = asyncio.run(self.calc.calculate(math.gcd(m, n)))
                
                actual_gcd = math.gcd(fm, fn)
                self.assertEqual(actual_gcd, fgcd,
                               f"gcd(F({m}), F({n})) ≠ F(gcd({m}, {n}))")


class TestPerformance(unittest.TestCase):
    """Tests de performance et de benchmark."""
    
    def setUp(self):
        self.fast_calc = new_calculator(FastDoubling())
        self.matrix_calc = new_calculator(MatrixExponentiation())
    
    def test_performance_comparison(self):
        """Compare les performances des algorithmes."""
        test_sizes = [1000, 5000, 10000]
        results = {}
        
        for n in test_sizes:
            results[n] = {}
            
            # Fast Doubling
            start_time = time.perf_counter()
            result_fast = asyncio.run(self.fast_calc.calculate(n))
            time_fast = time.perf_counter() - start_time
            
            # Matrix Exponentiation  
            start_time = time.perf_counter()
            result_matrix = asyncio.run(self.matrix_calc.calculate(n))
            time_matrix = time.perf_counter() - start_time
            
            results[n] = {
                'fast_time': time_fast,
                'matrix_time': time_matrix,
                'results_match': result_fast == result_matrix
            }
            
            # Vérification que les résultats correspondent
            self.assertTrue(results[n]['results_match'],
                          f"Results don't match for n={n}")
        
        # Affichage des résultats de performance
        print("\\n--- Performance Comparison ---")
        for n, data in results.items():
            print(f"F({n:,}):")
            print(f"  Fast Doubling: {data['fast_time']:.4f}s")
            print(f"  Matrix Exp:    {data['matrix_time']:.4f}s")
            ratio = data['matrix_time'] / data['fast_time']
            print(f"  Ratio:         {ratio:.2f}x")
    
    def test_scalability(self):
        """Test de la scalabilité avec des tailles croissantes."""
        sizes = [100, 500, 1000, 2000]
        times = []
        
        for n in sizes:
            start_time = time.perf_counter()
            asyncio.run(self.fast_calc.calculate(n))
            duration = time.perf_counter() - start_time
            times.append(duration)
        
        # La complexité devrait être approximativement logarithmique
        # Les temps ne devraient pas croître de façon exponentielle
        for i in range(1, len(times)):
            growth_factor = times[i] / times[i-1]
            size_factor = sizes[i] / sizes[i-1]
            
            # Le facteur de croissance du temps devrait être << facteur de taille
            self.assertLess(growth_factor, size_factor,
                          f"Performance degradation too high: {growth_factor}")


def run_all_tests():
    """Lance tous les tests."""
    # Création de la suite de tests
    test_suite = unittest.TestSuite()
    
    # Ajout des classes de tests
    test_classes = [TestFibonacciCalculators, TestFibonacciProperties, TestPerformance]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # Exécution des tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    # Exécution des tests si le script est lancé directement
    success = run_all_tests()
    exit(0 if success else 1)