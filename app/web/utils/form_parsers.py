def get_form_values(form) -> dict:
    return {
        "birth_day": form.get("birth_day", ""),
        "birth_month": form.get("birth_month", ""),
        "birth_year": form.get("birth_year", ""),
        "email": form.get("email", ""),
        "username": form.get("login", ""),
        "terms": bool(form.get("terms")),
    }