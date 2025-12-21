"""테마 및 색상 설정"""


class Theme:
    """애플리케이션 테마 설정"""
    
    LIGHT_THEME = {
        'primary': '#5B9FED',      # 부드러운 파란색
        'primary_hover': '#4A8DD9',
        'secondary': '#7BA9DE',    # 연한 파란색
        'success': '#78C2AD',      # 민트 그린
        'success_hover': '#66B39A',
        'danger': '#EC8D8D',       # 부드러운 핑크
        'danger_hover': '#E07777',
        'warning': '#F4B678',      # 부드러운 오렌지
        'info': '#8FB8E8',         # 밝은 파랑
        'dark': '#37474F',         # 다크 블루-그레이
        'light': '#F8F9FA',        # 밝은 배경
        'sidebar': '#FFFFFF',      # 사이드바
        'btn_bg': '#EBF4FB',       # 버튼 배경 (연한 파란색)
        'btn_hover': '#D4E7F7',    # 버튼 호버
        'text_dark': '#37474F',
        'text_light': '#FFFFFF',
        'text_gray': '#607D8B',    # 회색 텍스트
        'border': '#E1E8ED',       # 테두리
        'scrollbar': '#E1E8ED',    # 스크롤바 트랙
        'scrollbar_thumb': '#B0BEC5' # 스크롤바 썸
    }
    
    DARK_THEME = {
        'primary': '#4A90E2',      # 파란색 강조
        'primary_hover': '#5BA0F2',
        'secondary': '#6B7A8A',     # 회색
        'success': '#5CB85C',      # 초록
        'success_hover': '#6CC86C',
        'danger': '#D9534F',       # 빨강
        'danger_hover': '#E9635F',
        'warning': '#F0AD4E',      # 주황
        'info': '#5BC0DE',         # 하늘색
        'dark': '#2C3E50',         # 다크 블루
        'darker': '#1A1A1A',        # 더 어두운 배경
        'dark_bg': '#2D2D2D',      # 다크 배경
        'dark_panel': '#3A3A3A',   # 다크 패널
        'light': '#ECF0F1',        # 밝은 텍스트용
        'sidebar': '#2D2D2D',      # 사이드바 다크
        'btn_bg': '#3A3A3A',       # 버튼 배경 (다크)
        'btn_hover': '#4A4A4A',    # 버튼 호버
        'btn_active': '#4A90E2',   # 활성 버튼
        'text_dark': '#ECF0F1',    # 밝은 텍스트
        'text_light': '#FFFFFF',
        'text_gray': '#95A5A6',    # 회색 텍스트
        'border': '#4A4A4A',       # 테두리
        'scrollbar': '#3A3A3A',    # 스크롤바 트랙
        'scrollbar_thumb': '#5A5A5A', # 스크롤바 썸
        'tab_bg': '#2D2D2D',       # 탭 배경
        'tab_active': '#4A90E2',   # 활성 탭
        'tab_inactive': '#3A3A3A'  # 비활성 탭
    }
    
    @staticmethod
    def get_theme(theme_name='light'):
        """테마 반환"""
        if theme_name == 'dark':
            return Theme.DARK_THEME
        return Theme.LIGHT_THEME

