import random
from webapp.chat.prompt import *
import dashscope

API_KEY = 'sk-0ab3f0c21a4b48c2baf3a7986d9ed518'

def init_questions(request: HttpRequest, which):
    """
    根据给定条件初始化问题序号。

    :param request: HttpRequest对象，包含用户请求信息
    :param which: bool值，指示初始化哪个部分的问题序号
    :return: int，初始化的问题序号
    """
    if which == False:
        return random.randint(2, 4)
    else:
        return random.randint(0, 1)


def answer_openai(msg, request: HttpRequest):
    """
    使用OpenAI生成助手的回答。

    :param msg: string，用户消息
    :param request: HttpRequest对象，包含用户请求信息
    :return: string，助手的回答
    """
    request.session['answer_template'].append({"role": "user", "content": msg})
    response = dashscope.Generation.call(
        dashscope.Generation.Models.qwen_max,
        messages=request.session['answer_template'],
        result_format='message',
        api_key=API_KEY,
        temperature=1.9,
    )
    assistant_message = response["output"]["choices"][0]["message"]["content"]
    request.session['answer_template'] = request.session['answer_template'][:-2]
    return assistant_message


def ask_openai(msg, request: HttpRequest):
    """
    使用OpenAI提问。

    :param msg: string，用户消息
    :param request: HttpRequest对象，包含用户请求信息
    :return: string，OpenAI生成的问题
    """
    request.session['global_messages'].append({"role": "user", "content": msg})
    response = dashscope.Generation.call(
        dashscope.Generation.Models.qwen_plus,
        messages=request.session['global_messages'],
        result_format='message',
        api_key=API_KEY,
        temperature=1.8,
    )
    assistant_message = response["output"]["choices"][0]["message"]["content"]
    request.session['global_messages'].append({"role": "assistant", "content": assistant_message})
    return trimming(assistant_message, request)


def gpt_judge(msg, request: HttpRequest):
    """
    使用OpenAI判断用户消息。

    :param msg: string，用户消息
    :param request: HttpRequest对象，包含用户请求信息
    :return: string，OpenAI生成的判断结果
    """
    g_msg = []
    g_msg.append({"role": "user", "content": wanna(msg)})
    response = dashscope.Generation.call(
        dashscope.Generation.Models.qwen_plus,
        messages=g_msg,
        result_format='message',
        api_key=API_KEY,
        temperature=1.9,
    )
    assistant_message = response["output"]["choices"][0]["message"]["content"]
    return before_story(assistant_message, request)


def send_to_front(msg):
    """
    向前端发送消息。

    :param msg: string，要发送的消息
    """
    print(msg)


def get_front_msg():
    """
    获取前端消息。

    :return: string，前端消息
    """
    front_msg = input()
    return front_msg


def main():
    """
    主函数，模拟对话流程。
    """
    sys_content = get_system_prompt()
    global_messages = [{"role": "system", "content": sys_content}, ]

    send_to_front(greeting())

    global questions

    send_to_front(gpt_judge(get_front_msg()) + ask_openai(get_start_q(), global_messages))
    q_idx = init_questions()

    send_to_front(questions[q_idx])

    send_to_front(ask_openai(get_templete_q(q_idx, get_front_msg()), global_messages))
    q_idx = init_questions()

    send_to_front(questions[q_idx])

    send_to_front(ask_openai(get_templete_q(q_idx, get_front_msg()), global_messages))
    q_idx = init_questions()

    send_to_front(questions[q_idx])

    send_to_front(ask_openai(get_end_q(q_idx, get_front_msg()), global_messages) + "\n" + "听完整个故事，你有什么想对我说的吗？")

    send_to_front(ask_openai(discuss(get_front_msg()), global_messages))


if __name__ == "__main__":
    main()
