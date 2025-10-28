//! Bibliothèque principale pour le calcul de la suite de Fibonacci.
//!
//! Ce module contient la logique métier principale, notamment l'implémentation
//! de l'algorithme "Fast Doubling" pour le calcul de F(n).
//!
//! Ce code est structuré comme un 'crate' Rust standard et peut être utilisé
//! comme dépendance par d'autres projets Rust.

use num_bigint::BigUint;
use num_traits::{Zero, One};

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
/// Le choix de `u128` pour `n` permet de gérer une très large plage d'indices
/// (jusqu'à 2^128 - 1), bien au-delà de ce que les types 64-bits standards
/// permettent, tout en restant un type primitif rapide.
///
/// @param n L'index (u128) du nombre de Fibonacci à calculer.
/// @return Le nombre F(n) sous forme de `BigUint`, capable de stocker des
///         nombres de taille arbitraire.
pub fn fibonacci_fast_doubling_iterative(n: u128) -> BigUint {
    // Cas de base trivial F(0) = 0.
    if n == 0 {
        return BigUint::zero();
    }

    // Trouve l'index du bit le plus significatif (MSB).
    let msb_index = 127 - n.leading_zeros();

    // Initialise les états (a, b) = (F(0), F(1))
    let mut a = BigUint::zero(); // Représente F(k)
    let mut b = BigUint::one();  // Représente F(k+1)

    // Itération du MSB (index `msb_index`) jusqu'au LSB (index 0).
    for i in (0..=msb_index).rev() {
        // --- Étape 1: Doubling (toujours exécutée) ---
        let c = &a * (&b * 2u32 - &a);
        let d = &a * &a + &b * &b;
        a = c;
        b = d;

        // --- Étape 2: "Advance" (si le bit est '1') ---
        if (n >> i) & 1 == 1 {
            let t = &a + &b;
            a = b;
            b = t;
        }
    }
    a
}
