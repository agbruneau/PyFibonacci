# Justifications Architecturales - Migration Go vers Python

Ce document détaille les choix techniques et architecturaux effectués lors de la migration de l'application PyFibonacci de Go vers Python 3.11+. L'objectif n'était pas une simple traduction, mais une adaptation idiomatique des concepts de haute performance de Go à l'écosystème Python moderne.

## 1. Concurrence : `asyncio` et `TaskGroup`

**Problème :** L'application Go utilise des goroutines et un `errgroup` pour exécuter plusieurs algorithmes de Fibonacci en parallèle lorsque l'utilisateur spécifie l'option `--algo all`. Il fallait trouver un équivalent en Python qui offre une "concurrence structurée".

**Solution :** J'ai choisi `asyncio` et plus spécifiquement `asyncio.TaskGroup` (disponible depuis Python 3.11).

**Justification :**

1.  **Concurrence Structurée :** `TaskGroup` est l'équivalent direct du `errgroup` de Go. Il garantit que le programme attend la fin de toutes les tâches lancées dans le groupe avant de continuer, même en cas d'erreur. Cela prévient les "fuites" de tâches et simplifie grandement la gestion du cycle de vie des opérations concurrentes.
2.  **Gestion des E/S :** Bien que le calcul de Fibonacci soit principalement lié au CPU, `asyncio` est le framework standard pour gérer des opérations qui peuvent attendre (I/O, timeouts, etc.). L'utilisation d'`asyncio` a permis d'intégrer très proprement la gestion des **timeouts** (`asyncio.timeout`) et la communication avec l'interface utilisateur via `asyncio.Queue` (voir ci-dessous).
3.  **Modernité :** `TaskGroup` est l'approche moderne et recommandée pour la concurrence en Python, remplaçant des patrons plus anciens et plus complexes comme `asyncio.gather` avec une gestion manuelle des erreurs.

## 2. Parallélisme CPU-Bound : `ProcessPoolExecutor`

**Problème :** L'arithmétique sur de très grands nombres est une tâche intensive en CPU ("CPU-bound"). En Python, à cause du **Global Interpreter Lock (GIL)**, l'utilisation de threads (`threading` ou `asyncio` avec `ThreadPoolExecutor`) ne permet pas d'exécuter du code Python sur plusieurs cœurs de processeur simultanément.

**Solution :** J'ai utilisé `concurrent.futures.ProcessPoolExecutor`.

**Justification :**

1.  **Contournement du GIL :** `ProcessPoolExecutor` lance des processus Python distincts, chacun avec son propre interpréteur et son propre GIL. C'est le moyen standard et le plus robuste en Python pour obtenir un véritable parallélisme sur les machines multi-cœurs pour les tâches gourmandes en CPU.
2.  **Abstration et Simplicité :** L'API de `concurrent.futures` est de haut niveau. Elle permet de soumettre une tâche à un pool de processus (`loop.run_in_executor`) et d'attendre le résultat (`await`) de manière très similaire à l'appel d'une fonction asynchrone normale, masquant ainsi la complexité de la communication inter-processus.
3.  **Stratégie de Dispatch :** J'ai implémenté un dispatcher (`multiplication.py`) qui choisit dynamiquement entre la multiplication native de Python (pour les "petits" nombres) et la multiplication parallèle via le `ProcessPoolExecutor` (pour les très grands nombres). Cette stratégie garantit que le coût de la communication inter-processus n'est engagé que lorsque le gain en performance de calcul est significatif.

## 3. Gestion de la Mémoire et Pooling d'Objets

**Problème :** Le code Go utilise intensivement `sync.Pool` pour réutiliser des objets `big.Int` et éviter les allocations mémoire, une stratégie clé pour la "Zero-Allocation".

**Solution :** J'ai décidé de **ne pas** implémenter un pool d'objets en Python.

**Justification :**

1.  **Immuabilité des `int` Python :** Les entiers (`int`) en Python sont des objets immuables. On ne peut pas modifier leur valeur en place. Par conséquent, il est impossible de "réinitialiser" un objet `int` existant pour le réutiliser. Chaque nouvelle valeur entière nécessite une nouvelle allocation d'objet.
2.  **Gestion de la Mémoire Efficace de Python :** Le gestionnaire de mémoire de CPython est déjà très optimisé, notamment pour les petits entiers qui sont souvent mis en cache et réutilisés (interning). Pour les grands nombres, bien que de nouvelles allocations soient nécessaires, le Garbage Collector de Python est efficace pour récupérer la mémoire.
3.  **Complexité vs. Bénéfice :** Tenter de créer un pool pour des objets mutables qui encapsuleraient des entiers (par exemple, une classe `MutableInt`) ajouterait une complexité considérable au code et irait à l'encontre du caractère idiomatique de Python. Le gain de performance serait probablement marginal et ne justifierait pas la perte de clarté et de simplicité.

En conclusion, la stratégie de pooling de Go a été consciemment écartée au profit de l'utilisation directe des types de données natifs et idiomatiques de Python, dont la performance est jugée suffisante pour cette application.
