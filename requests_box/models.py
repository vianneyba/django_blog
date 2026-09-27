# requests_box/models.py
from django.conf import settings
from django.db import models

class SiteRequest(models.Model):
    class Kind(models.TextChoices):
        PASSWORD = "password", "Perte de mot de passe"
        ACCOUNT = "account", "Problème de compte"
        CONTENT = "content", "Correction / contenu"
        OTHER = "other", "Autre"

    class Status(models.TextChoices):
        NEW = "new", "Nouvelle"
        SEEN = "seen", "Vue"
        DONE = "done", "Traitée"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name="site_requests",
    )
    kind = models.CharField(max_length=20, choices=Kind.choices, default=Kind.OTHER)
    name = models.CharField("Nom", max_length=120)
    email = models.EmailField("Email")
    username = models.CharField("Identifiant", max_length=150, blank=True)
    message = models.TextField("Message")
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.NEW)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.get_kind_display()} — {self.email}"