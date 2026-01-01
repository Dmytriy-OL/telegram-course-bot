from fastapi import Request


def get_template_user(request: Request):
    return request.session.get("user")
