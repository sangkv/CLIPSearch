import torch
import clip

class CLIPEncoder:
    def __init__(self, device='cpu'):
        self.device = device
        self.model, self.preprocess = clip.load('ViT-B/32', device=self.device)

    def get_text_embedding(self, text):
        text_tokens = clip.tokenize([text]).to(self.device)
        with torch.no_grad():
            return self.model.encode_text(text_tokens)[0]

    def get_image_embedding(self, image):
        img_preprocessed = self.preprocess(image).unsqueeze(0).to(self.device)
        with torch.no_grad():
            return self.model.encode_image(img_preprocessed)[0]

