import json
import os

HISTORY_FILE = "D:/RunJobAgent/history.json"
MAX_MESSAGES = 100  # максимум сообщений (можно увеличить позже)

def load_history():
    """Загружает историю из файла. Возвращает список сообщений."""
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list):
                    return data[-MAX_MESSAGES:]  # обрезаем до лимита
        except (json.JSONDecodeError, IOError):
            pass
    return []

def save_history(history):
    """Сохраняет историю в файл, оставляя последние MAX_MESSAGES сообщений."""
    trimmed = history[-MAX_MESSAGES:]
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(trimmed, f, ensure_ascii=False, indent=2)

def add_to_history(history, role, content):
    """Добавляет сообщение в историю и возвращает обновленный список."""
    history.append({"role": role, "content": content})
    # обрезаем, чтобы не превысить лимит в оперативке
    if len(history) > MAX_MESSAGES:
        history = history[-MAX_MESSAGES:]
    return history