from PIL import Image
import torch
import open_clip

model, _, preprocess = open_clip.create_model_and_transforms(
    "ViT-B-32",
    pretrained="openai"
)

image = preprocess(Image.open("dataset/cat1.jpg")).unsqueeze(0)

with torch.no_grad():
    features = model.encode_image(image)
    features /= features.norm(dim=-1, keepdim=True)

embedding = features[0].cpu().numpy().astype("float32")

print("Shape:", embedding.shape)
print("First values:", embedding[:10])