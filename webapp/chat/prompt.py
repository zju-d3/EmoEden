import re
from django.http import HttpRequest
from webapp.models import UserProfile, RecordAnswer
from django.conf import settings
from django.utils import timezone
import dashscope

# 这段代码主要是为了生成一个故事，并根据用户的心情和场所，通过AI模型进行分析和回应。
good = f'''
### 第一部分：感激

我是一个叫做咪咪的小猫，喵~，在我家，每天，我都会被家人的呵护所感动。尤其是在厨房里，一股诱人的香气扑鼻而来。

每当我看到家人为我准备的番茄炒蛋时，那个又香又好吃的菜肴让我流口水。我最喜欢的就是番茄炒蛋的味道，真的是太好吃了！每次家人在厨房炒番茄炒蛋，我都会围着他们转，想要尝一口。

### 第二部分：羞愧

有一天，我看到一碗满满的饺子在桌上。香呀！我想上去尝尝，但是...哎哟！碗被我推到地上了，饺子到处都是。我不敢面对家人们的眼神，似乎可以感受到我的内心。我知道他们会为这个小小的错误感到失望。我真的好害怕，害怕家人会生气，于是，我迅速躲到了角落里，蜷缩起来，不敢面对他们的目光。

### 第三部分：敬佩

可是家人没有生气，他们开始包更多的饺子。我悄悄地从角落里探出头来，看到家人忙碌的身影。他们和面、擀皮、包饺子，看起来既熟练又专注。他们的手好快，一个一个的饺子都好圆好圆。我想：“哇，好厉害！”于是我跑过去，轻轻地用鼻子蹭他们，想要帮忙。他们给我一个饺子皮玩，我摆弄着，想要学他们，我多想守护好这温馨的时刻啊。

### 第四部分：总结

通过这个故事，我学到了珍惜他人的关爱和帮助，以及学会勇敢面对自己的错误。当我们犯错时，我们应该勇敢道歉，并努力弥补过失，学习成长。另外，我们也应该敬佩他人的智慧和努力，学习他们的优点，并以他人为榜样。
'''

qmode_1 = 2  # 猜测心情 index 0, 1
qmode_2 = 2  # 说一些话 index 2, 3, 4

ai_name = None
ai_char = None
user_name = None
mood1 = None
mood2 = None
mood3 = None
# 名字：贝贝；年龄：5岁；爱好：画画；喜欢的食物：面包；喜欢的颜色：绿色；最近的经历：刚刚和最好的朋友吵架了很难过
user_info = "名字：贝贝；年龄：5岁；爱好：画画；喜欢的食物：面包；喜欢的颜色：绿色；最近的经历：刚刚和最好的朋友吵架了很难过"
place = "教室"


def answer_template(index, front_msg, front_mood, user_words, request: HttpRequest):
    # front_msg 可以是选择的心情 可以是想说的一句话
    user_profile = UserProfile.objects.get(user=request.user)
    user_name = user_profile.name
    ai_name = request.session['ai_name']
    if index == 0 or index == 2:
        msg = f'''
请记住，你就是故事中的主角{ai_name}，我是{user_name}，请根据下面的要求做出回答：
听完故事，{user_name}猜你当时的心情是{front_msg}的，{user_name}想对你说：{user_words}
现在请你分析：{user_name}的猜测是否和故事中你当时{front_mood}的心情一致？
如果你觉得{user_name}猜测的心情{front_msg}不对，请告诉{user_name}“你当时产生{front_mood}的心情的原因”
以及请你再分析：结合整个故事，听了{user_name}对你说的话{user_words}，你的心情是什么样的？
如果你觉得{user_name}的回答不准确，请告诉{user_name}你期待的回答是什么。
请注意：你需要分别回答以上两个问题，千万不要把这两个问题混淆。
我知道你就是{ai_name}，请直接给出答案，足够简短，在50词左右。
'''
    else:
        msg = f'''
{user_name}的回答：{front_msg}
现在请你分析听了{user_name}的这句话你的心情是什么样的？
以及你期待的回答是什么？为什么期待的是这样的回答？
'''
    # print(msg)
    return msg


