from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton
from PyQt5.QtCore import Qt
from loguru import logger

from plugin import PluginBase

class Plugin(PluginBase):
    """Hello World 示例插件"""
    def __init__(self, config):
        super().__init__(config)
        self.name = "Hello World"
        self.version = "1.0.0"
        self.description = "一个简单的示例插件，展示插件系统的基本功能"
        self.author = "LitheTimetable Team"
        
        # 插件设置
        self.settings = self.load_settings()
        
        logger.info(f"{self.name} 插件已初始化")
    
    def initialize(self):
        """初始化插件"""
        logger.info(f"{self.name} 插件已启动")
        return True
    
    def terminate(self):
        """终止插件"""
        logger.info(f"{self.name} 插件已停止")
        return True
    
    def load_settings(self):
        """加载插件设置"""
        # 从插件管理器获取设置，如果没有则使用默认设置
        default_settings = {
            "message": "你好，世界！",
            "show_message": True
        }
        
        # 这里可以从配置中加载设置
        return default_settings
    
    def get_settings_ui(self):
        """获取插件设置UI"""
        # 创建设置界面
        settings_widget = QWidget()
        layout = QVBoxLayout(settings_widget)
        
        # 消息设置
        message_label = QLabel("显示消息:")
        self.message_edit = QLineEdit(self.settings.get("message", "你好，世界！"))
        
        # 是否显示消息
        self.show_message_checkbox = QPushButton("测试消息")
        self.show_message_checkbox.clicked.connect(self.test_message)
        
        # 添加到布局
        layout.addWidget(message_label)
        layout.addWidget(self.message_edit)
        layout.addWidget(self.show_message_checkbox)
        layout.addStretch(1)
        
        return settings_widget
    
    def save_settings(self, settings):
        """保存插件设置"""
        self.settings["message"] = self.message_edit.text()
        return True
    
    def test_message(self):
        """测试消息显示"""
        from PyQt5.QtWidgets import QMessageBox
        QMessageBox.information(None, "Hello World 插件", self.message_edit.text())