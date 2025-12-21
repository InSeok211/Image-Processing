"""파일 핸들러"""
import cv2
from tkinter import filedialog, messagebox


def load_image_file():
    """이미지 파일 불러오기"""
    file_path = filedialog.askopenfilename(
        title="이미지 선택",
        filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp *.tif"), 
                  ("All files", "*.*")]
    )
    
    if file_path:
        image = cv2.imread(file_path)
        if image is not None:
            return image, file_path
        else:
            messagebox.showerror("❌ 오류", "이미지를 불러올 수 없습니다.")
            return None, None
    return None, None


def save_image_file(image):
    """이미지 파일 저장"""
    if image is None:
        messagebox.showwarning("⚠️ 경고", "저장할 이미지가 없습니다.")
        return False
    
    file_path = filedialog.asksaveasfilename(
        defaultextension=".jpg",
        filetypes=[("JPEG", "*.jpg"), ("PNG", "*.png"), 
                  ("BMP", "*.bmp"), ("All files", "*.*")]
    )
    
    if file_path:
        cv2.imwrite(file_path, image)
        messagebox.showinfo("✅ 완료", "이미지가 저장되었습니다.")
        return True
    return False


