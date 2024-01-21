from typing import Any
import bentoml


class Yolov5Runnable(bentoml.Runnable):
    SUPPORTED_RESOURCES = ("nvidia.com/gpu", "cpu")
    SUPPORTS_CPU_MULTI_THREADING = True

    def __init__(self, model: bentoml.Model, config: dict):
        import torch

        self.model = model.load_model()

        if torch.cuda.is_available():
            self.model.cuda()
        else:
            self.model.cpu()

        # Config inference settings
        self.setup(config)

    def setup(self, config: dict):
        self.model.inference_size = config.get("inference_size", 320)
        self.model.multi_label = config.get(
            "model.multi_label", False
        )  # NMS multiple labels per box

    @bentoml.Runnable.method(batchable=True, batch_dim=0)
    def inference(self, input_imgs):
        # Return predictions only
        results = self.model(input_imgs, size=self.inference_size)
        return results.pandas().xyxy

    @bentoml.Runnable.method(batchable=True, batch_dim=0)
    def render(self, input_imgs):
        # Return images with boxes and labels
        return self.model(input_imgs, size=self.inference_size).render()