from datetime import datetime, time
now = datetime.now()
now_time = now.time()
if now_time >= time(23,00) or now_time <= time(13,45):
    print("night")