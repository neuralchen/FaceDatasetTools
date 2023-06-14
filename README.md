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
[baidu cloud](https://pan.baidu.com/s/1QjPZNojXI51tGbZvXH_Waw?pwd=au23)

Put ```arcface_checkpoint.tar``` to ```/arcface_ckpt```

Download ```insightface_func.zip``` from:
[baidu cloud](https://pan.baidu.com/s/1hNLc5i0tnlFJC-Fbf5ox6Q?pwd=au23) 

Unzip ```insightface_func.zip``` to root path of this project (i.e., "./")

# Usage

### To crop faces from a video or a directory:
```python face_crop.py```

### To roughly classify different faces:
```python face_cluster.py```

or 

```python face_cluster_kmeansplus.py```