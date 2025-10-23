# AI Player - Autonomous Game Agent for Dune Legacy

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![PyTorch](https://img.shields.io/badge/PyTorch-MPS-red.svg)](https://pytorch.org)
[![DVC](https://img.shields.io/badge/DVC-Data%20Versioning-green.svg)](https://dvc.org)

## Project Overview

The AI Player project implements an autonomous agent capable of playing Dune Legacy using external perception and reinforcement learning. The system follows a professional 5-step RL architecture: **Perception → State Representation → Decision → Action → Learning**.

### Architecture Highlights
- **External Perception**: No game modification required - uses screen capture and OCR
- **Apple Silicon Optimized**: PyTorch with MPS backend for AMD GPU acceleration  
- **Professional RL Stack**: Stable Baselines3 with PPO algorithm
- **Robust Perception**: Multi-method OCR with Apple Vision Framework fallbacks
- **Safety First**: Comprehensive cleanup protocols and audio feedback

## Milestone Progress

| Milestone | Status | Description |
|-----------|--------|-------------|
| M1 | ✅ **COMPLETE** | Game Launch POC - Automated Dune Legacy startup |
| M2 | 🔄 **REFACTORED** | Input Emulation API - NEW pyobjc-based precise input control |
| M3 | � **PLANNED** | Learning-Based Perception Engine - YOLOv8 AI vision model |
| M4 | 📋 **PLANNED** | State Representation - Semantic map to vector conversion |
| M5 | 📋 **PLANNED** | Decision & Learning - PPO RL training integration |

## ARCHITECTURAL UPDATE: V2.3 - LEARNING-BASED SYSTEM

**⚠️ LEVEL-6 ARCHITECTURAL PURGE COMPLETED**

The project has undergone a major architectural refactoring from rule-based vision (OCR/Template Matching) to learning-based AI perception systems per AIP-SDS-V2.3.

### NEW M2: Input Emulation API (`src/action/input_api.py`)
- **Precise Input Control**: pyobjc CoreGraphics-based mouse and keyboard emulation
- **Human-like Movement**: Non-linear interpolation for realistic cursor movement  
- **Comprehensive Actions**: left_click(), right_click(), drag_select(), key_press(), move_mouse()
- **High Precision**: Pixel-perfect, non-blocking input execution
- **Validated & Tested**: Complete test suite with permission validation

### NEW M3: Learning-Based Perception Engine (PLANNED)
- **YOLOv8 Object Detection**: AI vision model for Buttons, Resources, Units, Stats
- **Graphics Text Recognition**: Custom-trained YOLO layers for game text interpretation
- **Real-time Processing**: 30+ FPS with PyTorch MPS acceleration
- **Dynamic Classification**: Automatic new element detection and labeling
- **Semantic Mapping**: Hierarchical game state representation

### DEPRECATED (PURGED)
- ❌ Rule-based template matching system
- ❌ OCR-based text extraction methods  
- ❌ Apple Vision Framework integration
- ❌ Signal Fusion Engine architecture
- ❌ Manual template libraries and ROI detection

**Rationale**: Rule-based vision systems failed to handle graphics-rendered game text and dynamic UI elements. The new learning-based approach provides robust, scalable perception capabilities.

## Quick Start

### Prerequisites
- macOS (for pyobjc and Apple Vision Framework)
- Python 3.11+
- Dune Legacy installed in `/Applications/`
- Screen Recording permissions enabled

### Installation

1. **Clone and Setup**
```bash
git clone <repository_url>
cd ai_player
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

2. **Configure DVC** (for data artifacts)
```bash
dvc pull  # Download template library and training data
```

3. **Enable macOS Permissions**
   - System Preferences → Security & Privacy → Screen Recording
   - Add Terminal to allowed applications
   - Restart Terminal after permission changes

### Testing M1 (Game Launch)
```bash
python m1_game_launch.py
```

### Testing M2 (Input Emulation API)
```bash
python tests/test_input_emulation.py
```

### Architecture Validation
```bash
# Check system design compliance
cat "AI PLAYER SYSTEM DESIGN SPECIFICATION.md"

# Review session progress  
cat "SESSION_SUMMARY_2025-10-23.md"
```

## Project Structure

```
ai_player/
├── .git/                    # Git repository
├── src/                     # Source code modules
│   ├── action/             # M2 - Input Emulation API (NEW)
│   ├── perception/         # M3 - Learning-Based Vision Engine (PLANNED)
│   ├── decision/           # M5 - RL decision making (PLANNED)
│   ├── state/              # M4 - State representation (PLANNED)
│   └── utils/              # Shared utilities
├── tests/                   # Comprehensive test suites
├── data/                    # Training datasets and model artifacts
│   ├── yolo_dataset/       # YOLO training data (PLANNED)
│   ├── models/             # Trained model checkpoints
│   └── screenshots/        # Screenshot archive
├── config/                  # Configuration files
├── tools/                   # Development and annotation tools
└── docs/                    # Project documentation
```

## Development Workflow

This project follows strict **Git Governance Protocol (AIP-GIT-V1.0)**:

### Commit Message Format
```
[AGENT-A] SCOPE: Brief description

Extended description explaining changes,
architectural decisions, and milestone impact.

DVC-HASH: <hash_if_data_changed>
MILESTONE: <current_milestone>
COMPLIANCE: AIP-GIT-V1.0-COMPLIANT
```

### Data Management
- Large files tracked with DVC (templates, models, training data)
- Code changes tracked with Git
- Synchronized commits ensure data-code consistency

## Technical Specifications

### Core Dependencies
- **PyTorch** (MPS backend for Apple Silicon acceleration)
- **YOLOv8** (Ultralytics - Real-time object detection)
- **Stable Baselines3** (PPO reinforcement learning)
- **pyobjc** (macOS CoreGraphics for input emulation and screen capture)
- **OpenCV** (Image preprocessing and computer vision utilities)

### Performance Requirements
- Input emulation: Pixel-perfect precision with <10ms latency
- Object detection: 30+ FPS real-time processing
- YOLO inference: ≥0.8 confidence threshold for game elements
- PyTorch MPS: GPU acceleration for vision model inference
- Response time: <100ms for complete perception-action pipeline

### Safety Protocols
- Guaranteed cleanup: Always returns to VS Code after testing
- Audio feedback: Provides status updates during operation
- Error handling: Graceful degradation with multiple fallbacks
- Focus management: Prevents user from being stranded in game

## Testing & Validation

### Input Emulation Validation
```bash
python tests/test_input_emulation.py
```
Validates:
- ✅ Precise mouse control with CoreGraphics
- ✅ Keyboard input reliability
- ✅ Drag selection functionality
- ✅ Human-like movement interpolation

### System Architecture Tests
```bash
# Validate LEVEL-6 architectural purge completion
python -c "import os; print('✅ Purge Complete' if not os.path.exists('src/perception/perception_module.py') else '❌ Purge Incomplete')"

# Validate NEW M2 implementation
python -c "from src.action.input_api import InputAPI; print('✅ NEW M2 Ready')"
```

## Documentation

- [`docs/AI PLAYER SYSTEM DESIGN SPECIFICATION.md`](docs/AI%20PLAYER%20SYSTEM%20DESIGN%20SPECIFICATION.md) - Complete architectural specification
- [`docs/M2_COMPLETION_REPORT.md`](docs/M2_COMPLETION_REPORT.md) - M2 implementation validation
- [`docs/Git_Governance_Protocol.md`](docs/Git_Governance_Protocol.md) - Version control standards
- [`project plan.txt`](project%20plan.txt) - Development roadmap

## Contributing

This project follows strict governance protocols:

1. **All commits** must comply with AIP-GIT-V1.0 format
2. **Data changes** must be tracked with DVC
3. **New features** require comprehensive tests
4. **Documentation** must be updated with code changes

## License

This project is developed for research and educational purposes.

---

**Current Status**: LEVEL-6 Architectural Purge Complete, NEW M2 Input API Implementation  
**Architecture Version**: AIP-SDS-V2.3 - Learning-Based Perception Engine  
**Last Updated**: October 23, 2025  
**Governance**: AIP-GIT-V1.0 Compliant | AIP-COLLAB-V1.2 Audio Signal Mandate

### Setup
1. **Clone and setup environment:**
   ```bash
   cd /path/to/ai_player
   python setup.py
   ```

2. **Activate virtual environment:**
   ```bash
   source venv/bin/activate
   ```

3. **Test milestones:**
   ```bash
   # M1 - Game Launch
   python test_m1.py
   
   # M2 - Clean Perception System (Real Detection Only)
   python test_m2_clean.py
   ```

## 📋 Development Milestones

### Phase 1: Foundation (Current)
- [x] **M1 - Game Launch POC**: Launch Dune Legacy programmatically ✅
- [ ] **M2 - Menu Reading**: Screen capture + OCR + template matching
- [ ] **M3 - Menu Navigation**: Basic RL loop for UI navigation  
- [ ] **M4 - Game State Perception**: Complex dynamic analysis

### Phase 2: Gameplay (Future)
- [ ] **M5 - Basic Gameplay**: Unit selection and movement
- [ ] **M6 - Resource Management**: Economy and building
- [ ] **M7 - Combat AI**: Military strategy and tactics
- [ ] **M8 - Advanced Strategy**: Complete gameplay mastery

## 🛠️ Technical Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| **RL Framework** | PyTorch + Stable Baselines3 | PPO implementation with MPS GPU acceleration |
| **Computer Vision** | OpenCV | Template matching, feature detection |
| **OCR** | ocrmac (Apple Vision) | Native macOS text recognition |
| **Input Control** | pyobjc (CoreGraphics) | Mouse/keyboard emulation |
| **Screen Capture** | pyobjc (Quartz) | High-speed screenshot capture |

## 📁 Project Structure

```
ai_player/
├── src/                    # Main source code
│   ├── perception/         # Screen capture, OCR, templates
│   ├── state/             # State vector representation
│   ├── decision/          # RL model (PPO)
│   ├── action/            # Input emulation
│   └── utils/             # Configuration, logging
├── data/                  # Data and artifacts
│   ├── templates/         # UI element templates
│   ├── logs/             # Training logs
│   ├── models/           # Trained model weights
│   └── screenshots/      # Screenshot archive
├── config/               # Configuration files
├── tests/                # Unit tests
└── scripts/              # Utility scripts
```

## ⚙️ Configuration

Main configuration in `config/system_config.yaml`:

```yaml
model:
  algorithm: "PPO"
  learning_rate: 0.0003
  state_size: 104  # 26 base features × 4 frames

game:
  name: "Dune Legacy"
  app_path: "/Applications/Dune Legacy.app"

perception:
  confidence_threshold: 0.8
```

## 🧪 Testing

- **M1 Test**: `python test_m1.py` - Game launch verification
- **Full Suite**: `python -m pytest tests/` (when implemented)
- **Manual Test**: `python main.py` - Run full AI agent

## 📊 Monitoring

- **TensorBoard**: `tensorboard --logdir data/logs/tensorboard`
- **Logs**: Check `data/logs/ai_player.log`
- **Model Performance**: Tracked via Weights & Biases integration

## 🔧 Development

### Adding New Templates
```python
from src.perception.perception_module import PerceptionModule
perception = PerceptionModule(config)
perception.add_template("new_button", "data/templates/new_button.png", 0.8)
```

### Training the Model
```python
from src.decision.rl_model import RLModel
model = RLModel(config)
model.train(total_timesteps=10000)
model.save_model("data/models/trained_model.zip")
```

## 🎮 Game Requirements

**Dune Legacy** must be installed and launchable from `/Applications/Dune Legacy.app`

Download from: [Dune Legacy Official Site](https://dunelegacy.sourceforge.net/)

## 📈 Performance Goals

- **M3 Target**: 90%+ menu navigation success rate
- **M4 Target**: Reliable game state detection (95%+ confidence)
- **Phase 1 Target**: Complete autonomous game startup and basic control

## 🤝 Contributing

This is an AI-driven development project where the AI agent generates its own tools and improvements. See project plan for autonomous development requirements.

## 📄 License

See project documentation for license information.

---

**Status**: 🚧 Phase 1 Development - M1 Complete, M2 In Progress