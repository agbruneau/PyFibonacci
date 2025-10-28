"""
Tests unitaires pour le module `pyfibonacci.cli.args`.
"""

import sys
from unittest.mock import patch

import pytest
from pyfibonacci.cli.args import parse_args

@pytest.fixture
def setup_sys_argv():
    """
    Fixture pour mocker `sys.argv` avant chaque test.
    Ceci est nécessaire pour isoler les tests de la ligne de commande réelle.
    """
    original_argv = sys.argv
    yield
    sys.argv = original_argv

def test_parse_args_defaults(setup_sys_argv):
    """
    Vérifie que les valeurs par défaut sont correctement définies lorsque
    seul l'argument `-n` est fourni.
    """
    with patch.object(sys, 'argv', ['pyfibonacci', '-n', '10']):
        args = parse_args()
        assert args.n == 10
        assert args.algo == "fast"
        assert args.timeout == 10.0
        assert args.threshold == 10000
        assert not args.details
        assert not args.calibrate

def test_parse_args_all_options(setup_sys_argv):
    """
    Vérifie que tous les arguments fournis sont correctement interprétés.
    """
    with patch.object(sys, 'argv', [
        'pyfibonacci',
        '-n', '100',
        '--algo', 'matrix',
        '--timeout', '5.5',
        '--threshold', '500',
        '--details',
    ]):
        args = parse_args()
        assert args.n == 100
        assert args.algo == "matrix"
        assert args.timeout == 5.5
        assert args.threshold == 500
        assert args.details

def test_parse_args_calibrate(setup_sys_argv):
    """
    Vérifie que l'option `--calibrate` est correctement gérée, même sans `-n`.
    """
    with patch.object(sys, 'argv', ['pyfibonacci', '--calibrate']):
        args = parse_args()
        assert args.calibrate
        assert args.n is None  # n n'est pas requis avec --calibrate

def test_parse_args_invalid_choice(setup_sys_argv):
    """
    Vérifie qu'un choix invalide pour `--algo` lève une erreur.
    """
    with patch.object(sys, 'argv', ['pyfibonacci', '-n', '10', '--algo', 'invalid']):
        with pytest.raises(SystemExit):
            parse_args()
