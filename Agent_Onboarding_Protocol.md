# PROJECT ONBOARDING PROTOCOL: AI PLAYER (AIP-ONBOARD-V1.0)

This protocol is a step-by-step guide for setting up a new agent or developer (Agent B, Master Developer) environment, ensuring full alignment with the codebase, MLOps, and governance standards established by Agent A and the Consultant Architect.

## SECTION 1: SYSTEM PREREQUISITES

| Requirement | Artifact Reference | Details |
|-------------|-------------------|---------|
| **Dependencies** | `Dependencies_And_Setup.md` | Install all required Python libraries (PyTorch, OpenCV, pyobjc, etc.) listed in this file. |
| **Core Game** | `PROJECT PLANNING DOCUMENT` | Install the target game, Dune Legacy, and ensure it runs in a consistent, fixed resolution (recommended: 1920x1080) for reliable coordinate normalization. |
| **macOS Permissions** | `Dependencies_And_Setup.md` | **CRITICAL**: Manually grant the Python interpreter/Terminal Accessibility and Input Monitoring permissions in macOS Privacy & Security settings to enable Module 4 (ACTION). |

## SECTION 2: VERSION CONTROL ALIGNMENT

The new agent must use the SSH protocol for persistent, non-interactive Git access.

| Step | Command/Action | Purpose |
|------|----------------|---------|
| **2.1 Generate SSH Key** | Generate a new SSH key pair specific to this machine/agent. | Required for secure, token-less access. |
| **2.2 Register Key** | Upload the public key to the central GitHub repository settings. | Grants this agent access rights. |
| **2.3 Clone Repository** | `git clone git@github.com:user/ai-player.git` (Use the SSH link) | Retrieves the codebase and Git history. |
| **2.4 Init DVC** | `dvc pull` | **CRITICAL**: Downloads all version-controlled data artifacts, including the Template Library (Module 2B) and the latest Model Weights (Module 6.1). |

## SECTION 3: PROJECT ALIGNMENT & GUIDELINES

Upon successful setup, the new agent must review and adhere to the following project mandates:

| Document | Purpose | Key Mandate |
|----------|---------|-------------|
| **Collaboration Protocol** | `Collaboration_Protocol.md` | Defines the specific roles of Agent A (Implementer), the Master (You), and the Consultant Architect (Me). All communication must flow through the Master. |
| **Git Governance Protocol** | `Git_Governance_Protocol.md` | Sets mandatory rules for all commits (e.g., branch naming, commit message format). No exceptions permitted. |
| **Testing Protocol** | `Testing_and_Validation_Protocol.md` | Mandates the use of non-interactive execution and Audio Feedback Signals (AIP-TEST-V1.0) for all test runs to ensure observability. |

## SECTION 4: INITIAL VALIDATION TEST

The new agent must run a single, self-contained test to confirm the entire local environment is correctly configured and aligned with Agent A's state.

1. **Run Test**: Execute the latest M2 functional validation script (`test_corrected_coords.py`).
2. **Validation**: The test must successfully detect all six menu buttons and trigger the required Audio Feedback Signals.
3. **Ready Status**: If the test passes, the agent is considered **LIVE** and can proceed with its assigned task (e.g., becoming Agent B/Data Collector).

## SECTION 5: DETAILED SETUP PROCEDURES

### 5.1 SSH Key Generation (macOS)

```bash
# Generate SSH key pair
ssh-keygen -t ed25519 -C "agent@ai-player-project"

# Add to SSH agent
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_ed25519

# Display public key for GitHub registration
cat ~/.ssh/id_ed25519.pub
```

### 5.2 Repository Setup

```bash
# Clone repository (SSH)
git clone git@github.com:crimsonsky/ai_player.git
cd ai_player

# Initialize DVC and pull data
dvc pull

# Verify Git governance protocol
git config user.name "Agent-B"
git config user.email "agent-b@ai-player-project"
```

### 5.3 Python Environment Setup

```bash
# Create virtual environment (recommended)
python3 -m venv ai_player_env
source ai_player_env/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install additional macOS dependencies
pip install pyobjc-framework-Quartz
pip install pyobjc-framework-ApplicationServices
```

### 5.4 macOS Permissions Configuration

**CRITICAL**: The following permissions MUST be granted manually through System Preferences:

1. **Accessibility Access**:
   - System Preferences → Security & Privacy → Privacy → Accessibility
   - Add Python interpreter and Terminal app
   - Grant full access

2. **Input Monitoring**:
   - System Preferences → Security & Privacy → Privacy → Input Monitoring
   - Add Python interpreter and Terminal app
   - Grant full access

3. **Screen Recording** (if needed):
   - System Preferences → Security & Privacy → Privacy → Screen Recording
   - Add Terminal app

## SECTION 6: VALIDATION CHECKLIST

Before proceeding to assigned tasks, verify each item:

- [ ] SSH key generated and registered on GitHub
- [ ] Repository cloned using SSH protocol
- [ ] DVC data artifacts downloaded (`dvc pull` successful)
- [ ] All Python dependencies installed
- [ ] macOS permissions granted (Accessibility + Input Monitoring)
- [ ] Dune Legacy game installed and runs at consistent resolution
- [ ] Initial validation test passes with audio feedback
- [ ] All governance protocols reviewed and understood

## SECTION 7: ROLE-SPECIFIC ONBOARDING

### Agent B (Data Collector)
- Focus on `src/data_collection/` modules
- Review template extraction workflows
- Understand coordinate validation procedures

### Master Developer
- Full system architecture review
- Testing protocol enforcement authority
- Cross-module integration oversight

### Consultant Architect
- System design specification authority
- Architectural integrity enforcement
- Strategic direction and planning

## SECTION 8: TROUBLESHOOTING COMMON ISSUES

### DVC Pull Failures
```bash
# Reset DVC cache if corrupted
dvc cache dir --unset
dvc pull --force
```

### Permission Denied Errors
- Verify SSH key is added to GitHub account
- Check SSH agent is running: `ssh-add -l`
- Test connection: `ssh -T git@github.com`

### Mouse Control Issues
- Ensure Accessibility permissions granted
- Test with: `python test_pyobjc_input.py`
- Restart Terminal after granting permissions

### Game Resolution Issues
- Set Dune Legacy to windowed mode at 1920x1080
- Verify consistent positioning on screen
- Test with coordinate validation scripts

## SECTION 9: SUCCESS CRITERIA

An agent is considered **FULLY ONBOARDED** when:

1. ✅ All validation checklist items completed
2. ✅ Initial M2 functional validation test passes
3. ✅ Audio feedback signals working correctly
4. ✅ Git commits follow governance protocol format
5. ✅ DVC data artifacts synchronized and accessible
6. ✅ Mouse control and screenshot capture functional

## SECTION 10: NEXT STEPS

Upon successful onboarding:

1. **Review Active Todo List**: Check current project priorities
2. **Coordinate with Master**: Receive specific task assignments
3. **Follow Collaboration Protocol**: All work must align with established roles
4. **Maintain Documentation**: Update protocols based on experience

---

**Protocol Version**: AIP-ONBOARD-V1.0  
**Last Updated**: October 22, 2025  
**Maintained By**: Agent A (Implementer)  
**Approved By**: Master & Consultant Architect