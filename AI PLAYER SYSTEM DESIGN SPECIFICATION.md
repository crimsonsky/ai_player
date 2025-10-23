# **AI PLAYER SYSTEM DESIGN SPECIFICATION (AIP-SDS-V2.3)**

**Based on Project Plan V1.2 (Refactored) | Target Agent: Dune Legacy | Phase: Phase 1 (M1-M4)**

## **1. ARCHITECTURAL OVERVIEW (CLOSED-LOOP RL)**

The AI Player operates as an encapsulated Reinforcement Learning environment (Gym Wrapper). The core loop involves five interconnected modules executing sequentially at every time step ($\\Delta t$):

1. **ACTION:** Executes $A\_t$ via input emulation.
2. **PERCEPTION:** Captures raw screen data.
3. **STATE REPRESENTATION:** Converts raw data into the State Vector ($S\_t$).
4. **DECISION:** $S\_t \\rightarrow$ Action ($A\_t$) via the PPO model.
5. **LEARNING:** Receives Reward ($R\_t$) to update Decision Module weights.

## **2. MODULE 2: ACTION (INPUT EMULATION) - NEW M2 FOCUS**

**Goal:** Implement all required low-level input control methods (Req 2.1) before integrating any perception logic, creating a clean, tested Input API.

**Technology:** pyobjc (Mandatory for macOS precision).

| Target Action | Implementation Method | Precision/Notes |
| :---- | :---- | :---- |
| **Mouse Click** | Low-level CoreGraphics calls. | Required for pixel-perfect, non-blocking input. Includes left, right, double-click. |
| **Drag Select** | CoreGraphics $\\text{mouseDown} \\rightarrow \\text{mouseDrag} \\rightarrow \\text{mouseUp}$ sequence. | Required for unit selection and map navigation. |
| **Mouse Movement** | Low-level CoreGraphics calls. | Smooth, non-linear interpolation is required for realistic movement. |
| **Key Press/Release** | Low-level CoreGraphics calls. | Reliable for hotkeys (e.g., 'W', 'S', map controls). |

## **3. MODULE 3: LEARNING-BASED PERCEPTION STREAM ENGINE - NEW M3 FOCUS**

**Goal:** Build a robust, AI-driven visual interpretation engine to replace failed OCR/Template Matching, providing the high-quality semantic map data required for state representation.

**Technology:** Dedicated AI Model (e.g., $\\text{YOLOv8}$) with $\\text{PyTorch/MPS}$ inference acceleration.

| Sub-Module | Technology | Function | Output Format | Notes/Robustness |
| :---- | :---- | :---- | :---- | :---- |
| **A. Screen Capture** | pyobjc | High-speed, non-blocking capture of the active screen, with mandatory window isolation. | Cropped $\\text{PIL}$ Image (RGB) | Must exceed 30 FPS for effective real-time control ($\\Delta t$ requirement). |
| **B. Object Detection (The Engine)** | AI Vision Model ($\\text{YOLOv8}$) | Real-time object detection (R-CNN/YOLO based) trained to identify: 1) Buttons, 2) Resources, 3) Units, 4) Stats. | List of $\\text{\\{Label, Bounding Box, Confidence\\}}$. | Must use MPS acceleration for inference; YOLO chosen for speed/accuracy trade-off. |
| **C. Text/Value Interpretation** | Integrated into Vision Model | The Vision Model (3B) must be trained to read the stylized text as an image object, replacing all previous OCR attempts. | $\\text{Text Value}$ field within the object's metadata (e.g., Mineral count: "450"). | High Priority: Custom training of YOLO layer for graphics-rendered numerals/text. |
| **D. Semantic Map Generation** | Custom Routine | Converts the raw detection list (3B/3C) into a structured $\\text{Game State Map}$ for State Representation. | Hierarchical Semantic Graph (JSON) | CRITICAL for Extensibility: Routine flags new high-confidence, unclassified objects for Dynamic Class Generation in M6.1. |

## **4. MODULE 4: STATE REPRESENTATION (FEATURES $\\rightarrow$ $S\_t$) - NEW M4 FOCUS**

**Goal:** Convert the highly complex Semantic Map (from M3) into a compact, fixed-size numerical vector ($S\_t$) suitable for the RL algorithm.

$S\_t$ must be a flat, 1-dimensional $\\text{NumPy}$ array. The structure is dynamic but will include the following core sections for Phase 1:

