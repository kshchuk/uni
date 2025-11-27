"""
Population management for the genetic algorithm
"""

import random
from typing import List


class Population:
    """
    Manages a population of candidate solutions (individuals).
    
    Each individual is a string representing a potential plaintext.
    """
    
    def __init__(self, size: int, text_length: int, alphabet: str):
        """
        Initialize a random population.
        
        Args:
            size: Number of individuals in the population
            text_length: Length of each individual (plaintext length)
            alphabet: Valid characters for individuals
        """
        self.size = size
        self.text_length = text_length
        self.alphabet = alphabet
        self.individuals = self._initialize_random()
    
    def _initialize_random(self) -> List[str]:
        """Generate random individuals."""
        return [self._random_individual() for _ in range(self.size)]
    
    def _random_individual(self) -> str:
        """Generate a single random individual."""
        return "".join(random.choice(self.alphabet) for _ in range(self.text_length))
    
    @classmethod
    def from_individuals(cls, individuals: List[str], alphabet: str) -> 'Population':
        """
        Create a population from an existing list of individuals.
        
        Args:
            individuals: List of individuals (strings)
            alphabet: Valid characters
            
        Returns:
            Population instance
        """
        pop = cls.__new__(cls)
        pop.individuals = individuals
        pop.size = len(individuals)
        pop.text_length = len(individuals[0]) if individuals else 0
        pop.alphabet = alphabet
        return pop
    
    def __len__(self) -> int:
        """Return population size."""
        return len(self.individuals)
    
    def __getitem__(self, idx: int) -> str:
        """Get individual at index."""
        return self.individuals[idx]
    
    def __iter__(self):
        """Iterate over individuals."""
        return iter(self.individuals)
