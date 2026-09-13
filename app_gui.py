from datetime import datetime
import os
import sqlite3
import cv2
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import load_model
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk

# Cấu hình Cơ sở dữ liệu SQLite cho lịch sử
DB_NAME = "traffic_sign_history.db"


def init_db():
  conn = sqlite3.connect(DB_NAME)
  cursor = conn.cursor()
  cursor.execute("""
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            time_str TEXT,
            image_name TEXT,
            result TEXT,
            confidence TEXT
        )
    """)
  conn.commit()
  conn.close()


# Danh mục Biển báo giao thông Việt Nam (QCVN 41:2019/BGTVT)
CLASSES = {
    0: "P.101 - Cấm đi",
    1: "P.102 - Cấm xe đi lại",
    2: "P.103a - Cấm ô tô",
    3: "P.104 - Cấm xe máy / mô tô",
    4: "P.106a - Cấm xe tải",
    5: "P.107 - Cấm xe khách và xe tải",
    6: "P.112 - Cấm người đi bộ",
    7: "P.123a - Cấm rẽ trái",
    8: "P.123b - Cấm rẽ phải",
    9: "P.124a - Cấm quay đầu xe",
    10: "P.127 - Tốc độ (50 km/h)",
    11: "P.127 - Tốc độ (60 km/h)",
    12: "P.127 - Tốc độ (80 km/h)",
    13: "P.130 - Cấm dừng và đỗ xe",
    14: "P.131a - Cấm đỗ xe",
    15: "W.201a - Ngoặt vòng bên trái",
    16: "W.201b - Ngoặt vòng bên phải",
    17: "W.207a - Giao đường không ưu tiên",
    18: "W.208 - Giao đường ưu tiên",
    19: "W.209 - Giao nhau có tín hiệu đèn",
    20: "W.224 - Đường người đi bộ cắt ngang",
    21: "W.225 - Trẻ em sang đường",
    22: "W.227 - Công trường đang thi công",
    23: "R.301a - Hướng đi phải theo (Thẳng)",
    24: "R.301c - Hướng đi phải theo (Trái)",
    25: "R.301d - Hướng đi phải theo (Phải)",
    26: "R.303 - Giao nhau chạy theo vòng xuyến",
    27: "R.407a - Đường một chiều",
    28: "I.408 - Nơi đỗ xe",
    29: "I.423a - Vị trí người đi bộ sang đường",
}


class LoginWindow:

  def __init__(self, root, on_success):
    self.login_win = tk.Toplevel(root)
    self.login_win.title("Đăng Nhập Hệ Thống")

    # Phóng to toàn màn hình cho phần đăng nhập
    self.login_win.state("zoomed")

    self.login_win.configure(bg="#2b3e50")
    self.login_win.grab_set()
    self.on_success = on_success

    root.withdraw()

    # Chia lưới 2 cột co giãn đều 50% - 50%
    self.login_win.rowconfigure(0, weight=1)
    self.login_win.columnconfigure(0, weight=1)
    self.login_win.columnconfigure(1, weight=1)

    # --- PHẦN BÊN TRÁI: HÌNH ẢNH MINH HỌA ---
    left_frame = tk.Frame(self.login_win, bg="#1abc9c")
    left_frame.grid(row=0, column=0, sticky="nsew")

    self.bg_image_raw = None
    try:
      self.bg_image_raw = Image.open("banner.png")
    except:
      pass

    self.lbl_img = tk.Label(left_frame, bg="#1abc9c")
    self.lbl_img.place(x=0, y=0, relwidth=1, relheight=1)

    if self.bg_image_raw:
      left_frame.bind("<Configure>", self.resize_banner)
    else:
      tk.Label(
          left_frame,
          text="HỆ THỐNG\nNHẬN DIỆN\nBIỂN BÁO",
          fg="white",
          bg="#1abc9c",
          font=("Helvetica", 32, "bold"),
          justify="center",
      ).place(relx=0.5, rely=0.5, anchor="center")

    # --- PHẦN BÊN PHẢI: FORM ĐĂNG NHẬP ---
    right_frame = tk.Frame(self.login_win, bg="#2b3e50")
    right_frame.grid(row=0, column=1, sticky="nsew")

    center_form = tk.Frame(right_frame, bg="#2b3e50")
    center_form.place(relx=0.5, rely=0.5, anchor="center")

    tk.Label(
        center_form,
        text="ĐĂNG NHẬP",
        font=("Helvetica", 28, "bold"),
        fg="white",
        bg="#2b3e50",
    ).pack(pady=(0, 30))

    # Input Tài khoản
    tk.Label(
        center_form,
        text="Tài khoản",
        font=("Helvetica", 12),
        fg="#aeb6bf",
        bg="#2b3e50",
        anchor="w",
    ).pack(fill="x")
    self.entry_user = tk.Entry(
        center_form,
        font=("Helvetica", 14),
        bd=0,
        width=30,
        bg="#34495e",
        fg="white",
        insertbackground="white",
    )
    self.entry_user.pack(pady=(5, 2), ipady=8)
    tk.Frame(center_form, bg="#1abc9c", height=2, width=350).pack(pady=(0, 20))

    # Input Mật khẩu
    tk.Label(
        center_form,
        text="Mật khẩu",
        font=("Helvetica", 12),
        fg="#aeb6bf",
        bg="#2b3e50",
        anchor="w",
    ).pack(fill="x")
    self.entry_pass = tk.Entry(
        center_form,
        font=("Helvetica", 14),
        bd=0,
        width=30,
        show="*",
        bg="#34495e",
        fg="white",
        insertbackground="white",
    )
    self.entry_pass.pack(pady=(5, 2), ipady=8)
    tk.Frame(center_form, bg="#1abc9c", height=2, width=350).pack(pady=(0, 30))

    # Nút đăng nhập
    tk.Button(
        center_form,
        text="ĐĂNG NHẬP",
        command=self.check_login,
        font=("Helvetica", 13, "bold"),
        bg="#1abc9c",
        fg="white",
        activebackground="#16a085",
        activeforeground="white",
        bd=0,
        cursor="hand2",
    ).pack(fill="x", ipady=12)

  def resize_banner(self, event):
    if self.bg_image_raw:
      width = event.width
      height = event.height
      if width > 10 and height > 10:
        resized_img = self.bg_image_raw.resize(
            (width, height), Image.Resampling.LANCZOS
        )
        self.bg_image = ImageTk.PhotoImage(resized_img)
        self.lbl_img.config(image=self.bg_image)

  def check_login(self):
    username = self.entry_user.get()
    password = self.entry_pass.get()

    if username == "admin" and password == "123456":
      self.login_win.destroy()
      self.on_success()
    else:
      messagebox.showerror(
          "Lỗi", "Sai tài khoản hoặc mật khẩu!", parent=self.login_win
      )


