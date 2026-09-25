import re
from django import template
from django.template.loader import render_to_string
from polls.models import Poll

register = template.Library()

# Regex qui matche {% FORM slug %} ou {% form slug %}
_POLL_RE = re.compile(r"\{%\s*form\s+([\w-]+)\s*%\}", re.IGNORECASE)


@register.filter(name="render_polls", is_safe=True)
def render_polls(content: str, request=None) -> str:
    """Remplace tous les {% FORM slug %} par le HTML du sondage.

    Usage :
        {{ article.content | render_polls:request | safe }}
    """
    if not content:
        return ""

    def replace(match):
        slug = match.group(1)
        try:
            poll = Poll.objects.get(slug=slug, is_active=True)
        except Poll.DoesNotExist:
            # Fallback visible : l'auteur du site verra qu'il y a un souci
            return (
                f'<div class="poll-missing">'
                f'Sondage « {slug} » introuvable ou désactivé.'
                f'</div>'
            )

        user = request.user if request else None
        html = render_to_string(
            "polls/poll.html",
            {"poll": poll, "user": user, "request": request},
        )
        return html

    return _POLL_RE.sub(replace, content)