"""
Tests unitaires pour le module `pyfibonacci.cli.progress`.
"""

import asyncio
from unittest.mock import patch, MagicMock

import pytest
from pyfibonacci.cli.progress import progress_bar_manager

@pytest.mark.asyncio
@patch('pyfibonacci.cli.progress.tqdm')
async def test_progress_bar_manager_normal_flow(mock_tqdm):
    """
    Vérifie que le gestionnaire de barre de progression met à jour
    correctement la barre et se termine avec le message 'done'.
    """
    queue = asyncio.Queue()
    mock_pbar = MagicMock()
    mock_pbar.n = 0
    mock_pbar.total = 100
    # The context manager returns the mock object
    mock_tqdm.return_value.__enter__.return_value = mock_pbar

    total = 100
    description = "Testing"

    # Simuler le producteur qui envoie des mises à jour
    async def producer():
        await queue.put(10)
        await queue.put(20)
        await queue.put("done")

    # Lancer le gestionnaire de barre de progression et le producteur
    manager_task = asyncio.create_task(
        progress_bar_manager(queue, total, description)
    )
    await producer()
    await manager_task

    # Vérifications
    mock_tqdm.assert_called_once_with(total=total, desc=description, unit=" steps")
    assert mock_pbar.update.call_count == 2
    mock_pbar.update.assert_any_call(10)
    mock_pbar.update.assert_any_call(20)

    # Vérifie que la barre est bien mise à 100% à la fin
    assert mock_pbar.n == mock_pbar.total
    mock_pbar.refresh.assert_called_once()


@pytest.mark.asyncio
@patch('pyfibonacci.cli.progress.tqdm')
async def test_progress_bar_manager_timeout(mock_tqdm):
    """
    Vérifie que le gestionnaire se termine correctement si la file est vide
    après un timeout, sans message 'done'.
    """
    queue = asyncio.Queue()
    mock_pbar = MagicMock()
    # The context manager returns the mock object
    mock_tqdm.return_value.__enter__.return_value = mock_pbar

    total = 50
    description = "Timeout Test"

    async def producer():
        await queue.put(15)
        # Ne pas envoyer 'done' pour simuler un timeout

    manager_task = asyncio.create_task(
        progress_bar_manager(queue, total, description)
    )
    await producer()
    # Attendre un peu plus que le timeout interne de la fonction (1.0s)
    await asyncio.sleep(1.1)

    # La tâche devrait se terminer d'elle-même
    await manager_task

    mock_tqdm.assert_called_once_with(total=total, desc=description, unit=" steps")
    mock_pbar.update.assert_called_once_with(15)
    # Ne doit pas aller à 100% car 'done' n'a pas été reçu
    assert mock_pbar.n != mock_pbar.total


@pytest.mark.asyncio
@patch('pyfibonacci.cli.progress.tqdm')
async def test_progress_bar_manager_exception(mock_tqdm):
    """
    Vérifie que le gestionnaire gère une exception provenant de la file.
    """
    queue = asyncio.Queue()
    # Mocker `get` pour lever une exception
    queue.get = MagicMock(side_effect=ValueError("Test Exception"))
    mock_pbar = MagicMock()
    mock_tqdm.return_value.__enter__.return_value = mock_pbar

    total = 100
    description = "Exception Test"

    # La tâche devrait attraper l'exception et se terminer
    await progress_bar_manager(queue, total, description)

    # Vérifie que la barre de progression a été créée mais pas mise à jour
    mock_tqdm.assert_called_once_with(total=total, desc=description, unit=" steps")
    mock_pbar.update.assert_not_called()
