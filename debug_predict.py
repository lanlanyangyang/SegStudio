from cellpose import models
import numpy as np
from PIL import Image

MODEL_PATH = r"D:\SegStudio\models\AI_Cells_Custom_V5_converted.pth"
IMAGE_PATH = r"D:\多发性骨髓瘤\26.6.3训练\jieguo\1\IMG_20260126195727284.png"

model = models.CellposeModel(gpu=True, pretrained_model=MODEL_PATH)
image = np.array(Image.open(IMAGE_PATH).convert("RGB"))
print("图片尺寸:", image.shape)

channel_options = [[0, 0]]
diameter_options = [100, 150, 200, 250, 300, 350]

for ch in channel_options:
    for d in diameter_options:
        try:
            masks, flows, styles = model.eval(image, channels=ch, diameter=d)
            count = masks.max()
            print(f"channels={ch}, diameter={d} -> 检测到 {count} 个细胞")
        except Exception as e:
            print(f"channels={ch}, diameter={d} -> 报错: {e}")

