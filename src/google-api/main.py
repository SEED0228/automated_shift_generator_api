from flask import *
import datetime
import json,os,requests
import datetime ,calendar
from dateutil.relativedelta import relativedelta
app = Flask(__name__)
USERINFO_SCOPES = 'https://www.googleapis.com/auth/userinfo.profile'
USERINFO_API = "https://www.googleapis.com/oauth2/v1/userinfo"
CALENDAR_SCOPES = "https://www.googleapis.com/auth/calendar"
CALENDAR_API = "https://www.googleapis.com/calendar/v3/calendars/c_h37mp5ut4henp960odiqkgpiko@group.calendar.google.com/events"
OAUTH_ACCOUNTS = "https://accounts.google.com/o/oauth2/v2/auth"
OAUTH_TOKEN = "https://accounts.google.com/o/oauth2/token"
TOKEN_FILE = "/var/www/html_secure/google-api/tokens/token.json"
DEFAULT_PATH = "/var/www/html_secure/google-api/"
USERINFO_PATH = "/var/www/html_secure/google-api/users/"
CALENDAR_PATH = "/var/www/html_secure/google-api/calendars/"

# 月初を取得
def get_first_date(dt):
    return dt.replace(day=1)
# 月末の取得
def get_last_date(dt):
    return dt.replace(day=calendar.monthrange(dt.year, dt.month)[1])


#User情報を取得
def accessProfile():
    accessToken = open(TOKEN_FILE, 'r')
    accessToken_load = json.load(accessToken)
    bearer = "Bearer" + accessToken_load["access_token"]
    headers = {
        "Authorization" : bearer
    }
    res = requests.get(USERINFO_API, headers=headers)
    print(res.status_code)
    
    resData = res.json()
    fileName = USERINFO_PATH + str(resData["id"]) + ".json"
    #### Userprofileをjsonで保存 #####
    with open(fileName, 'w') as f:
        json.dump(resData, f, ensure_ascii=False,indent=4)
    
    return res.text

# カレンダー情報を取得
def accessCalendar():
    accessToken = open(TOKEN_FILE, 'r')
    accessToken_load = json.load(accessToken)
    bearer = "Bearer " + accessToken_load["access_token"]
    headers = {
        "Authorization" : bearer,
        "Accept" : "application/json",
        "Content-Type" : "application/json"
    }
    
    ### 時刻を指定する形式：：：：：：2022-07-30T00:00:00+09:00 ###
    dt = datetime.datetime.today()
    one_month_after = dt + relativedelta(months=1)
    firstDate = get_first_date(one_month_after)
    lastDate = get_last_date(one_month_after)
    firstDateParam = f"{str(firstDate.year)}-{str(firstDate.month)}-{str(firstDate.day)}T{str(firstDate.hour)}:{str(firstDate.minute)}:{str(firstDate.second)}+09:00"
    lastDateParam = f"{str(lastDate.year)}-{str(lastDate.month)}-{str(lastDate.day)}T{str(lastDate.hour)}:{str(lastDate.minute)}:{str(lastDate.second)}+09:00"
    param = {
        "timeMax" : lastDateParam,
        "timeMin" : firstDateParam
    }
    # param = {
    #     "maxResults" : "1"
    # }
    res = requests.get(CALENDAR_API, headers=headers,params=param)
    resData = res.json()
    
    fileName = CALENDAR_PATH + "cal.json"
    
    #### カレンダーをjsonで保存 #####
    with open(fileName, 'w') as f:
        json.dump(resData, f, ensure_ascii=False,indent=4)
    
    return redirect("http://high-entropy.australiaeast.cloudapp.azure.com:8080/list")

def oauth(scope):
    ##### 認可および認証のプロセス #####
            
    """OAuth 2.0
    https://accounts.google.com/o/oauth2/v2/auth?
    scope=スコープ
    &access_type=offline
    &include_granted_scope=true
    &response_type=code
    &redirect_uri=設定したリダイレクトURI
    &client_id=クライアントID
    """
    ### client_secret.jsonの読み込み ###
    json_open = open('/var/www/html_secure/google-api/client_secret.json', 'r')
    json_load = json.load(json_open)
    accessQueryPara = {
        "client_id" : json_load["web"]["client_id"],
        "redirect_uri" : json_load["web"]["redirect_uris"][0],
        "scope" : scope,
        "access_type" : "offline",
        "response_type" : "code"
    }
    req_url = OAUTH_ACCOUNTS
    req_url += "?"
    for k,v in accessQueryPara.items():
        plane = str(k) + "=" + str(v)
        req_url += plane
        req_url += "&"
    print(req_url)
    
    return req_url

