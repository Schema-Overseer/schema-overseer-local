import bentoml
import torch

model = torch.hub.load("ultralytics/yolov5", "yolov5s")

bentoml.pytorch.save_model(
    "yolov5",
    model,
    custom_objects={
        "inference_size": 320,
        "model.multi_label": False,
        "model.conf": 0.8,
    },
)