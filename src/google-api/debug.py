import json
import requests
import datetime ,calendar
from dateutil.relativedelta import relativedelta

def get_first_date(dt):
    return dt.replace(day=1)

def get_last_date(dt):
    return dt.replace(day=calendar.monthrange(dt.year, dt.month)[1])

dt = datetime.datetime.today()
print(dt)
one_month_after = dt + relativedelta(months=1)
print(one_month_after)
print(get_first_date(one_month_after),type(get_first_date(one_month_after)))
print(get_last_date(one_month_after))
firstDate = get_first_date(one_month_after)
lastDate = get_last_date(one_month_after)

firstDateParam = f"{str(firstDate.year)}-{str(firstDate.month)}-{str(firstDate.day)}T{str(firstDate.hour)}:{str(firstDate.minute)}:{str(firstDate.second)}+09:00"
endDateParam = f"{str(lastDate.year)}-{str(lastDate.month)}-{str(lastDate.day)}T{str(lastDate.hour)}:{str(lastDate.minute)}:{str(lastDate.second)}+09:00"
print(firstDateParam)
print("2022-07-30T00:00:00+09:00")



d = datetime.datetime.fromisoformat('2022-07-01T08:00:00+09:00'[:-6])
d = d.strftime('%Y-%m-%d %H:%M:%S')
print(d)
tdatetime = datetime.datetime.strptime(d, '%Y-%m-%d %H:%M:%S')
print(tdatetime,type(tdatetime))
