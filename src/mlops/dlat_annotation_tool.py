"""
DUNE LEGACY ANNOTATION TOOLKIT (DLAT)
Module 6.3: Human-in-the-Loop Annotation Tool for YOLOv8 Training Data

This tool provides a graphical interface for the Master to annotate game interface
screenshots with bounding boxes and hierarchical labels for ML training.

Features:
- PIL image display and manipulation  
- Interactive bounding box drawing
- Hierarchical labeling (Class + Semantic Value)
- Schema Sketch integration for M3D support
- YOLO format output with normalized coordinates
- Versioned dataset output for direct ML consumption

Author: Agent B
Version: 1.0
Compliance: AIP-SDS-V2.3, MODULE 6.3 specifications
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
from PIL import Image, ImageTk, ImageDraw
import json
import os
from datetime import datetime
from typing import List, Dict, Tuple, Optional
import numpy as np


class BoundingBox:
    """Represents a labeled bounding box with hierarchical annotation"""
    
    def __init__(self, x1: int, y1: int, x2: int, y2: int, 
                 class_label: str, semantic_value: str, class_id: int = 0):
        self.x1 = min(x1, x2)
        self.y1 = min(y1, y2)
        self.x2 = max(x1, x2) 
        self.y2 = max(y1, y2)
        self.class_label = class_label
        self.semantic_value = semantic_value
        self.class_id = class_id
        
    def get_normalized_coords(self, image_width: int, image_height: int) -> Tuple[float, float, float, float]:
        """Convert to YOLO format: center_x, center_y, width, height (normalized 0-1)"""
        center_x = ((self.x1 + self.x2) / 2) / image_width
        center_y = ((self.y1 + self.y2) / 2) / image_height
        width = (self.x2 - self.x1) / image_width
        height = (self.y2 - self.y1) / image_height
        return center_x, center_y, width, height
        
    def to_dict(self) -> Dict:
        """Export to dictionary for JSON serialization"""
        return {
            'bbox': [self.x1, self.y1, self.x2, self.y2],
            'class_label': self.class_label,
            'semantic_value': self.semantic_value,
            'class_id': self.class_id
        }


class DLATAnnotationTool:
    """Dune Legacy Annotation Toolkit - Main GUI Application"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("DLAT - Dune Legacy Annotation Toolkit v1.0")
        self.root.geometry("1400x900")
        
        # Application state
        self.current_image: Optional[Image.Image] = None
        self.current_image_path: str = ""
        self.photo_image: Optional[ImageTk.PhotoImage] = None
        self.canvas_image = None
        
        # Annotation state
        self.bounding_boxes: List[BoundingBox] = []
        self.current_box_start: Optional[Tuple[int, int]] = None
        self.current_box_rect = None
        self.schema_sketch: str = ""
        
        # Class management
        self.class_labels = ["Button", "Unit Icon", "Resource Counter", "Text Label", "Menu Item"]
        self.class_id_map = {label: idx for idx, label in enumerate(self.class_labels)}
        
        self.setup_ui()
        self.setup_bindings()
        
    def setup_ui(self):
        """Initialize the GUI components"""
        
        # Main frame layout
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Left panel - Controls
        control_frame = ttk.Frame(main_frame, width=300)
        control_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        control_frame.pack_propagate(False)
        
        # File operations
        file_frame = ttk.LabelFrame(control_frame, text="File Operations", padding=10)
        file_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(file_frame, text="Load Image", command=self.load_image).pack(fill=tk.X, pady=2)
        ttk.Button(file_frame, text="Save Annotations", command=self.save_annotations).pack(fill=tk.X, pady=2)
        ttk.Button(file_frame, text="Load Annotations", command=self.load_annotations).pack(fill=tk.X, pady=2)
        ttk.Button(file_frame, text="Export YOLO", command=self.export_yolo).pack(fill=tk.X, pady=2)
        
        # Schema sketch input
        schema_frame = ttk.LabelFrame(control_frame, text="Schema Sketch (M3D Support)", padding=10)
        schema_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(schema_frame, text="High-level description:").pack(anchor=tk.W)
        self.schema_text = tk.Text(schema_frame, height=4, wrap=tk.WORD)
        self.schema_text.pack(fill=tk.X, pady=2)
        
        ttk.Button(schema_frame, text="Set Schema", command=self.set_schema_sketch).pack(fill=tk.X, pady=2)
        
        # Class management
        class_frame = ttk.LabelFrame(control_frame, text="Class Labels", padding=10)
        class_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.class_listbox = tk.Listbox(class_frame, height=6)
        for label in self.class_labels:
            self.class_listbox.insert(tk.END, label)
        self.class_listbox.pack(fill=tk.X, pady=2)
        
        ttk.Button(class_frame, text="Add Class", command=self.add_class_label).pack(fill=tk.X, pady=2)
        ttk.Button(class_frame, text="Remove Class", command=self.remove_class_label).pack(fill=tk.X, pady=2)
        
        # Current annotations
        anno_frame = ttk.LabelFrame(control_frame, text="Current Annotations", padding=10)
        anno_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        self.anno_listbox = tk.Listbox(anno_frame)
        scrollbar = ttk.Scrollbar(anno_frame, orient=tk.VERTICAL, command=self.anno_listbox.yview)
        self.anno_listbox.configure(yscrollcommand=scrollbar.set)
        
        self.anno_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        ttk.Button(anno_frame, text="Delete Selected", command=self.delete_annotation).pack(fill=tk.X, pady=2)
        ttk.Button(anno_frame, text="Clear All", command=self.clear_annotations).pack(fill=tk.X, pady=2)
        
        # Right panel - Canvas
        canvas_frame = ttk.Frame(main_frame)
        canvas_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Canvas with scrollbars
        self.canvas = tk.Canvas(canvas_frame, bg='gray90', cursor='crosshair')
        
        h_scrollbar = ttk.Scrollbar(canvas_frame, orient=tk.HORIZONTAL, command=self.canvas.xview)
        v_scrollbar = ttk.Scrollbar(canvas_frame, orient=tk.VERTICAL, command=self.canvas.yview)
        
        self.canvas.configure(xscrollcommand=h_scrollbar.set, yscrollcommand=v_scrollbar.set)
        
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Status bar
        self.status_label = ttk.Label(self.root, text="Ready - Load an image to begin annotation")
        self.status_label.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=5)
        
    def setup_bindings(self):
        """Setup event bindings for interactive annotation"""
        self.canvas.bind("<Button-1>", self.start_bbox)
        self.canvas.bind("<B1-Motion>", self.update_bbox)
        self.canvas.bind("<ButtonRelease-1>", self.finish_bbox)
        
    def load_image(self):
        """Load an image file for annotation"""
        file_path = filedialog.askopenfilename(
            title="Select Game Interface Screenshot",
            filetypes=[
                ("Image files", "*.png *.jpg *.jpeg *.bmp *.gif"),
                ("PNG files", "*.png"),
                ("JPEG files", "*.jpg *.jpeg"),
                ("All files", "*.*")
            ]
        )
        
        if file_path:
            try:
                self.current_image = Image.open(file_path)
                self.current_image_path = file_path
                self.display_image()
                self.clear_annotations()
                self.status_label.config(text=f"Loaded: {os.path.basename(file_path)}")
                
                # Auto-prompt for schema sketch
                if not self.schema_sketch:
                    messagebox.showinfo("Schema Sketch", 
                                      "Please provide a high-level description of this interface in the Schema Sketch panel.")
                    
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load image: {str(e)}")
                
    def display_image(self):
        """Display the current image on canvas"""
        if self.current_image:
            # Convert to PhotoImage for display
            self.photo_image = ImageTk.PhotoImage(self.current_image)
            
            # Update canvas scroll region
            self.canvas.configure(scrollregion=(0, 0, self.current_image.width, self.current_image.height))
            
            # Clear previous image and display new one
            self.canvas.delete("all")
            self.canvas_image = self.canvas.create_image(0, 0, anchor=tk.NW, image=self.photo_image)
            
            # Redraw existing bounding boxes
            self.redraw_bboxes()
            
    def start_bbox(self, event):
        """Start drawing a new bounding box"""
        if self.current_image:
            # Convert canvas coordinates to image coordinates
            x = self.canvas.canvasx(event.x)
            y = self.canvas.canvasy(event.y) 
            self.current_box_start = (int(x), int(y))
            
    def update_bbox(self, event):
        """Update the current bounding box during drag"""
        if self.current_box_start and self.current_image:
            x = self.canvas.canvasx(event.x)
            y = self.canvas.canvasy(event.y)
            
            # Remove previous temporary rectangle
            if self.current_box_rect:
                self.canvas.delete(self.current_box_rect)
                
            # Draw new temporary rectangle
            self.current_box_rect = self.canvas.create_rectangle(
                self.current_box_start[0], self.current_box_start[1],
                x, y, outline='red', width=2, tags='temp_bbox'
            )
            
    def finish_bbox(self, event):
        """Finish drawing bounding box and prompt for labels"""
        if self.current_box_start and self.current_image:
            x = self.canvas.canvasx(event.x)
            y = self.canvas.canvasy(event.y)
            
            # Ensure minimum box size
            if abs(x - self.current_box_start[0]) < 10 or abs(y - self.current_box_start[1]) < 10:
                self.canvas.delete(self.current_box_rect)
                self.current_box_start = None
                self.current_box_rect = None
                return
                
            # Prompt for hierarchical labels
            labels = self.get_hierarchical_labels()
            if labels:
                class_label, semantic_value = labels
                class_id = self.class_id_map.get(class_label, 0)
                
                # Create bounding box
                bbox = BoundingBox(
                    self.current_box_start[0], self.current_box_start[1],
                    int(x), int(y),
                    class_label, semantic_value, class_id
                )
                
                self.bounding_boxes.append(bbox)
                self.update_annotation_list()
                self.redraw_bboxes()
                
                self.status_label.config(text=f"Added annotation: {class_label} - {semantic_value}")
            
            # Cleanup
            self.canvas.delete(self.current_box_rect)
            self.current_box_start = None  
            self.current_box_rect = None
            
    def get_hierarchical_labels(self) -> Optional[Tuple[str, str]]:
        """Prompt user for hierarchical labels: Class + Semantic Value"""
        
        # Class Label Dialog
        class_dialog = ClassSelectionDialog(self.root, self.class_labels)
        class_label = class_dialog.result
        
        if not class_label:
            return None
            
        # Semantic Value Dialog  
        semantic_value = simpledialog.askstring(
            "Semantic Value",
            f"Enter semantic value for {class_label}:\n"
            f"Examples:\n"
            f"- Button: 'Single Player', 'Options', 'Quit'\n" 
            f"- Resource Counter: '450', '1200'\n"
            f"- Unit Icon: 'Infantry ID: 4', 'Tank ID: 7'",
            parent=self.root
        )
        
        if not semantic_value:
            return None
            
        return class_label, semantic_value
        
    def redraw_bboxes(self):
        """Redraw all bounding boxes on canvas"""
        # Remove existing bbox drawings
        self.canvas.delete('bbox')
        
        # Draw each bounding box
        for i, bbox in enumerate(self.bounding_boxes):
            # Draw rectangle
            rect = self.canvas.create_rectangle(
                bbox.x1, bbox.y1, bbox.x2, bbox.y2,
                outline='blue', width=2, tags='bbox'
            )
            
            # Draw label
            label_text = f"{bbox.class_label}: {bbox.semantic_value}"
            self.canvas.create_text(
                bbox.x1, bbox.y1 - 10,
                anchor=tk.SW, text=label_text,
                fill='blue', font=('Arial', 10, 'bold'),
                tags='bbox'
            )
            
    def update_annotation_list(self):
        """Update the annotation listbox"""
        self.anno_listbox.delete(0, tk.END)
        for i, bbox in enumerate(self.bounding_boxes):
            label = f"{i+1}: {bbox.class_label} - {bbox.semantic_value}"
            self.anno_listbox.insert(tk.END, label)
            
    def delete_annotation(self):
        """Delete selected annotation"""
        selection = self.anno_listbox.curselection()
        if selection:
            index = selection[0]
            del self.bounding_boxes[index]
            self.update_annotation_list()
            self.redraw_bboxes()
            self.status_label.config(text="Deleted selected annotation")
            
    def clear_annotations(self):
        """Clear all annotations"""
        self.bounding_boxes.clear()
        self.update_annotation_list()
        self.redraw_bboxes()
        self.status_label.config(text="Cleared all annotations")
        
    def set_schema_sketch(self):
        """Set the schema sketch from text input"""
        self.schema_sketch = self.schema_text.get("1.0", tk.END).strip()
        if self.schema_sketch:
            messagebox.showinfo("Schema Set", "Schema sketch saved successfully")
            self.status_label.config(text="Schema sketch updated")
        else:
            messagebox.showwarning("Empty Schema", "Please enter a description first")
            
    def add_class_label(self):
        """Add a new class label"""
        new_label = simpledialog.askstring("New Class", "Enter new class label:")
        if new_label and new_label not in self.class_labels:
            self.class_labels.append(new_label)
            self.class_id_map[new_label] = len(self.class_labels) - 1
            self.class_listbox.insert(tk.END, new_label)
            self.status_label.config(text=f"Added class: {new_label}")
            
    def remove_class_label(self):
        """Remove selected class label"""
        selection = self.class_listbox.curselection()
        if selection:
            index = selection[0]
            label = self.class_labels[index]
            
            # Check if label is in use
            in_use = any(bbox.class_label == label for bbox in self.bounding_boxes)
            if in_use:
                messagebox.showerror("Cannot Remove", f"Class '{label}' is currently in use by annotations")
                return
                
            # Remove from lists
            del self.class_labels[index]
            self.class_listbox.delete(index)
            
            # Rebuild class ID map
            self.class_id_map = {label: idx for idx, label in enumerate(self.class_labels)}
            self.status_label.config(text=f"Removed class: {label}")
            
    def save_annotations(self):
        """Save annotations to JSON file"""
        if not self.current_image_path:
            messagebox.showwarning("No Image", "Load an image first")
            return
            
        save_path = filedialog.asksaveasfilename(
            title="Save Annotations",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if save_path:
            try:
                # Prepare annotation data
                annotation_data = {
                    'metadata': {
                        'image_path': self.current_image_path,
                        'image_size': [self.current_image.width, self.current_image.height],
                        'schema_sketch': self.schema_sketch,
                        'timestamp': datetime.now().isoformat(),
                        'annotator': 'DLAT-v1.0',
                        'class_labels': self.class_labels
                    },
                    'annotations': [bbox.to_dict() for bbox in self.bounding_boxes]
                }
                
                # Save to file
                with open(save_path, 'w') as f:
                    json.dump(annotation_data, f, indent=2)
                    
                self.status_label.config(text=f"Saved annotations: {os.path.basename(save_path)}")
                messagebox.showinfo("Saved", f"Annotations saved to {save_path}")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save annotations: {str(e)}")
                
    def load_annotations(self):
        """Load annotations from JSON file"""
        file_path = filedialog.askopenfilename(
            title="Load Annotations",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    
                # Load metadata
                metadata = data.get('metadata', {})
                self.schema_sketch = metadata.get('schema_sketch', '')
                self.schema_text.delete("1.0", tk.END)
                self.schema_text.insert("1.0", self.schema_sketch)
                
                # Load class labels if available
                if 'class_labels' in metadata:
                    self.class_labels = metadata['class_labels']
                    self.class_id_map = {label: idx for idx, label in enumerate(self.class_labels)}
                    
                    self.class_listbox.delete(0, tk.END)
                    for label in self.class_labels:
                        self.class_listbox.insert(tk.END, label)
                
                # Load annotations
                self.bounding_boxes.clear()
                for anno_data in data.get('annotations', []):
                    bbox_coords = anno_data['bbox']
                    bbox = BoundingBox(
                        bbox_coords[0], bbox_coords[1], bbox_coords[2], bbox_coords[3],
                        anno_data['class_label'], anno_data['semantic_value'],
                        anno_data.get('class_id', 0)
                    )
                    self.bounding_boxes.append(bbox)
                    
                self.update_annotation_list()
                self.redraw_bboxes()
                
                self.status_label.config(text=f"Loaded annotations: {os.path.basename(file_path)}")
                messagebox.showinfo("Loaded", f"Loaded {len(self.bounding_boxes)} annotations")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load annotations: {str(e)}")
                
    def export_yolo(self):
        """Export annotations in YOLO format"""
        if not self.current_image or not self.bounding_boxes:
            messagebox.showwarning("No Data", "Load image and create annotations first")
            return
            
        save_path = filedialog.asksaveasfilename(
            title="Export YOLO Format",
            defaultextension=".txt", 
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if save_path:
            try:
                with open(save_path, 'w') as f:
                    for bbox in self.bounding_boxes:
                        # Get normalized YOLO coordinates
                        center_x, center_y, width, height = bbox.get_normalized_coords(
                            self.current_image.width, self.current_image.height
                        )
                        
                        # Write YOLO format: class_id center_x center_y width height
                        f.write(f"{bbox.class_id} {center_x:.6f} {center_y:.6f} {width:.6f} {height:.6f}\n")
                        
                # Also save class names file
                class_file = save_path.replace('.txt', '_classes.txt')
                with open(class_file, 'w') as f:
                    for label in self.class_labels:
                        f.write(f"{label}\n")
                        
                self.status_label.config(text=f"Exported YOLO: {os.path.basename(save_path)}")
                messagebox.showinfo("Exported", 
                                  f"YOLO format exported:\n{save_path}\n{class_file}")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export YOLO: {str(e)}")
                
    def run(self):
        """Start the GUI application"""
        self.root.mainloop()


class ClassSelectionDialog:
    """Custom dialog for class label selection"""
    
    def __init__(self, parent, class_labels):
        self.result = None
        
        # Create dialog window
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Select Class Label")
        self.dialog.geometry("300x400")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center the dialog
        self.dialog.geometry("+%d+%d" % (
            parent.winfo_rootx() + 50,
            parent.winfo_rooty() + 50
        ))
        
        # Create UI
        ttk.Label(self.dialog, text="Select class label for this element:").pack(pady=10)
        
        # Listbox for class selection
        self.listbox = tk.Listbox(self.dialog, height=10)
        for label in class_labels:
            self.listbox.insert(tk.END, label)
        self.listbox.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Buttons
        button_frame = ttk.Frame(self.dialog)
        button_frame.pack(pady=10)
        
        ttk.Button(button_frame, text="OK", command=self.ok_clicked).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=self.cancel_clicked).pack(side=tk.LEFT, padx=5)
        
        # Bind double-click
        self.listbox.bind("<Double-Button-1>", lambda e: self.ok_clicked())
        
        # Wait for result
        self.dialog.wait_window()
        
    def ok_clicked(self):
        selection = self.listbox.curselection()
        if selection:
            self.result = self.listbox.get(selection[0])
        self.dialog.destroy()
        
    def cancel_clicked(self):
        self.dialog.destroy()


def main():
    """Main entry point for DLAT"""
    try:
        # Initialize and run the annotation tool
        app = DLATAnnotationTool()
        app.run()
        
    except Exception as e:
        print(f"DLAT Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()