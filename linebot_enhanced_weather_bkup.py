import os
import datetime
import requests
from flask import Flask, request, abort

# LINE Bot SDK v3
from linebot.v3 import WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.messaging import (
    Configuration, ApiClient, MessagingApi, ReplyMessageRequest, TextMessage
)
from linebot.v3.webhooks import MessageEvent, TextMessageContent

# Gemini API
import google.generativeai as genai

app = Flask(__name__)

# LINE設定
configuration = Configuration(access_token=os.getenv('LINE_CHANNEL_ACCESS_TOKEN'))
handler = WebhookHandler(os.getenv('LINE_CHANNEL_SECRET'))

# Gemini設定
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))

# 天気API設定
WEATHER_API_KEY = "f9f31998445b7eae562dd0666b8cc528"


def get_city_id(city_name):
    """都市名から都市IDを取得"""
    # 日本語→英語の都市名変換辞書（表示名も含む）
    city_name_map = {
        "東京": {"english": "tokyo", "display": "東京"},
        "横浜": {"english": "yokohama", "display": "横浜"},
        "大阪": {"english": "osaka", "display": "大阪"},
        "名古屋": {"english": "nagoya", "display": "名古屋"},
        "札幌": {"english": "sapporo", "display": "札幌"},
        "福岡": {"english": "fukuoka", "display": "福岡"},
        "神戸": {"english": "kobe", "display": "神戸"},
        "京都": {"english": "kyoto", "display": "京都"},
        "広島": {"english": "hiroshima", "display": "広島"},
        "仙台": {"english": "sendai", "display": "仙台"},
        "千葉": {"english": "chiba", "display": "千葉"},
        "埼玉": {"english": "saitama", "display": "さいたま"},
        "川崎": {"english": "kawasaki", "display": "川崎"},
        "北九州": {"english": "kitakyushu", "display": "北九州"},
        "沖縄": {"english": "naha", "display": "那覇"},
        "那覇": {"english": "naha", "display": "那覇"},
        "金沢": {"english": "kanazawa", "display": "金沢"},
        "新潟": {"english": "niigata", "display": "新潟"},
        "静岡": {"english": "shizuoka", "display": "静岡"},
        "岡山": {"english": "okayama", "display": "岡山"},
        "熊本": {"english": "kumamoto", "display": "熊本"},
        "鹿児島": {"english": "kagoshima", "display": "鹿児島"},
        "長崎": {"english": "nagasaki", "display": "長崎"},
        "宮崎": {"english": "miyazaki", "display": "宮崎"},
        "大分": {"english": "oita", "display": "大分"},
        "高松": {"english": "takamatsu", "display": "高松"},
        "松山": {"english": "matsuyama", "display": "松山"},
        "高知": {"english": "kochi", "display": "高知"},
        "和歌山": {"english": "wakayama", "display": "和歌山"},
        "奈良": {"english": "nara", "display": "奈良"}
    }

    # 都市名を英語に変換
    if city_name in city_name_map:
        english_name = city_name_map[city_name]["english"]
        display_name = city_name_map[city_name]["display"]
    else:
        english_name = city_name
        display_name = city_name

    # ",jp"が含まれていない場合は追加
    search_name = f"{english_name},jp" if not ",jp" in english_name.lower() else english_name

    URL = f'https://api.openweathermap.org/data/2.5/weather?q={search_name}&appid={WEATHER_API_KEY}'

    try:
        res = requests.get(URL)
        if res.status_code == 200:
            data = res.json()
            # 日本語の表示名を返す
            return data['id'], display_name
        else:
            return None, None
    except:
        return None, None


def get_current_weather(city_name):
    """現在の天気を取得"""
    city_id, actual_city_name = get_city_id(city_name)

    if not city_id:
        return f"申し訳ありません。'{city_name}'の天気情報が見つかりませんでした。🌍"

    URL = f'https://api.openweathermap.org/data/2.5/weather?id={city_id}&appid={WEATHER_API_KEY}&units=metric&lang=ja'

    try:
        res = requests.get(URL)
        if res.status_code == 200:
            data = res.json()
            return f"📍{actual_city_name}の現在の天気\n🌤️ {data['weather'][0]['description']}\n🌡️ 気温: {data['main']['temp']}°C\n💧 湿度: {data['main']['humidity']}%"
        else:
            return "申し訳ありません。天気情報の取得に失敗しました。"
    except:
        return "天気情報の取得中にエラーが発生しました。"


