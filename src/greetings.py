import datetime

def get_greeting():
    now = datetime.datetime.now()
    hour = now.hour

    if 22 <= hour or hour < 4:
        return "🌃Доброї ночі!😴"
    elif 5 <= hour < 9:
        return "☀️Доброго ранку!☕️"
    elif 9 <= hour < 12:
        return "🌞Доброго дня!😊"
    elif 12 <= hour < 17:
        return "🌞Доброго дня!😊"
    else:
        return "🌅Доброго вечора!😊"
