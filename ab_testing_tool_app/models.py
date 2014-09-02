from django.db import models

class Treatment(models.Model):
    name = models.CharField(max_length=512)
    notes = models.CharField(max_length=1000)
    course_id = models.CharField(max_length=12, db_index=True)
    treatment_url1 = models.CharField(max_length=512)
    treatment_url2 = models.CharField(max_length=512)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    def update(self, **kwargs):
        for k, v in kwargs.iteritems():
            setattr(self, k, v)
        self.save()