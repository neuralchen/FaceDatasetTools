#!/usr/bin/env python3
# -*- coding:utf-8 -*-
#############################################################
# File: face_crop_video.py
# Created Date: Tuesday February 1st 2022
# Author: Chen Xuanhong
# Email: chenxuanhongzju@outlook.com
# Last Modified:  Thursday, 28th April 2022 10:04:25 pm
# Modified By: Chen Xuanhong
# Copyright (c) 2022 Shanghai Jiao Tong University
#############################################################


import  os
import  cv2
import  sys
import  numpy as np
from    tqdm import tqdm
import  tkinter
from    tkinter.filedialog import askopenfilename, askdirectory

import threading
import tkinter as tk
import tkinter.ttk as ttk

from insightface_func.utils.face_align_ffhqandnewarc import ffhq_template
from insightface_func.face_detect_crop_multi_highresolution import Face_detect_crop

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
        self.master.title('Face Crop Tool for Video - %s'%cwd)
        # self.master.iconbitmap('./utilities/_logo.ico')
        self.master.geometry("{}x{}".format(640, 600))

        font_list = self.font_list
        
        #################################################################################################
        list_frame    = tk.Frame(self.master)
        list_frame.pack(fill="both", padx=5,pady=5)
        list_frame.columnconfigure(0, weight=1)
        list_frame.columnconfigure(1, weight=1)
        list_frame.columnconfigure(2, weight=1)

        self.img_path = tkinter.StringVar()

        tk.Label(list_frame, text="Video Path:",font=font_list,justify="left")\
                    .grid(row=0,column=0,sticky=tk.EW)
        
        tk.Entry(list_frame, textvariable= self.img_path, font=font_list)\
                    .grid(row=0,column=1,sticky=tk.EW)
        

        tk.Button(list_frame, text = "Select", font=font_list,
                    command = self.Select, bg='#F4A460', fg='#F5F5F5')\
                    .grid(row=0,column=2,sticky=tk.EW)
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
        

        tk.Button(list_frame1, text = "Select", font=font_list,
                    command = self.Select_Target, bg='#F4A460', fg='#F5F5F5')\
                    .grid(row=0,column=2,sticky=tk.EW)
        
        #################################################################################################
        label_frame    = tk.Frame(self.master)
        label_frame.pack(fill="both", padx=5,pady=5)
        label_frame.columnconfigure(0, weight=1)
        label_frame.columnconfigure(1, weight=1)
        label_frame.columnconfigure(2, weight=1)
        label_frame.columnconfigure(3, weight=1)
        label_frame.columnconfigure(4, weight=1)

        tk.Label(label_frame, text="Crop Size:",font=font_list,justify="left")\
                    .grid(row=0,column=0,sticky=tk.EW)
        
        tk.Label(label_frame, text="Align Mode:",font=font_list,justify="left")\
                    .grid(row=0,column=1,sticky=tk.EW)

        tk.Label(label_frame, text="Target Format:",font=font_list,justify="left")\
                    .grid(row=0,column=2,sticky=tk.EW)
        
        tk.Label(label_frame, text="Blurry Thredhold:",font=font_list,justify="left")\
                    .grid(row=0,column=3,sticky=tk.EW)
        

        tk.Label(label_frame, text="Frame Interval:",font=font_list,justify="left")\
                    .grid(row=0,column=4,sticky=tk.EW)
        
        #################################################################################################

        test_frame    = tk.Frame(self.master)
        test_frame.pack(fill="both", padx=5,pady=5)
        test_frame.columnconfigure(0, weight=1)
        test_frame.columnconfigure(1, weight=1)
        test_frame.columnconfigure(2, weight=1)
        test_frame.columnconfigure(3, weight=1)
        test_frame.columnconfigure(4, weight=1)

        self.test_var = tkinter.StringVar()

        self.test_com = ttk.Combobox(test_frame, textvariable=self.test_var)
        self.test_com.grid(row=0,column=0,sticky=tk.EW)
        self.test_com["value"] = [256,512,768,1024]
        self.test_com.current(3)

        self.align_var = tkinter.StringVar()
        self.align_com = ttk.Combobox(test_frame, textvariable=self.align_var)
        self.align_com.grid(row=0,column=1,sticky=tk.EW)
        self.align_com["value"] = ["VGGFace","ffhq"]
        self.align_com.current(1)

        self.format_var = tkinter.StringVar()

        self.format_com = ttk.Combobox(test_frame, textvariable=self.format_var)
        self.format_com.grid(row=0,column=2,sticky=tk.EW)
        self.format_com["value"] = ["png","jpg"]
        self.format_com.current(0)

        self.thredhold = tkinter.StringVar()
        tk.Entry(test_frame, textvariable= self.thredhold, font=font_list)\
                    .grid(row=0,column=3,sticky=tk.EW)
        self.thredhold.set("150")

        self.frame_interv = tkinter.StringVar()
        tk.Entry(test_frame, textvariable= self.frame_interv, font=font_list)\
                    .grid(row=0,column=4,sticky=tk.EW)
        self.frame_interv.set("10")
        #################################################################################################
        scale_frame    = tk.Frame(self.master)
        scale_frame.pack(fill="both", padx=5,pady=5)
        scale_frame.columnconfigure(0, weight=1)
        scale_frame.columnconfigure(1, weight=1)
        scale_frame.columnconfigure(2, weight=1)
        scale_frame.columnconfigure(3, weight=1)
        # label_frame.columnconfigure(2, weight=1)

        tk.Label(scale_frame, text="Min Size:",font=font_list,justify="left")\
                    .grid(row=0,column=0,sticky=tk.EW)
        self.min_scale = tkinter.StringVar()

        self.image_scale = ttk.Combobox(scale_frame, textvariable=self.min_scale)
        self.image_scale.grid(row=0,column=1,sticky=tk.EW)
        self.image_scale["value"] = [0.5,0.6,0.7,0.8,0.9,1.0,1.1,1.2,1.3,1.4,1.5,1.6,1.7,1.8,1.9,2.0]
        self.image_scale.current(2)

        tk.Label(scale_frame, text="Affine Size:",font=font_list,justify="left")\
                    .grid(row=0,column=2,sticky=tk.EW)
        self.affine_size_var = tkinter.StringVar()

        self.affine_size = ttk.Combobox(scale_frame, textvariable=self.affine_size_var)
        self.affine_size.grid(row=0,column=3,sticky=tk.EW)
        self.affine_size["value"] = [1,4,8,10,16,20,24,32]
        self.affine_size.current(1)

        #################################################################################################
        test_frame1    = tk.Frame(self.master)
        test_frame1.pack(fill="both", padx=5,pady=5)
        test_frame1.columnconfigure(0, weight=1)
        # test_frame1.columnconfigure(1, weight=1)

        test_update_button = tk.Button(test_frame1, text = "Crop",
                            font=font_list, command = self.Crop, bg='#F4A460', fg='#F5F5F5')
        test_update_button.grid(row=0,column=0,sticky=tk.EW)

        #################################################################################################
        

        text = tk.Text(self.master, wrap="word")
        text.pack(fill="both",expand="yes", padx=5,pady=5)
        

        sys.stdout = TextRedirector(text, "stdout")
        
        self.init_algorithm()
        self.master.protocol("WM_DELETE_WINDOW", self.on_closing)

    def init_algorithm(self):
        self.detect = Face_detect_crop(name='antelope', root='./insightface_func/models')
        
    
    # def __scaning_logs__(self):
    def Select(self):
        thread_update = threading.Thread(target=self.select_task)
        thread_update.start()
    
    def select_task(self):
        path = askopenfilename()
        
        if os.path.isfile(path):
            print("Selected source video: %s"%path)
            self.img_path.set(path)
    
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
        mode        = self.align_com.get()
        if mode == "VGGFace":
            mode = "None"
        crop_size   = int(self.test_com.get())
        
        path        = self.img_path.get()
        tg_path     = self.save_path.get()
        blur_t      = self.thredhold.get()
        frame_interv= self.frame_interv.get()
        frame_interv= int(frame_interv)
        affine_size = self.affine_size_var.get()
        affine_size = crop_size * int(affine_size)

        basepath    = os.path.splitext(os.path.basename(path))[0]
        tg_path     = os.path.join(tg_path,basepath)

        print("target path: ",tg_path)
        if not os.path.exists(tg_path):
            os.makedirs(tg_path)
        tg_format   = self.format_com.get()
        min_scale   = float(self.min_scale.get())
        blur_t      = float(blur_t)
        print("Blurry thredhold %f"%blur_t)
        self.detect.prepare(ctx_id = 0, det_thresh=0.6,\
                        det_size=(640,640),mode = mode,crop_size=crop_size,ratio=min_scale)
        log_file = "./dataset_readme.txt"
        with open(log_file,'a+') as logf: # ,encoding='UTF-8'
            logf.writelines("%s --> %s\n"%(path,tg_path))
        if path and tg_path:

            if os.path.isfile(path):
                print("Input a file....")

                video = cv2.VideoCapture(path)
        
                frame_count = int(video.get(cv2.CAP_PROP_FRAME_COUNT))

                for frame_index in tqdm(range(frame_count)):
                    ret, frame = video.read()
                    if frame_index % frame_interv ==0:
                        
                        if  ret:
                            detect_results = self.detect.get(frame, crop_size)
                            if detect_results is not None:
                                for index, face_i in enumerate(detect_results[0]):
                                    i_box = detect_results[2][index]
                                    print(i_box)
                                    imageVar = cv2.Laplacian(frame[i_box[1]:i_box[3],i_box[0]:i_box[2],:], cv2.CV_64F).var()
                                    cv2.imencode('.png',frame[i_box[1]:i_box[3],i_box[0]:i_box[2],:])[1].tofile("wocao.png")
                                    # print("save path: ",f_path)
                                    if imageVar < blur_t:
                                        print("Image var=%.3f. Over blurry image!"%imageVar)
                                        continue
                                    f_path =os.path.join(tg_path, str(frame_index).zfill(6)+"_%d.%s"%(index,tg_format))
                                    cv2.imencode('.png',face_i)[1].tofile(f_path)
                            # else:
                            #     print("No face detected!")

            else:
                print("Input a dir....")
                
            print("Process finished!")
        else:
            print("Pathes are invalid!")

    def on_closing(self):

        # self.__save_config__()
        self.master.destroy()
    


if __name__ == "__main__":
    app = Application()
    app.mainloop()