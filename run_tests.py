#!/usr/bin/env python3
"""
Simple test runner for X Feed Monitor
"""
import sys
import subprocess


def run_tests(test_path=None):
    """Run tests with pytest"""
    cmd = ["python", "-m", "pytest"]

    if test_path:
        cmd.append(test_path)
    else:
        cmd.append("tests/")

    cmd.extend(["-v", "--tb=short"])

    print("🧪 Running tests...")
    print(f"Command: {' '.join(cmd)}")
    print("-" * 50)

    result = subprocess.run(cmd)
    return result.returncode == 0


def run_unit_tests():
    """Run only unit tests"""
    return run_tests("tests/unit/")


def run_integration_tests():
    """Run only integration tests"""
    return run_tests("tests/integration/")


def run_specific_test(test_file):
    """Run a specific test file"""
    return run_tests(f"tests/unit/{test_file}")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        command = sys.argv[1]

        if command == "unit":
            success = run_unit_tests()
        elif command == "integration":
            success = run_integration_tests()
        elif command == "all":
            success = run_tests()
        else:
            # Assume it's a specific test file
            success = run_specific_test(command)
    else:
        # Default: run all tests
        success = run_tests()

    if success:
        print("\n✅ All tests passed!")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed!")
        sys.exit(1)
