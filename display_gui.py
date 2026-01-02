# model : display_gui
import tkinter as tk
import os
from PIL import Image, ImageTk

class Component:
    """所有GUI组件的基类"""
    def __init__(self, widget):
        self.widget = widget
        self._x = 0
        self._y = 0
        self._width = 0
        self._height = 0
        self.using_place = False  # 标记是否使用 place 布局

    def setBounds(self, x, y, width, height):
        """类似 Java Swing 的 setBounds(x, y, width, height)"""
        self._x = x
        self._y = y
        self._width = width
        self._height = height
        self.widget.place(x=x, y=y, width=width, height=height)
        self.using_place = True

    def setPosition(self, x, y):
        """仅设置位置"""
        self.setBounds(x, y, self._width, self._height)

    def setSize(self, width, height):
        """仅设置大小"""
        self.setBounds(self._x, self._y, width, height)

    def getX(self): return self._x
    def getY(self): return self._y
    def getWidth(self): return self._width
    def getHeight(self): return self._height


class JPic(Component):
    def __init__(self, image_path=None):
        """
        初始化图片组件
        :param image_path: 图片文件路径（可选，后续可通过 setImage 设置）
        """
        self._last_image_path = None
        self.label = tk.Label()
        super().__init__(self.label)
        self._image_tk = None  # 必须保留引用，防止被垃圾回收
        if image_path is not None:
            self.setImage(image_path)

    def setImage(self, image_path):
        """
        加载并显示指定路径的图片
        :param image_path: 图片文件的完整或相对路径
        """
        if not os.path.isfile(image_path):
            raise FileNotFoundError(f"图片文件不存在: {image_path}")

        try:
            # 使用 PIL 打开图片
            pil_image = Image.open(image_path)

            # 可选：根据当前组件尺寸自动缩放（如果已设置宽高）
            if self._width > 0 and self._height > 0:

                # 新版本（>=9.1.0）
                resample_filter = Image.Resampling.LANCZOS


                pil_image = pil_image.resize((self._width, self._height), resample=resample_filter)

            # 转换为 Tkinter 支持的格式
            self._image_tk = ImageTk.PhotoImage(pil_image)
            self.label.config(image=self._image_tk)

            # ⚠️ 必须保留引用，否则图片会被 GC 掉导致不显示
            self.label.image = self._image_tk

        except Exception as e:
            raise RuntimeError(f"无法加载图片 '{image_path}': {e}")

    def clear(self):
        """清空当前显示的图片"""
        self.label.config(image='')
        self._image_tk = None
        self.label.image = None

    def setSize(self, width, height):
        """重写 setSize，在调整大小时重新缩放图片（如果已有图片）"""
        _, old_h = self._width, self._height
        super().setSize(width, height)

        # 如果已有图片，尝试重新加载并缩放到新尺寸
        if hasattr(self, '_last_image_path') and self._last_image_path:
            self.setImage(self._last_image_path)  # 触发 resize

    def setImageWithPath(self, image_path):
        """兼容方法：同 setImage，但记录路径以便 setSize 时重用"""
        self._last_image_path = image_path
        self.setImage(image_path)

class JButton(Component):
    def __init__(self, text="", action=None):
        btn = tk.Button(text=text, command=action)
        super().__init__(btn)
        self.setText(text)
        self.action = action

    def setText(self, text):
        self.widget.config(text=text)

    def getText(self):
        return self.widget.cget("text")

    def addActionListener(self, func):
        self.action = func
        self.widget.config(command=func)


class JLabel(Component):
    def __init__(self, text=""):
        label = tk.Label(text=text, anchor='w')  # 左对齐
        super().__init__(label)
        self.setText(text)

    def setText(self, text):
        self.widget.config(text=text)

    def getText(self):
        return self.widget.cget("text")


class JList(Component):
    def __init__(self, items=None):
        """
        初始化 JList 组件
        :param items: 初始显示的字符串列表（可选）
        """
        self.listbox = tk.Listbox()
        super().__init__(self.listbox)
        self._selection_listeners = []  # 存储所有监听器
        self.setItems(items or [])

        # 绑定一次事件，内部调用所有监听器
        self.listbox.bind('<<ListboxSelect>>', self._on_selection_change)

    def setItems(self, items):
        """设置列表项"""
        self.listbox.delete(0, tk.END)
        for item in items:
            self.listbox.insert(tk.END, str(item))

    def getSelectedValue(self):
        """获取当前选中的值（单选）"""
        selection = self.listbox.curselection()
        if selection:
            return self.listbox.get(selection[0])
        return None

    def getSelectedIndex(self):
        """获取当前选中的索引（单选）"""
        selection = self.listbox.curselection()
        return selection[0] if selection else -1

    def addSelectionListener(self, func):
        """
        添加一个选择监听器（可多次调用，支持多个监听器）
        :param func: 回调函数，无参（或接受一个 event 参数，但通常不需要）
        """
        if not callable(func):
            raise TypeError("Listener must be callable.")
        self._selection_listeners.append(func)

    def removeSelectionListener(self, func):
        """可选：移除某个监听器"""
        if func in self._selection_listeners:
            self._selection_listeners.remove(func)

    def _on_selection_change(self, event=None):
        """内部统一事件处理器，广播给所有监听器"""
        for listener in self._selection_listeners:
            try:
                # 兼容两种写法：func() 或 func(event)
                if listener.__code__.co_argcount == 0:
                    listener()
                else:
                    listener(event)
            except Exception as e:
                # 可选：记录错误，避免一个监听器崩溃影响其他
                print(f"Error in selection listener: {e}")

    def getItems(self):
        """获取当前所有项（列表形式）"""
        return list(self.listbox.get(0, tk.END))
