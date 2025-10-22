# Automated Testing and Validation Protocol (AIP-TEST-V1.0)

This protocol defines the mandatory requirements for all automated tests executed by Agent A to ensure non-disruptive, verifiable, and observable operation, especially when the game window is in focus.

## 1. NON-INTERACTIVE MANDATE

**Prohibition**: All validation scripts and tests MUST NOT require manual terminal input (e.g., `input()`, `raw_input()`) from the Master.

**Rationale**: Terminal input breaks application focus on macOS, disrupting the game state and invalidating the test result (R2 Mitigation).

**Action**: If external data is needed, Agent A must source it from the version-controlled Game Config File (6.1) or the Template Library (6.1).

## 2. AUDIO FEEDBACK SYSTEM (OBSERVABILITY)

To provide clear, audible feedback while the game window obscures the console, Agent A must integrate a simple audio notification system into all testing scripts.

### Test Action Signalling
Agent A MUST trigger a distinct, brief audio tone for every major action executed during a test or self-validation step (e.g., Screen Capture, Click Event, Validation Success). This allows the Master to audibly track the test flow.

### Critical Input Required
In the highly exceptional case that the Master's manual intervention is unavoidable (e.g., a critical permission check), Agent A MUST trigger a loud, sustained audio alert (e.g., a "system alarm" sound) to draw immediate attention. This prevents silent failure.

## 3. ARTIFACT & VERSIONING

This protocol, along with the test output logs, must be version-controlled according to the Git Governance Protocol.

## 4. IMPLEMENTATION REQUIREMENTS

### Audio System Integration
All test scripts must include:
- Brief confirmation tones for successful actions
- Distinctive error tones for failures
- Emergency alert sounds for critical manual intervention needs
- Clear verbal announcements using macOS `say` command when appropriate

### Non-Interactive Design
Test scripts must:
- Use configuration files instead of interactive prompts
- Implement timeout mechanisms for operations
- Provide clear logging of all actions and results
- Generate artifact files for post-test analysis

### Focus Preservation
Testing must:
- Maintain game window focus throughout execution
- Avoid terminal interactions that would steal focus
- Use background processes where appropriate
- Implement proper window management

## 5. COMPLIANCE CHECKLIST

Before executing any test, Agent A must verify:
- [ ] No `input()` or interactive prompts in test code
- [ ] Audio feedback implemented for all major actions
- [ ] Emergency alert system in place for critical failures
- [ ] Configuration data sourced from version-controlled files
- [ ] Game window focus preservation mechanisms active
- [ ] Proper logging and artifact generation configured

## 6. GOVERNANCE INTEGRATION

This protocol operates under:
- AIP-COLLAB-V1.1 (Collaboration Protocol)
- AIP-GIT-V1.0 (Git Governance)
- Risk R2 (Input Instability) mitigation requirements

---

**Document Version**: AIP-TEST-V1.0  
**Last Updated**: Agent A Implementation  
**Governance**: Integrates with AIP-COLLAB-V1.1, AIP-GIT-V1.0, and System Design Specification