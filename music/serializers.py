from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from rest_framework import serializers
from music import models
from datetime import datetime
from rest_framework.exceptions import ValidationError
from django.db import IntegrityError

class BandSerializer(serializers.ModelSerializer):
    class Meta:
        model= models.Band
        fields= '__all__'

class TrackSerializer(serializers.ModelSerializer):
    class Meta:
        model= models.Track
        fields=  ('order', 'title', 'score')

class AddTrackSerializer(serializers.ModelSerializer):
    class Meta:
        model= models.Track
        fields= ('album', 'order', 'title', 'score')

    def create(self, validated_data):
        album = validated_data.pop('album')
        order = validated_data.pop('order')

        track = models.Track.objects.filter(album=album, order=order)

        if len(track) == 0:
            track = models.Track.objects.create(album=album, order=order, **validated_data)
        else:
            num = len(album.tracks.all()) + 1
            track = models.Track.objects.create(album=album, order=num, **validated_data)
        return track

class AlbumSerializer(serializers.ModelSerializer):
    band = BandSerializer()
    tracks = TrackSerializer(many=True)

    class Meta:
        model= models.Album
        fields= ('id', 'release_year', 'code', 'title', 'band', 'tracks', 'score')

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
            except:
                models.Track.objects.create(**track, album=album)
        return album

class ListeningHistorySerializer(serializers.Serializer):
    title = serializers.CharField(max_length=100)
    title_album = serializers.CharField(max_length=100)
    band = serializers.CharField(max_length=50)
    date = serializers.CharField()

    def create(self, validated_data):

        band_name = validated_data['band']
        band = models.Band.objects.get(name=band_name)

        title_album = validated_data['title_album']
        album = models.Album.objects.get(
            title=title_album,
            band=band)

        track_title = validated_data['title']
        track = models.Track.objects.get(
            title=track_title,
            album=album)

        date_str = validated_data['date']

        month_map = {
            "Jan": "janv.", "Feb": "févr.", "Mar": "mars",
            "Apr": "avr.", "May": "mai", "Jun": "juin",
            "Jul": "juil.", "Aug": "août", "Sep": "sept.",
            "Oct": "oct.", "Nov": "nov.", "Dec": "déc."
        }

        for en, fr in month_map.items():
            date_str = date_str.replace(fr, en)

        listening_date = datetime.strptime(date_str, "%d %b %Y, %H:%M")

        listening = models.Listening_History.objects.create(
            track=track,
            listening_date=listening_date
        )

        return listening