def split_text(text):
    print("split_text+++++++++++++++++++++++++++++++++")
    print(text)
    sections_with_delimiter = text.split("###")
    sections = []
    for section in sections_with_delimiter:
        section = section.strip()  # 去除首尾空白
        if section:
            section = "###" + section  # 添加分隔符
            sections.append(section)
    # 去除空白元素
    return sections


def read_txt_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        return content
    except FileNotFoundError:
        print(f"File '{file_path}' not found.")
        return None
    except Exception as e:
        print(f"Error occurred while reading the file: {e}")
        return None


# 函数gen用于生成故事，并保存在对应的文件中。
def gen(user_, place, mood1, mood2, mood3, who_use=True):
    answer = None
    q = [{"role": "system", "content": system_prompt(user_)}, ]
    # q.append({"role": "user", "content": start_q(user_, '教室', ['开心', '难过', '开心'])})
    # q.append({"role": "assistant", "content": good})
    q.append({"role": "user", "content": start_q(user_, '厨房', ['感激', '羞愧', '敬佩'])})
    q.append({"role": "assistant", "content": good})

    # q.append({"role": "user", "content": start_q(user_, '家中', ['感激', '羞愧', '敬佩'])})
    # q.append({"role": "assistant", "content": guaiabc})

    q.append({"role": "user", "content": start_q(user_, place, [mood1, mood2, mood3])})
    print(q)

    response = dashscope.Generation.call(
        dashscope.Generation.Models.qwen_plus,
        messages=q,
        result_format='message',  # set the result to be "message" format.
        api_key=API_KEY,
        temperature=1.9,
    )
    answer = response["output"]["choices"][0]["message"]["content"]

    story_dir_path = f"./webapp/story/bulubulu/{mood2}_{place}.txt"
    with open(story_dir_path, 'w', encoding='utf-8') as f:
        f.write(answer)

    return answer


place_dic = {
    '家庭': '家中',
    '娱乐': '游乐场',
    '交通': '公共汽车',
    '校园': '学校',
    '购物': '超市',
    '用餐': '餐厅',
}


