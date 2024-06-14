# views.py
from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.http import JsonResponse
from django.conf import settings
from .models import UserProfile, ImageProfile, RecordAnswer
import datetime
import json
import os
import subprocess
from webapp.chat import prompt, tts, asr, chat
from asgiref.sync import async_to_sync
from .forms import AvatarUploadForm


# 用户登录视图，处理用户登录请求，接收POST请求，验证表单数据，并重定向到登录后的页面
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            user_profile, created = UserProfile.objects.get_or_create(user=request.user)
            if user_profile.diagnostic == "H":
                return redirect('dashboard2')  # 重定向到登录后的页面
            else:
                return redirect('dashboard')  # 重定向到登录后的页面
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})


# 用户注册视图，处理用户注册请求，接收POST请求，验证表单数据，并重定向到注册后的页面
def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')  # 重定向到注册后的页面
    else:
        form = UserCreationForm()
    return render(request, 'register.html', {'form': form})


# 获取用户当天回答记录的场景列表
def getScenes(usr):
    today = datetime.date.today()
    print(str(today))
    records = RecordAnswer.objects.filter(user=usr.name, date=str(today))
    scenes = []
    for record in records:
        if record.summary != "":
            scenes.append(record.place)
    print(list(set(scenes)))
    return list(set(scenes))


# 用户仪表盘视图，需要登录后才能访问，处理用户的主页请求，展示用户信息和情感记录
@login_required
def dashboard(request):
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)
    avatar = f"/static/avatar/{user_profile.name}/喜.png"
    scenes = getScenes(user_profile)
    if user_profile.name == None:
        user_profile.name = "未设置用户名"
    if request.method == 'POST':
        mood = request.POST.get('mood', None)
        if mood in ['难过', '生气', '害怕']:
            request.session['mood'] = mood

        recent_experience = request.POST.get('recent_experience', None)
        if recent_experience is not None:
            request.session['recent'] = recent_experience
            user_profile.recent = recent_experience
        user_profile.save()

        place = request.POST.get('place', None)
        if place in ['家庭', '娱乐', '交通', '校园', '购物', '用餐']:
            request.session['place'] = place
            prompt.init_dialog(request)
            file_name = datetime.datetime.now().strftime('%Y%m%d%H%M%S') + '.mp3'
            request.session['tts_file'] = str(settings.BASE_DIR / 'webapp/tts' / file_name)
            # 暂时注释
            async_to_sync(async_to_sync(tts.ttsTrans)(request.session['gpt'], request.session['tts_file']))
            request.session['tts_file'] = '/tts/' + file_name
            # tts.ttsTrans(request.session['gpt'], request.session['tts_file'])
            return redirect('dialog')
    # print(request.session['recent'])
    return render(request, 'dashboard.html', {'user_profile': user_profile, 'scenes': scenes, 'avatar': avatar})


# 高级用户仪表盘视图，需要登录后才能访问，处理高级用户的主页请求，展示用户信息和情感记录
@login_required
def dashboard2(request):
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)
    avatar = f"/static/avatar/{user_profile.name}/喜.png"
    scenes = getScenes(user_profile)
    if user_profile.name == None:
        user_profile.name = "未设置用户名"
    if request.method == 'POST':
        high_mood_1 = request.POST.get('high_mood_1', None)
        if high_mood_1 in ['感激', '敬佩']:
            request.session['high_mood_1'] = high_mood_1
        high_mood_2 = request.POST.get('high_mood_2', None)
        if high_mood_2 in ['懊悔', '羞愧']:
            request.session['high_mood_2'] = high_mood_2
        high_mood_3 = request.POST.get('high_mood_3', None)
        if high_mood_3 in ['感激', '敬佩']:
            request.session['high_mood_3'] = high_mood_3

        recent_experience = request.POST.get('recent_experience', None)
        if recent_experience is not None:
            request.session['recent'] = recent_experience
            user_profile.recent = recent_experience
        user_profile.save()
        place = request.POST.get('place', None)
        if place in ['家庭', '娱乐', '交通', '校园', '购物', '用餐']:
            request.session['place'] = place
            prompt.init_dialog(request, True)
            file_name = datetime.datetime.now().strftime('%Y%m%d%H%M%S') + '.mp3'
            request.session['tts_file'] = str(settings.BASE_DIR / 'webapp/tts' / file_name)
            async_to_sync(async_to_sync(tts.ttsTrans)(request.session['gpt'], request.session['tts_file']))
            request.session['tts_file'] = '/tts/' + file_name
            # tts.ttsTrans(request.session['gpt'], request.session['tts_file'])
            return redirect('dialog2')
    # print(request.session['recent'])
    return render(request, 'dashboard2.html', {'user_profile': user_profile, 'scenes': scenes, 'avatar': avatar})


