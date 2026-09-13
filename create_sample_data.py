import os
import cv2
import numpy as np

def generate_sample_dataset(base_dir="dataset", num_classes=30, samples_per_class=15):
    """
    Tạo dữ liệu mẫu giả định (synthetic dataset) với 30 lớp biển báo Việt Nam
    để test quy trình huấn luyện train.py và giao diện app_gui.py.
    """
    print("Đang tạo bộ dữ liệu mẫu cho 30 lớp biển báo Việt Nam...")
    os.makedirs(base_dir, exist_ok=True)
    
    for c in range(num_classes):
        class_dir = os.path.join(base_dir, str(c))
        os.makedirs(class_dir, exist_ok=True)
        
        for i in range(samples_per_class):
            img = np.zeros((30, 30, 3), dtype=np.uint8)
            # Tạo màu sắc ngẫu nhiên theo ID lớp
            color = (int((c * 37) % 255), int((c * 59) % 255), int((c * 83) % 255))
            cv2.circle(img, (15, 15), 12, color, -1)
            cv2.putText(img, str(c), (5, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
            
            img_path = os.path.join(class_dir, f"sample_{i}.png")
            
            # Ghi file ảnh an toàn (hỗ trợ đường dẫn có tiếng Việt)
            is_success, buffer = cv2.imencode(".png", img)
            if is_success:
                with open(img_path, "wb") as f:
                    f.write(buffer)
            
    print(f"-> Đã tạo xong dữ liệu mẫu cho {num_classes} lớp (từ 0 đến {num_classes - 1}) tại thư mục '{base_dir}/'!")

if __name__ == "__main__":
    generate_sample_dataset()