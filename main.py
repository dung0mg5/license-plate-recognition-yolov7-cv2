import os
import cv2
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

isVideo = False

# load model
# model = torch.hub.load(
#     'WongKinYiu/yolov7', 'custom', 'best.pt')

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
window = tk.Tk()
window.resizable(False, False)
window.title("Nhận diện biển số xe")
window.geometry("1250x700+150+50")

# đường dẫn file ảnh
path_img = "input/test5.jpg"

header = tk.Frame(window, padx=4, pady=4)
tk.Label(header, text="Nhận diện biển số xe", font='tahoma 20 bold')





# frame chứa ảnh gốc
left_frame = tk.LabelFrame(window, text="Ảnh gốc", font='tahoma 12 italic',
                           bg='#fff', fg='#000', width=720, padx=10).pack(side='left', fill="y")


img = Image.open(path_img)
img_resize = img.resize((670, 600))
img_original = ImageTk.PhotoImage(img_resize)
label_original_image = tk.Label(left_frame, image=img_original, anchor="e")
label_original_image.place(x=2, y=80)


# frame bên phải, chứa ảnh kết quả và các button chức năng
right_frame = tk.LabelFrame(window, text="Chức năng", font='tahoma 12 italic',
                            bg='#fff', fg='#000', width=520).pack(side='right', fill="y")
# đọc ảnh bằng cv2
img_rs = cv2.imread(path_img)
img_rs = cv2.cvtColor(img_rs, cv2.COLOR_BGR2GRAY)
img_rs = cv2.resize(img_rs, (300, 100))

label_image_result = tk.Label(window,  width=490, height=200)
label_image_result.place(x=745, y=85)


# listbox biển số xe
list_box = tk.Listbox(right_frame, font='tahoma 14', fg='blue',
                      width=47, height=8, highlightthickness=2, activestyle='dotbox')
list_box.place(x=745, y=310)

# frame chứa các button xử lý
frame_button = tk.LabelFrame(
    right_frame, text="", bg="#fff", fg="#000", font="tahoma 14", borderwidth=2,
    padx=8, pady=8)
frame_button.place(x=745, y=600)

list_plate_crop = []
list_plate_crop_binary = []


def handle():
    global label_image_result, list_box, path_img, model, img_result, list_plate_crop, list_plate_crop_binary
    if isVideo == False:
        img_hadle = cv2.imread(path_img)
        detections = model(img_hadle)
        # print results
        results = detections.pandas().xyxy[0].to_dict(orient="records")
        img_rs1 = img_hadle.copy()
        # clear the text of the Listbox
        list_box.delete('0', 'end')
        list_plate_crop.clear()
        list_plate_crop_binary.clear()
        color = (0, 255, 0)
        # filter
        for i, result in enumerate(results):
            clas = result['class']
            if clas == 0:
                x1 = int(result['xmin'])
                y1 = int(result['ymin'])
                x2 = int(result['xmax'])
                y2 = int(result['ymax'])
                # cắt ảnh biển số xe để có thể lưu kết quả hoặc hiện lên màn hình
                img_crop = img_hadle[y1:y2, x1:x2]
                list_plate_crop.append(img_crop)
                ##################################################################################
                img_gray_scale, img_thresh_sence = preprocess(img_crop)
                #######################################################################################
                list_plate_crop_binary.append(255-img_thresh_sence)
                # cv2.imshow(f'image_adjusted{x1}', img_thresh_sence)
                text = pytesseract.image_to_string(255 -
                                                   img_thresh_sence, config='--psm 6')
                text_rs = get_valid_chars(text)
                if (len(text_rs) > 6):
                    list_box.insert('end', text_rs)
                else:
                    list_box.insert('end', f'Không nhận diện được({text_rs})')

                c1, c2 = (int(x1), int(y1)), (int(x2), int(y2))
                cv2.rectangle(img_rs1, c1, c2, color, 4, lineType=cv2.LINE_AA)

        list_plate_crop.append(img_rs1)
        img_rs1 = cv2.resize(img_rs1, (490, 200))
        img_result = Image.fromarray(img_rs1)
        img_result = ImageTk.PhotoImage(img_result)
        label_image_result.config(image=img_result)
    else:
        print("Commimg soon")


# button xử lý để nhận được biển số xe
btn_hanle = tk.Button(frame_button, text="Nhận dạng",
                      width=10, padx=4, pady=4, command=handle)
btn_hanle.grid(row=0, column=0, padx=8, pady=8)

# button để lưu kết quả vào folder


def save_result():
    global list_plate_crop, list_plate_crop_binary
    if (len(list_plate_crop) == 0):
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


btn_save_result = tk.Button(
    frame_button, text="Lưu kết quả", width=10, padx=4, pady=4, command=save_result)
btn_save_result.grid(row=0, column=1, padx=8, pady=8)
# function choose file image


def select_file():
    file_type = [('Image files', '.png .jpg .jpeg .gif')]
    file_name = filedialog.askopenfilename(initialdir=dir,
                                           title='Choose image file',
                                           filetypes=file_type)
    if (file_name != ""):
        # change image in left and right frame
        global path_img, label_original_image, label_image_result, img_result, img_original, list_box, list_plate_crop, isVideo, list_plate_crop_binary
        path_img = file_name

        # change image original
        img = Image.open(path_img)
        img_resize = img.resize((670, 600))
        img_original = ImageTk.PhotoImage(img_resize)
        label_original_image.config(image=img_original)

        list_box.delete('0', 'end')
        list_plate_crop.clear()
        list_plate_crop_binary.clear()
        label_image_result.config(image="")
        isVideo = False


# button chọn ảnh
btn_choose_image = tk.Button(
    frame_button, text="Chọn ảnh", width=10, padx=4, pady=4, command=select_file)
btn_choose_image.grid(row=0, column=2, padx=8, pady=8)

# button chọn video


def select_video():
    file_type = [('Video files', '.mp4')]
    file_name = filedialog.askopenfilename(initialdir=dir,
                                           title='Choose image file',
                                           filetypes=file_type)
    if (file_name != ""):
        global list_box, list_plate_crop, isVideo, list_plate_crop_binary, label_original_image, label_image_result
        isVideo = True


# button_thongke = tk.Button(
#     frame_button, text="Chọn video", width=10, padx=4, pady=4)
# button_thongke.grid(row=0, column=3, padx=8, pady=8)

# button show ket qua


def show_detail_result():
    global list_plate_crop, list_plate_crop_binary
    if (len(list_plate_crop) == 0):
        return
    for i, img1 in enumerate(list_plate_crop):
        if (i == len(list_plate_crop)-1):
            cv2.imshow("result", cv2.resize(img1, (500, 400)))
        else:
            cv2.imshow(f"crop{i}", img1)

    for j, img2 in enumerate(list_plate_crop_binary):
        cv2.imshow(f"crop_binary{j}", img2)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


button_thongke = tk.Button(
    frame_button, text="Hiển thị chi tiết ảnh", width=14, padx=4, pady=4, command=show_detail_result)
button_thongke.grid(row=0, column=3, padx=8, pady=8)


# code by person
# member = 'Group 2\n20110470 Phạm Văn Hào - 20110452 Phan Xuân Dũng - 20110119 Nguyễn Quốc Toản'
# tk.Label(right_frame, text=member, font='tahoma 10', anchor='e',
#          fg='#000', bg='#fff').place(x=740, y=650)


window.mainloop()