@login_required
def uinfo_view(request):
    """
    获取并处理用户个人信息页面请求。
    GET请求时，返回用户个人信息页面。
    POST请求时，接收表单数据更新用户个人信息，并根据用户的诊断结果重定向到不同的仪表板页面。

    :param request: HttpRequest对象，包含用户请求信息
    :return: HttpResponse对象，个人信息页面或重定向响应
    """
    # 获取当前用户的个人信息
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        user_profile.age = request.POST['age']
        user_profile.gender = request.POST['gender']
        user_profile.area = request.POST['area']
        user_profile.name = request.POST['name']
        user_profile.diagnostic = request.POST['diagnostic']
        user_profile.hobby = request.POST['hobby']
        user_profile.food_like = request.POST['food_like']
        user_profile.food_dislike = request.POST['food_dislike']
        user_profile.event_like = request.POST['event_like']
        user_profile.event_dislike = request.POST['event_dislike']
        user_profile.phrase = request.POST['phrase']
        user_profile.role = request.POST['role']
        user_profile.ai_name = request.POST['ai_name']
        user_profile.save()
        if user_profile.diagnostic == 'H':
            return redirect('dashboard2')
        else:
            return redirect('dashboard')
    else:
        if user_profile.age == None:
            user_profile.age = ""
        if user_profile.gender == None:
            user_profile.gender = ""
        if user_profile.area == None:
            user_profile.area = ""
        if user_profile.name == None:
            user_profile.name = ""
        if user_profile.diagnostic == None:
            user_profile.diagnostic = ""
        if user_profile.hobby == None:
            user_profile.hobby = ""
        if user_profile.food_like == None:
            user_profile.food_like = ""
        if user_profile.food_dislike == None:
            user_profile.food_dislike = ""
        if user_profile.event_like == None:
            user_profile.event_like = ""
        if user_profile.event_dislike == None:
            user_profile.event_dislike = ""
        if user_profile.phrase == None:
            user_profile.phrase = ""
        if user_profile.role == None:
            user_profile.role = "/static/img/roles/3%E8%93%9D%E9%80%8F%E5%85%94/%E8%93%9D%E9%80%8F%E5%85%94.png"
        user_profile.save()
        avatar = f"/static/avatar/{user_profile.name}/喜.png"
    return render(request, 'uinfo.html', {'user_profile': user_profile, 'avatar': avatar})


def getRolePath(request, mood_opt):
    """
    根据用户情绪和角色信息，获取角色图片的路径。
    :param request: HttpRequest对象，包含用户请求信息
    :param mood_opt: 字符串，表示用户情绪选项
    :return: 字符串，角色图片的路径
    """
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)
    mood_dic = {
        '难过': '哀',
        '生气': '怒',
        '害怕': '惧',
        '开心': '喜',
        '感激': '喜',
        '敬佩': '喜',
        '懊悔': '哀',
        '羞愧': '惧',

    }
    mood = mood_dic[mood_opt]
    role = user_profile.role
    role_name = role.split('/')[4]
    return f'/static/img/roles/{role_name}/{mood}.png'


