# Calculateur de Suite de Fibonacci de Haute Performance

## 1. Résumé

Ce projet propose un calculateur pour la suite de Fibonacci en Python, conçu comme une étude de cas sur l'implémentation et la comparaison d'algorithmes optimisés pour le calcul sur de très grands entiers. L'objectif est de fournir une base de code claire et performante, avec une documentation académique en français, à des fins pédagogiques.

## 2. Caractéristiques Principales

*   **Calcul sur de Très Grands Nombres** : Utilise le support natif de Python pour les entiers de précision arbitraire, permettant de calculer des termes de Fibonacci extraordinairement grands sans dépassement de capacité.
*   **Algorithmes Multiples** : Implémentation de plusieurs algorithmes de complexité logarithmique pour une comparaison de performance :
    *   **Fast Doubling** : Un algorithme efficace basé sur des identités mathématiques spécifiques à la suite.
    *   **Exponentiation Matricielle** : Une méthode classique qui utilise la puissance d'une matrice de transformation.
    *   **Fast Doubling avec Karatsuba** : Une variante du Fast Doubling qui remplace la multiplication standard par l'algorithme de Karatsuba pour accélérer les calculs sur de très grands nombres.
*   **Interface en Ligne de Commande (CLI) Riche** :
    *   Comparaison directe des performances des algorithmes.
    *   Barre de progression pour suivre l'exécution.
    *   Configuration de timeouts pour les calculs longs.
    *   Rapport de performance détaillé.

## 3. Architecture Logicielle

Le projet est structuré en trois modules principaux pour assurer une bonne séparation des responsabilités :

*   `fibonacci/` : Le domaine métier. Contient les implémentations des algorithmes de calcul.
*   `cli/` : La couche de présentation. Gère les interactions avec l'utilisateur via l'interface en ligne de commande.
*   `tests/` : Contient les tests unitaires qui valident l'exactitude des algorithmes.

## 4. Installation

Le projet nécessite Python 3. Pour installer les dépendances, exécutez la commande suivante :

```bash
pip install -r requirements.txt
```

## 5. Guide d'Utilisation

L'exécutable s'utilise de la manière suivante :
```bash
python3 -m cli.main [options]
```

### Options de la Ligne de Commande

| Flag        | Alias     | Description                                               | Défaut |
|-------------|-----------|-----------------------------------------------------------|--------|
| `-n`        |           | L'indice 'n' de la suite de Fibonacci à calculer (requis). |        |
| `-t`        | `--timeout` | Délai d'exécution maximal en secondes.                    | 300    |
| `-d`        | `--details` | Afficher les détails de performance et les métadonnées.   | false  |

### Exemples d'Utilisation

1.  **Calculer F(1 000 000) et comparer les algorithmes :**
    ```bash
    python3 -m cli.main -n 1000000
    ```

2.  **Calculer F(10 000 000) avec un timeout de 10 minutes et un rapport détaillé :**
    ```bash
    python3 -m cli.main -n 10000000 -t 600 -d
    ```

## 6. Validation et Tests

Le projet est doté d'une suite de tests pour garantir son exactitude. Pour exécuter les tests unitaires :

```bash
PYTHONPATH=. pytest
```
Cette commande exécute tous les tests du projet, validant que les algorithmes produisent des résultats corrects pour des entrées connues.
