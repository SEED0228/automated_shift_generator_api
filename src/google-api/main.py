from flask import *
import json,os,requests
app = Flask(__name__)
SCOPES = 'https://www.googleapis.com/auth/userinfo.profile'
USEINFOAPI = "https://www.googleapis.com/oauth2/v1/userinfo"
OAUTH_ACCOUNTS = "https://accounts.google.com/o/oauth2/v2/auth"
OAUTH_TOKEN = "https://accounts.google.com/o/oauth2/token"
TOKEN_FILE = "/var/www/html_secure/google-api/token.json"
DEFAULT_PATH = "/var/www/html_secure/google-api/"

def accessProfile():
    accessToken = open(TOKEN_FILE, 'r')
    accessToken_load = json.load(accessToken)
    bearer = "Bearer" + accessToken_load["access_token"]
    headers = {
        "Authorization" : bearer
    }
    res = requests.get(USEINFOAPI, headers=headers)
    print(res.status_code)
    
    resData = res.json()
    print(resData)
    print(resData["id"])
    fileName = DEFAULT_PATH + str(resData["id"]) + ".json"
    print(f"fileName : {fileName}")
    
    #### Userprofileをjsonで保存 #####
    with open(fileName, 'w') as f:
        json.dump(resData, f, ensure_ascii=False,indent=4)
    
    return res.text

@app.route("/")
def google_api_hands():
    if os.path.isfile(TOKEN_FILE):
        result = accessProfile()
        return result
    else:
        ### client_secret.jsonの読み込み ###
        json_open = open('/var/www/html_secure/google-api/client_secret.json', 'r')
        json_load = json.load(json_open)
        print(json_load)
        
        
        if request.args.get('code') != None:
            ##### アクセストークンの取得 #####
            # レスポンスヘッダにcodeがなければ認証前
            code = request.args.get('code')
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
            with open(TOKEN_FILE, 'w') as f:
                json.dump(resData, f, ensure_ascii=False,indent=4)
            
            
            result = accessProfile()
            return result
        else:
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
            accessQueryPara = {
                "client_id" : json_load["web"]["client_id"],
                "redirect_uri" : json_load["web"]["redirect_uris"][0],
                "scope" : SCOPES,
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
            
            return redirect(req_url)


    
if __name__ == '__main__':
    app.run(host="0.0.0.0",port="8080",debug=True)
    