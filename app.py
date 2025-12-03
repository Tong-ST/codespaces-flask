import os
import requests
from flask import Flask, redirect, request

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "fallback_secret")

CLIENT_ID = os.getenv("GITHUB_CLIENT_ID")
CLIENT_SECRET = os.getenv("GITHUB_CLIENT_SECRET")

REPOSITORY = "Tong-ST/codespaces-flask"  # owner/repo format
BRANCH = "main"

RENDER_URL = os.getenv("RENDER_EXTERNAL_URL", "http://localhost:5000")


@app.route("/")
def index():
    return '<a href="/login">Sign in with GitHub</a>'


@app.route("/login")
def login():
    callback_url = f"{RENDER_URL}/callback"
    login_url = (
        f"https://github.com/login/oauth/authorize"
        f"?client_id={CLIENT_ID}"
        f"&redirect_uri={callback_url}"
        f"&scope=codespace"
    )
    return redirect(login_url)


@app.route("/callback")
def callback():
    code = request.args.get("code")
    if not code:
        return "Error: No code returned from GitHub.", 400

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

    print("DEBUG token_resp:", token_resp)  # Render logs

    access_token = token_resp.get("access_token")
    if not access_token:
        return f"Error getting access token: {token_resp}", 400

    # Attempt to create Codespace
    create_resp = requests.post(
        "https://api.github.com/user/codespaces/",
        headers={"Authorization": f"token {access_token}"},
        json={
            "repository": REPOSITORY,
            "ref": BRANCH,
            "machine": "basicLinux",
            "devcontainer_path": ".devcontainer/devcontainer.json",
        },
    ).json()

    print("DEBUG create_resp:", create_resp)  # Render logs

    codespace_url = create_resp.get("web_url")
    if not codespace_url:
        return f"Error creating Codespace: {create_resp}", 400

    return redirect(codespace_url)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
