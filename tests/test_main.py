import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.agent_provocateur.main import main

def test_main():
    # Test that main function returns True
    assert main() is True

if __name__ == "__main__":
    # Run the test directly
    result = test_main()
    print("Test passed!" if result is None else "Test failed!")
