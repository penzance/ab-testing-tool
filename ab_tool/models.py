from django.db import models
from django.shortcuts import get_object_or_404
from ab_tool.exceptions import UNAUTHORIZED_ACCESS

class TimestampedModel(models.Model):
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    
    class Meta:
        abstract = True
    
    def update(self, **kwargs):
        """ Helper method to update objects """
        for k, v in kwargs.iteritems():
            setattr(self, k, v)
        self.save()


class CourseObject(TimestampedModel):
    course_id = models.CharField(max_length=128, db_index=True)
    
    class Meta:
        abstract = True
    
    @classmethod
    def get_or_404_check_course(cls, obj_id, course_id):
        """ Gets the object, raising a 404 if it does not exist and a 403
            if it doesn't match the passed course_id) """
        obj = get_object_or_404(cls, pk=obj_id)
        if obj.course_id != course_id:
            raise UNAUTHORIZED_ACCESS
        return obj


class Experiment(CourseObject):
    name = models.CharField(max_length=256)
    tracks_finalized = models.BooleanField(default=False)
    
    @classmethod
    def get_paceholder_course_track(cls, course_id):
        """ Gets or creates a single experiment for the course.  Placeholder
            method until interface supports multiple experiments.
            TODO: Remove once multiple experiments are supported """
        return Experiment.objects.get_or_create(course_id=course_id, name="Experiment 1")


class Track(CourseObject):
    name = models.CharField(max_length=256)
    notes = models.CharField(max_length=1024)
    experiment = models.ForeignKey(Experiment, related_name="tracks")


class InterventionPoint(CourseObject):
    """ This model stores the configuration of an intervention point"""
    name = models.CharField(max_length=256)
    notes = models.CharField(max_length=1024)
    experiment = models.ForeignKey(Experiment, related_name="intervention_points")
    tracks = models.ManyToManyField(Track, through='InterventionPointUrl')
    
    def is_missing_urls(self):
        if (Track.objects.filter(course_id=self.course_id).count()
            != self.tracks.count()):
            return True
        for intervention_point_url in InterventionPointUrl.objects.filter(intervention_point=self):
            if not intervention_point_url.url:
                return True
        return False

class InterventionPointUrl(TimestampedModel):
    """ This model stores the URL of a single intervention """
    url = models.URLField(max_length=2048)
    track = models.ForeignKey(Track)
    intervention_point = models.ForeignKey(InterventionPoint)
    open_as_tab = models.BooleanField(default=False)
    is_canvas_page = models.BooleanField(default=False)
    
    class Meta:
        unique_together = (('track', 'intervention_point'),)


class ExperimentStudent(TimestampedModel):
    """ This model stores which track a student is in for a given experiment
        within a given course.  A real-world can be represented by multiple
        ExperimentStudent objects, and will have a separate object for each 
        experiment they are in. """
    course_id = models.CharField(max_length=128, db_index=True)
    student_id = models.CharField(max_length=128, db_index=True)
    lis_person_sourcedid = models.CharField(max_length=128, db_index=True, null=True)
    experiment = models.ForeignKey(Experiment)
    track = models.ForeignKey(Track)
    
    class Meta:
        unique_together = (('experiment', 'student_id'),)
