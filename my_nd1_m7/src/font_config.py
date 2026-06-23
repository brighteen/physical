"""matplotlib 한글 폰트 자동 설정.

OS별로 사용 가능한 한글 폰트를 자동 탐지하여 설정.
모든 lab 스크립트의 첫머리에서 import 하세요.

Usage
-----
    from src.font_config import setup_korean_font
    setup_korean_font()
"""
import platform
import matplotlib
import matplotlib.font_manager as fm


def setup_korean_font():
    """OS별 한글 폰트 자동 설정.

    Returns
    -------
    font_name : str
        실제 적용된 폰트 이름 (찾지 못하면 'DejaVu Sans')
    """
    system = platform.system()

    candidates = []
    if system == 'Darwin':       # macOS
        candidates = ['AppleGothic', 'Apple SD Gothic Neo']
    elif system == 'Windows':
        candidates = ['Malgun Gothic', 'Gulim', 'Batang']
    else:                         # Linux
        candidates = ['Noto Sans CJK JP', 'Noto Sans CJK KR',
                       'NanumGothic', 'UnDotum', 'Baekmuk Gulim']

    # 사용 가능한 폰트 찾기
    available_fonts = {f.name for f in fm.fontManager.ttflist}
    selected = 'DejaVu Sans'      # 기본 fallback
    for cand in candidates:
        if cand in available_fonts:
            selected = cand
            break

    matplotlib.rcParams['font.family'] = selected
    matplotlib.rcParams['axes.unicode_minus'] = False     # 음수 부호 깨짐 방지
    return selected
