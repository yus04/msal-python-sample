import os
import uuid
import msal
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import RedirectResponse
from dotenv import load_dotenv

# .envファイルを読み込む
load_dotenv()

app = FastAPI()

# MSALの設定
config = {
    "client_id": os.getenv("CLIENT_ID"),
    "client_secret": os.getenv("CLIENT_SECRET"),
    "authority": os.getenv("AUTHORITY"),
    "scope": os.getenv("SCOPE").split(','),
    "redirect_uri": os.getenv("REDIRECT_URI")
}

# MSAL ConfidentialClientApplication のインスタンスを生成
application = msal.ConfidentialClientApplication(
    config["client_id"],
    authority=config["authority"],
    client_credential=config["client_secret"]
)

# ログインページと認証フローの実装
@app.get("/")
async def main():
    return RedirectResponse(url="/login")

@app.get("/login")
async def login():
    auth_state = str(uuid.uuid4())  # ランダムなstateを生成

    # MSAL認証リクエストURLを生成
    authorization_url = application.get_authorization_request_url(
        config['scope'], state=auth_state, redirect_uri=config['redirect_uri']
    )

    # 認証URLにリダイレクト
    return RedirectResponse(url=authorization_url)

@app.get("/get_access_token")
async def get_access_token(request: Request):
    code = request.query_params.get('code')
    state = request.query_params.get('state')

    # stateの比較
    if not state:
        raise HTTPException(status_code=400, detail="State is required")

    # MSALを使ってアクセストークンを取得
    result = application.acquire_token_by_authorization_code(
        code, scopes=config["scope"], redirect_uri=config['redirect_uri']
    )

    if "access_token" in result:
        # アクセストークンを返却
        return {"access_token": result["access_token"]}
    else:
        raise HTTPException(status_code=400, detail="Error acquiring access token")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
