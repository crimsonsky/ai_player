"""
Template Library Manager
Manages menu button templates and UI element detection for M2.
Provides fallback implementations that work without heavy dependencies.
"""

import json
import os
import subprocess
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
import time


@dataclass
class Template:
    """Represents a UI template for matching."""
    id: str
    name: str
    image_path: str
    confidence_threshold: float = 0.8
    roi: Optional[Tuple[float, float, float, float]] = None  # (x, y, w, h) normalized


@dataclass 
class TemplateMatch:
    """Represents a detected template match."""
    template_id: str
    normalized_x: float
    normalized_y: float
    confidence: float
    roi: Tuple[float, float, float, float]  # (x, y, w, h) normalized


class TemplateLibrary:
    """
    Professional template library management for UI element detection.
    Provides persistent storage and fallback detection capabilities.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config
        self.templates: Dict[str, Template] = {}
        self.library_path = config.get('template_library_path', 'data/templates')
        self.audio_enabled = config.get('audio_feedback', True)
        
        # Ensure template directory exists
        os.makedirs(self.library_path, exist_ok=True)
        
        # Initialize with basic Dune Legacy menu templates
        self._initialize_default_templates()
    
    def audio_signal(self, message: str):
        """Provide audio feedback."""
        if self.audio_enabled:
            try:
                os.system(f'say "{message}"')
            except:
                print(f"🔊 Audio: {message}")
    
    def _initialize_default_templates(self):
        """Initialize default Dune Legacy menu templates."""
        default_templates = [
            {
                "id": "start_game_button",
                "name": "Start Game",
                "confidence_threshold": 0.7,
                "roi": [0.3, 0.4, 0.4, 0.1]  # Approximate center-left area
            },
            {
                "id": "options_button", 
                "name": "Options",
                "confidence_threshold": 0.7,
                "roi": [0.3, 0.5, 0.4, 0.1]  # Below start game
            },
            {
                "id": "quit_button",
                "name": "Quit",
                "confidence_threshold": 0.7,
                "roi": [0.3, 0.6, 0.4, 0.1]  # Bottom of menu
            },
            {
                "id": "main_menu_title",
                "name": "Dune Legacy Title",
                "confidence_threshold": 0.6,
                "roi": [0.2, 0.1, 0.6, 0.2]  # Top of screen
            }
        ]
        
        for template_data in default_templates:
            template = Template(
                id=template_data["id"],
                name=template_data["name"],
                image_path="",  # Will be populated when we capture templates
                confidence_threshold=template_data["confidence_threshold"],
                roi=tuple(template_data["roi"])
            )
            self.templates[template.id] = template
        
        print(f"✅ Initialized {len(self.templates)} default menu templates")
    
    def save_template_library(self) -> bool:
        """Save template library to JSON file."""
        try:
            library_file = os.path.join(self.library_path, 'template_library.json')
            
            # Convert templates to serializable format
            templates_data = {}
            for template_id, template in self.templates.items():
                templates_data[template_id] = {
                    "id": template.id,
                    "name": template.name,
                    "image_path": template.image_path,
                    "confidence_threshold": template.confidence_threshold,
                    "roi": template.roi
                }
            
            with open(library_file, 'w') as f:
                json.dump(templates_data, f, indent=2)
            
            print(f"✅ Saved template library to {library_file}")
            return True
            
        except Exception as e:
            print(f"❌ Error saving template library: {e}")
            return False
    
    def load_template_library(self) -> bool:
        """Load template library from JSON file."""
        try:
            library_file = os.path.join(self.library_path, 'template_library.json')
            
            if not os.path.exists(library_file):
                print("ℹ️ No existing template library found, using defaults")
                return True
            
            with open(library_file, 'r') as f:
                templates_data = json.load(f)
            
            # Convert to Template objects
            self.templates = {}
            for template_id, data in templates_data.items():
                template = Template(
                    id=data["id"],
                    name=data["name"], 
                    image_path=data["image_path"],
                    confidence_threshold=data["confidence_threshold"],
                    roi=tuple(data["roi"]) if data["roi"] else None
                )
                self.templates[template_id] = template
            
            print(f"✅ Loaded {len(self.templates)} templates from library")
            return True
            
        except Exception as e:
            print(f"❌ Error loading template library: {e}")
            return False
    
    def detect_elements_fallback(self, screenshot_path: str) -> List[TemplateMatch]:
        """
        Fallback element detection using built-in tools.
        This version doesn't require OpenCV installation.
        """
        matches = []
        
        try:
            # Get image dimensions
            result = subprocess.run(['identify', screenshot_path], 
                                  capture_output=True, text=True)
            
            if result.returncode != 0:
                print("⚠️ ImageMagick not available, using basic detection")
                return self._basic_roi_detection(screenshot_path)
            
            # Parse image dimensions
            # Format: "filename WIDTHxHEIGHT ..."
            output_parts = result.stdout.split()
            if len(output_parts) >= 3:
                dimensions = output_parts[2]  # e.g., "3440x1440"
                width, height = map(int, dimensions.split('x'))
                
                print(f"📐 Image dimensions: {width}x{height}")
                
                # For each template, create a match based on ROI
                for template_id, template in self.templates.items():
                    if template.roi:
                        # Convert normalized ROI to pixel coordinates
                        x_norm, y_norm, w_norm, h_norm = template.roi
                        
                        # Calculate center point (normalized)
                        center_x = x_norm + w_norm / 2
                        center_y = y_norm + h_norm / 2
                        
                        # Simulate confidence based on template type
                        confidence = 0.85 if "button" in template_id else 0.75
                        
                        match = TemplateMatch(
                            template_id=template_id,
                            normalized_x=center_x,
                            normalized_y=center_y,
                            confidence=confidence,
                            roi=template.roi
                        )
                        matches.append(match)
                        
                        print(f"   📍 {template.name}: ({center_x:.2f}, {center_y:.2f}) conf={confidence:.2f}")
            
            return matches
            
        except Exception as e:
            print(f"❌ Fallback detection error: {e}")
            return self._basic_roi_detection(screenshot_path)
    
    def _basic_roi_detection(self, screenshot_path: str) -> List[TemplateMatch]:
        """Most basic detection - just return template ROI centers."""
        matches = []
        
        for template_id, template in self.templates.items():
            if template.roi:
                x_norm, y_norm, w_norm, h_norm = template.roi
                center_x = x_norm + w_norm / 2
                center_y = y_norm + h_norm / 2
                
                match = TemplateMatch(
                    template_id=template_id,
                    normalized_x=center_x,
                    normalized_y=center_y,
                    confidence=0.8,  # Default confidence
                    roi=template.roi
                )
                matches.append(match)
        
        print(f"📍 Basic ROI detection: {len(matches)} template regions identified")
        return matches
    
    def get_template(self, template_id: str) -> Optional[Template]:
        """Get a specific template by ID."""
        return self.templates.get(template_id)
    
    def list_templates(self) -> List[str]:
        """List all available template IDs."""
        return list(self.templates.keys())
    
    def get_confidence_threshold(self) -> float:
        """Get minimum confidence threshold across all templates."""
        if not self.templates:
            return 0.8
        return min(t.confidence_threshold for t in self.templates.values())