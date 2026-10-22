import json
import re
import os
from executor import create_file, replace_file, read_file as exec_read_file, list_files, run_shell, web_search, git_clone
from file_manager import read_file, read_file_chunked, search_in_file, list_directory
from code_analyzer import find_functions, find_ui_elements, find_api_calls, find_imports
from deepseek_client import chat
from verifier import full_verification

def check_file(path: str):
    return full_verification(path)

def make_absolute(path):
    if re.match(r'^[A-Za-z]:[\\/]', path):
        return path
    return "D:/projects/" + path.lstrip("/")

def execute_task(user_input, conversation_history=None):
    if conversation_history is None:
        conversation_history = []
    
    text = user_input.strip()
    
    # === ПРЯМЫЕ КОМАНДЫ ===
    m = re.search(r'прочитай\s+(?:файл\s+)?["\']?([^"\'\n]+)["\']?', text, re.IGNORECASE)
    if m:
        path = make_absolute(m.group(1).strip())
        content, error = read_file(path)
        if error:
            return f"Ошибка: {error}", conversation_history
        return content, conversation_history
    
    m = re.search(r'найди\s+строки\s+["\'](.+?)["\']\s+в\s+файле\s+["\']?([^"\'\n]+)["\']?', text, re.IGNORECASE)
    if m:
        pattern = m.group(1)
        path = make_absolute(m.group(2).strip())
        matches, error = search_in_file(path, pattern)
        if error:
            return f"Ошибка: {error}", conversation_history
        if not matches:
            return f"Строки '{pattern}' не найдены в {path}", conversation_history
        result = f"Найдено {len(matches)} строк:\n"
        for line_num, line in matches[:20]:
            result += f"  Строка {line_num}: {line}\n"
        return result, conversation_history
    
    m = re.search(r'покажи\s+(?:кнопки|UI)\s+в\s+файле\s+["\']?([^"\'\n]+)["\']?', text, re.IGNORECASE)
    if m:
        path = make_absolute(m.group(1).strip())
        content, error = read_file(path)
        if error:
            return f"Ошибка: {error}", conversation_history
        buttons = find_ui_elements(content)
        if not buttons:
            return "Кнопки не найдены", conversation_history
        result = f"Найдено {len(buttons)} кнопок:\n"
        for btn in buttons:
            result += f"  - {btn}\n"
        return result, conversation_history
    
    m = re.search(r'покажи\s+(?:функции|методы)\s+в\s+файле\s+["\']?([^"\'\n]+)["\']?', text, re.IGNORECASE)
    if m:
        path = make_absolute(m.group(1).strip())
        content, error = read_file(path)
        if error:
            return f"Ошибка: {error}", conversation_history
        ext = path.split('.')[-1]
        lang = "java" if ext == "java" else "javascript"
        funcs = find_functions(content, lang)
        if not funcs:
            return "Функции не найдены", conversation_history
        result = f"Найдено {len(funcs)} функций/методов:\n"
        for f in funcs:
            result += f"  - {f}\n"
        return result, conversation_history
    
    m = re.search(r'покажи\s+(?:API|вызовы)\s+в\s+файле\s+["\']?([^"\'\n]+)["\']?', text, re.IGNORECASE)
    if m:
        path = make_absolute(m.group(1).strip())
        content, error = read_file(path)
        if error:
            return f"Ошибка: {error}", conversation_history
        calls = find_api_calls(content)
        if not calls:
            return "API-вызовы не найдены", conversation_history
        result = f"Найдено {len(calls)} вызовов API:\n"
        for c in calls:
            result += f"  - {c}\n"
        return result, conversation_history
    
    m = re.search(r'покажи\s+(?:содержимое|список)\s+(?:папки|директории)\s+["\']?([^"\'\n]+)["\']?', text, re.IGNORECASE)
    if m:
        path = make_absolute(m.group(1).strip())
        items, error = list_directory(path)
        if error:
            return f"Ошибка: {error}", conversation_history
        result = f"Содержимое '{path}':\n"
        for item in items:
            result += f"  {item}\n"
        return result, conversation_history
    
    # === ЗАПИСЬ ФАЙЛОВ ===
    m = re.search(r'(?:создай|запиши|write)\s+(?:файл\s+)?["\']?([^"\'\n]+)["\']?\s+(?:с\s+содержимым|содержимое|content)\s*[:=]?\s*["\'](.+)["\']', text, re.IGNORECASE | re.DOTALL)
    if m:
        path = make_absolute(m.group(1).strip())
        content = m.group(2)
        result = create_file(path, content)
        return result, conversation_history

    m = re.search(r'(?:замени|перезапиши|replace)\s+(?:файл\s+)?["\']?([^"\'\n]+)["\']?\s+(?:на|с\s+содержимым|содержимое|content)\s*[:=]?\s*["\'](.+)["\']', text, re.IGNORECASE | re.DOTALL)
    if m:
        path = make_absolute(m.group(1).strip())
        content = m.group(2)
        result = replace_file(path, content)
        return result, conversation_history

    m = re.search(r'выполни\s+(?:команду\s+)?(.+)', text, re.IGNORECASE | re.DOTALL)
    if m:
        command = m.group(1).strip().strip('"').strip("'")
        return run_shell(command), conversation_history
    
    m = re.search(r'найди\s+в\s+интернете\s+(.+)', text, re.IGNORECASE | re.DOTALL)
    if m:
        query = m.group(1).strip().strip('"').strip("'")
        return web_search(query), conversation_history
    
    m = re.search(r'проверь\s+(?:файл\s+)?["\']?([^"\'\n]+)["\']?', text, re.IGNORECASE)
    if m:
        path = make_absolute(m.group(1).strip())
        return check_file(path), conversation_history
    
    # === DeepSeek API для сложных запросов ===
    reply = chat([{"role": "user", "content": user_input}])
    if reply:
        return reply, conversation_history
    
    return "Модель недоступна.", conversation_history