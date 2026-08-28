from django.db import models

class Singer(models.Model):
    name = models.CharField(max_length=200)
    source_url = models.URLField(max_length=500, blank=True)
    image = models.CharField(max_length=500, blank=True)
    song_count = models.CharField(max_length=100, blank=True)
    follower_count = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True)
    
    def __str__(self):
        return self.name
    

class Song(models.Model):
    name = models.CharField(max_length=200)
    singer = models.ForeignKey(
        Singer,
        on_delete=models.CASCADE,
        related_name='songs'
    )
    source_url = models.URLField(max_length=500, blank=True)
    image = models.CharField(max_length=500, blank=True)
    lyric = models.TextField(blank=True)
    
    def __str__(self):
        return self.name
    
    
class Comment(models.Model):
    song = models.ForeignKey(
        Song,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    session_key = models.CharField(max_length=40, blank=True, null=True)
    
    def __str__(self):
        return self.content[:30]
    