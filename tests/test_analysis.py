import os
import sys
import tempfile
import unittest
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'app'))

from core.analysis import compute_mask_statistics, filter_masks_by_area


class AnalysisTests(unittest.TestCase):
    def test_filter_masks_by_area(self):
        masks = np.array([
            [0, 0, 0, 0],
            [0, 1, 1, 0],
            [0, 1, 2, 0],
            [0, 0, 0, 0],
        ], dtype=np.int32)

        filtered = filter_masks_by_area(masks, min_area=2)
        self.assertEqual(int(filtered[1, 1]), 1)
        self.assertEqual(int(filtered[2, 2]), 0)

    def test_compute_mask_statistics(self):
        masks = np.array([
            [0, 0, 0],
            [0, 1, 1],
            [0, 1, 2],
        ], dtype=np.int32)

        stats = compute_mask_statistics(masks)
        self.assertEqual(stats["cell_count"], 2)
        self.assertEqual(stats["average_area"], 2.0)
        self.assertEqual(stats["max_area"], 3)


if __name__ == "__main__":
    unittest.main()
