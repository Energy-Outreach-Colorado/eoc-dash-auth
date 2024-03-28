import requests
import werkzeug
from dash import Dash
from dash_auth.auth import Auth  # type: ignore[import-untyped]
from flask import Response, redirect, request

BASE_FRONTEND_URL = "https://speechium.com"
BASE_API_URL = "https://speechium.com/api"


class EOCAuth(Auth):
    def __init__(self, app: Dash, path: str, **obsolete):
        super().__init__(app, **obsolete)

        if len(path) < 1:
            raise ValueError("EOCAuth path must be at least one character")
        if path[0] == "/":
            raise ValueError("Ensure path doesn't contain a leading slash")
        self.path = path

    def is_authorized(self) -> bool:
        auth_cookie = request.cookies.get("fastapiusersauth", None)
        if auth_cookie is None:
            return False

        response = requests.get(
            f"{BASE_API_URL}/dashboards/", cookies={"fastapiusersauth": auth_cookie}
        )
        if not response.ok:
            return False

        dashboard_paths = [dashboard["path"] for dashboard in response.json()]
        return self.path in dashboard_paths

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
