import os
import uuid
from datetime import datetime

def generate_unique_filename(extension="mp3", prefix="file"):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    unique_id = uuid.uuid4().hex
    return f"{prefix}_{timestamp}_{unique_id}.{extension}"

def delete_file(file_path):
    if os.path.exists(file_path):
        os.remove(file_path)