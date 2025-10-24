"""
Module principal d'orchestration de l'application PyFibonacci.
"""

import asyncio
import sys
from typing import Callable, Dict, Coroutine, Any, Awaitable
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
    """
    Exécute une fonction bloquante (CPU-bound) dans un exécuteur de thread
    pour ne pas bloquer la boucle d'événements asyncio.
    """
    loop = asyncio.get_running_loop()
    # Le 'None' en premier argument utilise le ThreadPoolExecutor par défaut.
    return await loop.run_in_executor(None, func, *args)

async def _run_single_algorithm(context: CalculationContext, n: int, algo_name: str, timeout: float):
    """Exécute un seul algorithme de Fibonacci avec un timeout."""
    algo_func = ALGORITHM_REGISTRY[algo_name]
    print(f"Calcul de F({n}) en utilisant l'algorithme '{algo_name}'...")

    try:
        async with asyncio.timeout(timeout):
            # Les algorithmes asynchrones (matrix, fast) sont appelés directement.
            # L'algorithme synchrone (iterative) est enveloppé.
            if asyncio.iscoroutinefunction(algo_func):
                result = await algo_func(context, n)
            else:
                result = await _run_cpu_bound_task(algo_func, n)

            print(f"Résultat ({algo_name}): {result}")
    except TimeoutError:
        print(f"ERREUR: L'algorithme '{algo_name}' a dépassé le timeout de {timeout}s.", file=sys.stderr)
    except Exception as e:
        print(f"ERREUR inattendue avec l'algorithme '{algo_name}': {e}", file=sys.stderr)

async def _run_all_algorithms(context: CalculationContext, n: int, timeout: float):
    """Exécute tous les algorithmes disponibles en parallèle en utilisant un TaskGroup."""
    print(f"Calcul de F({n}) en utilisant tous les algorithmes en parallèle...")

    async def _task_wrapper(name: str, func: Callable) -> None:
        """Enveloppe l'exécution d'un algo pour gérer le timeout et le type d'appel."""
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
):
    """
    Wrapper pour exécuter un algorithme et s'assurer que le signal 'done'
    est envoyé à la barre de progression à la fin du calcul.
    """
    try:
        await _run_single_algorithm(context, n, algo_name, timeout)
    finally:
        if context.progress_queue:
            await context.progress_queue.put("done")


async def main_async():
    """
    Fonction principale asynchrone qui orchestre l'application.
    """
    args = parse_args()

    # Le 'with' s'assure que le pool de processus est correctement fermé à la fin.
    with ProcessPoolExecutor() as executor:
        if args.calibrate:
            await run_calibration(executor)
            return

        if args.n is None:
            print("ERREUR: L'argument '-n' est obligatoire sauf si --calibrate est utilisé.", file=sys.stderr)
            sys.exit(1)

        progress_queue = asyncio.Queue() if args.details else None

        context = CalculationContext(
            threshold=args.threshold,
            executor=executor,
            progress_queue=progress_queue
        )

        if args.algo == "all":
            await _run_all_algorithms(context, args.n, args.timeout)
        else:
            # Si la barre de progression est activée, on la lance en parallèle du calcul.
            if progress_queue and args.algo in ["fast", "matrix"]:
                total_steps = args.n.bit_length()
                async with asyncio.TaskGroup() as tg:
                    tg.create_task(progress_bar_manager(progress_queue, total_steps, f"Algo: {args.algo}"))
                    # On utilise le nouveau wrapper ici
                    tg.create_task(_run_single_algorithm_with_progress_shutdown(context, args.n, args.algo, args.timeout))
            else:
                await _run_single_algorithm(context, args.n, args.algo, args.timeout)
