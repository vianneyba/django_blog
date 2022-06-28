from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from rest_framework import serializers, status
from rest_framework.response import Response
from music import models

class BandSerializer(serializers.ModelSerializer):
    class Meta:
        model= models.Band
        fields= '__all__'

class TrackSerializer(serializers.ModelSerializer):
    class Meta:
        model= models.Track
        fields=  ('order', 'title')


class AlbumSerializer(serializers.ModelSerializer):
    band = BandSerializer()
    tracks = TrackSerializer(many=True)

    class Meta:
        model= models.Album
        fields= ('id', 'release_year', 'code', 'title', 'band', 'tracks')

    def create(self, validated_data):
        name = validated_data.pop('band').get('name')
        tracks = validated_data.pop('tracks')
        try:
            band = models.Band.objects.get(name=name)
        except ObjectDoesNotExist:
            band = models.Band.objects.create(name=name)

        code = validated_data.pop('code')

        try:
            album = models.Album.objects.get(code=code)
        except ObjectDoesNotExist:
            album = models.Album.objects.create(**validated_data, code=code, band=band)

        for track in tracks:
            try:
                search_track = models.Track.objects.get(Q(title=track['title']), Q(album=album))
                print(search_track)
            except:
                models.Track.objects.create(**track, album=album)
        return album