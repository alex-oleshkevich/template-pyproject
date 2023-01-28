from kupala.responses import redirect_to_path
from starlette.requests import Request
from starlette.responses import Response


def error_401(request: Request, exc: Exception) -> Response:
    return redirect_to_path(request, path_name="login", status_code=302)


error_handlers = {
    401: error_401,
}
