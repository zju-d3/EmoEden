import os
import shutil
import json
import django
from django.conf import settings
from django.db.models import Q
# 导入必要的模块和库

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "web.settings")
django.setup()
# 设置Django环境

from webapp.chat.prompt import *
from webapp.models import *
from django.contrib.auth.models import User
from django.utils import timezone
import random
from pathlib import Path

# 设置API密钥和路径
story_dir_path = "./webapp/story/bulubulu"
good_exp = f'''
### 第一部分：感激

我是一只活泼的小猫咪，住在一个充满爱的家里。只只是我的主人，也是我最好的朋友，我们真的超级无敌好哦！

只只每天都给我做香香的番茄炒蛋，那是我的最爱！每当我看到那碗炒蛋，我会快乐地跳来跳去，摇摇尾巴。不仅如此，只只还给我乐高玩具，我可以堆成大房子、小汽车，真的太好玩了！

### 第二部分：羞愧

某天，我玩得太开心，不小心撕破了一张很特别的剪纸。哎哟，我吓得眼睛都圆了！我知道只只花了很多时间和心血制作这张剪纸，但我却毁了它，我怎么这么笨呀？

我知道我犯了错误，于是我躲在角落里，不敢面对只只。我似乎可以猜到只只的失望和伤心，这让我更加愧疚，只能在心里希望只只不会太伤心。我想说“对不起”，但不知道怎么说。

### 第三部分：敬佩

几天后，在只只的帮助下，我学会了剪纸折纸的技巧。我看着只只的手一刀一刀地剪，心里默默地想，“只只真的好厉害！”我也想尝试，想为只只做一张。我在尝试中变得越来越熟练。只只鼓励我继续努力，不断挑战更难的剪纸作品。

我慢慢学，每次成功，心里都好开心。不仅如此，我还学会了从错误中学习，明白了只要努力，一切都可以变好。

### 第四部分：总结

这个故事让我知道，我们要珍惜每一个朋友，感激他们的每一次帮助。当我们做错了，要勇敢说“对不起”。还要向只只那样，学会鼓励和支持，帮助朋友们一起成长。

'''

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

meibing = f'''
### 第一部分：开心

哈喽冰棒小朋友！我是活泼可爱的小朵，一只总是充满活力的小兔子。每次走进教室，我都感到无比兴奋，那里有五颜六色的蜡笔、洁白的纸张，还有我最最亲爱的小伙伴们。当我手中拿着蜡笔时，我总是忍不住欢快地开始创作，我喜欢画各种美食，比如香喷喷的咖喱土豆和五彩缤纷的彩虹糖。小辉是我的好朋友，每次和小辉分享我的画作时，他的眼睛是亮晶晶的，这种快乐充满了整个教室。

### 第二部分：难过

但是，有一天，当我准备画画的时候，我发现我珍藏的画纸不见了！我那会儿可着急啦，到处寻找。心情就像坠入深渊，因为那是我当天画画的唯一纸张，找不到的话就不能和同学们一起参加绘画课啦。我在自己的座位上急得哭了起来。

### 第三部分：开心

正在我独自难过时，小辉朝我走了过来，眨眼问我：“小朵，你在找什么呢？”我哽咽着告诉他我的画纸不见了。小辉眼睛一亮，笑了一笑，从书包里掏出了他的画纸，大方的递给我。收到了小辉的帮助，我连忙向他表示了感谢，并递给他我最喜欢的巧克力一起分享。最后在绘画课上，我画了小辉慷慨帮助我的这件事，得到了老师的表扬和夸奖，这可真让我高兴！

### 第四部分：总结

冰棒呀，听了这个简单的小故事，希望你可以明白：虽然有时我们会因为一些小事心情低落，但请相信，身边总会有那么一些好朋友，愿意伸出援手，和你一起度过难关。还有就是，无论遇到什么困境，都不要轻易放弃，因为转角就可能会有惊喜。当你遇到困难时，坚持并勇敢面对，你会重新找回那份开心和欢笑！
'''

