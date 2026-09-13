import os
import cv2
import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPool2D, Dense, Flatten, Dropout
from tensorflow.keras.utils import to_categorical

# ---------------- CONFIGURATION ----------------
IMG_HEIGHT = 30
IMG_WIDTH = 30
CHANNELS = 3
NUM_CLASSES = 30  # Đồng bộ với 30 loại biển báo Việt Nam trong app_gui.py
EPOCHS = 15
BATCH_SIZE = 32
DATA_DIR = "./dataset"
MODEL_SAVE_PATH = "traffic_sign_model.h5"

def load_data(data_dir):
    images = []
    labels = []
    print("Đang đọc dữ liệu từ thư mục:", data_dir)
    
    if not os.path.exists(data_dir):
        print(f"[LỖI] Thư mục '{data_dir}' không tồn tại!")
        return np.array(images), np.array(labels)

    for category in range(NUM_CLASSES):
        path = os.path.join(data_dir, str(category))
        if not os.path.exists(path):
            continue
            
        for img_name in os.listdir(path):
            img_path = os.path.join(path, img_name)
            try:
                # Đọc ảnh an toàn với đường dẫn/tên file Tiếng Việt
                img_bytes = np.fromfile(img_path, dtype=np.uint8)
                image = cv2.imdecode(img_bytes, cv2.IMREAD_COLOR)
                
                if image is None:
                    continue
                    
                image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                image = cv2.resize(image, (IMG_WIDTH, IMG_HEIGHT))
                images.append(image)
                labels.append(category)
            except Exception as e:
                print(f"Lỗi khi đọc {img_path}: {e}")
                
    images = np.array(images)
    labels = np.array(labels)
    print(f"-> Tổng số ảnh tải được: {len(images)}")
    return images, labels

def build_model(input_shape, num_classes):
    model = Sequential([
        Conv2D(filters=32, kernel_size=(5, 5), activation='relu', input_shape=input_shape),
        Conv2D(filters=32, kernel_size=(5, 5), activation='relu'),
        MaxPool2D(pool_size=(2, 2)),
        Dropout(rate=0.25),

        Conv2D(filters=64, kernel_size=(3, 3), activation='relu'),
        Conv2D(filters=64, kernel_size=(3, 3), activation='relu'),
        MaxPool2D(pool_size=(2, 2)),
        Dropout(rate=0.25),

        Flatten(),
        Dense(256, activation='relu'),
        Dropout(rate=0.5),
        Dense(num_classes, activation='softmax')
    ])

    model.compile(
        loss='categorical_crossentropy',
        optimizer='adam',
        metrics=['accuracy']
    )
    return model

def plot_history(history):
    plt.figure(figsize=(12, 4))
    
    # Đồ thị Accuracy
    plt.subplot(1, 2, 1)
    plt.plot(history.history['accuracy'], label='Train Accuracy')
    plt.plot(history.history['val_accuracy'], label='Val Accuracy')
    plt.title('Độ chính xác (Accuracy)')
    plt.xlabel('Epoch')
    plt.ylabel('Accuracy')
    plt.legend()

    # Đồ thị Loss
    plt.subplot(1, 2, 2)
    plt.plot(history.history['loss'], label='Train Loss')
    plt.plot(history.history['val_loss'], label='Val Loss')
    plt.title('Hàm mất mát (Loss)')
    plt.xlabel('Epoch')
    plt.ylabel('Loss')
    plt.legend()

    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    X, y = load_data(DATA_DIR)

    if len(X) == 0:
        print("[LỖI] Không tìm thấy dữ liệu ảnh! Vui lòng chuẩn bị các thư mục ảnh từ 0 đến 29 trong thư mục 'dataset'.")
    else:
        # Chuẩn hóa dữ liệu pixel về [0, 1]
        X = X / 255.0

        # Chia tập Train / Validation (80/20)
        unique_classes = len(np.unique(y))
        X_train, X_val, y_train, y_val = train_test_split(
            X, y, 
            test_size=0.2, 
            random_state=42, 
            stratify=y if unique_classes == NUM_CLASSES else None
        )

        y_train = to_categorical(y_train, NUM_CLASSES)
        y_val = to_categorical(y_val, NUM_CLASSES)

        input_shape = (IMG_HEIGHT, IMG_WIDTH, CHANNELS)
        model = build_model(input_shape, NUM_CLASSES)
        model.summary()

        print("\nBắt đầu huấn luyện mô hình...")
        history = model.fit(
            X_train, y_train,
            batch_size=BATCH_SIZE,
            epochs=EPOCHS,
            validation_data=(X_val, y_val)
        )

        model.save(MODEL_SAVE_PATH)
        print(f"\n[THÀNH CÔNG] Đã lưu file mô hình tại: {MODEL_SAVE_PATH}")
        
        # Vẽ biểu đồ kết quả Huấn luyện
        plot_history(history)