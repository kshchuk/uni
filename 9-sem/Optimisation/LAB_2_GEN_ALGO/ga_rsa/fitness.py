"""
Fitness evaluation for RSA cipher breaking
"""

from typing import List
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from var import rsa_lib


class FitnessEvaluator:
    """
    Evaluates fitness of candidate plaintexts based on encryption error.
    
    The fitness function measures how close the encryption of a candidate
    plaintext matches the target ciphertext.
    """
    
    def __init__(self, target_ciphertext: List[int], public_key: int, n: int):
        """
        Initialize the fitness evaluator.
        
        Args:
            target_ciphertext: The ciphertext to match
            public_key: RSA public exponent (e)
            n: RSA modulus
        """
        self.target_ciphertext = target_ciphertext
        self.public_key = public_key
        self.n = n
        self.target_length = len(target_ciphertext)
    
    def encrypt_candidate(self, plaintext: str) -> List[int]:
        """
        Encrypt a candidate plaintext.
        
        Args:
            plaintext: Candidate text to encrypt
            
        Returns:
            Encrypted ciphertext as list of integers
        """
        return rsa_lib.encrypt_text(plaintext, self.public_key, self.n)
    
    def error(self, candidate: str) -> float:
        """
        Calculate the mean squared error between candidate encryption
        and target ciphertext.
        
        Args:
            candidate: Candidate plaintext
            
        Returns:
            Mean squared error (P)
        """
        candidate_cipher = self.encrypt_candidate(candidate)
        
        # Use minimum length for safety
        L = min(len(candidate_cipher), self.target_length)
        
        squared_error = sum(
            (candidate_cipher[i] - self.target_ciphertext[i]) ** 2
            for i in range(L)
        )
        
        return squared_error / L
    
    def fitness(self, candidate: str) -> float:
        """
        Calculate fitness value for a candidate.
        
        Higher fitness is better. Fitness is inversely related to error.
        
        Args:
            candidate: Candidate plaintext
            
        Returns:
            Fitness value (0 to 1, where 1 is perfect match)
        """
        P = self.error(candidate)
        return 1.0 / (1.0 + P)
    
    def is_perfect_match(self, candidate: str, tolerance: float = 1e-10) -> bool:
        """
        Check if candidate is a perfect or near-perfect match.
        
        Args:
            candidate: Candidate plaintext
            tolerance: Error tolerance for perfect match
            
        Returns:
            True if error is within tolerance
        """
        return self.error(candidate) <= tolerance
