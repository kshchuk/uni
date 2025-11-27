"""
Genetic operators: Selection, Crossover, and Mutation
"""

import random
from typing import List, Tuple


class Selection:
    """Selection operators for choosing parents."""
    
    def __init__(self, tournament_size: int = 3):
        """
        Initialize selection operator.
        
        Args:
            tournament_size: Number of individuals in tournament
        """
        self.tournament_size = tournament_size
    
    def tournament_select(
        self, 
        population: List[str], 
        fitnesses: List[float]
    ) -> str:
        """
        Select an individual using tournament selection.
        
        Args:
            population: List of individuals
            fitnesses: Corresponding fitness values
            
        Returns:
            Selected individual
        """
        selected_idx = random.randrange(len(population))
        for _ in range(self.tournament_size - 1):
            i = random.randrange(len(population))
            if fitnesses[i] > fitnesses[selected_idx]:
                selected_idx = i
        return population[selected_idx]
    
    def roulette_wheel_select(
        self,
        population: List[str],
        fitnesses: List[float]
    ) -> str:
        """
        Select an individual using roulette wheel selection.
        
        Args:
            population: List of individuals
            fitnesses: Corresponding fitness values
            
        Returns:
            Selected individual
        """
        total_fitness = sum(fitnesses)
        if total_fitness == 0:
            return random.choice(population)
        
        selection_point = random.uniform(0, total_fitness)
        cumulative = 0
        for ind, fit in zip(population, fitnesses):
            cumulative += fit
            if cumulative >= selection_point:
                return ind
        return population[-1]


class Crossover:
    """Crossover operators for combining parents."""
    
    @staticmethod
    def one_point_crossover(parent1: str, parent2: str) -> Tuple[str, str]:
        """
        Perform one-point crossover.
        
        Args:
            parent1: First parent string
            parent2: Second parent string
            
        Returns:
            Tuple of two child strings
        """
        if len(parent1) != len(parent2):
            raise ValueError("Parents must have equal length")
        
        L = len(parent1)
        if L < 2:
            return parent1, parent2
        
        cut = random.randint(1, L - 1)
        child1 = parent1[:cut] + parent2[cut:]
        child2 = parent2[:cut] + parent1[cut:]
        return child1, child2
    
    @staticmethod
    def two_point_crossover(parent1: str, parent2: str) -> Tuple[str, str]:
        """
        Perform two-point crossover.
        
        Args:
            parent1: First parent string
            parent2: Second parent string
            
        Returns:
            Tuple of two child strings
        """
        if len(parent1) != len(parent2):
            raise ValueError("Parents must have equal length")
        
        L = len(parent1)
        if L < 3:
            return Crossover.one_point_crossover(parent1, parent2)
        
        cut1, cut2 = sorted(random.sample(range(1, L), 2))
        child1 = parent1[:cut1] + parent2[cut1:cut2] + parent1[cut2:]
        child2 = parent2[:cut1] + parent1[cut1:cut2] + parent2[cut2:]
        return child1, child2
    
    @staticmethod
    def uniform_crossover(
        parent1: str, 
        parent2: str, 
        swap_probability: float = 0.5
    ) -> Tuple[str, str]:
        """
        Perform uniform crossover.
        
        Args:
            parent1: First parent string
            parent2: Second parent string
            swap_probability: Probability of swapping each position
            
        Returns:
            Tuple of two child strings
        """
        if len(parent1) != len(parent2):
            raise ValueError("Parents must have equal length")
        
        child1_list = []
        child2_list = []
        
        for c1, c2 in zip(parent1, parent2):
            if random.random() < swap_probability:
                child1_list.append(c2)
                child2_list.append(c1)
            else:
                child1_list.append(c1)
                child2_list.append(c2)
        
        return "".join(child1_list), "".join(child2_list)


class Mutation:
    """Mutation operators for introducing variation."""
    
    def __init__(self, mutation_rate: float, alphabet: str):
        """
        Initialize mutation operator.
        
        Args:
            mutation_rate: Probability of mutating each character
            alphabet: Valid characters for mutation
        """
        self.mutation_rate = mutation_rate
        self.alphabet = alphabet
    
    def mutate(self, individual: str) -> str:
        """
        Apply random mutation to an individual.
        
        Args:
            individual: String to mutate
            
        Returns:
            Mutated string
        """
        individual_list = list(individual)
        for i in range(len(individual_list)):
            if random.random() < self.mutation_rate:
                individual_list[i] = random.choice(self.alphabet)
        return "".join(individual_list)
    
    def mutate_swap(self, individual: str) -> str:
        """
        Swap two random positions in the individual.
        
        Args:
            individual: String to mutate
            
        Returns:
            Mutated string
        """
        if len(individual) < 2:
            return individual
        
        individual_list = list(individual)
        i, j = random.sample(range(len(individual_list)), 2)
        individual_list[i], individual_list[j] = individual_list[j], individual_list[i]
        return "".join(individual_list)
    
    def mutate_insert(self, individual: str) -> str:
        """
        Insert a random character at a random position.
        
        Args:
            individual: String to mutate
            
        Returns:
            Mutated string (same length, replaces a character)
        """
        if len(individual) == 0:
            return individual
        
        individual_list = list(individual)
        i = random.randrange(len(individual_list))
        individual_list[i] = random.choice(self.alphabet)
        return "".join(individual_list)
