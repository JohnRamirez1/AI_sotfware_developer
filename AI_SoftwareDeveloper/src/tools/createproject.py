import os
from src.state.state import State

from dataclasses import dataclass

@dataclass
class GeneratedCode:
    parent_folder: str
    file_path: str
    generated_code: str

    def to_dict(self):
        return {
            "parent_folder": self.parent_folder,
            "file_path": self.file_path,
            "generated_code": self.generated_code
        }

    @staticmethod
    def from_dict(data):
        return GeneratedCode(
            parent_folder=data["parent_folder"],
            file_path=data["file_path"],
            generated_code=data["generated_code"]
        )


# Create project
def create_project(state: State):
    generated_project = state['generated_project']
    for item in generated_project:
        full_path = os.path.join('AI_GenCode', item.parent_folder, item.file_path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(item.generated_code)

    print("✅ Archivos generados exitosamente.")