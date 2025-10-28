"""
Module principal d'orchestration de l'application PyFibonacci.

Ce module contient la logique de haut niveau pour l'application en ligne de
commande PyFibonacci. Il gère l'analyse des arguments, l'initialisation des
composants (comme le pool de processus), et l'orchestration de l'exécution
des algorithmes de calcul de la suite de Fibonacci.
"""

import asyncio
import sys
from typing import Callable, Coroutine, Any, Awaitable, Dict
from concurrent.futures import ProcessPoolExecutor

from .cli.args import parse_args
from .cli.progress import progress_bar_manager
from .core.algorithms import fib_iterative, fib_matrix, fib_fast_doubling
from .core.context import CalculationContext
from .calibrate import run_calibration

# Le registre des algorithmes disponibles.
# Il mappe les noms de la CLI aux fonctions (asynchrones ou synchrones).
ALGORITHM_REGISTRY: Dict[str, Callable[..., Awaitable[int] | int]] = {
    "iterative": fib_iterative,
    "matrix": fib_matrix,
    "fast": fib_fast_doubling,
}


async def _run_cpu_bound_task(func: Callable[..., Any], *args: Any) -> Any:
    """Exécute une fonction bloquante (CPU-bound) dans un `ProcessPoolExecutor`.

    Cette fonction est essentielle pour ne pas bloquer la boucle d'événements
    `asyncio` lorsqu'une tâche intensive en calcul (comme `fib_iterative`)
    doit être exécutée.

    Args:
        func (Callable[..., Any]): La fonction synchrone et bloquante à exécuter.
        *args (Any): Les arguments positionnels à passer à `func`.

    Returns:
        Any: Le résultat retourné par `func`.
    """
    loop = asyncio.get_running_loop()
    # Le 'None' en premier argument utilise le ThreadPoolExecutor par défaut.
    return await loop.run_in_executor(None, func, *args)


async def _run_single_algorithm(
    context: CalculationContext, n: int, algo_name: str, timeout: float
) -> None:
    """Exécute un algorithme de Fibonacci et gère son cycle de vie.

    Cette fonction prend en charge l'exécution d'un algorithme, qu'il soit
    synchrone ou asynchrone, en appliquant un timeout et en gérant les
    exceptions potentielles. Le résultat est affiché sur la sortie standard.

    Args:
        context (CalculationContext): Le contexte de calcul contenant le pool
            de processus et la queue pour la barre de progression.
        n (int): L'indice de la suite de Fibonacci à calculer.
        algo_name (str): Le nom de l'algorithme à utiliser (clé de `ALGORITHM_REGISTRY`).
        timeout (float): Le temps maximum en secondes alloué pour l'exécution.
    """
    algo_func = ALGORITHM_REGISTRY[algo_name]
    print(f"Calcul de F({n}) en utilisant l'algorithme '{algo_name}'...")

    try:
        async with asyncio.timeout(timeout):
            if asyncio.iscoroutinefunction(algo_func):
                result = await algo_func(context, n)
            else:
                result = await _run_cpu_bound_task(algo_func, n)

            print(f"Résultat ({algo_name}): {result}")
    except TimeoutError:
        print(
            f"ERREUR: L'algorithme '{algo_name}' a dépassé le timeout de {timeout}s.",
            file=sys.stderr,
        )
    except Exception as e:
        print(
            f"ERREUR inattendue avec l'algorithme '{algo_name}': {e}", file=sys.stderr
        )


