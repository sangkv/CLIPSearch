import torch
import torch.nn.functional as F
from encoder import CLIPEncoder
from database import ImageDatabase

class CLIPSearcher:
    def __init__(self, db_path='image_database.db', device='cpu'):
        self.device = device
        self.encoder = CLIPEncoder(self.device)
        self.db = ImageDatabase(db_path)
        self.image_ids, self.embeddings = self.db.load_all_embeddings()
        self.embeddings = F.normalize(self.embeddings, dim=1).to(self.device)

    def search(self, query_text, top_k=10):
        query_emb = self.encoder.get_text_embedding(query_text)
        query_emb = F.normalize(query_emb, dim=0)

        similarities = (self.embeddings @ query_emb).cpu().numpy()
        top_indices = similarities.argsort()[::-1][:top_k]
        results = [(self.image_ids[i], similarities[i]) for i in top_indices]

        return results

