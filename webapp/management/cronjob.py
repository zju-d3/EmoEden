from django.core.management.base import BaseCommand
from webapp.models import StoryProfile  # 替换成你自己的模型
import os
import json
import datetime

def pp():
    print("hello")
    current_time = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    file_name = f"/Users/ziyuchen/Documents/ASD/frame/web/webapp/story/output_{current_time}.txt"
    file_name = f"C:/Users/10235/Desktop/ASD_Web/web/webapp/story/story/output_{current_time}.txt"

    with open(file_name, "w") as f:
        for i in range(1, 100):
            f.write(str(i) + "\n")



class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        # 获取所有的StoryProfile记录
        profiles = StoryProfile.objects.all()

        # 遍历每个记录，并将其转换为JSON格式
        data = []
        for profile in profiles:
            # 将单个记录转换为字典格式
            profile_data = {
                'user_id': profile.user.id,
                'home_angry': profile.home_angry,
                'home_sad': profile.home_sad,
                'home_panic': profile.home_panic,
                'play_angry': profile.play_angry,
                'play_sad': profile.play_sad,
                'play_panic': profile.play_panic,
                # ...添加其他字段...
                'car_panic': profile.car_panic,
            }
            # 将单个记录字典添加到列表中
            data.append(profile_data)

        # 将整个列表转换为JSON格式
        json_data = json.dumps(data, indent=4)

        # 在控制台输出JSON格式数据
        print(json_data)

        # 可以在控制台输出一些信息，以便查看定时任务是否正常运行
        self.stdout.write(self.style.SUCCESS('Custom cronjob executed successfully.'))