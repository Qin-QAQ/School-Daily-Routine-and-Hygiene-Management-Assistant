# gui.py - Python封装Tkinter，Java风格语法，支持 setBounds，使用 PFrame
from tool_kit import JButton
from tool_kit import JLabel
from tool_kit import JTextField
from tool_kit import JList
from tool_kit import User
from tool_kit import PFrame
from tool_kit import tk

class LoginPage(PFrame):
    def __init__(self):
        super().__init__(title="School Daily Routine and Hygiene Management Assistant", width=500, height=400)
        self.setDefaultCloseOperation("close")
        self.sys_name = JLabel("校园两操卫生管理助手/登陆")
        self.label = JLabel("输入你的账号和密码：")
        self.field1 = JTextField("账号", width=150)
        self.field2 = JTextField("密码", width=150)
        self.button = JButton("登陆")
        self.remind = JLabel("")

        # 设置位置和大小（像 Java 一样！）
        self.label.setBounds(50, 50, 150, 30)
        self.sys_name.setBounds(200, 0, 400, 30)
        self.field1.setBounds(50, 90, 200, 30)
        self.field2.setBounds(50, 150, 200, 30)
        self.button.setBounds(50, 210, 120, 35)
        self.remind.setBounds(50, 300, 150, 30)
        # 添加到窗体
        self.add(self.label)
        self.add(self.field1)
        self.add(self.field2)
        self.add(self.button)
        self.add(self.remind)
        self.add(self.sys_name)
        self.user = User("", "")


        # 绑定事件
        self.button.addActionListener(self.on_button_click)

    def on_button_click(self):
        name = self.field1.getText()
        password = self.field2.getText()
        if name.strip() and password.strip():
            self.user = User(name, password)
            if self.user.login_level != "has no login":
                self.root.destroy()
            else:
                self.remind.setText("用户名或密码错误")
        else:
            self.remind.setText("输入框内不能为<空>。")
class MainPage(PFrame):
    def __init__(self, self_user: User):
        super().__init__("School Daily Routine and Hygiene Management Assistant", 600, 600)
        # 创建元素
        self.d_sys_name = JLabel("校园两操卫生管理助手/工作界面")
        self.user = self_user
        self.d_level = JLabel(f"{self.user.login_level}@{self.user.login_name}")
        #编辑元素位置
        self.d_level.setBounds(0, 0, 200, 30)
        self.d_sys_name.setBounds(200, 0, 400, 30)
        #删除元素
        self.add(self.d_sys_name)
        self.add(self.d_level)

        self.click_state = ""
        if self.user.login_level == "Admin":
            def admin_button_on_click():
                self.click_state = "set_admin"
                self.root.destroy()
            def grader_button_on_click():
                self.click_state = "set_grader"
                self.root.destroy()
            def teacher_button_on_click():
                self.click_state = "set_teacher"
                self.root.destroy()
            # 管理员控件
            self.view_admin_button = JButton("管理 管理员账户...")
            self.view_grader_button = JButton("管理 打分员账户...")
            self.view_teacher_button = JButton("管理 教师账户...")
            # 设置位置
            self.view_admin_button.setBounds(230, 60, 140, 30)
            self.view_grader_button.setBounds(230, 110, 140, 30)
            self.view_teacher_button.setBounds(230, 160, 140, 30)

            self.add(self.view_admin_button)
            self.add(self.view_grader_button)
            self.add(self.view_teacher_button)

            self.view_admin_button.addActionListener(func=admin_button_on_click)
            self.view_grader_button.addActionListener(func=grader_button_on_click)
            self.view_teacher_button.addActionListener(func=teacher_button_on_click)


class AdminControl(PFrame):
    def __init__(self, s_user: User):
        super().__init__("School Daily Routine and Hygiene Management Assistant", 600, 600)
        def do_sth_when_click_at_add_button():
            self.list.listbox.selection_clear(0, tk.END)
            s_user.add_admin(self.root)
            self.list.setItems(s_user.get_user_names("Admin"))
        def do_sth_when_click_at_del_button_and_select():
            s = self.list.getSelectedValue()
            print(s)
            self.list.listbox.selection_clear(0, tk.END)
            if s:
                s_user.delete_admin(s)
                self.list.setItems(s_user.get_user_names("Admin"))
                print("ok")
        self.setDefaultCloseOperation("hide")

        self.l = JLabel("校园两操卫生管理助手/管理打分员账户")
        self.list = JList()
        self.add_button = JButton("添加 管理员")
        self.del_button = JButton("删除 管理员")


        self.add_button.setBounds(0, 70, 200, 30)
        self.del_button.setBounds(0, 120, 200, 30)
        self.l.setBounds(200, 0, 200, 30)
        self.list.setBounds(400, 70 , 200, 400)
        self.list.setItems(s_user.get_user_names("Admin"))

        self.add(self.l)
        self.add(self.list)
        self.add(self.add_button)
        self.add(self.del_button)

        self.add_button.addActionListener(func=do_sth_when_click_at_add_button)
        self.del_button.addActionListener(func=do_sth_when_click_at_del_button_and_select)
class GraderControl(PFrame):
    def __init__(self, s_user: User):
        self.title = "School Daily Routine and Hygiene Management Assistant"

        super().__init__(self.title, 600, 600)

        def do_sth_when_click_at_add_button():
            self.list.listbox.selection_clear(0, tk.END)
            s_user.add_admin(self.root)
            self.list.setItems(s_user.get_user_names("Grader"))
        def do_sth_when_click_at_del_button_and_select():
            s = self.list.getSelectedValue()
            print(s)
            self.list.listbox.selection_clear(0, tk.END)
            if s:
                s_user.delete_admin(s)
                self.list.setItems(s_user.get_user_names("Grader"))
                print("ok")
        self.setDefaultCloseOperation("hide")

        self.l = JLabel("校园两操卫生管理助手/管理打分员账户")
        self.list = JList()
        self.add_button = JButton("添加 管理员")
        self.del_button = JButton("删除 管理员")

        self.add_button.setBounds(0, 70, 200, 30)
        self.del_button.setBounds(0, 120, 200, 30)
        self.l.setBounds(200, 0, 200, 30)
        self.list.setBounds(400, 70 , 200, 400)
        self.list.setItems(s_user.get_user_names("Admin"))

        self.add(self.l)
        self.add(self.list)
        self.add(self.add_button)
        self.add(self.del_button)

        self.add_button.addActionListener(func=do_sth_when_click_at_add_button)
        self.del_button.addActionListener(func=do_sth_when_click_at_del_button_and_select)



if __name__ == '__main__':
    # 启动程序
    login_page = LoginPage()
    login_page.setVisible(True)
    user = login_page.user


    if user.login_level == "Admin":
        app = MainPage(user)
        app.setVisible(True)
        if app.click_state == "set_admin":
            a_c_page = AdminControl(user)
            a_c_page.setVisible(True)
        elif app.click_state == "set_grader":
            g_c_page = GraderControl
        elif app.click_state == "set_teacher":
            pass
    elif user.login_level == "Grader":
        pass
    elif user.login_level == "Teacher":
        pass
    print(f"OK, {user.login_level}")


