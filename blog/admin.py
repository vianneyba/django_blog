from django.contrib import admin
from django.conf import settings
from django.contrib import admin, messages
from django.utils.html import format_html

from blog.models import Article, Category, Tag

import requests
import logging

logger = logging.getLogger(__name__)
PROD_API_URL = getattr(settings, "PROD_API_URL", "")
PROD_API_USER = getattr(settings, "PROD_API_USER", "")
PROD_API_PASSWORD = getattr(settings, "PROD_API_PASSWORD", "")

def _get_prod_token() -> str | None:
    """Récupère un token JWT depuis l'API de prod."""
    if not (PROD_API_URL and PROD_API_USER and PROD_API_PASSWORD):
        return None

    try:
        response = requests.post(
            f"{PROD_API_URL}/api/token/",
            data={"username": PROD_API_USER, "password": PROD_API_PASSWORD},
            timeout=10,
        )
        response.raise_for_status()
        return response.json().get("access")
    except requests.RequestException as exc:
        logger.error("Auth API prod échouée : %s", exc)
        return None

@admin.action(description="Envoyer vers la prod")
def push_to_prod(modeladmin, request, queryset):
    """Envoie les articles sélectionnés vers l'API de production."""
    token = _get_prod_token()
    if not token:
        modeladmin.message_user(
            request,
            "Impossible d'obtenir un token depuis l'API de prod. "
            "Vérifie PROD_API_URL / PROD_API_USER / PROD_API_PASSWORD.",
            level=messages.ERROR,
        )
        return

    headers = {
        "Accept": "application/json",
        "Authorization": f"Bearer {token}",
    }

    success_count = 0
    error_count = 0
    errors = []

    for article in queryset:
        payload = {
            "title": article.title,
            "category": article.category.name if article.category else "",
            "tags": [tag.name for tag in article.tags.all()],
            "content": article.raw_content,   # ← important : le BRUT, pas le rendu
            "published": article.published,
        }

        try:
            response = requests.post(
                f"{PROD_API_URL}/blog/api/articles/",
                json=payload,
                headers=headers,
                timeout=30,
            )
        except requests.RequestException as exc:
            error_count += 1
            errors.append(f"{article.slug} : {exc}")
            continue

        if response.status_code in (200, 201):
            success_count += 1
        else:
            error_count += 1
            errors.append(
                f"{article.slug} : {response.status_code} — {response.text[:200]}"
            )

    # Message récapitulatif
    if success_count:
        modeladmin.message_user(
            request,
            f"{success_count} article(s) envoyé(s) avec succès.",
            level=messages.SUCCESS,
        )
    if error_count:
        modeladmin.message_user(
            request,
            f"{error_count} erreur(s) :\n" + "\n".join(errors),
            level=messages.ERROR,
        )

@admin.action(description="Plublier un article")
def make_published(ArticleAdmin, request, queryset):
    queryset.update(published=True)

@admin.action(description="Publier sur la prod")
def publish_on_prod(modeladmin, request, queryset):
    queryset.update(published=True)
    push_to_prod(modeladmin, request, queryset)

@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "published", "created_at", "prod_link")
    list_filter = ("published", "category")
    search_fields = ("title", "slug")
    prepopulated_fields = {"slug": ("title",)}
    filter_horizontal = ("tags",)
    actions = [push_to_prod, make_published]

    @admin.display(description="Prod")
    def prod_link(self, obj):
        """Affiche un lien vers l'article en prod, s'il est publié."""
        if not PROD_API_URL:
            return "—"
        url = f"{PROD_API_URL}/blog/article/{obj.slug}/"
        return format_html('<a href="{}" target="_blank">voir</a>', url)


admin.site.register(Category)
admin.site.register(Tag)