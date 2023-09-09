from datetime import datetime

def get_current_time():
    current_time = datetime.now().time()
    hour = current_time.hour
    minute = current_time.minute

    hour_str = str(hour).zfill(2)
    minute_str = str(minute).zfill(2)

    return hour_str, minute_str