@login_required
def dialog(request):
    """
    处理用户对话请求，根据对话次数和用户输入生成响应，并更新对话状态。

    :param request: HttpRequest对象，包含用户请求信息
    :return: HttpResponse对象，对话页面
    """
    role_path = getRolePath(request, '开心')
    tid = 0

    if request.session['dialog_times'] == -1:
        return redirect('log')
    elif request.session['dialog_times'] == 0:
        request.session['dialog_times'] += 1
        tid = 1

    elif request.session['dialog_times'] == 1:
        request.session['dialog_times'] += 1
        tid = 2
        user_words = request.session['user_words']
        judge = chat.gpt_judge(user_words, request)
        if judge[1]:
            request.session['gpt'] = judge[0] + request.session['story_list'][0]
            request.session['gpt'] += (
                        request.session['questions'][chat.init_questions(request, True)] + request.session['questions'][
                    chat.init_questions(request, False)])
        else:
            request.session['gpt'] = judge[0]
            request.session['dialog_times'] = -1
        update_tts(request, True)
    elif request.session['dialog_times'] == 2:
        request.session['dialog_times'] += 1
        tid = 3
        asw_temp = prompt.answer_template(0, request.session['guess'], "开心", request.session['user_words'], request)
        request.session['answer_template'].append({"role": "system", "content": request.session['story_list'][0]})
        res1 = chat.answer_openai(asw_temp, request)
        request.session['gpt'] = res1 + "\n让我们一起开始听故事的第二部分吧！\n" + request.session['story_list'][1]
        request.session['gpt'] += (
                    request.session['questions'][chat.init_questions(request, True)] + request.session['questions'][
                chat.init_questions(request, False)])
        role_path = getRolePath(request, request.session['mood'])
        update_tts(request, True)
        update_answer(request, 1, request.session['guess'], request.session['user_words'], res1)

    elif request.session['dialog_times'] == 3:
        request.session['dialog_times'] += 1
        tid = 4
        asw_temp = prompt.answer_template(0, request.session['guess'], request.session['mood'],
                                          request.session['user_words'], request)
        request.session['answer_template'].append({"role": "system", "content": request.session['story_list'][1]})
        res1 = chat.answer_openai(asw_temp, request)
        request.session['gpt'] = res1 + "\n让我们一起开始听故事的最后一部分吧！\n" + request.session['story_list'][2]
        request.session['gpt'] += (
                    request.session['questions'][chat.init_questions(request, True)] + request.session['questions'][
                chat.init_questions(request, False)])
        update_tts(request, True)
        update_answer(request, 2, request.session['guess'], request.session['user_words'], res1)

    elif request.session['dialog_times'] == 4:
        request.session['dialog_times'] += 1
        tid = 5
        asw_temp = prompt.answer_template(0, request.session['guess'], "开心", request.session['user_words'], request)
        request.session['answer_template'].append({"role": "system", "content": request.session['story_list'][2]})
        res1 = chat.answer_openai(asw_temp, request)
        request.session['gpt'] = res1 + request.session['story_list'][
            3] + f'\n{UserProfile.objects.get(user=request.user).name}，听完我的这个故事，你有什么心里话想对我说吗？'
        update_tts(request, True)
        update_answer(request, 3, request.session['guess'], request.session['user_words'], res1)

    elif request.session['dialog_times'] == 5:
        request.session['dialog_times'] += 1
        tid = 6
        # user_words = asr.asrTrans(request.session['asr_file'])
        user_words = request.session['user_words']
        request.session['answer_template'].append({"role": "system", "content": request.session['story_list'][0] +
                                                                                request.session['story_list'][1] +
                                                                                request.session['story_list'][2]})
        res = chat.answer_openai(
            f'这是听完整个故事，{UserProfile.objects.get(user=request.user).name}想对你说的话：{user_words}\n请做出回应。', request)
        request.session['gpt'] = res + '\n好啦！这就是我想与你分享的故事，我们下次再见！'
        request.session['dialog_times'] = -1
        update_tts(request, True)
        update_answer(request, 4, "", request.session['user_words'], res)

    return render(request, 'dialog.html', {'random_word': request.session['gpt'], 'role_path': role_path, 'tid': tid,
                                           'child_avatar': getChildAvatar(request)})


def upload_child_input(request):
    """
    接收并处理用户输入信息。
    :param request: HttpRequest对象，包含用户请求信息
    :return: JsonResponse对象，包含处理后的用户输入
    """
    data = json.loads(request.body)
    user_words = data.get('user_words')
    request.session['user_words_init'] = user_words
    request.session['user_words'] = user_words
    return JsonResponse({'user_words': user_words})