async def _run_all_algorithms(
    context: CalculationContext, n: int, timeout: float
) -> None:
    """Exécute tous les algorithmes de Fibonacci enregistrés en parallèle.

    Utilise un `asyncio.TaskGroup` pour lancer et gérer l'exécution
    concurrente de tous les algorithmes. Chaque algorithme est encapsulé dans
    une tâche distincte avec son propre timeout.

    Args:
        context (CalculationContext): Le contexte de calcul.
        n (int): L'indice de la suite de Fibonacci à calculer.
        timeout (float): Le timeout applicable à chaque algorithme individuellement.
    """
    print(f"Calcul de F({n}) en utilisant tous les algorithmes en parallèle...")

    async def _task_wrapper(name: str, func: Callable) -> None:
        """Encapsule un algorithme pour gestion d'erreurs et de timeout."""
        try:
            async with asyncio.timeout(timeout):
                if asyncio.iscoroutinefunction(func):
                    await func(context, n)
                else:
                    await _run_cpu_bound_task(func, n)
                print(f"  - Résultat ({name}): Calcul terminé.")
        except TimeoutError:
            print(f"  - Résultat ({name}): TIMEOUT ({timeout}s)", file=sys.stderr)
        except Exception as e:
            print(f"  - Résultat ({name}): ERREUR ({e})", file=sys.stderr)

    async with asyncio.TaskGroup() as tg:
        for name, func in ALGORITHM_REGISTRY.items():
            tg.create_task(_task_wrapper(name, func))


async def _run_single_algorithm_with_progress_shutdown(
    context: CalculationContext, n: int, algo_name: str, timeout: float
) -> None:
    """Exécute un algorithme et garantit la terminaison de la barre de progression.

    Cet enrobeur s'assure que le message de fin (`"done"`) est envoyé à la
    `progress_queue`, même en cas d'erreur ou d'annulation de l'algorithme.
    Ceci est crucial pour que la tâche de la barre de progression ne reste
    pas en attente indéfiniment.

    Args:
        context (CalculationContext): Le contexte de calcul.
        n (int): L'indice de la suite de Fibonacci à calculer.
        algo_name (str): Le nom de l'algorithme à exécuter.
        timeout (float): Le timeout pour l'exécution.
    """
    try:
        await _run_single_algorithm(context, n, algo_name, timeout)
    finally:
        if context.progress_queue:
            await context.progress_queue.put("done")


async def main_async() -> None:
    """Point d'entrée principal et orchestrateur de l'application asynchrone.

    Cette fonction orchestre le flux de l'application :
    1.  Analyse les arguments de la ligne de commande.
    2.  Initialise le `ProcessPoolExecutor` pour les calculs CPU-bound.
    3.  Exécute le mode de calibration si l'option `--calibrate` est passée.
    4.  Crée le `CalculationContext` partagé.
    5.  Lance le ou les algorithmes de Fibonacci.
    6.  Gère la barre de progression si l'option `--details` est activée.
    """
    args = parse_args()

    # Le 'with' s'assure que le pool de processus est correctement fermé à la fin.
    with ProcessPoolExecutor() as executor:
        if args.calibrate:
            await run_calibration(executor)
            return

        if args.n is None:
            print(
                "ERREUR: L'argument '-n' est obligatoire sauf si --calibrate est utilisé.",
                file=sys.stderr,
            )
            sys.exit(1)

        progress_queue = asyncio.Queue() if args.details else None

        context = CalculationContext(
            threshold=args.threshold,
            executor=executor,
            progress_queue=progress_queue,
        )

        if args.algo == "all":
            await _run_all_algorithms(context, args.n, args.timeout)
        else:
            # Si la barre de progression est activée, on la lance en parallèle du calcul.
            if progress_queue and args.algo in ["fast", "matrix"]:
                total_steps = args.n.bit_length()
                async with asyncio.TaskGroup() as tg:
                    tg.create_task(
                        progress_bar_manager(
                            progress_queue, total_steps, f"Algo: {args.algo}"
                        )
                    )
                    # On utilise le nouveau wrapper ici
                    tg.create_task(
                        _run_single_algorithm_with_progress_shutdown(
                            context, args.n, args.algo, args.timeout
                        )
                    )
            else:
                await _run_single_algorithm(context, args.n, args.algo, args.timeout)
