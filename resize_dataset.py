#!/usr/bin/env python3
# -*- coding:utf-8 -*-
#############################################################
# File: annotation.py
# Created Date: Saturday February 26th 2022
# Author: Chen Xuanhong
# Email: chenxuanhongzju@outlook.com
# Last Modified:  Wednesday, 30th March 2022 11:36:20 pm
# Modified By: Chen Xuanhong
# Copyright (c) 2022 Shanghai Jiao Tong University
#############################################################


import cv2
import os
import glob
import numpy as np
from insightface_func.face_detect_crop_single import Face_detect_crop

if __name__ == "__main__":
    image_dir= "J:/BaiduNetdiskDownload/SJTU_Swap"
    target_dir= "J:/BaiduNetdiskDownload/SJTU_Swap_224"
    
    detect = Face_detect_crop(name='antelope', root='./insightface_func/models')
    detect.prepare(ctx_id = 0, det_thresh=0.6,\
                        det_size=(640,640),mode = "none")
    temp_path   = os.path.join(image_dir,'*/')
    pathes      = glob.glob(temp_path)
    dataset = []
    for dir_item in pathes:
        join_path = glob.glob(os.path.join(dir_item,'*.png'))
        print("processing %s"%dir_item)
        temp_list = []
        dir_item = dir_item.replace("\\","/")
        dir_item = dir_item.split("/")[-2]
        print(dir_item)
        target_path = os.path.join(target_dir,dir_item)
        os.makedirs(target_path,exist_ok=True)
        for item in join_path:
            attr_img_ori = cv2.imdecode(np.fromfile(item, dtype=np.uint8),cv2.IMREAD_COLOR)
            
            attr_img_ori = cv2.copyMakeBorder(attr_img_ori, 200, 200, 200, 200, cv2.BORDER_CONSTANT, value=(0,0,0))
            attr_img_align_crop = detect.get(attr_img_ori,crop_size=224)
            if attr_img_align_crop is not None:
                save_name = os.path.splitext(os.path.basename(item))[0]
                f_path = os.path.join(target_path,save_name+".png")
                print(f_path)
                cv2.imencode('.png',attr_img_align_crop[0][0])[1].tofile(f_path)
