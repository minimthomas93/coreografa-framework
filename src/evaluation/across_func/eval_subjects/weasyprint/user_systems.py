import sys
import os
from importlib import import_module

def load_weasy(version):
    if version == 65:
        version_path = os.path.abspath("weasy_v65")
    elif version == 66:
        version_path = os.path.abspath("weasy_v66")
    elif version == 63.1:
        version_path = os.path.abspath("weasy_v63_1")
    elif version == 64:
        version_path = os.path.abspath("weasy_v64")
    else:
        raise ValueError("Unsupported version")

    if version_path not in sys.path:
        sys.path.insert(0, version_path)

    return import_module("weasyprint")

# Import once at module load
weasy65 = load_weasy(65)
weasy64 = load_weasy(64)

BASE = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
IMAGES_DIR = os.path.join(BASE, "eval_subjects", "weasyprint")

def weasyprint_64(output):
    """
    Render HTML using WeasyPrint v65.
    No PDF file is generated (fast).
    """
    html = weasy64.HTML(string=str(output), base_url=IMAGES_DIR)
    html.render()   # Layout engine only, no PDF write

def weasyprint_65(output):
    """
    Render HTML using WeasyPrint v63.1.
    No PDF file is generated (fast).
    """
    html = weasy65.HTML(string=str(output), base_url=IMAGES_DIR)
    html.render()   # Layout engine only, no PDF write