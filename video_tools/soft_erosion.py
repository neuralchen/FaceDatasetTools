#!/usr/bin/env python3
# -*- coding:utf-8 -*-
#############################################################
# File: soft_erosion.py
# Created Date: Saturday July 3rd 2021
# Author: Chen Xuanhong
# Email: chenxuanhongzju@outlook.com
# Last Modified:  Wednesday, 18th May 2022 1:15:00 pm
# Modified By: Chen Xuanhong
# Copyright (c) 2021 Shanghai Jiao Tong University
#############################################################


import torch
import torch.nn as nn
import torch.nn.functional as F

class SoftErosion(nn.Module):
    def __init__(self, kernel_size=17, threshold=0.6, iterations=1):
        super(SoftErosion, self).__init__()
        r = kernel_size // 2
        self.padding = r
        self.iterations = iterations
        self.threshold = threshold

        # Create kernel
        y_indices, x_indices = torch.meshgrid(torch.arange(0., kernel_size), torch.arange(0., kernel_size))
        dist = torch.sqrt((x_indices - r) ** 2 + (y_indices - r) ** 2)
        kernel = dist.max() - dist
        kernel /= kernel.sum()
        kernel = kernel.view(1, 1, *kernel.shape)
        self.register_buffer('weight', kernel)

    def forward(self, x):
        x = x.float()
        for _ in range(self.iterations - 1):
            x = torch.min(x, F.conv2d(x, weight=self.weight, groups=x.shape[1], padding=self.padding))
        x = F.conv2d(x, weight=self.weight, groups=x.shape[1], padding=self.padding)

        mask = x >= self.threshold
        x[mask] = 1.0
        x[~mask] /= x[~mask].max()

        return x, mask