def upload_audio(request):
    """
    处理用户上传音频文件的请求。
    如果请求方法为POST且包含'audio_file'字段，则保存音频文件，转换为WAV格式，并提取用户语音。
    否则，如果请求方法为POST且包含'user_words'字段，则根据对话状态更新用户语音。

    :param request: HttpRequest对象，包含用户请求信息
    :return: JsonResponse对象，包含处理后的用户语音
    """
    if request.method == 'POST' and 'audio_file' in request.FILES:
        audio_file = request.FILES['audio_file']
        # 使用当前时间生成一个独一无二的文件名
        filename = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
        with open(f'webapp/media/{filename}.webm', 'wb') as f:
            for chunk in audio_file.chunks():
                f.write(chunk)
        subprocess.run(
            ['ffmpeg', '-i', f'webapp/media/{filename}.webm', '-ar', '16000', f'webapp/media/{filename}.wav'])
        os.remove(f'webapp/media/{filename}.webm')
        request.session['asr_file'] = str(settings.BASE_DIR / 'webapp/media' / filename) + '.wav'
        user_words = asr.asrTrans(request.session['asr_file'])
        user_words = prompt.extend_user(user_words)
        request.session['user_words'] = user_words
        return JsonResponse({'user_words': user_words})
        # return HttpResponse(status=204)
    else:
        data = json.loads(request.body)
        user_words = data.get('user_words')
        request.session['user_words_init'] = user_words
        if request.session['dialog_times'] == 1:
            user_words = prompt.extend_user(user_words, '', True)
        else:
            if request.session['dialog_times'] == 2:
                user_words = prompt.extend_user(user_words, request.session['story_list'][0])
            elif request.session['dialog_times'] == 3:
                user_words = prompt.extend_user(user_words, request.session['story_list'][1])
            elif request.session['dialog_times'] == 4:
                user_words = prompt.extend_user(user_words, request.session['story_list'][2])
            else:
                total = request.session['story_list'][0] + request.session['story_list'][1] + \
                        request.session['story_list'][2]
                user_words = prompt.extend_user(user_words, total)
        request.session['extend'] = user_words
        request.session['user_words'] = user_words
        update_tts(request, False)
        return JsonResponse({'user_words': user_words, 'extend_file': request.session['extend_file']})
        # return render(request, 'dialog.html')


def update_mood(request):
    """
    处理用户更新情绪的请求。
    如果请求方法为POST，则尝试解析JSON数据，更新会话中的情绪猜测，并返回结果。
    否则，返回错误响应。

    :param request: HttpRequest对象，包含用户请求信息
    :return: JsonResponse对象，包含情绪猜测的结果
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            mood = data.get('mood')
            t = data.get('tid')
            guess = ""
            ans = ""
            if t == 2:
                guess = data.get('mood')
                ans = "开心"
            if t == 3:
                guess = data.get('mood')
                ans = request.session['mood']
            if t == 4:
                guess = data.get('mood')
                ans = "开心"
            # 在这里对按钮内容进行处理
            # 假设我们将按钮内容保存到会话中
            request.session['guess'] = mood
            if guess == ans:
                return JsonResponse({'status': 'success', 'ansTrue': 1})
            else:
                return JsonResponse({'status': 'success', 'ansTrue': 0})
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON data'})
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'})


def update_mood_pro(request):
    """
    处理高级用户更新情绪的请求。
    如果请求方法为POST，则尝试解析JSON数据，更新会话中的情绪猜测，并返回结果。
    否则，返回错误响应。

    :param request: HttpRequest对象，包含用户请求信息
    :return: JsonResponse对象，包含情绪猜测的结果
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            mood = data.get('mood')
            t = data.get('tid')
            guess = ""
            ans = ""
            if t == 2:
                guess = data.get('mood')
                ans = request.session['high_mood_1']
            if t == 3:
                guess = data.get('mood')
                ans = request.session['high_mood_2']
            if t == 4:
                guess = data.get('mood')
                ans = request.session['high_mood_3']
            # 在这里对按钮内容进行处理
            # 假设我们将按钮内容保存到会话中
            request.session['guess'] = mood
            if guess == ans:
                return JsonResponse({'status': 'success', 'ansTrue': 1})
            else:
                return JsonResponse({'status': 'success', 'ansTrue': 0})
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON data'})
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'})


