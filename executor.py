# executor.py
import os, subprocess, datetime
from config import ALLOWED_PATHS, DANGEROUS_COMMANDS, LOG_FILE

def log(message):
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{datetime.datetime.now()}] {message}\n")

def safe_path(path):
    return any(path.startswith(p) for p in ALLOWED_PATHS)

def dangerous_command(cmd):
    return any(word in cmd.lower() for word in DANGEROUS_COMMANDS)

def create_file(path: str, content: str):
    if not safe_path(path):
        return f"Безопасность: путь {path} запрещён"
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        log(f"Создан файл: {path}")
        return f"✅ Файл {path} создан."
    except Exception as e:
        return f"Ошибка создания файла: {str(e)}"

def replace_file(path: str, content: str):
    if not safe_path(path):
        return f"Безопасность: путь {path} запрещён"
    if not os.path.exists(path):
        return f"Файл {path} не найден для перезаписи"
    try:
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        log(f"Перезаписан файл: {path}")
        return f"✅ Файл {path} перезаписан."
    except Exception as e:
        return f"Ошибка перезаписи файла: {str(e)}"

def read_file(path: str):
    if not safe_path(path):
        return f"Безопасность: путь {path} запрещён"
    if not os.path.exists(path):
        return "Файл не найден"
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def run_shell(command: str):
    if dangerous_command(command):
        return f"⛔ Опасная команда заблокирована: {command}"
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=30)
        log(f"Выполнена команда: {command}")
        return (result.stdout + "\n" + result.stderr).strip() or "(пустой вывод)"
    except subprocess.TimeoutExpired:
        return "Команда превысила лимит времени (30 секунд)."
    except Exception as e:
        return f"Ошибка выполнения команды: {str(e)}"

def list_files(directory: str):
    """Возвращает список файлов и папок в указанной директории."""
    if not safe_path(directory):
        return f"Безопасность: путь {directory} запрещён"
    if not os.path.isdir(directory):
        return f"'{directory}' не является папкой"
    try:
        items = os.listdir(directory)
        items.sort()
        result = f"Содержимое папки '{directory}':\n"
        for item in items:
            full_path = os.path.join(directory, item)
            if os.path.isdir(full_path):
                result += f"  [ПАПКА] {item}\n"
            else:
                result += f"  [ФАЙЛ] {item}\n"
        return result
    except Exception as e:
        return f"Ошибка чтения папки: {str(e)}"

def web_search(query: str):
    try:
        from ddgs import DDGS
        results = DDGS().text(query, max_results=3)
        formatted = "\n".join([f"- {r['title']}: {r['href']}" for r in results])
        log(f"Поиск: {query}")
        return formatted if formatted else "Ничего не найдено"
    except ImportError:
        return "Ошибка: установите ddgs (pip install ddgs)"
    except Exception as e:
        return f"Ошибка поиска: {e}"

def git_clone(repo_url: str, target_dir: str):
    if not target_dir.startswith("D:/projects/"):
        return "Безопасность: клонирование разрешено только в D:/projects/"
    try:
        version_check = subprocess.run("git --version", shell=True, capture_output=True, text=True)
        if version_check.returncode != 0:
            return "Ошибка: Git не установлен."
    except:
        return "Ошибка проверки Git."
    try:
        result = subprocess.run(f"git clone {repo_url} {target_dir}", shell=True, capture_output=True, text=True, timeout=60)
        output = result.stdout + "\n" + result.stderr
        if result.returncode != 0:
            return f"Ошибка клонирования: {output}"
        return f"✅ Репозиторий склонирован в {target_dir}."
    except subprocess.TimeoutExpired:
        return "Ошибка: превышен таймаут клонирования."
    except Exception as e:
        return f"Ошибка клонирования: {str(e)}"