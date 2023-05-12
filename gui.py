import os
import cv2
from tkinter import *
from matplotlib import pyplot as plt
import tkinter as tk
from tkinter import RAISED, filedialog
from PIL import Image, ImageTk
import numpy as np
from tkinter import messagebox
import time
import pytesseract
import torch
import torch.backends.cudnn as cudnn
import random
from preprocess import preprocess
from processCharacter import *
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

model = torch.hub.load(
    'WongKinYiu/yolov7', 'custom', 'best.pt')


window = tk.Tk()
window.resizable(False, False)

# Get the width and height of the screen
screen_width = window.winfo_screenwidth()
screen_height = window.winfo_screenheight()

# Calculate the x and y coordinates of the window to center it on the screen
x1 = int((screen_width/2) - (1250/2))//2
y1 = int((screen_height/2) - (700/2))//2

window.title("Nhận diện biển số xe")
window.geometry(f"1250x700+{int(x1)}+{int(y1)}")


# Banner nhóm
logo = Image.open('./asset/logo.png')
logo = logo.resize((300, 150))
logo = ImageTk.PhotoImage(logo)
label_logo = tk.Label(window, image=logo)
label_logo.place(x=0, y=0)
# thêm các widget vào frame
tk.Label(window, text="Nhóm 2 - Nhận diện biển số xe oto",
         font='tahoma 20 bold').place(x=301, y=0)

logo_right = Image.open('./asset/fhq.png')
logo_right = logo_right.resize((1250-785, 150))
logo_right = ImageTk.PhotoImage(logo_right)
label_logo_right = tk.Label(window, image=logo_right)
label_logo_right.place(x=785, y=0)

tk.Label(window, text="Thành viên: ", font='tahoma 16 bold').place(x=350, y=35)
tk.Label(window, text="- Phạm Văn Hào - 20110470",
         font='tahoma 14 bold').place(x=400, y=65)
tk.Label(window, text="- Nguyễn Quốc Toản - 20110119",
         font='tahoma 14 bold').place(x=400, y=95)
tk.Label(window, text="- Phan Xuân Dũng - 20110452",
         font='tahoma 14 bold').place(x=400, y=125)

# End Banner nhóm


# GUI MAIN bao gồm ảnh đầu vào và các chức năng

tk.Label(text="Ảnh gốc", font='tahoma 20', fg='blue').place(x=20, y=155)

IMAGE_ORIGINAL_WIDTH = 500
IMAGE_ORIGINAL_HEIGHT = 450

IMAGE_RESULT_WIDTH = 350
IMAGE_RESULT_HEIGHT = 250

image_path = "input/test2.jpg"
image_original = Image.open(image_path)
image_original = image_original.resize(
    (IMAGE_ORIGINAL_WIDTH, IMAGE_ORIGINAL_HEIGHT))
image_original = ImageTk.PhotoImage(image_original)
label_input = tk.Label(window, width=IMAGE_ORIGINAL_WIDTH, height=IMAGE_ORIGINAL_HEIGHT,
                       bg='red', image=image_original)
label_input.place(x=20, y=200)

# variable to store image result
img_result = None
tk.Label(text="Ảnh kết quả", font='tahoma 20', fg='blue').place(x=580, y=155)
label_output = tk.Label(
    window, text='Ảnh kết quả sau khi bấm nút nhận dạng',  bg='red')
label_output.place(x=580, y=200, width=IMAGE_RESULT_WIDTH,
                   height=IMAGE_RESULT_HEIGHT)

tk.Label(text="Danh sách biển số", font='tahoma 20',
         fg='blue').place(x=950, y=155)
list_box = tk.Listbox(window, font='tahoma 16')
list_box.place(x=950, y=200, width=250, height=250)
list_box.insert('end', 'Chưa có kết quả')


scrollbar_listbox = tk.Scrollbar(window)
scrollbar_listbox.place(x=1205, y=200, width=20, height=250)
list_box.config(yscrollcommand=scrollbar_listbox.set)
scrollbar_listbox.config(command=list_box.yview)


