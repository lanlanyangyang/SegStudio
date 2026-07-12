import numpy as np


def filter_masks_by_area(masks, min_area=3):
    if masks is None:
        return masks

    filtered = np.zeros_like(masks, dtype=np.int32)
    labels = np.unique(masks)
    labels = labels[labels > 0]

    for label in labels:
        area = np.sum(masks == label)
        if area >= min_area:
            filtered[masks == label] = label

    return filtered


def compute_mask_statistics(masks):
    labels = np.unique(masks)
    labels = labels[labels > 0]

    areas = [int(np.sum(masks == label)) for label in labels]
    if not areas:
        return {
            "cell_count": 0,
            "average_area": 0,
            "max_area": 0,
            "areas": [],
        }

    return {
        "cell_count": len(labels),
        "average_area": float(np.mean(areas)),
        "max_area": int(np.max(areas)),
        "areas": areas,
    }
