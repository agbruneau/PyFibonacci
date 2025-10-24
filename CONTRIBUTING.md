# Guide de Contribution

Nous sommes ravis que vous envisagiez de contribuer à ce projet ! Toute contribution, qu'il s'agisse de corriger des bugs, d'ajouter de nouvelles fonctionnalités ou d'améliorer la documentation, est la bienvenue.

Ce document fournit un ensemble de lignes directrices pour vous aider à démarrer.

## Table des matières
1.  [Comment contribuer](#comment-contribuer)
    *   [Signaler un bug](#signaler-un-bug)
    *   [Suggérer une amélioration](#suggérer-une-amélioration)
    *   [Votre première contribution de code](#votre-première-contribution-de-code)
2.  [Mise en place de l'environnement de développement](#mise-en-place-de-lenvironnement-de-développement)
3.  [Standards de codage](#standards-de-codage)
    *   [Style du code](#style-du-code)
    *   [Messages de commit](#messages-de-commit)
4.  [Processus de Pull Request](#processus-de-pull-request)

## Comment contribuer

### Signaler un bug

Si vous pensez avoir trouvé un bug, veuillez vous assurer qu'il n'a pas déjà été signalé en consultant la section [Issues](https://github.com/agbruneau/PyFibonacci/issues) de GitHub.

Si le bug n'est pas encore signalé, veuillez ouvrir une nouvelle issue. Assurez-vous d'inclure :
*   Un titre clair et descriptif.
*   Une description aussi détaillée que possible du problème.
*   Les étapes pour reproduire le bug.
*   La version du projet que vous utilisez.
*   Toute information contextuelle pertinente (système d'exploitation, version de Python, etc.).

### Suggérer une amélioration

Si vous avez une idée pour une amélioration, n'hésitez pas à ouvrir une nouvelle issue pour en discuter. Veuillez fournir autant de contexte que possible et expliquer pourquoi cette amélioration serait bénéfique pour le projet.

### Votre première contribution de code

Les contributions de code sont les bienvenues ! Si vous souhaitez travailler sur une issue existante, veuillez laisser un commentaire pour indiquer que vous vous en chargez.

## Mise en place de l'environnement de développement

Pour configurer votre environnement de développement local, suivez ces étapes :

1.  **Forkez le projet** sur GitHub.
2.  **Clonez votre fork** en local :
    ```bash
    git clone https://github.com/agbruneau/PyFibonacci.git
    cd PyFibonacci
    ```
3.  **Créez un environnement virtuel** et activez-le. Il est fortement recommandé d'utiliser un environnement virtuel pour isoler les dépendances du projet.
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    ```
4.  **Installez les dépendances** du projet, y compris les dépendances de développement :
    ```bash
    pip install -e .[dev]
    ```

Vous êtes maintenant prêt à commencer le développement !

## Standards de codage

### Style du code

Ce projet adhère aux conventions de style définies par la [PEP 8](https://www.python.org/dev/peps/pep-0008/). Nous utilisons `black` pour le formatage automatique du code et `ruff` pour le linting.

Avant de soumettre votre code, veuillez exécuter ces outils pour vous assurer que le code est conforme :
```bash
black src tests
ruff check src tests
```

Toutes les docstrings doivent être rédigées en **français** et suivre le style [Google Style Python Docstrings](https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings).

### Messages de commit

Vos messages de commit doivent être clairs et suivre un format sémantique. Chaque message doit consister en :
*   Un **titre** concis (50 caractères maximum) écrit à l'impératif (par exemple, "Ajoute la fonctionnalité X" et non "Ajout de la fonctionnalité X").
*   Un **corps** optionnel plus détaillé, expliquant le "quoi" et le "pourquoi" de la modification.

Exemple :
```
feat: Ajoute la calibration automatique du seuil de parallélisme

Implémente un nouvel argument `--calibrate` qui exécute une série de benchmarks pour déterminer le nombre optimal de chiffres à partir duquel la multiplication parallèle devient plus performante que la multiplication standard.
```

## Processus de Pull Request

1.  Assurez-vous que votre fork est à jour avec le dépôt principal.
2.  Créez une nouvelle branche pour vos modifications : `git checkout -b nom-de-votre-branche`.
3.  Effectuez vos modifications et commitez-les en suivant les standards décrits ci-dessus.
4.  Assurez-vous que la suite de tests passe avec succès. Vous pouvez également générer un rapport de couverture de test localement pour visualiser les parties du code qui ne sont pas testées.
    ```bash
    # Exécuter les tests
    PYTHONPATH=src python3 -m pytest

    # Générer un rapport de couverture HTML
    PYTHONPATH=src python3 -m pytest --cov=src tests/ --cov-report=html
    ```
    Le rapport sera disponible dans le répertoire `htmlcov/`. Ouvrez `htmlcov/index.html` dans votre navigateur pour l'inspecter.
5.  Poussez votre branche vers votre fork sur GitHub.
6.  Ouvrez une **Pull Request** (PR) vers la branche `main` du dépôt principal.
7.  Dans la description de la PR, liez l'issue que votre PR résout (par exemple, `Closes #123`).
8.  L'équipe du projet examinera votre PR. Des modifications pourront vous être demandées avant la fusion.

Merci encore pour votre contribution !
