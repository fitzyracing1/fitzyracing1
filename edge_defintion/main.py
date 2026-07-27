"""
muvu1 - File Path Edge Orientation and Relay System
A Windows application that orients file paths to the innermost edge of the computer and relays them.
"""

import os
import sys
from pathlib import Path
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from typing import List, Optional
import threading


class FilePathRelay:
    """Core logic for file path orientation and relay."""
    
    def __init__(self):
        self.oriented_paths: List[Path] = []
        
    def orient_to_edge(self, file_path: str) -> Path:
        """
        Orient a file path to the innermost edge of the computer.
        This normalizes and resolves the path to its absolute form.
        """
        try:
            path = Path(file_path).resolve()
            return path
        except Exception as e:
            raise ValueError(f"Invalid path: {e}")
    
    def get_path_depth(self, path: Path) -> int:
        """Calculate the depth of a path from the root."""
        return len(path.parts)
    
    def relay_path(self, path: Path) -> dict:
        """
        Relay path information including depth, size, and metadata.
        """
        info = {
            'path': str(path),
            'absolute': str(path.absolute()),
            'depth': self.get_path_depth(path),
            'exists': path.exists(),
            'is_file': path.is_file() if path.exists() else False,
            'is_dir': path.is_dir() if path.exists() else False,
            'parent': str(path.parent),
            'name': path.name,
        }
        
        if path.exists():
            if path.is_file():
                info['size'] = path.stat().st_size
            info['drive'] = path.drive if path.drive else 'N/A'
        
        return info


class Muvu1App:
    """Main application GUI for muvu1."""
    
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("muvu1 - File Path Edge Orientation System")
        self.root.geometry("900x700")
        
        self.relay = FilePathRelay()
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the user interface."""
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="File Path Edge Orientation & Relay System", 
                               font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, pady=(0, 10), sticky=tk.W)
        
        # Input section
        input_frame = ttk.LabelFrame(main_frame, text="Path Input", padding="10")
        input_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        input_frame.columnconfigure(1, weight=1)
        
        ttk.Label(input_frame, text="File/Folder Path:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        
        self.path_entry = ttk.Entry(input_frame, width=50)
        self.path_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 5))
        
        ttk.Button(input_frame, text="Browse File", command=self.browse_file).grid(row=0, column=2, padx=2)
        ttk.Button(input_frame, text="Browse Folder", command=self.browse_folder).grid(row=0, column=3, padx=2)
        ttk.Button(input_frame, text="Orient & Relay", command=self.process_path).grid(row=0, column=4, padx=2)
        
        # Output section
        output_frame = ttk.LabelFrame(main_frame, text="Relayed Path Information", padding="10")
        output_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        output_frame.columnconfigure(0, weight=1)
        output_frame.rowconfigure(0, weight=1)
        
        self.output_text = scrolledtext.ScrolledText(output_frame, wrap=tk.WORD, width=80, height=25)
        self.output_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Action buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, sticky=(tk.W, tk.E))
        
        ttk.Button(button_frame, text="Clear Output", command=self.clear_output).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Exit", command=self.root.quit).pack(side=tk.RIGHT, padx=5)
        
    def browse_file(self):
        """Open file browser dialog."""
        filename = filedialog.askopenfilename(title="Select a file")
        if filename:
            self.path_entry.delete(0, tk.END)
            self.path_entry.insert(0, filename)
            
    def browse_folder(self):
        """Open folder browser dialog."""
        foldername = filedialog.askdirectory(title="Select a folder")
        if foldername:
            self.path_entry.delete(0, tk.END)
            self.path_entry.insert(0, foldername)
            
    def process_path(self):
        """Process the input path and display relay information."""
        path_str = self.path_entry.get().strip()
        
        if not path_str:
            messagebox.showwarning("Input Required", "Please enter or select a file/folder path.")
            return
        
        try:
            # Orient to edge
            oriented_path = self.relay.orient_to_edge(path_str)
            
            # Relay information
            info = self.relay.relay_path(oriented_path)
            
            # Display results
            self.display_relay_info(info)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to process path:\n{str(e)}")
            
    def display_relay_info(self, info: dict):
        """Display the relayed path information."""
        self.output_text.insert(tk.END, "="*80 + "\n")
        self.output_text.insert(tk.END, "PATH ORIENTATION & RELAY INFORMATION\n")
        self.output_text.insert(tk.END, "="*80 + "\n\n")
        
        self.output_text.insert(tk.END, f"Original Path:     {info['path']}\n")
        self.output_text.insert(tk.END, f"Absolute Path:     {info['absolute']}\n")
        self.output_text.insert(tk.END, f"Path Depth:        {info['depth']} levels from root\n")
        self.output_text.insert(tk.END, f"Parent Directory:  {info['parent']}\n")
        self.output_text.insert(tk.END, f"Name:              {info['name']}\n")
        self.output_text.insert(tk.END, f"Exists:            {'Yes' if info['exists'] else 'No'}\n")
        self.output_text.insert(tk.END, f"Type:              {'File' if info['is_file'] else 'Directory' if info['is_dir'] else 'N/A'}\n")
        
        if 'drive' in info:
            self.output_text.insert(tk.END, f"Drive:             {info['drive']}\n")
        
        if 'size' in info:
            size_kb = info['size'] / 1024
            size_mb = size_kb / 1024
            if size_mb > 1:
                self.output_text.insert(tk.END, f"Size:              {size_mb:.2f} MB ({info['size']} bytes)\n")
            else:
                self.output_text.insert(tk.END, f"Size:              {size_kb:.2f} KB ({info['size']} bytes)\n")
        
        self.output_text.insert(tk.END, "\n")
        self.output_text.see(tk.END)
        
    def clear_output(self):
        """Clear the output text area."""
        self.output_text.delete(1.0, tk.END)


def main():
    """Main entry point for the application."""
    root = tk.Tk()
    app = Muvu1App(root)
    root.mainloop()


if __name__ == "__main__":
    main()
