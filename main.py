import tkinter.messagebox
from tkinter import *
import configparser
import pyperclip
from PIL import ImageTk
from pynput import keyboard
from screenshot import *

global tk_image, screenshot


def read_config():
    try:
        config_ini = configparser.ConfigParser()
        config_ini.read('config.ini', encoding='utf-8')
        key = config_ini.get('Bind-Key', 'bind_key')
        color = config_ini.get('Select-Rectangle', 'color')
        width = config_ini.get('Select-Rectangle', 'width')
        return {'bind_key': key, 'select_rectangle_color': color, 'select_rectangle_width': width}
    except configparser.NoSectionError:
        return {'bind_key': '<ctrl>+<alt>', 'select_rectangle_color': 'red', 'select_rectangle_width': 1}


def on_activate(_select_rectangle_color, _select_rectangle_width):
    screenshot_image = screen_shot()
    init_window = Tk()
    window = Main(init_window, _select_rectangle_color, _select_rectangle_width)
    window.set_window()
    window.load_image(screenshot_image)
    window.draw_canvas()
    init_window.focus_force()
    init_window.mainloop()


def for_canonical(f):
    return lambda k: f(listener.canonical(k))


class Main:
    main_window_w = None
    main_window_h = None
    tk_result_window = None
    canvas = None
    position = []

    def __init__(self, init_tk_window, select_rectangle_outline, select_rectangle_width):
        self.tk_main_window = init_tk_window
        self.select_rectangle_outline = select_rectangle_outline
        self.select_rectangle_width = select_rectangle_width
        self.copy_button_text = StringVar(self.tk_result_window, '复制到剪切板')
        # self.tk_main_window.overrideredirect(True)
        self.tk_main_window.title('请选取二维码')
        self.tk_main_window.bind('<B1-Motion>', self.process_mouse_event)
        self.tk_main_window.bind('<Button-1>', self.process_mouse_event)
        self.tk_main_window.bind('<ButtonRelease-1>', self.get_coordinates)

    def set_window(self):
        self.main_window_w = self.tk_main_window.winfo_screenwidth()
        self.main_window_h = self.tk_main_window.winfo_screenheight()
        self.tk_main_window.resizable(width=False, height=False)

    def load_image(self, image):
        global tk_image, screenshot
        new_image = resize(self.main_window_w, self.main_window_h, image)
        screenshot = new_image
        tk_image = ImageTk.PhotoImage(new_image)

    def process_mouse_event(self, event):
        rectangle_id = self.draw_rectangle(event)
        self.clear_rectangle(rectangle_id)

    def draw_canvas(self):
        global tk_image
        self.canvas = Canvas(self.tk_main_window, width=self.main_window_w, height=self.main_window_h)
        self.canvas.create_image(0, 0, image=tk_image, anchor='nw')
        self.canvas.grid(row=0, column=0)

    def draw_rectangle(self, mouse_event):
        self.position.append([mouse_event.x, mouse_event.y])
        start_x = self.position[0][0]
        start_y = self.position[0][1]
        if len(self.position) >= 1000:
            self.position.pop(1000 - 500)

        return self.canvas.create_rectangle(
            start_x,
            start_y,
            mouse_event.x,
            mouse_event.y,
            outline=self.select_rectangle_outline,
            width=self.select_rectangle_width
        )

    def clear_rectangle(self, rectangle_id):
        if rectangle_id >= 3:  # 不删除画布，只删除选择框
            self.canvas.delete(rectangle_id - 1)

    def get_coordinates(self, event):
        x1 = self.position[0][0]
        y1 = self.position[0][1]
        x2 = self.position[len(self.position) - 1][0]
        y2 = self.position[len(self.position) - 1][1]
        # 处理一下反选问题
        if x1 > x2:
            x1, x2 = x2, x1
        if y1 > y2:
            y1, y2 = y2, y1
        qr_image = process_image(screenshot, [x1, y1, x2, y2])
        qr_code = decode_qr_code(qr_image)
        if not qr_code:
            tkinter.messagebox.showinfo('信息', '未识别到二维码')
        else:
            self.get_qr_code(qr_code)
        self.position = []

    def get_qr_code(self, result):
        self.tk_result_window = Toplevel()
        self.tk_result_window.title('结果')
        self.tk_result_window['bg'] = 'white'
        Label(self.tk_result_window, text=result, width=60, height=5, bg='white').grid(row=0, column=0)
        Button(
            self.tk_result_window,
            textvariable=self.copy_button_text,
            command=lambda: self.copy_qr_code(result),
            padx=10,
            bg='white'
        ).grid(row=1, column=0)
        Label(self.tk_result_window, bg='white').grid(row=2, column=0)

    def copy_qr_code(self, result):
        pyperclip.copy(result)
        self.copy_button_text.set('已复制')


if __name__ == '__main__':
    config_content = read_config()
    bind_key = config_content['bind_key']
    select_rectangle_color = config_content['select_rectangle_color']
    select_rectangle_width = config_content['select_rectangle_width']
    print('正在监听 %s 按键' % bind_key)
    print('选择框颜色 %s' % select_rectangle_color)
    print('选择框像素 %s' % select_rectangle_width)
    hotkey = keyboard.HotKey(keyboard.HotKey.parse(bind_key), lambda: on_activate(select_rectangle_color, select_rectangle_width))
    with keyboard.Listener(on_press=for_canonical(hotkey.press), on_release=for_canonical(hotkey.release)) as listener:
        listener.join()
