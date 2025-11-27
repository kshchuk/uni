"""
Utility functions for the GA RSA module
"""

import json
import pickle
from typing import Dict, Any, List
from pathlib import Path


def save_results(results: Dict[str, Any], filepath: str):
    """
    Save GA results to JSON file.
    
    Args:
        results: Dictionary with results
        filepath: Path to save file
    """
    # Convert non-serializable objects
    serializable_results = {}
    for key, value in results.items():
        if isinstance(value, (str, int, float, bool, list, dict)) or value is None:
            serializable_results[key] = value
        else:
            serializable_results[key] = str(value)
    
    with open(filepath, 'w') as f:
        json.dump(serializable_results, f, indent=2)


def load_results(filepath: str) -> Dict[str, Any]:
    """
    Load GA results from JSON file.
    
    Args:
        filepath: Path to results file
        
    Returns:
        Results dictionary
    """
    with open(filepath, 'r') as f:
        return json.load(f)


def save_history(history: List[Dict], filepath: str):
    """
    Save evolution history to file.
    
    Args:
        history: List of generation statistics
        filepath: Path to save file
    """
    with open(filepath, 'wb') as f:
        pickle.dump(history, f)


def load_history(filepath: str) -> List[Dict]:
    """
    Load evolution history from file.
    
    Args:
        filepath: Path to history file
        
    Returns:
        List of generation statistics
    """
    with open(filepath, 'rb') as f:
        return pickle.load(f)


def format_parameters(params: Dict[str, Any]) -> str:
    """
    Format parameters dictionary as readable string.
    
    Args:
        params: Parameters dictionary
        
    Returns:
        Formatted string
    """
    lines = ["GA Parameters:"]
    lines.append("=" * 40)
    for key, value in params.items():
        lines.append(f"  {key:20s}: {value}")
    return "\n".join(lines)


def parse_encrypted_file(filepath: str) -> List[int]:
    """
    Parse an encrypted text file.
    
    File format:
        Line 0: len of text: <number>
        Line 1: [encrypted array]
        Line 2: public key:<number>
        Line 3: n:<number>
    
    Args:
        filepath: Path to encrypted text file
        
    Returns:
        List of encrypted integers
    """
    with open(filepath, 'r') as f:
        lines = f.readlines()
        # Parse line 1 which contains the encrypted array
        ciphertext_line = lines[1].strip()
        return eval(ciphertext_line)


def load_test_case(test_id: int, var_dir: str = "var") -> Dict[str, Any]:
    """
    Load a test case from the var directory.
    
    Args:
        test_id: Test case number (1-8)
        var_dir: Path to var directory
        
    Returns:
        Dictionary with ciphertext and metadata
    """
    filepath = Path(var_dir) / f"{test_id}_encrypted_text.txt"
    ciphertext = parse_encrypted_file(str(filepath))
    
    return {
        'id': test_id,
        'ciphertext': ciphertext,
        'length': len(ciphertext),
        'filepath': str(filepath)
    }
