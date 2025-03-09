import os
import json
import time
import datetime
import requests
from loguru import logger

class WeatherService:
    """天气服务类"""
    def __init__(self, config):
        self.config = config
        self.data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
        self.weather_cache_file = os.path.join(self.data_dir, 'weather_cache.json')
        self.last_update_time = 0
        self.weather_data = None
        
        # 天气图标映射
        self.weather_icons = {
            '晴': 'sunny',
            '多云': 'cloudy',
            '阴': 'overcast',
            '小雨': 'light_rain',
            '中雨': 'moderate_rain',
            '大雨': 'heavy_rain',
            '暴雨': 'storm',
            '雷阵雨': 'thunderstorm',
            '小雪': 'light_snow',
            '中雪': 'moderate_snow',
            '大雪': 'heavy_snow',
            '暴雪': 'snowstorm',
            '雾': 'fog',
            '霾': 'haze'
        }
        
        # 加载缓存的天气数据
        self.load_cache()
        
        logger.info("天气服务初始化完成")
    
    def load_cache(self):
        """加载缓存的天气数据"""
        try:
            if os.path.exists(self.weather_cache_file):
                with open(self.weather_cache_file, 'r', encoding='utf-8') as f:
                    cache_data = json.load(f)
                    self.weather_data = cache_data.get('data')
                    self.last_update_time = cache_data.get('timestamp', 0)
                logger.info("天气缓存加载成功")
        except Exception as e:
            logger.error(f"加载天气缓存失败: {e}")
    
    def save_cache(self):
        """保存天气数据到缓存"""
        try:
            cache_data = {
                'timestamp': self.last_update_time,
                'data': self.weather_data
            }
            
            with open(self.weather_cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, ensure_ascii=False, indent=4)
            
            logger.info("天气缓存保存成功")
        except Exception as e:
            logger.error(f"保存天气缓存失败: {e}")
    
    def get_weather(self):
        """获取天气信息"""
        # 检查是否启用天气功能
        if not self.config.get('weather.enable', True):
            return None
        
        # 检查是否需要更新天气数据
        current_time = time.time()
        update_interval = self.config.get('weather.update_interval', 3600)  # 默认1小时更新一次
        
        if self.weather_data is None or (current_time - self.last_update_time) > update_interval:
            # 需要更新天气数据
            self.update_weather()
        
        return self.weather_data
    
    def update_weather(self):
        """更新天气数据"""
        try:
            city_code = self.config.get('weather.city_code', '101010100')  # 默认北京
            
            # 使用和风天气API获取天气数据
            # 注意：实际使用时需要替换为您自己的API密钥
            url = f"http://wthrcdn.etouch.cn/weather_mini?citykey={city_code}"
            
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            weather_json = response.json()
            
            if weather_json.get('status') == 1000:
                data = weather_json.get('data', {})
                
                # 提取需要的天气信息
                self.weather_data = {
                    'city': data.get('city', '未知'),
                    'temperature': data.get('wendu', '0'),
                    'condition': data.get('forecast', [{}])[0].get('type', '未知'),
                    'wind_direction': data.get('forecast', [{}])[0].get('fengxiang', ''),
                    'wind_strength': data.get('forecast', [{}])[0].get('fengli', '').replace('<![CDATA[', '').replace(']]>', ''),
                    'humidity': '',  # 此API不提供湿度
                    'update_time': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'icon': self.get_weather_icon(data.get('forecast', [{}])[0].get('type', '未知'))
                }
                
                # 更新时间戳和缓存
                self.last_update_time = time.time()
                self.save_cache()
                
                logger.info(f"天气数据更新成功: {self.weather_data['city']} {self.weather_data['temperature']}°C {self.weather_data['condition']}")
            else:
                logger.error(f"获取天气数据失败: {weather_json.get('desc', '未知错误')}")
        except Exception as e:
            logger.error(f"更新天气数据失败: {e}")
    
    def get_weather_icon(self, condition):
        """根据天气状况获取图标名称"""
        for key, icon in self.weather_icons.items():
            if key in condition:
                return icon
        
        # 默认图标
        return 'unknown'