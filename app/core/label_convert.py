import cv2
import numpy as np
import json

def mask_to_labelme_json(mask, image_path, image_height, image_width):
    shapes = []
    cell_ids = np.unique(mask)
    cell_ids = cell_ids[cell_ids != 0]

    for cell_id in cell_ids:
        cell_mask = (mask == cell_id).astype(np.uint8)
        contours, _ = cv2.findContours(
            cell_mask,
            cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE
        )
        for contour in contours:
            if len(contour) < 3:
                continue
            epsilon = 1.5
            approx = cv2.approxPolyDP(contour, epsilon, True)
            points = [[float(p[0][0]), float(p[0][1])] for p in approx]
            if len(points) < 3:
                continue

            shape = {
                "label": "cell",
                "points": points,
                "group_id": None,
                "description": None,
                "difficult": False,
                "shape_type": "polygon",
                "flags": {},
                "attributes": {}
            }
            shapes.append(shape)

    result = {
        "version": "2.3.5",
        "flags": {},
        "shapes": shapes,
        "imagePath": image_path,
        "imageData": None,
        "imageHeight": image_height,
        "imageWidth": image_width,
        "text": ""
    }
    return result

def save_labelme_json(data, output_path):
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def labelme_json_to_mask(json_path, image_height, image_width):
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    mask = np.zeros((image_height, image_width), dtype=np.int32)

    for index, shape in enumerate(data["shapes"]):
        points = np.array(shape["points"], dtype=np.int32)
        cv2.fillPoly(mask, [points], color=index + 1)

    return mask