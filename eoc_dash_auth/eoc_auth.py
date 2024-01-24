import requests
import werkzeug
from dash_auth.auth import Auth  # type: ignore[import-untyped]
from flask import Response, redirect, request
from requests import JSONDecodeError

from eoc_dash_auth import BASE_API_URL, BASE_FRONTEND_URL


class EOCAuth(Auth):
    def is_authorized(self) -> bool:
        auth_cookie = request.cookies.get("fastapiusersauth", None)
        if auth_cookie is None:
            return False

        response = requests.get(
            f"{BASE_API_URL}/users/me", cookies={"fastapiusersauth": auth_cookie}
        )
        try:
            response.json()
        except JSONDecodeError:
            return False

        return True

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
