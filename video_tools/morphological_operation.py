#!/usr/bin/env python3
# -*- coding:utf-8 -*-
#############################################################
# File: morphological_operation.py
# Created Date: Saturday July 3rd 2021
# Author: Chen Xuanhong
# Email: chenxuanhongzju@outlook.com
# Last Modified:  Wednesday, 18th May 2022 1:15:00 pm
# Modified By: Chen Xuanhong
# Copyright (c) 2021 Shanghai Jiao Tong University
#############################################################

import cv2
import torch
import torch.nn.functional as F
import numpy as np


def dilate(bin_img, ksize=5):
    pad = (ksize - 1) // 2
    bin_img = F.pad(bin_img, pad=[pad, pad, pad, pad], mode='reflect')
    out = F.max_pool2d(bin_img, kernel_size=ksize, stride=1, padding=0)
    return out


def erode(bin_img, ksize=5):
    out = 1 - dilate(1 - bin_img, ksize)
    return out