class JTextField(Component):
    def __init__(self, text="", width=20):
        self.var = tk.StringVar(value=text)
        entry = tk.Entry(textvariable=self.var)
        super().__init__(entry)
        self.setText(text)
        self.setSize(width * 10, 25)  # 默认高度25

    def setText(self, text):
        self.var.set(text)

    def getText(self):
        return self.var.get()


class MessageDialog:
    """
    显示一个模态子窗口，用于展示一段文本信息。

    参数:
        parent_root: 父窗口的 Tk 根对象（通常是 PFrame.root）
        message: 要显示的字符串内容
        title: 子窗口标题（可选，默认为 "提示"）
        width: 窗口宽度（默认 300）
        height: 窗口高度（默认 150）
    """

    def __init__(self, parent_root, message: str, title: str = "提示", width: int = 300, height: int = 150):
        self.parent_root = parent_root
        self.message = message
        self.title = title
        self.width = width
        self.height = height

        # 创建子窗口（Toplevel）
        self.dialog = tk.Toplevel(self.parent_root)
        self.dialog.title(self.title)
        self.dialog.geometry(f"{self.width}x{self.height}")
        self.dialog.resizable(False, False)

        # 居中显示（相对于父窗口）
        self._center_window()

        # 创建文本标签
        text_label = tk.Label(
            self.dialog,
            text=self.message,
            wraplength=self.width - 40,  # 自动换行
            justify="left",
            anchor="nw"
        )
        text_label.place(x=20, y=20, width=self.width - 40, height=self.height - 80)

        # 创建“确定”按钮
        ok_button = tk.Button(self.dialog, text="确定", command=self.close)
        ok_button.place(x=(self.width - 60) // 2, y=self.height - 50, width=60, height=30)

        # 模态：禁用父窗口交互
        self.dialog.transient(self.parent_root)
        self.dialog.grab_set()  # 模态锁定
        self.parent_root.wait_window(self.dialog)  # 等待窗口关闭

    def _center_window(self):
        """将子窗口居中于父窗口"""
        self.dialog.update_idletasks()
        parent_x = self.parent_root.winfo_x()
        parent_y = self.parent_root.winfo_y()
        parent_width = self.parent_root.winfo_width()
        parent_height = self.parent_root.winfo_height()

        x = parent_x + (parent_width - self.width) // 2
        y = parent_y + (parent_height - self.height) // 2
        self.dialog.geometry(f"+{x}+{y}")

    def close(self):
        """关闭对话框"""
        self.dialog.destroy()

class PFrame:
    """主窗口类，模仿 Java JFrame，但命名为 PFrame (Python Frame)"""
    def __init__(self, title="PFrame", width=400, height=300):
        self.root = tk.Tk()
        self.root.title(title)
        self.root.geometry(f"{width}x{height}")
        self.root.resizable(True, True)
        self.components = []

        # 存储布局模式：'pack', 'grid', 'place'
        self.layout_mode = None  # 自动检测

    def add(self, component):
        """添加组件。如果组件用了 place，则自动切换为 place 模式"""
        if not isinstance(component, Component):
            raise TypeError("Component must inherit from Component class.")

        # 如果组件设置了 bounds，强制使用 place 布局
        if hasattr(component, '_using_place') and component.using_place:
            if self.layout_mode not in (None, 'place'):
                raise RuntimeError("Cannot mix layout managers: already using pack/grid.")
            self.layout_mode = 'place'
        else:
            # 否则允许使用 pack/grid（暂不混合）
            if self.layout_mode is None:
                self.layout_mode = 'manual'  # 表示用户手动调用 pack/grid/setBounds

        self.components.append(component)
        # 注意：不需要主动 pack/grid，由用户或 setBounds 控制
    def add_s(self, components: list):
        for c in components:
            self.add(c)
    def setTitle(self, title):
        self.root.title(title)

    def setSize(self, width, height):
        self.root.geometry(f"{width}x{height}")

    def setResizable(self, resizable):
        self.root.resizable(resizable, resizable)

    def setDefaultCloseOperation(self, op="exit", f = None):
        """设置关闭行为"""
        if op == "exit":
            self.root.protocol("WM_DELETE_WINDOW", self.root.quit)
        elif op == "close":
            self.root.protocol("WM_DELETE_WINDOW", self.root.destroy)
        elif op == "hide":
            self.root.protocol("WM_DELETE_WINDOW", self.root.withdraw)
        elif op == "s":
            self.root.protocol("WM_DELETE_WINDOW", f)
    def setVisible(self, visible=True):
        """显示窗口并启动事件循环"""
        if visible:
            self.root.deiconify()
        else:
            self.root.withdraw()

        self.root.mainloop()  # 启动主循环（只应调用一次）

    # --- 辅助方法：支持传统布局 ---
    def packAll(self):
        """使用 pack 布局所有未使用 place 的组件"""
        for comp in self.components:
            if not comp.using_place:
                comp.pack(pady=2)

    def gridAll(self, cols=1):
        """简单 grid 布局：按行排列"""
        for idx, comp in enumerate(self.components):
            if not comp.using_place:
                row = idx // cols
                col = idx % cols
                comp.grid(row=row, column=col, padx=5, pady=5)