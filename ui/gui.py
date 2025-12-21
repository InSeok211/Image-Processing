"""메인 GUI 클래스"""
import cv2
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk

from .components import ModernButton
from .theme import Theme
import image_processing.filters as filters
import image_processing.transforms as transforms
from utils.file_handler import load_image_file, save_image_file


class ImageProcessingGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("🎨 영상처리 프로그램")
        self.root.geometry("1600x850")
        self.root.configure(bg='#f5f6fa')
        
        # 이미지 저장 변수
        self.original_image = None
        self.current_image = None
        
        # 레이어 시스템
        self.layers = []
        
        # 색상 팔레트
        self.colors = Theme.get_theme('light')
        
        # GUI 구성
        self.create_widgets()
        
    def create_widgets(self):
        header_canvas = tk.Canvas(self.root, height=100, bg=self.colors['primary'], 
                                 highlightthickness=0)
        header_canvas.pack(side=tk.TOP, fill=tk.X)
        
        header_canvas.create_text(70, 50, text="🎨 영상처리", 
                                 fill='white', font=('Segoe UI', 24, 'bold'),
                                 anchor='w')
        header_canvas.create_text(70, 75, text="Image Processing Studio", 
                                 fill='#E0E0E0', font=('Segoe UI', 10),
                                 anchor='w')
        
        button_frame = tk.Frame(self.root, bg=self.colors['light'], height=80)
        button_frame.pack(side=tk.TOP, fill=tk.X, padx=20, pady=15)
        
        btn_open = ModernButton(button_frame, "📂 이미지 열기", self.load_image,
                               self.colors['primary'], self.colors['primary_hover'],
                               width=180, height=50)
        btn_open.pack(side=tk.LEFT, padx=8)
        
        btn_save = ModernButton(button_frame, "💾 이미지 저장", self.save_image,
                               self.colors['success'], self.colors['success_hover'],
                               width=180, height=50)
        btn_save.pack(side=tk.LEFT, padx=8)
        
        btn_reset = ModernButton(button_frame, "↩️ 원본으로", self.reset_image,
                                self.colors['danger'], self.colors['danger_hover'],
                                width=180, height=50)
        btn_reset.pack(side=tk.LEFT, padx=8)
        
        # 메인 컨테이너
        main_container = tk.Frame(self.root, bg=self.colors['light'])
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))
        
        # 왼쪽 패널 - 필터 옵션 (카드 스타일)
        left_panel = tk.Frame(main_container, bg=self.colors['sidebar'], width=320,
                             relief=tk.FLAT, bd=0)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 15))
        left_panel.pack_propagate(False)
        
        # 필터 제목 영역
        title_frame = tk.Frame(left_panel, bg=self.colors['sidebar'])
        title_frame.pack(fill=tk.X, pady=20, padx=20)
        
        tk.Label(title_frame, text="✨ 필터 & 효과", bg=self.colors['sidebar'], 
                fg=self.colors['text_dark'],
                font=('Segoe UI', 16, 'bold')).pack(anchor='w')
        tk.Label(title_frame, text="원하는 효과를 선택하세요", bg=self.colors['sidebar'], 
                fg='#7F8C8D',
                font=('Segoe UI', 9)).pack(anchor='w', pady=(5, 0))
        
        # 구분선
        separator = tk.Frame(left_panel, bg=self.colors['border'], height=1)
        separator.pack(fill=tk.X, padx=20, pady=10)
        
        # 스크롤바 스타일 설정 (더 부드럽고 깔끔하게)
        style = ttk.Style()
        style.theme_use('clam')  # clam 테마가 더 깔끔함
        style.configure("Custom.Vertical.TScrollbar",
                       gripcount=0,
                       background=self.colors['scrollbar_thumb'],
                       troughcolor=self.colors['light'],
                       bordercolor=self.colors['light'],
                       arrowcolor=self.colors['text_dark'],
                       arrowsize=12,
                       width=12)
        style.map("Custom.Vertical.TScrollbar",
                 background=[('active', self.colors['primary']),
                           ('!active', self.colors['scrollbar_thumb'])])
        
        # 필터 버튼들을 담을 스크롤 가능한 프레임
        canvas = tk.Canvas(left_panel, bg=self.colors['sidebar'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(left_panel, orient="vertical", command=canvas.yview, 
                                 style="Custom.Vertical.TScrollbar")
        scrollable_frame = tk.Frame(canvas, bg=self.colors['sidebar'])
        self.scrollable_frame = scrollable_frame  # 인스턴스 변수로 저장
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # 마우스 휠 스크롤 기능 추가
        def on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        # Canvas와 scrollable_frame에 마우스 휠 이벤트 바인딩
        canvas.bind_all("<MouseWheel>", on_mousewheel)
        
        # 마우스가 Canvas 영역에 들어오고 나갈 때 이벤트 처리
        def bind_mousewheel(event):
            canvas.bind_all("<MouseWheel>", on_mousewheel)
        
        def unbind_mousewheel(event):
            canvas.unbind_all("<MouseWheel>")
        
        canvas.bind("<Enter>", bind_mousewheel)
        canvas.bind("<Leave>", unbind_mousewheel)
        
        # 트랙바 섹션들을 저장할 딕셔너리
        self.trackbar_sections = {}
        self.trackbar_buttons = {}
        
        # 카테고리별 필터 메뉴 (사용자 요청 기능 목록)
        # 1. 밝기 (트랙바 버튼)
        brightness_btn_frame = self.create_category_button(scrollable_frame, "☀️ 밝기", lambda: self.toggle_trackbar_section('brightness'))
        self.trackbar_buttons['brightness'] = brightness_btn_frame
        self.trackbar_sections['brightness'] = None
        self.brightness_section_visible = False
        
        # 2. 명암 대비 (트랙바 버튼)
        contrast_btn_frame = self.create_category_button(scrollable_frame, "🎨 명암 대비", lambda: self.toggle_trackbar_section('contrast'))
        self.trackbar_buttons['contrast'] = contrast_btn_frame
        self.trackbar_sections['contrast'] = None
        self.contrast_section_visible = False
        
        # 3. 히스토그램 스트레칭
        self.create_category_button(scrollable_frame, "📈 히스토그램 스트레칭", self.apply_histogram_stretching)
        
        # 4. 히스토그램 평활화
        self.create_category_button(scrollable_frame, "📊 히스토그램 평활화", self.apply_histogram_eq)
        
        # 5. 블러링
        self.create_category_button(scrollable_frame, "💨 블러링", self.apply_gaussian_blur)
        
        # 6. 샤프닝
        self.create_category_button(scrollable_frame, "✨ 샤프닝", self.apply_sharpening)
        
        # 7. 에지검출
        self.create_section_title(scrollable_frame, "🔍 에지검출")
        self.create_category_button(scrollable_frame, "   Canny", self.apply_canny, small=True)
        self.create_category_button(scrollable_frame, "   Sobel", self.apply_sobel, small=True)
        self.create_category_button(scrollable_frame, "   Laplacian", self.apply_laplacian, small=True)
        
        # 8. 필터링
        self.create_section_title(scrollable_frame, "🎨 필터링")
        self.create_category_button(scrollable_frame, "   그레이스케일", self.apply_grayscale, small=True)
        self.create_category_button(scrollable_frame, "   세피아 톤", self.apply_sepia, small=True)
        self.create_category_button(scrollable_frame, "   엠보싱", self.apply_emboss, small=True)
        self.create_category_button(scrollable_frame, "   이진화", self.apply_threshold, small=True)
        
        # 9. 모폴로지
        self.create_section_title(scrollable_frame, "⚙️ 모폴로지")
        self.create_category_button(scrollable_frame, "   침식 (Erode)", self.apply_erode, small=True)
        self.create_category_button(scrollable_frame, "   팽창 (Dilate)", self.apply_dilate, small=True)
        self.create_category_button(scrollable_frame, "   열림 (Opening)", self.apply_opening, small=True)
        self.create_category_button(scrollable_frame, "   닫힘 (Closing)", self.apply_closing, small=True)
        
        # 10. 확대/축소 (트랙바 버튼)
        scale_btn_frame = self.create_category_button(scrollable_frame, "🔍 확대/축소", lambda: self.toggle_trackbar_section('scale'))
        self.trackbar_buttons['scale'] = scale_btn_frame
        self.trackbar_sections['scale'] = None
        self.scale_section_visible = False
        
        # 11. 평행이동 (트랙바 버튼)
        translation_btn_frame = self.create_category_button(scrollable_frame, "↔️ 평행이동", lambda: self.toggle_trackbar_section('translation'))
        self.trackbar_buttons['translation'] = translation_btn_frame
        self.trackbar_sections['translation'] = None
        self.translation_section_visible = False
        
        # 12. 회전 (트랙바 버튼)
        rotation_btn_frame = self.create_category_button(scrollable_frame, "🔄 회전", lambda: self.toggle_trackbar_section('rotation'))
        self.trackbar_buttons['rotation'] = rotation_btn_frame
        self.trackbar_sections['rotation'] = None
        self.rotation_section_visible = False
        
        # 스크롤바를 먼저 배치 (오른쪽, 충분한 간격으로 버튼 안 가리게)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, padx=(0, 15))
        # Canvas를 나중에 배치 (왼쪽, 나머지 공간 차지)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(20, 0))
        
        # 오른쪽 패널 - 이미지 디스플레이와 레이어 패널
        right_panel = tk.Frame(main_container, bg=self.colors['sidebar'])
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # 이미지 컨테이너 (왼쪽)
        image_container = tk.Frame(right_panel, bg=self.colors['sidebar'])
        image_container.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(20, 10), pady=20)
        
        # 이미지 레이블
        self.image_label = tk.Label(image_container, bg='#F5F6FA', 
                                    text="📷\n\n이미지를 불러오세요\n\n'이미지 열기' 버튼을 클릭하세요", 
                                    fg='#95A5A6', font=('Segoe UI', 14),
                                    relief=tk.FLAT, bd=0)
        self.image_label.pack(expand=True, fill=tk.BOTH)
        
        # 레이어 패널 (오른쪽)
        self.create_layer_panel(right_panel)
        
        # 하단 상태바 (모던 스타일)
        status_frame = tk.Frame(self.root, bg=self.colors['dark'], height=40)
        status_frame.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.status_bar = tk.Label(status_frame, text="✅ 준비", 
                                  anchor=tk.W, bg=self.colors['dark'], 
                                  fg=self.colors['text_light'],
                                  font=('Segoe UI', 10), padx=20)
        self.status_bar.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    
    def create_layer_panel(self, parent):
        """레이어 패널 생성"""
        # 레이어 패널 프레임
        layer_panel = tk.Frame(parent, bg=self.colors['sidebar'], width=300)
        layer_panel.pack(side=tk.RIGHT, fill=tk.Y, padx=(10, 20), pady=20)
        layer_panel.pack_propagate(False)
        
        # 레이어 패널 제목
        title_frame = tk.Frame(layer_panel, bg=self.colors['sidebar'])
        title_frame.pack(fill=tk.X, pady=(0, 15))
        
        tk.Label(title_frame, text="📚 레이어", bg=self.colors['sidebar'], 
                fg=self.colors['text_dark'],
                font=('Segoe UI', 16, 'bold')).pack(anchor='w')
        tk.Label(title_frame, text="여러 효과를 조합하세요", bg=self.colors['sidebar'], 
                fg='#7F8C8D',
                font=('Segoe UI', 9)).pack(anchor='w', pady=(5, 0))
        
        # 구분선
        separator = tk.Frame(layer_panel, bg=self.colors['border'], height=1)
        separator.pack(fill=tk.X, pady=10)
        
        # 레이어 리스트를 담을 스크롤 가능한 프레임
        layer_canvas = tk.Canvas(layer_panel, bg=self.colors['sidebar'], highlightthickness=0)
        layer_scrollbar = ttk.Scrollbar(layer_panel, orient="vertical", 
                                       command=layer_canvas.yview,
                                       style="Custom.Vertical.TScrollbar")
        layer_scrollable_frame = tk.Frame(layer_canvas, bg=self.colors['sidebar'])
        self.layer_scrollable_frame = layer_scrollable_frame
        
        layer_scrollable_frame.bind(
            "<Configure>",
            lambda e: layer_canvas.configure(scrollregion=layer_canvas.bbox("all"))
        )
        
        layer_canvas.create_window((0, 0), window=layer_scrollable_frame, anchor="nw")
        layer_canvas.configure(yscrollcommand=layer_scrollbar.set)
        
        # 마우스 휠 스크롤
        def on_layer_wheel(event):
            layer_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        def bind_layer_wheel(event):
            layer_canvas.bind_all("<MouseWheel>", on_layer_wheel)
        
        def unbind_layer_wheel(event):
            layer_canvas.unbind_all("<MouseWheel>")
        
        layer_canvas.bind("<Enter>", bind_layer_wheel)
        layer_canvas.bind("<Leave>", unbind_layer_wheel)
        
        # 레이어 리스트가 비어있을 때 표시할 메시지
        self.layer_empty_label = tk.Label(layer_scrollable_frame, 
                                          text="레이어가 없습니다\n\n필터를 적용하면\n여기에 표시됩니다",
                                          bg=self.colors['sidebar'],
                                          fg='#95A5A6',
                                          font=('Segoe UI', 10),
                                          justify=tk.CENTER)
        self.layer_empty_label.pack(pady=30)
        
        # 스크롤바와 캔버스 배치
        layer_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        layer_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # 레이어 관리 버튼 프레임
        layer_control_frame = tk.Frame(layer_panel, bg=self.colors['sidebar'])
        layer_control_frame.pack(fill=tk.X, pady=(10, 0))
        
        # 모든 레이어 적용 버튼
        apply_all_btn = tk.Button(layer_control_frame, text="✅ 모두 적용",
                                 command=self.apply_all_layers,
                                 bg=self.colors['success'],
                                 fg='white',
                                 font=('Segoe UI', 9, 'bold'),
                                 relief=tk.FLAT, padx=10, pady=8,
                                 cursor='hand2',
                                 activebackground=self.colors['success_hover'])
        apply_all_btn.pack(fill=tk.X, pady=(0, 5))
        
        # 모든 레이어 삭제 버튼
        clear_all_btn = tk.Button(layer_control_frame, text="🗑️ 모두 삭제",
                                 command=self.clear_all_layers,
                                 bg=self.colors['danger'],
                                 fg='white',
                                 font=('Segoe UI', 9, 'bold'),
                                 relief=tk.FLAT, padx=10, pady=8,
                                 cursor='hand2',
                                 activebackground=self.colors['danger_hover'])
        clear_all_btn.pack(fill=tk.X)
    
    def create_section_title(self, parent, text):
        """섹션 제목 생성"""
        title_frame = tk.Frame(parent, bg=self.colors['sidebar'])
        title_frame.pack(fill=tk.X, pady=(15, 5), padx=15)
        
        tk.Label(title_frame, text=text, bg=self.colors['sidebar'],
                fg=self.colors['text_dark'], font=('Segoe UI', 11, 'bold'),
                anchor='w').pack(side=tk.LEFT)
    
    def create_category_button(self, parent, text, command, small=False):
        """카테고리 버튼 생성 (호버 효과 포함)"""
        btn_frame = tk.Frame(parent, bg=self.colors['sidebar'])
        pady_val = 4 if small else 6
        btn_frame.pack(fill=tk.X, pady=pady_val, padx=15)
        
        # Canvas 버튼 생성 (너비를 적절히 조정하여 스크롤바와 겹치지 않게)
        height = 38 if small else 45
        btn = tk.Canvas(btn_frame, width=250, height=height, bg=self.colors['sidebar'],
                       highlightthickness=0)
        btn.pack(anchor='w')
        
        # 초기 버튼 그리기
        def draw_btn(bg_color, text_color=None):
            btn.delete("all")
            # 텍스트 색상 - 항상 다크 색상 사용
            if text_color is None:
                text_color = self.colors['text_dark']
            # 둥근 사각형
            btn.create_rounded_rectangle(2, 2, 248, height-2, radius=10, 
                                        fill=bg_color, outline='')
            # 텍스트
            font_size = 9 if small else 10
            btn.create_text(125, height//2, text=text, fill=text_color, 
                          font=('Segoe UI', font_size, 'bold'))
        
        # Canvas에 둥근 사각형 그리기 메서드 추가
        def create_rounded_rectangle(self, x1, y1, x2, y2, radius=25, **kwargs):
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
        
        btn.create_rounded_rectangle = create_rounded_rectangle.__get__(btn, tk.Canvas)
        
        # 일관성 있는 색상으로 초기 그리기 (연한 파란색 배경)
        draw_btn(self.colors['btn_bg'])
        
        # 호버 효과 (더 진한 파란색으로)
        def on_enter(e):
            draw_btn(self.colors['btn_hover'])
        
        def on_leave(e):
            draw_btn(self.colors['btn_bg'])
        
        def on_click(e):
            command()
        
        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)
        btn.bind("<Button-1>", on_click)
        btn.config(cursor='hand2')
        
        return btn_frame  # 버튼 프레임 반환
    
    def hide_all_trackbars(self):
        """모든 트랙바 섹션 숨기기"""
        for section_type in ['brightness', 'contrast', 'scale', 'translation', 'rotation']:
            trackbar_frame = self.trackbar_sections.get(section_type)
            if trackbar_frame is not None:
                if section_type == 'brightness' and self.brightness_section_visible:
                    trackbar_frame.pack_forget()
                    self.brightness_section_visible = False
                elif section_type == 'contrast' and self.contrast_section_visible:
                    trackbar_frame.pack_forget()
                    self.contrast_section_visible = False
                elif section_type == 'scale' and self.scale_section_visible:
                    trackbar_frame.pack_forget()
                    self.scale_section_visible = False
                elif section_type == 'translation' and self.translation_section_visible:
                    trackbar_frame.pack_forget()
                    self.translation_section_visible = False
                elif section_type == 'rotation' and self.rotation_section_visible:
                    trackbar_frame.pack_forget()
                    self.rotation_section_visible = False
    
    def reset_to_original(self):
        """원본 이미지로 복원 및 모든 트랙바 리셋 (레이어는 유지)"""
        if self.original_image is not None:
            # 레이어 적용
            self.apply_all_layers()
            # 모든 트랙바 리셋
            if hasattr(self, 'brightness_scale'):
                self.brightness_scale.set(0)
            if hasattr(self, 'contrast_scale'):
                self.contrast_scale.set(1.0)
            if hasattr(self, 'scale_scale'):
                self.scale_scale.set(100)
            if hasattr(self, 'translation_x_scale'):
                self.translation_x_scale.set(0)
                self.translation_y_scale.set(0)
            if hasattr(self, 'rotation_scale'):
                self.rotation_scale.set(0)
    
    def toggle_trackbar_section(self, section_type):
        """트랙바 섹션 표시/숨김 토글"""
        # 다른 트랙바들 숨기기
        for other_type in ['brightness', 'contrast', 'scale', 'translation', 'rotation']:
            if other_type != section_type:
                other_frame = self.trackbar_sections.get(other_type)
                if other_frame is not None:
                    if other_type == 'brightness' and self.brightness_section_visible:
                        other_frame.pack_forget()
                        self.brightness_section_visible = False
                    elif other_type == 'contrast' and self.contrast_section_visible:
                        other_frame.pack_forget()
                        self.contrast_section_visible = False
                    elif other_type == 'scale' and self.scale_section_visible:
                        other_frame.pack_forget()
                        self.scale_section_visible = False
                    elif other_type == 'translation' and self.translation_section_visible:
                        other_frame.pack_forget()
                        self.translation_section_visible = False
                    elif other_type == 'rotation' and self.rotation_section_visible:
                        other_frame.pack_forget()
                        self.rotation_section_visible = False
        
        # 원본 이미지로 복원
        self.reset_to_original()
        
        trackbar_frame = self.trackbar_sections[section_type]
        btn_frame = self.trackbar_buttons[section_type]
        
        if trackbar_frame is None:
            # 트랙바 섹션 생성
            if section_type == 'brightness':
                trackbar_frame = self.create_brightness_section(btn_frame)
            elif section_type == 'contrast':
                trackbar_frame = self.create_contrast_section(btn_frame)
            elif section_type == 'scale':
                trackbar_frame = self.create_scale_section(btn_frame)
            elif section_type == 'translation':
                trackbar_frame = self.create_translation_section(btn_frame)
            elif section_type == 'rotation':
                trackbar_frame = self.create_rotation_section(btn_frame)
            
            self.trackbar_sections[section_type] = trackbar_frame
            # 첫 생성 시 표시
            trackbar_frame.pack(fill=tk.X, pady=5, padx=15, after=btn_frame)
            # 표시 상태 변수 설정
            if section_type == 'brightness':
                self.brightness_section_visible = True
            elif section_type == 'contrast':
                self.contrast_section_visible = True
            elif section_type == 'scale':
                self.scale_section_visible = True
            elif section_type == 'translation':
                self.translation_section_visible = True
            elif section_type == 'rotation':
                self.rotation_section_visible = True
        else:
            # 표시/숨김 토글
            if section_type == 'brightness':
                if self.brightness_section_visible:
                    trackbar_frame.pack_forget()
                    self.brightness_section_visible = False
                else:
                    trackbar_frame.pack(fill=tk.X, pady=5, padx=15, after=btn_frame)
                    self.brightness_section_visible = True
            elif section_type == 'contrast':
                if self.contrast_section_visible:
                    trackbar_frame.pack_forget()
                    self.contrast_section_visible = False
                else:
                    trackbar_frame.pack(fill=tk.X, pady=5, padx=15, after=btn_frame)
                    self.contrast_section_visible = True
            elif section_type == 'scale':
                if self.scale_section_visible:
                    trackbar_frame.pack_forget()
                    self.scale_section_visible = False
                else:
                    trackbar_frame.pack(fill=tk.X, pady=5, padx=15, after=btn_frame)
                    self.scale_section_visible = True
            elif section_type == 'translation':
                if self.translation_section_visible:
                    trackbar_frame.pack_forget()
                    self.translation_section_visible = False
                else:
                    trackbar_frame.pack(fill=tk.X, pady=5, padx=15, after=btn_frame)
                    self.translation_section_visible = True
            elif section_type == 'rotation':
                if self.rotation_section_visible:
                    trackbar_frame.pack_forget()
                    self.rotation_section_visible = False
                else:
                    trackbar_frame.pack(fill=tk.X, pady=5, padx=15, after=btn_frame)
                    self.rotation_section_visible = True
    
    def create_brightness_section(self, parent_frame):
        """밝기 변환 섹션 (트랙바 포함)"""
        # 트랙바 컨테이너 (부드러운 배경색)
        trackbar_frame = tk.Frame(self.scrollable_frame, bg=self.colors['btn_bg'], relief=tk.FLAT, bd=1)
        
        # 밝기 값 레이블 (더 큰 폰트와 색상)
        self.brightness_value_label = tk.Label(trackbar_frame, text="0", 
                                               bg=self.colors['btn_bg'],
                                               fg=self.colors['primary'],
                                               font=('Segoe UI', 14, 'bold'))
        self.brightness_value_label.pack(pady=8)
        
        # 트랙바 스타일 설정
        style = ttk.Style()
        style.configure("Brightness.Horizontal.TScale",
                       background=self.colors['primary'],
                       troughcolor='#E0E6ED',
                       borderwidth=0,
                       lightcolor=self.colors['primary'],
                       darkcolor=self.colors['primary'])
        
        # 트랙바 (스케일)
        self.brightness_scale = ttk.Scale(trackbar_frame, from_=-100, to=100,
                                         orient=tk.HORIZONTAL,
                                         style="Brightness.Horizontal.TScale",
                                         command=self.on_brightness_change)
        self.brightness_scale.set(0)
        self.brightness_scale.pack(fill=tk.X, padx=15, pady=8)
        
        # 안내 레이블
        range_frame = tk.Frame(trackbar_frame, bg=self.colors['btn_bg'])
        range_frame.pack(fill=tk.X, padx=15)
        tk.Label(range_frame, text="어둡게", 
                bg=self.colors['btn_bg'], fg=self.colors['text_gray'],
                font=('Segoe UI', 8)).pack(side=tk.LEFT)
        tk.Label(range_frame, text="밝게", 
                bg=self.colors['btn_bg'], fg=self.colors['text_gray'],
                font=('Segoe UI', 8)).pack(side=tk.RIGHT)
        
        # 버튼 프레임
        button_frame = tk.Frame(trackbar_frame, bg=self.colors['btn_bg'])
        button_frame.pack(pady=10)
        
        # 적용 버튼
        apply_btn = tk.Button(button_frame, text="✅ 적용", 
                             command=self.apply_brightness_layer,
                             bg=self.colors['success'], 
                             fg='white',
                             font=('Segoe UI', 9, 'bold'),
                             relief=tk.FLAT, padx=15, pady=5,
                             cursor='hand2',
                             activebackground=self.colors['success_hover'])
        apply_btn.pack(side=tk.LEFT, padx=5)
        
        # 리셋 버튼
        reset_btn = tk.Button(button_frame, text="↻ 리셋", 
                             command=self.reset_brightness,
                             bg=self.colors['btn_hover'], 
                             fg=self.colors['text_dark'],
                             font=('Segoe UI', 9, 'bold'),
                             relief=tk.FLAT, padx=15, pady=5,
                             cursor='hand2',
                             activebackground=self.colors['primary'])
        reset_btn.pack(side=tk.LEFT, padx=5)
        
        return trackbar_frame
    
    def on_brightness_change(self, value):
        """밝기 트랙바 값 변경 시 (미리보기만)"""
        if self.original_image is None:
            return
        
        brightness = int(float(value))
        self.brightness_value_label.config(text=str(brightness))
        
        # 원본 이미지에서 시작하여 레이어 적용 후 밝기 조절 (미리보기)
        base_image = self.original_image.copy()
        for layer in self.layers:
            if layer['enabled']:
                try:
                    if layer['params']:
                        base_image = layer['func'](base_image, **layer['params'])
                    else:
                        base_image = layer['func'](base_image)
                except Exception:
                    pass
        
        # 밝기 조절 적용 (미리보기)
        self.current_image = transforms.adjust_brightness(base_image, brightness)
        self.display_image(self.current_image)
        self.status_bar.config(text=f"☀️ 밝기 미리보기: {brightness:+d}")
    
    def apply_brightness_layer(self):
        """밝기를 레이어로 적용"""
        if self.original_image is None:
            return
        
        brightness = int(self.brightness_scale.get())
        if brightness == 0:
            return  # 0이면 레이어 추가 안 함
        
        # 람다 함수로 밝기 조절 함수 생성
        brightness_func = lambda img, b=brightness: transforms.adjust_brightness(img, b)
        self.add_layer(f"☀️ 밝기 {brightness:+d}", brightness_func)
        self.status_bar.config(text=f"✅ 밝기 레이어 추가됨: {brightness:+d}")
    
    def reset_brightness(self):
        """밝기 트랙바 리셋"""
        self.brightness_scale.set(0)
        if self.original_image is not None:
            self.apply_all_layers()
            self.status_bar.config(text="↻ 밝기 트랙바 리셋됨")
    
    def create_contrast_section(self, parent_frame):
        """명암 대비 섹션 (트랙바 포함)"""
        trackbar_frame = tk.Frame(self.scrollable_frame, bg=self.colors['btn_bg'], relief=tk.FLAT, bd=1)
        
        self.contrast_value_label = tk.Label(trackbar_frame, text="1.0", 
                                             bg=self.colors['btn_bg'],
                                             fg=self.colors['primary'],
                                             font=('Segoe UI', 14, 'bold'))
        self.contrast_value_label.pack(pady=8)
        
        style = ttk.Style()
        style.configure("Contrast.Horizontal.TScale",
                       background=self.colors['primary'],
                       troughcolor='#E0E6ED',
                       borderwidth=0,
                       lightcolor=self.colors['primary'],
                       darkcolor=self.colors['primary'])
        
        self.contrast_scale = ttk.Scale(trackbar_frame, from_=0.0, to=3.0,
                                       orient=tk.HORIZONTAL,
                                       style="Contrast.Horizontal.TScale",
                                       command=self.on_contrast_change)
        self.contrast_scale.set(1.0)
        self.contrast_scale.pack(fill=tk.X, padx=15, pady=8)
        
        range_frame = tk.Frame(trackbar_frame, bg=self.colors['btn_bg'])
        range_frame.pack(fill=tk.X, padx=15)
        tk.Label(range_frame, text="낮음", 
                bg=self.colors['btn_bg'], fg=self.colors['text_gray'],
                font=('Segoe UI', 8)).pack(side=tk.LEFT)
        tk.Label(range_frame, text="높음", 
                bg=self.colors['btn_bg'], fg=self.colors['text_gray'],
                font=('Segoe UI', 8)).pack(side=tk.RIGHT)
        
        # 버튼 프레임
        button_frame = tk.Frame(trackbar_frame, bg=self.colors['btn_bg'])
        button_frame.pack(pady=10)
        
        # 적용 버튼
        apply_btn = tk.Button(button_frame, text="✅ 적용", 
                             command=self.apply_contrast_layer,
                             bg=self.colors['success'], 
                             fg='white',
                             font=('Segoe UI', 9, 'bold'),
                             relief=tk.FLAT, padx=15, pady=5,
                             cursor='hand2',
                             activebackground=self.colors['success_hover'])
        apply_btn.pack(side=tk.LEFT, padx=5)
        
        # 리셋 버튼
        reset_btn = tk.Button(button_frame, text="↻ 리셋", 
                             command=self.reset_contrast,
                             bg=self.colors['btn_hover'], 
                             fg=self.colors['text_dark'],
                             font=('Segoe UI', 9, 'bold'),
                             relief=tk.FLAT, padx=15, pady=5,
                             cursor='hand2',
                             activebackground=self.colors['primary'])
        reset_btn.pack(side=tk.LEFT, padx=5)
        
        return trackbar_frame
    
    def on_contrast_change(self, value):
        """명암 대비 트랙바 값 변경 시 (미리보기만)"""
        if self.original_image is None:
            return
        
        contrast = float(value)
        self.contrast_value_label.config(text=f"{contrast:.2f}")
        
        # 원본 이미지에서 시작하여 레이어 적용 후 대비 조절 (미리보기)
        base_image = self.original_image.copy()
        for layer in self.layers:
            if layer['enabled']:
                try:
                    if layer['params']:
                        base_image = layer['func'](base_image, **layer['params'])
                    else:
                        base_image = layer['func'](base_image)
                except Exception:
                    pass
        
        self.current_image = transforms.adjust_contrast(base_image, contrast)
        self.display_image(self.current_image)
        self.status_bar.config(text=f"🎨 명암 대비 미리보기: {contrast:.2f}")
    
    def apply_contrast_layer(self):
        """명암 대비를 레이어로 적용"""
        if self.original_image is None:
            return
        
        contrast = float(self.contrast_scale.get())
        if contrast == 1.0:
            return  # 1.0이면 레이어 추가 안 함
        
        # 람다 함수로 대비 조절 함수 생성
        contrast_func = lambda img, c=contrast: transforms.adjust_contrast(img, c)
        self.add_layer(f"🎨 명암 대비 {contrast:.2f}", contrast_func)
        self.status_bar.config(text=f"✅ 명암 대비 레이어 추가됨: {contrast:.2f}")
    
    def reset_contrast(self):
        """명암 대비 트랙바 리셋"""
        self.contrast_scale.set(1.0)
        if self.original_image is not None:
            self.apply_all_layers()
            self.status_bar.config(text="↻ 명암 대비 트랙바 리셋됨")
    
    def create_scale_section(self, parent_frame):
        """확대/축소 섹션"""
        trackbar_frame = tk.Frame(self.scrollable_frame, bg=self.colors['btn_bg'], relief=tk.FLAT, bd=1)
        
        self.scale_value_label = tk.Label(trackbar_frame, text="100%", 
                                          bg=self.colors['btn_bg'],
                                          fg=self.colors['primary'],
                                          font=('Segoe UI', 14, 'bold'))
        self.scale_value_label.pack(pady=8)
        
        style = ttk.Style()
        style.configure("Scale.Horizontal.TScale",
                       background=self.colors['primary'],
                       troughcolor='#E0E6ED',
                       borderwidth=0,
                       lightcolor=self.colors['primary'],
                       darkcolor=self.colors['primary'])
        
        self.scale_scale = ttk.Scale(trackbar_frame, from_=50, to=200,
                                    orient=tk.HORIZONTAL,
                                    style="Scale.Horizontal.TScale",
                                    command=self.on_scale_change)
        self.scale_scale.set(100)
        self.scale_scale.pack(fill=tk.X, padx=15, pady=8)
        
        range_frame = tk.Frame(trackbar_frame, bg=self.colors['btn_bg'])
        range_frame.pack(fill=tk.X, padx=15)
        tk.Label(range_frame, text="50%", 
                bg=self.colors['btn_bg'], fg=self.colors['text_gray'],
                font=('Segoe UI', 8)).pack(side=tk.LEFT)
        tk.Label(range_frame, text="200%", 
                bg=self.colors['btn_bg'], fg=self.colors['text_gray'],
                font=('Segoe UI', 8)).pack(side=tk.RIGHT)
        
        # 버튼 프레임
        button_frame = tk.Frame(trackbar_frame, bg=self.colors['btn_bg'])
        button_frame.pack(pady=10)
        
        # 적용 버튼
        apply_btn = tk.Button(button_frame, text="✅ 적용", 
                             command=self.apply_scale_layer,
                             bg=self.colors['success'], 
                             fg='white',
                             font=('Segoe UI', 9, 'bold'),
                             relief=tk.FLAT, padx=15, pady=5,
                             cursor='hand2',
                             activebackground=self.colors['success_hover'])
        apply_btn.pack(side=tk.LEFT, padx=5)
        
        # 리셋 버튼
        reset_btn = tk.Button(button_frame, text="↻ 리셋", 
                             command=self.reset_scale,
                             bg=self.colors['btn_hover'], 
                             fg=self.colors['text_dark'],
                             font=('Segoe UI', 9, 'bold'),
                             relief=tk.FLAT, padx=15, pady=5,
                             cursor='hand2',
                             activebackground=self.colors['primary'])
        reset_btn.pack(side=tk.LEFT, padx=5)
        
        return trackbar_frame
    
    def on_scale_change(self, value):
        """확대/축소 트랙바 값 변경 시 (미리보기만)"""
        if self.original_image is None:
            return
        
        scale_percent = int(float(value))
        self.scale_value_label.config(text=f"{scale_percent}%")
        
        # 원본 이미지에서 시작하여 레이어 적용 후 확대/축소 (미리보기)
        base_image = self.original_image.copy()
        for layer in self.layers:
            if layer['enabled']:
                try:
                    if layer['params']:
                        base_image = layer['func'](base_image, **layer['params'])
                    else:
                        base_image = layer['func'](base_image)
                except Exception:
                    pass
        
        self.current_image = transforms.scale_image(base_image, scale_percent)
        self.display_image(self.current_image)
        self.status_bar.config(text=f"🔍 확대/축소 미리보기: {scale_percent}%")
    
    def apply_scale_layer(self):
        """확대/축소를 레이어로 적용"""
        if self.original_image is None:
            return
        
        scale_percent = int(self.scale_scale.get())
        if scale_percent == 100:
            return  # 100%이면 레이어 추가 안 함
        
        # 람다 함수로 확대/축소 함수 생성
        scale_func = lambda img, s=scale_percent: transforms.scale_image(img, s)
        self.add_layer(f"🔍 확대/축소 {scale_percent}%", scale_func)
        self.status_bar.config(text=f"✅ 확대/축소 레이어 추가됨: {scale_percent}%")
    
    def reset_scale(self):
        """확대/축소 트랙바 리셋"""
        self.scale_scale.set(100)
        if self.original_image is not None:
            self.apply_all_layers()
            self.status_bar.config(text="↻ 확대/축소 트랙바 리셋됨")
    
    def create_translation_section(self, parent_frame):
        """평행이동 섹션"""
        trackbar_frame = tk.Frame(self.scrollable_frame, bg=self.colors['btn_bg'], relief=tk.FLAT, bd=1)
        
        # X축 이동
        x_frame = tk.Frame(trackbar_frame, bg=self.colors['btn_bg'])
        x_frame.pack(fill=tk.X, padx=15, pady=5)
        tk.Label(x_frame, text="X축:", bg=self.colors['btn_bg'], 
                fg=self.colors['text_dark'], font=('Segoe UI', 9)).pack(side=tk.LEFT)
        self.translation_x_label = tk.Label(x_frame, text="0", 
                                            bg=self.colors['btn_bg'],
                                            fg=self.colors['primary'],
                                            font=('Segoe UI', 11, 'bold'))
        self.translation_x_label.pack(side=tk.RIGHT)
        
        self.translation_x_scale = ttk.Scale(trackbar_frame, from_=-200, to=200,
                                            orient=tk.HORIZONTAL,
                                            command=self.on_translation_change)
        self.translation_x_scale.set(0)
        self.translation_x_scale.pack(fill=tk.X, padx=15, pady=5)
        
        # Y축 이동
        y_frame = tk.Frame(trackbar_frame, bg=self.colors['btn_bg'])
        y_frame.pack(fill=tk.X, padx=15, pady=5)
        tk.Label(y_frame, text="Y축:", bg=self.colors['btn_bg'], 
                fg=self.colors['text_dark'], font=('Segoe UI', 9)).pack(side=tk.LEFT)
        self.translation_y_label = tk.Label(y_frame, text="0", 
                                            bg=self.colors['btn_bg'],
                                            fg=self.colors['primary'],
                                            font=('Segoe UI', 11, 'bold'))
        self.translation_y_label.pack(side=tk.RIGHT)
        
        self.translation_y_scale = ttk.Scale(trackbar_frame, from_=-200, to=200,
                                            orient=tk.HORIZONTAL,
                                            command=self.on_translation_change)
        self.translation_y_scale.set(0)
        self.translation_y_scale.pack(fill=tk.X, padx=15, pady=5)
        
        # 버튼 프레임
        button_frame = tk.Frame(trackbar_frame, bg=self.colors['btn_bg'])
        button_frame.pack(pady=10)
        
        # 적용 버튼
        apply_btn = tk.Button(button_frame, text="✅ 적용", 
                             command=self.apply_translation_layer,
                             bg=self.colors['success'], 
                             fg='white',
                             font=('Segoe UI', 9, 'bold'),
                             relief=tk.FLAT, padx=15, pady=5,
                             cursor='hand2',
                             activebackground=self.colors['success_hover'])
        apply_btn.pack(side=tk.LEFT, padx=5)
        
        # 리셋 버튼
        reset_btn = tk.Button(button_frame, text="↻ 리셋", 
                             command=self.reset_translation,
                             bg=self.colors['btn_hover'], 
                             fg=self.colors['text_dark'],
                             font=('Segoe UI', 9, 'bold'),
                             relief=tk.FLAT, padx=15, pady=5,
                             cursor='hand2',
                             activebackground=self.colors['primary'])
        reset_btn.pack(side=tk.LEFT, padx=5)
        
        return trackbar_frame
    
    def on_translation_change(self, value=None):
        """평행이동 트랙바 값 변경 시 (미리보기만)"""
        if self.original_image is None:
            return
        
        tx = int(self.translation_x_scale.get())
        ty = int(self.translation_y_scale.get())
        
        self.translation_x_label.config(text=str(tx))
        self.translation_y_label.config(text=str(ty))
        
        # 원본 이미지에서 시작하여 레이어 적용 후 평행이동 (미리보기)
        base_image = self.original_image.copy()
        for layer in self.layers:
            if layer['enabled']:
                try:
                    if layer['params']:
                        base_image = layer['func'](base_image, **layer['params'])
                    else:
                        base_image = layer['func'](base_image)
                except Exception:
                    pass
        
        self.current_image = transforms.translate_image(base_image, tx, ty)
        self.display_image(self.current_image)
        self.status_bar.config(text=f"↔️ 평행이동 미리보기: X={tx}, Y={ty}")
    
    def apply_translation_layer(self):
        """평행이동을 레이어로 적용"""
        if self.original_image is None:
            return
        
        tx = int(self.translation_x_scale.get())
        ty = int(self.translation_y_scale.get())
        if tx == 0 and ty == 0:
            return  # 0, 0이면 레이어 추가 안 함
        
        # 람다 함수로 평행이동 함수 생성
        translation_func = lambda img, x=tx, y=ty: transforms.translate_image(img, x, y)
        self.add_layer(f"↔️ 평행이동 X={tx} Y={ty}", translation_func)
        self.status_bar.config(text=f"✅ 평행이동 레이어 추가됨: X={tx}, Y={ty}")
    
    def reset_translation(self):
        """평행이동 트랙바 리셋"""
        self.translation_x_scale.set(0)
        self.translation_y_scale.set(0)
        if self.original_image is not None:
            self.apply_all_layers()
            self.status_bar.config(text="↻ 평행이동 트랙바 리셋됨")
    
    def create_rotation_section(self, parent_frame):
        """회전 섹션"""
        trackbar_frame = tk.Frame(self.scrollable_frame, bg=self.colors['btn_bg'], relief=tk.FLAT, bd=1)
        
        self.rotation_value_label = tk.Label(trackbar_frame, text="0°", 
                                             bg=self.colors['btn_bg'],
                                             fg=self.colors['primary'],
                                             font=('Segoe UI', 14, 'bold'))
        self.rotation_value_label.pack(pady=8)
        
        style = ttk.Style()
        style.configure("Rotation.Horizontal.TScale",
                       background=self.colors['primary'],
                       troughcolor='#E0E6ED',
                       borderwidth=0,
                       lightcolor=self.colors['primary'],
                       darkcolor=self.colors['primary'])
        
        self.rotation_scale = ttk.Scale(trackbar_frame, from_=-180, to=180,
                                       orient=tk.HORIZONTAL,
                                       style="Rotation.Horizontal.TScale",
                                       command=self.on_rotation_change)
        self.rotation_scale.set(0)
        self.rotation_scale.pack(fill=tk.X, padx=15, pady=8)
        
        range_frame = tk.Frame(trackbar_frame, bg=self.colors['btn_bg'])
        range_frame.pack(fill=tk.X, padx=15)
        tk.Label(range_frame, text="-180°", 
                bg=self.colors['btn_bg'], fg=self.colors['text_gray'],
                font=('Segoe UI', 8)).pack(side=tk.LEFT)
        tk.Label(range_frame, text="180°", 
                bg=self.colors['btn_bg'], fg=self.colors['text_gray'],
                font=('Segoe UI', 8)).pack(side=tk.RIGHT)
        
        # 버튼 프레임
        button_frame = tk.Frame(trackbar_frame, bg=self.colors['btn_bg'])
        button_frame.pack(pady=10)
        
        # 적용 버튼
        apply_btn = tk.Button(button_frame, text="✅ 적용", 
                             command=self.apply_rotation_layer,
                             bg=self.colors['success'], 
                             fg='white',
                             font=('Segoe UI', 9, 'bold'),
                             relief=tk.FLAT, padx=15, pady=5,
                             cursor='hand2',
                             activebackground=self.colors['success_hover'])
        apply_btn.pack(side=tk.LEFT, padx=5)
        
        # 리셋 버튼
        reset_btn = tk.Button(button_frame, text="↻ 리셋", 
                             command=self.reset_rotation,
                             bg=self.colors['btn_hover'], 
                             fg=self.colors['text_dark'],
                             font=('Segoe UI', 9, 'bold'),
                             relief=tk.FLAT, padx=15, pady=5,
                             cursor='hand2',
                             activebackground=self.colors['primary'])
        reset_btn.pack(side=tk.LEFT, padx=5)
        
        return trackbar_frame
    
    def on_rotation_change(self, value):
        """회전 트랙바 값 변경 시 (미리보기만)"""
        if self.original_image is None:
            return
        
        angle = int(float(value))
        self.rotation_value_label.config(text=f"{angle}°")
        
        # 원본 이미지에서 시작하여 레이어 적용 후 회전 (미리보기)
        base_image = self.original_image.copy()
        for layer in self.layers:
            if layer['enabled']:
                try:
                    if layer['params']:
                        base_image = layer['func'](base_image, **layer['params'])
                    else:
                        base_image = layer['func'](base_image)
                except Exception:
                    pass
        
        self.current_image = transforms.rotate_image(base_image, angle)
        self.display_image(self.current_image)
        self.status_bar.config(text=f"🔄 회전 미리보기: {angle}°")
    
    def apply_rotation_layer(self):
        """회전을 레이어로 적용"""
        if self.original_image is None:
            return
        
        angle = int(self.rotation_scale.get())
        if angle == 0:
            return  # 0도이면 레이어 추가 안 함
        
        # 람다 함수로 회전 함수 생성
        rotation_func = lambda img, a=angle: transforms.rotate_image(img, a)
        self.add_layer(f"🔄 회전 {angle}°", rotation_func)
        self.status_bar.config(text=f"✅ 회전 레이어 추가됨: {angle}°")
    
    def reset_rotation(self):
        """회전 트랙바 리셋"""
        self.rotation_scale.set(0)
        if self.original_image is not None:
            self.apply_all_layers()
            self.status_bar.config(text="↻ 회전 트랙바 리셋됨")
    
    def load_image(self):
        """이미지 파일 불러오기"""
        image, file_path = load_image_file()
        if image is not None:
            self.original_image = image
            self.current_image = self.original_image.copy()
            # 레이어 초기화
            self.layers.clear()
            self.update_layer_display()
            self.display_image(self.current_image)
            # 모든 트랙바 리셋
            if hasattr(self, 'brightness_scale'):
                self.brightness_scale.set(0)
            if hasattr(self, 'contrast_scale'):
                self.contrast_scale.set(1.0)
            if hasattr(self, 'scale_scale'):
                self.scale_scale.set(100)
            if hasattr(self, 'translation_x_scale'):
                self.translation_x_scale.set(0)
                self.translation_y_scale.set(0)
            if hasattr(self, 'rotation_scale'):
                self.rotation_scale.set(0)
            import os
            filename = os.path.basename(file_path)
            self.status_bar.config(text=f"✅ 이미지 로드 완료: {filename}")
    
    def save_image(self):
        """처리된 이미지 저장"""
        if save_image_file(self.current_image):
            self.status_bar.config(text="💾 이미지 저장 완료")
    
    def reset_image(self):
        """원본 이미지로 되돌리기"""
        if self.original_image is not None:
            self.current_image = self.original_image.copy()
            # 레이어 초기화
            self.layers.clear()
            self.update_layer_display()
            self.display_image(self.current_image)
            # 모든 트랙바 리셋
            if hasattr(self, 'brightness_scale'):
                self.brightness_scale.set(0)
            if hasattr(self, 'contrast_scale'):
                self.contrast_scale.set(1.0)
            if hasattr(self, 'scale_scale'):
                self.scale_scale.set(100)
            if hasattr(self, 'translation_x_scale'):
                self.translation_x_scale.set(0)
                self.translation_y_scale.set(0)
            if hasattr(self, 'rotation_scale'):
                self.rotation_scale.set(0)
            self.status_bar.config(text="↩️ 원본 이미지로 복원됨")
        else:
            messagebox.showwarning("⚠️ 경고", "원본 이미지가 없습니다.")
    
    def display_image(self, img):
        """이미지를 GUI에 표시"""
        if img is None:
            return
        
        # OpenCV는 BGR, PIL은 RGB를 사용하므로 변환
        if len(img.shape) == 3:
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        else:
            img_rgb = img
        
        # 화면 크기에 맞게 이미지 리사이즈
        max_width = 1000
        max_height = 650
        
        height, width = img_rgb.shape[:2]
        scale = min(max_width/width, max_height/height, 1.0)
        
        new_width = int(width * scale)
        new_height = int(height * scale)
        
        img_resized = cv2.resize(img_rgb, (new_width, new_height))
        
        # PIL Image로 변환 후 Tkinter에 표시
        img_pil = Image.fromarray(img_resized)
        img_tk = ImageTk.PhotoImage(img_pil)
        
        self.image_label.config(image=img_tk, text="", bg='#F5F6FA')
        self.image_label.image = img_tk
    
    def check_image(self):
        """이미지가 로드되었는지 확인"""
        if self.current_image is None:
            messagebox.showwarning("⚠️ 경고", "먼저 이미지를 불러오세요.")
            return False
        return True
    
    # 필터 적용 함수들
    def apply_grayscale(self):
        """그레이스케일 변환"""
        if not self.check_image():
            return
        self.hide_all_trackbars()
        self.add_layer("⚫ 그레이스케일", filters.apply_grayscale)
    
    def apply_gaussian_blur(self):
        """가우시안 블러"""
        if not self.check_image():
            return
        self.hide_all_trackbars()
        self.add_layer("🌫️ 가우시안 블러", filters.apply_gaussian_blur)
    
    def apply_sharpening(self):
        """샤프닝 효과"""
        if not self.check_image():
            return
        self.hide_all_trackbars()
        self.add_layer("✨ 샤프닝", filters.apply_sharpening)
    
    def apply_canny(self):
        """Canny 엣지 검출"""
        if not self.check_image():
            return
        self.hide_all_trackbars()
        self.add_layer("🔍 Canny", filters.apply_canny)
    
    def apply_sobel(self):
        """Sobel 엣지 검출"""
        if not self.check_image():
            return
        self.hide_all_trackbars()
        self.add_layer("📐 Sobel", filters.apply_sobel)
    
    def apply_laplacian(self):
        """라플라시안 필터"""
        if not self.check_image():
            return
        self.hide_all_trackbars()
        self.add_layer("🔲 Laplacian", filters.apply_laplacian)
    
    def apply_erode(self):
        """침식 효과"""
        if not self.check_image():
            return
        self.hide_all_trackbars()
        self.add_layer("⬇️ 침식", filters.apply_erode)
    
    def apply_dilate(self):
        """팽창 효과"""
        if not self.check_image():
            return
        self.hide_all_trackbars()
        self.add_layer("⬆️ 팽창", filters.apply_dilate)
    
    def apply_threshold(self):
        """이진화"""
        if not self.check_image():
            return
        self.hide_all_trackbars()
        self.add_layer("◼️ 이진화", filters.apply_threshold)
    
    def apply_histogram_stretching(self):
        """히스토그램 스트레칭"""
        if not self.check_image():
            return
        self.hide_all_trackbars()
        self.add_layer("📈 히스토그램 스트레칭", filters.apply_histogram_stretching)
    
    def apply_histogram_eq(self):
        """히스토그램 평활화"""
        if not self.check_image():
            return
        self.hide_all_trackbars()
        self.add_layer("📊 히스토그램 평활화", filters.apply_histogram_eq)
    
    def apply_sepia(self):
        """세피아 톤 효과"""
        if not self.check_image():
            return
        self.hide_all_trackbars()
        self.add_layer("📷 세피아", filters.apply_sepia)
    
    def apply_emboss(self):
        """엠보싱 효과"""
        if not self.check_image():
            return
        self.hide_all_trackbars()
        self.add_layer("🎭 엠보싱", filters.apply_emboss)
    
    def apply_opening(self):
        """모폴로지 열림 (Opening) = 침식 후 팽창"""
        if not self.check_image():
            return
        self.hide_all_trackbars()
        self.add_layer("⚙️ 열림", filters.apply_opening)
    
    def apply_closing(self):
        """모폴로지 닫힘 (Closing) = 팽창 후 침식"""
        if not self.check_image():
            return
        self.hide_all_trackbars()
        self.add_layer("⚙️ 닫힘", filters.apply_closing)
    
    # 레이어 관리 메서드들
    def add_layer(self, name, func, params=None):
        """레이어 추가"""
        if params is None:
            params = {}
        
        layer = {
            'name': name,
            'enabled': True,
            'func': func,
            'params': params
        }
        self.layers.append(layer)
        self.update_layer_display()
        self.apply_all_layers()
    
    def remove_layer(self, index):
        """레이어 삭제"""
        if 0 <= index < len(self.layers):
            self.layers.pop(index)
            self.update_layer_display()
            self.apply_all_layers()
    
    def toggle_layer(self, index):
        """레이어 활성화/비활성화 토글"""
        if 0 <= index < len(self.layers):
            self.layers[index]['enabled'] = not self.layers[index]['enabled']
            self.update_layer_display()
            self.apply_all_layers()
    
    def apply_all_layers(self):
        """모든 활성화된 레이어 적용"""
        if self.original_image is None:
            return
        
        # 원본 이미지에서 시작
        result = self.original_image.copy()
        
        # 활성화된 레이어들을 순서대로 적용
        for layer in self.layers:
            if layer['enabled']:
                try:
                    if layer['params']:
                        result = layer['func'](result, **layer['params'])
                    else:
                        result = layer['func'](result)
                except Exception as e:
                    self.status_bar.config(text=f"⚠️ 레이어 적용 오류: {layer['name']}")
                    return
        
        self.current_image = result
        self.display_image(self.current_image)
        
        enabled_count = sum(1 for layer in self.layers if layer['enabled'])
        self.status_bar.config(text=f"✅ {enabled_count}개 레이어 적용됨")
    
    def clear_all_layers(self):
        """모든 레이어 삭제"""
        self.layers.clear()
        self.update_layer_display()
        if self.original_image is not None:
            self.current_image = self.original_image.copy()
            self.display_image(self.current_image)
            self.status_bar.config(text="🗑️ 모든 레이어 삭제됨")
    
    def update_layer_display(self):
        """레이어 UI 업데이트"""
        # 기존 레이어 위젯들 제거
        for widget in self.layer_scrollable_frame.winfo_children():
            widget.destroy()
        
        if not self.layers:
            # 레이어가 없을 때 메시지 표시
            self.layer_empty_label = tk.Label(self.layer_scrollable_frame, 
                                              text="레이어가 없습니다\n\n필터를 적용하면\n여기에 표시됩니다",
                                              bg=self.colors['sidebar'],
                                              fg='#95A5A6',
                                              font=('Segoe UI', 10),
                                              justify=tk.CENTER)
            self.layer_empty_label.pack(pady=30)
            return
        
        # 각 레이어를 순서대로 표시 (최신 레이어가 아래에)
        for i in range(len(self.layers)):
            layer = self.layers[i]
            self.create_layer_item(i, layer)
    
    def create_layer_item(self, index, layer):
        """레이어 아이템 UI 생성"""
        # 고정 높이를 가진 레이어 프레임
        layer_frame = tk.Frame(self.layer_scrollable_frame, 
                              bg=self.colors['btn_bg'],
                              relief=tk.FLAT,
                              bd=1)
        layer_frame.pack(fill=tk.X, pady=5, padx=5)
        
        # 체크박스 (활성화/비활성화)
        var = tk.BooleanVar(value=layer['enabled'])
        
        # 체크박스 상태 변경 핸들러
        def on_checkbox_change(*args):
            enabled = var.get()
            # 레이어 상태 업데이트
            if 0 <= index < len(self.layers):
                self.layers[index]['enabled'] = enabled
                # 레이블 스타일 업데이트
                name_label.config(
                    fg=self.colors['text_dark'] if enabled else self.colors['text_gray'],
                    font=('Segoe UI', 9, 'bold' if enabled else 'normal')
                )
                # 모든 레이어 다시 적용
                self.apply_all_layers()
        
        # 텍스트가 길면 말줄임표 처리
        def truncate_text(text, max_chars=18):
            """텍스트가 너무 길면 말줄임표로 처리"""
            if len(text) > max_chars:
                return text[:max_chars-3] + '...'
            return text
        
        display_name = truncate_text(layer['name'], 18)
        
        # 체크박스 생성 (command 사용)
        checkbox = tk.Checkbutton(layer_frame,
                                 variable=var,
                                 bg=self.colors['btn_bg'],
                                 activebackground=self.colors['btn_bg'],
                                 command=on_checkbox_change)
        checkbox.pack(side=tk.LEFT, padx=8, pady=10)
        
        # 레이어 이름 (고정 너비로 텍스트 오버플로우 처리)
        name_label = tk.Label(layer_frame,
                             text=display_name,
                             bg=self.colors['btn_bg'],
                             fg=self.colors['text_dark'] if layer['enabled'] else self.colors['text_gray'],
                             font=('Segoe UI', 9, 'bold' if layer['enabled'] else 'normal'),
                             anchor='w',
                             width=18)  # 고정 너비 (문자 단위)
        name_label.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5), pady=10)
        
        # 삭제 버튼
        delete_btn = tk.Button(layer_frame,
                              text="✕",
                              command=lambda idx=index: self.remove_layer(idx),
                              bg=self.colors['danger'],
                              fg='white',
                              font=('Segoe UI', 8),
                              relief=tk.FLAT,
                              width=2,
                              height=1,
                              cursor='hand2',
                              activebackground=self.colors['danger_hover'])
        delete_btn.pack(side=tk.RIGHT, padx=5, pady=10)
