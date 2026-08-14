"""
COMPLETE SETUP - ALL-IN-ONE SCRIPT
===================================

This single script does EVERYTHING:
1. Generates realistic dataset (500 images)
2. Trains YOLOv11 model
3. Starts backend API server

Just run: python complete_setup.py

Author: Manufacturing Defect Detection System
"""

import os
import sys
import subprocess
from pathlib import Path
import time

def print_header(text):
    print("\n" + "="*70)
    print(f"{text.center(70)}")
    print("="*70 + "\n")

def run_command(command, description):
    """Run a command and show progress."""
    print(f"⏳ {description}...")
    result = subprocess.run(command, shell=True)
    if result.returncode == 0:
        print(f"✓ {description} completed!")
        return True
    else:
        print(f"✗ {description} failed!")
        return False

def main():
    print_header("COMPLETE DEFECT DETECTION SETUP")
    print("This will:")
    print("  1. Generate 500 realistic training images")
    print("  2. Train YOLOv11 model (30-60 minutes)")
    print("  3. Start the backend server")
    print("\nTotal time: ~60-90 minutes")
    
    response = input("\nContinue? (y/n): ")
    if response.lower() != 'y':
        print("Setup cancelled.")
        return
    
    # Check if files exist
    required_files = [
        'generate_dataset.py',
        'train_yolov11.py',
        'backend_api.py'
    ]
    
    missing_files = [f for f in required_files if not Path(f).exists()]
    
    if missing_files:
        print("\n⚠️ Missing required files:")
        for f in missing_files:
            print(f"  ✗ {f}")
        print("\n❌ Cannot continue without all files!")
        print("\nPlease download the complete package with:")
        print("  - generate_dataset.py")
        print("  - train_yolov11.py")
        print("  - backend_api.py")
        print("  - frontend/ folder")
        return
    
    # Step 1: Generate Dataset
    print_header("STEP 1: GENERATING DATASET")
    if not run_command("python generate_dataset.py", "Dataset generation"):
        return
    
    # Verify dataset was created
    if not Path("dataset/images/train").exists():
        print("✗ Dataset folder not created!")
        return
    
    train_images = list(Path("dataset/images/train").glob("*.jpg"))
    print(f"\n✓ Created {len(train_images)} training images")
    
    # Step 2: Train Model
    print_header("STEP 2: TRAINING YOLOV11 MODEL")
    print("⏱ This will take 30-60 minutes...")
    
    if not run_command("python train_yolov11.py", "Model training"):
        return
    
    # Verify model was created
    if not Path("models/best.pt").exists():
        print("✗ Model file not created!")
        return
    
    print(f"\n✓ Model saved to models/best.pt")
    
    # Step 3: Start Server
    print_header("STEP 3: STARTING BACKEND SERVER")
    print("Server will start at: http://localhost:5000")
    print("\nPress Ctrl+C to stop the server")
    print("\n" + "="*70)
    
    time.sleep(2)
    
    # Run backend
    subprocess.run("python backend_api.py", shell=True)

if __name__ == "__main__":
    main()