# 函数init_dialog用于初始化对话，设置请求会话中的各种参数。
def init_dialog(request: HttpRequest, is_high=False):
    user_profile = UserProfile.objects.get(user=request.user)
    print("+++++++++++++++++++")
    print(user_profile.user)
    print("+++++++++++++++++++")
    if is_high == True:
        request.session['mood'] = ''
        current_date = timezone.now().date()
        record = RecordAnswer(
            user=user_profile.name,
            date=current_date,
            place=request.session['place'],
            mood1=request.session['high_mood_1'],
            mood2=request.session['high_mood_2'],
            mood3=request.session['high_mood_3'],
        )
        record.save()
        user_profile.current_record_id = record.id
        user_profile.save()

    else:
        gen(user_profile, place_dic[request.session['place']], '开心', request.session['mood'], '开心')
        request.session['high_mood_1'] = ''
        request.session['high_mood_2'] = ''
        request.session['high_mood_3'] = ''
        current_date = timezone.now().date()
        record = RecordAnswer(
            user=user_profile.name,
            date=current_date,
            place=request.session['place'],
            mood1="开心",
            mood2=request.session['mood'],
            mood3="开心",
        )
        record.save()
        user_profile.current_record_id = record.id
        user_profile.save()

    if '%E5%85%94' in user_profile.role:
        request.session['ai_char'] = '兔子'
    elif '%E7%8C%AB' in user_profile.role:
        request.session['ai_char'] = '小猫'
    elif '%E7%8B%97' in user_profile.role:
        request.session['ai_char'] = '小狗'
    ai_name = user_profile.ai_name
    request.session['ai_name'] = ai_name
    ai_char = request.session['ai_char']
    user_profile.ai_char = request.session['ai_char']
    # user_profile.ai_name = request.session['ai_name']
    user_profile.save()

    request.session['gpt'] = greeting(request, ai_name).replace('\n', '')
    request.session['global_messages'] = [{"role": "system", "content": get_system_prompt(request).replace('\n', '')}]
    request.session['questions'] = [
        "你觉得我当时是什么样的心情呢？",
        "你可以猜猜看我当时的心情是什么样的呢？",
        "你有什么话可以对我说呢？",
        "你有什么话想对我说的吗？",
        "你可以对当时的我说些什么吗？",
    ]
    # request.session['qmode_1'] = 2
    # request.session['qmode_2'] = 2
    request.session['user_words'] = ''
    request.session['user_words_init'] = ''
    # request.session['dialog_times'] = 5
    request.session['dialog_times'] = 0
    md = request.session['mood']
    pls = place_dic[request.session['place']]
    m1 = request.session['high_mood_1']
    m2 = request.session['high_mood_2']
    m3 = request.session['high_mood_3']
    if is_high == False:
        request.session['story_list'] = split_text(
            read_txt_file(str(settings.BASE_DIR / 'webapp/story' / f'{user_profile.user}' / f'{md}_{pls}.txt')))

    else:
        print(user_profile.user)
        request.session['story_list'] = split_text(read_txt_file(
            str(settings.BASE_DIR / 'webapp/story' / f'{user_profile.user}' / f'{m1}_{m2}_{m3}_{pls}.txt')))

    processed_story_list = []
    for p in request.session['story_list']:
        lines = p.split('\n')
        if lines[0].startswith("###"):
            lines = lines[1:]
        processed_paragraph = trimming('\n'.join(lines), request)
        processed_story_list.append(processed_paragraph)

    request.session['story_list'] = processed_story_list
    print("++++++++++++++++++++++++++++++++++++++++++++++")
    print(processed_story_list)
    print("++++++++++++++++++++++++++++++++++++++++++++++")

    record.story_p1 = request.session['story_list'][0]
    record.story_p2 = request.session['story_list'][1]
    record.story_p3 = request.session['story_list'][2]
    record.story_p4 = request.session['story_list'][3]
    record.save()

    request.session['guess'] = '不知道'
    request.session['answer_template'] = [{"role": "system",
                                           "content": f'请根据以下的这段故事回答问题，请记住你是故事的主角{ai_name}，你是一只{ai_char}，我叫{UserProfile.objects.get(user=request.user).name}'}, ]


# 函数greeting用于生成问候语。
def greeting(request: HttpRequest, ai_name):
    user_profile = UserProfile.objects.get(user=request.user)
    place_dic = {
        '家庭': '家中',
        '娱乐': '游乐场',
        '交通': '公共汽车',
        '校园': '学校',
        '购物': '超市',
        '用餐': '餐厅',
    }
    pls = place_dic[request.session['place']]
    msg = f'''
嗨，{user_profile.name}，我是你的好朋友{ai_name}！最近在{pls}，我遇见了一件难忘的事情，我想和你分享一下，你愿意听我讲讲吗？
'''
    return msg


def wanna(msg):
    r_msg = f'''
甲激动地与乙分享故事，乙的回答是（{msg}），请分析乙是否想与甲分享故事，是请回答“1”，否请回答“0”。你只需要回答0或1，不需要说任何别的内容。
'''
    return r_msg


def before_story(res, request: HttpRequest):
    user_profile = UserProfile.objects.get(user=request.user)
    if (res == "1"):
        return ["那太好啦，感谢你愿意和我分享这个故事！", True]
    else:
        e_r = f'''
{user_profile.name}，你知道吗，其实我心里是很希望你可以和我分享这个故事的，你这样说我会很伤心的。
作为你的好朋友，我很希望自己能被你信任，能和你分享你的故事，能帮助你解决问题。你什么时候想和我聊天了，可以随时再来找我哦！
'''
        return [e_r, False]


# 函数trimming用于处理文本，去除不需要的字符。
def trimming(msg, request: HttpRequest):
    mood1 = request.session['mood']
    to_remove = [":", "：", "#"]
    for item in to_remove:
        if item != None:
            msg = msg.replace(item, "")

    to_repalce = [mood1, "开心"]
    for i in to_repalce:
        if i == "开心":
            msg = msg.replace(i, "高兴")
        elif i == "生气":
            msg = msg.replace(i, "不高兴")
        elif i == "害怕":
            msg = msg.replace(i, "恐惧")
        elif i == "难过":
            msg = msg.replace(i, "伤心")
        else:
            msg = msg

    pattern_to_remove = r"第.?部分"
    msg = re.sub(pattern_to_remove, "", msg)
    msg = "\n".join(line for line in msg.splitlines() if line.strip())
    return msg


