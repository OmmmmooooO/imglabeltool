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
    if Path(json_file).exists():
        with open(json_file, 'r') as f:
            json_data = json.load(f)
        #print(json.dumps(json_data, indent=4, sort_keys=True))

        for i in range(0, len(json_data)):
            print(json_data[i]['patientID'])
            ori_img = cv2.imread(dataset_file + json_data[i]['patientID'] + '.jpg')
            img     = ori_img.copy()

            ###e.g. CROP_IMG = IMG[y:y+h, x:x+w]
            img_L   = img[json_data[i]['left_y']:json_data[i]['left_y']+json_data[i]['left_height'], json_data[i]['left_x']:json_data[i]['left_x']+json_data[i]['left_width']]
            img_R   = img[]
            
            #cv2.imshow("cropped", crop_img)

if __name__ == '__main__':
    main()