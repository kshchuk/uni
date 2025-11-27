"""
Test suite for ga_rsa module
"""

import unittest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from ga_rsa import GeneticAlgorithm, Population, Crossover, Mutation, Selection
from ga_rsa.fitness import FitnessEvaluator


class TestPopulation(unittest.TestCase):
    """Test Population class."""
    
    def setUp(self):
        self.alphabet = "abc"
        self.size = 10
        self.length = 5
    
    def test_initialization(self):
        """Test population initialization."""
        pop = Population(self.size, self.length, self.alphabet)
        self.assertEqual(len(pop), self.size)
        self.assertEqual(len(pop[0]), self.length)
        for ind in pop:
            self.assertTrue(all(c in self.alphabet for c in ind))
    
    def test_from_individuals(self):
        """Test creating population from existing individuals."""
        individuals = ["abc", "bca", "cab"]
        pop = Population.from_individuals(individuals, self.alphabet)
        self.assertEqual(len(pop), 3)
        self.assertEqual(pop[0], "abc")


class TestOperators(unittest.TestCase):
    """Test genetic operators."""
    
    def test_one_point_crossover(self):
        """Test one-point crossover."""
        parent1 = "aaaaa"
        parent2 = "bbbbb"
        child1, child2 = Crossover.one_point_crossover(parent1, parent2)
        
        # Check lengths
        self.assertEqual(len(child1), len(parent1))
        self.assertEqual(len(child2), len(parent2))
        
        # Children should be different from parents (usually)
        self.assertTrue(child1 != parent1 or child2 != parent2)
    
    def test_two_point_crossover(self):
        """Test two-point crossover."""
        parent1 = "aaaaaaa"
        parent2 = "bbbbbbb"
        child1, child2 = Crossover.two_point_crossover(parent1, parent2)
        
        self.assertEqual(len(child1), len(parent1))
        self.assertEqual(len(child2), len(parent2))
    
    def test_mutation(self):
        """Test mutation operator."""
        alphabet = "abc"
        mutation = Mutation(mutation_rate=1.0, alphabet=alphabet)  # 100% mutation
        
        individual = "aaa"
        mutated = mutation.mutate(individual)
        
        # Length should be preserved
        self.assertEqual(len(mutated), len(individual))
        
        # Characters should be from alphabet
        self.assertTrue(all(c in alphabet for c in mutated))
    
    def test_tournament_selection(self):
        """Test tournament selection."""
        selection = Selection(tournament_size=3)
        population = ["aaa", "bbb", "ccc"]
        fitnesses = [0.5, 0.8, 0.3]
        
        # Run selection multiple times
        selected = [selection.tournament_select(population, fitnesses) 
                   for _ in range(10)]
        
        # Should select individuals from population
        self.assertTrue(all(ind in population for ind in selected))


class TestFitness(unittest.TestCase):
    """Test fitness evaluation."""
    
    def test_fitness_evaluator(self):
        """Test fitness evaluator."""
        target = [100, 200, 300]
        evaluator = FitnessEvaluator(target, public_key=65537, n=33227)
        
        # Test with some candidate
        candidate = "abc"
        fitness_value = evaluator.fitness(candidate)
        error_value = evaluator.error(candidate)
        
        # Fitness should be positive
        self.assertGreater(fitness_value, 0)
        
        # Error should be non-negative
        self.assertGreaterEqual(error_value, 0)
        
        # Fitness and error should be related
        self.assertAlmostEqual(fitness_value, 1.0 / (1.0 + error_value))


class TestGeneticAlgorithm(unittest.TestCase):
    """Test main GA class."""
    
    def test_initialization(self):
        """Test GA initialization."""
        ga = GeneticAlgorithm(
            target_ciphertext=[100, 200],
            text_length=2,
            public_key=65537,
            n=33227,
            pop_size=10
        )
        
        self.assertEqual(len(ga.population), 10)
        self.assertEqual(ga.generation, 0)
    
    def test_evolution_runs(self):
        """Test that evolution runs without errors."""
        ga = GeneticAlgorithm(
            target_ciphertext=[100, 200],
            text_length=2,
            public_key=65537,
            n=33227,
            pop_size=5
        )
        
        # Run for just a few generations
        best, generations, error = ga.evolve(
            max_generations=5,
            verbose=False
        )
        
        self.assertIsNotNone(best)
        self.assertGreaterEqual(generations, 0)
        self.assertGreaterEqual(error, 0)
    
    def test_get_statistics(self):
        """Test statistics retrieval."""
        ga = GeneticAlgorithm(
            target_ciphertext=[100, 200],
            text_length=2,
            public_key=65537,
            n=33227
        )
        
        ga.evolve(max_generations=2, verbose=False)
        stats = ga.get_statistics()
        
        self.assertIn('generations', stats)
        self.assertIn('best_individual', stats)
        self.assertIn('best_error', stats)


def run_tests():
    """Run all tests."""
    unittest.main(argv=[''], exit=False, verbosity=2)


if __name__ == '__main__':
    run_tests()
