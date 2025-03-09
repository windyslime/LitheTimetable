import sys
import os
import datetime
import json
import platform
from pathlib import Path

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt, QTimer, QDateTime, QDate, QTime, QSize
from PyQt5.QtGui import QIcon, QColor, QFont, QPixmap
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QLabel, QPushButton, QSystemTrayIcon, QMenu, QAction
from qt_material import apply_stylesheet
from loguru import logger

from config import Config
from timetable import TimeTable
from weather import WeatherService
from notification import NotificationService
from plugin import PluginManager

# 设置高DPI缩放
QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)

class MainWindow(QMainWindow):
    """主窗口类"""
    def __init__(self):
        super().__init__()
        
        # 初始化配置
        self.config = Config()
        
        # 设置窗口基本属性
        self.setWindowTitle("LitheTimetable")
        self.setMinimumSize(800, 600)
        
        # 初始化服务
        self.weather_service = WeatherService(self.config)
        self.notification_service = NotificationService(self.config)
        
        # 加载课表
        self.timetable = TimeTable(self.config)
        
        # 初始化插件管理器
        self.plugin_manager = PluginManager(self.config)
        self.plugin_manager.load_plugins()
        
        # 初始化UI
        self.init_ui()
        
        # 初始化系统托盘
        self.init_tray()
        
        # 加载课表数据
        self.load_timetable()
        
        # 更新天气
        self.update_weather()
        
        # 初始化定时器
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_time)
        self.timer.start(1000)  # 每秒更新一次
        
        logger.info("应用程序启动完成")
    
    def init_ui(self):
        """初始化UI组件"""
        # 创建中央部件
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        # 主布局
        self.main_layout = QtWidgets.QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(16, 16, 16, 16)
        self.main_layout.setSpacing(16)
        
        # 顶部信息栏
        self.top_bar = QtWidgets.QHBoxLayout()
        self.top_bar.setContentsMargins(0, 0, 0, 0)
        self.top_bar.setSpacing(16)
        
        # 时间日期显示
        self.time_label = QLabel()
        self.time_label.setAlignment(Qt.AlignCenter)
        self.time_label.setStyleSheet("font-size: 24px; font-weight: 500; color: #212121;")
        
        self.date_label = QLabel()
        self.date_label.setAlignment(Qt.AlignCenter)
        self.date_label.setStyleSheet("font-size: 14px; font-weight: 400; color: #757575;")
        
        # 天气信息
        self.weather_widget = QWidget()
        self.weather_widget.setStyleSheet("background-color: #ffffff; border-radius: 8px; padding: 8px;")
        self.weather_layout = QtWidgets.QHBoxLayout(self.weather_widget)
        self.weather_layout.setContentsMargins(8, 8, 8, 8)
        self.weather_layout.setSpacing(8)
        
        self.weather_icon = QLabel()
        self.weather_icon.setFixedSize(32, 32)
        
        self.weather_info = QLabel("正在获取天气...")
        self.weather_info.setStyleSheet("font-size: 14px; font-weight: 400; color: #212121;")
        
        self.weather_layout.addWidget(self.weather_icon)
        self.weather_layout.addWidget(self.weather_info)
        
        # 添加到顶部栏
        self.time_date_widget = QWidget()
        self.time_date_layout = QtWidgets.QVBoxLayout(self.time_date_widget)
        self.time_date_layout.setContentsMargins(0, 0, 0, 0)
        self.time_date_layout.addWidget(self.time_label)
        self.time_date_layout.addWidget(self.date_label)
        
        self.top_bar.addWidget(self.time_date_widget)
        self.top_bar.addStretch(1)
        self.top_bar.addWidget(self.weather_widget)
        
        # 课表区域
        self.timetable_widget = QWidget()
        self.timetable_widget.setStyleSheet("background-color: #ffffff; border-radius: 8px; padding: 16px;")
        self.timetable_layout = QtWidgets.QVBoxLayout(self.timetable_widget)
        self.timetable_layout.setContentsMargins(0, 0, 0, 0)
        self.timetable_layout.setSpacing(16)
        
        # 课表标题
        self.timetable_title = QLabel("本周课表")
        self.timetable_title.setStyleSheet("font-size: 18px; font-weight: 500; color: #212121; margin-bottom: 8px;")
        
        # 底部状态栏
        self.status_bar = QtWidgets.QHBoxLayout()
        self.status_bar.setContentsMargins(0, 0, 0, 0)
        self.status_bar.setSpacing(16)
        
        self.status_label = QLabel("就绪")
        self.status_label.setStyleSheet("font-size: 12px; font-weight: 400; color: #757575;")
        
        self.settings_button = QPushButton("设置")
        self.settings_button.setStyleSheet("QPushButton { background-color: #2196F3; color: white; border-radius: 4px; padding: 8px 16px; } QPushButton:hover { background-color: #1976D2; }")
        
        self.plugins_button = QPushButton("插件")
        self.plugins_button.setStyleSheet("QPushButton { background-color: #2196F3; color: white; border-radius: 4px; padding: 8px 16px; } QPushButton:hover { background-color: #1976D2; }")
        self.plugins_button.clicked.connect(self.open_plugin_settings)
        
        self.status_bar.addWidget(self.status_label)
        self.status_bar.addStretch(1)
        self.status_bar.addWidget(self.plugins_button)
        self.status_bar.addWidget(self.settings_button)
        
        # 添加所有组件到主布局
        self.main_layout.addLayout(self.top_bar)
        self.main_layout.addWidget(self.timetable_widget, 1)  # 1表示拉伸因子
        self.main_layout.addLayout(self.status_bar)
        
        # 初始更新时间
        self.update_time()
    
    def init_tray(self):
        """初始化系统托盘"""
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(QIcon(os.path.join("assets", "icon.png")))
        
        # 创建托盘菜单
        tray_menu = QMenu()
        
        show_action = QAction("显示主窗口", self)
        show_action.triggered.connect(self.show)
        
        settings_action = QAction("设置", self)
        settings_action.triggered.connect(self.open_settings)
        
        exit_action = QAction("退出", self)
        exit_action.triggered.connect(self.close_application)
        
        tray_menu.addAction(show_action)
        tray_menu.addAction(settings_action)
        tray_menu.addSeparator()
        tray_menu.addAction(exit_action)
        
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.activated.connect(self.tray_icon_activated)
        self.tray_icon.show()
    
    def tray_icon_activated(self, reason):
        """托盘图标激活事件"""
        if reason == QSystemTrayIcon.DoubleClick:
            self.show()
            self.activateWindow()
    
    def update_time(self):
        """更新时间显示"""
        current_datetime = QDateTime.currentDateTime()
        
        # 更新时间标签
        self.time_label.setText(current_datetime.toString("HH:mm:ss"))
        
        # 更新日期标签
        date_str = current_datetime.toString("yyyy年MM月dd日 dddd")
        self.date_label.setText(date_str)
        
        # 检查是否需要更新课表（例如，在午夜）
        if current_datetime.time().hour() == 0 and current_datetime.time().minute() == 0 and current_datetime.time().second() == 0:
            self.load_timetable()
        
        # 检查是否需要发送课程提醒
        self.check_class_notifications()
    
    def update_weather(self):
        """更新天气信息"""
        weather_data = self.weather_service.get_weather()
        if weather_data:
            self.weather_info.setText(f"{weather_data['temperature']}°C {weather_data['condition']}")
            
            # 设置天气图标
            icon_path = os.path.join("assets", "weather", f"{weather_data['icon']}.png")
            if os.path.exists(icon_path):
                self.weather_icon.setPixmap(QPixmap(icon_path).scaled(32, 32, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        
        # 设置定时更新天气（每小时）
        QTimer.singleShot(3600000, self.update_weather)
    
    def load_timetable(self):
        """加载课表"""
        # 清除现有课表
        for i in reversed(range(self.timetable_layout.count())):
            if i > 0:  # 保留标题
                widget = self.timetable_layout.itemAt(i).widget()
                if widget:
                    widget.deleteLater()
        
        # 获取当前周的课表
        current_week = self.timetable.get_current_week()
        self.timetable_title.setText(f"第{current_week}周课表")
        
        # 创建课表网格
        timetable_grid = QtWidgets.QGridLayout()
        
        # 添加表头
        weekdays = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
        for i, day in enumerate(weekdays):
            header = QLabel(day)
            header.setAlignment(Qt.AlignCenter)
            header.setStyleSheet("font-weight: bold; padding: 5px;")
            timetable_grid.addWidget(header, 0, i+1)
        
        # 添加时间段
        time_slots = self.timetable.get_time_slots()
        for i, slot in enumerate(time_slots):
            time_label = QLabel(f"{slot['start']}-{slot['end']}")
            time_label.setAlignment(Qt.AlignCenter)
            time_label.setStyleSheet("font-weight: bold; padding: 5px;")
            timetable_grid.addWidget(time_label, i+1, 0)
        
        # 填充课程
        courses = self.timetable.get_weekly_courses(current_week)
        for course in courses:
            day = course['day']  # 0-6 表示周一到周日
            slot = course['slot']  # 从0开始的时间段索引
            
            course_widget = self.create_course_widget(course)
            timetable_grid.addWidget(course_widget, slot+1, day+1)
        
        # 添加空白单元格
        for row in range(1, len(time_slots)+1):
            for col in range(1, 8):
                if timetable_grid.itemAtPosition(row, col) is None:
                    empty = QWidget()
                    empty.setStyleSheet("background-color: rgba(0, 0, 0, 0.05); border-radius: 5px;")
                    timetable_grid.addWidget(empty, row, col)
        
        # 将网格添加到课表布局
        grid_widget = QWidget()
        grid_widget.setLayout(timetable_grid)
        self.timetable_layout.addWidget(grid_widget)
        
        logger.info(f"已加载第{current_week}周课表")
    
    def create_course_widget(self, course):
        """创建课程卡片"""
        widget = QWidget()
        widget.mousePressEvent = lambda event: self.edit_course(course)
        layout = QtWidgets.QVBoxLayout(widget)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # 设置背景颜色
        color = course.get('color', '#3f51b5')  # 默认使用蓝色
        widget.setStyleSheet(f"background-color: {color}; color: white; border-radius: 5px;")
        
        # 课程名称
        name_label = QLabel(course['name'])
        name_label.setAlignment(Qt.AlignCenter)
        name_label.setWordWrap(True)
        name_label.setStyleSheet("font-weight: bold; font-size: 12px;")
        
        # 教室
        location_label = QLabel(course.get('location', ''))
        location_label.setAlignment(Qt.AlignCenter)
        location_label.setStyleSheet("font-size: 10px;")
        
        # 教师
        teacher_label = QLabel(course.get('teacher', ''))
        teacher_label.setAlignment(Qt.AlignCenter)
        teacher_label.setStyleSheet("font-size: 10px;")
        
        layout.addWidget(name_label)
        layout.addWidget(location_label)
        layout.addWidget(teacher_label)
        
        return widget
    
    def check_class_notifications(self):
        """检查是否需要发送课程提醒"""
        self.notification_service.check_upcoming_classes(self.timetable)
    
    def open_settings(self):
        """打开设置窗口"""
        from settings import SettingsDialog
        settings_dialog = SettingsDialog(self.config, self.timetable, self)
        if settings_dialog.exec_():
            # 如果用户点击了保存按钮，重新加载配置
            self.load_timetable()
            self.update_weather()
            
            # 应用新主题（如果有变化）
            theme = self.config.get('appearance.theme', 'light_blue')
            apply_stylesheet(QApplication.instance(), theme=f'{theme}.xml')
            
        logger.info("设置窗口已关闭")
    
    def open_plugin_settings(self):
        """打开插件设置窗口"""
        from plugin_settings import PluginSettingsDialog
        plugin_dialog = PluginSettingsDialog(self.plugin_manager, self)
        if plugin_dialog.exec_():
            # 重新加载插件
            self.plugin_manager.load_plugins()
        logger.info("插件设置窗口已关闭")
    
    def close_application(self):
        """关闭应用程序"""
        logger.info("应用程序关闭")
        QApplication.quit()
    
    def edit_course(self, course):
        """编辑课程"""
        from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QColorDialog
        
        dialog = QDialog(self)
        dialog.setWindowTitle("编辑课程")
        layout = QVBoxLayout(dialog)
        
        # 课程名称
        layout.addWidget(QLabel("课程名称:"))
        name_edit = QLineEdit(course['name'])
        layout.addWidget(name_edit)
        
        # 地点
        layout.addWidget(QLabel("地点:"))
        location_edit = QLineEdit(course.get('location', ''))
        layout.addWidget(location_edit)
        
        # 颜色选择
        layout.addWidget(QLabel("课程颜色:"))
        color_button = QPushButton("选择颜色")
        color_button.clicked.connect(lambda: self.choose_course_color(course, color_button))
        layout.addWidget(color_button)
        
        # 保存按钮
        save_button = QPushButton("保存")
        save_button.clicked.connect(lambda: self.save_course(course, name_edit.text(), location_edit.text(), dialog))
        layout.addWidget(save_button)
        
        dialog.exec_()

    def choose_course_color(self, course, button):
        """选择课程颜色"""
        color = QColorDialog.getColor()
        if color.isValid():
            course['color'] = color.name()
            button.setStyleSheet(f"background-color: {color.name()}; color: {'white' if color.lightness() < 128 else 'black'};")

    def add_course(self, day, slot):
        """添加新课程"""
        from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QColorDialog
        
        dialog = QDialog(self)
        dialog.setWindowTitle("添加课程")
        layout = QVBoxLayout(dialog)
        
        # 课程名称
        layout.addWidget(QLabel("课程名称:"))
        name_edit = QLineEdit()
        layout.addWidget(name_edit)
        
        # 地点
        layout.addWidget(QLabel("地点:"))
        location_edit = QLineEdit()
        layout.addWidget(location_edit)
        
        # 教师
        layout.addWidget(QLabel("教师:"))
        teacher_edit = QLineEdit()
        layout.addWidget(teacher_edit)
        
        # 颜色选择
        layout.addWidget(QLabel("课程颜色:"))
        color_button = QPushButton("选择颜色")
        color_button.clicked.connect(lambda: self.choose_course_color({'color': '#3f51b5'}, color_button))
        layout.addWidget(color_button)
        
        # 保存按钮
        save_button = QPushButton("保存")
        save_button.clicked.connect(lambda: self.save_new_course(day, slot, name_edit.text(), location_edit.text(), teacher_edit.text(), dialog))
        layout.addWidget(save_button)
        
        dialog.exec_()

    def save_new_course(self, day, slot, name, location, teacher, dialog):
        """保存新课程"""
        new_course = {
            'day': day,
            'slot': slot,
            'name': name,
            'location': location,
            'teacher': teacher,
            'color': '#3f51b5'
        }
        self.timetable.add_course(new_course)
        self.load_timetable()
        dialog.close()
    
    def save_course(self, course, name, location, dialog):
        """保存课程修改"""
        course['name'] = name
        course['location'] = location
        dialog.close()
        self.load_timetable()

    def closeEvent(self, event):
        """窗口关闭事件"""
        if self.config.get('minimize_to_tray', True):
            event.ignore()
            self.hide()
        else:
            event.accept()
            self.close_application()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # 设置日志
    logger.add("logs/app_{time}.log", rotation="10 MB", level="INFO")
    logger.info("应用程序启动")
    
    # 创建必要的目录
    os.makedirs("assets", exist_ok=True)
    os.makedirs("assets/weather", exist_ok=True)
    os.makedirs("data", exist_ok=True)
    os.makedirs("logs", exist_ok=True)
    
    # 应用Material样式
    apply_stylesheet(app, theme='light_blue.xml')
    
    # 创建并显示主窗口
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec_())


    def edit_course(self, course):
        """编辑课程"""
        from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QColorDialog
        
        dialog = QDialog(self)
        dialog.setWindowTitle("编辑课程")
        layout = QVBoxLayout(dialog)
        
        # 课程名称
        layout.addWidget(QLabel("课程名称:"))
        name_edit = QLineEdit(course['name'])
        layout.addWidget(name_edit)
        
        # 地点
        layout.addWidget(QLabel("地点:"))
        location_edit = QLineEdit(course.get('location', ''))
        layout.addWidget(location_edit)
        
        # 颜色选择
        layout.addWidget(QLabel("课程颜色:"))
        color_button = QPushButton("选择颜色")
        color_button.clicked.connect(lambda: self.choose_course_color(course, color_button))
        layout.addWidget(color_button)
        
        # 保存按钮
        save_button = QPushButton("保存")
        save_button.clicked.connect(lambda: self.save_course(course, name_edit.text(), location_edit.text(), dialog))
        layout.addWidget(save_button)
        
        dialog.exec_()

    def choose_course_color(self, course, button):
        """选择课程颜色"""
        color = QColorDialog.getColor()
        if color.isValid():
            course['color'] = color.name()
            button.setStyleSheet(f"background-color: {color.name()}; color: {'white' if color.lightness() < 128 else 'black'};")

    def add_course(self, day, slot):
        """添加新课程"""
        from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QColorDialog
        
        dialog = QDialog(self)
        dialog.setWindowTitle("添加课程")
        layout = QVBoxLayout(dialog)
        
        # 课程名称
        layout.addWidget(QLabel("课程名称:"))
        name_edit = QLineEdit()
        layout.addWidget(name_edit)
        
        # 地点
        layout.addWidget(QLabel("地点:"))
        location_edit = QLineEdit()
        layout.addWidget(location_edit)
        
        # 教师
        layout.addWidget(QLabel("教师:"))
        teacher_edit = QLineEdit()
        layout.addWidget(teacher_edit)
        
        # 颜色选择
        layout.addWidget(QLabel("课程颜色:"))
        color_button = QPushButton("选择颜色")
        color_button.clicked.connect(lambda: self.choose_course_color({'color': '#3f51b5'}, color_button))
        layout.addWidget(color_button)
        
        # 保存按钮
        save_button = QPushButton("保存")
        save_button.clicked.connect(lambda: self.save_new_course(day, slot, name_edit.text(), location_edit.text(), teacher_edit.text(), dialog))
        layout.addWidget(save_button)
        
        dialog.exec_()

    def save_new_course(self, day, slot, name, location, teacher, dialog):
        """保存新课程"""
        new_course = {
            'day': day,
            'slot': slot,
            'name': name,
            'location': location,
            'teacher': teacher,
            'color': '#3f51b5'
        }
        self.timetable.add_course(new_course)
        self.load_timetable()
        dialog.close()
        
    def save_course(self, course, name, location, dialog):
        """保存课程修改"""
        course['name'] = name
        course['location'] = location
        dialog.close()
        self.load_timetable()