from rest_framework import serializers, status
from magazine import models


class ParagraphSerializer(serializers.ModelSerializer):
    class Meta:
        model= models.Paragraph
        fields= '__all__'
        # extra_kwargs = {'title': {'required': False}} 


class OpinionSerializer(serializers.ModelSerializer):
    class Meta:
        model= models.Opinion
        fields= '__all__'


class LinkSerializer(serializers.ModelSerializer):
    class Meta:
        model= models.Link
        fields= '__all__'

class PhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model= models.PhotoArticle
        fields= '__all__'

class ScoreSerializer(serializers.ModelSerializer):
    class Meta:
        model= models.Score
        fields= '__all__'
        

class InsertSerializer(serializers.ModelSerializer):
    class Meta:
        model= models.Insert
        fields= '__all__'
        extra_kwargs = {'title': {'required': False}} 


class ArticleSerializer(serializers.ModelSerializer):
    inserts = InsertSerializer(many=True, required=False)
    scores = ScoreSerializer(many=True, required=False)
    photos = PhotoSerializer(many=True, required=False)
    links = LinkSerializer(many=True,required=False)
    opinions = OpinionSerializer(many=True, required=False)
    paragraphs = ParagraphSerializer(many=True, required=False)


    class Meta:
        model = models.Article
        fields = "__all__"
