import requests

API_KEY = "f9f31998445b7eae562dd0666b8cc528"


def get_city_id(city_name):
    """都市名から都市IDを取得"""
    URL = f'https://api.openweathermap.org/data/2.5/weather?q={city_name}&appid={API_KEY}'
    res = requests.get(URL)

    if res.status_code == 200:
        data = res.json()
        return data['id'], data['name']
    else:
        return None, None


# 使用例
city_id, city_name = get_city_id("nagoya,jp")
if city_id:
    print(f"{city_name}の都市ID: {city_id}")