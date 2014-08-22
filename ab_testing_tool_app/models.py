from django.db import models

class CustomModel(models.Model):
    
    def update(self, **kwargs):
        """Helper method to update objects"""
        for k, v in kwargs.iteritems():
            setattr(self, k, v)
        self.save()

class Track(CustomModel):
    name = models.CharField(max_length=512)
    notes = models.CharField(max_length=1000)
    course_id = models.CharField(max_length=12, db_index=True)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

class Stage(CustomModel):
    name = models.CharField(max_length=512)
    notes = models.CharField(max_length=1000)
    course_id = models.CharField(max_length=12, db_index=True)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

class StageUrl(CustomModel):
    url = models.CharField(max_length=512)
    track = models.ForeignKey(Track)
    stage = models.ForeignKey(Stage)