def update_tts(request, gpt):
    """
    更新TTS语音文件。
    如果gpt为True，则使用当前会话中的GPT对话内容生成TTS语音。
    否则，使用当前会话中的用户语音生成扩充语音的TTS语音。

    :param request: HttpRequest对象，包含用户请求信息
    :param gpt: 布尔值，表示是否使用GPT对话内容生成TTS语音
    :return: 空响应
    """
    file_name = datetime.datetime.now().strftime('%Y%m%d%H%M%S') + '.mp3'

    # 暂时注释
    if gpt:
        request.session['tts_file'] = str(settings.BASE_DIR / 'webapp/tts' / file_name)
        async_to_sync(async_to_sync(tts.ttsTrans)(request.session['gpt'], request.session['tts_file']))
        request.session['tts_file'] = '/tts/' + file_name
    else:
        print('生成扩充语音')
        request.session['extend_file'] = str(settings.BASE_DIR / 'webapp/tts' / file_name)
        async_to_sync(async_to_sync(tts.ttsTrans)(request.session['extend'], request.session['extend_file']))
        request.session['extend_file'] = '/tts/' + file_name


@login_required
def upload_avatar(request):
    """
    处理用户上传头像的请求。
    如果请求方法为POST，则验证上传的文件，并保存到数据库。
    否则，返回上传表单。

    :param request: HttpRequest对象，包含用户请求信息
    :return: HttpResponse对象，包含上传表单或上传成功的响应
    """
    try:
        image_profile = request.user.imageprofile
    except ImageProfile.DoesNotExist:
        # 如果没有关联的 ImageProfile 对象，则创建一个
        image_profile = ImageProfile.objects.create(user=request.user)

    if request.method == 'POST':
        form = AvatarUploadForm(request.POST, request.FILES, instance=image_profile)
        if form.is_valid():
            form.save()
            # return redirect('show_avatar')
    else:
        form = AvatarUploadForm(instance=image_profile)

    # return render(request, 'avatar/upload_avatar.html', {'form': form})
    return HttpResponse(status=200)


@login_required
def show_avatar(request):
    """
    显示用户头像的页面。
    如果用户有头像，则显示用户头像。
    否则，显示默认头像。

    :param request: HttpRequest对象，包含用户请求信息
    :return: HttpResponse对象，包含显示头像的页面
    """
    try:
        avatar_url = request.user.imageprofile.avatar.url
    except ImageProfile.DoesNotExist:
        # 如果没有关联的 ImageProfile 对象，则使用默认头像或其他错误处理逻辑
        avatar_url = 'avatar/default_avatar.png'  # 替换为你的默认头像路径

    return render(request, 'avatar/show_avatar.html', {'avatar_url': avatar_url})


