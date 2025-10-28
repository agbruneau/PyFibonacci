"""
Module pour la gestion de la barre de progression de l'interface CLI.

Ce module fournit un gestionnaire asynchrone pour afficher et mettre à jour
une barre de progression `tqdm` en fonction des messages reçus via une
`asyncio.Queue`.
"""

import asyncio
from tqdm.asyncio import tqdm


async def progress_bar_manager(
    queue: asyncio.Queue, total: int, description: str
) -> None:
    """Gère l'affichage et la mise à jour asynchrones d'une barre de progression.

    Cette coroutine s'exécute en parallèle du calcul principal. Elle écoute les
    messages sur une `asyncio.Queue` pour mettre à jour la barre de progression
    `tqdm`. La communication est unidirectionnelle : le gestionnaire reçoit des
    commandes de l'algorithme qui effectue le calcul.

    Args:
        queue (asyncio.Queue): La file d'attente pour recevoir les messages.
            Les messages attendus sont soit des entiers, indiquant le nombre
            de pas à avancer, soit la chaîne "done" pour signaler la fin.
        total (int): La valeur maximale de la barre de progression, correspondant
            à l'achèvement complet de la tâche.
        description (str): Un texte descriptif affiché à côté de la barre de
            progression.
    """
    with tqdm(total=total, desc=description, unit=" steps") as pbar:
        while True:
            try:
                # Attend un message avec un timeout pour éviter un blocage infini.
                message = await asyncio.wait_for(queue.get(), timeout=1.0)

                if message == "done":
                    pbar.n = pbar.total  # Assure que la barre atteint 100%
                    pbar.refresh()
                    break

                if isinstance(message, int):
                    pbar.update(message)

                queue.task_done()
            except asyncio.TimeoutError:
                # Si la file est vide après le timeout, on suppose que la tâche
                # productrice s'est terminée sans envoyer "done".
                if queue.empty():
                    break
            except Exception:
                # En cas d'autre erreur, on interrompt la barre de progression.
                break
