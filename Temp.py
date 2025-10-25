def get_reply(user_message):
    message = user_message.lower()
    greeting = get_time_based_greeting()

    # 天気に関するキーワードをチェック
    if "天気" in message:
        api_key = "f9f31998445b7eae562dd0666b8cc528"
        if "大阪" in message:
            return get_weather_info(api_key, "大阪")
        elif "名古屋" in message:
            return get_weather_info(api_key, "名古屋")
        else:
            return get_weather_info(api_key, "東京")

    elif "こんにちは" in message or "おはよう" in message or "こんばんは" in message:
        return f"{greeting}！今日も一日頑張りましょう！"
    elif "ありがとう" in message:
        return "どういたしまして！また何かあれば声をかけてくださいね。"
    # ... 他の条件