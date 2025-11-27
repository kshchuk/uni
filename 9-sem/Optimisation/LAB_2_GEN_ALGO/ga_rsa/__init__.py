"""
Genetic Algorithm for RSA Cipher Breaking

A modular implementation of a genetic algorithm designed to decipher RSA-encrypted text
by evolving candidate plaintexts that minimize the encryption error.
"""

__version__ = "1.0.0"
__author__ = "GA RSA Breaker"

from .ga import GeneticAlgorithm
from .population import Population
from .operators import Crossover, Mutation, Selection
from .fitness import FitnessEvaluator

__all__ = [
    'GeneticAlgorithm',
    'Population',
    'Crossover',
    'Mutation',
    'Selection',
    'FitnessEvaluator'
]
