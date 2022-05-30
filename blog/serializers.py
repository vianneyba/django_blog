from rest_framework import serializers
from blog.models import Article, Category, Tag

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['name', 'slug']

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['name', 'slug']

class ArticleSerializer(serializers.ModelSerializer):
    category = CategorySerializer()
    tags = TagSerializer(many=True)

    class Meta:
        model = Article
        fields = [
            'id', 'title', 'content', 'slug',
            'created_at', 'category', 'like_count',
            'dislike_count', 'tags']

class ArticleSaveSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = [
            'title', 'content', 'author', 'slug', 'category', 'tags']