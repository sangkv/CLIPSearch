import sqlite3
import numpy as np
import torch

class ImageDatabase:
    def __init__(self, db_path='image_database.db'):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS image_embeddings (
            image_id TEXT PRIMARY KEY,
            embedding BLOB
        )""")
        conn.commit()
        conn.close()

    def insert_embedding(self, image_id, embedding_tensor):
        embedding = embedding_tensor.cpu().numpy()
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("INSERT OR REPLACE INTO image_embeddings (image_id, embedding) VALUES (?, ?)",
                       (image_id, embedding.tobytes()))
        conn.commit()
        conn.close()

    def load_all_embeddings(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT image_id, embedding FROM image_embeddings")
        data = cursor.fetchall()
        conn.close()

        ids, embeddings = [], []
        for image_id, emb_bin in data:
            ids.append(image_id)
            embeddings.append(np.frombuffer(emb_bin, dtype=np.float32))

        return ids, torch.tensor(np.array(embeddings))

