"""
Module d'interface utilisateur pour le calculateur Fibonacci
===========================================================

Gestion de l'affichage des résultats, barres de progression et comparaisons.
"""

import sys
import time
from typing import List, Optional
from dataclasses import dataclass
from threading import Thread, Event
import multiprocessing as mp

from fibonacci.utils import CalculationResult


def format_duration(seconds: float) -> str:
    """Formate une durée en secondes vers un format lisible."""
    if seconds < 1.0:
        return f"{seconds*1000:.1f}ms"
    elif seconds < 60.0:
        return f"{seconds:.2f}s"
    elif seconds < 3600.0:
        minutes = int(seconds // 60)
        secs = seconds % 60
        return f"{minutes}m{secs:.1f}s"
    else:
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = seconds % 60
        return f"{hours}h{minutes}m{secs:.1f}s"


def format_number(n: int, verbose: bool = False) -> str:
    """Formate un grand nombre pour l'affichage."""
    if verbose:
        return str(n)
    
    # Pour les nombres très grands, affiche seulement le début et la fin
    str_n = str(n)
    if len(str_n) <= 100:
        return str_n
    
    return f"{str_n[:50]}...{str_n[-50:]} ({len(str_n)} chiffres)"


class ProgressBar:
    """Barre de progression dynamique non-bloquante."""
    
    def __init__(self, width: int = 50):
        self.width = width
        self.current = 0.0
        self.running = True
        self._stop_event = Event()
        self._thread = None
    
    def start(self):
        """Démarre l'affichage de la barre de progression."""
        self._thread = Thread(target=self._display_loop, daemon=True)
        self._thread.start()
    
    def update(self, progress: float):
        """Met à jour la progression (0.0 à 1.0)."""
        self.current = max(0.0, min(1.0, progress))
    
    def stop(self):
        """Arrête l'affichage de la barre de progression."""
        self.running = False
        self._stop_event.set()
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=1.0)
        
        # Affichage final
        self._display_progress()
        print()  # Nouvelle ligne
    
    def _display_loop(self):
        """Boucle d'affichage de la progression."""
        while self.running and not self._stop_event.is_set():
            self._display_progress()
            self._stop_event.wait(0.1)  # Mise à jour toutes les 100ms
    
    def _display_progress(self):
        """Affiche la barre de progression actuelle."""
        filled = int(self.current * self.width)
        bar = "█" * filled + "░" * (self.width - filled)
        percent = self.current * 100
        
        sys.stdout.write(f"\r[{bar}] {percent:5.1f}%")
        sys.stdout.flush()


def display_progress(progress_callback=None) -> ProgressBar:
    """
    Crée et démarre une barre de progression.
    
    Args:
        progress_callback: Fonction optionnelle appelée à chaque mise à jour
    
    Returns:
        Instance de ProgressBar
    """
    progress_bar = ProgressBar()
    
    def update_with_callback(value):
        progress_bar.update(value)
        if progress_callback:
            progress_callback(value)
    
    progress_bar.update_func = update_with_callback
    progress_bar.start()
    return progress_bar


def display_results(results: List[CalculationResult], 
                   verbose: bool = False, 
                   details: bool = False):
    """
    Affiche les résultats de calcul.
    
    Args:
        results: Liste des résultats à afficher
        verbose: Si True, affiche la valeur complète du nombre
        details: Si True, affiche les détails de performance
    """
    print("\\n--- Résultats ---")
    
    for result in results:
        print(f"\\nAlgorithme: {result.name}")
        print(f"Durée: {format_duration(result.duration)}")
        
        if result.error:
            print(f"❌ Erreur: {result.error}")
            continue
        
        if result.result is not None:
            print("✅ Succès")
            
            if details:
                bit_length = result.result.bit_length()
                digit_count = len(str(result.result))
                print(f"Métadonnées:")
                print(f"  - Longueur en bits: {bit_length:,}")
                print(f"  - Nombre de chiffres: {digit_count:,}")
                print(f"  - Complexité mémoire: ~{bit_length//8:,} bytes")
            
            print(f"Résultat: {format_number(result.result, verbose)}")


def display_comparison(results: List[CalculationResult]):
    """
    Affiche un tableau de comparaison des résultats.
    
    Args:
        results: Liste des résultats à comparer
    """
    if len(results) <= 1:
        return
    
    print("\\n--- Tableau de Comparaison ---")
    
    # En-têtes
    print(f"{'Algorithme':<30} │ {'Durée':<12} │ {'Statut':<15} │ {'Performance'}")
    print("─" * 30 + "┼" + "─" * 14 + "┼" + "─" * 17 + "┼" + "─" * 15)
    
    # Tri par durée (succès en premier)
    sorted_results = sorted(results, 
                           key=lambda r: (r.error is not None, r.duration))
    
    fastest_time = None
    for result in sorted_results:
        if result.error is None and fastest_time is None:
            fastest_time = result.duration
    
    # Affichage des résultats
    for result in sorted_results:
        duration_str = format_duration(result.duration)
        
        if result.error:
            status = f"❌ {result.error[:10]}..."
            performance = "N/A"
        else:
            status = "✅ Succès"
            if fastest_time and fastest_time > 0:
                ratio = result.duration / fastest_time
                if ratio == 1.0:
                    performance = "Référence"
                else:
                    performance = f"{ratio:.2f}x plus lent"
            else:
                performance = "N/A"
        
        print(f"{result.name:<30} │ {duration_str:<12} │ {status:<15} │ {performance}")
    
    # Statistiques de validation croisée
    successful_results = [r for r in results if r.error is None]
    if len(successful_results) > 1:
        print(f"\\n✅ Validation croisée: {len(successful_results)} algorithmes cohérents")
        
        # Vérification de l'égalité des résultats
        first_result = successful_results[0].result
        all_equal = all(r.result == first_result for r in successful_results)
        
        if all_equal:
            print("🔒 Tous les résultats sont identiques (validation réussie)")
        else:
            print("⚠️  ATTENTION: Résultats incohérents détectés!")


def display_system_info():
    """Affiche des informations sur le système."""
    print(f"Système: {mp.cpu_count()} CPU logiques détectés")
    print(f"Support du parallélisme: {'Activé' if mp.cpu_count() > 1 else 'Limité'}")


def display_configuration(config):
    """Affiche la configuration actuelle."""
    print("--- Configuration d'Exécution ---")
    print(f"Calcul de F({config.n:,})")
    print(f"Timeout: {config.timeout}s")
    print(f"Algorithme: {config.algo}")
    print(f"Seuil de parallélisation: {config.threshold}")
    display_system_info()


def clear_line():
    """Efface la ligne courante du terminal."""
    sys.stdout.write("\\r" + " " * 80 + "\\r")
    sys.stdout.flush()