import os
import json
import datetime
from datetime import timedelta
from pathlib import Path
from loguru import logger

class TimeTable:
    """课表管理类"""
    def __init__(self, config):
        self.config = config
        
        # 确保课表数据目录存在
        self.data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
        self.courses_file = os.path.join(self.data_dir, 'courses.json')
        
        # 加载课程数据
        self.courses = self.load_courses()
        
        # 颜色映射（为不同课程分配不同颜色）
        self.color_map = {
            '数学': '#3f51b5',  # 蓝色
            '语文': '#f44336',  # 红色
            '英语': '#4caf50',  # 绿色
            '物理': '#ff9800',  # 橙色
            '化学': '#9c27b0',  # 紫色
            '生物': '#009688',  # 青色
            '历史': '#795548',  # 棕色
            '地理': '#607d8b',  # 蓝灰色
            '政治': '#e91e63',  # 粉色
            '体育': '#cddc39',  # 酸橙色
            '音乐': '#673ab7',  # 深紫色
            '美术': '#ffc107',  # 琥珀色
            '信息': '#03a9f4',  # 浅蓝色
            '通用技术': '#8bc34a',  # 浅绿色
        }
        
        logger.info("课表管理器初始化完成")
    
    def load_courses(self):
        """加载课程数据"""
        try:
            if os.path.exists(self.courses_file):
                with open(self.courses_file, 'r', encoding='utf-8') as f:
                    courses = json.load(f)
                logger.info("课程数据加载成功")
                return courses
            else:
                logger.info("课程数据文件不存在，创建示例数据")
                # 创建示例数据
                example_courses = self.create_example_courses()
                self.save_courses(example_courses)
                return example_courses
        except Exception as e:
            logger.error(f"加载课程数据失败: {e}")
            return self.create_example_courses()
    
    def save_courses(self, courses=None):
        """保存课程数据"""
        if courses is None:
            courses = self.courses
        
        try:
            with open(self.courses_file, 'w', encoding='utf-8') as f:
                json.dump(courses, f, ensure_ascii=False, indent=4)
            logger.info("课程数据保存成功")
            return True
        except Exception as e:
            logger.error(f"保存课程数据失败: {e}")
            return False
    
    def create_example_courses(self):
        """创建示例课程数据"""
        return {
            "courses": [
                {
                    "id": 1,
                    "name": "高等数学",
                    "teacher": "张教授",
                    "location": "教学楼A-101",
                    "weeks": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16],
                    "day": 0,  # 周一
                    "slot": 0,  # 第一节课
                    "duration": 2  # 持续2个课时
                },
                {
                    "id": 2,
                    "name": "大学英语",
                    "teacher": "李教授",
                    "location": "教学楼B-202",
                    "weeks": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16],
                    "day": 0,  # 周一
                    "slot": 2,  # 第三节课
                    "duration": 2  # 持续2个课时
                },
                {
                    "id": 3,
                    "name": "程序设计",
                    "teacher": "王教授",
                    "location": "实验楼C-303",
                    "weeks": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16],
                    "day": 1,  # 周二
                    "slot": 0,  # 第一节课
                    "duration": 3  # 持续3个课时
                },
                {
                    "id": 4,
                    "name": "数据结构",
                    "teacher": "刘教授",
                    "location": "教学楼A-201",
                    "weeks": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16],
                    "day": 2,  # 周三
                    "slot": 2,  # 第三节课
                    "duration": 2  # 持续2个课时
                },
                {
                    "id": 5,
                    "name": "计算机网络",
                    "teacher": "赵教授",
                    "location": "教学楼B-301",
                    "weeks": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16],
                    "day": 3,  # 周四
                    "slot": 4,  # 第五节课
                    "duration": 2  # 持续2个课时
                },
                {
                    "id": 6,
                    "name": "操作系统",
                    "teacher": "孙教授",
                    "location": "实验楼C-101",
                    "weeks": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16],
                    "day": 4,  # 周五
                    "slot": 0,  # 第一节课
                    "duration": 2  # 持续2个课时
                }
            ]
        }
    
    def get_current_week(self):
        """获取当前教学周"""
        try:
            # 从配置中获取学期开始日期和当前周数
            start_date_str = self.config.get('timetable.semester_start_date')
            start_date = datetime.datetime.strptime(start_date_str, '%Y-%m-%d').date()
            
            # 计算当前日期与学期开始日期的差值
            today = datetime.date.today()
            days_diff = (today - start_date).days
            
            # 计算当前是第几周（向下取整）
            current_week = days_diff // 7 + 1
            
            # 确保周数在合理范围内
            total_weeks = self.config.get('timetable.total_weeks', 20)
            if current_week < 1:
                current_week = 1
            elif current_week > total_weeks:
                current_week = total_weeks
            
            return current_week
        except Exception as e:
            logger.error(f"获取当前教学周失败: {e}")
            return self.config.get('timetable.current_week', 1)
    
    def get_time_slots(self):
        """获取时间段配置"""
        return self.config.get('timetable.time_slots', [])
    
    def get_weekly_courses(self, week):
        """获取指定周的课程"""
        weekly_courses = []
        
        for course in self.courses.get('courses', []):
            # 检查课程是否在指定周进行
            if week in course.get('weeks', []):
                # 为课程添加颜色
                course_with_color = course.copy()
                course_name = course.get('name', '')
                
                # 根据课程名称的第一个字符（通常是学科名）分配颜色
                for subject, color in self.color_map.items():
                    if subject in course_name:
                        course_with_color['color'] = color
                        break
                else:
                    # 如果没有匹配的颜色，使用默认颜色
                    course_with_color['color'] = '#3f51b5'  # 默认蓝色
                
                weekly_courses.append(course_with_color)
        
        return weekly_courses
    
    def get_today_courses(self):
        """获取今天的课程"""
        current_week = self.get_current_week()
        today_weekday = datetime.datetime.now().weekday()  # 0-6 表示周一到周日
        
        today_courses = []
        for course in self.get_weekly_courses(current_week):
            if course.get('day') == today_weekday:
                today_courses.append(course)
        
        # 按时间段排序
        today_courses.sort(key=lambda x: x.get('slot', 0))
        
        return today_courses
    
    def get_next_course(self):
        """获取下一节课程"""
        today_courses = self.get_today_courses()
        if not today_courses:
            return None
        
        current_time = datetime.datetime.now().time()
        time_slots = self.get_time_slots()
        
        for course in today_courses:
            slot_index = course.get('slot', 0)
            if slot_index < len(time_slots):
                slot = time_slots[slot_index]
                end_time_str = slot.get('end', '00:00')
                end_time = datetime.datetime.strptime(end_time_str, '%H:%M').time()
                
                if current_time < end_time:
                    return course
        
        return None
    
    def add_course(self, course_data):
        """添加课程"""
        try:
            # 生成新的课程ID
            max_id = 0
            for course in self.courses.get('courses', []):
                if course.get('id', 0) > max_id:
                    max_id = course.get('id')
            
            new_course = course_data.copy()
            new_course['id'] = max_id + 1
            
            # 添加到课程列表
            if 'courses' not in self.courses:
                self.courses['courses'] = []
            
            self.courses['courses'].append(new_course)
            
            # 保存更新
            self.save_courses()
            
            logger.info(f"添加课程成功: {new_course['name']}")
            return True
        except Exception as e:
            logger.error(f"添加课程失败: {e}")
            return False
    
    def update_course(self, course_id, course_data):
        """更新课程"""
        try:
            for i, course in enumerate(self.courses.get('courses', [])):
                if course.get('id') == course_id:
                    # 更新课程数据，保留ID
                    updated_course = course_data.copy()
                    updated_course['id'] = course_id
                    
                    self.courses['courses'][i] = updated_course
                    
                    # 保存更新
                    self.save_courses()
                    
                    logger.info(f"更新课程成功: {updated_course['name']}")
                    return True
            
            logger.warning(f"未找到ID为{course_id}的课程")
            return False
        except Exception as e:
            logger.error(f"更新课程失败: {e}")
            return False
    
    def delete_course(self, course_id):
        """删除课程"""
        try:
            for i, course in enumerate(self.courses.get('courses', [])):
                if course.get('id') == course_id:
                    # 删除课程
                    del self.courses['courses'][i]
                    
                    # 保存更新
                    self.save_courses()
                    
                    logger.info(f"删除课程成功: ID={course_id}")
                    return True
            
            logger.warning(f"未找到ID为{course_id}的课程")
            return False
        except Exception as e:
            logger.error(f"删除课程失败: {e}")
            return False