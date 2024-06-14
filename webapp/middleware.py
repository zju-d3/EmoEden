# middleware.py
class GlobalVariableMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # 在请求开始时定义全局变量 x 并设置初始值为 0
        request.mood = None

        request.high_mood_1 = None
        request.high_mood_2 = None
        request.high_mood_3 = None

        request.resent = None
        request.place = None
        request.ai_name = None
        request.ai_char = None
        request.questions = None
        request.former_idx = None

        request.gpt = None
        request.global_messages = None
        request.guess = None
        request.speak = None
        request.extend = None
        # request.qmode_1 = None  # 猜测心情 index 0, 1
        # request.qmode_2 = None  # 说一些话 index 2, 3, 4
        request.dialog_times = None

        request.tts_file = None
        request.asr_file = None
        request.extend_file = None

        request.story_list = None
        request.answer_template = None
        request.user_words = None

        request.user_words_init = None

        response = self.get_response(request)
        return response
