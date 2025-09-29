#!/usr/bin/env python3
"""
Installation script for Nano Banana Image Generator
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        print(f"Error output: {e.stderr}")
        return False

def main():
    print("🍌 Nano Banana Image Generator - Installation Script")
    print("=" * 60)
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        sys.exit(1)
    
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")
    
    # Install dependencies
    print("\n📦 Installing dependencies...")
    if not run_command("pip install -r requirements.txt", "Installing Python packages"):
        print("❌ Failed to install dependencies")
        sys.exit(1)
    
    # Create necessary directories
    print("\n📁 Creating directories...")
    directories = ["output_images", "cache"]
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✅ Created directory: {directory}")
    
    # Check if config exists, if not create it
    if not os.path.exists("config.json"):
        print("\n⚙️  Creating default configuration...")
        from config_manager import ConfigManager
        config = ConfigManager()
        print("✅ Default configuration created")
    else:
        print("✅ Configuration file already exists")
    
    print("\n🎉 Installation completed successfully!")
    print("\nTo start the application:")
    print("  python app.py")
    print("\nTo start the API server:")
    print("  python main.py")
    print("\nFor help, check the README.md file")

if __name__ == "__main__":
    main()

