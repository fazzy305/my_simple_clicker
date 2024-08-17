import sys
import cv2
import numpy as np
import pyautogui
import time
import keyboard
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import threading
import sys
from pystray import MenuItem as item, Menu, Icon
import ctypes

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

if not is_admin():
    # 重新运行脚本并请求管理员权限
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
    sys.exit()

# 加载目标图片
template = cv2.imread('check.png')
template_height, template_width = template.shape[:2]

# 指定屏幕范围（左上角和右下角坐标）
x1, y1 = 1794, 310  # 左上角
x2, y2 = 1834, 350  # 右下角

is_running = False

def execute_code():
    global is_running
    if not is_running:
        return

    # 截取屏幕指定范围
    screenshot = pyautogui.screenshot(region=(x1, y1, x2 - x1, y2 - y1))
    screenshot = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)

    # 使用模板匹配
    result = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
    threshold = 0.4  # 匹配阈值
    locations = np.where(result >= threshold)

    # 如果找到匹配
    if locations[0].size > 0:
        # 获取第一个匹配的位置
        match_x = locations[1][0] + x1 + template_width // 2
        match_y = locations[0][0] + y1 + template_height // 2

        # 记录当前鼠标位置
        original_position = pyautogui.position()

        # 点击匹配位置
        pyautogui.click(match_x, match_y)

        # 等待一段时间（可选）
        time.sleep(0.1)

        # 还原鼠标位置
        pyautogui.moveTo(original_position)

    else:
        print("未找到匹配的图片。")

    # 继续执行
    if is_running:
        threading.Timer(1, execute_code).start()

def start_execution():
    global is_running
    if not is_running:
        is_running = True
        print("脚本启动")
        execute_code()

def pause_execution():
    global is_running
    if is_running:
        is_running = False
        print("脚本暂停")

def on_key_press(event):
    if event.name == 'f7':
        start_execution()
    elif event.name == 'f8':
        pause_execution()

keyboard.on_press(on_key_press)

def on_closing():
    global is_running
    if messagebox.askokcancel("退出", "确定要退出程序吗？"):
        is_running = False  # 停止执行代码
        root.destroy()
        icon.stop()
        sys.exit()  # 确保程序完全退出

def create_tray_icon(root):
    image = Image.open("icon.png")  # 请确保有一个名为 "icon.png" 的图标文件
    menu = (item('显示', lambda: root.deiconify()), item('退出', on_closing))
    icon = Icon("name", image, "自动点击器", menu)
    return icon

root = tk.Tk()
root.title("自动点击器")
root.geometry("200x100")

start_button = tk.Button(root, text="F7 启动", command=start_execution)
start_button.pack(pady=5)

pause_button = tk.Button(root, text="F8 暂停", command=pause_execution)
pause_button.pack(pady=5)

root.protocol("WM_DELETE_WINDOW", on_closing)

icon = create_tray_icon(root)
icon.run_detached()

root.mainloop()