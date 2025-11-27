"""
Genetic Algorithm core implementation
"""

import random
from typing import List, Tuple, Optional, Callable
from .population import Population
from .operators import Selection, Crossover, Mutation
from .fitness import FitnessEvaluator


class GeneticAlgorithm:
    """
    Main Genetic Algorithm class for RSA cipher breaking.
    
    This class orchestrates the evolution process using selection, crossover,
    mutation, and elitism to find the plaintext that best matches the ciphertext.
    """
    
    def __init__(
        self,
        target_ciphertext: List[int],
        text_length: int,
        public_key: int,
        n: int,
        alphabet: str = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ, ",
        pop_size: int = 100,
        mutation_rate: float = 0.02,
        crossover_rate: float = 0.8,
        tournament_size: int = 3,
        elite_count: int = 2,
        random_seed: Optional[int] = None
    ):
        """
        Initialize the Genetic Algorithm.
        
        Args:
            target_ciphertext: The encrypted text to match (list of integers)
            text_length: Length of the plaintext
            public_key: RSA public key exponent (e)
            n: RSA modulus
            alphabet: Valid characters for the plaintext
            pop_size: Population size
            mutation_rate: Probability of mutation per character
            crossover_rate: Probability of applying crossover
            tournament_size: Number of individuals in tournament selection
            elite_count: Number of best individuals preserved each generation
            random_seed: Random seed for reproducibility
        """
        if random_seed is not None:
            random.seed(random_seed)
        
        self.target_ciphertext = target_ciphertext
        self.text_length = text_length
        self.public_key = public_key
        self.n = n
        self.alphabet = alphabet
        self.pop_size = pop_size
        self.mutation_rate = mutation_rate
        self.crossover_rate = crossover_rate
        self.tournament_size = tournament_size
        self.elite_count = elite_count
        
        # Initialize components
        self.fitness_evaluator = FitnessEvaluator(
            target_ciphertext, public_key, n
        )
        self.selection = Selection(tournament_size)
        self.crossover = Crossover()
        self.mutation = Mutation(mutation_rate, alphabet)
        
        # Initialize population
        self.population = Population(
            pop_size, text_length, alphabet
        )
        
        # Statistics
        self.generation = 0
        self.best_individual = None
        self.best_fitness = 0.0
        self.best_error = float('inf')
        self.history = []
    
    def evaluate_population(self) -> List[float]:
        """
        Evaluate fitness for all individuals in the population.
        
        Returns:
            List of fitness values
        """
        return [
            self.fitness_evaluator.fitness(ind)
            for ind in self.population.individuals
        ]
    
    def get_best_individual(self, fitnesses: List[float]) -> Tuple[str, float, float]:
        """
        Get the best individual from the current population.
        
        Args:
            fitnesses: List of fitness values for the population
            
        Returns:
            Tuple of (best_individual, best_fitness, best_error)
        """
        best_idx = max(range(len(fitnesses)), key=lambda i: fitnesses[i])
        best_ind = self.population.individuals[best_idx]
        best_fit = fitnesses[best_idx]
        best_err = self.fitness_evaluator.error(best_ind)
        return best_ind, best_fit, best_err
    
    def create_next_generation(self, fitnesses: List[float]) -> Population:
        """
        Create the next generation using selection, crossover, mutation, and elitism.
        
        Args:
            fitnesses: Fitness values for the current population
            
        Returns:
            New population
        """
        # Sort population by fitness
        pop_fit = list(zip(self.population.individuals, fitnesses))
        pop_fit.sort(key=lambda x: x[1], reverse=True)
        
        # Elitism: preserve best individuals
        new_individuals = [ind for ind, _ in pop_fit[:self.elite_count]]
        
        # Generate rest through evolution
        while len(new_individuals) < self.pop_size:
            # Selection
            parent1 = self.selection.tournament_select(
                self.population.individuals, fitnesses
            )
            parent2 = self.selection.tournament_select(
                self.population.individuals, fitnesses
            )
            
            # Crossover
            if random.random() < self.crossover_rate:
                child1, child2 = self.crossover.one_point_crossover(parent1, parent2)
            else:
                child1, child2 = parent1, parent2
            
            # Mutation
            child1 = self.mutation.mutate(child1)
            child2 = self.mutation.mutate(child2)
            
            # Add to new population
            new_individuals.append(child1)
            if len(new_individuals) < self.pop_size:
                new_individuals.append(child2)
        
        return Population.from_individuals(new_individuals, self.alphabet)
    
    def evolve(
        self,
        max_generations: int = 20000,
        target_error: float = 0.0,
        callback: Optional[Callable[[int, str, float, float], bool]] = None,
        verbose: bool = True
    ) -> Tuple[str, int, float]:
        """
        Run the genetic algorithm evolution.
        
        Args:
            max_generations: Maximum number of generations
            target_error: Stop if error reaches this threshold
            callback: Optional callback function(generation, best_ind, best_fit, best_err)
                     that returns True to stop evolution
            verbose: Print progress
            
        Returns:
            Tuple of (best_individual, generations, final_error)
        """
        for self.generation in range(max_generations):
            # Evaluate population
            fitnesses = self.evaluate_population()
            
            # Get best individual
            best_ind, best_fit, best_err = self.get_best_individual(fitnesses)
            
            # Update statistics
            if best_fit > self.best_fitness:
                self.best_individual = best_ind
                self.best_fitness = best_fit
                self.best_error = best_err
            
            # Store history
            self.history.append({
                'generation': self.generation,
                'best_error': best_err,
                'best_fitness': best_fit,
                'avg_fitness': sum(fitnesses) / len(fitnesses),
                'best_individual': best_ind
            })
            
            # Progress output
            if verbose and (self.generation % 100 == 0 or best_err <= target_error):
                print(f"Gen {self.generation:5d} | Error: {best_err:.6f} | "
                      f"Fitness: {best_fit:.6f} | Best: {repr(best_ind[:20])}...")
            
            # Callback
            if callback and callback(self.generation, best_ind, best_fit, best_err):
                if verbose:
                    print("Stopped by callback")
                break
            
            # Check convergence
            if best_err <= target_error:
                if verbose:
                    print(f"Converged at generation {self.generation}")
                    print(f"Best individual: {repr(best_ind)}")
                break
            
            # Create next generation
            self.population = self.create_next_generation(fitnesses)
        
        return self.best_individual, self.generation, self.best_error
    
    def get_statistics(self) -> dict:
        """
        Get statistics about the evolution process.
        
        Returns:
            Dictionary with evolution statistics
        """
        return {
            'generations': self.generation,
            'best_individual': self.best_individual,
            'best_error': self.best_error,
            'best_fitness': self.best_fitness,
            'final_population_size': len(self.population.individuals),
            'converged': self.best_error == 0.0
        }
