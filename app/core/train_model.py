import os
import numpy as np
from PIL import Image
from cellpose import train

from core.segmentor import Segmentor
from core.label_convert import labelme_json_to_mask

def collect_training_data(data_folder):
    valid_ext = (".png", ".jpg", ".jpeg", ".tif", ".tiff", ".bmp")
    files = [f for f in os.listdir(data_folder) if f.lower().endswith(valid_ext)]

    images = []
    masks = []

    for filename in sorted(files):
        json_filename = os.path.splitext(filename)[0] + ".json"
        json_path = os.path.join(data_folder, json_filename)
        if not os.path.exists(json_path):
            continue

        image_path = os.path.join(data_folder, filename)
        image = np.array(Image.open(image_path).convert("RGB"))
        height, width = image.shape[0], image.shape[1]

        mask = labelme_json_to_mask(json_path, height, width)

        images.append(image)
        masks.append(mask)

    return images, masks

def retrain_model(data_folder, base_model_path, output_model_path, n_epochs=100):
    segmentor = Segmentor(base_model_path)
    net = segmentor.model.net

    images, masks = collect_training_data(data_folder)
    if len(images) == 0:
        raise ValueError("没有找到配对的图片+json标注文件，无法训练")

    save_folder = os.path.dirname(output_model_path)
    os.makedirs(save_folder, exist_ok=True)
    model_name = os.path.splitext(os.path.basename(output_model_path))[0]

    new_model_path, train_losses, test_losses = train.train_seg(
        net,
        train_data=images,
        train_labels=masks,
        channels=[0, 0],
        save_path=save_folder,
        model_name=model_name,
        n_epochs=n_epochs,
        learning_rate=0.005,
        weight_decay=1e-5,
        batch_size=1
    )

    return new_model_path, train_losses, len(images)