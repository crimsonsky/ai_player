"""
YOLO DETECTION ENGINE - Module 3B/C: YOLOv8 Object Detection & Semantic Mapping
Real-time AI Vision Pipeline for Dune Legacy Game Interface Recognition

This module implements the core AI perception engine using YOLOv8 for object detection,
replacing failed OCR and template matching systems with learning-based visual recognition.

Pipeline Flow:
M3A (screen_capture.py) → M3B (YOLOv8 Detection) → M3C (Semantic Mapping) → M3D (semantic_map.py)

Features:
- YOLOv8 model loading and inference pipeline
- Real-time object detection with confidence scoring
- Semantic mapping from raw detections to hierarchical game state
- PyTorch MPS acceleration support for Apple Silicon
- Integration with Agent B's MLOps data pipeline
- Performance monitoring and optimization

Author: Agent A
Version: 1.0
Compliance: AIP-SDS-V2.3, MODULE 3B/C specifications
Integration: Agent B MLOps foundation (ExperienceReplayBuffer, DLAT)
"""

import torch
import torchvision.transforms as transforms
from PIL import Image
import numpy as np
from typing import List, Dict, Tuple, Optional, Any
import logging
import time
from pathlib import Path
import json

# Import our M3D semantic mapping structures
from .semantic_map import SemanticMap, DetectedElement, ElementLabel, ScreenContext

# MLOps integration with Agent B's infrastructure
try:
    from ..mlops.data_manager import ExperienceReplayBuffer
    MLOPS_AVAILABLE = True
except ImportError:
    MLOPS_AVAILABLE = False
    logging.warning("MLOps infrastructure not available - running in standalone mode")


