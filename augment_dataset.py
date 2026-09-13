import os
import cv2
import numpy as np

DATA_DIR = "./dataset"
NUM_CLASSES = 30  # Khớp với 30 loại biển báo Việt Nam

def augment_image(image):
    augmented = [image] # Giữ lại ảnh gốc

    h, w = image.shape[:2]
    center = (w // 2, h // 2)

    # 1. Xoay ảnh nhẹ (-12, -6, 6, 12 độ)
    for angle in [-12, -6, 6, 12]:
        M = cv2.getRotationMatrix2D(center, angle, 1.0)
        rotated = cv2.warpAffine(image, M, (w, h), borderMode=cv2.BORDER_REPLICATE)
        augmented.append(rotated)

    # 2. Thay đổi độ sáng/tối (mô phỏng nắng/bóng râm)
    for alpha in [0.6, 0.8, 1.2, 1.4]:
        bright = cv2.convertScaleAbs(image, alpha=alpha, beta=0)
        augmented.append(bright)

    # 3. Làm mờ nhẹ (mô phỏng ảnh chụp bị nhoè)
    blurred = cv2.GaussianBlur(image, (3, 3), 0)
    augmented.append(blurred)

    # 4. Thêm nhiễu nhẹ (Noise)
    noise = np.random.normal(0, 10, image.shape).astype(np.uint8)
    noisy_img = cv2.add(image, noise)
    augmented.append(noisy_img)

    return augmented

def process_dataset():
    print("Bắt đầu tự động tạo thêm ảnh biến thể từ 30 ảnh thật...")
    
    for category in range(NUM_CLASSES):
        folder_path = os.path.join(DATA_DIR, str(category))
        if not os.path.exists(folder_path):
            continue

        images = [f for f in os.listdir(folder_path) if not f.startswith("aug_")]
        count = 0
        
        for img_name in images:
            img_path = os.path.join(folder_path, img_name)
            
            # Đọc ảnh an toàn (hỗ trợ đường dẫn tiếng Việt)
            img_bytes = np.fromfile(img_path, dtype=np.uint8)
            img = cv2.imdecode(img_bytes, cv2.IMREAD_COLOR)
            
            if img is None:
                continue

            # Sinh ra các biến thể từ 1 ảnh thật
            aug_images = augment_image(img)
            
            for idx, aug_img in enumerate(aug_images):
                save_path = os.path.join(folder_path, f"aug_{count}_{idx}.png")
                is_success, buffer = cv2.imencode(".png", aug_img)
                if is_success:
                    with open(save_path, "wb") as f:
                        f.write(buffer)
            count += 1

        print(f"-> Hoàn tất thư mục '{category}': Đã sinh thêm ảnh biến thể.")

if __name__ == "__main__":
    process_dataset()