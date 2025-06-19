import os
import torch
from PIL import Image
from encoder import CLIPEncoder
from database import ImageDatabase

def get_all_image_paths(folder):
    image_extensions = ('.png', '.jpg', '.jpeg')
    return [
        os.path.join(root, file)
        for root, _, files in os.walk(folder)
        for file in files
        if file.lower().endswith(image_extensions)
    ]

class CLIPIndexer:
    def __init__(self, db_path='image_database.db', device='cpu'):
        self.device = device
        self.encoder = CLIPEncoder(self.device)
        self.db = ImageDatabase(db_path)
    
    def index_folder(self, folder_path):
        image_paths = get_all_image_paths(folder_path)

        for path in image_paths:
            try:
                image = Image.open(path).convert('RGB')
                embedding = self.encoder.get_image_embedding(image)
                self.db.insert_embedding(path, embedding)
            except Exception as e:
                print(f"Error processing {path}: {e}")
        
        print("Indexing complete.")

if __name__ == "__main__":
    CLIPIndexer().index_folder('data')

