import os
import sys
import json
import importlib.util
from pathlib import Path
from loguru import logger

class PluginManager:
    """插件管理器，用于加载和管理插件"""
    def __init__(self, config):
        self.config = config
        
        # 插件目录
        self.plugins_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'plugins')
        os.makedirs(self.plugins_dir, exist_ok=True)
        
        # 已加载的插件
        self.plugins = {}
        
        # 插件配置文件
        self.plugins_config_file = os.path.join(self.plugins_dir, 'plugins.json')
        
        # 加载插件配置
        self.plugins_config = self.load_plugins_config()
        
        logger.info("插件管理器初始化完成")
    
    def load_plugins_config(self):
        """加载插件配置"""
        try:
            if os.path.exists(self.plugins_config_file):
                with open(self.plugins_config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                # 创建默认配置
                default_config = {
                    "enabled_plugins": [],
                    "plugin_settings": {}
                }
                with open(self.plugins_config_file, 'w', encoding='utf-8') as f:
                    json.dump(default_config, f, ensure_ascii=False, indent=4)
                return default_config
        except Exception as e:
            logger.error(f"加载插件配置失败: {e}")
            return {"enabled_plugins": [], "plugin_settings": {}}
    
    def save_plugins_config(self):
        """保存插件配置"""
        try:
            with open(self.plugins_config_file, 'w', encoding='utf-8') as f:
                json.dump(self.plugins_config, f, ensure_ascii=False, indent=4)
            logger.info("插件配置保存成功")
            return True
        except Exception as e:
            logger.error(f"保存插件配置失败: {e}")
            return False
    
    def discover_plugins(self):
        """发现可用的插件"""
        available_plugins = []
        
        # 遍历插件目录
        for item in os.listdir(self.plugins_dir):
            plugin_dir = os.path.join(self.plugins_dir, item)
            
            # 检查是否是目录
            if os.path.isdir(plugin_dir):
                # 检查是否有__init__.py文件
                init_file = os.path.join(plugin_dir, '__init__.py')
                manifest_file = os.path.join(plugin_dir, 'manifest.json')
                
                if os.path.exists(init_file) and os.path.exists(manifest_file):
                    try:
                        # 读取插件清单
                        with open(manifest_file, 'r', encoding='utf-8') as f:
                            manifest = json.load(f)
                        
                        # 添加到可用插件列表
                        available_plugins.append({
                            'id': item,
                            'name': manifest.get('name', item),
                            'version': manifest.get('version', '1.0.0'),
                            'description': manifest.get('description', ''),
                            'author': manifest.get('author', ''),
                            'enabled': item in self.plugins_config['enabled_plugins']
                        })
                    except Exception as e:
                        logger.error(f"读取插件{item}清单失败: {e}")
        
        return available_plugins
    
    def load_plugins(self):
        """加载启用的插件"""
        # 清空已加载的插件
        self.plugins = {}
        
        # 获取启用的插件列表
        enabled_plugins = self.plugins_config['enabled_plugins']
        
        for plugin_id in enabled_plugins:
            self.load_plugin(plugin_id)
        
        logger.info(f"已加载{len(self.plugins)}个插件")
    
    def load_plugin(self, plugin_id):
        """加载单个插件"""
        try:
            plugin_dir = os.path.join(self.plugins_dir, plugin_id)
            init_file = os.path.join(plugin_dir, '__init__.py')
            
            if not os.path.exists(init_file):
                logger.error(f"插件{plugin_id}的__init__.py文件不存在")
                return False
            
            # 动态导入模块
            spec = importlib.util.spec_from_file_location(f"plugins.{plugin_id}", init_file)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # 检查是否有Plugin类
            if not hasattr(module, 'Plugin'):
                logger.error(f"插件{plugin_id}没有定义Plugin类")
                return False
            
            # 实例化插件
            plugin_instance = module.Plugin(self.config)
            
            # 添加到已加载插件字典
            self.plugins[plugin_id] = plugin_instance
            
            logger.info(f"插件{plugin_id}加载成功")
            return True
        except Exception as e:
            logger.error(f"加载插件{plugin_id}失败: {e}")
            return False
    
    def enable_plugin(self, plugin_id):
        """启用插件"""
        if plugin_id not in self.plugins_config['enabled_plugins']:
            self.plugins_config['enabled_plugins'].append(plugin_id)
            self.save_plugins_config()
            self.load_plugin(plugin_id)
            return True
        return False
    
    def disable_plugin(self, plugin_id):
        """禁用插件"""
        if plugin_id in self.plugins_config['enabled_plugins']:
            self.plugins_config['enabled_plugins'].remove(plugin_id)
            self.save_plugins_config()
            if plugin_id in self.plugins:
                del self.plugins[plugin_id]
            return True
        return False
    
    def get_plugin_settings(self, plugin_id):
        """获取插件设置"""
        return self.plugins_config['plugin_settings'].get(plugin_id, {})
    
    def save_plugin_settings(self, plugin_id, settings):
        """保存插件设置"""
        self.plugins_config['plugin_settings'][plugin_id] = settings
        return self.save_plugins_config()
    
    def call_plugin_method(self, plugin_id, method_name, *args, **kwargs):
        """调用插件方法"""
        if plugin_id in self.plugins:
            plugin = self.plugins[plugin_id]
            if hasattr(plugin, method_name):
                method = getattr(plugin, method_name)
                if callable(method):
                    try:
                        return method(*args, **kwargs)
                    except Exception as e:
                        logger.error(f"调用插件{plugin_id}的{method_name}方法失败: {e}")
        return None


class PluginBase:
    """插件基类，所有插件都应该继承此类"""
    def __init__(self, config):
        self.config = config
        self.name = "未命名插件"
        self.version = "1.0.0"
        self.description = ""
        self.author = ""
    
    def initialize(self):
        """初始化插件，在插件加载时调用"""
        pass
    
    def terminate(self):
        """终止插件，在插件卸载时调用"""
        pass
    
    def get_settings_ui(self):
        """获取插件设置UI，返回一个QWidget"""
        return None
    
    def save_settings(self, settings):
        """保存插件设置"""
        pass