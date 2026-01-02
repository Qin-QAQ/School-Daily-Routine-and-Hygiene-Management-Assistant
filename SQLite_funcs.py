import sqlite3
import os
import datetime
import json
import ast

def str_to_dict(s: str) -> dict:
    """
    将字符串转换为字典，兼容多种常见格式

    参数:
        s: 待转换的字符串（支持 JSON 格式/原生 dict 格式字符串）

    返回:
        dict: 转换后的字典

    异常:
        ValueError: 字符串格式无法解析为字典时抛出
    """
    if not isinstance(s, str):
        raise TypeError("输入必须是字符串类型")

    # 去除首尾空白字符（包括换行、制表符等）
    s_stripped = s.strip()

    # 空字符串直接返回空字典
    if not s_stripped:
        return {}

    try:
        # 优先用 ast.literal_eval（支持 Python 原生 dict 格式，如单引号、True/False/None）
        result = ast.literal_eval(s_stripped)
        if isinstance(result, dict):
            return result
        else:
            raise ValueError("解析结果不是字典类型")
    except (SyntaxError, ValueError):
        # 降级用 json.loads（仅支持 JSON 标准格式：双引号、true/false/null）
        try:
            # 替换 Python 关键字为 JSON 关键字
            s_json = s_stripped.replace("'", '"') \
                .replace("True", "true") \
                .replace("False", "false") \
                .replace("None", "null")
            result = json.loads(s_json)
            if isinstance(result, dict):
                return result
            else:
                raise ValueError("解析结果不是字典类型")
        except json.JSONDecodeError as e:
            raise ValueError(f"无法将字符串解析为字典：{e}") from e
def get_time():
    #date to dict{"year":2025,"month": 12, "day": 13, "hour": "15", ...}
    time = datetime.datetime.now().strftime('{"y":"%Y", "m":"%m", "d":"%d", "h":"%H", "M":"%M", "s":"%S"}')
    return str_to_dict(time)
def create_folders(name:str):
    if not os.path.exists(name):
        os.makedirs(name)

class MyEasySQLite:


    """自定义的超级简单的SQLite"""

    def __init__(self, db_file: str = "校园卫生管理.db"):
        self.db_file = db_file
        self.conn = None
        self.cursor = None

    def _get_cursor(self):
        """内部自动维护连接，用户完全不用管"""
        try:
            if self.conn:
                self.conn.execute("SELECT 1")
            else:
                raise sqlite3.ProgrammingError
        except (sqlite3.ProgrammingError, sqlite3.OperationalError):
            self.conn = sqlite3.connect(self.db_file)
            self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()
        return self.cursor

    def close(self):
        """自动关闭连接，用with语句可省略"""
        if self.conn:
            try:
                self.conn.close()
            finally:
                self.conn = None
                self.cursor = None
                pass
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    # ===================== 创建表（仅需传列名列表） =====================
    def create_table(self, table_name: str, column_names: list):
        """
        创建表（极简版）
        :param table_name: 表名（如"卫生检查表"）
        :param column_names: 列名列表（如["编号", "学生姓名", "班级"]）
        """
        # 内部自动处理：所有列默认文本类型、非必填
        sql_columns = [f"`{col}` TEXT" for col in column_names]
        # 自动添加一个隐藏的自增编号（避免用户手动管编号）
        sql_columns.insert(0, "`_id` INTEGER PRIMARY KEY AUTOINCREMENT")

        sql = f"CREATE TABLE IF NOT EXISTS `{table_name}` ({', '.join(sql_columns)})"
        cursor = self._get_cursor()
        try:
            cursor.execute(sql)
            self.conn.commit()
            print(f"<$> 表「{table_name}」创建成功（列：{column_names}）")
        except Exception as e:
            self.conn.rollback()
            print(f"<$> 创建表失败：{e}")

    # ===================== 添加数据（仅需传{列名:值}） =====================
    def add_data(self, table_name: str, data: dict):
        """
        添加数据
        :param table_name: 表名
        :param data: 数据字典（如{"学生姓名":"张三", "班级":"三年级二班"}）
        :return: 新增数据的ID
        """
        if not data:
            print("<$> 数据不能为空")
            return None

        keys = list(data.keys())
        values = list(data.values())
        placeholders = ",".join(["?"] * len(keys))

        sql = f"INSERT INTO `{table_name}` ({','.join([f'`{k}`' for k in keys])}) VALUES ({placeholders})"
        cursor = self._get_cursor()
        try:
            cursor.execute(sql, values)
            self.conn.commit()
            print(f"<$> 数据添加成功，ID：{cursor.lastrowid}")
            return cursor.lastrowid
        except Exception as e:
            self.conn.rollback()
            print(f"<$> 添加数据失败：{e}")
            return None

    # ===================== 查询数据（可选条件） =====================
    def get_data(self, table_name: str, conditions: dict = None):
        """
        查询数据
        :param table_name: 表名
        :param conditions: 查询条件（可选，如{"班级":"三年级二班"}）
        :return: 结果列表（每个元素是字典，直接用列名取值）
        """
        cursor = self._get_cursor()
        try:
            if conditions:
                where_clause = " AND ".join([f"`{k}`=?" for k in conditions.keys()])
                sql = f"SELECT * FROM `{table_name}` WHERE {where_clause}"
                cursor.execute(sql, list(conditions.values()))
            else:
                sql = f"SELECT * FROM `{table_name}`"
                cursor.execute(sql)

            # 转成极简字典列表，用户直接用
            results = []
            for row in cursor.fetchall():
                row_dict = {}
                for col in row.keys():
                    # 隐藏内部的_id，只返回用户定义的列
                    if col != "_id":
                        row_dict[col] = row[col]
                results.append(row_dict)

            print(f"<$> 查询到 {len(results)} 条数据")
            return results
        except Exception as e:
            print(f"<$> 查询数据失败：{e}")
            return []

    # ===================== 修改数据 =====================
    def update_data(self, table_name: str, new_data: dict, conditions: dict):
        """
        修改数据
        :param table_name: 表名
        :param new_data: 新数据（如{"卫生分数":"98"}）
        :param conditions: 修改条件（如{"学生姓名":"张三"}）
        :return: 修改的行数
        """
        if not new_data:
            print("<$> 要修改的数据不能为空")
            return 0
        if not conditions:
            print("<$> 修改条件不能为空（防止改所有数据）")
            return 0

        set_clause = ",".join([f"`{k}`=?" for k in new_data.keys()])
        where_clause = " AND ".join([f"`{k}`=?" for k in conditions.keys()])
        sql = f"UPDATE `{table_name}` SET {set_clause} WHERE {where_clause}"

        params = list(new_data.values()) + list(conditions.values())
        cursor = self._get_cursor()
        try:
            cursor.execute(sql, params)
            self.conn.commit()
            print(f"<$> 成功修改 {cursor.rowcount} 条数据")
            return cursor.rowcount
        except Exception as e:
            self.conn.rollback()
            print(f"<$> 修改数据失败：{e}")
            return 0

    # ===================== 删除数据 =====================
    def delete_data(self, table_name: str, conditions: dict):
        """
        删除数据
        :param table_name: 表名
        :param conditions: 删除条件（如{"学生姓名":"张三"}）
        :return: 删除的行数
        """

        where_clause = " AND ".join([f"`{k}`=?" for k in conditions.keys()])
        sql = f"DELETE FROM `{table_name}` WHERE {where_clause}"

        cursor = self._get_cursor()
        try:
            cursor.execute(sql, list(conditions.values()))
            self.conn.commit()
            print(f"<$> 成功删除 {cursor.rowcount} 条数据")
            return cursor.rowcount
        except Exception as e:
            self.conn.rollback()
            print(f"<$> 删除数据失败：{e}")
            return 0

