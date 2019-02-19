import json
import cv2
from pathlib import Path
from argparse import ArgumentParser

def main():
    parser = ArgumentParser()

    # Just to be simple, keep them in the same size is fine.
    # Cause we don't have much time to deal with images in such a subtle way. 
    '''
    parser.add_argument("-wl","--width-left", dest="width_left",type=int)
    parser.add_argument("-hl","--height-left", dest="height_left",type=int)
    parser.add_argument("-wr","--width-right", dest="width_right",type=int)
    parser.add_argument("-hr","--height-right", dest="height_right",type=int)
    parser.add_argument("-l","--square-left", dest="square_left",type=int)
    parser.add_argument("-r","--square-right", dest="square_right",type=int)
    parser.add_argument("-s","--square-size", dest="square_size",type=int)
    '''
    # Instead, a customized squared size is enough.
    parser.add_argument("-s","--size", dest="crop_size",type=int)
    args = parser.parse_args()

    json_file    = 'dataset/xray/coordinates.json'
    dataset_file = 'dataset/xray/'
    cropped_file = 'cropped_imgs/'
    cropped_cust = 'cropped_cust/'

    if Path(json_file).exists():
        with open(json_file, 'r') as f:
            json_data = json.load(f)
        print(json.dumps(json_data, indent=4, sort_keys=True))
        
        if args.crop_size is not None:
            crop_size = args.crop_size
            for i in range(0, len(json_data)):
                ori_img = cv2.imread(dataset_file + json_data[i]['patientID'] + '.jpg')
                img     = ori_img.copy()

                center_lefty  = json_data[i]['left_y'] + int(json_data[i]['left_height']/2)
                center_leftx  = json_data[i]['left_x'] + int(json_data[i]['left_width']/2)
                center_righty = json_data[i]['right_y'] + int(json_data[i]['right_height']/2)
                center_rightx = json_data[i]['right_x'] + int(json_data[i]['right_width']/2)

                left_y  = center_lefty - int(crop_size/2)
                left_x  = center_leftx - int(crop_size/2)
                right_y = center_righty - int(crop_size/2)
                right_x = center_rightx - int(crop_size/2)

                ###e.g. CROP_IMG = IMG[y:y+h, x:x+w]    upperleft point
                img_L = img[left_y:left_y+crop_size, left_x:left_x+crop_size]
                img_R = img[right_y:right_y+crop_size, right_x:right_x+crop_size]

                filename_L = cropped_cust + json_data[i]['patientID'] + '_L.jpg'
                filename_R = cropped_cust + json_data[i]['patientID'] + '_R.jpg'
                
                
                cv2.imwrite(filename_L, img_L)
                cv2.imwrite(filename_R, img_R)
                
                print("img_L = ",img_L.shape)
                print("img_R =",img_R.shape)

        else:
            for i in range(0, len(json_data)):           
                ori_img = cv2.imread(dataset_file + json_data[i]['patientID'] + '.jpg')
                img     = ori_img.copy()

                ###e.g. CROP_IMG = IMG[y:y+h, x:x+w]    upperleft point
                img_L   = img[json_data[i]['left_y']:json_data[i]['left_y']+json_data[i]['left_height'], json_data[i]['left_x']:json_data[i]['left_x']+json_data[i]['left_width']]
                img_R   = img[json_data[i]['right_y']:json_data[i]['right_y']+json_data[i]['right_height'], json_data[i]['right_x']:json_data[i]['right_x']+json_data[i]['right_width']]
                
                filename_L = cropped_file + json_data[i]['patientID'] + '_L.jpg'
                filename_R = cropped_file + json_data[i]['patientID'] + '_R.jpg'
                
                
                cv2.imwrite(filename_L, img_L)
                cv2.imwrite(filename_R, img_R)
                
                print("*img_L = ",img_L.shape)
                print("*img_R =",img_R.shape)
        
if __name__ == '__main__':
    main()