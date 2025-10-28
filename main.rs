// Fichier : src/main.rs
//
// Objectif : Calculer F(n) (nombre de Fibonacci) pour de très grands 'n'
//            en utilisant l'algorithme Fast Doubling optimisé.
//
// --- Dépendances requises dans Cargo.toml ---
// [dependencies]
// num-bigint = "0.4.5"
// num-traits = "0.2.19"
//
// --- Pour compiler et exécuter avec optimisation maximale ---
// 1. Enregistrez ce fichier dans `src/main.rs` d'un nouveau projet Cargo.
// 2. Assurez-vous que le Cargo.toml contient les dépendances ci-dessus.
// 3. Exécutez : cargo run --release -- <n>
//    Exemple :   cargo run --release -- 1000000
//
// L'option `--release` active les optimisations complètes du compilateur Rust,
// ce qui est crucial pour la performance des opérations sur `BigUint`.

use num_bigint::BigUint;
use num_traits::{Zero, One};
use std::env;
use std::time::Instant;

/// Calcule F(n) en utilisant l'algorithme itératif "Fast Doubling".
///
/// Complexité : O(log n) opérations arithmétiques sur des grands entiers.
///
/// L'algorithme est basé sur les identités matricielles ou, plus directement :
/// F(2k)   = F(k) * [2*F(k+1) - F(k)]
/// F(2k+1) = F(k)^2 + F(k+1)^2
///
/// Cette fonction implémente cela de manière itérative en parcourant
/// les bits de 'n' du plus significatif (MSB) au moins significatif (LSB).
///
/// @param n L'index (u128) du nombre de Fibonacci à calculer.
/// @return Le nombre F(n) sous forme de `BigUint`.
fn fibonacci_fast_doubling_iterative(n: u128) -> BigUint {
    // Cas de base F(0) = 0
    if n == 0 {
        return BigUint::zero();
    }

    // Trouve l'index du bit le plus significatif (MSB).
    // `n.leading_zeros()` compte le nombre de zéros non significatifs (à gauche).
    // Pour `u128`, l'index max est 127.
    // `msb_index` est la position du premier '1' en partant de la gauche (base 0).
    let msb_index = 127 - n.leading_zeros();

    // Initialise les états (a, b) = (F(0), F(1))
    // Nous allons "construire" F(n) bit par bit.
    // 'a' et 'b' sont mutables et représentent F(k) et F(k+1)
    // aux différentes étapes de l'itération.
    let mut a = BigUint::zero(); // Représente F(k)
    let mut b = BigUint::one();  // Représente F(k+1)

    // Itération du MSB (index `msb_index`) jusqu'au LSB (index 0).
    // `(0..=msb_index)` crée une plage, `.rev()` l'inverse.
    for i in (0..=msb_index).rev() {
        // --- Étape 1: Doubling (toujours exécutée) ---
        // À ce point, (a, b) = (F(k), F(k+1))
        // Nous calculons (F(2k), F(2k+1)) en utilisant les identités.

        // Note : L'utilisation de `&a` et `&b` évite les déplacements (moves)
        // et permet des emprunts (borrows) pour les opérations de BigUint,
        // ce qui est efficace.

        // c = F(2k) = F(k) * [2*F(k+1) - F(k)]
        let c = &a * (&b * 2u32 - &a);
        // d = F(2k+1) = F(k)^2 + F(k+1)^2
        let d = &a * &a + &b * &b;

        // Met à jour (a, b) pour représenter (F(2k), F(2k+1))
        // Notre 'k' effectif vient de doubler.
        a = c;
        b = d;

        // --- Étape 2: "Advance" (si le bit est '1') ---
        // `(n >> i) & 1` vérifie si le i-ème bit de 'n' est à 1.
        if (n >> i) & 1 == 1 {
            // Si le bit est 1, cela signifie que notre 'n' cible est impair
            // à cette étape (n = 2k + 1).
            //
            // Nous avons actuellement (a, b) = (F(2k), F(2k+1)).
            // Nous devons avancer d'un pas pour obtenir :
            // (F(2k+1), F(2k+2))
            //
            // F(2k+1) = b (notre 'b' actuel)
            // F(2k+2) = F(2k) + F(2k+1) = a + b (nos 'a' et 'b' actuels)

            // t = F(2k+2) = a + b
            let t = &a + &b;
            // a = F(2k+1) = b
            a = b;
            // b = F(2k+2) = t
            b = t;
            // Notre 'k' effectif est maintenant 2k + 1.
        }
    }

    // Après avoir traité tous les bits de 'n', 'a' contient F(n).
    a
}

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
    // L'affichage de nombres immenses (conversion en base 10) peut être
    // très long et polluer la console.
    // Nous affichons le nombre de chiffres, et seulement les 100
    // premiers et 100 derniers chiffres si le nombre est trop grand.

    let result_str = result.to_string();
    let len = result_str.len();
    println!("Nombre total de chiffres décimaux: {}", len);

    if len <= 200 {
        // Si le nombre est "petit", on l'affiche en entier.
        println!("Résultat: {}", result_str);
    } else {
        // Sinon, on affiche un aperçu pour confirmation.
        println!("Début: {}...", &result_str[..100]);
        println!("Fin:   ...{}", &result_str[len - 100..]);
    }
}
