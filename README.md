# Dự Án Nhận Diện Biển Báo Giao Thông (Traffic Sign Recognition)

Dự án hoàn chỉnh gồm huấn luyện mô hình CNN (TensorFlow/Keras) và giao diện GUI (Tkinter).

## Cấu trúc thư mục
```text
Traffic_Sign_Recognition/
│
├── dataset/                  # Thư mục chứa dữ liệu ảnh (0, 1, ..., 42)
├── create_sample_data.py     # Script tạo dữ liệu mẫu để chạy test nhanh
├── train.py                  # Script huấn luyện mô hình CNN & xuất file traffic_sign_model.h5
├── app_gui.py                # Giao diện ứng dụng nhận diện bằng Tkinter
├── requirements.txt          # Thư viện cần cài đặt
└── README.md                 # Hướng dẫn sử dụng
```

## Hướng dẫn các bước chạy thử

### Bước 1: Cài đặt thư viện
```bash
pip install -r requirements.txt
```

### Bước 2: Chuẩn bị dữ liệu
- **Cách 1 (Chạy thử nhanh):** Chạy lệnh sau để tạo bộ dữ liệu mẫu giả lập:
  ```bash
  python create_sample_data.py
  ```
- **Cách 2 (Huấn luyện thực tế):** Tải bộ dữ liệu **GTSRB (German Traffic Sign Recognition Benchmark)** trên Kaggle, sau đó giải nén vào thư mục `dataset/` (sao cho có các thư mục con từ `0` đến `29`).

### Bước 3: Huấn luyện mô hình
Chạy lệnh huấn luyện để tạo ra file `traffic_sign_model.h5`:
```bash
python train.py
```

### Bước 4: Chạy giao diện người dùng (GUI)
Chạy ứng dụng GUI để chọn ảnh và nhận diện:
```bash
python app_gui.py
```
