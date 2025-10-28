//! Binaire principal pour l'interface en ligne de commande.
//!
//! Ce module gère l'analyse des arguments, l'appel à la bibliothèque `fib_rs`
//! pour le calcul, et l'affichage du résultat.
//!
//! Ce code est structuré comme un 'crate' Rust standard et peut être compilé
//! et exécuté avec Cargo.

use std::env;
use std::time::Instant;
use fib_rs::fibonacci_fast_doubling_iterative;

/// Point d'entrée principal de l'application.
fn main() {
    // Récupère les arguments de la ligne de commande
    let args: Vec<String> = env::args().collect();

    // S'attend à un argument exactement : le nombre 'n'
    if args.len() != 2 {
        eprintln!("Usage: cargo run --release -- <n>");
        eprintln!("Où <n> est l'index de Fibonacci à calculer (ex: 1000000).");
        std::process::exit(1);
    }

    // Tente de parser l'argument 'n' en u128
    let n: u128 = match args[1].parse() {
        Ok(num) => num,
        Err(_) => {
            eprintln!("Erreur : L'argument '{}' n'est pas un nombre u128 valide.", args[1]);
            std::process::exit(1);
        }
    };

    println!("Calcul de Fibonacci F({}) avec l'algorithme Fast Doubling (Itératif, Optimisé)...", n);

    // Mesure du temps d'exécution
    let start = Instant::now();
    let result = fibonacci_fast_doubling_iterative(n);
    let duration = start.elapsed();

    println!("Calcul terminé en {:?}", duration);

    // --- Affichage du résultat ---
    let result_str = result.to_string();
    let len = result_str.len();
    println!("Nombre total de chiffres décimaux: {}", len);

    if len <= 200 {
        println!("Résultat: {}", result_str);
    } else {
        println!("Début: {}...", &result_str[..100]);
        println!("Fin:   ...{}", &result_str[len - 100..]);
    }
}
