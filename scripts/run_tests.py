#!/usr/bin/env python3
"""
Comprehensive Test Runner for Jarvis AI Project

This script provides a unified interface to run all tests with proper configuration,
coverage reporting, and various test execution modes.

Usage:
    python run_tests.py [options]
    
Examples:
    python run_tests.py --all                    # Run all tests
    python run_tests.py --unit                   # Run only unit tests
    python run_tests.py --integration            # Run only integration tests
    python run_tests.py --security               # Run only security tests
    python run_tests.py --coverage               # Run with coverage report
    python run_tests.py --parallel               # Run tests in parallel
    python run_tests.py --verbose                # Verbose output
    python run_tests.py --module security        # Run specific module tests
    python run_tests.py --benchmark              # Run performance benchmarks
    python run_tests.py --mutation               # Run mutation testing
    python run_tests.py --lint                   # Run code quality checks
    python run_tests.py --install-deps           # Install test dependencies
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path
from typing import List, Optional


class TestRunner:
    """Comprehensive test runner for the Jarvis AI project."""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.tests_dir = self.project_root / "tests"
        self.coverage_dir = self.project_root / "htmlcov"
        self.reports_dir = self.project_root / "test_reports"
        
        # Ensure directories exist
        self.tests_dir.mkdir(exist_ok=True)
        self.reports_dir.mkdir(exist_ok=True)
    
    def run_command(self, cmd: List[str], capture_output: bool = False) -> subprocess.CompletedProcess:
        """Run a command and handle errors."""
        print(f"Running: {' '.join(cmd)}")
        try:
            result = subprocess.run(
                cmd,
                cwd=self.project_root,
                capture_output=capture_output,
                text=True,
                check=True
            )
            return result
        except subprocess.CalledProcessError as e:
            print(f"Command failed with exit code {e.returncode}")
            if e.stdout:
                print(f"STDOUT: {e.stdout}")
            if e.stderr:
                print(f"STDERR: {e.stderr}")
            sys.exit(e.returncode)
    
    def install_dependencies(self):
        """Install test dependencies."""
        print("Installing test dependencies...")
        self.run_command([sys.executable, "-m", "pip", "install", "-r", "requirements-test.txt"])
        print("Test dependencies installed successfully.")
    
    def run_unit_tests(self, verbose: bool = False, coverage: bool = False, parallel: bool = False):
        """Run unit tests."""
        cmd = [sys.executable, "-m", "pytest"]
        
        # Add test markers
        cmd.extend(["-m", "unit"])
        
        # Add coverage if requested
        if coverage:
            cmd.extend([
                "--cov=windows_use",
                "--cov-report=html",
                "--cov-report=term-missing",
                "--cov-report=xml",
                f"--cov-report=html:{self.coverage_dir}"
            ])
        
        # Add parallel execution if requested
        if parallel:
            cmd.extend(["-n", "auto"])
        
        # Add verbose output if requested
        if verbose:
            cmd.append("-v")
        
        # Add test directory
        cmd.append(str(self.tests_dir))
        
        # Add HTML report
        cmd.extend(["--html", str(self.reports_dir / "unit_tests.html"), "--self-contained-html"])
        
        self.run_command(cmd)
    
    def run_integration_tests(self, verbose: bool = False, parallel: bool = False):
        """Run integration tests."""
        cmd = [sys.executable, "-m", "pytest"]
        
        # Add test markers
        cmd.extend(["-m", "integration"])
        
        # Add parallel execution if requested
        if parallel:
            cmd.extend(["-n", "auto"])
        
        # Add verbose output if requested
        if verbose:
            cmd.append("-v")
        
        # Add test directory
        cmd.append(str(self.tests_dir))
        
        # Add HTML report
        cmd.extend(["--html", str(self.reports_dir / "integration_tests.html"), "--self-contained-html"])
        
        self.run_command(cmd)
    
    def run_security_tests(self, verbose: bool = False):
        """Run security tests."""
        cmd = [sys.executable, "-m", "pytest"]
        
        # Add test markers
        cmd.extend(["-m", "security"])
        
        # Add verbose output if requested
        if verbose:
            cmd.append("-v")
        
        # Add test directory
        cmd.append(str(self.tests_dir))
        
        # Add HTML report
        cmd.extend(["--html", str(self.reports_dir / "security_tests.html"), "--self-contained-html"])
        
        self.run_command(cmd)
    
    def run_module_tests(self, module: str, verbose: bool = False, coverage: bool = False):
        """Run tests for a specific module."""
        test_file = self.tests_dir / f"test_{module}.py"
        
        if not test_file.exists():
            print(f"Test file {test_file} does not exist.")
            sys.exit(1)
        
        cmd = [sys.executable, "-m", "pytest"]
        
        # Add coverage if requested
        if coverage:
            cmd.extend([
                f"--cov=windows_use.{module}",
                "--cov-report=html",
                "--cov-report=term-missing"
            ])
        
        # Add verbose output if requested
        if verbose:
            cmd.append("-v")
        
        # Add specific test file
        cmd.append(str(test_file))
        
        # Add HTML report
        cmd.extend(["--html", str(self.reports_dir / f"{module}_tests.html"), "--self-contained-html"])
        
        self.run_command(cmd)
    
    def run_all_tests(self, verbose: bool = False, coverage: bool = False, parallel: bool = False):
        """Run all tests."""
        cmd = [sys.executable, "-m", "pytest"]
        
        # Add coverage if requested
        if coverage:
            cmd.extend([
                "--cov=windows_use",
                "--cov-report=html",
                "--cov-report=term-missing",
                "--cov-report=xml",
                f"--cov-report=html:{self.coverage_dir}"
            ])
        
        # Add parallel execution if requested
        if parallel:
            cmd.extend(["-n", "auto"])
        
        # Add verbose output if requested
        if verbose:
            cmd.append("-v")
        
        # Add test directory
        cmd.append(str(self.tests_dir))
        
        # Add HTML report
        cmd.extend(["--html", str(self.reports_dir / "all_tests.html"), "--self-contained-html"])
        
        self.run_command(cmd)
    
    def run_benchmarks(self, verbose: bool = False):
        """Run performance benchmarks."""
        cmd = [sys.executable, "-m", "pytest"]
        
        # Add benchmark plugin
        cmd.extend(["--benchmark-only"])
        
        # Add verbose output if requested
        if verbose:
            cmd.append("-v")
        
        # Add test directory
        cmd.append(str(self.tests_dir))
        
        # Add benchmark report
        cmd.extend(["--benchmark-json", str(self.reports_dir / "benchmarks.json")])
        
        self.run_command(cmd)
    
    def run_mutation_testing(self):
        """Run mutation testing."""
        cmd = ["mutmut", "run", "--paths-to-mutate", "windows_use"]
        self.run_command(cmd)
        
        # Generate HTML report
        html_cmd = ["mutmut", "html"]
        self.run_command(html_cmd)
    
    def run_lint_checks(self):
        """Run code quality checks."""
        print("Running code quality checks...")
        
        # Run flake8
        print("\n=== Running flake8 ===")
        flake8_cmd = ["flake8", "windows_use", "tests", "--output-file", str(self.reports_dir / "flake8.txt")]
        try:
            self.run_command(flake8_cmd)
        except SystemExit:
            print("Flake8 found issues. Check the report for details.")
        
        # Run black check
        print("\n=== Running black check ===")
        black_cmd = ["black", "--check", "--diff", "windows_use", "tests"]
        try:
            self.run_command(black_cmd)
        except SystemExit:
            print("Black formatting issues found. Run 'black windows_use tests' to fix.")
        
        # Run isort check
        print("\n=== Running isort check ===")
        isort_cmd = ["isort", "--check-only", "--diff", "windows_use", "tests"]
        try:
            self.run_command(isort_cmd)
        except SystemExit:
            print("Import sorting issues found. Run 'isort windows_use tests' to fix.")
        
        # Run mypy
        print("\n=== Running mypy ===")
        mypy_cmd = ["mypy", "windows_use", "--html-report", str(self.reports_dir / "mypy")]
        try:
            self.run_command(mypy_cmd)
        except SystemExit:
            print("MyPy type checking issues found. Check the report for details.")
        
        # Run bandit security check
        print("\n=== Running bandit security check ===")
        bandit_cmd = [
            "bandit", "-r", "windows_use", 
            "-f", "html", "-o", str(self.reports_dir / "bandit.html")
        ]
        try:
            self.run_command(bandit_cmd)
        except SystemExit:
            print("Bandit security issues found. Check the report for details.")
        
        # Run pylint
        print("\n=== Running pylint ===")
        pylint_cmd = [
            "pylint", "windows_use", 
            "--output-format=html", 
            f"--reports=y"
        ]
        try:
            result = self.run_command(pylint_cmd, capture_output=True)
            with open(self.reports_dir / "pylint.html", "w") as f:
                f.write(result.stdout)
        except SystemExit:
            print("Pylint issues found. Check the report for details.")
    
    def run_security_audit(self):
        """Run security audit."""
        print("Running security audit...")
        
        # Run safety check
        print("\n=== Running safety check ===")
        safety_cmd = ["safety", "check", "--json", "--output", str(self.reports_dir / "safety.json")]
        try:
            self.run_command(safety_cmd)
        except SystemExit:
            print("Safety vulnerabilities found. Check the report for details.")
        
        # Run pip-audit
        print("\n=== Running pip-audit ===")
        audit_cmd = ["pip-audit", "--format=json", "--output", str(self.reports_dir / "pip-audit.json")]
        try:
            self.run_command(audit_cmd)
        except SystemExit:
            print("Pip-audit vulnerabilities found. Check the report for details.")
    
    def generate_coverage_badge(self):
        """Generate coverage badge."""
        if (self.coverage_dir / "index.html").exists():
            badge_cmd = ["coverage-badge", "-o", str(self.project_root / "coverage.svg")]
            self.run_command(badge_cmd)
            print("Coverage badge generated: coverage.svg")
    
    def clean_reports(self):
        """Clean test reports and coverage data."""
        import shutil
        
        if self.coverage_dir.exists():
            shutil.rmtree(self.coverage_dir)
        
        if self.reports_dir.exists():
            shutil.rmtree(self.reports_dir)
            self.reports_dir.mkdir(exist_ok=True)
        
        # Remove coverage files
        for file in self.project_root.glob(".coverage*"):
            file.unlink()
        
        print("Test reports and coverage data cleaned.")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Comprehensive test runner for Jarvis AI project",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    # Test execution options
    parser.add_argument("--all", action="store_true", help="Run all tests")
    parser.add_argument("--unit", action="store_true", help="Run unit tests only")
    parser.add_argument("--integration", action="store_true", help="Run integration tests only")
    parser.add_argument("--security", action="store_true", help="Run security tests only")
    parser.add_argument("--module", type=str, help="Run tests for specific module")
    parser.add_argument("--benchmark", action="store_true", help="Run performance benchmarks")
    parser.add_argument("--mutation", action="store_true", help="Run mutation testing")
    
    # Code quality options
    parser.add_argument("--lint", action="store_true", help="Run code quality checks")
    parser.add_argument("--audit", action="store_true", help="Run security audit")
    
    # Execution modifiers
    parser.add_argument("--coverage", action="store_true", help="Generate coverage report")
    parser.add_argument("--parallel", action="store_true", help="Run tests in parallel")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    
    # Utility options
    parser.add_argument("--install-deps", action="store_true", help="Install test dependencies")
    parser.add_argument("--clean", action="store_true", help="Clean test reports and coverage data")
    parser.add_argument("--badge", action="store_true", help="Generate coverage badge")
    
    args = parser.parse_args()
    
    runner = TestRunner()
    
    # Handle utility options first
    if args.install_deps:
        runner.install_dependencies()
        return
    
    if args.clean:
        runner.clean_reports()
        return
    
    if args.badge:
        runner.generate_coverage_badge()
        return
    
    # Handle test execution
    if args.all:
        runner.run_all_tests(verbose=args.verbose, coverage=args.coverage, parallel=args.parallel)
    elif args.unit:
        runner.run_unit_tests(verbose=args.verbose, coverage=args.coverage, parallel=args.parallel)
    elif args.integration:
        runner.run_integration_tests(verbose=args.verbose, parallel=args.parallel)
    elif args.security:
        runner.run_security_tests(verbose=args.verbose)
    elif args.module:
        runner.run_module_tests(args.module, verbose=args.verbose, coverage=args.coverage)
    elif args.benchmark:
        runner.run_benchmarks(verbose=args.verbose)
    elif args.mutation:
        runner.run_mutation_testing()
    elif args.lint:
        runner.run_lint_checks()
    elif args.audit:
        runner.run_security_audit()
    else:
        # Default: run all tests with coverage
        runner.run_all_tests(verbose=args.verbose, coverage=True, parallel=args.parallel)
    
    # Generate coverage badge if coverage was requested
    if args.coverage:
        runner.generate_coverage_badge()
    
    print("\n=== Test execution completed ===")
    print(f"Reports available in: {runner.reports_dir}")
    if args.coverage:
        print(f"Coverage report available in: {runner.coverage_dir}")


if __name__ == "__main__":
    main()