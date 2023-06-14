#!/usr/bin/env python3
# -*- coding:utf-8 -*-
#############################################################
# File: face_cluster.py
# Created Date: Monday April 25th 2022
# Author: Chen Xuanhong
# Email: chenxuanhongzju@outlook.com
# Last Modified:  Wednesday, 14th June 2023 3:27:40 pm
# Modified By: Chen Xuanhong
# Copyright (c) 2022 Shanghai Jiao Tong University
#############################################################


import torch
import torch.nn.functional as F
from   torchvision import transforms

import os
import cv2
import sys
import glob
import shutil
import numpy as np
from   sklearn.cluster import KMeans

import threading
import tkinter
import tkinter as tk
from tkinter.filedialog import askdirectory


class TextRedirector(object):
    def __init__(self, widget, tag="stdout"):
        self.widget = widget
        self.tag = tag

    def write(self, str):
        self.widget.configure(state="normal")
        self.widget.insert("end", str, (self.tag,))
        self.widget.configure(state="disabled")
        self.widget.see(tk.END)
    
    def flush(self):
        pass

#############################################################
# Main Class
#############################################################

class Application(tk.Frame):

    def __init__(self, master=None):
        tk.Frame.__init__(self, master,bg='black')
        # self.font_size = 16
        self.font_list = ("Times New Roman",14)
        self.padx = 5
        self.pady = 5
        self.window_init()
    
    def __label_text__(self, usr, root):
        return "User Name:  %s\nWorkspace:  %s"%(usr, root)

    def window_init(self):
        cwd = os.getcwd()
        self.master.title('Face Cluster - %s'%cwd)
        # self.master.iconbitmap('./utilities/_logo.ico')
        self.master.geometry("{}x{}".format(640, 600))

        font_list = self.font_list
        
        #################################################################################################
        list_frame    = tk.Frame(self.master)
        list_frame.pack(fill="both", padx=5,pady=5)
        list_frame.columnconfigure(0, weight=1)
        list_frame.columnconfigure(1, weight=5)
        list_frame.columnconfigure(2, weight=1)
        list_frame.columnconfigure(3, weight=1)

        self.img_path = tkinter.StringVar()

        tk.Label(list_frame, text="Image Path:",font=font_list,justify="left")\
                    .grid(row=0,column=0,sticky=tk.EW)
        
        tk.Entry(list_frame, textvariable= self.img_path, font=font_list)\
                    .grid(row=0,column=1,sticky=tk.EW)
        

        tk.Button(list_frame, text = "Add Path", font=font_list,
                    command = self.Select, bg='#F4A460', fg='#F5F5F5')\
                    .grid(row=0,column=2,sticky=tk.EW)
        tk.Button(list_frame, text = "Clear Path", font=font_list,
                    command = self.Clear, bg='#F4A460', fg='#F5F5F5')\
                    .grid(row=0,column=3,sticky=tk.EW)
        #################################################################################################
        list_frame1    = tk.Frame(self.master)
        list_frame1.pack(fill="both", padx=5,pady=5)
        list_frame1.columnconfigure(0, weight=1)
        list_frame1.columnconfigure(1, weight=1)
        list_frame1.columnconfigure(2, weight=1)

        self.save_path = tkinter.StringVar()

        tk.Label(list_frame1, text="Target Path:",font=font_list,justify="left")\
                    .grid(row=0,column=0,sticky=tk.EW)
        
        tk.Entry(list_frame1, textvariable= self.save_path, font=font_list)\
                    .grid(row=0,column=1,sticky=tk.EW)
        

        tk.Button(list_frame1, text = "Select Path", font=font_list,
                    command = self.Select_Target, bg='#F4A460', fg='#F5F5F5')\
                    .grid(row=0,column=2,sticky=tk.EW)
        
        #################################################################################################

        test_frame    = tk.Frame(self.master)
        test_frame.pack(fill="both", padx=5,pady=5)
        test_frame.columnconfigure(0, weight=1)
        test_frame.columnconfigure(1, weight=1)


        tk.Label(test_frame, text="Center number:",font=font_list,justify="left")\
                    .grid(row=0,column=0,sticky=tk.EW)

        self.thredhold = tkinter.StringVar()
        tk.Entry(test_frame, textvariable= self.thredhold, font=font_list)\
                    .grid(row=0,column=1,sticky=tk.EW)
        self.thredhold.set("20")
        
        #################################################################################################
        test_frame1    = tk.Frame(self.master)
        test_frame1.pack(fill="both", padx=5,pady=5)
        test_frame1.columnconfigure(0, weight=1)
        # test_frame1.columnconfigure(1, weight=1)

        test_update_button = tk.Button(test_frame1, text = "Cluster",
                            font=font_list, command = self.Crop, bg='#F4A460', fg='#F5F5F5')
        test_update_button.grid(row=0,column=0,sticky=tk.EW)

        

        #################################################################################################

        text = tk.Text(self.master, wrap="word")
        text.pack(fill="both",expand="yes", padx=5,pady=5)
        

        sys.stdout = TextRedirector(text, "stdout")
        
        self.init_algorithm()
        self.master.protocol("WM_DELETE_WINDOW", self.on_closing)

    def init_algorithm(self):
        arcface_ckpt= "./arcface_ckpt/arcface_checkpoint2.tar"
        self.transformer_Arcface = transforms.Compose([
                transforms.ToTensor(),
                transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
            ])

        self.arcface    = torch.load(arcface_ckpt, map_location=torch.device("cpu"))
        # self.arcface     = self.arcface1['model'].module
        self.arcface.eval()
        self.arcface.requires_grad_(False)
        self.arcface = self.arcface.cuda()
        
    
    # def __scaning_logs__(self):
    def Select(self):
        thread_update = threading.Thread(target=self.select_task)
        thread_update.start()
    
    def select_task(self):
        path = askdirectory()
        if os.path.isdir(path):
            print("Add source directory: %s"%path)
            paths = self.img_path.get()
            paths += ";" + path
            self.img_path.set(paths)
    
    def Clear(self):
        thread_update = threading.Thread(target=self.clear_task)
        thread_update.start()
    
    def clear_task(self):
        self.img_path.set("")
    
    def Select_Target(self):
        thread_update = threading.Thread(target=self.select_target_task)
        thread_update.start()
    
    def select_target_task(self):
        path = askdirectory()
        if os.path.isdir(path):
            print("Selected target directory: %s"%path)
            self.save_path.set(path)
    
    def Crop(self):
        thread_update = threading.Thread(target=self.crop_task)
        thread_update.start()
    
    def crop_task(self):
        path        = self.img_path.get()
        tg_path     = self.save_path.get()
        num_clusters= self.thredhold.get()
        num_clusters= int(num_clusters)

        if not path:
            print("Please select source path!")
            return

        

        print("Cluster center number %d"%num_clusters)

        input_dir = path.split(";")


        if not tg_path:
            tg_path     = os.path.join(input_dir[1],"seperated")
            
        print("target path: ",tg_path)
        if not os.path.exists(tg_path):
            os.makedirs(tg_path)

        print(input_dir)
        mark        = []
        imgs_tensor =None
        index       = 0
        for i_dir in input_dir:
            if not i_dir:
                continue
            for item in glob.iglob(os.path.join(i_dir,"**"),recursive=True):
                if os.path.isfile(item):
                    id_img  = cv2.imdecode(np.fromfile(item, dtype=np.uint8), cv2.IMREAD_COLOR)
                    mark.append(item)
                    id_img      = self.transformer_Arcface(id_img)
                    id_img      = id_img.unsqueeze(0).cuda()
                    id_img      = F.interpolate(id_img,size=(112,112), mode='bicubic')
                    latend_id   = self.arcface(id_img)
                    latend_id   = F.normalize(latend_id, p=2, dim=1)
                    if index == 0:
                        imgs_tensor = latend_id
                    else:
                        imgs_tensor = torch.cat((imgs_tensor,latend_id),dim=0)
                    index += 1
        print(imgs_tensor.shape)
        print("%d images are found!"%index)
        imgs_tensor = imgs_tensor.cpu().numpy()

        # kmeans
        estimator = KMeans(
            n_clusters= num_clusters,
            init='k-means++',
            tol=0.000001,
            max_iter=600
        ).fit(imgs_tensor)

        center_num = estimator.cluster_centers_.shape[0]
        cluster_ids_x = estimator.labels_

        target_paths = []
        print("%d differece face are found!"%center_num)
        for i in range(center_num):
            temppath = os.path.join(tg_path, str(i))
            if not os.path.exists(temppath):
                os.makedirs(temppath)
            target_paths.append(temppath)

        print("Copy images to differet dirs!")
        for i in range(index):
            tg_num = cluster_ids_x[i].item()
            attr_basename = os.path.basename(mark[i])
            tg_temp = os.path.join(target_paths[tg_num], attr_basename)
            print("source face: %s ---> target path %s"%(mark[i],tg_temp))
            shutil.copyfile(mark[i],tg_temp)
        print("Process finished!")

    def on_closing(self):

        # self.__save_config__()
        self.master.destroy()
    


if __name__ == "__main__":
    app = Application()
    app.mainloop()