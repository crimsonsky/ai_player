"""
Module 3D: Hierarchical Semantic Graph Definition - AIP-SDS-V2.3
Learning-Based Perception Stream Engine Data Structures

Defines the core output structure for YOLOv8 model integration with
hierarchical semantic organization for M4 State Representation.

MANDATE: Structured data schema for AI vision model outputs and 
semantic map generation per AIP-SDS-V2.3 specification.
"""

import time
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Union
from enum import Enum
import json


class ScreenContext(Enum):
    """
    Enumeration of possible screen contexts for semantic classification.
    
    Used to categorize the current game state for context-aware processing.
    """
    MAIN_MENU = "Main Menu"
    IN_GAME = "In Game" 
    LOADING = "Loading"
    SETTINGS = "Settings"
    GAME_OVER = "Game Over"
    PAUSED = "Paused"
    UNKNOWN = "Unknown"


class ElementLabel(Enum):
    """
    Enumeration of detectable game element types for YOLO classification.
    
    Categories aligned with game interface components and units.
    """
    # UI Elements
    BUTTON = "Button"
    TEXT_LABEL = "TextLabel"
    RESOURCE_COUNTER = "ResourceCounter"
    MENU_TITLE = "MenuTitle"
    VERSION_INFO = "VersionInfo"
    
    # Game Elements (for future expansion)
    UNIT_ICON = "UnitIcon"
    BUILDING_ICON = "BuildingIcon"
    MINIMAP = "Minimap"
    HEALTH_BAR = "HealthBar"
    
    # Interactive Elements
    INPUT_FIELD = "InputField"
    CHECKBOX = "Checkbox"
    SLIDER = "Slider"
    
    # Dynamic Content
    NOTIFICATION = "Notification"
    TOOLTIP = "Tooltip"
    CONTEXT_MENU = "ContextMenu"


@dataclass
class DetectedElement:
    """
    Individual detected object within the semantic map.
    
    Represents a single game element detected by the YOLOv8 model
    with all necessary information for state representation.
    """
    
    # Core identification
    label: ElementLabel
    semantic_value: str  # Interpreted text/value (e.g., "Single Player", "450")
    
    # Spatial information
    bbox: List[float]  # Normalized bounding box [x, y, w, h] (0.0-1.0 range)
    
    # Detection metadata
    confidence: float  # Detection confidence score from YOLO (0.0-1.0)
    
    # Additional attributes
    attributes: Dict[str, Any] = field(default_factory=dict)
    
    # Temporal tracking
    detection_time: float = field(default_factory=time.time)
    
    def __post_init__(self):
        """Validate element data after initialization."""
        # Validate bounding box format
        if len(self.bbox) != 4:
            raise ValueError("bbox must contain exactly 4 values [x, y, w, h]")
        
        # Validate normalized coordinates
        if not all(0.0 <= coord <= 1.0 for coord in self.bbox):
            raise ValueError("bbox coordinates must be normalized (0.0-1.0 range)")
        
        # Validate confidence range
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("confidence must be in range 0.0-1.0")
    
    def get_absolute_bbox(self, screen_width: int, screen_height: int) -> List[int]:
        """
        Convert normalized bbox to absolute pixel coordinates.
        
        Args:
            screen_width: Screen width in pixels
            screen_height: Screen height in pixels
            
        Returns:
            Absolute bounding box [x, y, w, h] in pixels
        """
        x, y, w, h = self.bbox
        return [
            int(x * screen_width),
            int(y * screen_height),
            int(w * screen_width),
            int(h * screen_height)
        ]
    
    def get_center_point(self) -> tuple[float, float]:
        """
        Get normalized center point of the detected element.
        
        Returns:
            Tuple of (center_x, center_y) in normalized coordinates
        """
        x, y, w, h = self.bbox
        return (x + w / 2, y + h / 2)
    
    def is_clickable(self) -> bool:
        """
        Determine if element is likely clickable based on its label.
        
        Returns:
            True if element is typically interactive
        """
        clickable_labels = {
            ElementLabel.BUTTON,
            ElementLabel.INPUT_FIELD,
            ElementLabel.CHECKBOX,
            ElementLabel.SLIDER,
            ElementLabel.UNIT_ICON,
            ElementLabel.BUILDING_ICON
        }
        return self.label in clickable_labels


