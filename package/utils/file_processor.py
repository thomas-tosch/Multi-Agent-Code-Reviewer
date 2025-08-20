import os
import zipfile
import tempfile
from typing import Any, Dict, List, Optional
import logging

from ..config import ALLOWED_EXTENSIONS, MAX_FILES_PER_UPLOAD, MAX_FILE_SIZE

logger = logging.getLogger(__name__)

class FileProcessor:
    
    def extract_zip(self, zip_path: str) -> Dict[str, str]:
        files = {}
        
        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                file_list = zip_ref.namelist()
                
                valid_files = self._filter_valid_files(file_list)
                
                if len(valid_files) > MAX_FILES_PER_UPLOAD:
                    logger.warning(f"Limiting to first {MAX_FILES_PER_UPLOAD} files")
                    valid_files = valid_files[:MAX_FILES_PER_UPLOAD]
                
                for filepath in valid_files:
                    try:
                        with zip_ref.open(filepath) as f:
                            content = f.read()
                            
                            if len(content) > MAX_FILE_SIZE:
                                logger.warning(f"Skipping {filepath}: file too large")
                                continue
                            
                            files[filepath] = content.decode('utf-8', errors='ignore')
                            
                    except Exception as e:
                        logger.error(f"Error reading {filepath}: {str(e)}")
                        continue
                
                logger.info(f"Extracted {len(files)} files from ZIP")
                
        except zipfile.BadZipFile:
            logger.error("Invalid ZIP file")
            raise ValueError("Invalid ZIP file format")
        except Exception as e:
            logger.error(f"Error extracting ZIP: {str(e)}")
            raise
        
        return files
    
    def _filter_valid_files(self, file_list: List[str]) -> List[str]:
        valid_files = []
        
        for filepath in file_list:
            if filepath.endswith('/'):
                continue
            
            if self._should_skip_file(filepath):
                continue
            
            ext = os.path.splitext(filepath)[1]
            if ext in ALLOWED_EXTENSIONS:
                valid_files.append(filepath)
        
        return valid_files
    
    def _should_skip_file(self, filepath: str) -> bool:
        skip_patterns = [
            '__pycache__',
            '.git',
            'node_modules',
            '.venv',
            'venv',
            '.env',
            '.pyc',
            '.pyo',
            '.pyd',
            '.so',
            '.dll',
            '.exe',
            '.bin',
            '.lock',
            '.log',
            '.tmp'
        ]
        
        filepath_lower = filepath.lower()
        return any(pattern in filepath_lower for pattern in skip_patterns)
    
    def detect_project_structure(self, files: Dict[str, str]) -> Dict[str, Any]:
        structure = {
            "total_files": len(files),
            "file_types": {},
            "directories": set(),
            "has_tests": False,
            "has_config": False,
            "entry_points": [],
            "dependencies": []
        }
        
        for filepath in files.keys():
            ext = os.path.splitext(filepath)[1]
            structure["file_types"][ext] = structure["file_types"].get(ext, 0) + 1
            
            dir_path = os.path.dirname(filepath)
            if dir_path:
                structure["directories"].add(dir_path)
            
            filename = os.path.basename(filepath).lower()
            
            if 'test' in filename or 'spec' in filename:
                structure["has_tests"] = True
            
            if filename in ['config.py', 'settings.py', '.env', 'config.json']:
                structure["has_config"] = True
            
            if filename in ['main.py', 'app.py', 'index.js', 'main.java']:
                structure["entry_points"].append(filepath)
            
            if filename in ['requirements.txt', 'package.json', 'pom.xml', 'go.mod']:
                structure["dependencies"].append(filepath)
        
        structure["directories"] = list(structure["directories"])
        
        return structure
    
    def create_file_graph(self, files: Dict[str, str]) -> Dict[str, List[str]]:
        graph = {}
        
        for filepath, content in files.items():
            imports = self._extract_imports(content, filepath)
            
            dependencies = []
            for import_name in imports:
                for other_file in files.keys():
                    if import_name in other_file:
                        dependencies.append(other_file)
            
            graph[filepath] = dependencies
        
        return graph
    
    def _extract_imports(self, content: str, filepath: str) -> List[str]:
        imports = []
        ext = os.path.splitext(filepath)[1]
        
        lines = content.split('\n')
        
        if ext == '.py':
            for line in lines:
                line = line.strip()
                if line.startswith('import ') or line.startswith('from '):
                    parts = line.split()
                    if len(parts) > 1:
                        imports.append(parts[1].split('.')[0])
        
        elif ext in ['.js', '.ts']:
            for line in lines:
                line = line.strip()
                if line.startswith('import ') or line.startswith('const ') and 'require(' in line:
                    if 'from' in line:
                        parts = line.split('from')
                        if len(parts) > 1:
                            module = parts[1].strip().strip(';').strip('"').strip("'")
                            imports.append(module)
        
        return imports