guaiabc = f'''
### 第一部分：感激
嗨！我是咪咪，一只元气满满的小猫。和我最好的朋友、主人贝贝一起，每一天都变得充满欢乐。某个阳光明媚的日子，贝贝为我带来了一只造型逼真的玩具老鼠，它可是我玩过的最有趣的玩具了！当那玩具出现在我眼前，我兴奋得团团转，心里对贝贝的感激如潮水般涌现。

### 第二部分：羞愧
某日，贝贝的好朋友来我家做客，他们在客厅愉快地涂鸦，画出五颜六色的世界。看着他们专心地作画，我也心痒痒地想试试。于是，我挥动我的小爪，希望能够绘出一幅杰作。但哎呀，我发现自己和画画似乎不太合拍，相较于他们的画，我真是差了不少。那时的我，真想找个洞钻进去藏起来。

### 第三部分：敬佩
又是一个晴朗的周末，贝贝带我到公园散心。当他们在草地上玩足球时，我也跃跃欲试，加入他们的行列。突然，一颗飞速而来的足球飞向了我。我本能地伸出我的小爪，瞬间将球接住，再轻松地传给队友。贝贝和其他小朋友看后，纷纷为我鼓掌，露出惊喜的表情。那一刻，我发现自己的爪子真的好神奇！

### 第四部分：宝贵的体悟
这段简单的经历，让我深刻领悟到：无论是人还是小动物，我们都有自己的闪光点。就算有时会遭遇挫折或感到尴尬，那都不过是生活中的一小段插曲。我们应当珍视自己的每一个才华，并勇敢去尝试、去挑战。当你感到自卑或尴尬时，想想那些为你鼓掌的人，相信自己的无穷潜能。同时，要学会欣赏他人，相互鼓励，这样我们的生活将充满阳光和温暖。在任何经历中，都有成长的机会。
'''


def load_processed_records(file_path):
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            return set(tuple(record.items()) for record in json.load(f))
    return set()


def save_processed_records(file_path, processed_records):
    with open(file_path, 'w') as f:
        json.dump([dict(record) for record in processed_records], f)


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
    with open(story_dir_path, 'w') as f:
        f.write(answer)

    return answer


def main():
    place_dic = {
        '家庭': '家中',
        '娱乐': '游乐场',
        '交通': '公共汽车',
        '校园': '学校',
        '购物': '超市',
        '用餐': '餐厅',
    }

    excluded_usernames = ["25351219", "abcde", "czyaac", "czyabc", "xingabc", "rongabc"]
    user_id = User.objects.exclude(username__in=excluded_usernames).values_list('id', flat=True)
    user_name = UserProfile.objects.filter().values_list('name', flat=True)

    today_records = RecordAnswer.objects.filter(date=timezone.datetime(2023, 8, 31).date()).exclude(gpt_sum='')
    selected_fields = ['user', 'place', 'mood1', 'mood2', 'mood3']
    records_list = today_records.values(*selected_fields)
    unique_records_set = set()
    for record in records_list:
        unique_records_set.add(tuple(record.items()))
    unique_records_list = [dict(record) for record in unique_records_set]

    processed_records_file = 'processed_records.json'  # 指定保存已处理记录的文件名
    processed_records = load_processed_records(processed_records_file)

    # print(processed_records)

    for record in unique_records_list:
        if tuple(record.items()) in processed_records:
            continue  # 已处理，跳过

        u_id = UserProfile.objects.get(name=record['user']).user.username
        u_name = record['user']
        pls = place_dic[record['place']]
        m1 = record['mood1']
        m2 = record['mood2']
        m3 = record['mood3']

        # move to the new folder
        if m1 == "开心":
            source_path = str(
                settings.BASE_DIR / 'webapp/story' / f'{u_id}' / f'{m2}_{pls}.txt')
        else:
            source_path = str(
                settings.BASE_DIR / 'webapp/story' / f'{u_id}' / f'{m1}_{m2}_{m3}_{pls}.txt')
        # destination_dir = str(settings.BASE_DIR / 'webapp/story_archived' / f'{u_id}' / f'{timezone.datetime(2023, 8, 15).date()}')
        # destination_path = str(
        #     settings.BASE_DIR / 'webapp/story_archived' / f'{u_id}' / f'{timezone.datetime(2023, 8, 16).date()}' / f'{m1}_{m2}_{m3}_{pls}.txt')

        with open(source_path, 'w') as file:
            file.write(gen(UserProfile.objects.get(name=u_name), pls, m1, m2, m3))
        print(source_path + " done")
        processed_records.add(tuple(record.items()))
        save_processed_records(processed_records_file, processed_records)


