from app.web.templates import templates


def render(request, template, **context):
    return templates.TemplateResponse(
        template,
        {
            "request": request,
            "user": request.session.get("user"),
            **context
        }
    )
