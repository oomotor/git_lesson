import requests

def result_sentense(api_kye, city_id):
    # 都市IDを使用したURL
    URL = f'https://api.openweathermap.org/data/2.5/weather?id={city_id}&appid={api_kye}&units=metric&lang=ja'
    res = requests.get(URL)

    if res.status_code == 200:
        data = res.json()
        #print(data)
        print(f"都市: {data['name']}")
        print(f"天気: {data['weather'][0]['description']}")
        print(f"気温: {data['main']['temp']}°C")
    else:
        print(f"エラー: {res.status_code}")



API_KEY = "f9f31998445b7eae562dd0666b8cc528"

print("*"*20)
result_sentense(API_KEY, "1850147") #東京
print("*"*20)
result_sentense(API_KEY, "1853909") #大阪
print("*"*20)
result_sentense(API_KEY, "1856057") #名古屋