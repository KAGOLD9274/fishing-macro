import time
import threading
import tkinter as tk
import pyautogui
from pynput import keyboard

# 맥 레티나 디스플레이 및 안전장치 설정
pyautogui.FAILSAFE = True

# ==================== [ 목표 색상 설정 영역 ] ====================
GAUGE_RGB = (220, 190, 85)   # 노란색 게이지 완료 색상
STOP_RGB = (245, 83, 86)     # STOP 버튼 색상[cite: 2]
TOLERANCE = 10               # 색상 오차 범위
# ================================================================

is_running = False
macro_thread = None

def is_match_color(current_color, target_rgb):
    return all(abs(c - t) <= TOLERANCE for c, t in zip(current_color, target_rgb))

def macro_loop():
    global is_running
    print("[+] 낚시 매크로가 시작되었습니다.")
    
    is_holding = False

    while is_running:
        x, y = pyautogui.position()
        
        try:
            current_pixel = pyautogui.pixel(x, y)
        except Exception:
            time.sleep(0.05)
            continue
        
        # 1. STOP 버튼 색상 감지[cite: 2]
        if is_match_color(current_pixel, STOP_RGB):
            if is_holding:
                pyautogui.mouseUp()
                is_holding = False
            
            for _ in range(5):
                if not is_running:
                    break
                pyautogui.click()
                time.sleep(0.03)
            continue

        # 2. 노란색 게이지 색상 감지
        if is_match_color(current_pixel, GAUGE_RGB):
            if is_holding:
                pyautogui.mouseUp()
                is_holding = False
            time.sleep(0.3)
            continue

        # 3. 평소에는 게이지 충전
        if not is_holding:
            pyautogui.mouseDown()
            is_holding = True

        time.sleep(0.03)

    pyautogui.mouseUp()
    print("[-] 매크로가 정지되었습니다.")

# ==================== [ GUI 및 제어 함수 ] ====================
def start_macro():
    global is_running, macro_thread
    if not is_running:
        is_running = True
        status_label.config(text="상태: 실행 중 (RUNNING)", fg="green")
        macro_thread = threading.Thread(target=macro_loop)
        macro_thread.daemon = True
        macro_thread.start()

def stop_macro():
    global is_running
    if is_running:
        is_running = False
        status_label.config(text="상태: 정지됨 (STOPPED)", fg="red")

def on_press(key):
    try:
        # 단축키 F6으로도 켜고 끌 수 있게 유지
        if key == keyboard.Key.f6:
            if is_running:
                stop_macro()
            else:
                start_macro()
    except AttributeError:
        pass

# 키보드 리스너 백그라운드 실행
listener = keyboard.Listener(on_press=on_press)
listener.start()

# ==================== [ Tkinter GUI 구성 ] ====================
root = tk.Tk()
root.title("낚시 매크로 조종기")
root.geometry("260x180")
root.resizable(False, False)

title_label = tk.Label(root, text="Steal an egg! 낚시 매크로", font=("Arial", 12, "bold"))
title_label.pack(pady=10)

status_label = tk.Label(root, text="상태: 정지됨 (STOPPED)", font=("Arial", 10), fg="red")
status_label.pack(pady=5)

# 시작 버튼
start_btn = tk.Button(root, text="매크로 시작 (START)", font=("Arial", 10, "bold"), bg="#4CAF50", fg="white", width=20, command=start_macro)
start_btn.pack(pady=5)

# 정지 버튼
stop_btn = tk.Button(root, text="매크로 정지 (STOP)", font=("Arial", 10, "bold"), bg="#F44336", fg="white", width=20, command=stop_macro)
stop_btn.pack(pady=5)

root.mainloop()