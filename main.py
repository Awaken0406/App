import os
import string
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.graphics import Color, Rectangle,Ellipse
from kivy.config import Config
from kivy.core.text import LabelBase
import requests  # 用于网络请求
import threading  # 防止网络请求阻塞UI
import random

# 设置窗口大小
Config.set('graphics', 'width', '800')
Config.set('graphics', 'height', '500')
#font_path = os.path.join(os.path.dirname(__file__), 'fonts', 'msyh.ttc')
#LabelBase.register(name='Chinese', fn_regular=font_path)

class SimpleArrayDisplayApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # 固定数组 - 红区和蓝区
        self.red_array = [0, 0, 0, 0, 0,0]
        self.blue_array = [0]
        
        self.red_index = 0  # 红区当前索引
        self.blue_index = 0  # 蓝区当前索引
        self.playing = False
        self.current_phase = 0  # 0:未播放, 1:红区播放中, 2:蓝区播放中, 3:播放完成
        self.red_labels = []  # 存储红区数字标签
        self.blue_labels = []  # 存储蓝区数字标签
        
    def build(self):
        # 主布局
        main_layout = BoxLayout(orientation='vertical', spacing=10, padding=15)
        # 显示数据的标签
        self.data_label = Label(text="", size_hint=(0.5, 0.4))
        main_layout.add_widget(self.data_label)
        # 标题
        title_label = Label(
            text='Number Area',
            size_hint=(1, 0.15),
            font_size='32sp',
            color=(1, 1, 1, 1),
            bold=True
        )
        
        # 红区标题
        red_header = BoxLayout(
            orientation='horizontal',
            size_hint=(1, 0.08),
            spacing=20,
            padding=[20, 0]
        )
        red_title = Label(
            text='red',
            size_hint=(0.1, 1),
            font_size='24sp',
            color=(1, 0.4, 0.4, 1)
        )
        red_area = BoxLayout(
            orientation='horizontal',
            spacing=10,
            size_hint=(0.9, 1)
        )
        red_header.add_widget(red_title)
        red_header.add_widget(red_area)
        
        # 蓝区标题
        blue_header = BoxLayout(
            orientation='horizontal',
            size_hint=(1, 0.08),
            spacing=20,
            padding=[20, 0]
        )
        blue_title = Label(
            text='blue',
            size_hint=(0.1, 1),
            font_size='24sp',
            color=(0.4, 0.4, 1, 1)
        )
        blue_area = BoxLayout(
            orientation='horizontal',
            spacing=10,
            size_hint=(0.9, 1)
        )
        blue_header.add_widget(blue_title)
        blue_header.add_widget(blue_area)
        
        # 状态显示区域
        self.status_label = Label(
            text='Start',
            size_hint=(1, 0.08),
            font_size='20sp',
            color=(0.9, 0.9, 0.9, 1)
        )
        
        # 播放按钮区域 - 居中
        button_container = BoxLayout(
            orientation='horizontal',
            size_hint=(1, 0.15),
            padding=[200, 0, 200, 0]
        )
        
        # 居中填充用的空白标签
        left_spacer = Label(size_hint=(0.2, 1))
        right_spacer = Label(size_hint=(0.2, 1))
        
        # 播放按钮（居中）
        self.play_button = Button(
            text='Start',
            size_hint=(0.6, 0.8),
            font_size='30sp',
            background_color=(0.2, 0.6, 0.8, 1),
            background_normal=''
        )
        self.play_button.bind(on_press=self.fetch_data)
        
        button_container.add_widget(left_spacer)
        button_container.add_widget(self.play_button)
        button_container.add_widget(right_spacer)
        
        # 进度标签
        self.progress_label = Label(
            text='',
            size_hint=(1, 0.06),
            font_size='16sp',
            color=(0.8, 0.8, 0.8, 1)
        )
        
        # 初始化红区和蓝区显示
        self.red_area = red_area
        self.blue_area = blue_area
        self.init_array_display()
        
        # 添加到布局
        main_layout.add_widget(title_label)
        main_layout.add_widget(red_header)
        main_layout.add_widget(blue_header)
        #main_layout.add_widget(self.status_label)
        main_layout.add_widget(button_container)
        main_layout.add_widget(self.progress_label)
        
        # 设置渐变背景
        with main_layout.canvas.before:
            Color(0.12, 0.12, 0.15, 1)
            self.bg_rect = Rectangle(size=main_layout.size, pos=main_layout.pos)
        
        main_layout.bind(size=self.update_bg, pos=self.update_bg)
        
        return main_layout
    
    def init_array_display(self):
        """初始化红区和蓝区的数字显示"""
        self.red_area.clear_widgets()
        self.blue_area.clear_widgets()
        self.red_labels = []
        self.blue_labels = []
        
        # 创建红区数字显示
        for i, num in enumerate(self.red_array):
            # 红区数字容器
            red_container = BoxLayout(orientation='vertical', size_hint=(None, 1))
            red_container.width = 60
            
            # 红区数字标签 - 初始为空
            red_label = Label(
                text='',
                font_size='28sp',
                color=(1, 0.8, 0.8, 0),  # 初始透明
                size_hint=(1, 0.7),
                halign='center',
                valign='middle'
            )
            
            # 红区索引标签
            red_index = Label(
                text=f'R{i}',
                font_size='14sp',
                color=(1, 0.6, 0.6, 1),
                size_hint=(1, 0.3)
            )
            
            # 红区数字背景
            with red_container.canvas.before:
                Color(0.4, 0.15, 0.15, 1)  # 深红色背景
                rect = Ellipse(size=red_container.size, pos=red_container.pos)
                red_container.bg_rect = rect
            
            red_container.bind(size=self.update_red_bg, pos=self.update_red_bg)
            red_container.add_widget(red_label)
            #red_container.add_widget(red_index)
            
            self.red_area.add_widget(red_container)
            self.red_labels.append({
                'container': red_container,
                'label': red_label,
                'index_label': red_index,
                'number': num
            })
        
        # 创建蓝区数字显示
        for i, num in enumerate(self.blue_array):
            # 蓝区数字容器
            blue_container = BoxLayout(orientation='vertical', size_hint=(None, 1))
            blue_container.width = 60
            
            # 蓝区数字标签 - 初始为空
            blue_label = Label(
                text='',
                font_size='28sp',
                color=(0.8, 0.8, 1, 0),  # 初始透明
                size_hint=(1, 0.7),
                halign='center',
                valign='middle'
            )
            
            # 蓝区索引标签
            blue_index = Label(
                text=f'B{i}',
                font_size='14sp',
                color=(0.6, 0.6, 1, 1),
                size_hint=(1, 0.3)
            )
            
            # 蓝区数字背景
            with blue_container.canvas.before:
                Color(0.15, 0.15, 0.4, 1)  # 深蓝色背景
                rect = Ellipse(size=blue_container.size, pos=blue_container.pos)
                blue_container.bg_rect = rect
            
            blue_container.bind(size=self.update_blue_bg, pos=self.update_blue_bg)
            blue_container.add_widget(blue_label)
            #blue_container.add_widget(blue_index)
            
            self.blue_area.add_widget(blue_container)
            self.blue_labels.append({
                'container': blue_container,
                'label': blue_label,
                'index_label': blue_index,
                'number': num
            })
    
    def update_red_bg(self, instance, value):
        """更新红区数字背景"""
        instance.bg_rect.size = instance.size
        instance.bg_rect.pos = instance.pos
    
    def update_blue_bg(self, instance, value):
        """更新蓝区数字背景"""
        instance.bg_rect.size = instance.size
        instance.bg_rect.pos = instance.pos
    
    def update_bg(self, instance, value):
        """更新主背景"""
        self.bg_rect.size = instance.size
        self.bg_rect.pos = instance.pos


    def clickBtn(self):
        """重置所有状态"""
        # 重置索引和阶段
        self.red_index = 0
        self.blue_index = 0
        self.current_phase = 0
        self.playing = False
        
        # 重置红区所有数字显示
        for item in self.red_labels:
            item['label'].text = ''
            item['label'].color = (1, 0.8, 0.8, 0)  # 透明
            item['index_label'].color = (1, 0.6, 0.6, 1)
            item['index_label'].font_size = '14sp'
        
        # 重置蓝区所有数字显示
        for item in self.blue_labels:
            item['label'].text = ''
            item['label'].color = (0.8, 0.8, 1, 0)  # 透明
            item['index_label'].color = (0.6, 0.6, 1, 1)
            item['index_label'].font_size = '14sp'
        self.playing = True
        self.current_phase = 1  # 开始红区播放
        self.play_button.disabled = True  # 禁用按钮
        self.play_button.text = '...'
        self.play_button.background_color = (0.6, 0.6, 0.6, 1)
        
        self.status_label.text = '...'
        self.status_label.color = (1, 0.6, 0.6, 1)
        
        self.progress_label.text = f'red: 0/{len(self.red_array)} | blue: 0/{len(self.blue_array)}'
    
    def start_play(self, instance):
        """开始播放"""
        # 如果正在播放或播放完成，则重置
        #if self.playing or self.current_phase == 3:
            #self.reset_all()     
        # 清除之前可能存在的定时器
        Clock.unschedule(self.show_next_number)
        
        # 固定速度：每秒显示1个数字
        Clock.schedule_interval(self.show_next_number, 1.0)
    
    def show_next_number(self, dt):
        """显示下一个数字"""
        if self.current_phase == 1:  # 红区播放阶段
            # 播放红区数字
            if self.red_index < len(self.red_array):
                red_item = self.red_labels[self.red_index]
                red_item['label'].text = str(red_item['number'])
                
                # 淡入动画效果
                from kivy.animation import Animation
                anim = Animation(color=(1, 0.8, 0.8, 1), duration=0.5)
                anim.start(red_item['label'])
                
                # 高亮红区索引
                red_item['index_label'].color = (1, 0.3, 0.3, 1)
                red_item['index_label'].font_size = '16sp'
                
                # 更新状态
                self.status_label.text = f'{self.red_index + 1} number: {red_item["number"]}...'
                self.progress_label.text = f'{self.red_index + 1}/{len(self.red_array)} | 0/{len(self.blue_array)}'
                
                # 移动到下一个红区索引
                self.red_index += 1
                
                # 如果红区播放完毕，切换到蓝区播放
                if self.red_index >= len(self.red_array):
                    self.current_phase = 2
                    self.status_label.text = '...'
                    self.status_label.color = (0.6, 0.6, 1, 1)
                    
                    # 红区播放完成后闪烁一次
                    for item in self.red_labels:
                        from kivy.animation import Animation
                        anim = Animation(color=(1, 0.5, 0.5, 1), duration=0.3) + \
                               Animation(color=(1, 0.8, 0.8, 1), duration=0.3)
                        anim.start(item['label'])
        
        elif self.current_phase == 2:  # 蓝区播放阶段
            # 播放蓝区数字
            if self.blue_index < len(self.blue_array):
                blue_item = self.blue_labels[self.blue_index]
                blue_item['label'].text = str(blue_item['number'])
                
                # 淡入动画效果
                from kivy.animation import Animation
                anim = Animation(color=(0.8, 0.8, 1, 1), duration=0.5)
                anim.start(blue_item['label'])
                
                # 高亮蓝区索引
                blue_item['index_label'].color = (0.3, 0.3, 1, 1)
                blue_item['index_label'].font_size = '16sp'
                
                # 更新状态
                self.status_label.text = f'... {self.blue_index + 1} ...: {blue_item["number"]}'
                self.progress_label.text = f'...: {len(self.red_array)}/{len(self.red_array)} | ...: {self.blue_index + 1}/{len(self.blue_array)}'
                
                # 移动到下一个蓝区索引
                self.blue_index += 1
                
                # 如果蓝区播放完毕，完成播放
                if self.blue_index >= len(self.blue_array):
                    self.current_phase = 3
                    self.finish_play()
    
    def finish_play(self):
        """播放完成"""
        self.playing = False
        self.current_phase = 3
        
        # 重新启用按钮
        self.play_button.disabled = False
        self.play_button.text = 'Replay'
        self.play_button.background_color = (0.4, 0.2, 0.8, 1)
        
        self.status_label.text = 'Done'
        self.status_label.color = (0.8, 0.4, 0.8, 1)
        
        self.progress_label.text = f'{len(self.red_array)}/{len(self.red_array)} | {len(self.blue_array)}/{len(self.blue_array)}'
        
        # 所有数字显示完成后，蓝区闪烁一次
        for item in self.blue_labels:
            from kivy.animation import Animation
            anim = Animation(color=(0.5, 0.5, 1, 1), duration=0.3) + \
                   Animation(color=(0.8, 0.8, 1, 1), duration=0.3)
            anim.start(item['label'])
        
        # 停止定时器
        Clock.unschedule(self.show_next_number)
    
    def reset_all(self):
    
        # 重置按钮和状态
        self.play_button.disabled = False
        self.play_button.text = 'Start'
        self.play_button.background_color = (0.2, 0.6, 0.8, 1)
        self.status_label.text = 'Start Btn Pressed'
        self.status_label.color = (0.9, 0.9, 0.9, 1)
        self.progress_label.text = ''


    def fetch_data(self, instance):
        self.clickBtn()
        # 在线程中执行网络请求，避免阻塞UI
        threading.Thread(target=self._do_fetch).start()
    
    def _do_fetch(self):
        try:
            self.data_label.text = "Fetching data..."
            waitTime = random.randint(3, 8)
            #sleep(waitTime) 
            # 从服务器GET数据（替换成你的服务器URL）
            response = requests.get("http://localhost:8000/api/hello/")
            if response.status_code == 200:
                data = response.json()  # 解析JSON
                # 更新UI（必须在主线程）
                self.data_label.text = "Done !!!"
                Clock.schedule_once(lambda dt: self.update_label(data), 0)
            else:
                self.data_label.text = "Request fail: " + str(response.status_code)
        except Exception as e:
            self.data_label.text = "Error: " + str(e)

    def update_label(self, data):
            redStr = data['red']
            blueStr = data['blue']
            self.red_array = list(map(int, redStr.split(',')))
            self.blue_array = list(map(int, blueStr.split(',')))
            self.init_array_display()
            self.start_play(instance=None)

if __name__ == '__main__':
    SimpleArrayDisplayApp().run()