# 函数get_system_prompt用于生成提示信息。
def get_system_prompt(request: HttpRequest):
    # global ai_name, ai_char, user_name, mood1, mood2, mood3, user_info
    user_info = ""
    ai_name = request.session['ai_name']
    user_name = UserProfile.objects.get(user=request.user).name
    mood1 = "开心"
    mood2 = request.session['mood']
    mood3 = "开心"
    ai_char = request.session['ai_char']
    # get the basic info from user input
    '''
    ai_name = get_from_user("ai_name")
    '''
    sys_content = f'''
我们来玩一个角色扮演游戏，你是{ai_name}，你是一只{ai_char}，我叫{user_name}。
你要给我讲一个发生在你身上的故事，这个故事中你的心情变化是"{mood1} -> {mood2} -> {mood3}"
根据这三次心情变化，把故事拆分成三个部分，分别是“第一部分：{mood1}；第二部分：{mood2}；第三部分：{mood3}”，在一部分故事讲完后停下，以“#”结束。
我是一个5岁的孩子，你的故事需要引导我，对我有所启发。
以下是关于我的一些信息：
{user_info}
你的回答需要包括足够多的指导性语句和透视性语句
指导性语句示例：
- 当我看到(具体事物)时，我会(具体反应)。
- 如果我遇到(具体人物)，我通常会(具体行动)。
- 当(具体情况)发生时，我倾向于(具体行动)。

透视性语句示例：
- (具体事件)让(具体人物)感到(具体情绪)。
- 面对(具体情况)，(具体人物)可能会感到(具体情绪)。
- (具体人物)对(具体事物或事件)的反应表明(具体人物)可能(具体情绪)。
'''
    return sys_content


# 函数get_start_q用于生成开始提问的提示信息。
def get_start_q(request: HttpRequest):
    user_profile = UserProfile.objects.get(user=request.user)
    ai_name = 'ai'
    place_dic = {
        '家庭': '家中',
        '娱乐': '游乐场',
        '交通': '公共汽车',
        '校园': '学校',
        '购物': '超市',
        '用餐': '餐厅',
    }
    pls = place_dic[request.session['place']]
    start_message = f'''
请记住，你是{ai_name}，故事的主角，请使用“我”来代替“{ai_name}”。使用“你”来代替“{user_profile.name}”。
以下是一些建议来帮助你：
- 故事发生的场景是{pls}，你可以在其中描述与其他人或事物之间的友好互动。
- 这种互动可以是有趣的、特别的，也可以是日常的。
- 你可以讨论喜欢的玩具、食物、游戏、户外活动或任何使你感到开心的事情。
- {user_profile.name}不能出现在你的故事中，只是作为你和我交流时称呼我的方式。
- 在叙述时，请使用指导性语句来引导行动，使用透视性语句来描述他人的内心状态、感受和信念。
- 故事应该有足够的细节，每一部分至少400词，并且丰富而充实。
请以你的故事第一部分为开端
现在，请开始详细讲述你的故事的第一部分
'''
    return start_message


# 函数get_templete_q和get_end_q用于生成问题和回答的模板。
def get_templete_q(index, front_msg):
    # front_msg 可以是选择的心情 可以是想说的一句话
    global user_name, ai_name
    if index == 0 or index == 1:
        msg = f'''
{user_name}的回答：我猜{ai_name}当时的心情是{front_msg}的
现在请{ai_name}分析我的回答是否和故事中你当时的心情一致?
如果是一致的请鼓励我、夸夸我
如果不一致请告诉我你期待的答案是什么，以及你当时真正的心情和产生的原因。明白的话就开始讲你的故事的下一部分。
'''
    else:
        msg = f'''
{user_name}的回答：{front_msg}
现在请{ai_name}分析听了{user_name}的这句话你的心情是什么样的？
以及{ai_name}期待的回答是什么？为什么期待的是这样的回答？明白的话就开始讲你的故事的下一部分。
'''
    print(msg)
    return msg