def get_weather_forecast(city_name, days_ahead=1):
    """天気予報を取得（1-5日後まで）"""
    if days_ahead < 1 or days_ahead > 5:
        return "天気予報は1日後から5日後までしか取得できません。"

    city_id, actual_city_name = get_city_id(city_name)

    if not city_id:
        return f"申し訳ありません。'{city_name}'の天気予報が見つかりませんでした。🌍"

    URL = f'https://api.openweathermap.org/data/2.5/forecast?id={city_id}&appid={WEATHER_API_KEY}&units=metric&lang=ja'

    try:
        res = requests.get(URL)
        if res.status_code == 200:
            data = res.json()

            # 現在時刻から指定日数後の日付を計算（JST時間で）
            now = datetime.datetime.now()
            target_date = now + datetime.timedelta(days=days_ahead)
            target_date_str = target_date.strftime('%Y-%m-%d')

            print(f"DEBUG: 検索対象日付: {target_date_str}")  # デバッグ用

            # その日の予報データを検索
            day_forecasts = []
            for forecast in data['list']:
                # UTCタイムスタンプをJSTに変換
                forecast_time_utc = datetime.datetime.fromtimestamp(forecast['dt'])
                forecast_time_jst = forecast_time_utc + datetime.timedelta(hours=9)  # JST変換
                forecast_date_str = forecast_time_jst.strftime('%Y-%m-%d')

                print(f"DEBUG: 予報時刻: {forecast_time_jst}, 日付: {forecast_date_str}")  # デバッグ用

                if forecast_date_str == target_date_str:
                    day_forecasts.append({
                        'forecast': forecast,
                        'time': forecast_time_jst
                    })

            print(f"DEBUG: 見つかった予報数: {len(day_forecasts)}")  # デバッグ用

            if not day_forecasts:
                # 利用可能な日付を表示
                available_dates = []
                for forecast in data['list'][:8]:  # 最初の8件をチェック
                    forecast_time_utc = datetime.datetime.fromtimestamp(forecast['dt'])
                    forecast_time_jst = forecast_time_utc + datetime.timedelta(hours=9)
                    available_dates.append(forecast_time_jst.strftime('%Y-%m-%d'))

                return f"申し訳ありません。{actual_city_name}の{days_ahead}日後（{target_date_str}）の予報データが見つかりませんでした。\n利用可能な予報日: {', '.join(set(available_dates))}"

            # 1日の中で最適な時間帯を選択（昼頃 or 最初のデータ）
            selected_forecast = day_forecasts[0]  # デフォルトは最初のデータ

            # 昼頃（11-15時）のデータがあれば優先
            for item in day_forecasts:
                if 11 <= item['time'].hour <= 15:
                    selected_forecast = item
                    break

            forecast_data = selected_forecast['forecast']
            forecast_time = selected_forecast['time']

            day_names = ["明日", "明後日", "3日後", "4日後", "5日後"]
            day_name = day_names[days_ahead - 1]

            # 曜日の日本語変換
            weekdays = ['月', '火', '水', '木', '金', '土', '日']
            weekday = weekdays[forecast_time.weekday()]

            return (f"📍{actual_city_name}の{day_name}の天気\n"
                    f"📅 {forecast_time.strftime('%m月%d日')}({weekday})\n"
                    f"🌤️ {forecast_data['weather'][0]['description']}\n"
                    f"🌡️ 気温: {forecast_data['main']['temp']}°C\n"
                    f"💧 湿度: {forecast_data['main']['humidity']}%")

        else:
            return f"申し訳ありません。天気予報の取得に失敗しました。（ステータス: {res.status_code}）"
    except Exception as e:
        return f"天気予報の取得中にエラーが発生しました: {str(e)}"