@dataclass
class SemanticMap:
    """
    Hierarchical Semantic Graph for Learning-Based Perception Engine.
    
    Primary data structure for M3 output, organized hierarchically
    for efficient M4 State Representation processing.
    """
    
    # Temporal information
    timestamp: float
    
    # Context classification
    screen_context: ScreenContext
    
    # Detected elements list
    elements: List[DetectedElement]
    
    # Capture metadata
    screen_resolution: tuple[int, int] = (0, 0)  # (width, height)
    capture_source: str = "game_window"  # "game_window" or "full_screen"
    
    # Processing metadata
    processing_time_ms: float = 0.0
    yolo_model_version: str = "unknown"
    
    # Additional context
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Validate semantic map data after initialization."""
        if not isinstance(self.timestamp, (int, float)):
            raise ValueError("timestamp must be numeric")
        
        if not isinstance(self.elements, list):
            raise ValueError("elements must be a list")
        
        # Validate all elements
        for element in self.elements:
            if not isinstance(element, DetectedElement):
                raise ValueError("all elements must be DetectedElement instances")
    
    def get_elements_by_label(self, label: ElementLabel) -> List[DetectedElement]:
        """
        Filter elements by specific label type.
        
        Args:
            label: ElementLabel to filter by
            
        Returns:
            List of elements matching the label
        """
        return [elem for elem in self.elements if elem.label == label]
    
    def get_clickable_elements(self) -> List[DetectedElement]:
        """
        Get all elements that are likely clickable/interactive.
        
        Returns:
            List of interactive elements
        """
        return [elem for elem in self.elements if elem.is_clickable()]
    
    def get_high_confidence_elements(self, threshold: float = 0.8) -> List[DetectedElement]:
        """
        Filter elements by confidence threshold.
        
        Args:
            threshold: Minimum confidence score (default 0.8)
            
        Returns:
            List of high-confidence elements
        """
        return [elem for elem in self.elements if elem.confidence >= threshold]
    
    def get_element_count_by_label(self) -> Dict[ElementLabel, int]:
        """
        Get count of elements grouped by label.
        
        Returns:
            Dictionary mapping labels to counts
        """
        counts = {}
        for element in self.elements:
            counts[element.label] = counts.get(element.label, 0) + 1
        return counts
    
    def find_element_by_semantic_value(self, value: str, case_sensitive: bool = False) -> List[DetectedElement]:
        """
        Find elements by their semantic value (text content).
        
        Args:
            value: Semantic value to search for
            case_sensitive: Whether to perform case-sensitive search
            
        Returns:
            List of matching elements
        """
        if case_sensitive:
            return [elem for elem in self.elements if elem.semantic_value == value]
        else:
            value_lower = value.lower()
            return [elem for elem in self.elements if elem.semantic_value.lower() == value_lower]
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert semantic map to dictionary for JSON serialization.
        
        Returns:
            Dictionary representation of semantic map
        """
        return {
            'timestamp': self.timestamp,
            'screen_context': self.screen_context.value,
            'screen_resolution': list(self.screen_resolution),
            'capture_source': self.capture_source,
            'processing_time_ms': self.processing_time_ms,
            'yolo_model_version': self.yolo_model_version,
            'elements': [
                {
                    'label': elem.label.value,
                    'semantic_value': elem.semantic_value,
                    'bbox': elem.bbox,
                    'confidence': elem.confidence,
                    'attributes': elem.attributes,
                    'detection_time': elem.detection_time,
                    'center_point': elem.get_center_point(),
                    'is_clickable': elem.is_clickable()
                }
                for elem in self.elements
            ],
            'metadata': self.metadata,
            'summary': {
                'total_elements': len(self.elements),
                'high_confidence_count': len(self.get_high_confidence_elements()),
                'clickable_count': len(self.get_clickable_elements()),
                'element_counts_by_label': {
                    label.value: count 
                    for label, count in self.get_element_count_by_label().items()
                }
            }
        }
    
    def to_json(self, indent: int = 2) -> str:
        """
        Convert semantic map to JSON string.
        
        Args:
            indent: JSON indentation level
            
        Returns:
            JSON string representation
        """
        return json.dumps(self.to_dict(), indent=indent)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SemanticMap':
        """
        Create SemanticMap from dictionary data.
        
        Args:
            data: Dictionary containing semantic map data
            
        Returns:
            SemanticMap instance
        """
        # Convert elements list
        elements = []
        for elem_data in data.get('elements', []):
            element = DetectedElement(
                label=ElementLabel(elem_data['label']),
                semantic_value=elem_data['semantic_value'],
                bbox=elem_data['bbox'],
                confidence=elem_data['confidence'],
                attributes=elem_data.get('attributes', {}),
                detection_time=elem_data.get('detection_time', time.time())
            )
            elements.append(element)
        
        return cls(
            timestamp=data['timestamp'],
            screen_context=ScreenContext(data['screen_context']),
            elements=elements,
            screen_resolution=tuple(data.get('screen_resolution', (0, 0))),
            capture_source=data.get('capture_source', 'unknown'),
            processing_time_ms=data.get('processing_time_ms', 0.0),
            yolo_model_version=data.get('yolo_model_version', 'unknown'),
            metadata=data.get('metadata', {})
        )


