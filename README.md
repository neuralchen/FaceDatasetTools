# FaceDatasetTools
 
***Currently the GUI only supports Windows operating systems***

# Dependencies
- pip install insightface==0.2.0
- onnx
- onnxruntime
- pytorch
- onnxruntime==1.15
- tqdm
- pillow
- numpy
- kmeans_pytorch
- pip install opencv-python
- pip install scikit-learn
- torchvision
- pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu117


# Download
Download ```arcface_checkpoint.tar``` from: [baidu cloud](https://pan.baidu.com/s/1ytCegRrORVoEyQyznMZREg?pwd=sjtu)

Put ```arcface_checkpoint.tar``` to ```/arcface_ckpt```

Download ```insightface_func.zip``` from:
[baidu cloud](https://pan.baidu.com/s/1hNLc5i0tnlFJC-Fbf5ox6Q?pwd=au23) 

Unzip ```insightface_func.zip``` to ***root path*** of this project (i.e., "./")

# Usage

## To crop faces from a video:
```python face_crop_video.py```


### Parameters in GUI:
- Video Path: The path to the video file. Users need to create a dedicated folder for the target video to prevent the results from being overwritten.
- Target Path: Folder to store processed face images.
- Crop Size: Face image size.
- Align Mode: The padding size of the face area.
- Blurry Thredhold: The threshold for a picture to be considered blurry. The larger the value, the clearer the face.


## To roughly classify different faces:
```python face_cluster.py```

or 

```python face_cluster_kmeansplus.py```

## Detect face mask with FaRL:

Download ```FaRL.rar``` from:
[baidu cloud (password: we0q)](https://pan.baidu.com/s/1umvmpGqe0e0tZPhc3msqwQ?pwd=we0q) 
