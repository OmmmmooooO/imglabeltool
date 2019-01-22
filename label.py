import tkinter
from tkinter import Toplevel
from tkinter import Scrollbar
import cv2
import PIL.Image, PIL.ImageTk, PIL.ImageDraw
from pathlib import Path
import fnmatch
import os

class App:
    def __init__(self, master, window_title='cropping tool', dataset_path="dataset/"):
        self.window = master
        self.window.title(window_title)
        self.popup_switch = 0
        self.img_path     = dataset_path + 'test.png'
        self.img_id       = '150057'  #first image
        self.dataset_path = dataset_path + 'CHD/'
        
        def get_id_list():
            DATASET_DIR       = Path().cwd() / 'dataset'/ 'CHD'
            DATASET_DIR_LIST  = list(DATASET_DIR.glob('*'))
            id_list           = list()

            for data_dir in sorted(DATASET_DIR_LIST):
                img_id      = data_dir.stem
                img_name    = img_id + '_VD'
                img_name_de = img_id + '_VDanno'
                id_list += sorted(list(set(data_dir.glob(img_name + '*')) - set(data_dir.glob(img_name_de + '*'))))
            
            #print(str(id_list[10].absolute()))
            return id_list    
        self.id_list = get_id_list()
        print(str(self.id_list[1].absolute()))
        
        #[Frame] Including upper half
        self.upframe = tkinter.Frame(self.window)
        self.upframe.pack()

        #[Frame] Including lower half
        self.downframe = tkinter.Frame(self.window, width=800,height=800)
        self.downframe.pack()

        # TO-DO label of entry ---using grid and frame of whole theme
        self.l1 = tkinter.Label(self.upframe, text="Test", fg="red", bg="white")
        self.l1.pack(anchor=tkinter.N)      
        
        #[ENTRY] Creat a entry where user can decide the cropping size
        self.id = tkinter.StringVar(self.upframe)
        self.id.set(self.img_id)

        vcmd = (self.upframe.register(self.validate), '%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W')
        self.entry_id = tkinter.Entry(self.upframe, validate = 'key', validatecommand = vcmd, textvariable=self.id)
        self.entry_id.pack(anchor=tkinter.N)

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

        #[Scrollbar]
        self.yscrollbar = Scrollbar(self.downframe, orient='vertical')
        self.yscrollbar.pack(side='right', fill='y')
        self.xscrollbar = Scrollbar(self.downframe, orient='horizontal')
        self.xscrollbar.pack(side='bottom', fill='x')
        
        #[CANVAS] Create a canvas to fit a image
        self.canvas_height = 300
        self.canvas_width  = 300
        self.canvas = tkinter.Canvas(self.downframe, width = self.canvas_width, height = self.canvas_height, xscrollcommand = self.xscrollbar.set, yscrollcommand=self.yscrollbar.set)
        self.xscrollbar.config(command = self.canvas.xview)
        self.yscrollbar.config(command = self.canvas.yview)

        self.cv_img = cv2.cvtColor(cv2.imread(self.img_path), cv2.COLOR_BGR2RGB)
        self.photo  = PIL.ImageTk.PhotoImage(image = PIL.Image.fromarray(self.cv_img))
        
        self.canvas.create_image(0, 0, image=self.photo, anchor=tkinter.NW)
        self.canvas.pack(side = 'left', fill = 'both')
        self.canvas.config(scrollregion=self.canvas.bbox('all'))

        #[MASK][CALLBACK] Draw a rectangle mask which follows the mouse
        def mask(event):
            self.img = self.cv_img.copy()
            self.overlay = self.cv_img.copy()
            self.opacity = 0.3
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
            self.load_image()
        self.canvas.bind("<Button-1>", func=click)

        #[CLICK][CALLBACK] Create pop-up window
        def new_page(self):
            if self.popup_switch == 0:
                self.popup = Toplevel(self.window)
                self.popup.title("Sure?")
                self.popup_label = tkinter.Label(self.popup,text="Left bone", fg="black")
                self.popup_label.config(width=20)
                self.popup_label.config(font=("Courier", 14))
                self.popup.geometry("%dx%d%+d%+d" % (150, 150, self.window.winfo_x()+self.currentx, self.window.winfo_y()+self.currenty))
                self.popup_label.pack()
            
                self.btn_popup1 = tkinter.Button(self.popup, text="OK", height=5, width=5, command=self.popup_ok)
                self.btn_popup2 = tkinter.Button(self.popup, text="CANCLE", height=5, width=5, command=self.popup_cancle)
                self.btn_popup1.pack(side=tkinter.RIGHT)
                self.btn_popup2.pack(side=tkinter.LEFT)
            else:
                self.popup = Toplevel(self.window)
                self.popup.title("Sure?")
                self.popup_label = tkinter.Label(self.popup,text="Right bone", fg="black")
                self.popup_label.config(width=20)
                self.popup_label.config(font=("Courier", 14))
                self.popup.geometry("%dx%d%+d%+d" % (150, 150, self.window.winfo_x()+self.currentx, self.window.winfo_y()+self.currenty))
                self.popup_label.pack()
            
                self.btn_popup1 = tkinter.Button(self.popup, text="OK", height=5, width=5, command=self.popup_ok)
                self.btn_popup2 = tkinter.Button(self.popup, text="CANCLE", height=5, width=5, command=self.popup_cancle)
                self.btn_popup1.pack(side=tkinter.RIGHT)
                self.btn_popup2.pack(side=tkinter.LEFT)

        self.window.mainloop()

    # Read dataset
    def load_image(self):
        DATASET_DIR       = Path().cwd() / 'dataset'/ 'CHD'
        DATASET_DIR_LIST  = list(DATASET_DIR.glob('*'))
        self.dataset_path = DATASET_DIR
        self.vd_list      = list()

        for data_dir in sorted(DATASET_DIR_LIST):
            img_id      = data_dir.stem
            img_name    = img_id + '_VD'
            img_name_de = img_id + '_VDanno'
            self.vd_list += sorted(list(set(data_dir.glob(img_name + '*')) - set(data_dir.glob(img_name_de + '*'))))
        print(DATASET_DIR)
        #print(str(self.vd_list[0].absolute()))
        
    def set_canvas(self):
        dataset_path = self.dataset_path
        img_path = dataset_path + self.img_id + '/' + ''
        self.cv_img = cv2.cvtColor(cv2.imread(self.img_path), cv2.COLOR_BGR2RGB)
        self.photo  = PIL.ImageTk.PhotoImage(image = PIL.Image.fromarray(self.cv_img))
        
        self.canvas.create_image(0, 0, image=self.photo, anchor=tkinter.NW)
        self.canvas.pack(side = 'left', fill = 'both')
        self.canvas.config(scrollregion=self.canvas.bbox('all'))
        return img
    
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
        self.mask_height=int(self.crop_height.get())
        self.mask_width =int(self.crop_width.get())
        self.entry_id.config(bg='red')
        self.img_id = self.id.get()
        print(self.img_id)
        
        print(self.id_list[0].match(self.img_id +'/*.jpg'))
        #print (filter(lambda x: self.img_id in x, self.id_list))
        #self.set_canvas()



        '''
        # debug only
        print("crop_height=" ,self.mask_height)
        print("crop_width=" ,self.mask_width)
            
        self.load_image()        
        self.canvas.delete("all")
        self.img_path = str(self.vd_list[0].absolute())
        
        self.l1 = tkinter.Label(text=self.vd_list[0].stem, fg="red", bg="white")
        
        # Load an image using OpenCV
        self.cv_img = cv2.cvtColor(cv2.imread(self.img_path), cv2.COLOR_BGR2RGB)
        self.photo = PIL.ImageTk.PhotoImage(image = PIL.Image.fromarray(self.cv_img))
        self.height, self.width, no_channels = self.cv_img.shape

        #[CANVAS] Create a canvas that can fit the above image
        self.canvas = tkinter.Canvas(self.downframe, width = self.width, height = self.height, xscrollcommand = self.xscrollbar.set, yscrollcommand=self.yscrollbar.set)
        self.xscrollbar.config(command = self.canvas.xview)
        self.yscrollbar.config(command = self.canvas.yview)
        self.canvas.create_image(0, 0, image=self.photo, anchor=tkinter.NW)
        self.canvas.pack(side = 'left', fill = 'both')
        self.canvas.config(scrollregion=self.canvas.bbox('all'))
        '''
    #[BUTTON][CALLBACK] Callback for new_page popup "OK" button
    def popup_ok(self):
        if self.popup_switch == 0:
                self.popup_switch = 1
        else:
            self.popup_switch = 0
        self.popup.destroy()
        
        #TO-DO save coordinate, next image
        pass

    #[BUTTON][CALLBACK] Callback for new_page popup "CANCLE" button
    def popup_cancle(self):
        self.popup.destroy()

        #TO-DO
        pass
     
# Create a window and pass it to the Application object
App(tkinter.Tk(), "Tkinter and OpenCV")

