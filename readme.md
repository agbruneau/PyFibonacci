# Calculateur de Suite de Fibonacci - Équivalent Python

## Vue d'ensemble

Ce projet est l'équivalent Python du calculateur Fibonacci Go haute performance. Il implémente deux algorithmes avancés pour le calcul de très grands nombres de Fibonacci avec des optimisations de performance et une architecture modulaire.

## Architecture du Projet

```
fibonacci_calculator/
├── main.py                      # Point d'entrée et orchestration
├── fibonacci/
│   ├── __init__.py
│   ├── calculator.py            # Interface et décorateur principal
│   ├── fast_doubling.py         # Algorithme Fast Doubling
│   ├── matrix_exponentiation.py # Algorithme matriciel
│   └── utils.py                 # Utilitaires communs
├── cli/
│   ├── __init__.py
│   └── ui.py                    # Interface utilisateur
├── tests/
│   ├── __init__.py
│   ├── test_calculator.py
│   ├── test_fast_doubling.py
│   └── test_matrix.py
├── requirements.txt
└── README.md
```

## Fonctionnalités Principales

- **Calcul sur de Très Grands Nombres** : Utilisation des entiers arbitraires de Python
- **Algorithmes Multiples** :
  - **Fast Doubling** : O(log n) avec optimisations parallèles
  - **Exponentiation Matricielle** : O(log n) avec exploitations des symétries
- **Optimisations de Performance** :
  - Table de consultation (LUT) pour les petits nombres
  - Parallélisation adaptative des multiplications
  - Gestion optimisée de la mémoire
- **Interface CLI Riche** :
  - Barre de progression dynamique
  - Modes de comparaison et calibration
  - Validation croisée des résultats

## Installation

```bash
# Cloner le repository
git clone <votre-repo-url>
cd fibonacci_calculator

# Créer un environnement virtuel
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows

# Installer les dépendances
pip install -r requirements.txt
```

## Utilisation

### Exemples de base

```bash
# Calculer F(1000000) avec tous les algorithmes
python main.py -n 1000000 -algo all

# Utiliser uniquement l'algorithme Fast Doubling
python main.py -n 1000000 -algo fast -d

# Mode calibration pour optimiser les performances
python main.py --calibrate

# Calculer avec timeout personnalisé
python main.py -n 10000000 --timeout 600 -v
```

### Options de ligne de commande

| Option | Description | Défaut |
|--------|-------------|--------|
| `-n` | Indice du nombre de Fibonacci à calculer | 1000000 |
| `-algo` | Algorithme : `fast`, `matrix`, ou `all` | `all` |
| `--timeout` | Timeout en secondes | 300 |
| `--threshold` | Seuil de parallélisation | 1000 |
| `-d, --details` | Afficher les détails de performance | False |
| `-v, --verbose` | Afficher la valeur complète | False |
| `--calibrate` | Mode calibration | False |

## Optimisation des Performances

### Calibration Automatique

```bash
python main.py --calibrate
```

Cette commande teste différents seuils de parallélisation et recommande la valeur optimale pour votre machine.

### Comparaison d'Algorithmes

```bash
python main.py -n 5000000 -algo all --threshold 1000 -d
```

Execute les deux algorithmes en parallèle et compare leurs performances avec validation croisée.

## Architecture Technique

### Patrons de Conception Implémentés

1. **Décorateur** : `FibCalculator` ajoute des fonctionnalités (LUT, progression) aux algorithmes
2. **Adaptateur** : Conversion entre interfaces de progression
3. **Registre** : Gestion centralisée des implémentations d'algorithmes
4. **Factory** : Construction des calculateurs via `new_calculator()`

### Principes SOLID

- **SRP** : Séparation claire des responsabilités entre modules
- **OCP** : Facilité d'ajout de nouveaux algorithmes
- **DIP** : Dépendance sur des abstractions plutôt que des implémentations

### Optimisations

- **Table de Consultation** : O(1) pour F(0) à F(93)
- **Parallélisation** : Multiplications concurrentes pour les grands nombres
- **Gestion Mémoire** : Réutilisation d'objets pour minimiser les allocations

## Tests et Validation

```bash
# Tests unitaires
python -m pytest tests/ -v

# Tests de performance
python -m pytest tests/ -v --benchmark

# Validation des propriétés mathématiques
python -m pytest tests/test_properties.py
```

## Exemples d'Algorithmes

### Fast Doubling

Utilise les identités :
- F(2k) = F(k) × [2×F(k+1) - F(k)]
- F(2k+1) = F(k)² + F(k+1)²

### Exponentiation Matricielle

Calcule Q^(n-1) où Q = [[1,1],[1,0]] est la matrice de Fibonacci.

## Performance

Sur un processeur moderne :
- F(1,000,000) : ~0.1 seconde
- F(10,000,000) : ~2-5 secondes  
- F(100,000,000) : ~30-60 secondes

## Contributions

1. Fork le projet
2. Créer une branche pour votre fonctionnalité
3. Ajouter des tests
4. Soumettre une pull request

## Licence

Distribué sous licence MIT. Voir `LICENSE` pour plus de détails.