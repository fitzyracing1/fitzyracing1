"""
Algorithm Verification Page
Checks and validates the compute difference algorithm implementation
"""

import json
from datetime import datetime, timezone
from typing import List, Dict, Any, Tuple


class AlgorithmChecker:
    """Validates compute difference algorithm correctness"""
    
    def __init__(self):
        self.test_results: List[Dict[str, Any]] = []
    
    def compute_difference(self, value_a: float, value_b: float) -> float:
        """
        Core algorithm: compute difference between two values
        """
        return value_a - value_b
    
    def verify_computation(self, value_a: float, value_b: float, expected: float) -> bool:
        """
        Verify a single computation
        """
        actual = self.compute_difference(value_a, value_b)
        # Handle infinity cases
        if expected == float('inf') or expected == float('-inf'):
            return actual == expected
        return abs(actual - expected) < 0.0001
    
    def run_test_case(self, value_a: float, value_b: float, expected: float, 
                     test_name: str = "") -> Dict[str, Any]:
        """
        Run a single test case and record results
        """
        start_time = datetime.now(timezone.utc)
        actual = self.compute_difference(value_a, value_b)
        # Handle infinity cases
        if expected == float('inf') or expected == float('-inf'):
            passed = actual == expected
        else:
            passed = abs(actual - expected) < 0.0001
        
        result = {
            "test_name": test_name or f"Test_{len(self.test_results) + 1}",
            "value_a": value_a,
            "value_b": value_b,
            "expected": expected,
            "actual": actual,
            "passed": passed,
            "timestamp": start_time.isoformat(),
            "error": None if passed else f"Expected {expected}, got {actual}"
        }
        
        self.test_results.append(result)
        return result
    
    def run_standard_tests(self) -> List[Dict[str, Any]]:
        """
        Run standard algorithm validation tests
        """
        test_cases = [
            (10, 5, 5, "Basic positive difference"),
            (100, 50, 50, "Large positive difference"),
            (5, 10, -5, "Negative difference"),
            (0, 0, 0, "Zero difference"),
            (-10, -5, -5, "Negative values"),
            (7.5, 2.3, 5.2, "Decimal precision"),
            (1000, 250, 750, "Large scale difference"),
            (0.1, 0.05, 0.05, "Small decimal values"),
            (-100, 50, -150, "Mixed sign difference"),
            (3.14159, 2.71828, 0.42331, "Pi minus e"),
        ]
        
        results = []
        for value_a, value_b, expected, name in test_cases:
            result = self.run_test_case(value_a, value_b, expected, name)
            results.append(result)
        
        return results
    
    def run_edge_cases(self) -> List[Dict[str, Any]]:
        """
        Test edge cases and boundary conditions
        """
        edge_cases = [
            (float('inf'), 100, float('inf'), "Positive infinity"),
            (100, float('inf'), float('-inf'), "Subtract infinity"),
            (1e10, 1e-10, 1e10, "Very large vs very small"),
            (-1e10, 1e10, -2e10, "Large negative spread"),
        ]
        
        results = []
        for value_a, value_b, expected, name in edge_cases:
            result = self.run_test_case(value_a, value_b, expected, name)
            results.append(result)
        
        return results
    
    def generate_report(self) -> str:
        """
        Generate a formatted test report
        """
        total = len(self.test_results)
        passed = sum(1 for r in self.test_results if r["passed"])
        failed = total - passed
        
        report = []
        report.append("=" * 70)
        report.append("ALGORITHM VERIFICATION REPORT")
        report.append("=" * 70)
        report.append(f"\nGenerated: {datetime.now(timezone.utc).isoformat()}")
        report.append(f"\nTotal Tests: {total}")
        report.append(f"Passed: {passed} ({100 * passed / total if total > 0 else 0:.1f}%)")
        report.append(f"Failed: {failed}")
        report.append("\n" + "=" * 70)
        report.append("\nTEST RESULTS:")
        report.append("-" * 70)
        
        for i, result in enumerate(self.test_results, 1):
            status = "✓ PASS" if result["passed"] else "✗ FAIL"
            report.append(f"\n{i}. {result['test_name']}")
            report.append(f"   {status}")
            report.append(f"   Input: {result['value_a']} - {result['value_b']}")
            report.append(f"   Expected: {result['expected']}, Actual: {result['actual']}")
            if result["error"]:
                report.append(f"   Error: {result['error']}")
        
        report.append("\n" + "=" * 70)
        
        return "\n".join(report)
    
    def export_json(self, filename: str = "algorithm_check_results.json") -> None:
        """
        Export results to JSON file
        """
        data = {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "total_tests": len(self.test_results),
            "passed": sum(1 for r in self.test_results if r["passed"]),
            "failed": sum(1 for r in self.test_results if not r["passed"]),
            "test_results": self.test_results
        }
        
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"Results exported to {filename}")


def main():
    """
    Main execution function
    """
    print("Starting Algorithm Verification...")
    print()
    
    checker = AlgorithmChecker()
    
    # Run standard tests
    print("Running standard test cases...")
    standard_results = checker.run_standard_tests()
    print(f"Completed {len(standard_results)} standard tests")
    
    # Run edge cases
    print("\nRunning edge case tests...")
    edge_results = checker.run_edge_cases()
    print(f"Completed {len(edge_results)} edge case tests")
    
    # Generate and display report
    print("\n")
    report = checker.generate_report()
    print(report)
    
    # Export to JSON
    checker.export_json()
    
    # Summary
    total = len(checker.test_results)
    passed = sum(1 for r in checker.test_results if r["passed"])
    
    print("\n" + "=" * 70)
    if passed == total:
        print("✓ ALL TESTS PASSED - Algorithm verified successfully!")
    else:
        print(f"⚠ {total - passed} test(s) failed - Review required")
    print("=" * 70)


if __name__ == "__main__":
    main()
