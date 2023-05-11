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

window = tk.Tk()
window.resizable(False, False)
window.title("Nhận diện biển số xe")
window.geometry("1250x700+150+50")


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

IMAGE_RESULT_WIDTH = 300
IMAGE_RESULT_HEIGHT = 200

image_path = "input/test2.jpg"
image_original = Image.open(image_path)
image_original = image_original.resize(
    (IMAGE_ORIGINAL_WIDTH, IMAGE_ORIGINAL_HEIGHT))
image_original = ImageTk.PhotoImage(image_original)
label_input = tk.Label(window, width=IMAGE_ORIGINAL_WIDTH, height=IMAGE_ORIGINAL_HEIGHT,
                       bg='red', image=image_original)
label_input.place(x=20, y=200)

tk.Label(text="Ảnh kết quả", font='tahoma 20', fg='blue').place(x=580, y=155)
label_output = tk.Label(
    window, text='Ảnh kết quả sau khi bấm nút nhận dạng',  bg='red')
label_output.place(x=580, y=200, width=300, height=200)

tk.Label(text="Danh sách biển số", font='tahoma 20',
         fg='blue').place(x=950, y=155)
list_box = tk.Listbox(window)
list_box.place(x=950, y=200, width=150, height=200)
list_box.insert('end', 'Chưa có kết quả')

frame_button = tk.LabelFrame(window, text='Chức năng')
frame_button.place(x=580, y=450, width=700, height=100)
frame_button.columnconfigure(0, weight=1)
frame_button.columnconfigure(1, weight=1)
frame_button.columnconfigure(2, weight=1)
frame_button.columnconfigure(3, weight=1)
frame_button.columnconfigure(4, weight=1)

frame_button.rowconfigure(0, weight=1)


btn_open_file = tk.Button(frame_button, text="Chọn ảnh")
btn_open_file.grid(row=0, column=0, padx=4, pady=4)

btn_recoginze = tk.Button(frame_button, text="Nhận dạng")
btn_recoginze.grid(row=0, column=1, padx=4, pady=4)

btn_save = tk.Button(frame_button, text="Lưu kết quả")
btn_save.grid(row=0, column=2, padx=4, pady=4)

btn_show = tk.Button(frame_button, text="Hiện kết quả chi tiết")
btn_show.grid(row=0, column=3, columnspan=2, padx=4, pady=4)


def getorigin(eventorigin):
    global x, y
    x = eventorigin.x
    y = eventorigin.y
    print(x, y)


window.bind("<Button 1>", getorigin)
window.mainloop()
