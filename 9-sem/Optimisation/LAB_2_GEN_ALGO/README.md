# GA RSA Cipher Breaker

A modular Python implementation of a Genetic Algorithm for breaking RSA-encrypted text.

## Features

- **Modular architecture**: Separate modules for GA core, population, operators, and fitness evaluation
- **Flexible configuration**: Easily adjust GA parameters
- **Multiple operators**: Tournament/roulette selection, multiple crossover methods, various mutation strategies
- **Progress tracking**: Built-in history tracking and statistics
- **Cross-validation**: Included notebook for hyperparameter optimization

## Installation

No external dependencies required beyond Python standard library and the included `var/rsa_lib.py`.

For cross-validation notebook, install:
```bash
pip install numpy pandas matplotlib seaborn
```

## Project Structure

```
LAB_2_GEN_ALGO/
├── ga_rsa/                    # Main GA module
│   ├── __init__.py           # Package initialization
│   ├── ga.py                 # Core GA implementation
│   ├── population.py         # Population management
│   ├── operators.py          # Selection, crossover, mutation
│   ├── fitness.py            # Fitness evaluation
│   └── utils.py              # Utility functions
├── var/                       # Test data and RSA library
│   ├── rsa_lib.py            # RSA encryption/decryption
│   └── *_encrypted_text.txt  # Test cases
├── example_usage.py          # Usage example
├── cross_validation.ipynb    # Hyperparameter optimization
└── RSA_BREAK_TRY_1.ipynb    # Original implementation
```

## Quick Start

### Basic Usage

```python
from ga_rsa import GeneticAlgorithm
from ga_rsa.utils import load_test_case

# Load test case
test_case = load_test_case(8)

# Create GA instance
ga = GeneticAlgorithm(
    target_ciphertext=test_case['ciphertext'],
    text_length=test_case['length'],
    public_key=65537,
    n=33227,
    pop_size=100,
    mutation_rate=0.02,
    crossover_rate=0.8,
    tournament_size=3,
    elite_count=2
)

# Run evolution
best_individual, generations, error = ga.evolve(
    max_generations=20000,
    target_error=0.0,
    verbose=True
)

print(f"Deciphered text: {best_individual}")
```

### Advanced Usage with Custom Operators

```python
from ga_rsa import GeneticAlgorithm
from ga_rsa.operators import Crossover, Mutation

# Use two-point crossover
ga.crossover.two_point_crossover = Crossover.two_point_crossover

# Use custom mutation
ga.mutation.mutate = lambda x: Mutation.mutate_swap(ga.mutation, x)

# Run with callback
def callback(gen, ind, fit, err):
    if gen % 500 == 0:
        print(f"Generation {gen}: error={err:.4f}")
    return err < 0.01  # Stop early if error is small enough

best, gens, err = ga.evolve(callback=callback)
```

## Cross-Validation

The `cross_validation.ipynb` notebook performs hyperparameter optimization:

1. Tests multiple parameter combinations
2. Uses multiple test cases for validation
3. Evaluates convergence rates and generation counts
4. Visualizes parameter effects
5. Saves best parameters

Run the notebook to find optimal parameters for your specific problem.

## Module Documentation

### GeneticAlgorithm

Main class orchestrating the evolution process.

**Parameters:**
- `target_ciphertext`: List of encrypted integers to match
- `text_length`: Length of plaintext
- `public_key`: RSA public exponent (e)
- `n`: RSA modulus
- `alphabet`: Valid characters (default: letters, comma, space)
- `pop_size`: Population size (default: 100)
- `mutation_rate`: Per-character mutation probability (default: 0.02)
- `crossover_rate`: Crossover application probability (default: 0.8)
- `tournament_size`: Tournament selection size (default: 3)
- `elite_count`: Elites preserved per generation (default: 2)

**Methods:**
- `evolve()`: Run the evolution process
- `get_statistics()`: Get evolution statistics
- `evaluate_population()`: Evaluate all individuals

### Population

Manages the population of candidate solutions.

**Methods:**
- `__init__(size, text_length, alphabet)`: Create random population
- `from_individuals(individuals, alphabet)`: Create from existing individuals

### Selection

Tournament and roulette wheel selection operators.

### Crossover

Multiple crossover methods:
- `one_point_crossover()`: Single crossover point
- `two_point_crossover()`: Two crossover points
- `uniform_crossover()`: Position-wise swapping

### Mutation

Various mutation strategies:
- `mutate()`: Random character replacement
- `mutate_swap()`: Swap two positions
- `mutate_insert()`: Replace single position

### FitnessEvaluator

Evaluates fitness based on encryption error.

**Methods:**
- `error(candidate)`: Calculate mean squared error
- `fitness(candidate)`: Calculate fitness (1/(1+error))
- `is_perfect_match(candidate)`: Check if perfect match

## Algorithm Details

The GA uses:
1. **Initialization**: Random population of candidate plaintexts
2. **Fitness evaluation**: MSE between encrypted candidate and target
3. **Selection**: Tournament selection for parent choosing
4. **Crossover**: One-point crossover (configurable)
5. **Mutation**: Random character replacement per position
6. **Elitism**: Best individuals preserved each generation

## Tips for Optimization

1. **Population size**: Larger populations explore more but are slower
2. **Mutation rate**: Higher rates increase exploration but may disrupt good solutions
3. **Crossover rate**: Usually 0.7-0.9 works well
4. **Tournament size**: Larger values increase selection pressure
5. **Elite count**: 1-3 elites typically sufficient

Use the cross-validation notebook to find optimal parameters for your specific problem.

## Example Output

```
Loading test case...
Ciphertext length: 42

Starting evolution...
======================================================================
Gen     0 | Error: 234567890.123456 | Fitness: 0.000000 | Best: 'xKpQjMnBvCdEfGhIjK'...
Gen   100 | Error: 123456.789012 | Fitness: 0.000008 | Best: 'This is a secwet m'...
Gen   500 | Error: 1234.567890 | Fitness: 0.000810 | Best: 'This is a secret m'...
Gen  1000 | Error: 0.000000 | Fitness: 1.000000 | Best: 'This is a secret me'...
Converged at generation 1234

======================================================================
RESULTS:
======================================================================
Generations: 1234
Final error: 0.0000000000
Converged: True

Deciphered text:
  'This is a secret message for you to find'
```

## License

Educational use - part of Optimization course lab work.
