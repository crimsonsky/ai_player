# Dependencies and Setup Documentation

## 1. Core Dependencies

### Python Dependencies
- **Python 3.8+**: Core runtime environment
- **PyTorch with MPS**: GPU acceleration for neural networks
- **Stable Baselines3**: Reinforcement learning algorithms
- **OpenCV (cv2)**: Computer vision and image processing
- **pyobjc**: macOS system integration and input control
- **ocrmac**: macOS-native OCR capabilities

### System Dependencies
- **macOS**: Primary target platform
- **Dune Legacy**: Target game application (installed in /Applications)
- **Git + DVC**: Version control and data versioning

## 2. Installation Commands

```bash
# Create virtual environment
python3 -m venv ai_player_env
source ai_player_env/bin/activate

# Install core dependencies
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
pip install stable-baselines3
pip install opencv-python
pip install pyobjc-framework-Quartz pyobjc-framework-ApplicationServices
pip install ocrmac
pip install dvc

# Additional utilities
pip install numpy matplotlib pillow
```

## 3. Configuration Artifacts

### 🔐 MANDATORY PERMISSION SETUP (CRITICAL)

**REQUIREMENT**: All AI player agents MUST configure these macOS permissions before any input emulation work.

#### Required System Permissions:

1. **Screen Recording Permission**:
   - Path: `System Settings → Privacy & Security → Screen Recording`
   - Required for: Screenshot capture and visual perception
   - Applications to enable: Terminal, VS Code, Python executable

2. **Accessibility Permission**:
   - Path: `System Settings → Privacy & Security → Accessibility`
   - Required for: Mouse/keyboard input emulation via pyobjc
   - Applications to enable: Terminal, VS Code, Python executable
   - **CRITICAL**: This permission is mandatory for Req 2.1 (Input Emulation)

3. **Input Monitoring Permission**:
   - Path: `System Settings → Privacy & Security → Input Monitoring`
   - Required for: Advanced input capture and monitoring
   - Applications to enable: Terminal, VS Code, Python executable
   - **CRITICAL**: Required for Risk R2 (Input Instability) mitigation

#### Permission Validation:

After configuring permissions, validate using the test script:

```bash
python test_pyobjc_input.py
```

Expected output for successful configuration:
- ✅ Req 2.1 (Input Emulation): VALIDATED
- ✅ Risk R2 (Input Instability): MITIGATED
- Mouse moves visibly to test coordinates
- Click events register successfully

#### Common Issues:

- **Issue**: Mouse control reports success but no visible movement
- **Cause**: Missing Accessibility permissions for the executing application
- **Fix**: Add Terminal/Python executable to Accessibility permissions list

- **Issue**: Screenshot capture fails with permission errors  
- **Cause**: Missing Screen Recording permissions
- **Fix**: Add Terminal/Python executable to Screen Recording permissions list

**⚠️ IMPORTANT**: Restart Terminal/VS Code after permission changes for them to take effect.

## 4. Project Structure

```
ai_player/
├── README.md                    # Project overview and governance
├── Dependencies_And_Setup.md    # This file - setup instructions
├── .gitignore                  # Git ignore patterns
├── .dvc/                       # DVC configuration and cache
├── m1_game_launch.py           # M1: Game Launch POC
├── m2_perception.py            # M2: Perception Module
├── mouse_control.py            # M3/M4: Action Module (Input Emulation)
├── visual_validation_tool.py   # M2 validation and debugging
├── test_pyobjc_input.py        # Permission validation script
├── templates/                  # Game UI templates for matching
└── screenshots/                # Captured game screenshots
```

## 5. Validation Tests

### System Readiness Check:
1. **Dependencies**: `python -c "import torch, cv2, ocrmac; print('Dependencies OK')"`
2. **Permissions**: `python test_pyobjc_input.py`
3. **Game Launch**: `python m1_game_launch.py`
4. **Screenshot**: `python -c "from m2_perception import capture_screenshot; capture_screenshot()"`
5. **Mouse Control**: `python mouse_control.py`

### Success Criteria:
- All imports successful
- pyobjc mouse control validated
- Game launches without errors
- Screenshots captured successfully
- Mouse movement and clicking functional

## 6. Risk Mitigation

### Risk R2 (Input Instability)
- **Mitigation**: Comprehensive macOS permission setup
- **Validation**: pyobjc CoreGraphics testing
- **Fallback**: Multiple input methods (pyobjc primary, AppleScript secondary)

### Risk R3 (Game State Detection)  
- **Mitigation**: Template matching + OCR hybrid approach
- **Validation**: Visual validation tool with confidence metrics
- **Fallback**: Multiple detection algorithms

### Risk R1 (Environment Inconsistency)
- **Mitigation**: Fixed game installation path and standardized screen resolution
- **Validation**: Game launch validation and screenshot consistency checks

---

**Last Updated**: Agent A - M2 INPUT PERMISSION DEBUG & FIX Protocol
**Validation Status**: ✅ Req 2.1 (Input Emulation) VALIDATED, Risk R2 MITIGATED