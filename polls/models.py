import datetime
from django.contrib.auth.models import User
from django.template.defaultfilters import slugify
from django.db import models
from game.models import Game


from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.text import slugify


class Poll(models.Model):
    """Un sondage."""

    TYPE_CHOICES = [
        ("single", "Choix unique"),
        ("multiple", "Choix multiple"),
        ("free", "Réponse libre"),
    ]

    slug = models.SlugField(
        max_length=120,
        unique=True,
        help_text="Identifiant utilisé dans {% FORM slug %}",)
    question = models.TextField("Question")
    description = models.TextField(
        "Description", blank=True, help_text="Texte d'introduction optionnel")
    poll_type = models.CharField(
        "Type de sondage", max_length=10, choices=TYPE_CHOICES, default="single")

    # Ouverture / fermeture
    created_at = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField("Actif", default=True)
    closes_at = models.DateTimeField(
        "Clôture", null=True, blank=True,
        help_text="Laisser vide pour un sondage permanent",)

    # Anti-spam
    require_login = models.BooleanField(
        "Connexion obligatoire", default=False,
        help_text="Seuls les utilisateurs connectés peuvent voter",)
    one_vote_per_user = models.BooleanField(
        "Un vote par utilisateur", default=True,
        help_text="Empêche un utilisateur de voter plusieurs fois",)

    # Résultats
    show_results_before_vote = models.BooleanField(
        "Afficher les résultats avant vote", default=False)
    show_results_after_vote = models.BooleanField(
        "Afficher les résultats après vote", default=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Sondage"
        verbose_name_plural = "Sondages"

    def __str__(self):
        return self.question[:60]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.question[:100])
        super().save(*args, **kwargs)

    # ------------------------------------------------------------------
    # État du sondage
    # ------------------------------------------------------------------
    @property
    def is_open(self) -> bool:
        """Le sondage accepte-t-il des votes en ce moment ?"""
        if not self.is_active:
            return False
        if self.closes_at and timezone.now() >= self.closes_at:
            return False
        return True

    # ------------------------------------------------------------------
    # Stats
    # ------------------------------------------------------------------
    def total_votes(self) -> int:
        """Nombre total de votes (utilisateurs distincts ou réponses)."""
        return self.responses.values("user").distinct().count() \
            if self.require_login else self.responses.count()

    def results(self):
        """Retourne les résultats agrégés par choix.

        Renvoie une liste de dicts :
            [{"choice": Choice, "count": int, "percent": float}, ...]
        """
        choices = list(self.choices.all())
        total = sum(c.responses.count() for c in choices)

        results = []
        for choice in choices:
            count = choice.responses.count()
            percent = (count / total * 100) if total else 0
            results.append({
                "choice": choice,
                "count": count,
                "percent": round(percent, 1),
            })
        return results

    def user_has_voted(self, user) -> bool:
        """L'utilisateur a-t-il déjà voté à ce sondage ?"""
        if not user or not user.is_authenticated:
            return False
        return self.responses.filter(user=user).exists()
    
    def has_voted(self, user, session_key: str | None = None) -> bool:
        """L'utilisateur (ou la session) a-t-il déjà voté ?"""
        if user and user.is_authenticated:
            return self.responses.filter(user=user).exists()
        if session_key:
            return self.responses.filter(session_key=session_key).exists()
        return False

class PollChoice(models.Model):
    """Un choix possible pour un sondage à choix."""

    poll = models.ForeignKey(
        Poll, on_delete=models.CASCADE, related_name="choices")
    label = models.CharField("Libellé", max_length=200)
    order = models.PositiveIntegerField("Ordre", default=0)

    class Meta:
        ordering = ["order", "id"]
        verbose_name = "Choix"
        verbose_name_plural = "Choix"

    def __str__(self):
        return self.label


class PollResponse(models.Model):
    """Une réponse à un sondage.

    Pour un sondage "single" ou "multiple" : `choice` est rempli.
    Pour un sondage "free" : `free_text` est rempli.
    Le champ `user` ou `session_key` identifie l'auteur du vote.
    """

    poll = models.ForeignKey(
        Poll, on_delete=models.CASCADE, related_name="responses")
    choice = models.ForeignKey(
        PollChoice, on_delete=models.CASCADE, null=True, blank=True,
        related_name="responses",)
    free_text = models.TextField("Réponse libre", blank=True)

    # Auteur
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name="poll_responses",)
    session_key = models.CharField(
        max_length=64, blank=True,
        help_text="Utilisé pour les utilisateurs anonymes",)

    # Métadonnées
    created_at = models.DateTimeField(default=timezone.now)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    one_vote_per_user = models.BooleanField(default=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Réponse"
        verbose_name_plural = "Réponses"
        indexes = [
            models.Index(fields=["poll", "user"]),
            models.Index(fields=["poll", "session_key"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["poll", "user"],
                condition=models.Q(user__isnull=False, one_vote_per_user=True),
                name="unique_response_per_user_when_required",
            ),
            models.UniqueConstraint(
                fields=["poll", "session_key"],
                condition=models.Q(session_key__gt="", one_vote_per_user=True),
                name="unique_response_per_session_when_required",
            ),
        ]

    def __str__(self):
        if self.choice:
            return f"{self.poll.slug} → {self.choice.label}"
        return f"{self.poll.slug} → (libre) {self.free_text[:40]}"

    @property
    def is_free_text(self) -> bool:
        return self.poll.poll_type == "free"