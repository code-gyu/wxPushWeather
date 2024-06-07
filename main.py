import json
from datetime import date
from datetime import datetime, timedelta

from lunardate import LunarDate
from wechatpy import WeChatClient
from wechatpy.client.api import WeChatMessage
import requests
import os


# 哪天在一起的
start_date = os.environ['START_DATE']
# 和风天气key
appKey = os.environ['APP_KEY']
# 生日
birthday = os.environ['BIRTHDAY']
# 微信公众号的appid和app_secret
app_id = os.environ["APP_ID"]
app_secret = os.environ["APP_SECRET"]
# 微信公众号的user_id,多个用;（分号）隔开
user_ids = os.environ["USER_IDS"]
# 白天模板id
template_id_day = os.environ["TEMPLATE_ID_DAY"]
# 晚上模板id
template_id_night = os.environ["TEMPLATE_ID_NIGHT"]
# 呢称
name = os.environ['NAME']
# 城市
city = os.environ['CITY']

# 当前时间
today = datetime.now()
# YYYY年MM月DD日
today_date = today.strftime("%Y年%m月%d日")


# 构建请求体
headers = {"Content-Type": "application/x-www-form-urlencoded"}
params = {
    "key": appKey,
    "location": city
}

# 根据城市名查找地理位置
url = "https://geoapi.qweather.com/v2/city/lookup"
resp_json = json.loads(requests.get(url, params, headers=headers).text)
city_id = resp_json["location"][0]["id"]
params["location"] = city_id

# 根据城市地理位置获取当前实时天气
url = "https://devapi.qweather.com/v7/weather/now"
realtime_json = json.loads(requests.get(url, params, headers=headers).text)
# 实时天气状况
realtime = realtime_json["now"]
# 当前温度 拼接 当前天气
now_temperature = realtime["temp"] + "℃" + realtime["text"]

# 根据城市地理位置获取3天天气状况
url = "https://devapi.qweather.com/v7/weather/3d"
day_forecast_json = json.loads(requests.get(url, params, headers=headers).text)

# -----------------------今天天气状况-----------------------------
# 天气状况
day_forecast_today = day_forecast_json["daily"][0]
# 日出时间
day_forecast_today_sunrise = day_forecast_today["sunrise"]
# 日落时间
day_forecast_today_sunset = day_forecast_today["sunset"]
# 天气
day_forecast_today_weather = day_forecast_today["textDay"]
# 最低温度
day_forecast_today_temperature_min = day_forecast_today["tempMin"]+"℃"
# 最高温度
day_forecast_today_temperature_max = day_forecast_today["tempMax"]+"℃"
# 夜间天气
day_forecast_today_night = day_forecast_today["textNight"]
# 白天风向
day_forecast_today_windDirDay = day_forecast_today["windDirDay"]
# 夜间风向
day_forecast_today_windDirNight = day_forecast_today["windDirNight"]
# 风力等级
day_forecast_today_windScaleDay = day_forecast_today["windScaleDay"]
# -----------------------今天天气状况-----------------------------


# -----------------------明天天气状况-----------------------------
# 天气状况
day_forecast_tomorrow = day_forecast_json["daily"][1]
# 天气
day_forecast_tomorrow_weather = day_forecast_tomorrow["textDay"]
# 日出时间
day_forecast_tomorrow_sunrise = day_forecast_tomorrow["sunrise"]
# 日落时间
day_forecast_tomorrow_sunset = day_forecast_tomorrow["sunset"]
# 最低温度
day_forecast_tomorrow_temperature_min = day_forecast_tomorrow["tempMin"] + "℃"
# 最高温度
day_forecast_tomorrow_temperature_max = day_forecast_tomorrow["tempMax"] + "℃"
# 夜间天气
day_forecast_tomorrow_night = day_forecast_today["textNight"]
# 白天风向
day_forecast_tomorrow_windDirDay = day_forecast_today["windDirDay"]
# 夜间风向
day_forecast_tomorrow_windDirNight = day_forecast_today["windDirNight"]
# 风力等级
day_forecast_tomorrow_windScaleDay = day_forecast_today["windScaleDay"]
# -----------------------明天天气状况-----------------------------


