import os
import re
from config import ALLOWED_PATHS, CACHE_DIR

def safe_path(path):
    return any(path.startswith(p) for p in ALLOWED_PATHS)

def read_file(path):
    if not safe_path(path):
        return None, "Безопасность: путь запрещён"
    if not os.path.exists(path):
        return None, "Файл не найден"
    try:
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        return content, None
    except Exception as e:
        return None, str(e)

def read_file_chunked(path, max_chars=4000):
    """Читает файл и разбивает на части для анализа."""
    content, error = read_file(path)
    if error:
        return [], error
    
    chunks = []
    lines = content.split('\n')
    current_chunk = ""
    for line in lines:
        if len(current_chunk) + len(line) < max_chars:
            current_chunk += line + '\n'
        else:
            chunks.append(current_chunk)
            current_chunk = line + '\n'
    if current_chunk:
        chunks.append(current_chunk)
    return chunks, None

def search_in_file(path, pattern, case_sensitive=False):
    """Ищет строки по регулярному выражению в файле."""
    content, error = read_file(path)
    if error:
        return [], error
    
    flags = 0 if case_sensitive else re.IGNORECASE
    matches = []
    for i, line in enumerate(content.split('\n'), 1):
        if re.search(pattern, line, flags):
            matches.append((i, line.strip()))
    return matches, None

def list_directory(path):
    if not safe_path(path):
        return None, "Безопасность: путь запрещён"
    if not os.path.isdir(path):
        return None, "Не папка"
    items = os.listdir(path)
    items.sort()
    return items, None