import requests
import werkzeug
from dash_auth.auth import Auth  # type: ignore[import-untyped]
from flask import Response, redirect, request

BASE_FRONTEND_URL = "http://localhost:8000"
BASE_API_URL = "http://localhost:8000"


class EOCAuth(Auth):
    def is_authorized(self) -> bool:
        auth_cookie = request.cookies.get("fastapiusersauth", None)
        if auth_cookie is None:
            return False

        response = requests.get(
            f"{BASE_API_URL}/users/me", cookies={"fastapiusersauth": auth_cookie}
        )
        return response.status_code == 200

    def login_request(self) -> werkzeug.Response:
        return redirect(BASE_FRONTEND_URL, code=307)

    def auth_wrapper(self, f):
        def wrap(*args, **kwargs):
            if not self.is_authorized():
                return Response(status=403)

            response = f(*args, **kwargs)
            return response

        return wrap

    def index_auth_wrapper(self, f):
        return self.auth_wrapper(f)


__all__ = ["EOCAuth", "BASE_FRONTEND_URL", "BASE_API_URL"]
