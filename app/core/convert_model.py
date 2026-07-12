import torch
import os
sd = torch.load(r"D:\多发性骨髓瘤\AI_Cells_Custom_V5 qi", map_location="cpu", weights_only=False)
os.makedirs(r"D:\SegStudio\models", exist_ok=True)
torch.save(sd, r"D:\SegStudio\models\AI_Cells_Custom_V5_converted.pth")
print("转换完成")