def get_end_q(index, front_msg):
    # front_msg 可以是选择的心情 可以是想说的一句话
    global user_name, ai_name
    if index == 0 or index == 1:
        msg = f'''
{user_name}的回答：我猜{ai_name}当时的心情是{front_msg}的
现在请{ai_name}分析我的回答是否和故事中你当时的心情一致?
如果是一致的请鼓励我、夸夸我
如果不一致请告诉我你期待的答案是什么，以及你当时真正的心情和产生的原因。
最后请对故事归纳总结，说明其中道理或生活经验或者相处方式，从中{user_name}可以学到什么？{user_name}以后遇到什么样的情况也可以怎么做？
'''
    else:
        msg = f'''
{user_name}的回答：{front_msg}
现在请{ai_name}分析听了{user_name}的这句话你的心情是什么样的？
以及{ai_name}期待的回答是什么？为什么期待的是这样的回答？
最后请对故事归纳总结，说明其中道理或生活经验或者相处方式，从中{user_name}可以学到什么？{user_name}以后遇到什么样的情况也可以怎么做？
'''
    print(msg)
    return msg


# 函数discuss用于生成讨论的提示信息。
def discuss(front_msg):
    global user_name
    msg = f'''
这是听完整个故事，{user_name}想对你说的话：{front_msg}
请做出回应，并结束对话
'''
    return msg


API_KEY = 'sk-0ab3f0c21a4b48c2baf3a7986d9ed518'


# 函数extend_user用于扩展用户的回答。
def extend_user(message, story='', want=False):
    if want:
        msg = [{"role": "system", "content": "请帮我判断我给出的语句是表达愿意的、正向的意愿还是负向的意愿，如果是正向的请输出“1”，如果是负向的请输出“0”："}, ]
        msg.append({"role": "user", "content": "愿意"})
        msg.append({"role": "assistant", "content": "1"})
        msg.append({"role": "user", "content": "我愿意"})
        msg.append({"role": "assistant", "content": "1"})
        msg.append({"role": "user", "content": "不想听"})
        msg.append({"role": "assistant", "content": "0"})
        msg.append({"role": "user", "content": "好的"})
        msg.append({"role": "assistant", "content": "1"})
        msg.append({"role": "user", "content": "好呀"})
        msg.append({"role": "assistant", "content": "1"})
        msg.append({"role": "user", "content": "不好"})
        msg.append({"role": "assistant", "content": "0"})
        msg.append({"role": "user", "content": "明白"})
        msg.append({"role": "assistant", "content": "1"})
        msg.append({"role": "user", "content": "不明白"})
        msg.append({"role": "assistant", "content": "0"})
        msg.append({"role": "user", "content": "不行"})
        msg.append({"role": "assistant", "content": "0"})
        msg.append({"role": "user", "content": message})

        response = dashscope.Generation.call(
            dashscope.Generation.Models.qwen_plus,
            messages=msg,
            result_format='message',  # set the result to be "message" format.
            api_key=API_KEY,
            temperature=1.9

        )
        assistant_message = response["output"]["choices"][0]["message"]["content"]

        if assistant_message == '1':
            answer = "那太好啦，我很愿意听到你与我的分享。"
        else:
            answer = "很抱歉，我现在没有做好与你分享故事的准备，下次有时间再听可以吗？"
        return answer
    else:
        sys_p = f'''
现在需要你辅助语言障碍人士进行表达，我会给出语言障碍人士听到的一段话和用户听完这段话的后回答。
你需要根据用户的回答，在不改变表达原意的基础上，参考用户的语境（优化）回答的内容。        
'''
        msg = [{"role": "system", "content": sys_p}, ]
        usr_p = f'''
听到的话：{story}
用户回答：{message}
你只需要给出优化后的用户回答即可，明白请回答。        
'''
        msg.append({"role": "user", "content": usr_p})
        response = dashscope.Generation.call(
            dashscope.Generation.Models.qwen_plus,
            messages=msg,
            result_format='message',  # set the result to be "message" format.
            api_key=API_KEY,
            temperature=1.9

        )
        assistant_message = response["output"]["choices"][0]["message"]["content"]
        # assistant_message = response.choices[0].message['content']
        return assistant_message