#########################SQL####################

#============================Leaf=======================================
class Leaf:
    def __init__(self,user_name: str):
        """
        Leaf是最底层的数据结构，用于存储打分员每周的分数
        :param user_name: 用户名
        """
        import json
        import os

        def read_config(file_path='config.json'):
            """
            读取 config.json 配置文件并返回其内容。

            参数:
                file_path (str): 配置文件路径，默认为 'config.json'

            返回:
                dict: JSON 文件解析后的 Python 字典

            异常:
                FileNotFoundError: 如果文件不存在
                json.JSONDecodeError: 如果文件内容不是合法的 JSON
            """
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"配置文件 '{file_path}' 不存在。")

            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        def spawn_class(grade: int = 1, max_class: int = 6) -> list:
            results = []
            for i in range(max_class):
                results.append(f"{grade}0{i+1}")
            return results

        self.user_name = user_name
        self.data = []
        self.__data_sum: int = len(self.data)
        self.__location: str = f"{user_name}"
        _grade = read_config()["grade"]
        _max_class = read_config()["m_number"]

        self.classes = spawn_class(grade = _grade, max_class = _max_class)
    @property
    def data_sum(self) :
        self.__data_sum = len(self.data)
        return self.__data_sum
    @data_sum.setter
    def data_sum(self,data_sum):
        self.data_sum = data_sum
    def add_data(self,data:str):
        if data or (data.isdigit()):
            if self.data_sum < len(self.classes) * 5 + 1:       # 一周有5天上学
                self.data.append(data)
                print(f"<$>数据{data}添加成功")
        else:
            ascii_red = "\033[31m"
            ascii_white = "\033[37m"

            print(f"{ascii_red}<<<   !!!   >>>输入不合规{data}{ascii_white}")
    def delete_data(self, conditions: dict):
        if not conditions:
            try:
                sql: MyEasySQLite = MyEasySQLite(f"Leaf\\{self.user_name}\\{get_time()['y']}-{get_time()['m']}.db")
                table_name = f"{get_time()['d']}"
                sql.create_table(table_name, ["mouth","class", "score"])
                sql.delete_data(table_name, conditions)
            except sqlite3.Error as e:
                print(e)
    def save(self) -> None:
        """
        保存这个Leaf到 ".\\Leaf\\ {user_name}\\{time}.db"文件中
        """
        create_folders(f"Leaf/{self.__location}")
        sql: MyEasySQLite = MyEasySQLite(f"Leaf/{self.__location}/{get_time()['y']}-{get_time()['m']}.db")
        table_name = f"{get_time()['d']}"
        sql.create_table(table_name, ["class", "day", "score"])
        k = 0
        for i in self.classes:
            for j in range(5):
                sql.add_data(table_name, {"day": f"{j + 1}", "class": f"{i}", "score": self.data[k]})
                k += 1
        sql.close()
        print(f"保存至{get_time()['d']}")

