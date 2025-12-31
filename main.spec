# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[
    # openpyxl 及其常见子模块（必须全）
    'openpyxl',
    'openpyxl.utils',
    'openpyxl.workbook',
    'openpyxl.worksheet',
    'openpyxl.cell',
    'openpyxl.styles',
    'openpyxl.reader.excel',
    'openpyxl.writer.excel',
    'et_xmlfile',          # ⚠️ 关键！openpyxl 的底层依赖，常被遗漏

    # 加密库（pycryptodome）
    'Crypto.Cipher.AES',
    'Crypto.Util.Padding',
    'Crypto.Cipher',       # 有时需要父模块
    'Crypto.Util',         # 同上

    # 图像处理（Pillow）
    'PIL',
    'PIL.Image',
    'PIL.ImageTk',
    'PIL._imaging',        # 某些系统需要这个 C 扩展模块

    # GUI（tkinter）
    'tkinter',
    'tkinter.ttk',
    'tkinter.messagebox',  # 如果你用了 messagebox
    'tkinter.filedialog',  # 如果你用了文件选择对话框

    # 数据库
    'sqlite3',
    'sqlite3.dbapi2',      # 某些 PyInstaller 版本需要

    # 其他（根据你代码中的 import 补充）
    'base64',              # 标准库，通常不需要，但保险起见可加
    'warnings',            # 同上
    'datetime',
    'json',
    'ast'
],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='main',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
