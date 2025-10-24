"""
Tests pour le module de calibration.
"""
from unittest.mock import AsyncMock, MagicMock, patch
import pytest
from pyfibonacci.calibrate import (_measure_standard_multiply, _measure_parallel_multiply, run_calibration)

@pytest.mark.asyncio
@patch("time.perf_counter", side_effect=[1.0, 2.5])
async def test_measure_standard_multiply(mock_perf_counter):
    """
    Vérifie que _measure_standard_multiply mesure correctement le temps.
    """
    duration = await _measure_standard_multiply(size_in_bits=100)
    assert duration == 1.5


@pytest.mark.asyncio
@patch("asyncio.get_running_loop")
@patch("time.perf_counter", side_effect=[1.0, 3.0])
async def test_measure_parallel_multiply(mock_perf_counter, mock_get_loop):
    """
    Vérifie que _measure_parallel_multiply mesure correctement le temps
    d'exécution parallèle.
    """
    mock_executor = MagicMock()
    # On simule l'exécution dans l'exécuteur.
    mock_get_loop.return_value.run_in_executor = AsyncMock()

    duration = await _measure_parallel_multiply(mock_executor, size_in_bits=100)

    assert duration == 2.0
    mock_get_loop.return_value.run_in_executor.assert_called_once()


@pytest.mark.asyncio
@patch("pyfibonacci.calibrate._measure_standard_multiply", new_callable=AsyncMock)
@patch("pyfibonacci.calibrate._measure_parallel_multiply", new_callable=AsyncMock)
async def test_run_calibration_finds_crossover(mock_measure_parallel, mock_measure_standard, capsys):
    """
    Vérifie que run_calibration identifie correctement le point de croisement
    où le calcul parallèle devient plus rapide.
    """
    mock_executor = MagicMock()

    # On configure les temps de retour pour simuler le croisement.
    # Pour 10000 bits, standard est plus rapide.
    # Pour 20000 bits, parallèle est plus rapide.
    mock_measure_standard.side_effect = [0.1, 0.1, 0.1, 0.5, 0.5, 0.5]  # 3 passes par taille
    mock_measure_parallel.side_effect = [0.8, 0.8, 0.8, 0.4, 0.4, 0.4]

    await run_calibration(mock_executor)

    captured = capsys.readouterr()
    # On vérifie que la sortie indique le bon seuil.
    assert "Seuil optimal approximatif trouvé autour de 20000 bits" in captured.out
    # On vérifie que la calibration s'est arrêtée après avoir trouvé le seuil.
    assert "50000" not in captured.out


@pytest.mark.asyncio
@patch("pyfibonacci.calibrate._measure_standard_multiply", AsyncMock(return_value=0.1))
@patch("pyfibonacci.calibrate._measure_parallel_multiply", AsyncMock(return_value=0.5))
async def test_run_calibration_no_crossover(capsys):
    """
    Vérifie que run_calibration gère le cas où aucun point de croisement
    n'est trouvé dans la plage testée.
    """
    mock_executor = MagicMock()
    await run_calibration(mock_executor)

    captured = capsys.readouterr()
    assert "Aucun seuil optimal trouvé" in captured.out
