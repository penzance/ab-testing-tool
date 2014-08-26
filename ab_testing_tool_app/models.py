from django.db import models

class CustomModel(models.Model):
    class Meta:
        abstract = True
    
    def update(self, **kwargs):
        """ Helper method to update objects """
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
    """ This model stores the configuration of an intervention point"""
    name = models.CharField(max_length=512)
    notes = models.CharField(max_length=1000)
    course_id = models.CharField(max_length=12, db_index=True)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)


class StageUrl(CustomModel):
    """ This model stores the URL of a single intervention """
    url = models.CharField(max_length=512)
    track = models.ForeignKey(Track)
    stage = models.ForeignKey(Stage)


class Student(CustomModel):
    """ This model stores which track a student is in for each course. """
    course_id = models.CharField(max_length=12, db_index=True)
    student_id = models.CharField(max_length=12)
    track = models.ForeignKey(Track)
    
    class Meta:
        unique_together = (('course_id', 'student_id'),)


class CourseSetting(CustomModel):
    """
    This model stores various settings about each course.  In order to ensure
    that this model exists whenever it is needed (since courses exist
    independently of this external tool), existence of this model for a course
    is checked (and corrected for) whenever it is requested.  Consequently,
    instances of this model are generated on-demand, and it is recommended that
    this model is only used through it's class methods.
    
    WARNING: DO NOT HAVE FOREIGN KEYS TO THIS MODEL.  THERE IS NO GUARANTEE
        IT WILL EXIST FOR A GIVEN COURSE.
    """
    course_id = models.CharField(max_length=12, db_index=True, unique=True)
    tracks_finalized = models.BooleanField(default=False)
    
    @classmethod
    def get_is_finalized(cls, course_id):
        course_setting, _ = CourseSetting.objects.get_or_create(course_id=course_id)
        return course_setting.tracks_finalized
    
    @classmethod
    def set_finalized(cls, course_id):
        course_setting, _ = CourseSetting.objects.get_or_create(
                course_id=course_id, defaults={"tracks_finalized": True})
        if not course_setting.tracks_finalized:
            course_setting.tracks_finalized = True
            course_setting.save()