def move_dir():
    place_dic = {
        '家庭': '家中',
        '娱乐': '游乐场',
        '交通': '公共汽车',
        '校园': '学校',
        '购物': '超市',
        '用餐': '餐厅',
    }

    excluded_usernames = ["25351219", "abcde", "czyaac", "czyabc", "rongabc"]
    user_id = User.objects.exclude(username__in=excluded_usernames).values_list('id', flat=True)
    user_name = UserProfile.objects.filter().values_list('name', flat=True)

    today_records = RecordAnswer.objects.filter(date=timezone.now().date())
    selected_fields = ['user', 'place', 'mood1', 'mood2', 'mood3']
    records_list = today_records.values(*selected_fields)
    unique_records_set = set()
    for record in records_list:
        unique_records_set.add(tuple(record.items()))
    unique_records_list = [dict(record) for record in unique_records_set]

    processed_records_file = 'processed_records.json'  # 指定保存已处理记录的文件名
    processed_records = load_processed_records(processed_records_file)

    for record in unique_records_list:
        if tuple(record.items()) in processed_records:
            continue  # 已处理，跳过

        u_id = UserProfile.objects.get(name=record['user']).user.username
        u_name = record['user']
        pls = place_dic[record['place']]
        m1 = record['mood1']
        m2 = record['mood2']
        m3 = record['mood3']

        # 构建源路径
        if m1 == "开心":
            source_path = str(settings.BASE_DIR / 'webapp/story' / f'{u_id}' / f'{m2}_{pls}.txt')
        else:
            source_path = str(settings.BASE_DIR / 'webapp/story' / f'{u_id}' / f'{m1}_{m2}_{m3}_{pls}.txt')

        # 检查源文件是否存在
        if not os.path.exists(source_path):
            print(f"Source file not found: {source_path}")
            continue  # 源文件不存在，跳过当前循环

        # 构建目标路径
        destination_dir = os.path.join(settings.BASE_DIR, 'webapp/story_archived', u_id,
                                       str(timezone.datetime(2023, 8, 18).date()))
        os.makedirs(destination_dir, exist_ok=True)
        destination_path = os.path.join(destination_dir, f'{m1}_{m2}_{m3}_{pls}.txt')

        # 尝试移动文件
        try:
            shutil.move(source_path, destination_path)
            print(f"File moved successfully: {source_path} -> {destination_path}")
        except FileNotFoundError:
            print(f"Error moving file: Source file not found - {source_path}")
        except Exception as e:
            print(f"Error moving file: {e}")


def template_gen(user_id):
    user = UserProfile.objects.get(name="乖乖")
    print(user.name)
    for pls in ['游乐场', '家中', '超市', '学校', '公共汽车', '餐厅']:
        for m1 in ['感激', '敬佩']:
            for m2 in ['羞愧', '懊悔']:
                m3 = None
                if m1 == '感激':
                    m3 = '敬佩'
                else:
                    m3 = '感激'
                story = gen(user, pls, m1, m2, m3)
                source_path = str(
                    settings.BASE_DIR / 'webapp/story' / f'{user.user.username}' / f'{m1}_{m2}_{m3}_{pls}.txt')
                with open(source_path, 'w') as file:
                    file.write(story)
                print(source_path + " done")
    # print(gen(user, "家中", "感激", "羞愧", "敬佩"))


