"""
Example: Using the GA RSA module to decipher encrypted text
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from ga_rsa import GeneticAlgorithm
from ga_rsa.utils import load_test_case


def main():
    """Main example function."""
    
    # Load a test case (variant 8)
    print("Loading test case...")
    test_case = load_test_case(8)
    
    print(f"Ciphertext length: {test_case['length']}")
    print(f"First 5 values: {test_case['ciphertext'][:5]}")
    
    # RSA parameters
    public_key = 65537
    n = 33227
    
    # Create GA instance with optimized parameters
    print("\nInitializing Genetic Algorithm...")
    ga = GeneticAlgorithm(
        target_ciphertext=test_case['ciphertext'],
        text_length=test_case['length'],
        public_key=public_key,
        n=n,
        pop_size=100,
        mutation_rate=0.02,
        crossover_rate=0.8,
        tournament_size=3,
        elite_count=2,
        random_seed=42  # For reproducibility
    )
    
    # Run evolution
    print("\nStarting evolution...")
    print("=" * 70)
    
    best_individual, generations, final_error = ga.evolve(
        max_generations=20000,
        target_error=0.0,
        verbose=True
    )
    
    # Print results
    print("\n" + "=" * 70)
    print("RESULTS:")
    print("=" * 70)
    print(f"Generations: {generations}")
    print(f"Final error: {final_error:.10f}")
    print(f"Converged: {final_error == 0.0}")
    print(f"\nDeciphered text:")
    print(f"  {repr(best_individual)}")
    
    # Get statistics
    stats = ga.get_statistics()
    print("\nStatistics:")
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    # Optionally save results
    from ga_rsa.utils import save_results
    save_results(stats, 'ga_results.json')
    print("\nResults saved to 'ga_results.json'")


if __name__ == "__main__":
    main()
