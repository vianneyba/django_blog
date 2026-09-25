"""Rendu des blocs dynamiques dans le contenu d'un article.

Blocs supportés :
    {{ form slug=mon-sondage }}
    {{ top_list slug=mon-top }}
    {{ article=mon-article }}
    {{ type=markdown }}
    {{ type=html }}
"""

from __future__ import annotations

import re
from pathlib import Path

import markdown
from django.conf import settings
from django.template.loader import render_to_string
from django.urls import reverse


# ---------------------------------------------------------------------------
# Patterns
# ---------------------------------------------------------------------------
PATTERNS = {
    "form":          re.compile(r"\{\{\s*form\s+slug=([\w-]+)\s*\}\}"),
    "top_list":      re.compile(r"\{\{\s*top_list\s+slug=([\w-]+)\s*\}\}"),
    "article":       re.compile(r"\{\{\s*article=([\w-]+)\s*\}\}"),
    "type_markdown": re.compile(r"\{\{\s*type=markdown\s*\}\}"),
    "type_html":     re.compile(r"\{\{\s*type=html\s*\}\}"),
}


class ArticleRenderer:
    """Résout les blocs dynamiques dans le contenu brut d'un article."""

    def __init__(self, article, request=None):
        self.article = article
        self.request = request

        # Contenu BRUT — jamais article.content (sinon boucle infinie)
        self.raw = article.raw_content or ""
        self.content = self.raw

        # Anti-boucle pour {{ article=... }} récursif
        self._seen_articles = {article.slug}

    # ------------------------------------------------------------------
    # Point d'entrée
    # ------------------------------------------------------------------
    def render(self, max_depth: int = 5) -> str:
        for _ in range(max_depth):
            prev = self.content
            self._render_forms()
            self._render_top_lists()
            self._render_articles()
            if self.content == prev:
                break
        self._apply_content_type()
        return self.content

    # ------------------------------------------------------------------
    # Bloc : {{ form slug=... }}
    # ------------------------------------------------------------------
    def _render_forms(self):
        def repl(match):
            slug = match.group(1)
            try:
                from polls.models import Poll
                poll = Poll.objects.get(slug=slug, is_active=True)
            except Poll.DoesNotExist:
                return f''

            user = self.request.user if self.request else None
            session_key = ""
            if self.request and hasattr(self.request, "session"):
                session_key = self.request.session.session_key or ""

            has_voted = poll.has_voted(user, session_key)
 
            return render_to_string(
                "polls/poll.html",
                {
                    "poll": poll,
                    "user": user,
                    "has_voted": has_voted,
                    "request": self.request,
                    "require_login": poll.require_login
                },
                request=self.request,
            )

        self.content = PATTERNS["form"].sub(repl, self.content)

    # ------------------------------------------------------------------
    # Bloc : {{ top_list slug=... }}
    # ------------------------------------------------------------------
    def _render_top_lists(self):
        def repl(match):
            slug = match.group(1)
            try:
                from polls.models import Liste_Title, Choice_Liste_Title
                top = Liste_Title.objects.get(slug=slug)
            except Exception:
                return f'<div class="top-missing">Top « {slug} » introuvable.</div>'

            my_top = []
            user = self.request.user if self.request else None
            if user and user.is_authenticated:
                my_top = list(
                    Choice_Liste_Title.objects
                    .filter(user=user, liste=top)
                    .order_by("num_id")
                )

            # Complète avec des lignes vides si nécessaire
            if len(my_top) < top.num_choice_max:
                my_top = [
                    Choice_Liste_Title(suggestion="")
                    for _ in range(top.num_choice_max)
                ]

            return render_to_string(
                "polls/form_liste_title.html",
                {
                    "top": top,
                    "my_top": my_top,
                    "url": reverse("polls:valid-top"),
                    "user": user,
                    "article_blog": self.article,
                },
                request=self.request,
            )

        self.content = PATTERNS["top_list"].sub(repl, self.content)

    # ------------------------------------------------------------------
    # Bloc : {{ article=slug }}
    # ------------------------------------------------------------------
    def _render_articles(self):
        def repl(match):
            slug = match.group(1)

            # Anti-boucle
            if slug in self._seen_articles:
                return (
                    f'<div class="article-cycle">'
                    f'Cycle détecté : {slug}'
                    f'</div>'
                )
            self._seen_articles.add(slug)

            # 1. Chercher dans magazine/articles/
            path = Path(settings.BASE_DIR) / "magazine" / "articles" / f"{slug}.html"
            if path.exists():
                return path.read_text(encoding="utf-8")

            # 2. Fallback : générer depuis le modèle Magazine
            try:
                from magazine.models import Article as MagazineArticle
                from magazine.convert_ini import Template
                tpl = Template(slug, MagazineArticle)
                tpl.return_template()
                return f"<article>{tpl.article.template}</article>"
            except Exception as exc:
                return (
                    f'<div class="article-missing">'
                    f'Article « {slug} » introuvable ({exc}).'
                    f'</div>'
                )

        self.content = PATTERNS["article"].sub(repl, self.content)

    # ------------------------------------------------------------------
    # Bloc : {{ type=markdown }} / {{ type=html }}
    # ------------------------------------------------------------------
    def _apply_content_type(self):
        if PATTERNS["type_markdown"].search(self.content):
            self.content = PATTERNS["type_markdown"].sub("", self.content)
            self.content = markdown.markdown(
                self.content,
                extensions=["extra", "codehilite", "tables"],
            )
        elif PATTERNS["type_html"].search(self.content):
            self.content = PATTERNS["type_html"].sub("", self.content)
        # sinon : HTML brut, rien à faire