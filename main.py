"""메인 진입점"""
import tkinter as tk
from ui.gui import ImageProcessingGUI


def main():
    """메인 함수"""
    root = tk.Tk()
    app = ImageProcessingGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()

