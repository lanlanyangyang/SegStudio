import cv2
import numpy as np

def draw_segmentation_overlay(image, masks):
    overlay = image.copy()
    if overlay.dtype != np.uint8:
        overlay = overlay.astype(np.uint8)

    cell_ids = np.unique(masks)
    cell_ids = cell_ids[cell_ids != 0]

    for cell_id in cell_ids:
        cell_mask = (masks == cell_id).astype(np.uint8)
        contours, _ = cv2.findContours(
            cell_mask,
            cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE
        )
        cv2.drawContours(overlay, contours, -1, (0, 255, 0), 3)

        ys, xs = np.where(cell_mask)
        if len(xs) > 0:
            cx = int(xs.mean())
            cy = int(ys.mean())
            cv2.putText(
                overlay,
                str(int(cell_id)),
                (cx, cy),
                cv2.FONT_HERSHEY_SIMPLEX,
                1.2,
                (255, 0, 0),
                3
            )

    return overlay