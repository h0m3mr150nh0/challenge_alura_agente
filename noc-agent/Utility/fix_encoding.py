import os

def convert_to_utf8(file_path):
    try:
        with open(file_path, 'r', encoding='latin-1') as f:
            content = f.read()

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)

        print(f"Convertido: {file_path}")

    except Exception:
        pass

def scan_folder(folder):
    for root, dirs, files in os.walk(folder):
        # IGNORAR pastas críticas
        if ".venv" in root or "__pycache__" in root:
            continue

        for file in files:
            if file.endswith(('.py', '.txt', '.md', '.env', '.csv')):
                convert_to_utf8(os.path.join(root, file))

scan_folder(".")