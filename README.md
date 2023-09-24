# FaceDatasetTools
 
# Dependencies
- pip install insightface==0.2.0
- onnx
- onnxruntime
- pytorch
- pillow
- numpy
- pip install opencv-python
- pip install scikit-learn
- torchvision

# Download
Download ```arcface_checkpoint.tar``` from:
[baidu cloud](https://pan.baidu.com/s/1ytCegRrORVoEyQyznMZREg?pwd=sjtu)

Put ```arcface_checkpoint.tar``` to ```/arcface_ckpt```

Download ```insightface_func.zip``` from:
[baidu cloud](https://pan.baidu.com/s/1hNLc5i0tnlFJC-Fbf5ox6Q?pwd=au23) 

Unzip ```insightface_func.zip``` to root path of this project (i.e., "./")

# Usage

## To crop faces from a video or a directory:
```python face_crop.py```

## To roughly classify different faces:
```python face_cluster.py```

or 

```python face_cluster_kmeansplus.py```

## Detect face mask with FaRL:

Download ```FaRL.rar``` from:
[baidu cloud (password: we0q)](https://pan.baidu.com/s/1umvmpGqe0e0tZPhc3msqwQ?pwd=we0q) 

Unzip ```FaRL.rar``` to root path of this project (i.e., "./")

Refer to ```debug_FaRL.py``` to detect face mask.