# 函数system_prompt用于生成系统提示信息。
def system_prompt(User_info):
    ai_name = User_info.ai_name
    user_name = User_info.name
    ai_char = User_info.ai_char
    food_like = User_info.food_like
    food_dislike = User_info.food_dislike
    event_like = User_info.event_like
    event_dislike = User_info.event_dislike
    hobby = User_info.hobby
    recent = User_info.recent
    user_info = f'''
我喜欢吃{food_like}
我不喜欢{food_dislike}
我喜欢{event_like}
我不喜欢{event_dislike}
我的爱好是{hobby}
我最近的经历是{recent}
请注意！！你生成的故事必须结合我最近的经历。你生成的故事必须结合我最近的经历。你生成的故事必须结合我最近的经历。
'''
    # get the basic info from user input
    sys_content = f'''
我们来玩一个角色扮演游戏，你是{ai_name}，你是一只{ai_char}，我叫{user_name}。
你要给我讲一个发生在你身上的故事。
我是一个3岁的孩子，你的故事需要引导我，对我有所启发。
以下是关于我的一些信息：
{user_info}
你的回答需要包括足够多的指导性语句和透视性语句
指导性语句示例：
- 当我看到(具体事物)时，我会(具体反应)。
- 如果我遇到(具体人物)，我通常会(具体行动)。
- 当(具体情况)发生时，我倾向于(具体行动)。

透视性语句示例：
- (具体事件)让(具体人物)感到(具体情绪)。
- 面对(具体情况)，(具体人物)可能会感到(具体情绪)。
- (具体人物)对(具体事物或事件)的反应表明(具体人物)可能(具体情绪)。
'''
    return sys_content


# 函数start_q用于生成开始提问的提示信息。
def start_q(User_info, plc, mood_list):
    mood1 = mood_list[0]
    mood2 = mood_list[1]
    mood3 = mood_list[2]
    ai_name = User_info.ai_name
    user_name = User_info.name
    # ai_name = '咪咪'
    start_message = f'''
请记住，你是{ai_name}，故事的主角，请使用“我”来代替“{ai_name}”。使用“你”来代替“{user_name}”。
你要给我讲一个发生在你身上的故事，这个故事中你的心情变化是"{mood1} -> {mood2} -> {mood3}"
根据这三次心情变化，把故事拆分成三个部分，分别是“第一部分：{mood1}；第二部分：{mood2}；第三部分：{mood3}”。
以下是一些建议来帮助你：
- 故事发生的场景是{plc}，你可以在其中描述与其他人或事物之间的友好互动。
- 这种互动可以是有趣的、特别的，也可以是日常的。
- 你可以讨论喜欢的玩具、食物、游戏、户外活动或任何使你感到开心的事情。
- 在叙述时，请使用指导性语句来引导行动，使用透视性语句来描述他人的内心状态、感受和信念。
- 故事应该简单生动，并且多用短句和直白的词汇。
- 每一部分故事的情节要能足够明显的推断出你当时的心情。

这个故事分为三个部分，每个部分的开头使用“### 第一部分：”、“### 第二部分：”、“### 第三部分：”作为开头。
每一部分的情节应当只包含相应的唯一一种心情，不要包含其他心情，不要有任何故事情节之外的语言出现。
故事需要足够简单，多用简单的短的句子，类似于*儿童绘本的语言*简单易懂。
记住：*不要*有太多的人物，*不要*有复杂的情节，*不要*有太多的转折。
以 “### 第四部分” 开头，对故事归纳总结，说明其中道理或生活经验或者相处方式，从中我可以学到什么？我以后遇到什么样的情况也可以怎么做？
明白请开始叙述完整的故事，只需要叙述内容，不能添加任何故事外的语句。每部分150词左右，总数少于200词。
'''
    # 请以你的故事第一部分为开端
    # 现在，请开始详细讲述你的故事的第一部分
    # print(start_message)
    return start_message
