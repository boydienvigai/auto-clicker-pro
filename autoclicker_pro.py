import threading
import time
import tkinter as tk
from tkinter import ttk, messagebox

import pyautogui
from pynput import keyboard

try:
    import win32con
    import win32gui
except ImportError:
    win32con = win32gui = None

# Tắt độ trễ mặc định của PyAutoGUI; rê chuột vào góc trên trái để dừng khẩn cấp.
pyautogui.PAUSE = 0
pyautogui.FAILSAFE = True


class AutoClicker:
    def __init__(self, root):
        self.root = root
        self.root.title("Auto Clicker Pro")
        self.root.geometry("520x650")
        self.root.minsize(480, 580)
        self.root.attributes("-topmost", True)
        self.root.configure(bg="#f3f5f8")

        self.points = []
        self.overlays = []
        self.running = False
        self.worker = None
        self.listener = None
        self.points_lock = threading.Lock()

        self.interval = tk.StringVar(value="100")
        self.repeat_mode = tk.StringVar(value="infinite")
        self.repeat_count = tk.StringVar(value="10")
        self.click_type = tk.StringVar(value="left")
        self.status_var = tk.StringVar(
            value="Sẵn sàng — nhấn F7 để thêm điểm tại vị trí chuột"
        )

        self._setup_style()
        self.setup_ui()
        self.setup_hotkeys()
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def _setup_style(self):
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure("TLabelframe", background="#ffffff")
        style.configure("TLabelframe.Label", font=("Segoe UI", 10, "bold"))
        style.configure("TFrame", background="#ffffff")
        style.configure("TLabel", background="#ffffff", font=("Segoe UI", 10))
        style.configure("TButton", font=("Segoe UI", 9), padding=7)
        style.configure("TRadiobutton", background="#ffffff", font=("Segoe UI", 9))

    def setup_ui(self):
        header = tk.Label(
            self.root, text="🖱  AUTO CLICKER PRO",
            font=("Segoe UI", 17, "bold"), bg="#1976D2",
            fg="white", pady=15
        )
        header.pack(fill="x")

        ctrl = ttk.LabelFrame(self.root, text="Điều khiển điểm click")
        ctrl.pack(fill="x", padx=12, pady=(12, 7))
        row = ttk.Frame(ctrl)
        row.pack(fill="x", padx=8, pady=8)
        ttk.Button(row, text="＋ Thêm điểm (F7)", command=self.add_point).pack(
            side="left", expand=True, fill="x", padx=(0, 4)
        )
        ttk.Button(row, text="Xóa tất cả", command=self.clear_points).pack(
            side="left", expand=True, fill="x", padx=(4, 0)
        )

        list_frame = ttk.LabelFrame(self.root, text="Danh sách điểm click")
        list_frame.pack(fill="both", expand=True, padx=12, pady=7)
        self.listbox = tk.Listbox(
            list_frame, height=9, font=("Consolas", 10),
            selectmode=tk.SINGLE, activestyle="dotbox",
            bg="#fbfcfe", relief="flat", highlightthickness=1,
            highlightbackground="#d7dce3"
        )
        scroll = ttk.Scrollbar(list_frame, orient="vertical", command=self.listbox.yview)
        self.listbox.configure(yscrollcommand=scroll.set)
        self.listbox.pack(side="left", fill="both", expand=True, padx=(8, 0), pady=8)
        scroll.pack(side="right", fill="y", padx=(0, 8), pady=8)
        ttk.Button(
            list_frame, text="Xóa điểm đang chọn", command=self.delete_selected
        ).pack(fill="x", padx=8, pady=(0, 8))

        settings = ttk.LabelFrame(self.root, text="Cài đặt")
        settings.pack(fill="x", padx=12, pady=7)

        row1 = ttk.Frame(settings)
        row1.pack(fill="x", padx=8, pady=(8, 4))
        ttk.Label(row1, text="Khoảng cách giữa các click (ms):", width=30).pack(side="left")
        ttk.Entry(row1, textvariable=self.interval, width=12).pack(side="left")

        row2 = ttk.Frame(settings)
        row2.pack(fill="x", padx=8, pady=4)
        ttk.Label(row2, text="Loại click:", width=30).pack(side="left")
        ttk.Combobox(
            row2, textvariable=self.click_type,
            values=("left", "right", "double", "middle"),
            state="readonly", width=12
        ).pack(side="left")

        row3 = ttk.Frame(settings)
        row3.pack(fill="x", padx=8, pady=(4, 8))
        ttk.Label(row3, text="Chế độ lặp:", width=30).pack(side="left")
        ttk.Radiobutton(
            row3, text="Vô hạn", variable=self.repeat_mode, value="infinite"
        ).pack(side="left")
        ttk.Radiobutton(
            row3, text="Số vòng:", variable=self.repeat_mode, value="count"
        ).pack(side="left", padx=(8, 4))
        ttk.Entry(row3, textvariable=self.repeat_count, width=7).pack(side="left")

        self.start_btn = tk.Button(
            self.root, text="▶  BẮT ĐẦU (F6)", command=self.toggle,
            bg="#2E9D55", activebackground="#258347", fg="white",
            activeforeground="white", font=("Segoe UI", 13, "bold"),
            relief="flat", height=2, cursor="hand2"
        )
        self.start_btn.pack(fill="x", padx=12, pady=12)

        tk.Label(
            self.root, textvariable=self.status_var, fg="#155A9C",
            bg="#f3f5f8", font=("Segoe UI", 9), wraplength=480
        ).pack(pady=(0, 5))
        tk.Label(
            self.root,
            text="Phím tắt toàn hệ thống: F6 bắt đầu/dừng  •  F7 thêm điểm",
            fg="#697586", bg="#f3f5f8", font=("Segoe UI", 8)
        ).pack(pady=(0, 10))

    def setup_hotkeys(self):
        def on_press(key):
            if key == keyboard.Key.f6:
                self.root.after(0, self.toggle)
            elif key == keyboard.Key.f7:
                self.root.after(0, self.add_point)

        self.listener = keyboard.Listener(on_press=on_press)
        self.listener.daemon = True
        self.listener.start()

    def make_click_through(self, hwnd):
        if win32gui is None:
            return
        try:
            styles = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
            styles |= win32con.WS_EX_LAYERED | win32con.WS_EX_TRANSPARENT
            win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, styles)
        except Exception:
            pass

    def add_point(self):
        if self.running:
            self.status_var.set("Hãy dừng Auto Clicker trước khi thay đổi danh sách điểm.")
            return
        x, y = pyautogui.position()
        self.points.append((x, y))
        self.listbox.insert(tk.END, f"#{len(self.points)}   X: {x:<6} Y: {y}")
        self.create_overlay(x, y)
        self.status_var.set(f"Đã thêm điểm ({x}, {y}) — tổng cộng {len(self.points)} điểm")

    def create_overlay(self, x, y):
        overlay = tk.Toplevel(self.root)
        overlay.overrideredirect(True)
        overlay.attributes("-topmost", True)
        overlay.attributes("-alpha", 0.78)
        overlay.geometry(f"24x24+{x - 12}+{y - 12}")
        overlay.configure(bg="#e53935")
        tk.Label(
            overlay, text="●", fg="white", bg="#e53935",
            font=("Segoe UI", 11, "bold")
        ).pack(expand=True, fill="both")
        overlay.update_idletasks()
        self.make_click_through(overlay.winfo_id())
        self.overlays.append(overlay)

    def clear_points(self):
        if self.running:
            self.status_var.set("Hãy dừng Auto Clicker trước khi xóa điểm.")
            return
        self.points.clear()
        self.listbox.delete(0, tk.END)
        for overlay in self.overlays:
            try:
                overlay.destroy()
            except tk.TclError:
                pass
        self.overlays.clear()
        self.status_var.set("Đã xóa tất cả điểm click.")

    def delete_selected(self):
        if self.running:
            self.status_var.set("Hãy dừng Auto Clicker trước khi xóa điểm.")
            return
        selected = self.listbox.curselection()
        if not selected:
            return
        index = selected[0]
        self.points.pop(index)
        try:
            self.overlays.pop(index).destroy()
        except (IndexError, tk.TclError):
            pass
        self.refresh_list()

    def refresh_list(self):
        self.listbox.delete(0, tk.END)
        for i, (x, y) in enumerate(self.points, 1):
            self.listbox.insert(tk.END, f"#{i}   X: {x:<6} Y: {y}")
        self.status_var.set(f"Danh sách hiện có {len(self.points)} điểm.")

    def toggle(self):
        if self.running:
            self.stop()
        else:
            self.start()

    def start(self):
        if not self.points:
            messagebox.showwarning(
                "Chưa có điểm click",
                "Bạn chưa thêm điểm nào. Di chuyển chuột đến vị trí cần click rồi nhấn F7."
            )
            return
        try:
            interval_ms = float(self.interval.get())
            if interval_ms < 1:
                raise ValueError
            repeat_count = int(self.repeat_count.get())
            if self.repeat_mode.get() == "count" and repeat_count < 1:
                raise ValueError
        except ValueError:
            messagebox.showerror(
                "Thông số không hợp lệ",
                "Khoảng cách phải từ 1 ms trở lên và số vòng lặp phải là số nguyên dương."
            )
            return

        self.running = True
        self.start_btn.config(text="⏹  DỪNG (F6)", bg="#D93636", activebackground="#B92B2B")
        self.status_var.set("Đang chạy — nhấn F6 để dừng.")
        points = list(self.points)
        click_type = self.click_type.get()
        mode = self.repeat_mode.get()
        max_count = repeat_count if mode == "count" else 0
        self.worker = threading.Thread(
            target=self.run_clicker,
            args=(points, interval_ms / 1000.0, click_type, max_count),
            daemon=True
        )
        self.worker.start()

    def stop(self):
        self.running = False
        self.start_btn.config(text="▶  BẮT ĐẦU (F6)", bg="#2E9D55", activebackground="#258347")
        self.status_var.set("Đã dừng.")

    def run_clicker(self, points, interval, click_type, max_count):
        completed = 0
        try:
            while self.running:
                for x, y in points:
                    if not self.running:
                        return
                    pyautogui.moveTo(x, y, duration=0.02)
                    if click_type == "left":
                        pyautogui.click(x, y)
                    elif click_type == "right":
                        pyautogui.rightClick(x, y)
                    elif click_type == "double":
                        pyautogui.doubleClick(x, y)
                    elif click_type == "middle":
                        pyautogui.middleClick(x, y)
                    if not self.running:
                        return
                    time.sleep(interval)

                completed += 1
                if max_count and completed >= max_count:
                    self.root.after(0, self.finish_run, completed)
                    return
        except pyautogui.FailSafeException:
            self.root.after(0, self.stop)
            self.root.after(0, lambda: self.status_var.set("Đã dừng khẩn cấp (chuột ở góc trên trái)."))
        except Exception as exc:
            self.root.after(0, self.stop)
            self.root.after(0, lambda e=str(exc): messagebox.showerror("Lỗi Auto Clicker", e))

    def finish_run(self, completed):
        self.stop()
        self.status_var.set(f"Hoàn thành {completed} vòng click.")

    def on_close(self):
        self.running = False
        if self.listener is not None:
            self.listener.stop()
        for overlay in self.overlays:
            try:
                overlay.destroy()
            except tk.TclError:
                pass
        self.root.destroy()


def main():
    root = tk.Tk()
    AutoClicker(root)
    root.mainloop()


if __name__ == "__main__":
    main()
