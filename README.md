# PyFibonacci - Calculateur de Fibonacci Haute Performance en Python

[![CI Pipeline](https://github.com/agbruneau/PyFibonacci/actions/workflows/ci.yml/badge.svg)](https://github.com/agbruneau/PyFibonacci/actions/workflows/ci.yml)
[![Coverage Status](https://coveralls.io/repos/github/agbruneau/PyFibonacci/badge.svg?branch=main)](https://coveralls.io/github/agbruneau/PyFibonacci?branch=main)

Ce projet est une migration idiomatique en Python 3.11+ d'une application Go de haute performance pour le calcul des nombres de Fibonacci. L'objectif est de préserver les optimisations et l'architecture de la source Go tout en adoptant les meilleures pratiques et bibliothèques de l'écosystème Python moderne.

## Features

-   **Algorithmes Multiples** : Implémentation de plusieurs algorithmes (itératif, exponentiation matricielle, fast doubling) pour comparaison.
-   **Haute Performance pour Grands Nombres** : Utilise `asyncio` pour la concurrence et un `ProcessPoolExecutor` pour paralléliser les multiplications de très grands nombres.
-   **Calibration Automatique** : Inclut un outil pour calibrer et trouver le seuil de performance optimal pour la multiplication parallèle sur une machine donnée.
-   **Interface en Ligne de Commande (CLI) Complète** : Interface flexible avec des options pour choisir les algorithmes, définir des timeouts, et afficher des barres de progression détaillées.
-   **Qualité de Code et Tests** : Suite de tests complète avec `pytest`, `Hypothesis` pour les tests basés sur les propriétés, et `pytest-benchmark` pour les mesures de performance.

## Architecture

Le projet adopte une structure de paquet moderne et une séparation claire des préoccupations :

-   `pyfibonacci/`: Le paquet principal.
    -   `core/`: Contient la logique métier pure, y compris les implémentations des algorithmes (`algorithms.py`), la stratégie de multiplication parallèle (`multiplication.py`) et les contextes de données.
    -   `cli/`: Gère toute l'interaction avec l'utilisateur en ligne de commande, y compris l'analyse des arguments (`args.py`), la barre de progression (`progress.py`) et le point d'entrée (`main.py`).
-   `app.py`: Le point d'orchestration principal, qui connecte la CLI à la logique métier.
-   `tests/`: Contient la suite de tests complète (unitaires, de propriété et benchmarks).
-   `main.py`: Le point d'entrée global pour une exécution facile.

## Installation

Ce projet utilise `pyproject.toml` pour la gestion des dépendances.

1.  **Clonez le dépôt :**
    ```bash
    git clone <url-du-repo>
    cd PyFibonacci-Python
    ```

2.  **Installez les dépendances :**
    Il est recommandé d'utiliser un environnement virtuel.
    ```bash
    python -m venv venv
    source venv/bin/activate
    ```
    Installez le projet en mode éditable avec les dépendances de développement (pour les tests) :
    ```bash
    pip install -e .[dev]
    ```

## Utilisation

L'application s'exécute en ligne de commande.

**Syntaxe de base :**
```bash
python -m pyfibonacci.cli.main -n <nombre> [OPTIONS]
```

**Arguments :**

-   `-n INT`: (Obligatoire) L'indice du nombre de Fibonacci à calculer.
-   `--algo {iterative,matrix,fast,all}`: L'algorithme à utiliser (par défaut: `fast`).
-   `--timeout FLOAT`: Timeout en secondes pour un calcul (par défaut: 10.0).
-   `--threshold INT`: Seuil (en nombre de chiffres) pour passer à la multiplication parallèle (par défaut: 10000).
-   `-d, --details`: Affiche une barre de progression pour les longs calculs.
-   `--calibrate`: Lance un benchmark pour trouver le `--threshold` optimal.
-   `--version`: Affiche la version du programme.

**Exemples :**

-   **Calculer F(100) avec l'algorithme par défaut (`fast`):**
    ```bash
    python -m pyfibonacci.cli.main -n 100
    ```

-   **Calculer F(10000) avec l'algorithme matriciel et afficher la barre de progression :**
    ```bash
    python -m pyfibonacci.cli.main -n 10000 --algo matrix --details
    ```

-   **Comparer tous les algorithmes pour F(50) :**
    ```bash
    python -m pyfibonacci.cli.main -n 50 --algo all
    ```

-   **Trouver le seuil de multiplication optimal pour votre machine :**
    ```bash
    python -m pyfibonacci.cli.main --calibrate
    ```

## Suite de Tests

Le projet est fourni avec une suite de tests robuste utilisant `pytest`.

Pour exécuter la suite de tests, vous devez d'abord définir la variable d'environnement `PYTHONPATH` pour que Python puisse trouver les modules du projet. La syntaxe varie selon votre système d'exploitation.

### Linux / macOS

```bash
PYTHONPATH=src python3 -m pytest
```

### Windows (PowerShell)

```powershell
$env:PYTHONPATH="src"; python3 -m pytest
```

### Windows (Command Prompt)

```cmd
set PYTHONPATH=src && python3 -m pytest
```

### Exécuter les tests avec le rapport de couverture

Pour générer un rapport de couverture de test, utilisez l'option `--cov` :

```bash
# Pour Linux / macOS
PYTHONPATH=src python3 -m pytest --cov=src tests/

# Pour Windows PowerShell
$env:PYTHONPATH="src"; python3 -m pytest --cov=src tests/
```
