# Game Configuration File (Module 6.1)
# AI Player System - Dune Legacy Configuration

## Game Information
GAME_NAME = "Dune Legacy"
GAME_PATH = "/Applications/Dune Legacy.app"
SCREEN_RESOLUTION = (3440, 1440)

## Template Matching Configuration
TEMPLATE_MATCHING_THRESHOLD = 0.95
CONFIDENCE_MINIMUM = 0.95
MATCHING_METHOD = "TM_CCOEFF_NORMED"

## Menu Navigation Path (Learned Artifacts)
# These coordinates are LEARNED GROUND TRUTH for Module 3 (Decision) target selection
# NOT for use in Module 2C (Element Location) - that must use dynamic template matching

MENU_BUTTONS = {
    # Format: Button Name: (normalized_x, normalized_y, confidence_required)
    "SINGLE_PLAYER": (0.5000, 0.5896, 0.95),  # Confirmed via click test
    "OPTIONS": (0.5000, 0.7563, 0.95),        # Ground Truth: (1720, 1089) normalized
    "MAP_EDITOR": (0.5000, 0.7007, 0.95),     # Confirmed via click test: (1720, 1009)
    
    # Additional calculated positions (validation targets)
    "MULTI_PLAYER": (0.5000, 0.6451, 0.95),   # Calculated: (1720, 929)
    "REPLAY": (0.5000, 0.8118, 0.95),         # Calculated: (1720, 1169)
    "QUIT": (0.5000, 0.8674, 0.95)            # Calculated: (1720, 1249)
}

## Template Library Paths
TEMPLATE_PATH_OPTIONS = "templates/options_button.png"
TEMPLATE_PATH_SINGLE_PLAYER = "templates/single_player_button.png"
TEMPLATE_PATH_MAP_EDITOR = "templates/map_editor_button.png"

## Validation Configuration
GROUND_TRUTH_TOLERANCE = 2  # pixels
COORDINATE_VALIDATION_ENABLED = True

## Risk Mitigation
# R2 (Input Instability) - Use pyobjc CoreGraphics for mouse control
MOUSE_CONTROL_METHOD = "pyobjc"
INPUT_VALIDATION_REQUIRED = True

# R3 (Game State Detection) - Template matching + OCR hybrid
DETECTION_METHOD = "template_matching_primary"
OCR_FALLBACK_ENABLED = True

## Module Integration
# Module 2C must use ONLY template matching against templates in TEMPLATE_PATH_*
# Module 3 uses coordinates from [MENU_BUTTONS] as action targets AFTER Module 2C detection
# Module 4 uses MOUSE_CONTROL_METHOD for input execution

## AIP Compliance
GOVERNANCE_VERSION = "AIP-COLLAB-V1.1"
TESTING_PROTOCOL = "AIP-TEST-V1.0"
GIT_GOVERNANCE = "AIP-GIT-V1.0"