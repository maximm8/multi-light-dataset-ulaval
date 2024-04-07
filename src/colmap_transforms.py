import os
import json
import numpy as np
import cv2

def read_file(fn):
    with open(fn) as f:
        contents = f.readlines()

    return contents

def create_output_dirs(output_dir):
    if os.path.exists(f'{output_dir}/images'):
        return

    os.makedirs(f'{output_dir}/images')
    os.makedirs(f'{output_dir}/images_2')
    os.makedirs(f'{output_dir}/images_4')
    os.makedirs(f'{output_dir}/images_8')

def get_intrinsics(cam_params):
    fx = float(cam_params[0])
    cx = float(cam_params[2])
    fy = float(cam_params[4])
    cy = float(cam_params[5])

    return fx, fy, cx, cy


dataset_name = 'bottle'
output_dir = f'output/{dataset_name}'

create_output_dirs(output_dir)

fn = f'data/{dataset_name}/params/camera_bw_int.txt'
cam_params = read_file(fn)[0].split()
fn = f'data/{dataset_name}/params/camera_bw_ext.txt'
cam_pose = read_file(fn)

fx, fy, cx, cy = get_intrinsics(cam_params)

data = {}
data ["camera_model"]   =  'OPENCV'
data ["fl_x"]           =  fx
data ["fl_y"]           =  fy
data ["cx"]             =  cx
data ["cy"]             =  cy
data ["w"]              =  2448
data ["h"]              =  2048
data['k1']              = 0
data['k2']              = 0
data['p1']              = 0
data['p2']              = 0

data_frames = []
# bad_views = np.array([35, 49, 254, 263, 273, 291, 302, 305, 317, 319, 321, 324])-1 

k = 1
img_step = 10
for i, pose in enumerate(cam_pose):
    # if i in bad_views:
    #     continue

    if i%img_step !=0:
        continue

    try:
        M = np.array(pose.split(), dtype=np.float32).reshape(4,4)
        r = M[0:3, 0:3]
        t = M[0:3,3][:,None]
        M2 = np.concatenate([r, t], axis=1)        
        M2 = np.concatenate([M2, np.array([0,0,0, 1])[None,:]], axis=0)


        frame = {'file_path': f'images/frame_{k:05d}.jpg', 
                 'transform_matrix':M2.tolist(),
                 'colmap_im_id': k}
        data_frames.append(frame)

        img = cv2.imread(f'data/{dataset_name}/images/PoseCameras_{i:03d}_00_BW.png')
        cv2.imwrite(f'{output_dir}/images/frame_{k:05d}.jpg', img)

        img = cv2.resize(img, (int(img.shape[1]*0.5), int(img.shape[0]*0.5)))
        cv2.imwrite(f'{output_dir}/images_2/frame_{k:05d}.jpg', img)

        img = cv2.resize(img, (int(img.shape[1]*0.5), int(img.shape[0]*0.5)))
        cv2.imwrite(f'{output_dir}/images_4/frame_{k:05d}.jpg', img)

        img = cv2.resize(img, (int(img.shape[1]*0.5), int(img.shape[0]*0.5)))
        cv2.imwrite(f'{output_dir}/images_8/frame_{k:05d}.jpg', img)
        k += 1

    except:
        print('bad view', i)
        print(M)


data['frames'] = data_frames

with open(f'{output_dir}/transforms.json', 'w') as f:
    json.dump(data, f, sort_keys=True, indent=4)
    