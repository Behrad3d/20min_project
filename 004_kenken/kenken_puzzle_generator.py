import random
from itertools import permutations

class KenKenGenerator:
    def __init__(self, size):
        self.size = size
        self.grid = self.generate_latin_square()
        self.cages = self.create_cages()

    def generate_latin_square(self):
        """
        Generate an NxN Latin square using a backtracking approach.
        """
        size = self.size
        grid = [[0] * size for _ in range(size)]
        
        def is_valid(num, row, col):
            """ Check if num is valid in the current row and column. """
            return num not in grid[row] and all(grid[i][col] != num for i in range(row))
        
        def solve(row=0, col=0):
            """ Backtracking approach to construct the Latin square. """
            if row == size:
                return True  # Successfully filled the grid
            next_row, next_col = (row, col + 1) if col + 1 < size else (row + 1, 0)
            
            nums = list(range(1, size + 1))
            random.shuffle(nums)  # Shuffle for random variations
            
            for num in nums:
                if is_valid(num, row, col):
                    grid[row][col] = num
                    if solve(next_row, next_col):
                        return True
                    grid[row][col] = 0  # Backtrack
            
            return False
        
        solve()
        return grid

    def is_valid_latin_square(self, grid):
        """Check if the generated grid is a valid Latin square."""
        size = self.size
        for col in range(size):
            column_values = {grid[row][col] for row in range(size)}
            if len(column_values) != size:
                return False
        return True

    def create_cages(self):
        """
        Divide the grid into cages with operations (+, -, ×, ÷).
        """
        size = self.size
        cells = [(r, c) for r in range(size) for c in range(size)]
        random.shuffle(cells)
        cages = []
        
        while cells:
            cage_size = random.choice([1, 2, 3]) if len(cells) > 3 else len(cells)
            cage_cells = [cells.pop() for _ in range(cage_size)]
            
            numbers = [self.grid[r][c] for r, c in cage_cells]
            operation, target = self.assign_operation(numbers)
            
            cages.append({"cells": cage_cells, "operation": operation, "target": target})
        
        return cages

    def assign_operation(self, numbers):
        """
        Assign an operation and target based on cage numbers.
        """
        if len(numbers) == 1:
            return None, numbers[0]
        
        operations = {
            '+': sum(numbers),
            '-': abs(numbers[0] - numbers[1]) if len(numbers) == 2 else None,
            '*': self.multiply(numbers),
            '÷': numbers[0] // numbers[1] if len(numbers) == 2 and numbers[0] % numbers[1] == 0 else None
        }
        
        valid_operations = [(op, res) for op, res in operations.items() if res is not None]
        return random.choice(valid_operations)
    
    def multiply(self, numbers):
        result = 1
        for num in numbers:
            result *= num
        return result

    def get_puzzle(self):
        """
        Return the generated puzzle with grid and cages.
        """
        return {"grid": self.grid, "cages": self.cages}

if __name__ == "__main__":
    size = random.randint(6, 9)  # Choose a random size between 6x6 and 9x9
    generator = KenKenGenerator(size)
    puzzle = generator.get_puzzle()
    
    print("Generated KenKen Puzzle:")
    for row in puzzle["grid"]:
        print(row)
    print("\nCages:")
    for cage in puzzle["cages"]:
        print(cage)
