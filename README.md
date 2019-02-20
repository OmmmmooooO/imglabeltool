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
|       └── annotation.csv   <-- Most follow this format as input of label.py
├── cropped_imgs             <-- An empty folder before running cut.py
│   ├──
│   :
│   └── 
├── cropped_cust             <-- An empty folder before running cut.py -s xxx
│   ├──
│   :
│   └── 
├── cut.py                
├── label.py                     
└── README.md
```

## Usage
```label.py``` -- Manually crop a image in a customized size. The coordinate, width and height are recorded in a json file.  
```cut.py```  -- Read the abovementioned json to genereate an image dataset.


## Run in 3 steps
1. Prepare the dataset and a csv. The csv should include all image ids.

2. Manually cropping
```
  $ cd imglabeltool
  $ python label.py
```
3. Generate cropped images
```
  $ python cut.py
```  
      Or if you want to generate a dataset in other size, e.g., 224x224 :

```
  $ python cut.py -s 224
```  
