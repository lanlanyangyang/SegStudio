from cellpose import models

model = models.CellposeModel(gpu=True, pretrained_model=r"D:\SegStudio\models\AI_Cells_Custom_V5_converted.pth")
print(model.diam_mean)
print(model.net)