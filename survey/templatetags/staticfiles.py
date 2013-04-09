try:
    from django.contrib.staticfiles.templatetags import staticfiles
except ImportError:
    from urlparse import urljoin
    from django import template
    from django.templatetags.static import PrefixNode

    register = template.Library()

    # Fallback to simple URL handling for 1.3.x
    @register.simple_tag
    def static(path):
        """
        Joins the given path with the STATIC_URL setting.

        Usage::

            {% static path %}

        Examples::

            {% static "myapp/css/base.css" %}
            {% static variable_with_path %}

        """
        return urljoin(PrefixNode.handle_simple("STATIC_URL"), path)
