import tkinter
import json
import numpy as np
import pandas as pd
from tkinter import Toplevel
from tkinter import Scrollbar
import cv2
import PIL.Image, PIL.ImageTk, PIL.ImageDraw
from pathlib import Path
import fnmatch
import os

class App:
    def __init__(self, master, window_title='cropping tool', dataset_path='dataset/'):
        self.window = master
        self.window.title(window_title)
        self.popup_switch = 0
        #self.img_path     = dataset_path + 'test.png'
        #self.img_id       = '150057'  #first image
        self.dataset_path = dataset_path + 'xray/'
        self.csv_file     = dataset_path + 'annotation.csv'
        
        def get_img_list():
            DATASET_DIR       = Path().cwd() / 'dataset'/ 'CHD'
            DATASET_DIR_LIST  = list(DATASET_DIR.glob('*'))
            img_list          = list()

            for data_dir in sorted(DATASET_DIR_LIST):
                img_id      = data_dir.stem
                img_name    = img_id + '_VD'
                img_name_de = img_id + '_VDanno'
                img_list += sorted(list(set(data_dir.glob(img_name + '*')) - set(data_dir.glob(img_name_de + '*'))))
            #print(str(img_list[0].absolute()))
            return img_list

        def get_xray_list():
            DATASET_DIR = Path().cwd() / 'dataset'/ 'xray'
            dataList    = sorted(list(DATASET_DIR.glob('*.jpg')))
            return dataList
        
        #self.img_list  = get_img_list()
        
        # Get whole X-ray list by going through dataset and get the starting information by checking CSV file.
        self.xray_list = get_xray_list()
        self.df, self.startIndex = self.read_todoList(self.csv_file)
        self.img_path = str(self.xray_list[self.startIndex].absolute())
        self.img_id   = self.xray_list[self.startIndex].stem

        #self.img_list_index = self.startIndex  #first image index in img_list
        #print('xray_list[start]=',str(self.xray_list[self.startIndex].absolute()))

        #[Frame] Including upper half
        self.upframe = tkinter.Frame(self.window)
        self.upframe.pack()
        
        self.entry_id_var = tkinter.StringVar(self.upframe)
        self.entry_id_var.set(self.img_id)
        self.entry_id = tkinter.Entry(self.upframe, textvariable=self.entry_id_var, state='disabled')
        self.entry_id.config(disabledforeground='red', disabledbackground='yellow')
        self.entry_id.pack(anchor=tkinter.N)

        '''
        #[Label]
        self.l1 = tkinter.Label(self.upframe, text=self.img_id, fg="red", bg="yellow")
        self.l1.pack(anchor=tkinter.N)   
        '''

        '''
        #[ENTRY] Creat a entry where user can decide the cropping size
        self.id = tkinter.StringVar(self.upframe)
        self.id.set(self.img_id)
        '''
        #self.entry_id = tkinter.Entry(self.upframe, validate = 'key', validatecommand = vcmd, textvariable=self.id)
        #self.entry_id.pack(anchor=tkinter.N)

        #[ENTRY] Creat a entry where user can decide the cropping size
        self.crop_height = tkinter.StringVar(self.upframe)
        self.crop_width = tkinter.StringVar(self.upframe)
        self.crop_height.set("100") # default size
        self.crop_width.set("100")
        vcmd = (self.upframe.register(self.validate), '%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W')
        self.entry_height = tkinter.Entry(self.upframe, validate = 'key', validatecommand = vcmd, textvariable=self.crop_height)
        self.entry_width = tkinter.Entry(self.upframe, validate = 'key', validatecommand = vcmd, textvariable=self.crop_width)  
        self.entry_height.pack(anchor=tkinter.N)
        self.entry_width.pack(anchor=tkinter.N)
        
        #[BUTTON] Button for determining the crop size and image starting id       
        self.btn_crop_size = tkinter.Button(self.upframe, text="OK", width=10, command=self.crop_size)
        self.btn_crop_size.pack(anchor=tkinter.N, expand=True)
        
        #[Frame] Including lower half
        self.downframe = tkinter.Frame(self.window, width=800,height=800)
        self.downframe.pack()
        
        #[Scrollbar]
        self.yscrollbar = Scrollbar(self.downframe, orient='vertical', width=20)
        self.yscrollbar.pack(side='right', fill='y')
        self.xscrollbar = Scrollbar(self.downframe, orient='horizontal', width=20)
        self.xscrollbar.pack(side='bottom', fill='x')
        
        #[MOUSEWHEEL][CALLBACK]
        def bound_to_mousewheel(event):
            self.canvas.bind_all("<MouseWheel>", func=on_mousewheel)
        #[MOUSEWHEEL][CALLBACK]
        def unbound_to_mousewheel(event):
            self.canvas.unbind_all("<MouseWheel>")
        #[MOUSEWHEEL][CALLBACK]
        def on_mousewheel(event):
            self.canvas.yview_scroll(-1*(event.delta/120), "units")

        #[CANVAS] Create a canvas to fit a image
        self.canvas_height = 600
        self.canvas_width  = 800
        self.canvas = tkinter.Canvas(self.downframe, width = self.canvas_width, height = self.canvas_height, xscrollcommand = self.xscrollbar.set, yscrollcommand=self.yscrollbar.set)
        self.xscrollbar.config(command = self.canvas.xview)
        self.yscrollbar.config(command = self.canvas.yview)
        self.yscrollbar.bind('<Enter>', func=bound_to_mousewheel)
        self.yscrollbar.bind('<Leave>', func=unbound_to_mousewheel)
        self.set_canvas()
        
        #[MASK][CALLBACK] Draw a rectangle mask which follows the mouse
        def mask(event):
            self.img = self.cv_img.copy()
            self.overlay = self.cv_img.copy()
            self.opacity = 0.3
            self.canvasx = event.x
            self.canvasy = event.y
            if hasattr(self,'mask_height'): # customized mask size
                cv2.rectangle(self.overlay,(int(self.canvas.canvasx(event.x))-int(self.mask_width/2),int(self.canvas.canvasy(event.y))-int(self.mask_height/2)),
                (int(self.canvas.canvasx(event.x))+int(self.mask_width/2),int(self.canvas.canvasy(event.y))+int(self.mask_height/2)),(255,255,0),-1)
            else: # default mask size is 100x100
                cv2.rectangle(self.overlay,(int(self.canvas.canvasx(event.x))-50,int(self.canvas.canvasy(event.y))-50),
                (int(self.canvas.canvasx(event.x))+50,int(self.canvas.canvasy(event.y))+50),(255,255,0),-1)
            cv2.addWeighted(self.overlay, self.opacity, self.img, 1 - self.opacity, 0, self.img)
            
            if hasattr(self, 'img'):
                self.canvas.delete("all")

            self.photo = PIL.ImageTk.PhotoImage(image = PIL.Image.fromarray(self.img))
            self.canvas.create_image(0, 0, image=self.photo, anchor=tkinter.NW)
            # debug only
            print('{},{}'.format(self.canvas.canvasx(event.x),self.canvas.canvasy(event.y)))
        self.canvas.bind("<Motion>", func=mask)
        
        #[CLICK][CALLBACK] Capture click position
        def click(event):
            self.currentx = int(self.canvas.canvasx(event.x))
            self.currenty = int(self.canvas.canvasy(event.y))
            print ("clicked at", self.currentx, self.currenty)
            new_page(self)
        self.canvas.bind("<Button-1>", func=click)

        #[CLICK][CALLBACK] Create pop-up window
        def new_page(self):
            # Left bone   
            if self.popup_switch == 0:
                self.popup = Toplevel(self.window)
                self.popup.title("Sure?")
                self.popup_label = tkinter.Label(self.popup,text="Left bone", fg="black")
                self.popup_label.config(width=20)
                self.popup_label.config(font=("Courier", 14))
                self.popup.geometry("%dx%d%+d%+d" % (150, 150, self.canvasx, self.canvasy))
                self.popup_label.pack()
            
                self.btn_popup1 = tkinter.Button(self.popup, text="OK", height=5, width=5, command=self.popup_ok)
                self.btn_popup2 = tkinter.Button(self.popup, text="CANCLE", height=5, width=5, command=self.popup_cancle)
                self.btn_popup1.pack(side=tkinter.RIGHT)
                self.btn_popup2.pack(side=tkinter.LEFT)
            # Right bone
            else:          
                self.popup = Toplevel(self.window)
                self.popup.title("Sure?")
                self.popup_label = tkinter.Label(self.popup,text="Right bone", fg="black")
                self.popup_label.config(width=20)
                self.popup_label.config(font=("Courier", 14))
                self.popup.geometry("%dx%d%+d%+d" % (150, 150, self.canvasx, self.canvasy))
                self.popup_label.pack()
            
                self.btn_popup1 = tkinter.Button(self.popup, text="OK", height=5, width=5, command=self.popup_ok)
                self.btn_popup2 = tkinter.Button(self.popup, text="CANCLE", height=5, width=5, command=self.popup_cancle)
                self.btn_popup1.pack(side=tkinter.RIGHT)
                self.btn_popup2.pack(side=tkinter.LEFT)
        self.window.mainloop()
        
    def set_canvas(self):
        
        self.cv_img = cv2.cvtColor(cv2.imread(self.img_path), cv2.COLOR_BGR2RGB)
        self.photo  = PIL.ImageTk.PhotoImage(image = PIL.Image.fromarray(self.cv_img))
        self.canvas.create_image(0, 0, image=self.photo, anchor=tkinter.NW)
        self.canvas.pack(side = 'left', fill = 'both')
        self.canvas.config(scrollregion=self.canvas.bbox('all'))
        
        self.entry_id_var.set(self.img_id)
    
    # read CSV file 
    def read_todoList(self, csv_file):
        df = pd.read_csv(csv_file)
        df_notCrop = df[df['Cropped']=='N']
        #todoList = df_notCrop.iloc[0:]['PatientID'].tolist()
        startIndex = np.where(df['Cropped']=='N')[0].tolist()[0]
        print('******', df.at[startIndex,'Cropped'])
        #print("whole list = ",df.iloc[0:]['PatientID'].tolist())
        return df, startIndex

    # Update annotation_new.csv whenever finishing an image.
    def write_csv(self, df, row, column, path):
        df2 = df
        df2.at[row, column] = 'Y'
        path = path + 'annotation_new.csv'
        #df2.to_csv(path,index=0)
        
    def read_json(self):
        pass

    def write_json(self):
    
        pass
    # Valid list for entry object to restrict some characters.
    def validate(self, action, index, value_if_allowed, prior_value, text, validation_type, trigger_type, widget_name):
        if text in '0123456789':
            try:
                float(value_if_allowed)
                return True
            except ValueError:
                return False
        else:
            return False

    #[BUTTON][CALLBACK] Callback for btn_crop_size or "OK" button
    def crop_size(self):
        #self.canvas.delete("all")
        self.mask_height = int(self.crop_height.get())
        self.mask_width  = int(self.crop_width.get())
        '''
        self.entry_id.config(bg='red')

        self.img_id   = self.id.get()
        img_posixpath = [posixpath for posixpath in self.img_list if posixpath.match(self.img_id + '/*.jpg')]
        self.img_list_index = self.img_list.index(img_posixpath[0])
        self.img_path = str(img_posixpath[0])

        print('###self.img_path = %s\n' %self.img_path)
        print('***self.img_list_index = %d\n' %self.img_list_index)
        self.set_canvas()
        '''
    #[BUTTON][CALLBACK] Callback for new_page popup "OK" button
    def popup_ok(self):
        # Left bone is finished
        if self.popup_switch == 0:
                self.popup_switch = 1
        # Right bone is finished
        else:
            self.popup_switch = 0

            self.write_csv(self.df, self.startIndex, column='Cropped', path=self.dataset_path)
            #TO-DO save json

            self.startIndex += 1
            self.img_path    = str(self.xray_list[self.startIndex].absolute())
            self.img_id      = self.xray_list[self.startIndex].stem
            
            self.set_canvas()


        self.popup.destroy()
        
        #TO-DO save coordinate, next image
        pass

    #[BUTTON][CALLBACK] Callback for new_page popup "CANCLE" button
    def popup_cancle(self):
        self.popup.destroy()


# Create a window and pass it to the Application object
App(tkinter.Tk(), "Tkinter and OpenCV")

