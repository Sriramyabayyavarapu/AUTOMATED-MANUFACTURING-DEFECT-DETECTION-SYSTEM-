"""
YOLOV11 LIGHTWEIGHT TRAINING SCRIPT - OPTIMIZED FOR LOW-END PCs
===============================================================

Features:
- Reduced epochs (30 instead of 150) for faster training
- Smaller model (yolo11n.pt - nano) for low memory
- Optimized for systems with limited GPU/CPU
- Google Colab compatible
- Quick training time: 20-40 minutes on GPU

Author: DefectVision AI System
Version: 2.0 (Lightweight)
"""

from ultralytics import YOLO
import torch
import yaml
from pathlib import Path
import json
from datetime import datetime
import shutil
import warnings
warnings.filterwarnings('ignore')

class LightweightYOLOv11Trainer:
    """Lightweight YOLOv11 training for low-end systems."""
    
    def __init__(self, project_dir: str = "."):
        self.project_dir = Path(project_dir)
        self.results_dir = self.project_dir / 'training_results'
        self.results_dir.mkdir(exist_ok=True)
        
        # LIGHTWEIGHT Configuration - Optimized for low-end PCs
        self.config = {
            # Model Selection - NANO (smallest and fastest)
            'model_size': 'yolo11n.pt',  # Nano model - only ~3MB, very fast!
            # Alternative: 'yolo11s.pt' (small) if you have a bit more power
            
            # Training Parameters - REDUCED for speed
            'epochs': 30,  # Reduced from 150 to 30 for quick training
            'batch_size': 8,  # Small batch size for low memory
            'img_size': 640,
            'patience': 10,  # Early stopping
            'save_period': -1,  # Don't save intermediate checkpoints to save disk space
            
            # Optimizer Settings
            'optimizer': 'AdamW',
            'lr0': 0.001,
            'lrf': 0.01,
            'momentum': 0.937,
            'weight_decay': 0.0005,
            'warmup_epochs': 3.0,  # Reduced warmup
            'warmup_momentum': 0.8,
            'warmup_bias_lr': 0.1,
            
            # Learning Rate Scheduler
            'cos_lr': True,
            
            # REDUCED Augmentation for faster training
            'hsv_h': 0.015,
            'hsv_s': 0.7,
            'hsv_v': 0.4,
            'degrees': 10.0,  # Reduced rotation
            'translate': 0.1,
            'scale': 0.5,
            'shear': 0.0,  # Disabled for speed
            'perspective': 0.0,  # Disabled for speed
            'flipud': 0.0,
            'fliplr': 0.5,
            'mosaic': 1.0,
            'mixup': 0.1,  # Reduced mixup
            'copy_paste': 0.0,  # Disabled for speed
            
            # Loss Weights
            'box': 7.5,
            'cls': 0.5,
            'dfl': 1.5,
            
            # Performance - Optimized for low-end systems
            'amp': True,  # Automatic Mixed Precision for speed
            'cache': False,  # Don't cache to save RAM
            'workers': 4,  # Reduced workers
            'device': None,  # Auto-select
            'exist_ok': True,
            'pretrained': True,
            'verbose': True,
            
            # Validation
            'val': True,
            'plots': True,
        }
        
        self.training_metrics = {
            'best_map50': 0.0,
            'training_time': 0.0,
        }
    
    def print_banner(self):
        """Print banner."""
        banner = """
        ╔═══════════════════════════════════════════════════════════════╗
        ║                                                               ║
        ║        🚀 DEFECTVISION AI - LIGHTWEIGHT TRAINER 🚀            ║
        ║                                                               ║
        ║              Quick Training for Low-End Systems               ║
        ║                   30 Epochs • Nano Model                      ║
        ║                                                               ║
        ╚═══════════════════════════════════════════════════════════════╝
        """
        print(banner)
    
    def check_system(self):
        """System check with auto-optimization."""
        print("\n" + "="*70)
        print("SYSTEM CHECK".center(70))
        print("="*70)
        
        # GPU Check
        if torch.cuda.is_available():
            gpu_name = torch.cuda.get_device_name(0)
            gpu_memory = torch.cuda.get_device_properties(0).total_memory / 1e9
            
            print(f"\n✅ GPU Found: {gpu_name}")
            print(f"   Memory: {gpu_memory:.2f} GB")
            
            # Auto-adjust batch size
            if gpu_memory < 4:
                print("   ⚠️  Limited GPU memory - setting batch size to 4")
                self.config['batch_size'] = 4
            elif gpu_memory < 6:
                print("   Setting batch size to 8 (optimal)")
                self.config['batch_size'] = 8
            else:
                print("   Setting batch size to 16 (good GPU!)")
                self.config['batch_size'] = 16
            
            device = '0'
        else:
            print("\n⚠️  No GPU - using CPU (slower but will work)")
            print("   Estimated time: 1-2 hours")
            print("   Tip: Use Google Colab for FREE GPU!")
            self.config['batch_size'] = 4
            self.config['workers'] = 2
            device = 'cpu'
        
        # Dataset Check
        dataset_dir = self.project_dir / 'dataset'
        if not dataset_dir.exists():
            print(f"\n❌ Dataset not found!")
            print("   Run: python generate_dataset.py")
            return None
        
        train_images = list((dataset_dir / 'images' / 'train').glob('*.jpg'))
        val_images = list((dataset_dir / 'images' / 'val').glob('*.jpg'))
        
        print(f"\n✅ Dataset Ready:")
        print(f"   Training: {len(train_images)} images")
        print(f"   Validation: {len(val_images)} images")
        
        print("\n" + "="*70)
        return device
    
    def create_data_yaml(self):
        """Create data.yaml."""
        dataset_dir = self.project_dir / 'dataset'
        
        data_config = {
            'path': str(dataset_dir.absolute()),
            'train': 'images/train',
            'val': 'images/val',
            'test': 'images/test',
            'nc': 4,
            'names': {0: 'crack', 1: 'scratch', 2: 'deformation', 3: 'missing'}
        }
        
        yaml_path = self.project_dir / 'data.yaml'
        with open(yaml_path, 'w') as f:
            yaml.dump(data_config, f, default_flow_style=False)
        
        print(f"✅ Created data.yaml")
        return yaml_path
    
    def train(self):
        """Execute lightweight training."""
        
        self.print_banner()
        
        # System check
        device = self.check_system()
        if device is None:
            return None, None
        
        # Create data config
        data_yaml = self.create_data_yaml()
        
        # Load model
        print(f"\n🔄 Loading {self.config['model_size']} (Nano - Fast & Lightweight)...")
        model = YOLO(self.config['model_size'])
        print("✅ Model loaded!")
        
        # Print config
        print("\n" + "="*70)
        print("TRAINING CONFIGURATION".center(70))
        print("="*70)
        print(f"\n🎯 Model: {self.config['model_size']} (Nano - ~3MB)")
        print(f"📊 Epochs: {self.config['epochs']} (Quick training!)")
        print(f"📦 Batch Size: {self.config['batch_size']}")
        print(f"🖼️  Image Size: {self.config['img_size']}")
        print(f"⏱️  Estimated Time: 20-40 min (GPU) or 1-2 hours (CPU)")
        print(f"🎯 Expected Accuracy: 80-85% (Good for lightweight!)")
        print("="*70)
        
        print("\n🚀 Starting training NOW!\n")
        
        # Record start time
        import time
        start_time = time.time()
        
        # Train
        try:
            results = model.train(
                data=str(data_yaml),
                epochs=self.config['epochs'],
                batch=self.config['batch_size'],
                imgsz=self.config['img_size'],
                device=device,
                
                # Optimizer
                optimizer=self.config['optimizer'],
                lr0=self.config['lr0'],
                lrf=self.config['lrf'],
                momentum=self.config['momentum'],
                weight_decay=self.config['weight_decay'],
                warmup_epochs=self.config['warmup_epochs'],
                cos_lr=self.config['cos_lr'],
                
                # Augmentation
                hsv_h=self.config['hsv_h'],
                hsv_s=self.config['hsv_s'],
                hsv_v=self.config['hsv_v'],
                degrees=self.config['degrees'],
                translate=self.config['translate'],
                scale=self.config['scale'],
                flipud=self.config['flipud'],
                fliplr=self.config['fliplr'],
                mosaic=self.config['mosaic'],
                mixup=self.config['mixup'],
                
                # Loss
                box=self.config['box'],
                cls=self.config['cls'],
                dfl=self.config['dfl'],
                
                # Settings
                patience=self.config['patience'],
                save=True,
                save_period=self.config['save_period'],
                project=str(self.results_dir),
                name='yolov11_lightweight',
                exist_ok=self.config['exist_ok'],
                pretrained=self.config['pretrained'],
                verbose=self.config['verbose'],
                val=self.config['val'],
                plots=self.config['plots'],
                
                # Performance
                workers=self.config['workers'],
                cache=self.config['cache'],
                amp=self.config['amp'],
            )
            
            end_time = time.time()
            self.training_metrics['training_time'] = (end_time - start_time) / 60
            
            print("\n" + "="*70)
            print("✅ TRAINING COMPLETED!".center(70))
            print("="*70)
            
            return model, results
            
        except Exception as e:
            print(f"\n❌ Training failed: {e}")
            return None, None
    
    def analyze_results(self, model):
        """Quick results analysis."""
        
        print("\n" + "="*70)
        print("RESULTS".center(70))
        print("="*70)
        
        # Validate
        print("\n🔍 Testing model...")
        metrics = model.val(data=str(self.project_dir / 'data.yaml'), split='test')
        
        map50 = float(metrics.box.map50)
        precision = float(metrics.box.mp)
        recall = float(metrics.box.mr)
        
        self.training_metrics['best_map50'] = map50
        
        print(f"\n📊 Performance:")
        print(f"   mAP@0.5:   {map50*100:.2f}%")
        print(f"   Precision: {precision*100:.2f}%")
        print(f"   Recall:    {recall*100:.2f}%")
        print(f"   Time:      {self.training_metrics['training_time']:.1f} minutes")
        
        if map50 >= 0.80:
            print(f"\n🌟 EXCELLENT! Ready for deployment!")
        elif map50 >= 0.75:
            print(f"\n✅ GOOD! Usable for most cases.")
        else:
            print(f"\n⚠️  Consider training longer (increase epochs to 50-100)")
        
        # Save report
        report = {
            'model': 'YOLOv11-Nano',
            'epochs_trained': self.config['epochs'],
            'timestamp': datetime.now().isoformat(),
            'metrics': {
                'mAP@0.5': map50,
                'precision': precision,
                'recall': recall,
            },
            'training_time_minutes': self.training_metrics['training_time'],
        }
        
        report_path = self.results_dir / 'training_report.json'
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=4)
        
        # Copy model
        source = self.results_dir / 'yolov11_lightweight' / 'weights' / 'best.pt'
        dest_dir = self.project_dir / 'models'
        dest_dir.mkdir(exist_ok=True)
        dest = dest_dir / 'best.pt'
        
        if source.exists():
            shutil.copy(source, dest)
            print(f"\n✅ Model saved: models/best.pt")
        
        print("\n" + "="*70)
    
    def print_summary(self):
        """Print summary."""
        print("\n🎉 ALL DONE!\n")
        print("📁 Files created:")
        print("   ├─ models/best.pt (Your trained model!)")
        print("   └─ training_results/yolov11_lightweight/")
        print("\n🚀 Next steps:")
        print("   1. Run: python backend_api.py")
        print("   2. Open frontend in browser")
        print("   3. Upload images and test!")
        print(f"\n💡 Your model accuracy: {self.training_metrics['best_map50']*100:.1f}%")
        print(f"⏱️  Training took: {self.training_metrics['training_time']:.1f} minutes\n")


def main():
    """Main execution."""
    trainer = LightweightYOLOv11Trainer(project_dir=".")
    model, results = trainer.train()
    
    if model and results:
        trainer.analyze_results(model)
        trainer.print_summary()
    else:
        print("\n❌ Training failed. Check errors above.\n")


if __name__ == "__main__":
    main()
