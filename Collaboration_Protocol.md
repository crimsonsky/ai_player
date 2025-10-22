# Collaboration and Roles Protocol (AIP-COLLAB-V1.1)

This protocol formalizes the roles, responsibilities, and mandatory communication flow across the project team: the Human Operator (Master), the Strategic Advisor (Consultant Architect), and the Automated Implementer (Agent A).

## 1. DEFINED ROLES AND RESPONSIBILITIES

| Role | Responsibility | Communication Mandate |
|------|---------------|----------------------|
| **Master (Human Operator)** | Project Owner & Local Context Provider. Defines high-level goals and manually executes system-level debugging/fixes (e.g., macOS permissions). | Communicates with the Consultant Architect to initiate commands or report unresolvable physical/permission issues. |
| **Consultant Architect (Advisor)** | Strategic Planning & Governance. Translates Master's goals and Agent A's technical reports into clear, low-level AGENT COMMANDS. Does not assume local project state or dependencies. | Provides instructions exclusively via a formal AGENT COMMAND prompt, strictly referencing versioned project documentation. |
| **Agent A (The Implementer)** | Code Execution, Testing, and Artifact Management. Strictly adheres to all commands, writes and commits code, executes self-validation tests, and maintains DVC/Git integrity (Rule 2B/2C). | Must report status or blockages only when a command is fully executed or a system-level error (R1, R2, R3) prevents execution. |

## 2. THE MANDATORY INTERACTION LOOP

The system operates on an explicit command-response cycle. Agent A is prohibited from starting new work, moving milestones, or changing the system architecture unless explicitly directed by the Consultant Architect via an AGENT COMMAND.

### Agent A Status Report (Input)
Agent A signals the status of the current command:

- **Success**: "Command $$ID$$ fully executed and committed. Status: Ready for next task."
- **Failure/Blocker**: "Command $$ID$$ blocked. Reason: $$Detailed technical reason, e.g., 'Perception confidence fell below 0.8 on template X'$$. Requesting debugging protocol."

### Architect Analysis
The Consultant analyzes the report against the $\text{System Design}$ and $\text{Dependencies Checklist}$.

### Architect Command (Output)
The Consultant issues a new AGENT COMMAND prompt, which serves as the next unit of work (e.g., M2 implementation, debugging R2, or setup).

## 3. PROTOCOL FOR HANDLING CRITICAL BLOCKERS

When Agent A reports a physical or permission-related blocker (e.g., the recent $\text{pyobjc}$ failure), the loop is automatically redirected to the Master:

- **Architect Response**: The Consultant Architect provides a Debugging Protocol targeting the specific physical or permission issue, clearly instructing the Master to perform the manual fix on the operating system.
- **Master Action**: The Master performs the manual fix (e.g., checking Accessibility permissions).
- **Agent A Resumption**: Once the fix is confirmed by the Master, Agent A receives a new AGENT COMMAND to re-run the previous blocked task.

## 4. PROTOCOL FOR NEW AGENTS (Future-Proofing)

Any new agent (e.g., Agent B) must execute the Synchronization Protocol and the Git Pull/DVC Checkout mandate before reporting its status or commencing work. Their role must be defined by the Consultant Architect and documented here prior to deployment.

## 5. GOVERNANCE COMPLIANCE

This protocol operates under the AIP-GIT-V1.0 governance framework and requires:

- All AGENT COMMANDs must reference specific versioned documentation
- Agent A must maintain Git/DVC integrity per established rules
- Status reports must include technical details sufficient for architectural decision-making
- Blocking issues must be escalated through the defined chain of command

---

**Document Version**: AIP-COLLAB-V1.1  
**Last Updated**: Agent A Implementation  
**Governance**: Integrates with AIP-GIT-V1.0, Dependencies_And_Setup.md, and System Design Specification