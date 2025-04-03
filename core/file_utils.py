import os
import sys
import chardet
from pathlib import Path

def normalize_path(file_path):
    """Normalize file path to handle different encodings and formats"""
    try:
        # Convert to Path object which handles various path formats better
        path = Path(file_path)
        return str(path.absolute())
    except Exception as e:
        print(f"Error normalizing path: {e}")
        return file_path

def read_file_with_auto_encoding(file_path):
    """Read a file with automatic encoding detection"""
    try:
        # First detect the encoding
        with open(file_path, 'rb') as f:
            raw_data = f.read()
            result = chardet.detect(raw_data)
            encoding = result['encoding'] or 'utf-8'
        
        # Then read with detected encoding
        with open(file_path, 'r', encoding=encoding) as f:
            return f.read(), None
    except Exception as e:
        return None, str(e)
        
def write_file_with_encoding(file_path, content, encoding='utf-8'):
    """Write content to file with specified encoding"""
    try:
        with open(file_path, 'w', encoding=encoding) as f:
            f.write(content)
        return True, None
    except Exception as e:
        return False, str(e)
