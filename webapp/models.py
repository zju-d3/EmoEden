# Create your models here.
from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    """
    用户个人资料模型。
    """

    user = models.OneToOneField(User, on_delete=models.CASCADE)  # 关联用户表
    api_key = models.CharField(max_length=100, blank=True, null=True)  # API密钥
    name = models.CharField(max_length=50, blank=True, null=True)  # 姓名
    gender = models.CharField(max_length=10, blank=True, null=True)  # 性别
    diagnostic = models.CharField(max_length=50, blank=True, null=True)  # 诊断
    area = models.CharField(max_length=50, blank=True, null=True)  # 地区
    hobby = models.CharField(max_length=50, blank=True, null=True)  # 爱好
    food_like = models.CharField(max_length=50, blank=True, null=True)  # 喜欢的食物
    food_dislike = models.CharField(max_length=50, blank=True, null=True)  # 不喜欢的食物
    event_like = models.CharField(max_length=50, blank=True, null=True)  # 喜欢的事件
    event_dislike = models.CharField(max_length=50, blank=True, null=True)  # 不喜欢的事件
    phrase = models.CharField(max_length=50, blank=True, null=True)  # 特定短语
    age = models.CharField(max_length=10, blank=True, null=True)  # 年龄
    role = models.CharField(max_length=100, blank=True, null=True)  # 角色
    current_record_id = models.IntegerField(default=0)  # 当前记录ID
    ai_name = models.CharField(max_length=20, blank=True, null=True)  # AI名称
    ai_char = models.CharField(max_length=20, blank=True, null=True)  # AI角色
    recent = models.CharField(max_length=200, blank=True, null=True)  # 最近记录


class StoryProfile(models.Model):
    """
    故事个人资料模型。
    """

    user = models.OneToOneField(User, on_delete=models.CASCADE)  # 关联用户表
    OPTIONS = [
        (0, 'False'),
        (1, 'True'),
        (2, '未设置'),
    ]

    # 18个字段的映射
    home_angry = models.IntegerField(choices=OPTIONS, default=2)  # 家庭 - 生气
    home_sad = models.IntegerField(choices=OPTIONS, default=2)  # 家庭 - 悲伤
    home_panic = models.IntegerField(choices=OPTIONS, default=2)  # 家庭 - 恐慌

    play_angry = models.IntegerField(choices=OPTIONS, default=2)  # 娱乐 - 生气
    play_sad = models.IntegerField(choices=OPTIONS, default=2)  # 娱乐 - 悲伤
    play_panic = models.IntegerField(choices=OPTIONS, default=2)  # 娱乐 - 恐慌

    school_angry = models.IntegerField(choices=OPTIONS, default=2)  # 校园 - 生气
    school_sad = models.IntegerField(choices=OPTIONS, default=2)  # 校园 - 悲伤
    school_panic = models.IntegerField(choices=OPTIONS, default=2)  # 校园 - 恐慌

    eat_angry = models.IntegerField(choices=OPTIONS, default=2)  # 用餐 - 生气
    eat_sad = models.IntegerField(choices=OPTIONS, default=2)  # 用餐 - 悲伤
    eat_panic = models.IntegerField(choices=OPTIONS, default=2)  # 用餐 - 恐慌

    shop_angry = models.IntegerField(choices=OPTIONS, default=2)  # 购物 - 生气
    shop_sad = models.IntegerField(choices=OPTIONS, default=2)  # 购物 - 悲伤
    shop_panic = models.IntegerField(choices=OPTIONS, default=2)  # 购物 - 恐慌

    car_angry = models.IntegerField(choices=OPTIONS, default=2)  # 交通 - 生气
    car_sad = models.IntegerField(choices=OPTIONS, default=2)  # 交通 - 悲伤
    car_panic = models.IntegerField(choices=OPTIONS, default=2)  # 交通 - 恐慌


class ImageProfile(models.Model):
    """
    图像个人资料模型。
    """

    user = models.OneToOneField(User, on_delete=models.CASCADE)  # 关联用户表
    avatar = models.ImageField(upload_to='avatar', default='avatar/default_avatar.png')  # 头像图片

    def __str__(self):
        return self.user.username  # 返回用户用户名


class RecordAnswer(models.Model):
    """
    记录答案模型。
    """

    user = models.CharField(max_length=20, blank=True, null=True)  # 用户
    date = models.DateField()  # 日期
    place = models.CharField(max_length=20)  # 地点

    mood1 = models.CharField(max_length=20)  # 心情1
    mood2 = models.CharField(max_length=20)  # 心情2
    mood3 = models.CharField(max_length=20)  # 心情3

    story_p1 = models.TextField()  # 故事段落1
    story_p2 = models.TextField()  # 故事段落2
    story_p3 = models.TextField()  # 故事段落3
    story_p4 = models.TextField()  # 故事段落4

    q1_mood = models.BooleanField(default=False)  # 问题1心情
    q2_mood = models.BooleanField(default=False)  # 问题2心情
    q3_mood = models.BooleanField(default=False)  # 问题3心情
    rate = models.IntegerField(default=0)  # 评分

    q1_init = models.CharField(max_length=200, blank=True, null=True)  # 问题1初始化
    q2_init = models.CharField(max_length=200, blank=True, null=True)  # 问题2初始化
    q3_init = models.CharField(max_length=200, blank=True, null=True)  # 问题3初始化
    summary_init = models.CharField(max_length=200)  # 总结初始化

    q1_answer = models.CharField(max_length=200)  # 问题1答案
    q2_answer = models.CharField(max_length=200)  # 问题2答案
    q3_answer = models.CharField(max_length=200)  # 问题3答案

    gpt_1 = models.TextField()  # GPT-3生成1
    gpt_2 = models.TextField()  # GPT-3生成2
    gpt_3 = models.TextField()  # GPT-3生成3
    gpt_sum = models.TextField()  # GPT-3生成总结

    summary = models.CharField(max_length=200)  # 总结

    recent = models.CharField(max_length=200, blank=True, null=True)  # 最近记录
