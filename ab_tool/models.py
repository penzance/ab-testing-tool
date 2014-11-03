from django.db import models
from django.shortcuts import get_object_or_404
from ab_tool.exceptions import (UNAUTHORIZED_ACCESS,
    EXPERIMENT_TRACKS_ALREADY_FINALIZED, TRACK_WEIGHTS_ERROR)

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
    UNIFORM_RANDOM = 1
    WEIGHTED_PROBABILITY_RANDOM = 2
    CSV_UPLOAD = 3
    REVERSE_API = 4
    
    ASSIGNMENT_ENUM_TYPES = (
        (UNIFORM_RANDOM, "uniform_random"),
        (WEIGHTED_PROBABILITY_RANDOM, "weighted_probability_random"),
        (CSV_UPLOAD, "csv_upload"),
        (REVERSE_API, "reverse_api"),
    )
    
    name = models.CharField(max_length=256)
    notes = models.CharField(max_length=1024)
    tracks_finalized = models.BooleanField(default=False)
    assignment_method = models.IntegerField(max_length=1, default=1,
                                            choices=ASSIGNMENT_ENUM_TYPES,)
    
    def assert_not_finalized(self):
        if self.tracks_finalized:
            raise EXPERIMENT_TRACKS_ALREADY_FINALIZED
    
    @classmethod
    def get_placeholder_course_experiment(cls, course_id):
        """ Gets or creates a single experiment for the course.  Placeholder
            method until interface supports multiple experiments.
            TODO: Remove once multiple experiments are supported """
        return Experiment.objects.get_or_create(course_id=course_id, name="Experiment 1")[0]

    def set_number_of_tracks(self, num):
        """ Sets number of tracks to num """
        current_num = self.tracks.count()
        if current_num == num:
            return
        if current_num < num:
            #add more tracks
            for i in range(current_num + 1, num + 1):
                Track.objects.create(name="Track %s" % i,
                                     course_id=self.course_id,
                                     track_number=i,
                                     experiment=self)
        if current_num > num:
            #delete tracks
            for i in range(num + 1, current_num + 1):
                Track.objects.filter(track_number=i, experiment=self).delete()
                #self.tracks[i].delete()
    
    def set_track_weights(self, weights_list):
        """ Sets TrackProbabilityWeights for tracks in weights_list """
        if len(weights_list) != self.tracks.count():
            raise TRACK_WEIGHTS_ERROR
        for i in range(1, len(weights_list) + 1):
            track = Track.objects.get(experiment=self, course_id=self.course_id, track_number=i)
            try:
                weighting_obj = TrackProbabilityWeight.objects.get(
                        track=track, course_id=self.course_id, experiment=self)
                weighting_obj.update(weighting=weights_list[i-1])
            except TrackProbabilityWeight.DoesNotExist:
                TrackProbabilityWeight.objects.create(
                    track=track, course_id=self.course_id, experiment=self,
                    weighting=weights_list[i-1])


class Track(CourseObject):
    track_number = models.IntegerField()
    name = models.CharField(max_length=256)
    notes = models.CharField(max_length=1024)
    experiment = models.ForeignKey(Experiment, related_name="tracks")
    
    class Meta:
        unique_together = (('experiment', 'track_number'),)


class TrackProbabilityWeight(CourseObject):
    #Definition: A `weighting` is an integer between 1 and 1000 inclusive
    weighting = models.IntegerField()
    track = models.ForeignKey(Track)
    experiment = models.ForeignKey(Experiment, related_name="track_probabilites")


class InterventionPoint(CourseObject):
    """ This model stores the configuration of an intervention point"""
    name = models.CharField(max_length=256)
    notes = models.CharField(max_length=1024)
    experiment = models.ForeignKey(Experiment, related_name="intervention_points")
    tracks = models.ManyToManyField(Track, through="InterventionPointUrl")
    
    def is_missing_urls(self):
        if (Track.objects.filter(course_id=self.course_id, experiment=self.experiment).count()
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


class ExperimentStudent(CourseObject):
    """ This model stores which track a student is in for a given experiment
        within a given course.  A real-world can be represented by multiple
        ExperimentStudent objects, and will have a separate object for each
        experiment they are in. """
    student_id = models.CharField(max_length=128, db_index=True)
    lis_person_sourcedid = models.CharField(max_length=128, db_index=True, null=True)
    experiment = models.ForeignKey(Experiment)
    track = models.ForeignKey(Track)
    
    class Meta:
        unique_together = (('experiment', 'student_id'),)


class InterventionPointDeployments(CourseObject):
    """ This model logs every time an intervention point is deployed for a
        student.  Consider moving this out of the database and into
        flat file storage. """
    student = models.ForeignKey(ExperimentStudent)
    intervention_point = models.ForeignKey(InterventionPoint)