@login_required
def dialog2(request):
    """
    处理高级用户的对话请求。
    根据对话次数和用户输入生成响应，并更新对话状态。

    :param request: HttpRequest对象，包含用户请求信息
    :return: HttpResponse对象，对话页面
    """
    role_path = getRolePath(request, '开心')
    tid = 0

    if request.session['dialog_times'] == -1:
        return redirect('log')
    elif request.session['dialog_times'] == 0:
        request.session['dialog_times'] += 1
        tid = 1

    elif request.session['dialog_times'] == 1:
        request.session['dialog_times'] += 1
        tid = 2
        user_words = request.session['user_words']
        judge = chat.gpt_judge(user_words, request)
        if judge[1]:
            request.session['gpt'] = judge[0] + request.session['story_list'][0]
            request.session['gpt'] += (
                    request.session['questions'][chat.init_questions(request, True)] + request.session['questions'][
                chat.init_questions(request, False)])
        else:
            request.session['gpt'] = judge[0]
            request.session['dialog_times'] = -1
        update_tts(request, True)
    elif request.session['dialog_times'] == 2:
        # 面对第一段内容
        request.session['dialog_times'] += 1
        tid = 3
        asw_temp = prompt.answer_template(0, request.session['guess'], request.session['high_mood_1'],
                                          request.session['user_words'], request)
        request.session['answer_template'].append({"role": "system", "content": request.session['story_list'][0]})
        res1 = chat.answer_openai(asw_temp, request)
        request.session['gpt'] = res1 + "\n让我们一起开始听故事的第二部分吧！\n" + request.session['story_list'][1]
        # request.session['former_idx'] = chat.init_questions(request)
        request.session['gpt'] += (
                request.session['questions'][chat.init_questions(request, True)] + request.session['questions'][
            chat.init_questions(request, False)])
        role_path = getRolePath(request, request.session['high_mood_2'])
        update_tts(request, True)
        update_answer(request, 1, request.session['guess'], request.session['user_words'], res1)

    elif request.session['dialog_times'] == 3:
        request.session['dialog_times'] += 1
        tid = 4
        asw_temp = prompt.answer_template(0, request.session['guess'], request.session['high_mood_2'],
                                          request.session['user_words'], request)
        request.session['answer_template'].append({"role": "system", "content": request.session['story_list'][1]})
        res1 = chat.answer_openai(asw_temp, request)
        request.session['gpt'] = res1 + "\n让我们一起开始听故事的最后一部分吧！\n" + request.session['story_list'][2]
        request.session['gpt'] += (
                request.session['questions'][chat.init_questions(request, True)] + request.session['questions'][
            chat.init_questions(request, False)])
        update_tts(request, True)
        update_answer(request, 2, request.session['guess'], request.session['user_words'], res1)

    elif request.session['dialog_times'] == 4:
        # print("第四部分")
        request.session['dialog_times'] += 1
        tid = 5
        asw_temp = prompt.answer_template(0, request.session['guess'], request.session['high_mood_3'],
                                          request.session['user_words'], request)
        request.session['answer_template'].append({"role": "system", "content": request.session['story_list'][2]})
        res1 = chat.answer_openai(asw_temp, request)
        request.session['gpt'] = res1 + request.session['story_list'][
            3] + f'\n{UserProfile.objects.get(user=request.user).name}，听完我的这个故事，你有什么心里话想对我说吗？'
        update_tts(request, True)
        update_answer(request, 3, request.session['guess'], request.session['user_words'], res1)

    elif request.session['dialog_times'] == 5:
        request.session['dialog_times'] += 1
        tid = 6
        # user_words = asr.asrTrans(request.session['asr_file'])
        user_words = request.session['user_words']
        request.session['answer_template'].append({"role": "system", "content": request.session['story_list'][0] +
                                                                                request.session['story_list'][1] +
                                                                                request.session['story_list'][2]})
        res = chat.answer_openai(
            f'这是听完整个故事，{UserProfile.objects.get(user=request.user).name}想对你说的话：{user_words}\n请做出回应。',
            request)
        request.session['gpt'] = res + '\n好啦！这就是我想与你分享的故事，我们下次再见！'
        request.session['dialog_times'] = -1
        update_tts(request, True)
        update_answer(request, 4, "", request.session['user_words'], res)

    return render(request, 'dialog2.html', {'random_word': request.session['gpt'], 'role_path': role_path, 'tid': tid,
                                            'child_avatar': getChildAvatar(request)})


def getChildAvatar(request):
    """
    获取并返回用户的头像路径。

    :param request: HttpRequest对象，包含用户请求信息
    :return: 字符串，表示用户头像的静态文件路径
    """
    usr = UserProfile.objects.get(user=request.user)
    return f"/static/avatar/{usr.name}"


