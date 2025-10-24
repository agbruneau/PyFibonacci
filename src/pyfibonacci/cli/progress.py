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
    """
    Consomme les messages d'une file d'attente pour mettre à jour une barre de progression tqdm.
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
