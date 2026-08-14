"""
BULLETPROOF DATASET GENERATOR - NO OVERFLOW ERRORS
===================================================

Completely rewritten to eliminate all overflow issues.
Safe version that works on all systems.

Author: Manufacturing Defect Detection System
Version: 3.0 (Bulletproof)
"""

import cv2
import numpy as np
from pathlib import Path
import random
import math
import json

class RealisticDefectGenerator:
    """Generate realistic manufacturing defect images - overflow-safe version."""
    
    def __init__(self, output_dir: str = "dataset"):
        self.output_dir = Path(output_dir)
        self.setup_directories()
        
        self.stats = {
            'total_images': 0,
            'defects_per_class': {'crack': 0, 'scratch': 0, 'deformation': 0, 'missing': 0},
            'defects_per_image': [],
            'defect_sizes': []
        }
    
    def setup_directories(self):
        """Create directory structure."""
        dirs = ['images/train', 'images/val', 'images/test',
                'labels/train', 'labels/val', 'labels/test']
        for d in dirs:
            (self.output_dir / d).mkdir(parents=True, exist_ok=True)
    
    def generate_metal_texture(self, size=(640, 640)):
        """Generate metal texture - SAFE VERSION."""
        h, w = size
        
        # Create base image with safe values
        base_color = random.randint(180, 220)
        img = np.full((h, w, 3), base_color, dtype=np.float32)  # Use float32
        
        # Add brushed metal effect - SAFE
        for i in range(h):
            variation = 10 * math.sin(i * 0.1)
            # Safe addition - stays in float32
            img[i, :, :] += variation
        
        # Add noise - SAFE
        noise = np.random.normal(0, 5, (h, w, 3)).astype(np.float32)
        img += noise
        
        # Clip and convert to uint8 at the end
        img = np.clip(img, 0, 255).astype(np.uint8)
        
        # Add subtle scratches
        for _ in range(random.randint(3, 8)):
            x1, y1 = random.randint(0, w-1), random.randint(0, h-1)
            x2 = np.clip(x1 + random.randint(-100, 100), 0, w-1)
            y2 = np.clip(y1 + random.randint(-20, 20), 0, h-1)
            color = np.clip(base_color + random.randint(-15, 15), 0, 255)
            cv2.line(img, (x1, y1), (int(x2), int(y2)), (int(color), int(color), int(color)), 1)
        
        # Add lighting gradient - SAFE
        gradient = np.linspace(0.9, 1.1, w).astype(np.float32)
        for i in range(3):
            channel = img[:, :, i].astype(np.float32) * gradient
            img[:, :, i] = np.clip(channel, 0, 255).astype(np.uint8)
        
        return img
    
    def generate_plastic_texture(self, size=(640, 640)):
        """Generate plastic texture - SAFE VERSION."""
        h, w = size
        
        colors = [(200, 200, 210), (180, 190, 200), (190, 200, 190)]
        base_color = random.choice(colors)
        
        # Create image safely
        img = np.zeros((h, w, 3), dtype=np.float32)
        img[:, :, 0] = base_color[0]
        img[:, :, 1] = base_color[1]
        img[:, :, 2] = base_color[2]
        
        # Add noise
        noise = np.random.normal(0, 3, (h, w, 3)).astype(np.float32)
        img += noise
        
        # Clip and convert
        img = np.clip(img, 0, 255).astype(np.uint8)
        
        # Add mold line
        if random.random() > 0.5:
            line_y = random.randint(h//4, 3*h//4)
            color = tuple(int(c * 0.95) for c in base_color)
            cv2.line(img, (0, line_y), (w, line_y), color, 2)
        
        return img
    
    def generate_fatigue_crack(self, img, x, y, length):
        """Generate crack - SAFE VERSION."""
        h, w = img.shape[:2]
        points = [(x, y)]
        current_angle = random.uniform(-math.pi/4, math.pi/4)
        
        for step in range(length):
            current_angle += random.uniform(-0.3, 0.3)
            step_length = random.randint(3, 8)
            
            new_x = int(points[-1][0] + step_length * math.cos(current_angle))
            new_y = int(points[-1][1] + step_length * math.sin(current_angle))
            
            # Safe bounds
            new_x = max(10, min(w-10, new_x))
            new_y = max(10, min(h-10, new_y))
            
            points.append((new_x, new_y))
            
            # Draw crack
            width = random.randint(1, 3)
            cv2.line(img, points[-2], points[-1], (0, 0, 0), width)
            
            # Add branches
            if random.random() > 0.8 and step > 5:
                branch_angle = current_angle + random.choice([-math.pi/3, math.pi/3])
                branch_len = random.randint(5, 15)
                branch_x = int(new_x + branch_len * math.cos(branch_angle))
                branch_y = int(new_y + branch_len * math.sin(branch_angle))
                branch_x = max(10, min(w-10, branch_x))
                branch_y = max(10, min(h-10, branch_y))
                cv2.line(img, (new_x, new_y), (branch_x, branch_y), (0, 0, 0), 1)
        
        # Calculate bbox
        xs = [p[0] for p in points]
        ys = [p[1] for p in points]
        bbox = [min(xs), min(ys), max(xs) - min(xs), max(ys) - min(ys)]
        
        return img, bbox
    
    def generate_scratch(self, img, x, y, length, scratch_type='linear'):
        """Generate scratch - SAFE VERSION."""
        h, w = img.shape[:2]
        
        if scratch_type == 'linear':
            angle = random.uniform(-math.pi/6, math.pi/6)
            end_x = int(x + length * math.cos(angle))
            end_y = int(y + length * math.sin(angle))
            end_x = max(10, min(w-10, end_x))
            end_y = max(10, min(h-10, end_y))
            
            cv2.line(img, (x, y), (end_x, end_y), (60, 60, 60), 2)
            cv2.line(img, (x+1, y), (end_x+1, end_y), (140, 140, 140), 1)
            
            bbox = [min(x, end_x), min(y, end_y), abs(end_x - x), abs(end_y - y)]
        
        else:  # curved
            points = [(x, y)]
            current_angle = random.uniform(-math.pi/4, math.pi/4)
            
            for _ in range(length // 5):
                current_angle += random.uniform(-0.2, 0.2)
                step = 5
                new_x = int(points[-1][0] + step * math.cos(current_angle))
                new_y = int(points[-1][1] + step * math.sin(current_angle))
                new_x = max(10, min(w-10, new_x))
                new_y = max(10, min(h-10, new_y))
                points.append((new_x, new_y))
                
                cv2.line(img, points[-2], points[-1], (60, 60, 60), 2)
            
            xs = [p[0] for p in points]
            ys = [p[1] for p in points]
            bbox = [min(xs), min(ys), max(xs) - min(xs), max(ys) - min(ys)]
        
        return img, bbox
    
    def generate_deformation(self, img, x, y, size, deform_type='dent'):
        """Generate deformation - SAFE VERSION."""
        center = (x + size//2, y + size//2)
        
        if deform_type == 'dent':
            for r in range(size//2, 0, -3):
                brightness = int(np.clip(180 - (size//2 - r) * 2, 0, 255))
                cv2.circle(img, center, r, (brightness, brightness, brightness), 1)
            
            highlight_offset = size // 4
            cv2.circle(img, (center[0] - highlight_offset, center[1] - highlight_offset), 
                      size // 6, (230, 230, 230), -1)
        else:  # bulge
            for r in range(size//2, 0, -3):
                brightness = int(np.clip(200 + (size//2 - r) * 1.5, 0, 255))
                cv2.circle(img, center, r, (brightness, brightness, brightness), 1)
        
        bbox = [x, y, size, size]
        return img, bbox
    
    def generate_missing_component(self, img, x, y, size):
        """Generate missing component - SAFE VERSION."""
        cv2.rectangle(img, (x, y), (x + size, y + size), (255, 255, 255), -1)
        cv2.rectangle(img, (x, y), (x + size, y + size), (120, 120, 120), 3)
        
        for i in range(5):
            offset = i * 2
            darkness = int(np.clip(120 + i * 10, 0, 255))
            cv2.rectangle(img, 
                        (x + offset, y + offset), 
                        (x + size - offset, y + size - offset),
                        (darkness, darkness, darkness), 1)
        
        bbox = [x, y, size, size]
        return img, bbox
    
    def generate_sample(self, img_size=(640, 640), material='metal'):
        """Generate one complete sample - SAFE VERSION."""
        
        # Generate base texture
        if material == 'plastic':
            img = self.generate_plastic_texture(img_size)
        else:
            img = self.generate_metal_texture(img_size)
        
        # Add lighting variations - SAFE
        if random.random() > 0.5:
            brightness = random.uniform(0.85, 1.15)
            img_float = img.astype(np.float32) * brightness
            img = np.clip(img_float, 0, 255).astype(np.uint8)
        
        defects = []
        num_defects = random.randint(2, 5)
        h, w = img_size
        
        for _ in range(num_defects):
            defect_type = random.randint(0, 3)
            
            margin = 80
            x = random.randint(margin, w - margin - 100)
            y = random.randint(margin, h - margin - 100)
            
            if defect_type == 0:  # Crack
                length = random.randint(30, 60)
                img, bbox = self.generate_fatigue_crack(img, x, y, length)
                class_id = 0
            
            elif defect_type == 1:  # Scratch
                length = random.randint(60, 120)
                scratch_type = random.choice(['linear', 'curved'])
                img, bbox = self.generate_scratch(img, x, y, length, scratch_type)
                class_id = 1
            
            elif defect_type == 2:  # Deformation
                size = random.randint(40, 80)
                deform_type = random.choice(['dent', 'bulge'])
                img, bbox = self.generate_deformation(img, x, y, size, deform_type)
                class_id = 2
            
            else:  # Missing
                size = random.randint(30, 70)
                img, bbox = self.generate_missing_component(img, x, y, size)
                class_id = 3
            
            # Convert to YOLO format - SAFE
            x_center = float(np.clip((bbox[0] + bbox[2]/2) / w, 0.0, 1.0))
            y_center = float(np.clip((bbox[1] + bbox[3]/2) / h, 0.0, 1.0))
            width = float(np.clip(bbox[2] / w, 0.0, 1.0))
            height = float(np.clip(bbox[3] / h, 0.0, 1.0))
            
            defects.append((class_id, x_center, y_center, width, height))
            
            # Update stats
            self.stats['defects_per_class'][['crack', 'scratch', 'deformation', 'missing'][class_id]] += 1
            self.stats['defect_sizes'].append(bbox[2] * bbox[3])
        
        self.stats['defects_per_image'].append(len(defects))
        
        return img, defects
    
    def generate_dataset(self, num_train=400, num_val=80, num_test=20):
        """Generate complete dataset."""
        
        print("="*70)
        print("GENERATING REALISTIC MANUFACTURING DEFECT DATASET".center(70))
        print("="*70)
        
        total = num_train + num_val + num_test
        print(f"\nTotal images to generate: {total}")
        print(f"  Training: {num_train}")
        print(f"  Validation: {num_val}")
        print(f"  Test: {num_test}\n")
        
        materials = ['metal', 'plastic', 'metal', 'metal']  # More metal
        
        # Generate training set
        print("Generating training set...")
        for i in range(num_train):
            material = random.choice(materials)
            img, defects = self.generate_sample(material=material)
            
            img_path = self.output_dir / 'images' / 'train' / f'img_{i:04d}.jpg'
            cv2.imwrite(str(img_path), img)
            
            label_path = self.output_dir / 'labels' / 'train' / f'img_{i:04d}.txt'
            with open(label_path, 'w') as f:
                for d in defects:
                    f.write(f"{d[0]} {d[1]:.6f} {d[2]:.6f} {d[3]:.6f} {d[4]:.6f}\n")
            
            if (i + 1) % 50 == 0:
                print(f"  Generated {i + 1}/{num_train} training images")
            
            self.stats['total_images'] += 1
        
        # Generate validation set
        print("\nGenerating validation set...")
        for i in range(num_val):
            material = random.choice(materials)
            img, defects = self.generate_sample(material=material)
            
            img_path = self.output_dir / 'images' / 'val' / f'img_{i:04d}.jpg'
            cv2.imwrite(str(img_path), img)
            
            label_path = self.output_dir / 'labels' / 'val' / f'img_{i:04d}.txt'
            with open(label_path, 'w') as f:
                for d in defects:
                    f.write(f"{d[0]} {d[1]:.6f} {d[2]:.6f} {d[3]:.6f} {d[4]:.6f}\n")
            
            self.stats['total_images'] += 1
        
        # Generate test set
        print("\nGenerating test set...")
        for i in range(num_test):
            material = random.choice(materials)
            img, defects = self.generate_sample(material=material)
            
            img_path = self.output_dir / 'images' / 'test' / f'img_{i:04d}.jpg'
            cv2.imwrite(str(img_path), img)
            
            label_path = self.output_dir / 'labels' / 'test' / f'img_{i:04d}.txt'
            with open(label_path, 'w') as f:
                for d in defects:
                    f.write(f"{d[0]} {d[1]:.6f} {d[2]:.6f} {d[3]:.6f} {d[4]:.6f}\n")
            
            self.stats['total_images'] += 1
        
        print("\n" + "="*70)
        print("DATASET GENERATION COMPLETE!".center(70))
        print("="*70)
        
        self.save_statistics()
        self.print_summary()
    
    def save_statistics(self):
        """Save statistics."""
        stats_file = self.output_dir / 'dataset_stats.json'
        
        stats_data = {
            'total_images': self.stats['total_images'],
            'defects_per_class': self.stats['defects_per_class'],
            'avg_defects_per_image': float(np.mean(self.stats['defects_per_image'])),
            'min_defects_per_image': int(min(self.stats['defects_per_image'])),
            'max_defects_per_image': int(max(self.stats['defects_per_image'])),
            'avg_defect_size': float(np.mean(self.stats['defect_sizes'])),
        }
        
        with open(stats_file, 'w') as f:
            json.dump(stats_data, f, indent=4)
        
        print(f"\nStatistics saved to: {stats_file}")
    
    def print_summary(self):
        """Print summary."""
        print("\nDATASET SUMMARY:")
        print("-" * 70)
        print(f"Total images: {self.stats['total_images']}")
        print(f"\nDefects by class:")
        for class_name, count in self.stats['defects_per_class'].items():
            total = sum(self.stats['defects_per_class'].values())
            pct = (count/total*100) if total > 0 else 0
            print(f"  {class_name:15s}: {count:4d} ({pct:.1f}%)")
        
        print(f"\nDefects per image:")
        print(f"  Average: {np.mean(self.stats['defects_per_image']):.2f}")
        print(f"  Min: {min(self.stats['defects_per_image'])}")
        print(f"  Max: {max(self.stats['defects_per_image'])}")
        
        print(f"\nAverage defect size: {np.mean(self.stats['defect_sizes']):.0f} pixels²")
        print("="*70)


if __name__ == "__main__":
    generator = RealisticDefectGenerator(output_dir="dataset")
    generator.generate_dataset(num_train=400, num_val=80, num_test=20)
    
    print("\n✓ Dataset ready for training!")
    print("  Location: dataset/")
    print("  Next step: python train_yolov11.py")
