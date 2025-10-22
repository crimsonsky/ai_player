#!/usr/bin/env python3
"""
Enhanced Button Detection for M2 Functional Validation
Advanced detection algorithms for various button types and screen layouts
"""

import cv2
import numpy as np
import subprocess
import time

class EnhancedButtonDetector:
    """Advanced button detection for functional validation"""
    
    def __init__(self):
        self.debug_output = True
        
    def detect_text_regions(self, screenshot):
        """Detect regions that contain text (potential buttons)"""
        gray = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)
        
        # Multiple text detection approaches
        detected_regions = []
        
        # Method 1: MSER (Maximally Stable Extremal Regions) for text
        mser = cv2.MSER_create()
        regions, _ = mser.detectRegions(gray)
        
        for region in regions:
            x, y, w, h = cv2.boundingRect(region.reshape(-1, 1, 2))
            
            # Filter for button-like text regions
            if (w > 60 and w < 400 and h > 20 and h < 100 and 
                w > h * 1.5 and cv2.contourArea(region) > 500):
                
                center_x = x + w // 2
                center_y = y + h // 2
                detected_regions.append({
                    'method': 'MSER',
                    'center': (center_x, center_y),
                    'bounds': (x, y, w, h),
                    'area': cv2.contourArea(region)
                })
        
        # Method 2: Template matching for common button patterns
        button_templates = self.create_generic_templates()
        
        for template_name, template in button_templates.items():
            result = cv2.matchTemplate(gray, template, cv2.TM_CCOEFF_NORMED)
            locations = np.where(result >= 0.6)  # Lower threshold for generic templates
            
            for pt in zip(*locations[::-1]):
                x, y = pt
                w, h = template.shape[1], template.shape[0]
                center_x = x + w // 2
                center_y = y + h // 2
                
                confidence = result[y, x]
                
                detected_regions.append({
                    'method': f'Template_{template_name}',
                    'center': (center_x, center_y),
                    'bounds': (x, y, w, h),
                    'confidence': confidence
                })
        
        # Method 3: Contour-based detection with relaxed parameters
        edges = cv2.Canny(gray, 30, 100)
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            
            # More relaxed button detection
            if (w > 40 and w < 500 and h > 15 and h < 120 and 
                cv2.contourArea(contour) > 200):
                
                center_x = x + w // 2
                center_y = y + h // 2
                detected_regions.append({
                    'method': 'Contour',
                    'center': (center_x, center_y),
                    'bounds': (x, y, w, h),
                    'area': cv2.contourArea(contour)
                })
        
        return detected_regions
    
    def create_generic_templates(self):
        """Create generic button templates for common UI patterns"""
        templates = {}
        
        # Generic rectangular button template
        rect_template = np.zeros((40, 120), dtype=np.uint8)
        cv2.rectangle(rect_template, (5, 5), (115, 35), 255, 2)
        templates['rectangle'] = rect_template
        
        # Generic rounded button template  
        rounded_template = np.zeros((35, 100), dtype=np.uint8)
        cv2.ellipse(rounded_template, (50, 17), (45, 15), 0, 0, 360, 255, 2)
        templates['rounded'] = rounded_template
        
        return templates
    
    def cluster_and_filter_detections(self, detections):
        """Remove duplicate detections and cluster nearby regions"""
        if not detections:
            return []
        
        # Sort by position for clustering
        detections.sort(key=lambda d: (d['center'][1], d['center'][0]))
        
        clustered = []
        merge_distance = 50  # Pixels
        
        for detection in detections:
            merged = False
            
            for cluster in clustered:
                center_dist = np.sqrt(
                    (detection['center'][0] - cluster['center'][0])**2 + 
                    (detection['center'][1] - cluster['center'][1])**2
                )
                
                if center_dist < merge_distance:
                    # Merge with existing cluster - keep the one with better bounds
                    if detection['bounds'][2] * detection['bounds'][3] > cluster['bounds'][2] * cluster['bounds'][3]:
                        cluster.update(detection)
                    merged = True
                    break
            
            if not merged:
                clustered.append(detection)
        
        # Sort by y-coordinate (top to bottom)
        clustered.sort(key=lambda d: d['center'][1])
        
        return clustered
    
    def analyze_screenshot_with_debug(self, screenshot_path):
        """Analyze screenshot with comprehensive debugging"""
        print(f"🔍 ENHANCED ANALYSIS: {screenshot_path}")
        
        img = cv2.imread(screenshot_path)
        if img is None:
            print("❌ Failed to read screenshot")
            return []
        
        print(f"📊 Image dimensions: {img.shape}")
        
        # Detect all potential button regions
        all_detections = self.detect_text_regions(img)
        
        print(f"🎯 Raw detections: {len(all_detections)}")
        for i, detection in enumerate(all_detections[:10]):  # Show first 10
            method = detection.get('method', 'Unknown')
            center = detection['center']
            bounds = detection['bounds']
            print(f"   {i+1:2d}. {method:12s}: Center{center} | Bounds{bounds}")
        
        # Cluster and filter
        filtered_detections = self.cluster_and_filter_detections(all_detections)
        
        print(f"✅ Filtered detections: {len(filtered_detections)}")
        
        # Create debug image
        debug_img = img.copy()
        for i, detection in enumerate(filtered_detections):
            center = detection['center']
            bounds = detection['bounds']
            x, y, w, h = bounds
            
            # Draw bounding box
            cv2.rectangle(debug_img, (x, y), (x + w, y + h), (0, 255, 0), 2)
            
            # Draw center point
            cv2.circle(debug_img, center, 5, (255, 0, 0), -1)
            
            # Label
            label = f"Btn_{i+1}"
            cv2.putText(debug_img, label, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
        
        debug_path = screenshot_path.replace('.png', '_debug.png')
        cv2.imwrite(debug_path, debug_img)
        print(f"🖼️ Debug visualization saved: {debug_path}")
        
        return filtered_detections

def main():
    """Test enhanced detection on new screen"""
    detector = EnhancedButtonDetector()
    
    # Analyze the new submenu screenshot
    new_screen_path = "/tmp/functional_test_new_submenu.png"
    
    if not os.path.exists(new_screen_path):
        print(f"❌ Screenshot not found: {new_screen_path}")
        return
    
    detections = detector.analyze_screenshot_with_debug(new_screen_path)
    
    if detections:
        print("\n🎉 ENHANCED DETECTION SUCCESS!")
        print(f"✅ Found {len(detections)} potential buttons")
        
        for i, detection in enumerate(detections):
            center = detection['center']
            bounds = detection['bounds']
            method = detection.get('method', 'Unknown')
            print(f"   Button_{i+1}: {center} | Method: {method} | Size: {bounds[2]}x{bounds[3]}")
    else:
        print("\n❌ No buttons detected even with enhanced algorithms")
        print("   The new screen may not contain traditional button elements")
        print("   Manual inspection of the screenshot may be required")

if __name__ == "__main__":
    import os
    main()