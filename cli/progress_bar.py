import sys

def progress_bar(current, total):
    """
    Affiche une barre de progression dynamique dans la console.

    Cette fonction est conçue pour être appelée dans une boucle afin de
    montrer la progression d'une tâche.

    Args:
        current (int): L'itération actuelle.
        total (int): Le nombre total d'itérations.
    """
    bar_length = 40
    percent = 100.0 * current / total
    sys.stdout.write('\r')
    progress = int(bar_length * current / total)
    sys.stdout.write("Progression Moyenne : {:.2f}% [".format(percent) + "█" * progress + " " * (bar_length - progress) + "]")
    sys.stdout.flush()
    if current == total:
        print()