def getAccessToken(code):
    ##### アクセストークンの取得 #####
    # レスポンスヘッダにcodeがなければ認証前
    
    print(f"code : {code}")
    print("認証OK")
    
    """アクセストークン
    https://accounts.google.com/o/oauth2/token
    -d code=取得した認可コード 
    -d client_id=クライアントID
    -d client_secret=クライアントシークレット
    -dredirect_uri=リダイレクトURI
    -d grant_type=authorization_code 
    """
    ### client_secret.jsonの読み込み ###
    json_open = open('/var/www/html_secure/google-api/client_secret.json', 'r')
    json_load = json.load(json_open)
    tokenQueryPara = {
        "client_id" : json_load["web"]["client_id"],
        "code" : code,
        "redirect_uri" : json_load["web"]["redirect_uris"][0],
        "grant_type" : "authorization_code",
        "client_secret" :  json_load["web"]["client_secret"]
    }
    
    #### TOKENはPOSTじゃないと動かないっぽい ####
    # req_url += "?"
    # for k,v in tokenQueryPara.items():
    #     plane = str(k) + "=" + str(v)
    #     req_url += plane
    #     req_url += "&"
    res = requests.post(OAUTH_TOKEN, json=tokenQueryPara)
    print(res.status_code)
    resData = res.json()
    print(resData)
    
    #### アクセストークンをjsonで保存 #####
    #fileName = TOKEN_PATH + 
    with open(TOKEN_FILE, 'w') as f:
        json.dump(resData, f, ensure_ascii=False,indent=4)
    result = accessCalendar()
    
    return result


@app.route("/login")
def google_api_hands():
    if os.path.isfile(TOKEN_FILE):
        result = 0
        accessToken = open(TOKEN_FILE, 'r')
        accessToken_load = json.load(accessToken)
        ### 何かしたの理由でtoken.jsonの中にaccess_tokenがない場合は再度ログイン ###
        if "access_token" not in accessToken_load:
            os.remove(TOKEN_FILE)
            return redirect("http://high-entropy.australiaeast.cloudapp.azure.com:8080/login")
        #result = accessProfile()
        result = accessCalendar()
        ### access_tokenはあるけど403が帰ってきた場合はtoken.jsonを更新 ###
        if "error" in result:
            if str(result["error"]["code"]) == "403":
                os.remove(TOKEN_FILE)
                return redirect("http://high-entropy.australiaeast.cloudapp.azure.com:8080/login")
        
        return redirect("http://high-entropy.australiaeast.cloudapp.azure.com:8080/list")
    else:
        
        ## OAuth認証が通るとパラメータにcodeが入る ##
        ## codeがあれば認証不必要 , なければ認証 ##
        if request.args.get('code') != None:
            ##### アクセストークンの取得 #####
            # レスポンスヘッダにcodeがなければ認証前
            code = request.args.get('code')
            result = getAccessToken(code)
            return result
        else:
            req_url = oauth(CALENDAR_SCOPES)
            return redirect(req_url)
buttonLink = "http://high-entropy.australiaeast.cloudapp.azure.com:8080/login"
calendarListLink = "http://high-entropy.australiaeast.cloudapp.azure.com:8080/list"
calendarUpdateLink = "http://high-entropy.australiaeast.cloudapp.azure.com:8080/update_calendar"
@app.route("/")
def mainPage():
    
    html = f"""
    <!DOCTYPE>
    <html lang="ja">
    <head>
        <title>Google API Main Page</title>
        <meta charaset="utf-8">
    </head>
    <body>
        <h2>Google API Mainpage</h2>
        <button onclick='location.href="{buttonLink}"'>ログイン</button>
        <button onclick='location.href="{calendarListLink}"'>カレンダーの一覧</button>
        <button onclick='location.href="{calendarUpdateLink}"'>カレンダーの更新</button>
    </body>
    </html>
    """
    return html

@app.route("/list")
def calendarList():
    json_open = open('/var/www/html_secure/google-api/calendars/cal.json', 'r')
    json_load = json.load(json_open)
    html = f"""
    <!DOCTYPE>
    <html lang="ja">
    <head>
        <title>Google API Main Page</title>
        <meta charaset="utf-8">
    </head>
    <body>
        <h2>Googleカレンダーリスト</h2> 
        <h3>カレンダー : [{json_load['description']}]</h3>
        <button onclick='location.href="{calendarUpdateLink}"'>カレンダーの更新</button>
    """
    
    for col in json_load["items"]:
        html += f"<p>予定 : {col['summary']}</p>"
        start = col['start']
        end = col['end']
        if "date" in start:
            start = start['date']
            dStart = datetime.datetime.strptime(dStart, '%Y-%m-%d')
            end = end['date']
            dEnd = datetime.datetime.strptime(dEnd, '%Y-%m-%d')
        else:
            start = start['dateTime']
            dStart = datetime.datetime.fromisoformat(start[:-6])
            dStart = dStart.strftime('%Y-%m-%d %H:%M:%S')
            dStart = datetime.datetime.strptime(dStart, '%Y-%m-%d %H:%M:%S')
            end = end['dateTime']
            dEnd = datetime.datetime.fromisoformat(end[:-6])
            dEnd = dEnd.strftime('%Y-%m-%d %H:%M:%S')
            dEnd =datetime.datetime.strptime(dEnd, '%Y-%m-%d %H:%M:%S')
        html += f"<p>{dStart.year}年 {dStart.month}月 {dStart.day}日 {dStart.hour}時{dStart.minute}分 〜 {dEnd.hour}時{dEnd.minute}分</p>"
        
    
    html += """
    </body>
    </html>
    """
    return html

@app.route("/update_calendar")
def updateCalendar():
    accessCalendar()
    return redirect("http://high-entropy.australiaeast.cloudapp.azure.com:8080/list")



    
if __name__ == '__main__':
    app.run(host="0.0.0.0",port="8080",debug=True)
    