### **Game Phase Indicator:** (From Semantic Map: Context key)

* is\_in\_main\_menu: $\\{0, 1\\}$
* is\_in\_game: $\\{0, 1\\}$

### **Resources/Stats:** (From Semantic Map: Elements keys)

* current\_minerals: Integer.
* power\_consumption: Integer.

### **Perception Confidence:**

* avg\_detection\_score: Float (Average of all element confidence scores from M3).

### **4.2. HISTORY STACKING**

The final $S\_t$ will be a stack of the last $N=\\text{HISTORY\\\_FRAMES}$ State Vectors (default $N=4$).

## **5. MODULE 5: DECISION (RL MODEL & TRAINING)**

**Goal:** Learn an optimal policy ($\\pi(a|s)$) to maximize cumulative reward using the PPO algorithm.

* **Model:** Proximal Policy Optimization (PPO) (Req 2.4).
* **Implementation:** Stable Baselines3 ($\\text{SB3}$) with PyTorch backend.
* **Hardware Acceleration:** Must utilize $\\text{PyTorch}$'s Metal Performance Shaders (MPS) backend for AMD GPU acceleration (Technical Stack).

## **6. MODULE 6: DATA & MLOPS SPECIFICATIONS**

### **6.1. DATA ARTIFACTS (VERSION CONTROL & MANAGEMENT)**

| Artifact | Location/Tool | Purpose | Versioning/Storage |
| :---- | :---- | :---- | :---- |
| **Model Dataset** | File System/DVC | Labeled images for M3 training (e.g., $\\text{YOLO}$ dataset). | Mandatory upon any new labeling session. |
| **Experience Replay Buffer** | In-Memory (or $\\text{NumPy}$ persistence) | Stores recent $\\text{SARSA}$ tuples for RL training (M5). | Fixed-size, revolving buffer to prevent data bloat. Older data is overwritten. |
| **Model Weights** | Git/W&B | $\\text{YOLO}$ or $\\text{CNN}$ trained weights (M3) and $\\text{SB3}$ weights (M5). | Mandatory upon successful training/retraining. |
| **State Vector Logs** | Data Lake/W&B | Training data ($\\text{S}\_t, \\text{A}\_t, \\text{R}\_t$). | Saved as Compressed Numerical Arrays (e.g., HDF5) for efficient retrieval and low I/O. |
| **Game Config File** | JSON/Git | Stores Hyperparameters, $\\text{Data Version ID}$, and Dynamic Class Dictionary (M3D). | Updates upon M3 success, MLOps Retraining. |

### **6.2. MONITORING & RETRAINING TRIGGERS**

* **Performance Drift:** ($\\text{SR}\_{7d}$ drops by $\\ge 10\\%$) $\\rightarrow$ Trigger $\\text{High-Priority Retraining Cycle}$.
* **Data Drift:** ($50\\%$ shift in key State Vector variable mean) $\\rightarrow$ Halt play, trigger Perception Stream Engine Re-Validation, then trigger $\\text{High-Priority Retraining Cycle}$.
* **Classification Drift (New):** $\\text{M3}$ reports $\\ge 5$ new Dynamic Class Generation events in 24 hours. $\\rightarrow$ Halt play, trigger Human Labeling/Review Protocol, and then $\\text{Retraining Cycle}$.

### **6.3. TOOLING: DUNE LEGACY ANNOTATION TOOLKIT (DLAT)**

**Purpose:** Custom labeling tool to generate high-quality, game-specific training data for the $\\text{YOLOv8}$ Perception Stream Engine (M3). This tool implements the Human Labeling/Review Protocol defined in M6.2.

**Core Requirements:**

* **GUI Schema Sketch (New):** Allows the Master to provide an initial, high-level description of the screen layout (e.g., "Top-left is Resource Panel, Center is Minimap"). This generates skeleton data to pre-populate the labeling interface, improving human efficiency.
* **Input Source:** Accepts screenshots directly from Module 3A (Screen Capture).
* **Annotation Type:** Supports standard Bounding Box annotation for object localization.
* **Hierarchical Output:** Prompts the human operator for both a primary Class Label (Button, Unit, Resource) and a secondary Semantic Value (Start Game, 450 Minerals).
* **Output Format:** Saves labeled data in $\\text{YOLO}$ format, ready for DVC versioning and direct model consumption.