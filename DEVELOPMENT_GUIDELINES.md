# AI Player Development Guidelines

## Core Development Principles

### 1. Focus Management Protocol
- **CRITICAL:** Always ensure the target application is in focus before performing any actions
- Use `NSApplication.sharedApplication().activateIgnoringOtherApps_(True)` to bring app to front
- Verify window focus before screen capture or input emulation
- Implement focus validation in all perception and action modules

### 2. Audio Feedback System
- **Real Tests:** Include audio signals to indicate test progress and status
- Use system audio or speech synthesis for key events:
  - Test start/completion
  - Milestone achievements
  - Error conditions
  - Hang detection alerts
- Example: `os.system('say "Starting M2 test"')` for macOS

### 3. Application State Management
- **Post-Test Protocol:** 
  - De-focus the game application after test completion
  - Return focus to VS Code for report visibility
  - Ensure clean application state between tests
- Use `NSWorkspace` to manage application switching

### 4. Hang Detection & Reporting
- Monitor operation duration for potential hangs
- Set reasonable timeouts for all operations:
  - Screen capture: 5 seconds max
  - OCR processing: 10 seconds max
  - Template matching: 3 seconds max
  - Game launch: 30 seconds max
- Report potential hangs immediately to user
- Implement graceful timeout handling

## Technical Implementation Standards

### Screen Capture Requirements
```python
# Always verify app focus before capture
def ensure_app_focus(app_name: str):
    workspace = NSWorkspace.sharedWorkspace()
    running_apps = workspace.runningApplications()
    for app in running_apps:
        if app.localizedName() == app_name:
            app.activateWithOptions_(NSApplicationActivateIgnoringOtherApps)
            time.sleep(0.5)  # Allow focus transition
            return True
    return False
```

### Audio Feedback Implementation
```python
import os

def audio_signal(message: str, voice: str = "Alex"):
    """Provide audio feedback during tests"""
    os.system(f'say -v {voice} "{message}"')

def test_milestone_audio(milestone: str, status: str):
    """Standardized audio for milestone progress"""
    audio_signal(f"Milestone {milestone} {status}")
```

### Timeout & Hang Detection
```python
import signal

class TimeoutException(Exception):
    pass

def timeout_handler(signum, frame):
    raise TimeoutException("Operation timed out")

def with_timeout(seconds):
    def decorator(func):
        def wrapper(*args, **kwargs):
            signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(seconds)
            try:
                result = func(*args, **kwargs)
                signal.alarm(0)  # Cancel alarm
                return result
            except TimeoutException:
                print(f"⚠️ HANG DETECTED: {func.__name__} exceeded {seconds}s timeout")
                return None
        return wrapper
    return decorator
```

## Testing Protocol

### Pre-Test Checklist
1. [ ] Verify game application is installed and accessible
2. [ ] Ensure VS Code is active for report viewing
3. [ ] Clear any previous test artifacts
4. [ ] Initialize audio feedback system

### During Test Execution
1. [ ] Start with audio announcement
2. [ ] Ensure app focus before each major operation
3. [ ] Monitor for hangs and report immediately
4. [ ] Provide audio progress updates for long operations

### Post-Test Protocol (CRITICAL - ALWAYS EXECUTE)
1. [ ] **MANDATORY**: Use try-finally blocks to ensure cleanup always runs
2. [ ] Close/de-focus game application (even if test failed)
3. [ ] **CRITICAL**: Return focus to VS Code (even if cleanup fails)
4. [ ] Announce test completion via audio
5. [ ] Generate and display test report
6. [ ] Update project progress documentation

**NEVER LEAVE USER STRANDED**: Always return to VS Code regardless of test outcome.

## Milestone-Specific Guidelines

### M2 - Menu Reading
- Focus Dune Legacy before screen capture
- Audio signal: "Starting menu analysis"
- Timeout: 15 seconds for full menu scan
- Audio progress: "Menu detected", "OCR complete", "Template matching done"
- Post-test: Return to VS Code with results

### M3 - Menu Navigation
- Ensure focus before each click action
- Audio signal for each navigation step
- Timeout: 30 seconds for complete navigation
- Audio feedback: "Clicking button", "Navigation successful"

### M4 - Game State Perception
- Maintain focus during gameplay analysis
- Audio updates every 10 seconds during long scans
- Timeout: 60 seconds for state vector generation
- Regular hang detection during complex analysis

## Error Handling Standards

### Graceful Degradation
- Never crash on focus loss - retry with focus restoration
- Handle OCR failures with fallback template matching
- Timeout gracefully with user notification
- Audio error reporting: "Error in [component], retrying"

### User Communication
- Clear, immediate reporting of hangs or long operations
- Audio feedback for all user-facing events
- Visual progress indicators in terminal output
- Structured error messages with suggested actions