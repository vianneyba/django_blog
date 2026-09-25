# polls/views.py
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views.decorators.http import require_POST
from django.utils import timezone

from .models import Poll, PollChoice, PollResponse


@require_POST
def vote(request, slug):
    poll = get_object_or_404(Poll, slug=slug)

    if not poll.is_open:
        messages.error(request, "Ce sondage est fermé.")
        return redirect(request.META.get("HTTP_REFERER", "/"))

    if poll.require_login and not request.user.is_authenticated:
        messages.error(request, "Vous devez être connecté pour voter.")
        return redirect(request.META.get("HTTP_REFERER", "/"))

    if poll.one_vote_per_user and poll.user_has_voted(request.user):
        messages.warning(request, "Vous avez déjà voté.")
        return redirect(request.META.get("HTTP_REFERER", "/"))

    # Identifiant du votant
    user = request.user if request.user.is_authenticated else None
    session_key = request.session.session_key or ""
    ip = _get_client_ip(request)

    # Traitement selon le type
    if poll.poll_type == "free":
        text = request.POST.get("free_text", "").strip()
        if not text:
            messages.error(request, "Réponse vide.")
            return redirect(request.META.get("HTTP_REFERER", "/"))

        PollResponse.objects.create(
            poll=poll, free_text=text,
            user=user, session_key=session_key, ip_address=ip,
            one_vote_per_user=poll.one_vote_per_user,
        )

    elif poll.poll_type == "single":
        choice_id = request.POST.get("choice")
        choice = get_object_or_404(PollChoice, id=choice_id, poll=poll)
        PollResponse.objects.create(
            poll=poll, choice=choice,
            user=user, session_key=session_key, ip_address=ip,
            one_vote_per_user=poll.one_vote_per_user,
        )

    elif poll.poll_type == "multiple":
        choice_ids = request.POST.getlist("choice")
        if not choice_ids:
            messages.error(request, "Sélectionnez au moins un choix.")
            return redirect(request.META.get("HTTP_REFERER", "/"))
        choices = PollChoice.objects.filter(id__in=choice_ids, poll=poll)
        for choice in choices:
            PollResponse.objects.create(
                poll=poll, choice=choice,
                user=user, session_key=session_key, ip_address=ip,
                one_vote_per_user=poll.one_vote_per_user,
            )

    messages.success(request, "Merci pour votre vote !")
    return redirect(request.META.get("HTTP_REFERER", "/"))


def _get_client_ip(request):
    xff = request.META.get("HTTP_X_FORWARDED_FOR")
    if xff:
        return xff.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")