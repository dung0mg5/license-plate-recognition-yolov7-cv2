import tkinter as tk

# tạo cửa sổ Tkinter
root = tk.Tk()

# tạo frame với đường viền và màu tùy chọn
frame = tk.Frame(root, borderwidth=2, highlightbackground="blue")

# thêm các widget vào frame
label = tk.Label(frame, text="This is a frame with a border")
button = tk.Button(frame, text="Click me!")
label.pack(pady=10)
button.pack(pady=10)

# pack frame vào cửa sổ
frame.pack(padx=10, pady=10)

root.mainloop()
