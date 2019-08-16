# Description
An UI tool designed for manually cropping two rectangular areas of an image in any customized size.

## Directory Layout
```
imglabeltool                 
├── dataset                     
│   └── xray                  
│       ├── 150057.jpg
|       ├── 160022.jpg
|       ├── 160565.jpg
|       ├── 170116.jpg
|       ├── 180006.jpg
|       ├── annotation.csv    <-- Most follow this format as an input of label.py
|       └── coordinate.json   <-- It's an output of label.py and the input of cut.py
├── cropped_L                 <-- Generate left desired region after running cut.py
│   ├──150057_L.jpg
│   :
│   └──
├── cropped_R                 <-- Generate right desired region after running cut.py
│   ├──150057_R.jpg
│   :
│   └──
├── cropped_L_flip            <-- Generate mirrored left desired region after running cut.py
│   ├──150057_L_flip.jpg
│   :
│   └──
├── cropped_R_flip            <-- Generate mirrored right desired region after running cut.py
│   ├──150057_R_flip.jpg
│   :
│   └──
├── cropped_cust_L            <-- Generate left desired region in customed size after running cut.py -s xxx
│   ├──150057_L.jpg
│   :
│   └──
├── cropped_cust_R            <-- Generate right desired region in customed size after running cut.py -s xxx
│   ├──150057_R.jpg
│   :
│   └── 
├── cropped_cust_L_flip       <-- Generate mirrored left desired region in customed size after running cut.py -s xxx
│   ├──150057_L_flip.jpg
│   :
│   └── 
├── cropped_cust_R_flip       <-- Generate mirrored right desired region in customed size after running cut.py -s xxx
│   ├──150057_R_flip.jpg
│   :
│   └── 
├── cut.py                
├── label.py                     
└── README.md
```

## Usage
```label.py``` -- Manually crop an image in a customized size. The coordinate, width and height are recorded in a json file.  
```cut.py```  -- Read the abovementioned json to genereate an image dataset.


## Run in 3 steps
1. Prepare the dataset and a csv. The csv should include all image ids.

2. Manually cropping.
```
  $ cd imglabeltool
  $ python label.py
```
3. Generate cropped images in the size of 500x500.
```
  $ python cut.py
```  
Or if you want to generate a dataset in other size, e.g., 224x224 :

```
  $ python cut.py -s 224
```  
