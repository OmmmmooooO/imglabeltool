import tkinter
from tkinter import Toplevel
import cv2
import PIL.Image, PIL.ImageTk, PIL.ImageDraw

class App:
    def __init__(self, master, window_title, image_path="test.png"):
        self.window = master
        self.window.title(window_title)
        self.popup_switch = 0

        # TO-DO label of entry ---using grid and frame of whole theme
        self.l1 = tkinter.Label(text="Test", fg="red", bg="white")
        self.l1.pack(anchor=tkinter.NW)

        #[ENTRY] Creat a entry where user can decide the cropping size
        self.crop_height = tkinter.StringVar()
        self.crop_width = tkinter.StringVar()
        self.crop_height.set("100") # default size
        self.crop_width.set("100")
        vcmd = (self.window.register(self.validate), '%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W')
        self.entry_height = tkinter.Entry(self.window, validate = 'key', validatecommand = vcmd, textvariable=self.crop_height)
        self.entry_width = tkinter.Entry(self.window, validate = 'key', validatecommand = vcmd, textvariable=self.crop_width)  
        self.entry_height.pack(anchor=tkinter.N)
        self.entry_width.pack(anchor=tkinter.N)
        
        #[BUTTON] Button for determining the crop size        
        self.btn_crop_size = tkinter.Button(self.window, text="OK", width=10, command=self.crop_size)
        self.btn_crop_size.pack(anchor=tkinter.N, expand=True)

        # Load an image using OpenCV
        self.cv_img = cv2.cvtColor(cv2.imread(image_path), cv2.COLOR_BGR2RGB)
        self.height, self.width, no_channels = self.cv_img.shape

        #[CANVAS] Create a canvas that can fit the above image
        self.canvas = tkinter.Canvas(self.window, width = self.width, height = self.height)
        self.canvas.pack()
        self.photo = PIL.ImageTk.PhotoImage(image = PIL.Image.fromarray(self.cv_img))
        self.canvas.create_image(0, 0, image=self.photo, anchor=tkinter.NW)
        
        #[MASK][CALLBACK] Draw a rectangle mask which follows the mouse
        def mask(event):

            if hasattr(self, 'img'):
                self.canvas.delete("all")
            self.img = self.cv_img.copy()
            self.overlay = self.cv_img.copy()
            self.opacity = 0.3
            if hasattr(self,'mask_height'):
                cv2.rectangle(self.overlay,(event.x-int(self.mask_width/2),event.y-int(self.mask_height/2)),
                (event.x+int(self.mask_width/2),event.y+int(self.mask_height/2)),(255,255,0),-1)
            else:
                cv2.rectangle(self.overlay,(event.x-50,event.y-50),(event.x+50,event.y+50),(255,255,0),-1)
            cv2.addWeighted(self.overlay, self.opacity, self.img, 1 - self.opacity, 0, self.img)
            self.photo = PIL.ImageTk.PhotoImage(image = PIL.Image.fromarray(self.img))
            self.canvas.create_image(0, 0, image=self.photo, anchor=tkinter.NW)
            # debug only
            print('{},{}'.format(event.x,event.y))
        self.canvas.bind("<Motion>", func=mask)
        
        #[CLICK][CALLBACK] Capture click position
        def click(event):
            self.currentx = event.x
            self.currenty = event.y
            print ("clicked at", self.currentx, self.currenty)
            new_page(self)
        self.canvas.bind("<Button-1>", func=click)

        #[CLICK][CALLBACK] Create popup
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
        self.mask_width=int(self.crop_width.get())
        
        # debug only
        print("crop_height=" ,self.mask_height)
        print("crop_width=" ,self.mask_width)

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