@login_required
def update_answer(request, q_id, mood, usr_words, gpt_answer):  # type || request int string string
    """
    更新用户对于特定问题的回答，并记录心情状态。

    :param request: HttpRequest对象，包含用户请求信息
    :param q_id: int，问题编号
    :param mood: string，用户回答问题时的心情
    :param usr_words: string，用户的回答
    :param gpt_answer: string，AI助手生成的回答
    :return: 无返回值
    """
    usr = UserProfile.objects.get(user=request.user)  # 获取当前用户的用户资料
    cur_record = usr.current_record_id  # 获取用户当前记录的ID
    record = RecordAnswer.objects.get(id=cur_record)  # 获取当前记录
    record.date = str(datetime.date.today())  # 更新记录的日期为今天
    print(record)  # 打印记录信息
    record.recent = usr.recent  # 更新记录的最近状态

    if q_id == 1:  # 如果问题编号为1
        record.q1_answer = usr_words  # 更新记录的问题1回答
        record.q1_init = request.session['user_words_init']  # 更新记录的问题1初始回答
        if (mood == request.session['high_mood_1']) or (request.session['mood'] != '' and mood == "开心"):
            record.q1_mood = True  # 如果心情符合预期，则更新问题1的心情状态
            record.rate += 1  # 更新记录的评分
    elif q_id == 2:  # 如果问题编号为2
        record.gpt_1 = gpt_answer  # 更新记录的GPT助手问题1的回答
        record.q2_answer = usr_words  # 更新记录的问题2回答
        record.q2_init = request.session['user_words_init']  # 更新记录的问题2初始回答
        if (mood == request.session['high_mood_2']) or (mood == request.session['mood']):
            record.q2_mood = True  # 如果心情符合预期，则更新问题2的心情状态
            record.rate += 1  # 更新记录的评分
    elif q_id == 3:  # 如果问题编号为3
        record.gpt_2 = gpt_answer  # 更新记录的GPT助手问题2的回答
        record.q3_answer = usr_words  # 更新记录的问题3回答
        record.q3_init = request.session['user_words_init']  # 更新记录的问题3初始回答
        if (mood == request.session['high_mood_3']) or (request.session['mood'] != '' and mood == "开心"):
            record.q3_mood = True  # 如果心情符合预期，则更新问题3的心情状态
            record.rate += 1  # 更新记录的评分
    elif q_id == 4:  # 如果问题编号为4
        record.gpt_3 = gpt_answer  # 更新记录的GPT助手问题3的回答
        record.summary = usr_words  # 更新记录的总结回答
        record.summary_init = request.session['user_words_init']  # 更新记录的总结初始回答
        record.gpt_sum = gpt_answer  # 更新记录的总结GPT助手回答

    record.save()  # 保存记录


@login_required
def log_view(request):
    """
    处理用户查看日志的请求，并根据请求类型返回对应的页面。

    :param request: HttpRequest对象，包含用户请求信息
    :return: HttpResponse对象，日志页面
    """
    usr = UserProfile.objects.get(user=request.user)

    if request.method == 'POST':
        return render(request, 'log.html')
    else:
        usr = UserProfile.objects.get(user=request.user)
        cur_record = usr.current_record_id
        cur = datetime.date(2023, 8, 14)
        records = RecordAnswer.objects.filter(user=usr.name, date=str(cur))
        print(len(records))

        data = []
        for i in range(0, 30):
            records = RecordAnswer.objects.filter(user=usr.name, date=str(cur))
            cur = cur + datetime.timedelta(days=1)
            d = []
            count = 0
            for record in records:
                if record.summary != "":
                    d.append({'score': record.rate, 'complete': 1})
                    count += 1
                if count == 6:
                    break
            while len(d) < 6:
                d.append({'score': 0, 'complete': 0})
            data.append(d)
            print('-------')
        return render(request, 'log.html', {'data': data, 'user_profile': usr})


