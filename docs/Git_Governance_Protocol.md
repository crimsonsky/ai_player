# Git Governance Protocol (AIP-GIT-V1.0)

## Overview
This document establishes the version control governance for the AI Player project. All commits, data artifacts, and collaborative development must adhere to these protocols.

## Section 1: Repository Structure Requirements

### 1.1 Core Directory Organization
```
ai_player/
├── .git/                 # Git repository metadata
├── .dvc/                 # DVC configuration and metadata
├── .gitignore           # Git ignore patterns
├── .dvcignore           # DVC ignore patterns
├── README.md            # Project overview and setup
├── docs/                # Documentation directory
├── src/                 # Source code modules
├── tests/               # Test suites and validation
├── data/                # DVC-tracked data artifacts
│   ├── templates/       # Template Library (Module 2B)
│   ├── training/        # Training data and logs
│   └── models/          # Trained model artifacts
└── config/              # Configuration files
```

### 1.2 DVC Data Tracking Requirements
The following data artifacts MUST be tracked with DVC:
- Template Library images (`data/templates/`)
- Training datasets (`data/training/`)
- Model checkpoints (`data/models/`)
- State vector logs (`data/training/state_vectors/`)

## Section 2: Commit Message Standards

### 2.1 Commit Message Structure
All commit messages MUST follow this exact format:
```
[AGENT-ID] SCOPE: Brief description of changes

Extended description explaining:
- What was changed and why
- Any architectural decisions made
- Impact on milestone progression

DVC-HASH: <hash_if_data_changed>
MILESTONE: <current_milestone>
COMPLIANCE: <governance_compliance_status>
```

### 2.2 Scope Categories
Valid SCOPE values:
- `INIT`: Initial repository setup
- `M1`: Milestone 1 (Game Launch) changes  
- `M2`: Milestone 2 (Menu Reading) changes
- `M3`: Milestone 3 (Menu Navigation) changes
- `M4`: Milestone 4 (Action Execution) changes
- `M5`: Milestone 5 (Learning Integration) changes
- `DOCS`: Documentation updates
- `TEST`: Test suite changes
- `CONFIG`: Configuration changes
- `INFRA`: Infrastructure/tooling changes

### 2.3 Agent Identification
Since this is a single-agent development environment, all commits MUST include:
- `[AGENT-A]` as the agent identifier

### 2.4 DVC Integration
When data artifacts are modified, commits MUST include:
- `DVC-HASH: <dvc_commit_hash>` 
- Updated `.dvc` files in the same commit as code changes

## Section 3: Development Workflow Rules

### 3.1 Mandatory Pre-Commit Validation
Before ANY commit, the following checks MUST pass:
1. All Python files pass syntax validation
2. Core tests execute without errors
3. DVC status shows no untracked large files
4. Git status shows clean working directory (except intended changes)

### 3.2 Data Artifact Management
- Large files (>10MB) MUST be tracked with DVC, not Git
- Template images MUST be stored in `data/templates/`
- Training data MUST be stored in `data/training/`
- Model artifacts MUST be stored in `data/models/`

### 3.3 Branch Protection (Future)
When remote repository is configured:
- Main branch requires commit message compliance
- All data changes require DVC hash validation
- No direct pushes to main without PR (in team environment)

## Section 4: Compliance Enforcement

### 4.1 Automated Validation
Git hooks MUST validate:
- Commit message format compliance
- Agent identifier presence
- DVC tracking for large files
- Milestone progression tracking

### 4.2 Manual Verification
Each commit MUST be manually verified for:
- Architectural consistency with design documents
- Proper documentation updates
- Test coverage for new functionality
- DVC data integrity

### 4.3 Violation Consequences
Non-compliant commits will result in:
- Immediate commit rejection (via hooks)
- Required commit amendment with proper format
- Documentation of compliance violation in project log

## Section 5: Initial Commit Requirements

### 5.1 Baseline Commit Structure
The initial commit MUST include:
- All existing source code
- Project documentation (design specs, planning docs)
- Initial DVC configuration
- Git governance protocol (this document)
- Empty data directories with DVC tracking

### 5.2 Initial Commit Message Format
```
[AGENT-A] INIT: Establish project baseline with M1/M2 implementation

Initial commit establishing the AI Player project foundation:
- M1 Game Launch POC implemented and validated
- M2 Menu Reading specification fully implemented
- All four M2 modules (2A-2D) with validation tests
- DVC initialized for data artifact management
- Git governance protocol established

DVC-HASH: <initial_dvc_hash>
MILESTONE: M2-COMPLETE
COMPLIANCE: AIP-GIT-V1.0-COMPLIANT
```

## Section 6: Remote Repository Configuration

### 6.1 Origin Setup
When ready for remote:
```bash
git remote add origin <repository_url>
git branch -M main
git push -u origin main
```

### 6.2 DVC Remote (Future)
For team collaboration:
```bash
dvc remote add -d storage <cloud_storage_url>
dvc push
```

---

**Document Version**: AIP-GIT-V1.0
**Last Updated**: October 22, 2025  
**Compliance Requirement**: MANDATORY for all development work
**Enforcement**: Automated via Git hooks + Manual verification