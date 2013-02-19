from survey import settings


def settingscontext(request):
    """
        Gathers any UPPERCASE variable name in survey.settings
        and adds it to template context.
    """
    return {name: getattr(settings, name) for name in dir(settings) if name.isupper()}
