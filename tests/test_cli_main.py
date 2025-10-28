"""
Tests unitaires pour le module `pyfibonacci.cli.main`.
"""

import sys
from unittest.mock import patch, MagicMock

import pytest
from pyfibonacci.cli.main import main

@patch('pyfibonacci.cli.main.sys.set_int_max_str_digits')
@patch('pyfibonacci.cli.main.asyncio.run')
def test_main_success(mock_asyncio_run, mock_set_digits):
    """
    Vérifie que la fonction `main` appelle `sys.set_int_max_str_digits`
    et `asyncio.run` avec les bons arguments.
    """
    main()
    mock_set_digits.assert_called_once_with(0)
    mock_asyncio_run.assert_called_once()

@patch('pyfibonacci.cli.main.sys.set_int_max_str_digits')
@patch('pyfibonacci.cli.main.asyncio.run', side_effect=KeyboardInterrupt)
def test_main_keyboard_interrupt(mock_asyncio_run, mock_set_digits, capsys):
    """
    Vérifie que `main` gère correctement une `KeyboardInterrupt` et affiche
    le message approprié.
    """
    main()
    mock_set_digits.assert_called_once_with(0)
    mock_asyncio_run.assert_called_once()
    captured = capsys.readouterr()
    assert "\nProgramme interrompu par l'utilisateur." in captured.out
