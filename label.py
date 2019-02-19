import tkinter
import json
import time
import numpy as np
import pandas as pd
from tkinter import Toplevel
from tkinter import Scrollbar
import cv2
import PIL.Image, PIL.ImageTk, PIL.ImageDraw
from pathlib import Path
import fnmatch
import os
from PyQt5.QtWidgets import QApplication

class App:
    def __init__(self, master, window_title='cropping tool', dataset_path='dataset/'):
        self.window = master
        self.window.title(window_title)
        self.center(self.window)
        self.popup_switch = 0
        self.popup_flag   = 0
        self.dataset_path = dataset_path + 'xray/'
        self.csv_file     = dataset_path + 'xray/annotation.csv'
        self.json_file    = dataset_path + 'xray/coordinates.json'

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
        
        
        # Get whole X-ray list by going through dataset and get the starting information by checking CSV file.
        self.xray_list = get_xray_list()
        self.df, self.startIndex = self.read_todoList(self.csv_file)
        self.img_path = str(self.xray_list[self.startIndex].absolute())
        self.img_id   = self.xray_list[self.startIndex].stem

        #[Frame] Including upper half
        self.upframe = tkinter.Frame(self.window)
        self.upframe.pack()
        
        self.entry_id_var = tkinter.StringVar(self.upframe)
        self.entry_id_var.set(self.img_id)
        self.entry_id = tkinter.Entry(self.upframe, textvariable=self.entry_id_var, state='disabled')
        self.entry_id.config(disabledforeground='red', disabledbackground='yellow')
        self.entry_id.pack(anchor=tkinter.N)

        #[ENTRY] Creat a entry where user can decide the cropping size
        self.crop_height = tkinter.StringVar(self.upframe)
        self.crop_width = tkinter.StringVar(self.upframe)
        self.height = 100
        self.width  = 100
        self.crop_height.set("100") # default size 100*100
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
            self.canvas.yview_scroll(-1*(event.delta), "units")

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
            if self.popup_flag==1:
                return
            self.img = self.cv_img.copy()
            self.overlay = self.cv_img.copy()
            self.opacity = 0.3
            self.canvasx = event.x
            self.canvasy = event.y
            cv2.rectangle(self.overlay,(int(self.canvas.canvasx(event.x))-int(self.width/2),int(self.canvas.canvasy(event.y))-int(self.height/2)), 
            (int(self.canvas.canvasx(event.x))+int(self.width/2),int(self.canvas.canvasy(event.y))+int(self.height/2)),(255,255,0),-1)

            cv2.addWeighted(self.overlay, self.opacity, self.img, 1 - self.opacity, 0, self.img)

            if hasattr(self, 'img'):
                self.canvas.delete("all")
            self.image = PIL.Image.fromarray(self.img)
            self.photo = PIL.ImageTk.PhotoImage(self.image)
            self.canvas.create_image(0, 0, image=self.photo, anchor=tkinter.NW)
            # debug only
            #print('{},{}'.format(self.canvas.canvasx(event.x),self.canvas.canvasy(event.y)))
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
            self.popup_flag = 1
            # Left bone   
            if self.popup_switch == 0:
                self.popup = Toplevel(self.window)
                self.popup.title("Sure?")
                self.popup_label = tkinter.Label(self.popup,text="Left hand side", fg="black")
                self.popup_label.config(width=20)
                self.popup_label.config(font=("Courier", 14))
                self.popup.geometry("%dx%d" % (200, 200))
                self.center(self.popup)
                self.popup_label.pack()
            
                self.btn_popup1 = tkinter.Button(self.popup, text="OK", height=5, width=5, command=self.popup_ok)
                self.btn_popup2 = tkinter.Button(self.popup, text="CANCLE", height=5, width=5, command=self.popup_cancle)
                self.btn_popup1.pack(side=tkinter.RIGHT)
                self.btn_popup2.pack(side=tkinter.LEFT)
            # Right bone
            else:          
                self.popup = Toplevel(self.window)
                self.popup.title("Sure?")
                self.popup_label = tkinter.Label(self.popup,text="Right hand side", fg="black")
                self.popup_label.config(width=20)
                self.popup_label.config(font=("Courier", 14))
                self.popup.geometry("%dx%d" % (200, 200))
                self.center(self.popup)
                self.popup_label.pack()
            
                self.btn_popup1 = tkinter.Button(self.popup, text="OK", height=5, width=5, command=self.popup_ok)
                self.btn_popup2 = tkinter.Button(self.popup, text="CANCLE", height=5, width=5, command=self.popup_cancle)
                self.btn_popup1.pack(side=tkinter.RIGHT)
                self.btn_popup2.pack(side=tkinter.LEFT)
        self.window.mainloop()
    
    # Set window on the center
    def center(self, toplevel):
        toplevel.update_idletasks()

        # Tkinter way to find the screen resolution
        # screen_width = toplevel.winfo_screenwidth()
        # screen_height = toplevel.winfo_screenheight()

        # PyQt way to find the screen resolution
        app = QApplication([])
        screen_width = app.desktop().screenGeometry().width()
        screen_height = app.desktop().screenGeometry().height()

        size = tuple(int(_) for _ in toplevel.geometry().split('+')[0].split('x'))
        x = screen_width/2 - size[0]/2
        y = screen_height/2 - size[1]/2

        toplevel.geometry("+%d+%d" % (x, y))
        #toplevel.title("Centered!")    

    def set_canvas(self):
        self.cv_img = cv2.cvtColor(cv2.imread(self.img_path), cv2.COLOR_BGR2RGB)
        self.photo  = PIL.ImageTk.PhotoImage(image = PIL.Image.fromarray(self.cv_img))
        self.canvas.create_image(0, 0, image=self.photo, anchor=tkinter.NW)
        self.canvas.pack(side = 'left', fill = 'both')
        self.canvas.config(scrollregion=self.canvas.bbox('all'))
        
        self.entry_id_var.set(self.img_id)
    
    # Read CSV file 
    def read_todoList(self, csv_file):
        df = pd.read_csv(csv_file)
        df_notCrop = df[df['Cropped']!='Y']
        #todoList = df_notCrop.iloc[0:]['PatientID'].tolist()
        startIndex = np.where(df['Cropped']!='Y')[0].tolist()[0]
        #print('******', df.at[startIndex,'Cropped'])
        #print("whole list = ",df.iloc[0:]['PatientID'].tolist())
        
        return df, startIndex

    # Update csv whenever finishing an image.
    def write_csv(self, df, row, column, path):
        df.to_csv(path+'annotation_prev.csv',index=0)
        df2 = df
        df2.at[row, column] = 'Y'
        df2.at[row, 'Time'] = time.strftime("%b/%d/%X", time.localtime())       
        df2.to_csv(path+'annotation.csv',index=0)
    
    # Save cropped mask
    def save_mask(self,side='L'):
        left_x  = self.currentx-int(self.width/2)-25
        left_y  = self.currenty-int(self.height/2)-25
        right_x = self.currentx+int(self.width/2)+25
        right_y = self.currenty+int(self.height/2)+25

        if side == 'L':
            if not os.path.exists(self.dataset_path+ 'crop_L/'):
                os.makedirs(self.dataset_path+ 'crop_L/')
            file_name = self.dataset_path + 'crop_L/' + self.img_id + '_' + side + '.jpg'
        else:
            if not os.path.exists(self.dataset_path+ 'crop_R/'):
                os.makedirs(self.dataset_path+ 'crop_R/')
            file_name = self.dataset_path + 'crop_R/' + self.img_id + '_' + side + '.jpg'

        self.image.crop((left_x,left_y,right_x,right_y)).save(file_name)
        
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
        self.height = int(self.crop_height.get())
        self.width  = int(self.crop_width.get())
        
    #[BUTTON][CALLBACK] Callback for new_page popup "OK" button
    def popup_ok(self):
        # Left bone is finished
        if self.popup_switch == 0:
                self.popup_switch = 1
                self.left_x = int(self.currentx - self.width/2)
                self.left_y = int(self.currenty - self.height/2)
                self.left_height = self.height
                self.left_width  = self.width
                self.save_mask(side='L')                

        # Right bone is finished
        else:
            self.popup_switch = 0
            self.write_csv(self.df, row=self.startIndex, column='Cropped', path=self.dataset_path)
            
            first_data = [{
                'patientID': self.img_id,
                'left_x': self.left_x,
                'left_y': self.left_y,
                'left_width': self.left_width,
                'left_height': self.left_height,
                'right_x': int(self.currentx - self.width/2),
                'right_y': int(self.currenty - self.height/2),
                'right_width': self.width,
                'right_height': self.height
            }]

            data = {
                'patientID': self.img_id,
                'left_x': self.left_x,
                'left_y': self.left_y,
                'left_width': self.left_width,
                'left_height': self.left_height,
                'right_x': int(self.currentx - self.width/2),
                'right_y': int(self.currenty - self.height/2),
                'right_width': self.width,
                'right_height': self.height
            }

            self.save_mask(side='R')
            
            if Path(self.json_file).exists():
                with open(self.json_file, 'r') as f:
                    self.json_data = json.load(f)
                    self.json_data.append(data)

                with open(self.json_file, 'w') as f:
                    json.dump(self.json_data, f)
            else:
                with open(self.json_file, 'w') as f:
                    json.dump(first_data, f)

            self.startIndex += 1
            self.img_path    = str(self.xray_list[self.startIndex].absolute())
            self.img_id      = self.xray_list[self.startIndex].stem
            
            self.set_canvas()

        self.popup.destroy()
        self.popup_flag = 0

    #[BUTTON][CALLBACK] Callback for new_page popup "CANCLE" button
    def popup_cancle(self):
        self.popup.destroy()
        self.popup_flag = 0

# Create a window and pass it to the Application object
App(tkinter.Tk(), "Cropper")

