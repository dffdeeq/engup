import os

SRC_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE_DIR = os.path.dirname(SRC_DIR)
TEMP_FILES_DIR = os.path.join(BASE_DIR, 'temp_files')
