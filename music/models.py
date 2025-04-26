from django.db import models

class Band(models.Model):
	name = models.CharField(max_length=50)

	class Meta:
		verbose_name = "Groupe"
		ordering = ['name']

	def __str__(self):
		return self.name


class Album(models.Model):
	code = models.CharField(max_length=20)
	band = models.ForeignKey('Band', on_delete=models.CASCADE, related_name='band')
	title = models.CharField(max_length=100)
	release_year = models.IntegerField(null=True, blank=True)
	score = models.IntegerField(null=True, blank=True)

	class Meta:
		unique_together = ('code',)
		ordering= ('release_year',)

	def __str__(self):
		return f'{self.band.name} - {self.title} '


class Track(models.Model):
	album = models.ForeignKey(Album, related_name='tracks', on_delete=models.CASCADE)
	order = models.IntegerField()
	title = models.CharField(max_length=100)
	score = models.IntegerField(null=True, blank=True)

	class Meta:
		ordering= ('order',)
	
	def __str__(self):
		return f'{self.order} - {self.title}'

class Links_Review(models.Model):
	album = models.ForeignKey(Album, related_name='reviews', on_delete=models.CASCADE)
	link= models.URLField(max_length=128, db_index=True, unique=True)
	name= models.CharField(max_length=50, null=True, blank=True)

	def __str__(self):
		return f'{self.album.band.name} - {self.album.title} [{self.name}]'

class Listening_History(models.Model):
	track = models.ForeignKey(Track, related_name='listenings', on_delete=models.CASCADE)
	listening_date = models.DateTimeField()

	def __str__(self):
		date_str = self.listening_date.strftime("%d %b %Y, %H:%M")
		return f'{self.track.album.band.name} - {self.track.album.title} - {self.track.title} - {date_str}'