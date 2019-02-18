import json
import cv2
from pathlib import Path

'''
if Path(self.json_file).exists():
    with open(self.json_file, 'r') as f:
        self.json_data = json.load(f)
        self.json_data.append(data)

    with open(self.json_file, 'w') as f:
        json.dump(self.json_data, f)
'''

def main():
    json_file    = 'dataset/xray/coordinates.json'
    dataset_file = 'dataset/xray/'
    cropped_file = 'cropped_imgs/'
    
    if Path(json_file).exists():
        with open(json_file, 'r') as f:
            json_data = json.load(f)
        print(json.dumps(json_data, indent=4, sort_keys=True))

        for i in range(0, len(json_data)):           
            ori_img = cv2.imread(dataset_file + json_data[i]['patientID'] + '.jpg')
            img     = ori_img.copy()

            ###e.g. CROP_IMG = IMG[y:y+h, x:x+w]
            img_L   = img[json_data[i]['left_y']:json_data[i]['left_y']+json_data[i]['left_height'], json_data[i]['left_x']:json_data[i]['left_x']+json_data[i]['left_width']]
            img_R   = img[json_data[i]['right_y']:json_data[i]['right_y']+json_data[i]['right_height'], json_data[i]['right_x']:json_data[i]['right_x']+json_data[i]['right_width']]
            
            filename_L = cropped_file + json_data[i]['patientID'] + '_L.jpg'
            filename_R = cropped_file + json_data[i]['patientID'] + '_R.jpg'

            cv2.imwrite(filename_L, img_L)
            cv2.imwrite(filename_R, img_R)

if __name__ == '__main__':
    main()