frame_button = tk.LabelFrame(window, text='Chức năng')
frame_button.place(x=580, y=450, width=650, height=60)
frame_button.columnconfigure(0, weight=1)
frame_button.columnconfigure(1, weight=1)
frame_button.columnconfigure(2, weight=1)
frame_button.columnconfigure(3, weight=1)
frame_button.columnconfigure(4, weight=1)
frame_button.rowconfigure(0, weight=1)


# variable to store list of plate
list_plate_crop = []
# variable to store list of plate after preprocess
list_plate_crop_binary = []
# Add the images to the canvas
image_objects = []


def choose_image():
    file_type = [('Image files', '.png .jpg .jpeg .gif')]
    file_name = filedialog.askopenfilename(initialdir=dir,
                                           title='Choose image file',
                                           filetypes=file_type)
    if (file_name != ""):
        # change image in left and right frame
        global image_path, label_input, label_output, img_result, img_original, list_box, list_plate_crop, list_plate_crop_binary, canvas, container
        image_path = file_name
        # change image original
        img = Image.open(image_path)
        img_resize = img.resize((IMAGE_ORIGINAL_WIDTH, IMAGE_ORIGINAL_HEIGHT))
        img_original = ImageTk.PhotoImage(img_resize)
        label_input.config(image=img_original)

        list_box.delete('0', 'end')
        list_plate_crop.clear()
        list_plate_crop_binary.clear()
        label_output.config(image="")
        container.destroy()
        container = tk.Frame(canvas, bg="white")
        canvas.create_window((0, 0), window=container, anchor="nw")
        # Reset the scroll region to fit the new container
        canvas.config(scrollregion=canvas.bbox("all"))


btn_open_file = tk.Button(frame_button, text="Chọn ảnh",
                          font='tahoma 16', command=choose_image)
btn_open_file.grid(row=0, column=0, padx=4, pady=4, sticky='we')


def reconize_plate():
    global label_input, list_box, image_path, model, img_result, list_plate_crop, list_plate_crop_binary
    img_hadle = cv2.imread(image_path)
    detections = model(img_hadle)
    # print results
    results = detections.pandas().xyxy[0].to_dict(orient="records")
    img_rs1 = img_hadle.copy()
    # clear the text of the Listbox
    list_box.delete('0', 'end')
    list_plate_crop.clear()
    list_plate_crop_binary.clear()
    color = (0, 255, 0)
    isFind = False
    # filter
    for i, result in enumerate(results):
        clas = result['class']
        if clas == 0:
            isFind = True
            x1 = int(result['xmin'])
            y1 = int(result['ymin'])
            x2 = int(result['xmax'])
            y2 = int(result['ymax'])
            # cắt ảnh biển số xe để có thể lưu kết quả hoặc hiện lên màn hình
            img_crop = img_hadle[y1:y2, x1:x2]
            list_plate_crop.append(cv2.cvtColor(img_crop, cv2.COLOR_RGB2GRAY))

            ##################################################################################
            img_gray_scale, img_thresh_sence = preprocess(img_crop)
            #######################################################################################
            list_plate_crop_binary.append(255-img_thresh_sence)
            # cv2.imshow(f'image_adjusted{x1}', img_thresh_sence)
            text1 = pytesseract.image_to_string(255 -
                                                img_crop, config='--psm 6')
            text2 = pytesseract.image_to_string(255 -
                                                img_thresh_sence, config='--psm 6')

            text1 = get_valid_chars(text1)
            text2 = get_valid_chars(text2)

            if (is_valid_license_plate(text1)):
                list_box.insert('end', text1)
            else:
                if (is_valid_license_plate(text2)):
                    list_box.insert('end', text2)
                else:
                    list_box.insert('end', f'ERR({text1}|{text2})')

            print(text1, text2)
            c1, c2 = (int(x1), int(y1)), (int(x2), int(y2))
            cv2.rectangle(img_rs1, c1, c2, color, 4, lineType=cv2.LINE_AA)

    if isFind == True:
        list_plate_crop.append(img_rs1)
        img_rs1 = cv2.resize(
            img_rs1, (IMAGE_RESULT_WIDTH, IMAGE_RESULT_HEIGHT))
        img_result = Image.fromarray(img_rs1)
        img_result = ImageTk.PhotoImage(img_result)
        label_output.config(image=img_result)
    else:
        list_box.insert('end', "Không tìm thấy biển số xe")


