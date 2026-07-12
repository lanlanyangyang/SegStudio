import os

import shutil
from core.label_convert import mask_to_labelme_json, save_labelme_json
import numpy as np
from PIL import Image
from core.segmentor import Segmentor
from core.model_manager import get_current_model_path

def get_image_files(folder):
    valid_ext = (".png", ".jpg", ".jpeg", ".tif", ".tiff", ".bmp")
    files = [f for f in os.listdir(folder) if f.lower().endswith(valid_ext)]
    return sorted(files)

def auto_label_folder(image_folder, output_folder, progress_callback=None):
    segmentor = Segmentor(get_current_model_path())
    os.makedirs(output_folder, exist_ok=True)

    image_files = get_image_files(image_folder)
    results = []

    for index, filename in enumerate(image_files):
        image_path = os.path.join(image_folder, filename)
        image = np.array(Image.open(image_path).convert("RGB"))
        masks = segmentor.predict(image)

        mask_filename = os.path.splitext(filename)[0] + "_mask.npy"
        mask_path = os.path.join(output_folder, mask_filename)
        np.save(mask_path, masks)

        height, width = masks.shape
        json_data = mask_to_labelme_json(masks, filename, height, width)
        json_filename = os.path.splitext(filename)[0] + ".json"
        json_path = os.path.join(output_folder, json_filename)
        save_labelme_json(json_data, json_path)

        image_copy_path = os.path.join(output_folder, filename)
        shutil.copy(image_path, image_copy_path)

        cell_count = int(masks.max())
        results.append((filename, cell_count))

        if progress_callback is not None:
            progress_callback(index + 1, len(image_files), filename, cell_count)

    return results