import os
import json
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon, QColor
from PyQt5.QtWidgets import (QDialog, QTabWidget, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QLineEdit, QComboBox, QCheckBox, QPushButton, 
                             QSpinBox, QColorDialog, QMessageBox, QDateEdit, QGroupBox,
                             QFormLayout, QListWidget, QListWidgetItem, QFrame)
from qt_material import list_themes
from loguru import logger

class SettingsDialog(QDialog):
    """设置窗口类"""
    def __init__(self, config, timetable, parent=None):
        super().__init__(parent)
        self.config = config
        self.timetable = timetable
        self.original_config = config.config.copy()  # 保存原始配置，用于取消操作
        
        # 设置窗口基本属性
        self.setWindowTitle("设置")
        self.setMinimumSize(600, 500)
        self.setWindowIcon(QIcon(os.path.join("assets", "icon.png")))
        
        # 初始化UI
        self.init_ui()
        
        # 加载当前配置
        self.load_config()
        
        logger.info("设置窗口已打开")
    
    def init_ui(self):
        """初始化UI组件"""
        # 主布局
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(10, 10, 10, 10)
        
        # 创建选项卡
        self.tab_widget = QTabWidget()
        
        # 创建各个设置页面
        self.general_tab = self.create_general_tab()
        self.timetable_tab = self.create_timetable_tab()
        self.appearance_tab = self.create_appearance_tab()
        self.notification_tab = self.create_notification_tab()
        self.weather_tab = self.create_weather_tab()
        
        # 添加选项卡
        self.tab_widget.addTab(self.general_tab, "常规")
        self.tab_widget.addTab(self.timetable_tab, "课表")
        self.tab_widget.addTab(self.appearance_tab, "外观")
        self.tab_widget.addTab(self.notification_tab, "通知")
        self.tab_widget.addTab(self.weather_tab, "天气")
        
        # 添加按钮区域
        self.button_layout = QHBoxLayout()
        self.button_layout.setContentsMargins(0, 10, 0, 0)
        
        self.reset_button = QPushButton("重置")
        self.reset_button.clicked.connect(self.reset_settings)
        
        self.cancel_button = QPushButton("取消")
        self.cancel_button.clicked.connect(self.reject)
        
        self.save_button = QPushButton("保存")
        self.save_button.clicked.connect(self.save_settings)
        self.save_button.setDefault(True)
        
        self.button_layout.addWidget(self.reset_button)
        self.button_layout.addStretch(1)
        self.button_layout.addWidget(self.cancel_button)
        self.button_layout.addWidget(self.save_button)
        
        # 添加到主布局
        self.main_layout.addWidget(self.tab_widget)
        self.main_layout.addLayout(self.button_layout)
    
    def create_general_tab(self):
        """创建常规设置选项卡"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # 基本设置组
        basic_group = QGroupBox("基本设置")
        basic_layout = QFormLayout(basic_group)
        
        # 语言选择
        self.language_combo = QComboBox()
        self.language_combo.addItem("简体中文", "zh_CN")
        self.language_combo.addItem("English", "en_US")
        basic_layout.addRow("语言:", self.language_combo)
        
        # 启动选项
        self.start_with_system = QCheckBox("开机自启动")
        basic_layout.addRow("", self.start_with_system)
        
        self.minimize_to_tray = QCheckBox("关闭窗口时最小化到托盘")
        basic_layout.addRow("", self.minimize_to_tray)
        
        # 添加到主布局
        layout.addWidget(basic_group)
        
        # 数据管理组
        data_group = QGroupBox("数据管理")
        data_layout = QVBoxLayout(data_group)
        
        # 导入导出按钮
        import_export_layout = QHBoxLayout()
        
        self.import_button = QPushButton("导入配置")
        self.import_button.clicked.connect(self.import_config)
        
        self.export_button = QPushButton("导出配置")
        self.export_button.clicked.connect(self.export_config)
        
        import_export_layout.addWidget(self.import_button)
        import_export_layout.addWidget(self.export_button)
        
        data_layout.addLayout(import_export_layout)
        
        # 添加到主布局
        layout.addWidget(data_group)
        layout.addStretch(1)
        
        return tab
    
    def create_timetable_tab(self):
        """创建课表设置选项卡"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # 学期设置组
        semester_group = QGroupBox("学期设置")
        semester_layout = QFormLayout(semester_group)
        
        # 学期开始日期
        self.semester_start_date = QDateEdit()
        self.semester_start_date.setCalendarPopup(True)
        semester_layout.addRow("学期开始日期:", self.semester_start_date)
        
        # 当前周数
        self.current_week_spin = QSpinBox()
        self.current_week_spin.setMinimum(1)
        self.current_week_spin.setMaximum(30)
        semester_layout.addRow("当前周数:", self.current_week_spin)
        
        # 总周数
        self.total_weeks_spin = QSpinBox()
        self.total_weeks_spin.setMinimum(1)
        self.total_weeks_spin.setMaximum(30)
        semester_layout.addRow("总周数:", self.total_weeks_spin)
        
        # 添加到主布局
        layout.addWidget(semester_group)
        
        # 时间段设置组
        time_slots_group = QGroupBox("时间段设置")
        time_slots_layout = QVBoxLayout(time_slots_group)
        
        # 时间段列表
        self.time_slots_list = QListWidget()
        self.time_slots_list.setSelectionMode(QListWidget.SingleSelection)
        
        # 时间段编辑按钮
        slots_buttons_layout = QHBoxLayout()
        
        self.add_slot_button = QPushButton("添加")
        self.add_slot_button.clicked.connect(self.add_time_slot)
        
        self.edit_slot_button = QPushButton("编辑")
        self.edit_slot_button.clicked.connect(self.edit_time_slot)
        
        self.remove_slot_button = QPushButton("删除")
        self.remove_slot_button.clicked.connect(self.remove_time_slot)
        
        slots_buttons_layout.addWidget(self.add_slot_button)
        slots_buttons_layout.addWidget(self.edit_slot_button)
        slots_buttons_layout.addWidget(self.remove_slot_button)
        
        time_slots_layout.addWidget(self.time_slots_list)
        time_slots_layout.addLayout(slots_buttons_layout)
        
        # 添加到主布局
        layout.addWidget(time_slots_group)
        
        return tab
    
    def create_appearance_tab(self):
        """创建外观设置选项卡"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # 主题设置组
        theme_group = QGroupBox("主题设置")
        theme_layout = QFormLayout(theme_group)
        
        # 主题选择
        self.theme_combo = QComboBox()
        for theme in list_themes():
            self.theme_combo.addItem(theme, theme)
        theme_layout.addRow("主题:", self.theme_combo)
        
        # 暗色模式
        self.dark_mode = QCheckBox("暗色模式")
        theme_layout.addRow("", self.dark_mode)
        
        # 添加到主布局
        layout.addWidget(theme_group)
        
        # 颜色设置组
        color_group = QGroupBox("颜色设置")
        color_layout = QFormLayout(color_group)
        
        # 主色调
        self.primary_color_button = QPushButton()
        self.primary_color_button.setFixedSize(30, 30)
        self.primary_color_button.clicked.connect(lambda: self.choose_color("primary"))
        color_layout.addRow("主色调:", self.primary_color_button)
        
        # 强调色
        self.accent_color_button = QPushButton()
        self.accent_color_button.setFixedSize(30, 30)
        self.accent_color_button.clicked.connect(lambda: self.choose_color("accent"))
        color_layout.addRow("强调色:", self.accent_color_button)
        
        # 添加到主布局
        layout.addWidget(color_group)
        layout.addStretch(1)
        
        return tab
    
    def create_notification_tab(self):
        """创建通知设置选项卡"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # 通知设置组
        notification_group = QGroupBox("通知设置")
        notification_layout = QFormLayout(notification_group)
        
        # 启用通知
        self.enable_notification = QCheckBox("启用课程提醒")
        notification_layout.addRow("", self.enable_notification)
        
        # 提前提醒时间
        self.advance_time_spin = QSpinBox()
        self.advance_time_spin.setMinimum(1)
        self.advance_time_spin.setMaximum(60)
        self.advance_time_spin.setSuffix(" 分钟")
        notification_layout.addRow("提前提醒时间:", self.advance_time_spin)
        
        # 启用提示音
        self.enable_sound = QCheckBox("启用提示音")
        notification_layout.addRow("", self.enable_sound)
        
        # 添加到主布局
        layout.addWidget(notification_group)
        layout.addStretch(1)
        
        return tab
    
    def create_weather_tab(self):
        """创建天气设置选项卡"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # 天气设置组
        weather_group = QGroupBox("天气设置")
        weather_layout = QFormLayout(weather_group)
        
        # 启用天气
        self.enable_weather = QCheckBox("显示天气信息")
        weather_layout.addRow("", self.enable_weather)
        
        # 城市设置
        self.city_edit = QLineEdit()
        weather_layout.addRow("城市名称:", self.city_edit)
        
        # 城市代码
        self.city_code_edit = QLineEdit()
        weather_layout.addRow("城市代码:", self.city_code_edit)
        
        # 更新间隔
        self.update_interval_spin = QSpinBox()
        self.update_interval_spin.setMinimum(10)
        self.update_interval_spin.setMaximum(1440)
        self.update_interval_spin.setSuffix(" 分钟")
        weather_layout.addRow("更新间隔:", self.update_interval_spin)
        
        # 添加到主布局
        layout.addWidget(weather_group)
        layout.addStretch(1)
        
        return tab
    
    def load_config(self):
        """加载当前配置到UI"""
        # 常规设置
        language = self.config.get('language', 'zh_CN')
        index = self.language_combo.findData(language)
        if index >= 0:
            self.language_combo.setCurrentIndex(index)
        
        self.start_with_system.setChecked(self.config.get('start_with_system', False))
        self.minimize_to_tray.setChecked(self.config.get('minimize_to_tray', True))
        
        # 课表设置
        start_date_str = self.config.get('timetable.semester_start_date')
        if start_date_str:
            start_date = QtCore.QDate.fromString(start_date_str, "yyyy-MM-dd")
            self.semester_start_date.setDate(start_date)
        
        self.current_week_spin.setValue(self.config.get('timetable.current_week', 1))
        self.total_weeks_spin.setValue(self.config.get('timetable.total_weeks', 20))