def create_semantic_map(
    screen_context: ScreenContext,
    elements: List[DetectedElement] = None,
    **kwargs
) -> SemanticMap:
    """
    Factory function to create semantic map with current timestamp.
    
    Args:
        screen_context: Current screen context classification
        elements: List of detected elements (default empty)
        **kwargs: Additional semantic map parameters
        
    Returns:
        SemanticMap instance
    """
    return SemanticMap(
        timestamp=time.time(),
        screen_context=screen_context,
        elements=elements or [],
        **kwargs
    )


def create_detected_element(
    label: Union[ElementLabel, str],
    semantic_value: str,
    bbox: List[float],
    confidence: float,
    **kwargs
) -> DetectedElement:
    """
    Factory function to create detected element with validation.
    
    Args:
        label: Element label (enum or string)
        semantic_value: Interpreted text/value
        bbox: Normalized bounding box [x, y, w, h]
        confidence: Detection confidence score
        **kwargs: Additional element parameters
        
    Returns:
        DetectedElement instance
    """
    if isinstance(label, str):
        label = ElementLabel(label)
    
    return DetectedElement(
        label=label,
        semantic_value=semantic_value,
        bbox=bbox,
        confidence=confidence,
        **kwargs
    )


# Validation and testing functions
def validate_semantic_map_structure():
    """Validate semantic map data structure functionality."""
    try:
        print("🧪 Testing semantic map data structures...")
        
        # Create test elements
        button_element = create_detected_element(
            label=ElementLabel.BUTTON,
            semantic_value="Single Player",
            bbox=[0.3, 0.2, 0.2, 0.1],
            confidence=0.95
        )
        
        title_element = create_detected_element(
            label=ElementLabel.MENU_TITLE,
            semantic_value="DUNE LEGACY",
            bbox=[0.25, 0.05, 0.5, 0.08],
            confidence=0.98
        )
        
        # Create semantic map
        semantic_map = create_semantic_map(
            screen_context=ScreenContext.MAIN_MENU,
            elements=[button_element, title_element],
            screen_resolution=(800, 600),
            capture_source="game_window"
        )
        
        print("✅ Semantic map created successfully")
        print(f"   Context: {semantic_map.screen_context.value}")
        print(f"   Elements: {len(semantic_map.elements)}")
        
        # Test filtering functions
        buttons = semantic_map.get_elements_by_label(ElementLabel.BUTTON)
        clickable = semantic_map.get_clickable_elements()
        high_conf = semantic_map.get_high_confidence_elements(threshold=0.9)
        
        print(f"   Buttons found: {len(buttons)}")
        print(f"   Clickable elements: {len(clickable)}")
        print(f"   High confidence elements: {len(high_conf)}")
        
        # Test JSON serialization
        json_data = semantic_map.to_json(indent=None)
        reconstructed = SemanticMap.from_dict(json.loads(json_data))
        
        print(f"   JSON serialization: ✅")
        print(f"   Reconstructed elements: {len(reconstructed.elements)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Semantic map validation failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("📋 Module 3D: Hierarchical Semantic Graph - AIP-SDS-V2.3")
    print("=" * 70)
    validate_semantic_map_structure()