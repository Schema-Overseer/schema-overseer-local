import bentoml
from bentoml.io import Image, PandasDataFrame

from yolo_runner import Yolov5Runnable

yolo_model = bentoml.models.get("yolov5:latest")
# torch_model = bentoml.pytorch.load_model("yolov5:latest")

# yolo_model = bentoml.models.get("yolov5:latest")
# torch_model = yolo_model.load_model("yolov5:latest") # Doesn't work

# yolo_model = bentoml.models.get("yolov5:latest")
# torch_model = yolo_model._model # Doesn't work - see the code the Model, it needs to load it first

# Next time - see the https://github.com/mlflow/mlflow/issues/9514

yolo_v5_runner = bentoml.Runner(
    Yolov5Runnable,
    max_batch_size=30,
    runnable_init_params={
        "model": yolo_model,  # replace with torch_model - still doesn't work
        "config": yolo_model.custom_objects,
    },
)

svc = bentoml.Service("yolo_v5_demo", runners=[yolo_v5_runner])


@svc.api(input=Image(), output=PandasDataFrame())
async def invocation(input_img):
    batch_ret = await yolo_v5_runner.inference.async_run([input_img])
    return batch_ret[0]


@svc.api(input=Image(), output=Image())
async def render(input_img):
    batch_ret = await yolo_v5_runner.render.async_run([input_img])
    return batch_ret[0]