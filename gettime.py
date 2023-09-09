from datetime import datetime

def get_current_time():
    current_time = datetime.now().time()
    hour = current_time.hour
    minute = current_time.minute

    return str(hour).zfill(2), str(minute).zfill(2)