@login_required
def statistics_view(request):
    """
    处理用户查看统计数据的请求，并返回统计数据页面。

    :param request: HttpRequest对象，包含用户请求信息
    :return: HttpResponse对象，统计数据页面
    """
    cur = datetime.date(2023, 8, 14)  # 当前日期设为2023年8月14日
    today = datetime.date.today()  # 获取今天的日期
    user_list = ["立行", "子豪", "卟噜", "小潘", "乖乖", "冰棒", "果果", "钰钰"]  # 用户列表
    place_list = ["家庭", "娱乐", "交通", "校园", "购物", "用餐"]  # 地点列表
    cur_user_index = 0  # 当前用户索引
    data = [
        [""], [], [], [], [], [], [], [], []
    ]  # 初始化数据
    story_data = []  # 初始化故事数据
    while today >= cur:
        data[0].append(str(cur)[5:])  # 将日期添加到数据的第一行
        cur = cur + datetime.timedelta(days=1)  # 日期加一天
    for user in user_list:
        cur = datetime.date(2023, 8, 14)  # 当前日期设为2023年8月14日
        data[cur_user_index + 1].append(user)  # 将用户添加到数据的当前行
        while today >= cur:
            cur_place_index = 0  # 当前地点索引
            res = []  # 结果列表
            correct_score = 0  # 正确得分
            total_score = 0  # 总得分
            for place in place_list:
                temp = f'{place}: '  # 地点字符串
                records = RecordAnswer.objects.filter(date=str(cur), user=user, place=place)  # 获取记录
                score_str = "0/0 "  # 得分字符串
                if len(records) > 0:
                    for record in records:
                        if record.summary != "":
                            score = record.q1_mood + record.q2_mood + record.q3_mood  # 计算得分
                            score_str = f'{score}/3 '  # 更新得分字符串
                            correct_score += score  # 更新正确得分
                            total_score += 3  # 更新总得分
                            break
                        else:
                            if len(records) == 1 and (record.q1_answer != ""):
                                if record.q2_answer == "":
                                    score = int(record.q1_mood)
                                    score_str = f'{score}/1 '
                                    correct_score += score
                                    total_score += 1
                                    break
                                if record.q2_answer != "" and record.q3_answer == "":
                                    score = record.q1_mood + record.q2_mood
                                    score_str = f'{score}/2 '
                                    correct_score += score
                                    total_score += 2
                                    break
                                if record.q2_answer != "" and record.q3_answer != "":
                                    score = record.q1_mood + record.q2_mood + record.q3_mood
                                    score_str = f'{score}/3 '
                                    correct_score += score
                                    total_score += 3
                                    break
                            score_str = f'0/0 '
                temp += score_str  # 添加得分字符串到地点字符串
                res.append(temp)  # 将地点字符串添加到结果列表
                cur_place_index += 1  # 地点索引加一

            if total_score > 0:
                per = str(correct_score / total_score)[0:4]  # 计算百分比
                res.append(f"总计: {correct_score}/{total_score} = {per}")  # 添加总计字符串到结果列表
            else:
                res.append(f"总计: {correct_score}/{total_score}")  # 添加总计字符串到结果列表
            cur = cur + datetime.timedelta(days=1)  # 日期加一天
            data[cur_user_index + 1].append(res)  # 将结果列表添加到数据的当前行
        cur_user_index += 1  # 用户索引加一

    for user in user_list:
        user_story_info = {'user': user, 'dateList': []}  # 用户故事信息
        cur = datetime.date(2023, 8, 14)  # 当前日期设为2023年8月14日
        while today >= cur:
            date_info = {"date": str(cur)[5:], "placeList": []}  # 日期信息
            for place in place_list:
                place_info = {"place": place, "storyList": []}  # 地点信息
                records = RecordAnswer.objects.filter(date=str(cur), user=user, place=place)  # 获取记录
                if len(records) > 0:
                    for record in records:
                        if (record.summary != ""):
                            story_info = {"story_p1": record.story_p1, "q1_init": record.q1_init,
                                          "q1_answer": record.q1_answer,
                                          "story_p2": record.story_p2, "q2_init": record.q2_init,
                                          "q2_answer": record.q2_answer,
                                          "story_p3": record.story_p3, "q3_init": record.q3_init,
                                          "q3_answer": record.q3_answer,
                                          "gpt_1": record.gpt_1, "gpt_2": record.gpt_2, "gpt_3": record.gpt_3,
                                          "gpt_sum": record.gpt_sum,
                                          "story_p4": record.story_p4, "summary_init": record.summary_init,
                                          "summary": record.summary,
                                          "recent": record.recent
                                          }  # 故事信息
                            place_info["storyList"] = story_info  # 更新地点信息的故事列表
                            break
                date_info["placeList"].append(place_info)  # 将地点信息添加到日期信息的地点列表
            user_story_info["dateList"].append(date_info)  # 将日期信息添加到用户故事信息的日期列表
            cur = cur + datetime.timedelta(days=1)  # 日期加一天
        story_data.append(user_story_info)  # 将用户故事信息添加到故事数据列表
    print(story_data)  # 输出故事数据
    return render(request, 'statistics.html', {'data': data, 'story_data': story_data})  # 返回统计数据页面
