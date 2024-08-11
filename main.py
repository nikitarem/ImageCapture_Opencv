import cv2
import os
import sys
import tkinter as tk
from tkinter import Button,Label,Entry,messagebox
from PIL import Image,ImageTk
from datetime import datetime

default_folder_to_save="C:\PhotoBook"

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)


cam = cv2.VideoCapture(0)
captured_frame = None
frame_png = resource_path("frame.png")
icon_image = resource_path("icon.ico")


# Create window
window = tk.Tk()
window.title("Capture image")
window.iconbitmap(icon_image)

video_label=Label(window)
video_label.pack()

directory_label = Label(window, text="Save To :")
directory_entry = Entry(window , width=70)
directory_entry.insert(0, default_folder_to_save) 

def update_frame():
    if captured_frame is None:
        ret, frame = cam.read()
        fliped_frame = cv2.flip(frame, 1)
        if ret:
            # Convert to RGB and resize to fit within a 500x500 frame
            frame_rgb = cv2.cvtColor(fliped_frame, cv2.COLOR_BGR2RGB)
            h, w, _ = frame_rgb.shape
            aspect_ratio = w / h
            
            # Compute new dimensions while maintaining aspect ratio
            new_width = 500
            new_height = int(new_width / aspect_ratio)
            
            if new_height > 500:
                new_height = 500
                new_width = int(new_height * aspect_ratio)
            
            resized_frame = cv2.resize(frame_rgb, (new_width, new_height))
            
            # Create a blank 500x500 image
            blank_frame = Image.new("RGB", (500, 500), (0, 0, 0))
            # Convert resized frame to PIL image
            resized_pil = Image.fromarray(resized_frame)
            # Calculate position to center the resized image in the 500x500 frame
            x = (500 - new_width) // 2
            y = (500 - new_height) // 2
            # Paste the resized image onto the blank frame
            blank_frame.paste(resized_pil, (x, y))

            # Load and resize the frame image
            frame_image = Image.open(frame_png).convert("RGBA")
            frame_image = frame_image.resize((500, 500), Image.LANCZOS)

            # Composite the frame over the live video feed
            combined_image = Image.alpha_composite(blank_frame.convert("RGBA"), frame_image)

            # Convert combined image to display in Tkinter
            imageTk = ImageTk.PhotoImage(image=combined_image)
            video_label.imageTk = imageTk
            video_label.configure(image=imageTk)
            capture_button.pack(side="left", padx=10)
    window.after(10, update_frame)
    
#capturing 500x500 image   
def capture_image():       
    global captured_frame
    ret, frame = cam.read()
    if ret:
        # Flip the frame and convert it to RGB
        fliped_frame = cv2.flip(frame, 1)
        cv2image = cv2.cvtColor(fliped_frame, cv2.COLOR_BGR2RGB)

        # Get dimensions of the captured frame
        h, w, _ = cv2image.shape
        crop_size = 500
        start_x = max(0, (w - crop_size) // 2)

        # # If the height is less than 500, pad the top and bottom with black pixels
        if h < crop_size:
            padding = (crop_size - h) // 2
            cv2image = cv2.copyMakeBorder(cv2image, padding, padding, 0, 0, cv2.BORDER_CONSTANT, value=[0, 0, 0])
            h = crop_size

        start_y = max(0, (h - crop_size) // 2)
        # Crop the image
        cropped_frame = cv2image[start_y:start_y + crop_size, start_x:start_x + crop_size]

        # Convert the cropped image to PIL format
        img = Image.fromarray(cropped_frame).convert("RGBA")
        captured_frame = cropped_frame

        # Open and resize the frame image
        frame_image = Image.open(frame_png).convert("RGBA")
        frame_image = frame_image.resize((crop_size, crop_size), Image.LANCZOS)
        
        # Ensure both images are the same size
        if img.size == frame_image.size:
            combined_image = Image.alpha_composite(img, frame_image)
            imagetk = ImageTk.PhotoImage(image=combined_image)
            video_label.imagetk = imagetk
            video_label.configure(image=imagetk)

            start_button.pack_forget()
            capture_button.pack_forget()
            submit_button.pack(side='left', padx=10)
            retake_button.pack(side='left', padx=10)
            close_button.pack(side='left', padx=10)
            directory_label.pack(pady=5)
            directory_entry.pack(pady=5)
        else:
            print("Size of cropped image and frame image do not match")
    else:
        print("Failed to capture image")

#make success pop ups 
def show_success_message():
    success_window=tk.Toplevel(window)
    success_window.title("Success message :")
    success_window.geometry("200x100")
    
    label=tk.Label(success_window,text="Saved Successfully !",pady=20)
    label.pack()
    
    window.after(3000,success_window.destroy)
#save image to the folder             
def submit_image():
    global captured_frame
    if captured_frame is not None :
        folder_to_save=directory_entry.get()
        if not os.path.exists(folder_to_save):
            messagebox.showerror("Error",f"Can't find the directory : {folder_to_save}")
            return  
        
        cv2image=cv2.cvtColor(captured_frame,cv2.COLOR_BGR2RGB)
        img=Image.fromarray(cv2image).convert("RGBA")
        frame_image=Image.open(frame_png).convert("RGBA")
        frame_image=frame_image.resize((500,500),Image.LANCZOS)
        
        combined_image=Image.alpha_composite(img,frame_image)
        
        folder_to_save=directory_entry.get()
        timestamp=datetime.now().strftime("%Y%m%d_%H%M%S")
        filename=f"{timestamp}.png"
        filepath=os.path.join(folder_to_save,filename)
        # cv2.imwrite(filepath,captured_frame)
        combined_image.save(filepath)
        print(f"Image saved {filepath}")
        
        captured_frame=None
        submit_button.pack_forget()
        retake_button.pack_forget()
        start_button.pack_forget()
        capture_button.pack(side='left',padx=10)
        close_button.pack(side='left',padx=10)
        
        show_success_message()
          
def retake_image():
    global captured_frame
    captured_frame=None
    submit_button.pack_forget()
    start_button.pack_forget()
    retake_button.pack_forget()
    capture_button.pack(side='left',padx=10)
    
def close():
    cam.release()
    window.destroy()    

#Here add button_frame to adjust buttons to butttom center position
button_frame = tk.Frame(window)
button_frame.pack(side='bottom', pady=10)

start_button = Button(button_frame, text="Start Camera", command=update_frame,relief="raised",bg="#78f88e")
start_button.pack(side='left', padx=10)

capture_button = Button(button_frame, text="Click to Capture", command=capture_image,relief="raised",bg="#fdf53b")

submit_button = Button(button_frame, text="Save", command=submit_image,relief="raised",bg="#67ecfd")

retake_button = Button(button_frame, text="Retake", command=retake_image,relief="raised",bg="#78f88e")

close_button = Button(button_frame, text="Close Window", command=close,relief="raised",bg="#fa0116")
close_button.pack(side='left', padx=10)



window.minsize(600,600)
window.mainloop()

cam.release()
cv2.destroyAllWindows()

    
   
        