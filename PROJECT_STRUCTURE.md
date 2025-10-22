# AI Player Project Structure

## Main Modules
src/
├── perception/          # Module 1: Screen capture, OCR, template matching
├── state/              # Module 2: State vector representation
├── decision/           # Module 3: RL model and training
├── action/             # Module 4: Input emulation
└── utils/              # Shared utilities and configuration

## Data & Artifacts
data/
├── templates/          # Template library for UI elements
├── logs/              # Training logs and state vectors
├── models/            # Trained RL model weights
└── screenshots/       # Raw screenshot archive

## Configuration
config/
├── game_config.json   # Game-specific settings and learned paths
├── model_config.yaml  # RL hyperparameters and model settings
└── system_config.yaml # System settings and paths

## Development
tests/                 # Unit tests for each module
scripts/              # Utility scripts and tools
docs/                 # Additional documentation