def parse_weather_request(message):
    """メッセージから都市名と日付を解析"""
    # まず時間に関するキーワードをチェック
    original_message = message

    if "明日" in message:
        city_name = message.replace("の明日の天気", "").replace("明日の天気", "").replace("の天気", "").replace("は？", "").replace("は",
                                                                                                                    "").replace(
            "？", "").strip()
        return city_name, 1
    elif "明後日" in message:
        city_name = message.replace("の明後日の天気", "").replace("明後日の天気", "").replace("の天気", "").replace("は？", "").replace(
            "は", "").replace("？", "").strip()
        return city_name, 2
    elif "3日後" in message:
        city_name = message.replace("の3日後の天気", "").replace("3日後の天気", "").replace("の天気", "").replace("は？", "").replace(
            "は", "").replace("？", "").strip()
        return city_name, 3
    elif "4日後" in message:
        city_name = message.replace("の4日後の天気", "").replace("4日後の天気", "").replace("の天気", "").replace("は？", "").replace(
            "は", "").replace("？", "").strip()
        return city_name, 4
    elif "5日後" in message:
        city_name = message.replace("の5日後の天気", "").replace("5日後の天気", "").replace("の天気", "").replace("は？", "").replace(
            "は", "").replace("？", "").strip()
        return city_name, 5
    else:
        # 現在の天気（"今"、"現在"などを含む）
        city_name = message.replace("の今の天気", "").replace("今の天気", "").replace("の現在の天気", "").replace("現在の天気", "").replace(
            "の天気", "").replace("天気", "").replace("は？", "").replace("は", "").replace("？", "").strip()
        return city_name, 0


def get_time_based_greeting():
    """現在時刻に応じた挨拶を返す"""
    now = datetime.datetime.now()
    hour = now.hour

    if 5 <= hour < 12:
        return "おはようございます"
    elif 12 <= hour < 17:
        return "こんにちは"
    elif 17 <= hour < 22:
        return "こんばんは"
    else:
        return "夜更かしですね"


def chat_with_gemini(message):
    """Gemini APIを使用した自然対話"""
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')

        system_prompt = """
        あなたは親しみやすいLINEボットです。以下の特徴で会話してください：
        - 親しみやすく丁寧な日本語で返答
        - 返答は150文字以内で簡潔に
        - 絵文字を適度に使用
        - ユーザーに寄り添う優しい口調
        """

        full_prompt = f"{system_prompt}\n\nユーザー: {message}\nボット: "

        response = model.generate_content(full_prompt)
        return response.text

    except:
        return f"申し訳ありません。AIとの会話でエラーが発生しました。🤖💦"


def get_reply(user_message):
    """ユーザーメッセージに応じた返答を生成"""
    message = user_message.lower()
    greeting = get_time_based_greeting()

    # 天気情報の処理（最優先）
    if "天気" in message:
        city_name, days_ahead = parse_weather_request(message)

        # 都市名が空の場合はデフォルトで東京
        if not city_name:
            city_name = "東京"

        if days_ahead == 0:
            return get_current_weather(city_name)
        else:
            return get_weather_forecast(city_name, days_ahead)

    # 基本的な挨拶
    elif any(word in message for word in ["こんにちは", "おはよう", "こんばんは", "はじめまして"]):
        return f"{greeting}！今日も一日頑張りましょう！😊"

    # 感謝
    elif "ありがとう" in message:
        return "どういたしまして！また何かあれば声をかけてくださいね。✨"

    # 疲れた
    elif "疲れた" in message:
        return f"{greeting}！お疲れ様です。少し休憩してくださいね。🍵"

    # 特定のキーワード
    elif "バカ" in message:
        return f"{greeting}！馬と鹿と書いてバカと読みます！🐴🦌"
    elif "宿題" in message:
        return f"{greeting}！宿題は言われなくても早くやって下さい！または諦めてズーンをくらって下さい！📚"
    elif "ママ" in message:
        return f"{greeting}！ママのいう事は聞いて下さい。ワガママばかり言ってはいけないよ！👩"
    elif "パパ" in message:
        return f"{greeting}！パパを見習って宿題は早く終わらせるよう頑張って下さい！パパに文句ばかり言ってはいけないよ！👨"

    # 上記に該当しない場合はGemini APIで自然対話
    else:
        return chat_with_gemini(user_message)


@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        print("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)

    return 'OK'


@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    user_message = event.message.text
    reply_text = get_reply(user_message)

    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        line_bot_api.reply_message_with_http_info(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[TextMessage(text=reply_text)]
            )
        )


if __name__ == "__main__":
    port = 5001
    app.run(host="0.0.0.0", port=port)