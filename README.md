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
| M2 | ✅ **COMPLETE** | Menu Reading - Template matching & OCR integration |
| M3 | 🔄 **PENDING** | Menu Navigation - RL-driven menu interaction |
| M4 | 📋 **PLANNED** | Action Execution - In-game command implementation |
| M5 | 📋 **PLANNED** | Learning Integration - Training pipeline & optimization |

## M2 Implementation Details

**MILESTONE 2 SPECIFICATION: ✅ FULLY COMPLIANT**

The M2 Menu Reading system includes four complete modules:

### Module 2A: Perception Module (`src/perception/perception_module.py`)
- Screen capture using pyobjc with macOS integration
- Image preprocessing with OpenCV
- Integration hub for template matching and OCR

### Module 2B: Template Library (`src/utils/template_library.py`)
- Professional template management with JSON persistence
- Default templates for Dune Legacy UI elements
- Confidence threshold ≥0.95 enforcement
- ROI-based fallback detection

### Module 2C: Element Location (`src/perception/element_location.py`)
- OpenCV-based template matching with cv2.matchTemplate
- Normalized coordinate output (0.0-1.0 range)
- Multiple fallback methods for robustness
- Comprehensive error handling

### Module 2D: OCR Integration (`src/perception/ocr_integration.py`)
- Apple Vision Framework via ocrmac (primary method)
- Tesseract OCR integration (secondary fallback)
- Pattern matching (ultimate fallback)
- Numerical value extraction capabilities

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
python -c "
from src.action.action_module import ActionModule
config = {'audio_feedback': True, 'game_name': 'Dune Legacy'}
action_module = ActionModule(config)
action_module.launch_game()
"
```

### Testing M2 (Menu Reading)
```bash
python tests/test_m2_integration.py
```

## Project Structure

```
ai_player/
├── .git/                    # Git repository
├── .dvc/                    # DVC configuration  
├── src/                     # Source code modules
│   ├── action/             # M1 - Game launch & input simulation
│   ├── perception/         # M2 - Screen capture, templates, OCR
│   ├── decision/           # M3 - RL decision making (future)
│   ├── state/              # M4 - Game state representation (future)
│   └── utils/              # Shared utilities
├── tests/                   # Comprehensive test suites
├── tools/                   # Development tools
├── data/                    # DVC-tracked data artifacts
│   ├── templates/          # UI element templates
│   ├── training/           # Training datasets
│   └── models/             # Trained model checkpoints
├── docs/                    # Project documentation
└── config/                  # Configuration files
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
- **Stable Baselines3** (PPO reinforcement learning)
- **OpenCV** (Computer vision and template matching)
- **pyobjc** (macOS integration for screen capture)
- **ocrmac** (Apple Vision Framework OCR)

### Performance Requirements
- Template matching: ≥0.95 confidence threshold
- OCR text extraction: ≥0.8 confidence threshold
- Coordinate normalization: 0.0-1.0 range for all outputs
- Response time: <100ms for perception pipeline

### Safety Protocols
- Guaranteed cleanup: Always returns to VS Code after testing
- Audio feedback: Provides status updates during operation
- Error handling: Graceful degradation with multiple fallbacks
- Focus management: Prevents user from being stranded in game

## Testing & Validation

### M2 Self-Tests
```bash
python tests/m2_self_tests.py
```
Validates:
- ✅ Completeness: All components implemented
- ✅ Robustness: Error handling under adverse conditions  
- ✅ Stability: Consistent performance and recalibration

### Integration Testing
```bash
python tests/test_m2_integration.py
```
Validates full M2 pipeline with realistic scenarios.

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

**Current Status**: M2 Complete, M3 Development Ready  
**Last Updated**: October 22, 2025  
**Governance**: AIP-GIT-V1.0 Compliant

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