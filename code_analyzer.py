import re

def find_functions(code, language="javascript"):
    """Находит все функции в коде."""
    if language in ("javascript", "jsx", "js"):
        pattern = r'(?:async\s+)?(?:function\s+)?(\w+)\s*\([^)]*\)\s*\{'
        return re.findall(pattern, code)
    elif language == "java":
        pattern = r'(?:public|private|protected)?\s*(?:static\s+)?(?:<[^>]+>\s+)?\w+\s+(\w+)\s*\([^)]*\)\s*\{'
        return re.findall(pattern, code)
    return []

def find_ui_elements(code):
    """Находит кнопки, ссылки, инпуты в JSX/HTML."""
    buttons = re.findall(r'<button[^>]*>(.*?)</button>', code, re.DOTALL | re.IGNORECASE)
    button_texts = [re.sub(r'<[^>]+>', '', b).strip() for b in buttons]
    return button_texts

def find_api_calls(code):
    """Находит вызовы API (fetch, axios, apiService)."""
    calls = re.findall(r'(?:fetch|axios\.\w+|apiService\.\w+)\s*\([^)]+\)', code)
    return calls

def find_imports(code):
    """Находит все импорты."""
    imports = re.findall(r'import\s+.*?(?:from\s+)?["\']([^"\']+)["\']', code)
    return imports