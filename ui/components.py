"""UI 컴포넌트"""
import tkinter as tk


class ModernButton(tk.Canvas):
    """모던한 스타일의 커스텀 버튼"""
    
    def __init__(self, parent, text, command, bg_color, hover_color, fg_color='white', 
                 width=200, height=45, **kwargs):
        super().__init__(parent, width=width, height=height, bg=parent['bg'], 
                        highlightthickness=0, **kwargs)
        
        self.command = command
        self.bg_color = bg_color
        self.hover_color = hover_color
        self.fg_color = fg_color
        self.text = text
        self.width = width
        self.height = height
        
        self.draw_button(self.bg_color)
        
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)
        self.bind("<Button-1>", self.on_click)
    
    def draw_button(self, color):
        """버튼 그리기"""
        self.delete("all")
        # 둥근 사각형 그리기
        self.create_rounded_rect(2, 2, self.width-2, self.height-2, 
                                radius=15, fill=color, outline="")
        # 텍스트
        self.create_text(self.width//2, self.height//2, text=self.text, 
                        fill=self.fg_color, font=('Segoe UI', 11, 'bold'))
    
    def create_rounded_rect(self, x1, y1, x2, y2, radius=25, **kwargs):
        """둥근 사각형 생성"""
        points = [x1+radius, y1,
                 x2-radius, y1,
                 x2, y1,
                 x2, y1+radius,
                 x2, y2-radius,
                 x2, y2,
                 x2-radius, y2,
                 x1+radius, y2,
                 x1, y2,
                 x1, y2-radius,
                 x1, y1+radius,
                 x1, y1]
        return self.create_polygon(points, smooth=True, **kwargs)
    
    def on_enter(self, event):
        """마우스 진입 이벤트"""
        self.draw_button(self.hover_color)
    
    def on_leave(self, event):
        """마우스 이탈 이벤트"""
        self.draw_button(self.bg_color)
    
    def on_click(self, event):
        """클릭 이벤트"""
        if self.command:
            self.command()

