"""
Tests pour le module principal de l'application.
"""
import asyncio
import sys
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from pyfibonacci.app import (_run_single_algorithm, _run_all_algorithms, main_async)
from pyfibonacci.core.context import CalculationContext


@pytest.fixture
def mock_context():
    """Fixture pour un contexte de calcul mocké."""
    return MagicMock(spec=CalculationContext)


@pytest.mark.asyncio
async def test_run_single_algorithm_sync_and_async(mock_context):
    """
    Vérifie que _run_single_algorithm gère correctement les
    algorithmes synchrones et asynchrones.
    """
    with patch("pyfibonacci.app.ALGORITHM_REGISTRY", {"test_sync": MagicMock(), "test_async": AsyncMock()}) as mock_registry:
        # Test avec un algorithme synchrone
        mock_registry["test_sync"].return_value = 123
        await _run_single_algorithm(mock_context, 10, "test_sync", timeout=1)
        mock_registry["test_sync"].assert_called_once_with(10)

        # Test avec un algorithme asynchrone
        mock_registry["test_async"].return_value = 456
        await _run_single_algorithm(mock_context, 10, "test_async", timeout=1)
        mock_registry["test_async"].assert_called_once_with(mock_context, 10)


@pytest.mark.asyncio
async def test_run_single_algorithm_timeout(mock_context, capsys):
    """
    Vérifie que le timeout est correctement géré dans _run_single_algorithm.
    """
    with patch("pyfibonacci.app.ALGORITHM_REGISTRY", {"test_async": AsyncMock(side_effect=asyncio.TimeoutError)}):
        await _run_single_algorithm(mock_context, 10, "test_async", timeout=0.01)
        captured = capsys.readouterr()
        assert "ERREUR: L'algorithme 'test_async' a dépassé le timeout" in captured.err


@pytest.mark.asyncio
async def test_run_all_algorithms(mock_context, capsys):
    """
    Vérifie que _run_all_algorithms exécute tous les algorithmes
    et gère les erreurs individuellement.
    """
    with patch("pyfibonacci.app.ALGORITHM_REGISTRY", {
        "sync": MagicMock(return_value=1),
        "async": AsyncMock(return_value=2),
        "timeout": AsyncMock(side_effect=asyncio.TimeoutError)
    }) as mock_registry:
        await _run_all_algorithms(mock_context, 10, timeout=1)

        # Vérifie que les fonctions ont été appelées
        mock_registry["sync"].assert_called_once_with(10)
        mock_registry["async"].assert_called_once_with(mock_context, 10)
        mock_registry["timeout"].assert_called_once_with(mock_context, 10)

        # Vérifie la sortie
        captured = capsys.readouterr()
        assert "Résultat (sync): Calcul terminé." in captured.out
        assert "Résultat (async): Calcul terminé." in captured.out
        assert "Résultat (timeout): TIMEOUT" in captured.err


@pytest.mark.asyncio
@patch("pyfibonacci.app.parse_args")
@patch("pyfibonacci.app.run_calibration", new_callable=AsyncMock)
@patch("pyfibonacci.app.ProcessPoolExecutor")
async def test_main_async_calibrate(mock_process_pool_executor, mock_run_calibration, mock_parse_args):
    """
    Vérifie que `main_async` appelle `run_calibration` lorsque
    l'argument --calibrate est fourni.
    """
    mock_args = MagicMock(calibrate=True, n=None)
    mock_parse_args.return_value = mock_args

    await main_async()
    mock_run_calibration.assert_called_once()


@pytest.mark.asyncio
@patch("pyfibonacci.app.parse_args")
@patch("pyfibonacci.app.ProcessPoolExecutor")
async def test_main_async_missing_n_argument(mock_process_pool_executor, mock_parse_args, capsys):
    """
    Vérifie que `main_async` affiche une erreur si -n est manquant
    sans --calibrate.
    """
    mock_args = MagicMock(calibrate=False, n=None)
    mock_parse_args.return_value = mock_args

    with pytest.raises(SystemExit) as e:
        await main_async()

    assert e.value.code == 1
    captured = capsys.readouterr()
    assert "ERREUR: L'argument '-n' est obligatoire" in captured.err


@pytest.mark.asyncio
@patch("pyfibonacci.app.parse_args")
@patch("pyfibonacci.app._run_single_algorithm", new_callable=AsyncMock)
@patch("pyfibonacci.app.ProcessPoolExecutor")
async def test_main_async_progress_bar_deadlock(
    mock_process_pool_executor, mock_run_single_algorithm, mock_parse_args, capsys
):
    """
    Vérifie que le programme ne se bloque pas (deadlock) lorsque la barre
    de progression est activée. C'est un test de régression pour le bug où
    le message "done" n'était jamais envoyé à la queue, bloquant le
    gestionnaire de progression.
    """
    mock_args = MagicMock(
        n=10,
        algo="fast",
        details=True,  # Active la barre de progression
        calibrate=False,
        timeout=1.0,
        threshold=1000
    )
    mock_parse_args.return_value = mock_args

    try:
        # On exécute avec un timeout court. Si le deadlock se produit,
        # ce test échouera par timeout.
        async with asyncio.timeout(2):
            await main_async()
    except TimeoutError:
        pytest.fail("Deadlock détecté: main_async a dépassé le timeout.")
