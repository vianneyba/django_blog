from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.utils.text import slugify

from blog.models import Article, Category, Tag
from blog.serializers import ArticleSerializer


class ArticlePushView(APIView):
    """Endpoint pour créer ou mettre à jour un article depuis l'admin local.

    POST /blog/api/articles/
    {
        "title": "...",
        "category": "...",
        "tags": ["...", "..."],
        "content": "<html>...</html>",
        "published": true
    }
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        data = request.data

        title = data.get("title", "").strip()
        if not title:
            return Response(
                {"title": ["Champ obligatoire."]},
                status=status.HTTP_400_BAD_REQUEST,
            )

        slug = slugify(title)

        # Récupère ou crée la catégorie
        category_name = data.get("category", "").strip()
        category = None
        if category_name:
            category, _ = Category.objects.get_or_create(name=category_name)

        # Crée ou met à jour l'article
        article, created = Article.objects.update_or_create(
            slug=slug,
            defaults={
                "title": title,
                "category": category,
                "author": request.user,
                "published": bool(data.get("published", False)),
            },
        )

        # Remplace les tags
        tag_names = data.get("tags", [])
        if tag_names:
            tags = [Tag.objects.get_or_create(name=name.strip())[0]
                    for name in tag_names if name.strip()]
            article.tags.set(tags)

        # Écrit le contenu HTML dans le fichier
        content = data.get("content", "")
        if content:
            article.save_content(content)

        serializer = ArticleSerializer(article)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )