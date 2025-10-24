"""
Module pour la gestion de la barre de progression de l'interface CLI.
"""
import asyncio
from typing import AsyncGenerator
from tqdm.asyncio import tqdm

async def progress_bar_manager(
    queue: asyncio.Queue,
    total: int,
    description: str
) -> None:
    """Gère l'affichage et la mise à jour d'une barre de progression `tqdm`.

    Cette coroutine écoute les messages entrants sur une file `asyncio.Queue`.
    Elle met à jour la barre de progression en fonction des messages reçus
    jusqu'à ce qu'un message "done" soit reçu ou que la file soit vide
    après un timeout.

    Args:
        queue: La file d'attente `asyncio` depuis laquelle lire les
               mises à jour de progression. Les messages peuvent être des
               entiers (pour incrémenter la barre) ou la chaîne "done"
               pour terminer.
        total: La valeur totale de la barre de progression, représentant
               l'achèvement.
        description: Le texte à afficher à côté de la barre de progression.
    """
    with tqdm(total=total, desc=description, unit=" steps") as pbar:
        while True:
            try:
                # On attend un message de progression avec un petit timeout
                # pour ne pas bloquer indéfiniment si le producteur se termine.
                message = await asyncio.wait_for(queue.get(), timeout=1.0)

                if message == "done":
                    pbar.n = pbar.total # S'assure que la barre va à 100%
                    pbar.refresh()
                    break

                pbar.update(message)
                queue.task_done()
            except asyncio.TimeoutError:
                # Si le producteur s'arrête sans envoyer "done", on sort.
                if queue.empty():
                    break
            except Exception:
                break
