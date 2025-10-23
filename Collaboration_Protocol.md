# COLLABORATION AND ROLES PROTOCOL (AIP-COLLAB-V1.3)

This protocol formalizes the roles, responsibilities, and mandatory communication flow across the project team: the Human Operator (Master), the Strategic Advisor (Consultant Architect), and the Automated Implementers (Agent A & Agent B).

## 1. DEFINED ROLES AND RESPONSIBILITIES

| Role | Responsibility | Communication Mandate | Audio Signal Mandate |
|------|---------------|----------------------|----------------------|
| **Master (Human Operator)** | Project Owner & Local Context Provider. Defines high-level goals and manually executes system-level debugging/fixes (e.g., macOS permissions). **Agent A is the preferred implementer.** | Communicates with the Consultant Architect to initiate commands or report unresolvable physical/permission issues. | Listens for audio alerts to execute Manual Intervention Protocols (e.g., granting permissions, re-labeling data). |
| **Consultant Architect (Advisor)** | Strategic Planning & Governance. Translates Master's goals and agent technical reports into clear, low-level AGENT COMMANDS. Does not assume local project state or dependencies. | Provides instructions exclusively via a formal AGENT COMMAND prompt, strictly referencing versioned project documentation. | Monitors system for trigger events requiring $\text{Master}$ intervention or architectural guidance. |
| **Agent A (Primary Implementer)** | **PRIMARY AGENT** - Code Execution, Testing, and Artifact Management. Leads implementation of core milestones (M1-M5). Strictly adheres to all commands, writes and commits code, executes self-validation tests, and maintains Git integrity. | Must report status or blockages only when a command is fully executed or a system-level error prevents execution. **Coordinates with Agent B for concurrent work.** | MANDATORY: Generates distinct audio alerts when triggering a Master Intervention Protocol (See $\text{Protocol 5}$). |
| **Agent B (Secondary Implementer)** | **SECONDARY AGENT** - Specialized tasks, documentation, testing support. Works under Agent A coordination for parallel development. Must sync with project state before starting work. | Must execute Synchronization Protocol and Git Pull before reporting status. **Must coordinate with Agent A to avoid conflicts.** | MANDATORY: Generates distinct audio alerts when triggering a Master Intervention Protocol (See $\text{Protocol 5}$). |

## 2. THE MANDATORY INTERACTION LOOP

The system operates on an explicit command-response cycle. Both agents are prohibited from starting new work, moving milestones, or changing the system architecture unless explicitly directed by the Consultant Architect via an AGENT COMMAND.

### Multi-Agent Coordination (NEW)
- **Agent A (Primary):** Handles core milestone implementation and architectural changes
- **Agent B (Secondary):** Supports with specialized tasks, testing, documentation
- **Conflict Prevention:** Agent B must always check latest commits and coordinate with Agent A
- **Work Assignment:** Consultant Architect specifies target agent in AGENT COMMANDS

### Agent Status Report (Input)
Agents signal the status of current commands:

- **Success**: "[AGENT-A/B] Command $$ID$$ fully executed and committed. Status: Ready for next task."
- **Failure/Blocker**: "[AGENT-A/B] Command $$ID$$ blocked. Reason: $$Detailed technical reason$$. Requesting debugging protocol."
- **Coordination**: "[AGENT-A/B] Coordinating with [other agent] on overlapping work in [area]."

### Architect Analysis
The Consultant analyzes the report against the $\text{System Design}$ and $\text{Dependencies Checklist}$.

### Architect Command (Output)
The Consultant issues a new AGENT COMMAND prompt, which serves as the next unit of work (e.g., M2 implementation, debugging R2, or setup).

## 3. PROTOCOL FOR HANDLING CRITICAL BLOCKERS

When Agent A reports a physical or permission-related blocker (e.g., the recent $\text{pyobjc}$ failure), the loop is automatically redirected to the Master:

- **Architect Response**: The Consultant Architect provides a Debugging Protocol targeting the specific physical or permission issue, clearly instructing the Master to perform the manual fix on the operating system.
- **Master Action**: The Master performs the manual fix (e.g., checking Accessibility permissions).
- **Agent A Resumption**: Once the fix is confirmed by the Master, Agent A receives a new AGENT COMMAND to re-run the previous blocked task.

## 4. MULTI-AGENT COORDINATION PROTOCOL (Agent A & Agent B)

### Agent B Synchronization Requirements
- **MANDATORY:** Execute `git pull origin main` before starting any work
- **MANDATORY:** Review latest commits and project status documents  
- **MANDATORY:** Check for Agent A active work to avoid conflicts
- **MANDATORY:** Coordinate with Agent A for overlapping areas (same files/modules)

### Commit Message Standards
- **Agent A:** `[AGENT-A] SCOPE: Description` (existing format maintained)
- **Agent B:** `[AGENT-B] SCOPE: Description` (must follow same standards)
- **Coordination:** Include coordination notes when agents work on related areas

### Work Assignment Priority
1. **Agent A (Primary):** Core milestones (M1-M5), architectural changes, critical path work
2. **Agent B (Secondary):** Documentation, testing, specialized tasks, parallel development support
3. **Conflict Resolution:** Master's preference for Agent A takes priority in disputes

## 5. INTERACTION LOOP PROTOCOL

Each agent must provide the following status when reporting:
- **Agent Identity:** Clearly state "Agent A" or "Agent B" in status reports
- Current working branch  
- Active milestone/objective
- Progress summary
- Next planned action
- Any blockers requiring external resolution
- **Coordination Status:** Note any Agent A/B collaboration or potential conflicts

## 6. IMPLEMENTATION PRIORITY MATRIX

| Task Category | Primary Agent | Secondary Agent Role |
|---------------|---------------|---------------------|
| Core Milestones (M1-M5) | Agent A | Support/Testing |
| Architecture Changes | Agent A | Review/Validation |
| Input Systems | Agent A | Integration Testing |
| Perception Systems | Agent A | Data Collection |
| Documentation | Agent B | Agent A Review |
| Test Suites | Agent B | Agent A Validation |
| Performance Optimization | Shared | Coordinate Required |

This protocol ensures unified master plan execution with Agent A as preferred primary implementer per Master's specification.

## 6. GOVERNANCE COMPLIANCE

This protocol operates under the AIP-GIT-V1.0 governance framework and requires:

- All AGENT COMMANDs must reference specific versioned documentation
- Agent A must maintain Git/DVC integrity per established rules
- Status reports must include technical details sufficient for architectural decision-making
- Blocking issues must be escalated through the defined chain of command
- **NEW**: Audio signal compliance for Master Intervention Protocols

---

**Document Version**: AIP-COLLAB-V1.2  
**Last Updated**: Master Protocol Enhancement - Audio Signals  
**Governance**: Integrates with AIP-GIT-V1.0, Dependencies_And_Setup.md, System Design Specification, and Master Intervention Protocol