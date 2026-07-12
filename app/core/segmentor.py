import os

from cellpose import models


class Segmentor:
    def __init__(self, model_path):
        self.model_path = model_path
        self.model = None
        self._initialize_model()

    def _initialize_model(self):
        if self.model is None and os.path.exists(self.model_path):
            self.model = models.CellposeModel(gpu=True, pretrained_model=self.model_path)

    def predict(self, image):
        if self.model is None:
            self._initialize_model()
        if self.model is None:
            raise RuntimeError(f"无法加载模型文件：{self.model_path}")
        masks, flows, styles = self.model.eval(image, channels=[0, 0], diameter=250)
        return masks