def clear_name():
    cartoon_names = [
        "萌萌",
        "蓓蓓",
        "乐乐",
        "欢欢",
        "笑笑",
        "雪雪",
        "妮妮",
        "琳琳",
        "可可",
        "宝宝",
        "悠悠",
        "莉莉",
        "小橙",
        "小蓝",
        "小绿",
        "小紫",
        "嘟嘟",
        "娃娃",
        "露露",
        "豆豆"
    ]

    user_list = UserProfile.objects.filter()
    for user in user_list:
        print(user.user.username)
        source_path = Path(settings.BASE_DIR / 'webapp/story' / user.user.username)

        for txt_file in source_path.glob('*.txt'):
            with open(txt_file, 'r', encoding='utf-8') as file:
                original_text = file.read()

            # 随机选择一个卡通名字
            random_name = random.choice(cartoon_names)

            # 使用replace方法替换
            new_text = original_text.replace(user.name, random_name)

            # 写回到文件
            with open(txt_file, 'w', encoding='utf-8') as file:
                file.write(new_text)

            print(f"处理完成：{txt_file}")


def so_what():
    so_w = f'''
    ### 第一部分：开心

    哈喽子豪小朋友！我是活泼可爱的小朵，一只总是充满活力的小兔子。每次走进教室，我都感到无比兴奋，那里有五颜六色的蜡笔、洁白的纸张，还有我最最亲爱的小伙伴们。当我手中拿着蜡笔时，我总是忍不住欢快地开始创作，我喜欢画各种美食，比如香喷喷的咖喱土豆和五彩缤纷的彩虹糖。小辉是我的好朋友，每次和小辉分享我的画作时，他的眼睛是亮晶晶的，这种快乐充满了整个教室。

    ### 第二部分：难过

    但是，有一天，当我准备画画的时候，我发现我珍藏的画纸不见了！然后呢，我那会儿可着急啦，到处寻找。心情就像坠入深渊，因为那是我当天画画的唯一纸张，找不到的话就不能和同学们一起参加绘画课啦。然后呢，我在自己的座位上急得哭了起来。

    ### 第三部分：开心

    正在我独自难过时，小辉朝我走了过来，眨眼问我：“小朵，你在找什么呢？”我哽咽着告诉他我的画纸不见了。小辉眼睛一亮，笑了一笑，然后呢，他从书包里掏出了他的画纸，大方的递给我。收到了小辉的帮助，我连忙向他表示了感谢，然后呢递给他我最喜欢的巧克力一起分享。最后在绘画课上，我画了小辉慷慨帮助我的这件事，得到了老师的表扬和夸奖，这可真让我高兴！

    ### 第四部分：总结

    子豪呀，听了这个简单的小故事，希望你可以明白：虽然有时我们会因为一些小事心情低落，但请相信，身边总会有那么一些好朋友，愿意伸出援手，和你一起度过难关。还有就是，无论遇到什么困境，都不要轻易放弃，因为转角就可能会有惊喜。当你遇到困难时，坚持并勇敢面对，你会重新找回那份开心和欢笑！
    '''
    user_ = UserProfile.objects.get(name="子豪")
    q = [{"role": "system", "content": system_prompt(user_)}, ]
    q.append({"role": "user", "content": start_q(user_, '教室', ['开心', '难过', '开心'])})
    q.append({"role": "assistant", "content": so_w})
    # q.append({"role": "user", "content": start_q(user_, '厨房', ['感激', '羞愧', '敬佩'])})
    # q.append({"role": "assistant", "content": so_w})

    # q.append({"role": "user", "content": start_q(user_, '家中', ['感激', '羞愧', '敬佩'])})
    # q.append({"role": "assistant", "content": guaiabc})

    q.append({"role": "user", "content": start_q(user_, "公共汽车", ["开心", "难过", "开心"])})
    print(q)
    response = dashscope.Generation.call(
        dashscope.Generation.Models.qwen_plus,
        messages=q,
        result_format='message',  # set the result to be "message" format.
        api_key=API_KEY,
        temperature=1.9,
    )
    answer = response["output"]["choices"][0]["message"]["content"]
    # response = openai.ChatCompletion.create(
    #     model="gpt-3.5-turbo",
    #     # model="gpt-4",
    #     messages=q,
    #     temperature=1,
    # )
    # answer = response.choices[0].message['content']
    print(answer)


if __name__ == "__main__":
    # main()
    # move_dir()
    # template_gen(2)
    # clear_name()
    # so_what()

    print(gen(UserProfile.objects.get(name='卟噜'), '学校', '开心', '难过', '开心'))
