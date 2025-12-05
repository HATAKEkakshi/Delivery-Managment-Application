#!/usr/bin/env python3
"""
Test runner script for FastAPI backend
"""
import subprocess
import sys
import os

def run_tests():
    """Run all tests with coverage reporting"""
    
    # Change to project directory
    project_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(project_dir)
    
    print("🚀 Starting FastAPI Backend Tests")
    print("=" * 50)
    
    # Test commands to run
    test_commands = [
        # Run all tests with verbose output
        ["python", "-m", "pytest", "app/tests/", "-v", "--tb=short"],
        
        # Run tests with coverage (if pytest-cov is installed)
        # ["python", "-m", "pytest", "app/tests/", "--cov=app", "--cov-report=html", "--cov-report=term"],
        
        # Run specific test categories
        # ["python", "-m", "pytest", "app/tests/test_seller.py", "-v"],
        # ["python", "-m", "pytest", "app/tests/test_delivery_partner.py", "-v"],
        # ["python", "-m", "pytest", "app/tests/test_shipment.py", "-v"],
        # ["python", "-m", "pytest", "app/tests/test_integration.py", "-v"],
        # ["python", "-m", "pytest", "app/tests/test_security.py", "-v"],
        # ["python", "-m", "pytest", "app/tests/test_performance.py", "-v"],
    ]
    
    for i, cmd in enumerate(test_commands, 1):
        print(f"\n📋 Running test command {i}/{len(test_commands)}")
        print(f"Command: {' '.join(cmd)}")
        print("-" * 30)
        
        try:
            result = subprocess.run(cmd, check=True, capture_output=False)
            print(f"✅ Test command {i} completed successfully")
        except subprocess.CalledProcessError as e:
            print(f"❌ Test command {i} failed with exit code {e.returncode}")
            return False
        except FileNotFoundError:
            print(f"❌ Command not found: {cmd[0]}")
            print("Make sure pytest is installed: pip install pytest pytest-asyncio")
            return False
    
    print("\n🎉 All tests completed successfully!")
    return True

def run_specific_tests():
    """Run specific test categories"""
    
    test_categories = {
        "1": ("Health Check", ["python", "-m", "pytest", "app/tests/test_health.py", "-v"]),
        "2": ("Seller Tests", ["python", "-m", "pytest", "app/tests/test_seller.py", "-v"]),
        "3": ("Partner Tests", ["python", "-m", "pytest", "app/tests/test_delivery_partner.py", "-v"]),
        "4": ("Shipment Tests", ["python", "-m", "pytest", "app/tests/test_shipment.py", "-v"]),
        "5": ("Integration Tests", ["python", "-m", "pytest", "app/tests/test_integration.py", "-v"]),
        "6": ("Security Tests", ["python", "-m", "pytest", "app/tests/test_security.py", "-v"]),
        "7": ("Performance Tests", ["python", "-m", "pytest", "app/tests/test_performance.py", "-v"]),
        "8": ("All Tests", ["python", "-m", "pytest", "app/tests/", "-v"]),
    }
    
    print("🧪 FastAPI Test Categories")
    print("=" * 30)
    for key, (name, _) in test_categories.items():
        print(f"{key}. {name}")
    
    choice = input("\nSelect test category (1-8): ").strip()
    
    if choice in test_categories:
        name, cmd = test_categories[choice]
        print(f"\n🚀 Running {name}")
        print("-" * 30)
        
        try:
            subprocess.run(cmd, check=True)
            print(f"\n✅ {name} completed successfully!")
        except subprocess.CalledProcessError as e:
            print(f"\n❌ {name} failed with exit code {e.returncode}")
        except FileNotFoundError:
            print(f"\n❌ Command not found. Make sure pytest is installed:")
            print("pip install pytest pytest-asyncio")
    else:
        print("❌ Invalid choice")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--interactive":
        run_specific_tests()
    else:
        success = run_tests()
        sys.exit(0 if success else 1)