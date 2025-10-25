import requests
import datetime
import re

API_KEY = "f9f31998445b7eae562dd0666b8cc528"

def get_city_id(city_name):
    """都市名から都市IDを取得"""
    # 日本の都市の場合は",jp"を自動追加
    search_name = f"{city_name},jp" if not ",jp" in city_name.lower() else city_name
    
    URL = f'https://api.openweathermap.org/data/2.5/weather?q={search_name}&appid={API_KEY}'
    
    try:
        res = requests.get(URL)
        if res.status_code == 200:
            data = res.json()
            return data['id'], data['name']
        else:
            return None, None
    except Exception as e:
        print(f"エラー: {e}")
        return None, None

def get_current_weather(city_name):
    """現在の天気を取得"""
    city_id, actual_city_name = get_city_id(city_name)
    
    if not city_id:
        return f"申し訳ありません。'{city_name}'の天気情報が見つかりませんでした。"
    
    URL = f'https://api.openweathermap.org/data/2.5/weather?id={city_id}&appid={API_KEY}&units=metric&lang=ja'
    
    try:
        res = requests.get(URL)
        if res.status_code == 200:
            data = res.json()
            return f"📍{actual_city_name}の現在の天気\n🌤️ {data['weather'][0]['description']}\n🌡️ 気温: {data['main']['temp']}°C\n💧 湿度: {data['main']['humidity']}%"
        else:
            return "申し訳ありません。天気情報の取得に失敗しました。"
    except Exception as e:
        return f"天気情報の取得中にエラーが発生しました: {e}"

def get_weather_forecast(city_name, days_ahead=1):
    """天気予報を取得（1-5日後まで）"""
    if days_ahead < 1 or days_ahead > 5:
        return "天気予報は1日後から5日後までしか取得できません。"
    
    city_id, actual_city_name = get_city_id(city_name)
    
    if not city_id:
        return f"申し訳ありません。'{city_name}'の天気予報が見つかりませんでした。"
    
    URL = f'https://api.openweathermap.org/data/2.5/forecast?id={city_id}&appid={API_KEY}&units=metric&lang=ja'
    
    try:
        res = requests.get(URL)
        if res.status_code == 200:
            data = res.json()
            
            # 指定日数後の予報を探す
            target_date = datetime.datetime.now() + datetime.timedelta(days=days_ahead)
            target_date_str = target_date.strftime('%Y-%m-%d')
            
            # その日の予報データを検索
            day_forecasts = []
            for forecast in data['list']:
                forecast_time = datetime.datetime.fromtimestamp(forecast['dt'])
                if forecast_time.strftime('%Y-%m-%d') == target_date_str:
                    day_forecasts.append(forecast)
            
            if not day_forecasts:
                return f"{actual_city_name}の{days_ahead}日後の予報データが見つかりませんでした。"
            
            # 1日の中で代表的な時間帯（昼頃）の予報を選択
            midday_forecast = None
            for forecast in day_forecasts:
                forecast_time = datetime.datetime.fromtimestamp(forecast['dt'])
                if 11 <= forecast_time.hour <= 15:  # 11時〜15時の範囲
                    midday_forecast = forecast
                    break
            
            # 昼頃のデータがない場合は最初のデータを使用
            if not midday_forecast:
                midday_forecast = day_forecasts[0]
            
            forecast_time = datetime.datetime.fromtimestamp(midday_forecast['dt'])
            day_name = ["明日", "明後日", "3日後", "4日後", "5日後"][days_ahead-1]
            
            return (f"📍{actual_city_name}の{day_name}の天気\n"
                   f"📅 {forecast_time.strftime('%m月%d日(%a)')}\n"
                   f"🌤️ {midday_forecast['weather'][0]['description']}\n"
                   f"🌡️ 気温: {midday_forecast['main']['temp']}°C\n"
                   f"💧 湿度: {midday_forecast['main']['humidity']}%")
            
        else:
            return "申し訳ありません。天気予報の取得に失敗しました。"
    except Exception as e:
        return f"天気予報の取得中にエラーが発生しました: {e}"

def parse_weather_request(message):
    """メッセージから都市名と日付を解析"""
    message = message.replace("の天気", "").replace("は？", "").replace("？", "").strip()
    
    # 日付キーワードの検索
    if "明日" in message:
        city_name = message.replace("明日", "").strip()
        return city_name, 1
    elif "明後日" in message:
        city_name = message.replace("明後日", "").strip()
        return city_name, 2
    elif "3日後" in message:
        city_name = message.replace("3日後", "").strip()
        return city_name, 3
    elif "4日後" in message:
        city_name = message.replace("4日後", "").strip()
        return city_name, 4
    elif "5日後" in message:
        city_name = message.replace("5日後", "").strip()
        return city_name, 5
    else:
        # 現在の天気
        city_name = message.replace("今", "").replace("現在", "").strip()
        return city_name, 0

# テスト用のメイン関数
def main():
    print("拡張天気機能のテスト")
    print("例: '広島の今の天気は？', '大阪の明日の天気は？'")
    print("終了するには 'quit' と入力してください\n")
    
    while True:
        user_input = input("天気を聞く: ")
        if user_input.lower() == 'quit':
            break
        
        if "天気" in user_input:
            city_name, days_ahead = parse_weather_request(user_input)
            
            if days_ahead == 0:
                result = get_current_weather(city_name)
            else:
                result = get_weather_forecast(city_name, days_ahead)
            
            print(f"結果: {result}\n")
        else:
            print("天気に関する質問をしてください。\n")

if __name__ == "__main__":
    main()