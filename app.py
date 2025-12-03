import os
import requests
from flask import Flask, redirect, request

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY")   # Make sure Render has this

CLIENT_ID = os.getenv("GITHUB_CLIENT_ID")
CLIENT_SECRET = os.getenv("GITHUB_CLIENT_SECRET")

REPOSITORY = "Tong-ST/codespaces-flask"   # Correct format
BRANCH = "main"

RENDER_URL = os.getenv("RENDER_EXTERNAL_URL")  # Render auto-provides this


@app.route("/")
def index():
    return '<a href="/login">Sign in with GitHub</a>'


@app.route("/login")
def login():
    callback_url = f"{RENDER_URL}/callback"

    return redirect(
        f"https://github.com/login/oauth/authorize"
        f"?client_id={CLIENT_ID}"
        f"&redirect_uri={callback_url}"
        f"&scope=codespace"
    )


@app.route("/callback")
def callback():
    code = request.args.get("code")

    # Exchange code for access token
    token_resp = requests.post(
        "https://github.com/login/oauth/access_token",
        headers={"Accept": "application/json"},
        data={
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "code": code,
        },
    ).json()
    
    print(token_resp)
    access_token = token_resp.get("access_token")
    print("Access token:", access_token)
    
    if not access_token:
        return f"Error getting access token: {token_resp}", 400



    # Create Codespace
    create = requests.post(
        "https://api.github.com/user/codespaces/",
        headers={"Authorization": f"token {access_token}"},
        json={
            "repository": REPOSITORY,
            "ref": BRANCH,
            "machine": "basicLinux",
            "devcontainer_path": ".devcontainer/devcontainer.json",
        },
    ).json()

    codespace_url = create["web_url"]

    return redirect(codespace_url)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
