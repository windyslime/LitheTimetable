import os
import datetime
import time
from PyQt5.QtWidgets import QSystemTrayIcon
from PyQt5.QtGui import QIcon
from loguru import logger

class NotificationService:
    """通知服务类，用于提醒即将开始的课程"""
    def __init__(self, config):
        self.config = config
        self.last_notification_time = {}
        self.notification_cooldown = 300  # 5分钟内不重复提醒同一课程
        
        # 通知音效文件路径
        self.sound_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'assets', 'notification.wav')
        
        logger.info("通知服务初始化完成")
    
    def check_upcoming_classes(self, timetable):
        """检查即将开始的课程并发送通知"""
        # 检查是否启用通知
        if not self.config.get('notification.enable', True):
            return
        
        # 获取当前时间
        now = datetime.datetime.now()
        current_time = now.time()
        current_weekday = now.weekday()  # 0-6 表示周一到周日
        
        # 获取当前周的课程
        current_week = timetable.get_current_week()
        courses = timetable.get_weekly_courses(current_week)
        
        # 获取时间段配置
        time_slots = timetable.get_time_slots()
        
        # 提前提醒时间（分钟）
        advance_time = self.config.get('notification.advance_time', 10)
        
        for course in courses:
            # 检查课程是否在今天
            if course.get('day') != current_weekday:
                continue
            
            # 获取课程开始时间
            slot_index = course.get('slot', 0)
            if slot_index >= len(time_slots):
                continue
                
            slot = time_slots[slot_index]
            start_time_str = slot.get('start', '00:00')
            
            # 解析开始时间
            try:
                start_time = datetime.datetime.strptime(start_time_str, '%H:%M').time()
                
                # 计算提醒时间
                reminder_datetime = datetime.datetime.combine(now.date(), start_time) - datetime.timedelta(minutes=advance_time)
                reminder_time = reminder_datetime.time()
                
                # 检查是否到了提醒时间
                if self._is_time_between(current_time, reminder_time, start_time):
                    # 检查是否在冷却期内
                    course_id = course.get('id')
                    if course_id in self.last_notification_time:
                        last_time = self.last_notification_time[course_id]
                        if (time.time() - last_time) < self.notification_cooldown:
                            continue
                    
                    # 发送通知
                    self._send_notification(course, start_time_str)
                    
                    # 更新最后通知时间
                    self.last_notification_time[course_id] = time.time()
            except Exception as e:
                logger.error(f"处理课程通知时出错: {e}")
    
    def _is_time_between(self, current, start, end):
        """检查当前时间是否在指定的时间范围内"""
        if start <= end:
            return start <= current <= end
        else:  # 跨越午夜的情况
            return start <= current or current <= end
    
    def _send_notification(self, course, start_time):
        """发送课程通知"""
        try:
            course_name = course.get('name', '未知课程')
            location = course.get('location', '未知地点')
            teacher = course.get('teacher', '未知教师')
            
            # 构建通知内容
            title = f"课程提醒: {course_name}"
            message = f"课程将于 {start_time} 开始\n地点: {location}\n教师: {teacher}"
            
            # 显示系统通知
            tray_icon = QSystemTrayIcon()
            tray_icon.setIcon(QIcon(os.path.join("assets", "icon.png")))
            tray_icon.show()
            tray_icon.showMessage(title, message, QSystemTrayIcon.Information, 10000)  # 显示10秒
            
            # 播放提示音（如果启用）
            if self.config.get('notification.sound', True) and os.path.exists(self.sound_file):
                # 这里可以添加播放声音的代码
                # 例如使用QSound或其他音频库
                pass
            
            logger.info(f"已发送课程提醒: {course_name} - {start_time}")
        except Exception as e:
            logger.error(f"发送通知失败: {e}")