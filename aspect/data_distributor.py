"""
Data Distributor - Algorithm Reporting System
Distributes computation data and reports algorithm usage to terminal
"""

from datetime import datetime, timezone
from typing import List, Tuple
from enum import Enum


class AlgorithmType(Enum):
    """Available algorithm types"""
    COMPUTE_DIFFERENCE = "COMPUTE_DIFFERENCE"
    COMPUTE_SUM = "COMPUTE_SUM"
    COMPUTE_PRODUCT = "COMPUTE_PRODUCT"
    COMPUTE_DIVISION = "COMPUTE_DIVISION"


class DataPackage:
    """Represents a data package for distribution"""
    
    def __init__(self, value_a: float, value_b: float, algorithm: AlgorithmType):
        self.value_a = value_a
        self.value_b = value_b
        self.algorithm = algorithm
        self.timestamp = datetime.now(timezone.utc)
        self.result = None
        self.executed = False
    
    def execute(self) -> float:
        """Execute the algorithm on the data"""
        if self.algorithm == AlgorithmType.COMPUTE_DIFFERENCE:
            self.result = self.value_a - self.value_b
        elif self.algorithm == AlgorithmType.COMPUTE_SUM:
            self.result = self.value_a + self.value_b
        elif self.algorithm == AlgorithmType.COMPUTE_PRODUCT:
            self.result = self.value_a * self.value_b
        elif self.algorithm == AlgorithmType.COMPUTE_DIVISION:
            if self.value_b != 0:
                self.result = self.value_a / self.value_b
            else:
                self.result = 0.0
                print("   WARNING: Division by zero avoided")
        
        self.executed = True
        return self.result


class DataDistributor:
    """Manages data distribution and algorithm reporting"""
    
    def __init__(self):
        self.packages: List[DataPackage] = []
        self.statistics = {algo: 0 for algo in AlgorithmType}
    
    def add_package(self, value_a: float, value_b: float, algorithm: AlgorithmType):
        """Add a data package to the distributor"""
        package = DataPackage(value_a, value_b, algorithm)
        self.packages.append(package)
    
    def print_separator(self):
        """Print a separator line"""
        print("=" * 72)
    
    def print_header(self, title: str):
        """Print a section header"""
        self.print_separator()
        print(title)
        self.print_separator()
    
    def distribute_package(self, package: DataPackage, index: int):
        """Distribute and process a single package"""
        print()
        print(f"DISTRIBUTION #{index}")
        print("-" * 45)
        print(f"Algorithm: {package.algorithm.value}")
        print(f"Input Values: {package.value_a:.2f} and {package.value_b:.2f}")
        
        result = package.execute()
        
        print(f"Result: {result:.4f}")
        print("Status: ✓ Distributed and Executed")
        
        # Update statistics
        self.statistics[package.algorithm] += 1
    
    def distribute_all(self):
        """Distribute all packages"""
        self.print_header("DATA DISTRIBUTION IN PROGRESS")
        
        for i, package in enumerate(self.packages, 1):
            self.distribute_package(package, i)
    
    def print_statistics(self):
        """Print algorithm usage statistics"""
        print()
        self.print_header("ALGORITHM USAGE STATISTICS")
        print()
        
        total = len(self.packages)
        print(f"Total Distributions: {total}")
        print()
        print("Algorithm Breakdown:")
        
        for algo, count in self.statistics.items():
            if total > 0:
                percentage = (count * 100) // total
            else:
                percentage = 0
            print(f"  - {algo.value:20s}: {count:2d} distributions ({percentage:2d}%)")
        
        print()
    
    def print_primary_algorithm(self):
        """Print information about the primary algorithm"""
        # Find most used algorithm
        primary_algo = max(self.statistics.items(), key=lambda x: x[1])
        algo_type, count = primary_algo
        
        self.print_header("PRIMARY ALGORITHM USED")
        print(f"Algorithm: {algo_type.value}")
        print(f"Usage: {count} out of {len(self.packages)} distributions")
        
        if algo_type == AlgorithmType.COMPUTE_DIFFERENCE:
            print("Description: Computes the numerical difference between two values")
            print("Formula: Result = Value_A - Value_B")
        elif algo_type == AlgorithmType.COMPUTE_SUM:
            print("Description: Computes the sum of two values")
            print("Formula: Result = Value_A + Value_B")
        elif algo_type == AlgorithmType.COMPUTE_PRODUCT:
            print("Description: Computes the product of two values")
            print("Formula: Result = Value_A × Value_B")
        elif algo_type == AlgorithmType.COMPUTE_DIVISION:
            print("Description: Computes the division of two values")
            print("Formula: Result = Value_A ÷ Value_B")
        
        print()


def main():
    """Main execution function"""
    
    # Initialize distributor
    distributor = DataDistributor()
    
    # Print system header
    distributor.print_header("DATA DISTRIBUTOR - ALGORITHM REPORTING SYSTEM")
    print("System: Aspect Control Unit")
    print("Module: Data Distribution & Algorithm Dispatcher")
    print()
    
    # Add data packages
    distributor.add_package(100.0, 25.0, AlgorithmType.COMPUTE_DIFFERENCE)
    distributor.add_package(50.0, 30.0, AlgorithmType.COMPUTE_DIFFERENCE)
    distributor.add_package(200.0, 150.0, AlgorithmType.COMPUTE_DIFFERENCE)
    distributor.add_package(10.5, 3.2, AlgorithmType.COMPUTE_DIFFERENCE)
    distributor.add_package(7.5, 2.3, AlgorithmType.COMPUTE_SUM)
    distributor.add_package(15.0, 4.0, AlgorithmType.COMPUTE_PRODUCT)
    distributor.add_package(100.0, 5.0, AlgorithmType.COMPUTE_DIVISION)
    distributor.add_package(88.0, 44.0, AlgorithmType.COMPUTE_DIFFERENCE)
    distributor.add_package(12.5, 7.5, AlgorithmType.COMPUTE_SUM)
    distributor.add_package(6.0, 3.0, AlgorithmType.COMPUTE_PRODUCT)
    
    # Distribute all packages
    distributor.distribute_all()
    
    # Print statistics
    distributor.print_statistics()
    
    # Print primary algorithm info
    distributor.print_primary_algorithm()
    
    # Print completion message
    distributor.print_separator()
    print("✓ ALL DATA DISTRIBUTIONS COMPLETED SUCCESSFULLY")
    distributor.print_separator()


if __name__ == "__main__":
    main()
