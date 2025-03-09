import os
import json
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
                             QListWidget, QListWidgetItem, QWidget, QCheckBox,
                             QStackedWidget, QScrollArea, QFrame, QMessageBox)
from loguru import logger

class PluginSettingsDialog(QDialog):
    """插件设置窗口"""
    def __init__(self, plugin_manager, parent=None):
        super().__init__(parent)
        self.plugin_manager = plugin_manager
        
        # 设置窗口基本属性
        self.setWindowTitle("插件管理")
        self.setMinimumSize(700, 500)
        self.setWindowIcon(QIcon(os.path.join("assets", "icon.png")))
        
        # 初始化UI
        self.init_ui()
        
        # 加载插件列表
        self.load_plugins()
        
        logger.info("插件设置窗口已打开")
    
    def init_ui(self):
        """初始化UI组件"""
        # 主布局
        self.main_layout = QHBoxLayout(self)
        self.main_layout.setContentsMargins(10, 10, 10, 10)
        
        # 左侧插件列表
        self.left_panel = QWidget()
        self.left_layout = QVBoxLayout(self.left_panel)
        
        self.plugin_list_label = QLabel("可用插件")
        self.plugin_list_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        
        self.plugin_list = QListWidget()
        self.plugin_list.setMinimumWidth(200)
        self.plugin_list.currentRowChanged.connect(self.on_plugin_selected)
        
        self.left_layout.addWidget(self.plugin_list_label)
        self.left_layout.addWidget(self.plugin_list)
        
        # 右侧插件详情和设置
        self.right_panel = QWidget()
        self.right_layout = QVBoxLayout(self.right_panel)
        
        # 插件详情区域
        self.plugin_detail = QWidget()
        self.detail_layout = QVBoxLayout(self.plugin_detail)
        
        self.plugin_name = QLabel("")
        self.plugin_name.setStyleSheet("font-weight: bold; font-size: 16px;")
        
        self.plugin_version = QLabel("")
        self.plugin_author = QLabel("")
        self.plugin_description = QLabel("")
        self.plugin_description.setWordWrap(True)
        
        self.enable_plugin = QCheckBox("启用此插件")
        self.enable_plugin.stateChanged.connect(self.on_enable_changed)
        
        self.detail_layout.addWidget(self.plugin_name)
        self.detail_layout.addWidget(self.plugin_version)
        self.detail_layout.addWidget(self.plugin_author)
        self.detail_layout.addWidget(self.plugin_description)
        self.detail_layout.addWidget(self.enable_plugin)
        
        # 插件设置区域
        self.settings_label = QLabel("插件设置")
        self.settings_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        
        self.settings_container = QScrollArea()
        self.settings_container.setWidgetResizable(True)
        self.settings_container.setFrameShape(QFrame.NoFrame)
        
        self.settings_widget = QStackedWidget()
        self.settings_container.setWidget(self.settings_widget)
        
        # 添加到右侧布局
        self.right_layout.addWidget(self.plugin_detail)
        self.right_layout.addWidget(self.settings_label)
        self.right_layout.addWidget(self.settings_container, 1)  # 1表示拉伸因子
        
        # 底部按钮区域
        self.button_layout = QHBoxLayout()
        
        self.refresh_button = QPushButton("刷新")
        self.refresh_button.clicked.connect(self.load_plugins)
        
        self.close_button = QPushButton("关闭")
        self.close_button.clicked.connect(self.accept)
        self.close_button.setDefault(True)
        
        self.button_layout.addWidget(self.refresh_button)
        self.button_layout.addStretch(1)
        self.button_layout.addWidget(self.close_button)
        
        # 添加到主布局
        self.main_layout.addWidget(self.left_panel, 1)  # 1表示拉伸因子
        self.main_layout.addWidget(self.right_panel, 2)  # 2表示拉伸因子
        
        # 添加底部按钮
        self.main_layout.addLayout(self.button_layout)
    
    def load_plugins(self):
        """加载插件列表"""
        self.plugin_list.clear()
        
        # 获取可用插件
        available_plugins = self.plugin_manager.discover_plugins()
        
        if not available_plugins:
            # 如果没有可用插件，显示提示
            item = QListWidgetItem("没有可用插件")
            item.setFlags(item.flags() & ~Qt.ItemIsEnabled)  # 禁用该项
            self.plugin_list.addItem(item)
            return
        
        # 添加到列表
        for plugin in available_plugins:
            item = QListWidgetItem(plugin['name'])
            item.setData(Qt.UserRole, plugin)  # 存储插件数据
            self.plugin_list.addItem(item)
        
        # 选择第一个插件
        if self.plugin_list.count() > 0:
            self.plugin_list.setCurrentRow(0)
    
    def on_plugin_selected(self, row):
        """当选择插件时"""
        if row < 0 or self.plugin_list.count() == 0:
            # 清空详情
            self.plugin_name.setText("")
            self.plugin_version.setText("")
            self.plugin_author.setText("")
            self.plugin_description.setText("")
            self.enable_plugin.setChecked(False)
            self.enable_plugin.setEnabled(False)
            return
        
        # 获取选中的插件数据
        item = self.plugin_list.item(row)
        plugin_data = item.data(Qt.UserRole)
        
        # 更新详情
        self.plugin_name.setText(plugin_data['name'])
        self.plugin_version.setText(f"版本: {plugin_data['version']}")
        self.plugin_author.setText(f"作者: {plugin_data['author']}")
        self.plugin_description.setText(plugin_data['description'])
        
        # 更新启用状态
        self.enable_plugin.setChecked(plugin_data['enabled'])
        self.enable_plugin.setEnabled(True)
        
        # 加载插件设置UI
        self.load_plugin_settings(plugin_data['id'])
    
    def on_enable_changed(self, state):
        """当启用状态改变时"""
        row = self.plugin_list.currentRow()
        if row < 0:
            return
        
        item = self.plugin_list.item(row)
        plugin_data = item.data(Qt.UserRole)
        plugin_id = plugin_data['id']
        
        if state == Qt.Checked:
            # 启用插件
            success = self.plugin_manager.enable_plugin(plugin_id)
            if not success:
                QMessageBox.warning(self, "警告", f"启用插件 {plugin_data['name']} 失败")
                self.enable_plugin.setChecked(False)
                return
        else:
            # 禁用插件
            success = self.plugin_manager.disable_plugin(plugin_id)
            if not success:
                QMessageBox.warning(self, "警告", f"禁用插件 {plugin_data['name']} 失败")
                self.enable_plugin.setChecked(True)
                return
        
        # 更新插件数据
        plugin_data['enabled'] = (state == Qt.Checked)
        item.setData(Qt.UserRole, plugin_data)
    
    def load_plugin_settings(self, plugin_id):
        """加载插件设置UI"""
        # 清空现有设置UI
        while self.settings_widget.count() > 0:
            widget = self.settings_widget.widget(0)
            self.settings_widget.removeWidget(widget)
            widget.deleteLater()
        
        # 检查插件是否已加载
        if plugin_id not in self.plugin_manager.plugins:
            # 创建一个空白设置页面
            empty_widget = QWidget()
            empty_layout = QVBoxLayout(empty_widget)
            empty_label = QLabel("此插件未启用或没有设置选项")
            empty_label.setAlignment(Qt.AlignCenter)
            empty_layout.addWidget(empty_label)
            self.settings_widget.addWidget(empty_widget)
            return
        
        # 获取插件实例
        plugin = self.plugin_manager.plugins[plugin_id]
        
        # 获取插件设置UI
        settings_ui = plugin.get_settings_ui()
        if settings_ui is None:
            # 创建一个空白设置页面
            empty_widget = QWidget()
            empty_layout = QVBoxLayout(empty_widget)
            empty_label = QLabel("此插件没有设置选项")
            empty_label.setAlignment(Qt.AlignCenter)
            empty_layout.addWidget(empty_label)
            self.settings_widget.addWidget(empty_widget)
        else:
            # 添加插件设置UI
            self.settings_widget.addWidget(settings_ui)