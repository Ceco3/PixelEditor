import os

def Lerp(a: float, b: float, c: float) -> float:
    "c indicates how done you are"
    return a + (b - a) * c

def get_any_in_folder(folder_path: str) -> list[str]:
    """Lists folders and files in <folder_path> directory.
        Provide full C: path"""
    return os.listdir(folder_path)