btn_recoginze = tk.Button(frame_button, text="Nhận dạng",
                          font='tahoma 16', command=reconize_plate)
btn_recoginze.grid(row=0, column=1, padx=4, pady=4, sticky='we')


def save_result():
    global list_plate_crop, list_plate_crop_binary
    if (len(list_plate_crop) == 0):
        messagebox.showwarning("Lỗi", "Vui lòng nhận dạng trước khi lưu ảnh")
        return
    existing_dirs = os.listdir("result")
    existing_counts = [int(d[3:])
                       for d in existing_dirs if d.startswith("exp")]
    next_count = max(existing_counts, default=0) + 1
    result_dir = os.path.join("result", f"exp{next_count}")
    os.makedirs(result_dir)
    for i, img1 in enumerate(list_plate_crop):
        if (i == len(list_plate_crop)-1):
            cv2.imwrite(os.path.join(result_dir, "result.jpg"), img1)
        else:
            cv2.imwrite(os.path.join(result_dir, f"crop{i}.jpg"), img1)
    for j, img2 in enumerate(list_plate_crop_binary):
        cv2.imwrite(os.path.join(result_dir, f"crop_binary{j}.jpg"), img2)

    # clear list_plate_crop
    list_plate_crop.clear()
    list_plate_crop_binary.clear()
    # notification
    messagebox.showinfo("Thông báo", "Lưu kết quả thành công")


btn_save = tk.Button(frame_button, text="Lưu kết quả",
                     font='tahoma 16', command=save_result)
btn_save.grid(row=0, column=2, padx=4, pady=4, sticky='we')

canvas = tk.Canvas(window, bg="white", highlightthickness=0)
scrollbar = tk.Scrollbar(window,  orient="horizontal", command=canvas.xview)

canvas.place(x=580, y=530, width=650, height=110)
scrollbar.place(x=580, y=645, width=650, height=20)
canvas.config(xscrollcommand=scrollbar.set)
container = tk.Frame(canvas, bg="white")
canvas.create_window((0, 0), window=container, anchor="nw")


def show_result():
    global list_plate_crop, list_plate_crop_binary, canvas, scrollbar, container
    if (len(list_plate_crop) == 0):
        messagebox.showwarning("Cảnh báo", "Vui lòng nhận dạng trước.")
        return
    for i, image1 in enumerate(list_plate_crop):
        img_pil = Image.fromarray(image1)
        img_pil = img_pil.resize((100, 100), Image.LANCZOS)
        mg_tk = ImageTk.PhotoImage(img_pil)
        label = tk.Label(container, image=mg_tk, bg="red")
        label.image = mg_tk
        label.pack(side="left", fill="y")
    container.update_idletasks()
    canvas.config(scrollregion=canvas.bbox("all"))
    for i, image2 in enumerate(list_plate_crop_binary):
        img_pil = Image.fromarray(image2)
        img_pil = img_pil.resize((110, 110), Image.LANCZOS)
        mg_tk = ImageTk.PhotoImage(img_pil)
        label = tk.Label(container, image=mg_tk, bg="red")
        label.image = mg_tk
        label.pack(side="left", fill="y")
    # Set the canvas scrollable area
    container.update_idletasks()
    canvas.config(scrollregion=canvas.bbox("all"))


btn_show = tk.Button(
    frame_button, text="Hiện kết quả chi tiết", font='tahoma 16', command=show_result)
btn_show.grid(row=0, column=3, columnspan=2, padx=4, pady=4, sticky='we')


window.mainloop()
