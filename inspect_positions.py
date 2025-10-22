#!/usr/bin/env python3
"""
Manual Button Position Inspector
Creates a grid overlay on the Dune Legacy screenshot to help identify correct button positions
"""

import cv2
import numpy as np
import subprocess

def audio_signal(message):
    """Provide audio feedback."""
    try:
        subprocess.run(['say', message], capture_output=True, timeout=3)
    except:
        print(f"🔊 Audio: {message}")

def create_inspection_grid(screenshot_path):
    """Create a grid overlay to help identify button positions."""
    print("📏 CREATING POSITION INSPECTION GRID")
    print("=" * 40)
    
    img = cv2.imread(screenshot_path)
    if img is None:
        print(f"❌ Could not load screenshot: {screenshot_path}")
        return
    
    height, width = img.shape[:2]
    print(f"📐 Image dimensions: {width}x{height}")
    
    # Create overlay
    overlay = img.copy()
    
    # Draw grid lines every 10% of screen
    grid_color = (255, 255, 0)  # Cyan
    line_thickness = 1
    
    # Vertical lines
    for i in range(1, 10):
        x = int(i * 0.1 * width)
        cv2.line(overlay, (x, 0), (x, height), grid_color, line_thickness)
        # Add percentage labels
        cv2.putText(overlay, f"{i*10}%", (x + 5, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, grid_color, 1)
    
    # Horizontal lines  
    for i in range(1, 10):
        y = int(i * 0.1 * height)
        cv2.line(overlay, (0, y), (width, y), grid_color, line_thickness)
        # Add percentage labels
        cv2.putText(overlay, f"{i*10}%", (10, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.6, grid_color, 1)
    
    # Add coordinate markers at key positions
    markers = [
        # Check common game menu positions
        (0.2, 0.3), (0.2, 0.4), (0.2, 0.5), (0.2, 0.6), (0.2, 0.7), (0.2, 0.8),
        (0.5, 0.3), (0.5, 0.4), (0.5, 0.5), (0.5, 0.6), (0.5, 0.7), (0.5, 0.8),
        (0.8, 0.3), (0.8, 0.4), (0.8, 0.5), (0.8, 0.6), (0.8, 0.7), (0.8, 0.8)
    ]
    
    for x_norm, y_norm in markers:
        x = int(x_norm * width)
        y = int(y_norm * height)
        cv2.circle(overlay, (x, y), 8, (0, 0, 255), -1)  # Red dots
        cv2.putText(overlay, f"({x_norm:.1f},{y_norm:.1f})", (x + 10, y), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 255), 1)
    
    # Draw our current button predictions with different color
    current_buttons = {
        "SP": (0.35, 0.35, 0.30, 0.08),     # Single Player
        "MP": (0.35, 0.45, 0.30, 0.08),     # Multiplayer  
        "OP": (0.35, 0.55, 0.30, 0.08),     # Options
        "ME": (0.35, 0.65, 0.30, 0.08),     # Map Editor
        "RP": (0.35, 0.75, 0.30, 0.08),     # Replay
        "QT": (0.35, 0.85, 0.30, 0.08)      # Quit
    }
    
    for name, (x_norm, y_norm, w_norm, h_norm) in current_buttons.items():
        x = int(x_norm * width)
        y = int(y_norm * height)
        w = int(w_norm * width)
        h = int(h_norm * height)
        
        # Draw rectangle for our current prediction
        cv2.rectangle(overlay, (x, y), (x + w, y + h), (255, 0, 255), 2)  # Magenta
        cv2.putText(overlay, f"{name}", (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 255), 2)
    
    # Blend overlay with original
    alpha = 0.7
    result = cv2.addWeighted(img, alpha, overlay, 1 - alpha, 0)
    
    # Save result
    output_path = "/tmp/dune_legacy_grid_inspection.png"
    cv2.imwrite(output_path, result)
    
    print(f"📸 Grid inspection image saved: {output_path}")
    print("\n📋 Legend:")
    print("   🟡 Yellow grid: 10% increments")
    print("   🔴 Red dots: Common menu positions")
    print("   🟣 Magenta rectangles: Our current predictions")
    print("\nOpen the image to visually identify where the actual buttons are!")
    
    return output_path

def main():
    """Create inspection grid for manual button identification."""
    audio_signal("Creating position inspection grid")
    
    # Capture fresh screenshot
    subprocess.run(['screencapture', '-x', '/tmp/dune_legacy_inspection.png'], capture_output=True)
    
    # Create grid
    grid_path = create_inspection_grid('/tmp/dune_legacy_inspection.png')
    
    if grid_path:
        audio_signal("Grid created, opening for inspection")
        # Note: Don't automatically open to avoid focus issues
        print(f"\n✅ Inspection grid ready: {grid_path}")
        print("Examine the image to identify correct button positions!")
    
if __name__ == "__main__":
    main()