#!/usr/bin/env python3
"""
Setup script for AI Player project.
Installs dependencies and prepares the development environment.
"""

import subprocess
import sys
from pathlib import Path


def run_command(command, description=""):
    """Run a shell command and handle errors."""
    print(f"\n{'='*50}")
    print(f"Running: {description}")
    print(f"Command: {command}")
    print('='*50)
    
    try:
        result = subprocess.run(command, shell=True, check=True, 
                              capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {e}")
        if e.stdout:
            print(f"STDOUT: {e.stdout}")
        if e.stderr:
            print(f"STDERR: {e.stderr}")
        return False


def setup_virtual_environment():
    """Create and activate virtual environment."""
    venv_path = Path("venv")
    
    if not venv_path.exists():
        print("Creating virtual environment...")
        if not run_command("python3 -m venv venv", "Create virtual environment"):
            return False
    else:
        print("Virtual environment already exists.")
    
    return True


def install_dependencies():
    """Install Python dependencies."""
    print("Installing Python dependencies...")
    
    # Check if we're in a virtual environment
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        pip_command = "pip install -r requirements.txt"
    else:
        pip_command = "venv/bin/pip install -r requirements.txt"
    
    return run_command(pip_command, "Install Python packages")


def verify_pytorch_mps():
    """Verify PyTorch MPS (Metal Performance Shaders) support."""
    print("Verifying PyTorch MPS support...")
    
    test_script = """
import torch
print(f"PyTorch version: {torch.__version__}")
print(f"MPS available: {torch.backends.mps.is_available()}")
if torch.backends.mps.is_available():
    print("✅ MPS backend is available for GPU acceleration")
else:
    print("❌ MPS backend not available, will use CPU")
"""
    
    try:
        if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
            python_command = "python"
        else:
            python_command = "venv/bin/python"
            
        result = subprocess.run([python_command, "-c", test_script], 
                              capture_output=True, text=True, check=True)
        print(result.stdout)
        return True
    except Exception as e:
        print(f"Error verifying PyTorch: {e}")
        return False


def create_initial_directories():
    """Create initial directory structure."""
    print("Creating directory structure...")
    
    directories = [
        "data/logs/tensorboard",
        "data/screenshots",
        "data/templates", 
        "data/models",
        "tests",
        "scripts"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"Created: {directory}")
    
    return True


def test_dune_legacy_access():
    """Test if Dune Legacy can be launched."""
    print("Testing Dune Legacy access...")
    
    app_path = Path("/Applications/Dune Legacy.app")
    if app_path.exists():
        print("✅ Dune Legacy found at /Applications/Dune Legacy.app")
        return True
    else:
        print("❌ Dune Legacy not found at /Applications/Dune Legacy.app")
        print("Please ensure Dune Legacy is installed in the Applications folder")
        return False


def main():
    """Main setup function."""
    print("AI Player Project Setup")
    print("="*50)
    
    steps = [
        ("Setting up virtual environment", setup_virtual_environment),
        ("Installing dependencies", install_dependencies),
        ("Verifying PyTorch MPS support", verify_pytorch_mps),
        ("Creating directories", create_initial_directories),
        ("Testing Dune Legacy access", test_dune_legacy_access)
    ]
    
    failed_steps = []
    
    for step_name, step_function in steps:
        print(f"\n🔄 {step_name}...")
        if step_function():
            print(f"✅ {step_name} completed successfully")
        else:
            print(f"❌ {step_name} failed")
            failed_steps.append(step_name)
    
    print("\n" + "="*50)
    print("SETUP SUMMARY")
    print("="*50)
    
    if failed_steps:
        print("❌ Setup completed with errors:")
        for step in failed_steps:
            print(f"  - {step}")
        print("\nPlease resolve the errors above before proceeding.")
        return False
    else:
        print("✅ All setup steps completed successfully!")
        print("\nNext steps:")
        print("1. Activate virtual environment: source venv/bin/activate")
        print("2. Run the main script: python main.py")
        print("3. Start with M1 milestone: Game Launch POC")
        return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)