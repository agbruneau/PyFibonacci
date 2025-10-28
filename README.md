# PyFibonacci - Calculateur de Fibonacci Haute Performance

[![CI Pipeline](https://github.com/agbruneau/PyFibonacci/actions/workflows/ci.yml/badge.svg)](https://github.com/agbruneau/PyFibonacci/actions/workflows/ci.yml)
[![Coverage Status](https://coveralls.io/repos/github/agbruneau/PyFibonacci/badge.svg?branch=main)](https://coveralls.io/github/agbruneau/PyFibonacci?branch=main)

Ce projet propose deux implémentations d'un calculateur de nombres de Fibonacci de haute performance : une en **Python 3.11+** et une en **Rust**. L'implémentation Python est une migration idiomatique d'une application Go, préservant les optimisations tout en adoptant les meilleures pratiques de l'écosystème Python moderne.

## Features

### Implémentation Python

-   **Algorithmes Multiples** : Implémentation de plusieurs algorithmes (itératif, exponentiation matricielle, fast doubling).
-   **Haute Performance pour Grands Nombres** : Utilise `asyncio` pour la concurrence et un `ProcessPoolExecutor` pour paralléliser les multiplications de très grands nombres.
-   **Calibration Automatique** : Inclut un outil pour calibrer et trouver le seuil de performance optimal pour la multiplication parallèle.
-   **Interface en Ligne de Commande (CLI) Complète** : Interface flexible avec des options pour choisir les algorithmes, définir des timeouts, et afficher des barres de progression.
-   **Qualité de Code et Tests** : Suite de tests complète avec `pytest`, `Hypothesis` et `pytest-benchmark`.

### Implémentation Rust (`fib_rs`)

-   **Performance Maximale** : Écrit en Rust pour une performance proche du niveau système, sans garbage collector.
-   **Algorithme Optimisé** : Utilise une implémentation itérative de "Fast Doubling" pour une efficacité maximale.
-   **Gestion des Très Grands Nombres** : S'appuie sur le crate `num_bigint` pour une arithmétique de précision arbitraire.
-   **Binaire Autonome** : Peut être compilé en un binaire natif unique, rapide et portable.

## Architecture (Python)

-   `src/pyfibonacci/`: Le paquet principal.
    -   `core/`: Contient la logique métier pure (algorithmes, multiplication parallèle).
    -   `cli/`: Gère l'interaction avec l'utilisateur en ligne de commande.
-   `src/pyfibonacci/app.py`: Le point d'orchestration principal.
-   `tests/`: Contient la suite de tests complète.

## Installation

### Python

Ce projet utilise `pyproject.toml` pour la gestion des dépendances.

1.  **Clonez le dépôt :**
    ```bash
    git clone https://github.com/agbruneau/PyFibonacci.git
    cd PyFibonacci
    ```

2.  **Installez les dépendances :**
    Il est recommandé d'utiliser un environnement virtuel.
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    pip install -e .[dev]
    ```

### Rust

1.  **Installez Rust et Cargo :**
    Suivez les instructions sur [rustup.rs](https://rustup.rs/).

2.  **Compilez le projet :**
    Naviguez dans le répertoire `fib_rs` et utilisez Cargo pour compiler en mode release.
    ```bash
    cd fib_rs
    cargo build --release
    ```
    Le binaire se trouvera dans `target/release/fib_rs`.

## Utilisation

### Python

Le projet Python est accessible via la commande `pyfibonacci` grâce à un point d'entrée défini dans `pyproject.toml`.

**Syntaxe de base :**
```bash
pyfibonacci -n <nombre> [OPTIONS]
```

**Exemples :**

-   **Calculer F(1 000 000) avec l'algorithme par défaut (`fast_doubling`) et afficher les détails :**
    ```bash
    pyfibonacci -n 1000000 --details
    ```

-   **Comparer la performance de tous les algorithmes pour F(50) :**
    ```bash
    pyfibonacci -n 50 --algo all
    ```

-   **Trouver le seuil de multiplication parallèle optimal pour votre machine :**
    Cette commande exécute une série de benchmarks pour déterminer le nombre de chiffres à partir duquel la multiplication parallèle est plus performante.
    ```bash
    pyfibonacci --calibrate
    ```

-   **Obtenir de l'aide sur les commandes et options disponibles :**
    ```bash
    pyfibonacci --help
    ```

### Rust

L'exécutable Rust peut être lancé via Cargo ou en exécutant le binaire compilé directement.

**Syntaxe :**

-   **Avec Cargo :**
    La commande `cargo run` compile et exécute le programme. Le double tiret `--` est utilisé pour séparer les arguments de Cargo de ceux de votre programme.
    ```bash
    cd fib_rs
    cargo run --release -- <nombre>
    ```

-   **Avec le binaire direct :**
    Après une compilation avec `cargo build --release`, le binaire se trouve dans `target/release/`.
    ```bash
    ./fib_rs/target/release/fib_rs <nombre>
    ```

**Exemple :**

-   **Calculer F(1 000 000) avec Rust :**
    ```bash
    cd fib_rs
    cargo run --release -- 1000000
    ```

## Suite de Tests (Python)

Pour exécuter les tests, assurez-vous que `PYTHONPATH` est correctement configuré.

### Linux / macOS

```bash
PYTHONPATH=src python3 -m pytest
```

### Windows (PowerShell)

```powershell
$env:PYTHONPATH="src"; python3 -m pytest
```

### Générer le rapport de couverture

```bash
PYTHONPATH=src python3 -m pytest --cov=src tests/
```
