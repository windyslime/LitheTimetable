import os
import json
import datetime
from pathlib import Path
from loguru import logger

class Config:
    """配置管理类"""
    def __init__(self):
        # 确保配置目录存在
        self.config_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
        os.makedirs(self.config_dir, exist_ok=True)
        
        # 配置文件路径
        self.config_file = os.path.join(self.config_dir, 'config.json')
        
        # 默认配置
        self.default_config = {
            'general': {
                'theme': 'light_blue',
                'minimize_to_tray': True,
                'start_with_system': False,
                'language': 'zh_CN'
            },
            'timetable': {
                'semester_start_date': datetime.datetime.now().strftime('%Y-%m-%d'),
                'current_week': 1,
                'total_weeks': 20,
                'time_slots': [
                    {'name': '第1节', 'start': '08:00', 'end': '08:45'},
                    {'name': '第2节', 'start': '08:55', 'end': '09:40'},
                    {'name': '第3节', 'start': '10:00', 'end': '10:45'},
                    {'name': '第4节', 'start': '10:55', 'end': '11:40'},
                    {'name': '第5节', 'start': '14:00', 'end': '14:45'},
                    {'name': '第6节', 'start': '14:55', 'end': '15:40'},
                    {'name': '第7节', 'start': '16:00', 'end': '16:45'},
                    {'name': '第8节', 'start': '16:55', 'end': '17:40'},
                    {'name': '第9节', 'start': '19:00', 'end': '19:45'},
                    {'name': '第10节', 'start': '19:55', 'end': '20:40'}
                ]
            },
            'notification': {
                'enable': True,
                'advance_time': 10,  # 提前10分钟提醒
                'sound': True
            },
            'weather': {
                'enable': True,
                'city': '北京',
                'city_code': '101010100',
                'update_interval': 3600  # 更新间隔（秒）
            },
            'appearance': {
                'primary_color': '#3f51b5',
                'accent_color': '#ff4081',
                'dark_mode': False,
                'custom_colors': {}
            }
        }
        
        # 加载配置
        self.config = self.load_config()
    
    def load_config(self):
        """加载配置文件"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                logger.info("配置文件加载成功")
                
                # 合并默认配置（确保新增配置项存在）
                merged_config = self.default_config.copy()
                self._deep_update(merged_config, config)
                return merged_config
            else:
                logger.info("配置文件不存在，使用默认配置")
                self.save_config(self.default_config)  # 保存默认配置
                return self.default_config
        except Exception as e:
            logger.error(f"加载配置文件失败: {e}")
            return self.default_config
    
    def save_config(self, config=None):
        """保存配置文件"""
        if config is None:
            config = self.config
        
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=4)
            logger.info("配置文件保存成功")
            return True
        except Exception as e:
            logger.error(f"保存配置文件失败: {e}")
            return False
    
    def get(self, key, default=None, section=None):
        """获取配置项"""
        try:
            if section:
                return self.config.get(section, {}).get(key, default)
            
            # 支持点分隔的键，如 'timetable.current_week'
            if '.' in key:
                parts = key.split('.')
                value = self.config
                for part in parts:
                    value = value.get(part, {})
                return value if value != {} else default
            
            return self.config.get(key, default)
        except Exception as e:
            logger.error(f"获取配置项失败: {key}, {e}")
            return default
    
    def set(self, key, value, section=None):
        """设置配置项"""
        try:
            if section:
                if section not in self.config:
                    self.config[section] = {}
                self.config[section][key] = value
            elif '.' in key:
                # 支持点分隔的键
                parts = key.split('.')
                config = self.config
                for part in parts[:-1]:
                    if part not in config:
                        config[part] = {}
                    config = config[part]
                config[parts[-1]] = value
            else:
                self.config[key] = value
            
            self.save_config()
            return True
        except Exception as e:
            logger.error(f"设置配置项失败: {key}, {e}")
            return False
    
    def _deep_update(self, d, u):
        """递归更新字典"""
        for k, v in u.items():
            if isinstance(v, dict) and k in d and isinstance(d[k], dict):
                self._deep_update(d[k], v)
            else:
                d[k] = v