# -----------------------后天天气状况-----------------------------
# 天气状况
day_forecast_T2 = day_forecast_json["daily"][2]
# 天气
day_forecast_T2_textDay = day_forecast_T2["textDay"]
# 最低温度
day_forecast_T2_temperature_min = day_forecast_T2["tempMin"] + "℃"
# 最高温度
day_forecast_T2_temperature_max = day_forecast_T2["tempMax"] + "℃"
# -----------------------后天天气状况-----------------------------


# 距离春节还有多少天
def days_until_spring_festival(year=None):
    """
    计算距离下一个春节还有多少天。
    如果未提供年份，则默认为当前年份。
    """
    if year is None:
        year = datetime.now().year  # 获取当前年份

    # 获取当年春节的日期（农历正月初一转换为公历）
    spring_festival_lunar = LunarDate(year, 1, 1)
    spring_festival_solar = spring_festival_lunar.toSolarDate()

    # 获取当前日期
    today = datetime.now().date()

    # 计算差值，注意需要将日期转换为同类型的对象才能相减
    days_until = (spring_festival_solar - today).days

    # 如果春节已经过去，则计算到下一年的春节
    if days_until <= 0:
        days_until = days_until_spring_festival(year + 1)

    return days_until


# 在一起多天计算
def get_count():
    delta = today - datetime.strptime(start_date, "%Y-%m-%d")
    return delta.days+1


# 生日计算
def get_birthday():
    next = datetime.strptime(str(date.today().year) + "-" + birthday, "%Y-%m-%d")
    if next < datetime.now():
      next = next.replace(year=next.year + 1)
    return (next - today).days


# 彩虹屁接口
def get_words():
    words = requests.get("https://api.shadiao.pro/chp")
    if words.status_code != 200:
        return get_words()
    text = words.json()['data']['text']

    # 按照20个字符分割字符串
    chunk_size = 20
    split_notes = [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]
    # 分配note N 如果split_notes元素少于5，则用空字符串填充
    [note1, note2, note3, note4, note5] = (split_notes + [""] * 5)[:5]
    return note1, note2, note3, note4, note5


if __name__ == '__main__':
    # 获取微信客户端
    client = WeChatClient(app_id, app_secret)

    # 获取微信模板消息接口
    wm = WeChatMessage(client)

    # 获取彩虹屁
    note1, note2, note3, note4, note5 = get_words()

    # 获取当前UTC时间
    now_utc = datetime.utcnow()
    # 转换为北京时间（UTC+8）
    beijing_time = now_utc + timedelta(hours=0)
    # 获取当前小时数
    hour_of_day = beijing_time.hour

    # 默认发当天
    strDay = "today"
    # 如果当前时间大于15点，也就是晚上，则发送明天天气
    if hour_of_day > 15:
        strDay = "tomorrow"
        template_id_day = template_id_night

    print("当前时间：" + str(hour_of_day)+"即将推送："+strDay+"信息")

    data = {"name": {"value": name},
            "today": {"value": today_date},
            "city": {"value": city},
            "weather": {"value": globals()[f'day_forecast_{strDay}_weather']},
            "now_temperature": {"value": now_temperature},
            "min_temperature": {"value": globals()[f'day_forecast_{strDay}_temperature_min']},
            "max_temperature": {"value": globals()[f'day_forecast_{strDay}_temperature_max']},
            "love_date": {"value": get_count()},
            "birthday": {"value": get_birthday()},
            "diff_date1": {"value": days_until_spring_festival()},
            "sunrise": {"value": globals()[f'day_forecast_{strDay}_sunrise']},
            "sunset": {"value": globals()[f'day_forecast_{strDay}_sunset']},
            "textNight": {"value": globals()[f'day_forecast_{strDay}_night']},
            "windDirDay": {"value": globals()[f'day_forecast_{strDay}_windDirDay']},
            "windDirNight": {"value": globals()[f'day_forecast_{strDay}_windDirNight']},
            "windScaleDay": {"value": globals()[f'day_forecast_{strDay}_windScaleDay']},
            "note1": {"value": note1},
            "note2": {"value": note2},
            "note3": {"value": note3},
            "note4": {"value": note4},
            "note5": {"value": note5}
            }
    # print(data)

    # 拆分user_ids
    user_ids = user_ids.split(";")
    # for e in user_ids:
    #     res = wm.send_template(e, template_id_day, data)
    #     print(res)