class TrafficSignApp:

  def __init__(self, root):
    self.root = root
    self.root.title("Hệ Thống Nhận Diện Biển Báo Giao Thông Việt Nam")

    # Phóng to toàn màn hình cho cửa sổ chính
    self.root.state("zoomed")
    self.root.configure(bg="#2c3e50")

    self.model_path = "traffic_sign_model.h5"
    self.model = None

    # Khởi tạo Database SQLite
    init_db()

    # Khởi chạy màn hình đăng nhập trước
    LoginWindow(self.root, self.init_main_app)

  def init_main_app(self):
    self.root.deiconify()  # Hiển thị lại cửa sổ chính
    self.load_traffic_model()
    self.create_widgets()
    self.load_history_from_db()  # Nạp lịch sử từ database lên bảng

  def load_traffic_model(self):
    if os.path.exists(self.model_path):
      try:
        self.model = load_model(self.model_path)
        print("Đã tải mô hình thành công.")
      except Exception as e:
        messagebox.showerror("Lỗi", f"Không thể tải model: {e}")
    else:
      messagebox.showwarning(
          "Cảnh báo",
          f"Không tìm thấy file '{self.model_path}'.\nHãy chạy train.py trước"
          " để tạo file model!",
      )

  def create_widgets(self):
    # Tiêu đề chung trên cùng
    title_label = tk.Label(
        self.root,
        text="HỆ THỐNG NHẬN DIỆN BIỂN BÁO GIAO THÔNG VIỆT NAM",
        font=("Helvetica", 20, "bold"),
        fg="#ecf0f1",
        bg="#2c3e50",
        pady=15,
    )
    title_label.pack(side="top", fill="x")

    # Khung chứa chính (chia trái - phải) trải rộng toàn màn hình
    main_frame = tk.Frame(self.root, bg="#2c3e50")
    main_frame.pack(fill="both", expand=True, padx=25, pady=15)

    # --- KHUNG BÊN TRÁI: Khu vực chọn ảnh & kết quả ---
    left_frame = tk.Frame(main_frame, bg="#2c3e50", width=420)
    left_frame.pack(side="left", fill="y", padx=(0, 20))
    left_frame.pack_propagate(False)

    self.image_frame = tk.Frame(
        left_frame, width=360, height=360, bg="#34495e", bd=2, relief="solid"
    )
    self.image_frame.pack_propagate(False)
    self.image_frame.pack(pady=5)

    self.image_label = tk.Label(
        self.image_frame,
        text="Chưa có ảnh nào được chọn",
        fg="#bdc3c7",
        bg="#34495e",
        font=("Helvetica", 11),
    )
    self.image_label.pack(expand=True, fill="both")

    self.btn_select = tk.Button(
        left_frame,
        text="📁 Chọn hình ảnh",
        command=self.upload_image,
        font=("Helvetica", 12, "bold"),
        bg="#3498db",
        fg="white",
        pady=10,
        relief="flat",
        cursor="hand2",
    )
    self.btn_select.pack(pady=15, fill="x")

    self.result_frame = tk.Frame(left_frame, bg="#2c3e50")
    self.result_frame.pack(pady=5, fill="x")

    self.lbl_class = tk.Label(
        self.result_frame,
        text="Kết quả: ---",
        font=("Helvetica", 14, "bold"),
        fg="#2ecc71",
        bg="#2c3e50",
        wraplength=400,
        justify="left",
    )
    self.lbl_class.pack(pady=5, anchor="w")

    self.lbl_confidence = tk.Label(
        self.result_frame,
        text="Độ tin cậy: ---",
        font=("Helvetica", 12),
        fg="#f1c40f",
        bg="#2c3e50",
    )
    self.lbl_confidence.pack(pady=2, anchor="w")

    # --- KHUNG BÊN PHẢI: Lịch sử nhận diện (Mở rộng lấp đầy toàn bộ phần còn lại) ---
    right_frame = tk.Frame(main_frame, bg="#2c3e50")
    right_frame.pack(side="right", fill="both", expand=True)

    lbl_history = tk.Label(
        right_frame,
        text="Lịch Sử Nhận Diện",
        font=("Helvetica", 15, "bold"),
        fg="#ecf0f1",
        bg="#2c3e50",
    )
    lbl_history.pack(anchor="w", pady=(0, 10))

    # Khung chứa bảng và thanh cuộn giúp co giãn tối đa diện tích
    table_container = tk.Frame(right_frame, bg="#2c3e50")
    table_container.pack(fill="both", expand=True)

    columns = ("thoi_gian", "ten_anh", "ket_qua", "do_tin_cay")
    self.tree = ttk.Treeview(table_container, columns=columns, show="headings")

    self.tree.heading("thoi_gian", text="Thời Gian")
    self.tree.heading("ten_anh", text="Tên Ảnh")
    self.tree.heading("ket_qua", text="Kết Quả Nhận Diện")
    self.tree.heading("do_tin_cay", text="Độ Tin Cậy")

    self.tree.column("thoi_gian", width=160, anchor="center")
    self.tree.column("ten_anh", width=200, anchor="w")
    self.tree.column("ket_qua", width=350, anchor="w")
    self.tree.column("do_tin_cay", width=120, anchor="center")

    scrollbar = ttk.Scrollbar(
        table_container, orient="vertical", command=self.tree.yview
    )
    self.tree.configure(yscrollcommand=scrollbar.set)

    self.tree.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

  def load_history_from_db(self):
    for item in self.tree.get_children():
      self.tree.delete(item)

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT time_str, image_name, result, confidence FROM history ORDER BY"
        " id DESC"
    )
    rows = cursor.fetchall()
    conn.close()

    for row in rows:
      self.tree.insert("", "end", values=row)

  def upload_image(self):
    file_path = filedialog.askopenfilename(
        filetypes=[("Image Files", "*.png *.jpg *.jpeg *.bmp")]
    )
    if not file_path:
      return

    uploaded_img = Image.open(file_path)
    uploaded_img_resized = uploaded_img.resize(
        (350, 350), Image.Resampling.LANCZOS
    )
    tk_img = ImageTk.PhotoImage(uploaded_img_resized)

    self.image_label.configure(image=tk_img, text="")
    self.image_label.image = tk_img

    self.classify_image(file_path)

  def classify_image(self, file_path):
    if self.model is None:
      messagebox.showwarning(
          "Thông báo", "Model chưa được tải lên. Vui lòng chạy train.py trước!"
      )
      return

    try:
      img = cv2.imdecode(
          np.fromfile(file_path, dtype=np.uint8), cv2.IMREAD_COLOR
      )

      if img is None:
        messagebox.showerror("Lỗi nhận diện", "Không thể đọc file ảnh!")
        return

      img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
      img_resized = cv2.resize(img, (30, 30))
      img_normalized = np.expand_dims(img_resized / 255.0, axis=0)

      predictions = self.model.predict(img_normalized)
      class_id = np.argmax(predictions)
      confidence = np.max(predictions) * 100

      sign_name = CLASSES.get(class_id, "Không xác định")

      self.lbl_class.config(text=f"Kết quả: {sign_name}")
      self.lbl_confidence.config(text=f"Độ tin cậy: {confidence:.2f}%")

      timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
      filename = os.path.basename(file_path)
      confidence_str = f"{confidence:.2f}%"

      # Lưu vào Cơ sở dữ liệu SQLite
      conn = sqlite3.connect(DB_NAME)
      cursor = conn.cursor()
      cursor.execute(
          """
                INSERT INTO history (time_str, image_name, result, confidence)
                VALUES (?, ?, ?, ?)
            """,
          (timestamp, filename, sign_name, confidence_str),
      )
      conn.commit()
      conn.close()

      # Tải lại lịch sử lên giao diện
      self.load_history_from_db()

    except Exception as e:
      messagebox.showerror(
          "Lỗi nhận diện", f"Đã xảy ra lỗi khi xử lý ảnh: {e}"
      )


if __name__ == "__main__":
  root = tk.Tk()
  app = TrafficSignApp(root)
  root.mainloop()