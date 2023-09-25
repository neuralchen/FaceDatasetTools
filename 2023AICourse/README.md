# 课程指南 （持续更新中，请同学们多关注）

## 课程目的及意义
目前换脸算法已经成为人脸编辑/重演领域应用最为广泛的算法，其已经广泛的应用于视频直播、短视频制作、电子商务，甚至电影等场景。换脸算法目前主要有DeepFacelab式、simswap式两种类型的算法路线。Deepfacelab需要针对每一个目标人物训练模型，其特点是效果好，训练代价大。SimSwap不需要针对目标人物训练，它是一种One-shot式的换脸算法，模型一旦训练后可以实现任意人脸不经训练即可实现换脸，其特点是应用方便简单，不依赖特定人物的训练，但其效果相较Deepfacelab逊色。目前，已经发展出大量后续的框架以取代前面两者，例如：应用于直播的deepface live，one-shot界面友好的roop/ROPE/facefusion等。这些算法，他们具有相同的通病，只能处理低清的图片（也即224*224/256/112），光影效果差，需要依赖人脸超分来提示质量，即使通过超分提升分辨率，其人脸质量、光影等等属性与电影级别的应用场景仍有不小的差距。


### SimSwap++(TPAMI)的效果
[Source ID: Scarlett Johansson Target ID: Iron Man (1080p on YouTube)](https://youtu.be/zMpejDaYFHg)

[![Scarlett Johansson](https://github.com/neuralchen/SimSwapPlus/blob/main/docs/video/id_ScarlettJohansson--attr_AvengersEndgmeIAmIronMan.gif)](https://youtu.be/zMpejDaYFHg)

## 项目内容
本项目致力于提升换脸模型的生成质量，瞄准其最核心的问题：缺乏大规模的电影场景高分辨率人脸数据集。
具体而言，本项目分为三个步骤：
- 第一步下载数据[数据列表](./video_list.md)，需要说明的是每组数据大体数据量相当；
- 第二步，利用本项目中提供的[face_crop_video.py](../face_crop_video.py)来实现从电影数据中粗截取人脸，其使用说明参考[README.md](../README.md)，同学们需要首先参照```Dependencies```安装环境依赖。注意每一部电影需要为其建立一个独立的文件夹以免后续结果覆盖。通过这个脚本得到的数据经常有数据冗余的问题请调整GUI界面中的```Frame Interval```，它用来抽样视频中的帧，取的数值也即多少帧抽样一次。人脸也有可能比较模糊，同学们可以通过调整```Blurry Thredhold```的数值来调整软件筛选人脸清晰度的数值，这个数值越大人脸需要越清晰，也意味着软件会抛弃掉更多的人脸，建议这个数值设置在20~30。人脸分辨率统一规定为```1024*1024```，文件格式统一为```.png```，对齐方式统一为```FFHQ```；
- 第三步，利用本项目中提供的[face_cluster.py](../face_cluster.py)来实现对第二步得到的人脸按其身份进行粗分类，我们最终目标的数据是以人物身份作为文件夹归档，不同的人必须位于不同的文件夹中。这一步需要调整GUI中的聚类中心的数目，需要我们事先大概估计目标文件夹中的人物数量，然后聚类中心取为预估数量的两倍，这样以来GUI可以把不能良好识别的人脸从正常人脸中剥离，注意这一部分软件只能起到粗分类的作用，通过加大聚类中心的数目可以缓解软件将不同的人物分类到同一个文件夹的问题。得到粗分类结果后，我们对这些数据进行手工清洗，去掉人脸朝向角度过大的数据、去掉过于模糊的数据、去掉五官不全的数据、去掉没有被良好对齐的数据。

- ***数据上传***：数据统一保存在***交大云盘***中，请将数据上传至与自己组别一致的文件夹中，请将文件压缩为```.zip```上传，请注意上传的为***清洗后的数据***，链接：[交大云盘](https://jbox.sjtu.edu.cn/l/31pA46)


## 标准人脸样例：
![Alt text](1695669816913.png)

如上图所示，左右眼中心，鼻尖，两嘴角位于图像中相近的区域即可认定为标准人脸，并且注意以这五点区域向外延拓的区域也应与上图类似。
- ***人脸对齐失败***：另外可接受的图片可以以两眼关键点的连线为参考，如若连线显著性倾斜，例如：水平轴与两眼中心点连线超过+/-30度以上即可认定为显著性倾斜，即可抛弃。
- ***人脸放缩失败***：人脸过小，例如：人脸只占图像40%面积以下即可认定为过小，即可抛弃。
- ***大幅度侧脸***：完全侧脸，人脸朝向与镜头呈90度，只要不违背上述两条即可留下。完全背过


## 正常图片样例：
<table frame=void>
	<tr>		  
    <td><center><img src="./normalcase/035300_0.png"		
                     alt="out-of-focus"
                     height="300"/></center></td>
    <td><center><img src="./normalcase/036920_0.png"
                     alt="motion blurry"
                     height="300"/></center></td>
    <td><center><img src="./normalcase/057240_0.png"
                     alt="out-of-focus"
                     height="300"/></center></td>
    </tr>
    <tr>
    <td><center><img src="./normalcase/011120_0.png"
                     alt="out-of-focus"
                     height="300"/></center></td>
    <td><center><img src="./normalcase/048820_0.png"
                     alt="out-of-focus"
                     height="300"/></center></td>
    <td><center><img src="./normalcase/007850_0.png"
                     alt="out-of-focus"
                     height="300"/></center></td>
    </tr>
    
</table>


## 需要被丢弃的图片样例：

### 图像模糊，包括运动失焦、失焦：
<table frame=void>
	<tr>		  
    <td><center><img src="./badcase/000840_1.png"		
                     alt="out-of-focus"
                     height="300"/></center></td>
    <td><center><img src="./badcase/017540_0.png"
                     alt="motion blurry"
                     height="300"/></center></td>
    <td><center><img src="./badcase/006620_1.png"
                     alt="out-of-focus"
                     height="300"/></center></td>
    </tr>
    <tr>		  
    <td><center><img src="./badcase/054680_0.png"		
                     alt="out-of-focus"
                     height="300"/></center></td>
    <td><center><img src="./badcase/010020_0.png"
                     alt="motion blurry"
                     height="300"/></center></td>
    <td><center><img src="./badcase/016290_0.png"
                     alt="out-of-focus"
                     height="300"/></center></td>
    </tr>
</table>

### 五官不全，无法辨认主体身份：

<table frame=void>
	<tr>		  
    <td><center><img src="./badcase/006430_2.png"		
                     alt="out-of-focus"
                     height="300"/></center></td>
    <td><center><img src="./badcase/006430_3.png"
                     alt="motion blurry"
                     height="300"/></center></td>
    <td><center><img src="./badcase/024190_3.png"
                     alt="out-of-focus"
                     height="300"/></center></td>
    </tr>
</table>



其工作流可以总结如下图：

![workflow](./workflow.PNG)

任何问题请邮件：[xuanhong chen](mailto:chenxuanhongzju@outlook.com)

对研究项目感兴趣的同学也可以邮件咨询，欢迎对于***虚拟人***、***电影换脸***、***人脸重建***、***AIGC***感兴趣的同学前来咨询。

## 相关链接：
- https://github.com/neuralchen/SimSwap
- https://github.com/neuralchen/SimSwapPlus