class YOLODetectionEngine:
    """
    Core YOLOv8 detection engine for real-time game interface recognition.
    
    Replaces deprecated OCR/template matching with learning-based AI perception.
    Integrates with Agent B's MLOps pipeline for continuous learning.
    """
    
    def __init__(self, model_path: Optional[str] = None, use_mps: bool = True):
        """
        Initialize YOLOv8 detection engine.
        
        Args:
            model_path: Path to trained YOLOv8 model (None for dummy model)
            use_mps: Enable PyTorch Metal Performance Shaders on Apple Silicon
        """
        self.logger = logging.getLogger(__name__)
        self.model_path = model_path
        self.model = None
        self.device = self._setup_device(use_mps)
        self.using_real_yolo = False  # Track if using real YOLOv8 or dummy model
        self.performance_metrics = {
            'total_inferences': 0,
            'average_inference_time': 0.0,
            'last_inference_time': 0.0
        }
        
        # Initialize model
        self._load_model()
        
        # MLOps integration for experience replay
        if MLOPS_AVAILABLE:
            self.experience_buffer = ExperienceReplayBuffer(capacity=50000)
            self.logger.info("MLOps integration active - experience replay enabled")
        
        self.logger.info(f"YOLOv8 Detection Engine initialized - Device: {self.device}")
    
    def _setup_device(self, use_mps: bool) -> torch.device:
        """
        Configure PyTorch device with optimal acceleration for Intel processors.
        
        Returns:
            torch.device: Optimal device for inference
        """
        if torch.cuda.is_available():
            device = torch.device("cuda")
            self.logger.info("CUDA acceleration enabled for Intel processor")
        else:
            device = torch.device("cpu")
            self.logger.info("Using CPU inference on Intel processor - optimized for x86_64")
        
        # MPS is not available on Intel processors
        if use_mps:
            self.logger.info("MPS acceleration not available on Intel processors, using CUDA/CPU")
        
        return device
    
    def _load_model(self):
        """
        Load YOLOv8 model for inference.
        
        Uses dummy model if no trained model available - ready for DLAT integration.
        """
        if self.model_path and Path(self.model_path).exists():
            try:
                # Load trained YOLOv8 model (when available from DLAT pipeline)
                self.model = torch.jit.load(self.model_path, map_location=self.device)
                self.model.eval()
                self.logger.info(f"Loaded trained YOLOv8 model from {self.model_path}")
            except Exception as e:
                self.logger.error(f"Failed to load model from {self.model_path}: {e}")
                self._load_dummy_model()
        else:
            self._load_dummy_model()
    
    def _load_dummy_model(self):
        """
        Load dummy model for development and testing.
        
        Placeholder until Agent B's DLAT provides trained YOLOv8 model.
        """
        try:
            # Try to load pre-trained YOLOv8 for basic object detection
            from ultralytics import YOLO
            self.model = YOLO('yolov8n.pt')  # Nano model for Intel CPU performance
            self.model.to(self.device)
            self.logger.info("Loaded YOLOv8 nano model - Intel CPU optimized")
            self.using_real_yolo = True
        except Exception as e:
            # Fallback to dummy model
            class DummyYOLOModel:
                def __call__(self, x):
                    # Return dummy detections for testing
                    return [{
                        'boxes': torch.tensor([[100, 100, 200, 150], [300, 200, 450, 250]]),
                        'labels': torch.tensor([0, 1]),  # Class IDs
                        'scores': torch.tensor([0.95, 0.87])
                    }]
            
            self.model = DummyYOLOModel()
            self.using_real_yolo = False
            self.logger.info(f"Loaded dummy YOLO model (YOLOv8 failed: {e}) - ready for DLAT training integration")
    
    def run_yolo_inference(self, pil_image: Image.Image) -> Dict[str, Any]:
        """
        Core inference function - accepts PIL Image from M3A screen capture.
        
        Args:
            pil_image: PIL Image from screen_capture.py (M3A)
            
        Returns:
            Dict containing raw detection results:
            - boxes: Bounding box coordinates
            - labels: Class ID predictions  
            - scores: Confidence scores
            - inference_time: Performance metric
        """
        start_time = time.time()
        
        try:
            if self.using_real_yolo:
                # Real YOLOv8 inference using Ultralytics
                results = self.model(pil_image, verbose=False)
                
                # Extract detection data from Ultralytics results
                if results and len(results) > 0:
                    result = results[0]
                    boxes = result.boxes.xyxy.cpu() if result.boxes is not None else torch.empty((0, 4))
                    labels = result.boxes.cls.cpu() if result.boxes is not None else torch.empty((0,))
                    scores = result.boxes.conf.cpu() if result.boxes is not None else torch.empty((0,))
                    
                    detections = [{
                        'boxes': boxes,
                        'labels': labels,
                        'scores': scores
                    }]
                else:
                    detections = []
            else:
                # Dummy model processing
                # Preprocessing for YOLOv8 input
                transform = transforms.Compose([
                    transforms.Resize((640, 640)),  # YOLOv8 standard input size
                    transforms.ToTensor(),
                    transforms.Normalize(mean=[0.485, 0.456, 0.406], 
                                       std=[0.229, 0.224, 0.225])
                ])
                
                # Convert PIL to tensor
                input_tensor = transform(pil_image).unsqueeze(0).to(self.device)
                
                # YOLOv8 inference
                with torch.no_grad():
                    detections = self.model(input_tensor)
            
            # Process raw output
            if isinstance(detections, list) and len(detections) > 0:
                detection = detections[0]
                raw_results = {
                    'boxes': detection['boxes'].cpu(),
                    'labels': detection['labels'].cpu(), 
                    'scores': detection['scores'].cpu(),
                    'image_size': pil_image.size,
                    'inference_time': time.time() - start_time
                }
            else:
                # No detections
                raw_results = {
                    'boxes': torch.empty((0, 4)),
                    'labels': torch.empty((0,)),
                    'scores': torch.empty((0,)),
                    'image_size': pil_image.size,
                    'inference_time': time.time() - start_time
                }
            
            # Update performance metrics
            self._update_performance_metrics(raw_results['inference_time'])
            
            self.logger.debug(f"YOLOv8 inference completed in {raw_results['inference_time']:.3f}s "
                            f"- Found {len(raw_results['boxes'])} objects")
            
            return raw_results
            
        except Exception as e:
            self.logger.error(f"YOLOv8 inference failed: {e}")
            return {
                'boxes': torch.empty((0, 4)),
                'labels': torch.empty((0,)),
                'scores': torch.empty((0,)),
                'image_size': pil_image.size,
                'inference_time': time.time() - start_time,
                'error': str(e)
            }
    
    def process_detections(self, raw_yolo_results: Dict[str, Any], 
                          screen_image: Image.Image) -> SemanticMap:
        """
        Module 3C: Convert raw YOLO output to hierarchical SemanticMap.
        
        This is the core semantic mapping function that replaces OCR with
        AI-based visual interpretation of game interface elements.
        
        Args:
            raw_yolo_results: Raw detection output from run_yolo_inference()
            screen_image: Original screen capture for context
            
        Returns:
            SemanticMap: Hierarchical game state representation
        """
        try:
            # Initialize semantic map with screen context
            semantic_map = SemanticMap(
                timestamp=time.time(),
                screen_context=ScreenContext.UNKNOWN,  # Will be determined by context analysis
                elements=[],  # Will be populated below
                screen_resolution=screen_image.size,
                yolo_model_version="YOLOv8n-Intel"
            )
            
            boxes = raw_yolo_results['boxes']
            labels = raw_yolo_results['labels']  
            scores = raw_yolo_results['scores']
            
            # Convert each detection to DetectedElement
            for i in range(len(boxes)):
                box = boxes[i]
                class_id = int(labels[i])
                confidence = float(scores[i])
                
                # Apply confidence threshold
                if confidence < 0.5:
                    continue
                
                # Convert box coordinates to screen coordinates
                # (Adjust from YOLOv8 640x640 back to original screen size)
                img_width, img_height = screen_image.size
                x1 = int(box[0] * img_width / 640)
                y1 = int(box[1] * img_height / 640)
                x2 = int(box[2] * img_width / 640)  
                y2 = int(box[3] * img_height / 640)
                
                # Convert each detection to DetectedElement
                element_label, semantic_value = self._interpret_detection(
                    class_id, confidence, (x1, y1, x2, y2), screen_image
                )
                
                # Create DetectedElement using correct semantic_map structure
                detected_element = DetectedElement(
                    label=element_label,
                    semantic_value=semantic_value,
                    bbox=[x1/img_width, y1/img_height, (x2-x1)/img_width, (y2-y1)/img_height],  # Normalized coordinates
                    confidence=confidence,
                    attributes={'detection_method': 'YOLOv8', 'class_id': class_id}
                )
                
                # Add to semantic map
                semantic_map.add_element(detected_element)
            
            # Store experience for MLOps pipeline (Agent B integration)
            if MLOPS_AVAILABLE and hasattr(self, 'experience_buffer'):
                experience = {
                    'screen_capture': np.array(screen_image),
                    'detections': len(boxes),
                    'confidence_avg': float(scores.mean()) if len(scores) > 0 else 0.0,
                    'timestamp': time.time()
                }
                # Note: Full SARSA integration will be implemented in M4/M5
            
            self.logger.info(f"Processed {len(boxes)} detections into semantic map "
                           f"with {len(semantic_map.elements)} valid elements")
            
            return semantic_map
            
        except Exception as e:
            self.logger.error(f"Semantic mapping failed: {e}")
            # Return empty semantic map on error
            return SemanticMap(
                timestamp=time.time(),
                screen_context=ScreenContext.UNKNOWN,
                elements=[],
                screen_resolution=screen_image.size
            )
    
    def _interpret_detection(self, class_id: int, confidence: float, 
                           bbox: Tuple[int, int, int, int], 
                           image: Image.Image) -> Tuple[ElementLabel, str]:
        """
        Semantic interpretation of YOLOv8 detections into game-specific meaning.
        
        This replaces OCR text extraction with AI visual interpretation.
        
        Args:
            class_id: YOLOv8 predicted class
            confidence: Detection confidence score
            bbox: Bounding box coordinates
            image: Source image for context
            
        Returns:
            Tuple of (ElementLabel, semantic_value)
        """
        # Placeholder class mapping - will be replaced with DLAT-trained classes
        class_mapping = {
            0: (ElementLabel.BUTTON, "menu_button"),
            1: (ElementLabel.TEXT_LABEL, "game_title"),
            2: (ElementLabel.RESOURCE_COUNTER, "resource_count"),
            3: (ElementLabel.UNIT_ICON, "unit_icon"),
            4: (ElementLabel.MENU_TITLE, "submenu"),
            5: (ElementLabel.VERSION_INFO, "version_number")
        }
        
        if class_id in class_mapping:
            element_label, base_semantic = class_mapping[class_id]
            
            # Enhanced semantic interpretation based on position/context
            semantic_value = self._enhance_semantic_value(
                base_semantic, bbox, image, confidence
            )
            
            return element_label, semantic_value
        else:
            # Unknown class - default classification
            return ElementLabel.TEXT_LABEL, f"unknown_class_{class_id}"
    
    def _enhance_semantic_value(self, base_semantic: str, bbox: Tuple[int, int, int, int],
                               image: Image.Image, confidence: float) -> str:
        """
        Enhance semantic interpretation using positional and contextual analysis.
        
        This is where AI visual understanding replaces OCR text extraction.
        """
        x1, y1, x2, y2 = bbox
        width, height = image.size
        
        # Position-based semantic enhancement
        if y1 < height * 0.2:  # Top area
            if "button" in base_semantic:
                return "header_menu_button"
            elif "text" in base_semantic:
                return "title_text"
        elif y1 > height * 0.8:  # Bottom area
            if "button" in base_semantic:
                return "footer_action_button"
        elif x1 < width * 0.2:  # Left side
            if base_semantic == "resource_count":
                return "left_resource_display"
        
        # Confidence-based interpretation
        if confidence > 0.9:
            return f"high_confidence_{base_semantic}"
        elif confidence < 0.7:
            return f"uncertain_{base_semantic}"
        
        return base_semantic
    
    def _update_performance_metrics(self, inference_time: float):
        """Update performance tracking for optimization."""
        self.performance_metrics['total_inferences'] += 1
        self.performance_metrics['last_inference_time'] = inference_time
        
        # Running average calculation
        total = self.performance_metrics['total_inferences']
        current_avg = self.performance_metrics['average_inference_time']
        self.performance_metrics['average_inference_time'] = (
            (current_avg * (total - 1) + inference_time) / total
        )
    
    def get_performance_stats(self) -> Dict[str, float]:
        """
        Get current performance statistics for monitoring.
        
        Returns:
            Dict with inference timing and throughput metrics
        """
        return {
            **self.performance_metrics,
            'target_fps': 30.0,  # Target for real-time gameplay
            'current_fps': 1.0 / self.performance_metrics['average_inference_time'] 
                          if self.performance_metrics['average_inference_time'] > 0 else 0,
            'cuda_enabled': self.device.type == 'cuda',
            'processor_type': 'Intel x86_64'
        }


def create_detection_engine(model_path: Optional[str] = None) -> YOLODetectionEngine:
    """
    Factory function for creating YOLOv8 detection engine.
    
    Args:
        model_path: Optional path to trained model
        
    Returns:
        Configured YOLODetectionEngine instance
    """
    return YOLODetectionEngine(model_path=model_path, use_mps=True)


# Integration function for complete M3 pipeline
def run_complete_perception_pipeline(screen_image: Image.Image, 
                                   detection_engine: YOLODetectionEngine) -> SemanticMap:
    """
    Complete M3 perception pipeline: Screen Capture → Detection → Semantic Mapping.
    
    Args:
        screen_image: PIL Image from M3A screen capture
        detection_engine: Configured YOLODetectionEngine
        
    Returns:
        SemanticMap: Final hierarchical game state representation
    """
    # M3B: YOLOv8 object detection
    raw_detections = detection_engine.run_yolo_inference(screen_image)
    
    # M3C: Semantic mapping and interpretation  
    semantic_map = detection_engine.process_detections(raw_detections, screen_image)
    
    return semantic_map