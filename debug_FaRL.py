import  os
import  cv2
import  torch

import  numpy as np
from    PIL import Image
from    torchvision import transforms
from    video_tools.faceparsing_FaRL import FaceParsing#, encode_segmentation_rgb
from    insightface_func.face_detect_crop_single import Face_detect


transformer_Arcface = transforms.Compose([
                transforms.ToTensor(),
                # transforms.Normalize([0.5, 0.5, 0.5], [0.5, 0.5, 0.5])
                transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
            ])

if __name__ == "__main__":
    mode = "ffhq"
    face_parser = FaceParsing()
    face_parser.reset_smooth_mask(5,5)
    detect = Face_detect(name='antelope', root='./insightface_func/models')
    detect.prepare(ctx_id = 0, det_thresh=0.6, det_size=(640,640),mode = mode)
    id_imgs  = "../id_img/ts_frame_0000021.png"
    tg_path  = "./"

    id_img                  = cv2.imread(id_imgs)
    id_img_align_crop, _    = detect.get(id_img,512)
    id_cv2_img              = id_img_align_crop[0]
    id_img_align_crop_pil   = Image.fromarray(cv2.cvtColor(id_img_align_crop[0],cv2.COLOR_BGR2RGB)) 
    id_img                  = transformer_Arcface(id_img_align_crop_pil)
    id_img                  = id_img.unsqueeze(0).cuda()
    out                     = face_parser.unionmask_fusion(id_img, id_img)
    out = out * 255
    print(out.shape)
    out = out.permute(0,2,3,1).cpu().numpy()
    out = list(out)
    filename    = os.path.splitext(os.path.basename(id_imgs))[0]
    # for i in range(18):
    #     mask               = face_parser.getmask(id_img, [i])
    #     mask = mask * 255
    #     mask = mask[0].cpu().numpy()
    #     f_path      = os.path.join(tg_path, "%s-lable-%d-mask.png"%(filename, i))
    #     cv2.imencode('.png', mask.astype(np.uint8))[1].tofile(f_path)
    # print(out.shape)
    # parsing                 = out.squeeze(0).argmax(0).cpu()

    # vis_parsing_anno        = parsing
    # vis_parsing_anno        = encode_segmentation_rgb(vis_parsing_anno)
    # print(vis_parsing_anno.shape)
    # # vis_parsing_anno = vis_parsing_anno[:,:,0] + vis_parsing_anno[:,:,1]
    
    for index, i_img in enumerate(out):
        f_path      = os.path.join(tg_path, "%s-%d-fused.png"%(filename, index))
        cv2.imencode('.png', i_img.astype(np.uint8))[1].tofile(f_path)
