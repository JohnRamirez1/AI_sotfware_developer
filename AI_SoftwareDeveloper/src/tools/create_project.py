import os

# Suponiendo que tienes esta clase
class GeneratedCode:
    def __init__(self, parent_folder, file_path, generated_code):
        self.parent_folder = parent_folder
        self.file_path = file_path
        self.generated_code = generated_code

# Tu lista simulada
generated_project = [
    GeneratedCode(
        parent_folder='backend',
        file_path='services/validation/validation.py',
        generated_code='''# Validation.py\nclass InputValidator: pass'''
    ),
    GeneratedCode(
        parent_folder='backend',
        file_path='API/authentication.py',
        generated_code='''# authentication.py\nclass Authenticator: pass'''
    )
]

# Escritura en carpetas reales
for item in generated_project:
    full_path = os.path.join(item.parent_folder, item.file_path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, 'w', encoding='utf-8') as f:
        f.write(item.generated_code)

print("✅ Archivos generados exitosamente.")
