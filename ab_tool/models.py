from django.db import models
from django.shortcuts import get_object_or_404
from ab_tool.exceptions import (UNAUTHORIZED_ACCESS,
    EXPERIMENT_TRACKS_ALREADY_FINALIZED)
import json
from django.core.urlresolvers import reverse


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
    
    def save_as_new_object(self, **kwargs):
        """ Saves a new object based on the original, applying updates in
            kwargs.  Note that this operates in-place; do not use this if
            other memory references to this object exist """
        for k, v in kwargs.iteritems():
            setattr(self, k, v)
        self.pk, self.id = None, None
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
    
    class Meta:
        unique_together = (('course_id', 'name'),)
    
    def assert_not_finalized(self):
        if self.tracks_finalized:
            raise EXPERIMENT_TRACKS_ALREADY_FINALIZED
    
    def new_track(self, track_name):
        return Track.objects.create(course_id=self.course_id, experiment=self,
                                    name=track_name)
    
    def to_json(self):
        """ Converts the experiment and its associated tracks to json,
            in the form expected by the editExperiment.html template and
            by experiment.js """
        experiment_dict = {
            "id": self.id,
            "name": self.name,
            "notes": self.notes,
            "uniformRandom": bool(self.assignment_method == self.UNIFORM_RANDOM),
            "tracks": [{"id": t.id, "weighting": t.get_weighting(), "name": t.name,
                        "deleteURL": reverse('ab_testing_tool_delete_track', args=(t.id,))}
                       for t in self.tracks.all()],
        }
        return json.dumps(experiment_dict)
    
    def copy(self, new_name):
        original_exp = Experiment.objects.get(pk=self.pk)
        # Copy Experiment
        self.save_as_new_object(name=new_name, tracks_finalized=False)
        
        # Copy Tracks
        track_id_mapping = {}
        for track in original_exp.tracks.all():
            original_track_id = track.id
            track.save_as_new_object(experiment=self)
            track_id_mapping[original_track_id] = track
            # Copy TrackProbabilityWeight, if any
            try:
                weight = TrackProbabilityWeight.objects.get(track_id=original_track_id)
                weight.save_as_new_object(track=track)
            except TrackProbabilityWeight.DoesNotExist:
                pass
        
        # Copy InterventionPoints
        for intervention_point in original_exp.intervention_points.all():
            orig_ip_id = intervention_point.id
            intervention_point.save_as_new_object(experiment=self)
            # Copy InterventionPointUrls, if any
            for ip_url in InterventionPointUrl.objects.filter(intervention_point_id=orig_ip_id):
                ip_url.save_as_new_object(track=track_id_mapping[ip_url.track.id],
                                          intervention_point=intervention_point)
    
    @classmethod
    def get_placeholder_course_experiment(cls, course_id):
        """ Gets or creates a single experiment for the course.  Placeholder
            method until interface supports multiple experiments.
            TODO: Remove once multiple experiments are supported """
        return Experiment.objects.get_or_create(course_id=course_id, name="Experiment 1")[0]


class Track(CourseObject):
    name = models.CharField(max_length=256)
    experiment = models.ForeignKey(Experiment, related_name="tracks")
    
    class Meta:
        unique_together = (('experiment', 'name'),)
    
    def set_weighting(self, new_weighting):
        if new_weighting is None:
            new_weighting = 0
        try:
            self.weight.update(weighting=new_weighting)
        except TrackProbabilityWeight.DoesNotExist:
            TrackProbabilityWeight.objects.create(
                    track=self, weighting=new_weighting,
                    experiment=self.experiment
        )
    
    def get_weighting(self):
        try:
            return self.weight.weighting
        except TrackProbabilityWeight.DoesNotExist:
            return None


class TrackProbabilityWeight(CourseObject):
    #Definition: A `weighting` is an integer between 1 and 1000 inclusive
    weighting = models.IntegerField()
    track = models.OneToOneField(Track, related_name="weight")
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
    
    class Meta:
        unique_together = (('experiment', 'name'),)
    
    def track_urls(self):
        """ This gets the InterventionPointUrls for an InterventionPoint in the
            default databse order of Tracks and uses a mock InterventionPointUrl
            with only the track attribute set in the event an InterventionPointUrl
            is missing for that track """
        ip_urls = self.interventionpointurl_set.all()
        track_urls = []
        for track in self.experiment.tracks.all():
            for ip_url in ip_urls:
                if ip_url.track == track:
                    track_urls.append(ip_url)
                    break
            else:
                track_urls.append(InterventionPointUrl(track=track))
        return track_urls


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
    experiment = models.ForeignKey(Experiment, related_name="students")
    track = models.ForeignKey(Track)
    
    class Meta:
        unique_together = (('experiment', 'student_id'),)


class InterventionPointInteraction(CourseObject):
    """ This model logs every time an intervention point is deployed for a
        student.  Consider moving this out of the database and into
        flat file storage. """
    student = models.ForeignKey(ExperimentStudent)
    intervention_point = models.ForeignKey(InterventionPoint)
    experiment = models.ForeignKey(Experiment, related_name="intervention_point_interactions")
