"""
File Manager Module for JARVIS - Handles file creation and persistence
"""
import json
import os
from datetime import datetime
from typing import Dict, Any


class FileManager:
    """Manages file creation and organization for generated parts"""
    
    def __init__(self, base_path: str = 'data'):
        """Initialize file manager with base output path"""
        self.base_path = base_path
        self.parts_dir = os.path.join(base_path, 'parts')
        self.logs_dir = os.path.join(base_path, 'logs')
        self.metadata_dir = os.path.join(base_path, 'metadata')
        
        # Create directories if they don't exist
        self._ensure_directories()
        
        self.created_files = []
        self.session_log = []
    
    def _ensure_directories(self):
        """Ensure all required directories exist"""
        for directory in [self.parts_dir, self.logs_dir, self.metadata_dir]:
            os.makedirs(directory, exist_ok=True)
    
    def save_part(self, part_data: Dict[str, Any]) -> str:
        """Save a mechanical part definition to a JSON file"""
        part_name = part_data.get('name', 'unknown_part')
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{part_name}_{timestamp}.json"
        filepath = os.path.join(self.parts_dir, filename)
        
        try:
            with open(filepath, 'w') as f:
                json.dump(part_data, f, indent=2)
            
            self.created_files.append(filepath)
            self.session_log.append({
                'timestamp': timestamp,
                'action': 'part_created',
                'filename': filename,
                'part_id': part_data.get('id')
            })
            
            return filepath
        except Exception as e:
            self.session_log.append({
                'timestamp': timestamp,
                'action': 'part_creation_failed',
                'error': str(e)
            })
            raise
    
    def save_batch(self, parts: list) -> list:
        """Save multiple parts and return list of created filepaths"""
        filepaths = []
        for part in parts:
            filepath = self.save_part(part)
            filepaths.append(filepath)
        return filepaths
    
    def save_metadata(self, metadata: Dict[str, Any]) -> str:
        """Save metadata about generated parts"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"metadata_{timestamp}.json"
        filepath = os.path.join(self.metadata_dir, filename)
        
        with open(filepath, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        return filepath
    
    def save_session_log(self) -> str:
        """Save the session log to a file"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"session_log_{timestamp}.json"
        filepath = os.path.join(self.logs_dir, filename)
        
        log_data = {
            'session_start': timestamp,
            'total_files_created': len(self.created_files),
            'log_entries': self.session_log
        }
        
        with open(filepath, 'w') as f:
            json.dump(log_data, f, indent=2)
        
        return filepath
    
    def load_part(self, filepath: str) -> Dict[str, Any]:
        """Load a part definition from a JSON file"""
        with open(filepath, 'r') as f:
            return json.load(f)
    
    def list_generated_parts(self) -> list:
        """List all generated part files"""
        if not os.path.exists(self.parts_dir):
            return []
        return os.listdir(self.parts_dir)
    
    def get_session_summary(self) -> Dict[str, Any]:
        """Get a summary of the current session"""
        return {
            'files_created': len(self.created_files),
            'created_files': self.created_files,
            'log_entries': len(self.session_log),
            'session_timestamp': datetime.now().isoformat()
        }
