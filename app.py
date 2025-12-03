import os
import requests
from flask import Flask, redirect, request, session

app = Flask(__name__)
app.secret_key = os.getenv("RANDOM_SECRET")

CLIENT_ID = os.getenv("GITHUB_CLIENT_ID")
CLIENT_SECRET = os.getenv("GITHUB_CLIENT_SECRET")

REPOSITORY = "https://github.com/Tong-ST/codespaces-flask"   # Your repo
BRANCH = "main"


@app.route("/")
def index():
    return '<a href="/login">Sign in with GitHub</a>'


@app.route("/login")
def login():
    return redirect(
        f"https://github.com/login/oauth/authorize"
        f"?client_id={CLIENT_ID}&scope=codespace"
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

    access_token = token_resp.get("access_token")

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

    # URL of the student’s IDE
    codespace_url = create["web_url"]

    return redirect(codespace_url)


app.run(host="0.0.0.0", port=8080)
