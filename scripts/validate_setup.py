#!/usr/bin/env python3
"""
Validation script to check if the project setup is correct
"""

import os
import sys
from pathlib import Path

def check_directory_structure():
    """Check if all required directories exist"""
    required_dirs = [
        'src/scraper',
        'src/models', 
        'src/utils',
        'src/config',
        'data/raw',
        'data/processed',
        'data/external',
        'data/backup_data',
        'notebooks',
        'tests',
        'docs',
        'scripts'
    ]
    
    missing_dirs = []
    for dir_path in required_dirs:
        if not os.path.exists(dir_path):
            missing_dirs.append(dir_path)
    
    if missing_dirs:
        print("❌ Missing directories:")
        for dir_path in missing_dirs:
            print(f"   - {dir_path}")
        return False
    else:
        print("✅ All required directories exist")
        return True

def check_required_files():
    """Check if all required files exist"""
    required_files = [
        'requirements.txt',
        'config.yaml',
        'README.md',
        'setup.py',
        '.gitignore',
        'src/__init__.py',
        'src/config/__init__.py',
        'src/config/config.py'
    ]
    
    missing_files = []
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
    
    if missing_files:
        print("❌ Missing files:")
        for file_path in missing_files:
            print(f"   - {file_path}")
        return False
    else:
        print("✅ All required files exist")
        return True

def check_data_files():
    """Check if data files are in the correct location"""
    expected_data_files = [
        'data/raw/combined_3seasons.csv',
        'data/raw/serie_a_results_2022_2023.csv',
        'data/raw/serie_a_results_2023_2024.csv',
        'data/raw/serie_a_results_2024_2025.csv'
    ]
    
    missing_data = []
    for file_path in expected_data_files:
        if not os.path.exists(file_path):
            missing_data.append(file_path)
    
    if missing_data:
        print("⚠️  Missing data files:")
        for file_path in missing_data:
            print(f"   - {file_path}")
        return False
    else:
        print("✅ All data files are in place")
        return True

def check_imports():
    """Check if key modules can be imported"""
    try:
        # Add src to path for testing
        sys.path.insert(0, 'src')
        
        from config import get_config
        config = get_config()
        print("✅ Configuration system working")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return False

def main():
    """Run all validation checks"""
    print("🔍 Validating Serie A Predictor setup...\n")
    
    checks = [
        ("Directory Structure", check_directory_structure),
        ("Required Files", check_required_files), 
        ("Data Files", check_data_files),
        ("Module Imports", check_imports)
    ]
    
    results = []
    for check_name, check_func in checks:
        print(f"Checking {check_name}...")
        result = check_func()
        results.append(result)
        print()
    
    if all(results):
        print("🎉 All checks passed! Your project setup is ready.")
        return 0
    else:
        print("❌ Some checks failed. Please fix the issues above.")
        return 1

if __name__ == "__main__":
    exit(main())
