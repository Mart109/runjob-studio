# verifier.py
from executor import run_shell, read_file

def full_verification(filepath):
    report = []
    # 1. Существование
    result = run_shell(f"dir \"{filepath}\"")
    report.append(f"[1/7] Существование: {'✅' if 'не найден' not in result else '❌'} {result}")
    # 2. Размер
    report.append(f"[2/7] Размер: {'✅' if '0 байт' not in result else '❌'} {result}")
    # 3. Синтаксис
    result = run_shell(f"python -m py_compile \"{filepath}\"")
    report.append(f"[3/7] Синтаксис: {'✅' if 'Error' not in result else '❌'} {result}")
    # 4. Импорты
    result = run_shell(f"python -c \"import sys; sys.path.insert(0, 'D:/projects'); import {filepath.split('/')[-1].replace('.py', '')}\"")
    report.append(f"[4/7] Импорты: {'✅' if 'Error' not in result else '❌'} {result}")
    # 5. Компиляция
    result = run_shell(f"python -c \"import py_compile; py_compile.compile('{filepath}', doraise=True)\"")
    report.append(f"[5/7] Компиляция: {'✅' if 'Error' not in result else '❌'} {result}")
    # 6. Тестовый запуск
    result = run_shell(f"python \"{filepath}\"")
    report.append(f"[6/7] Тестовый запуск: {'✅' if 'Error' not in result else '❌'} {result}")
    # 7. Итог
    success = all("✅" in line for line in report)
    report.append(f"[7/7] Итог: {'Все проверки пройдены' if success else 'Обнаружены ошибки'}")
    return "\n".join(report)