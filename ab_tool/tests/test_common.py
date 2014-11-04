from ab_tool.tests.common import SessionTestCase
from ab_tool.models import (Experiment, Track, TrackProbabilityWeight,
    InterventionPoint)

class ItemWithId(object):
    def __init__(self, _id):
        self.id = _id


class TestCommon(SessionTestCase):
    def test_same_ids_fails(self):
        """ Tests that two iterables with different ids fail the sameIds test """
        iter_1 = [ItemWithId(1), ItemWithId(2)]
        iter_2 = [ItemWithId(1)]
        self.assertRaises(Exception, self.assertSameIds, iter_1, iter_2)
    
    def test_same_ids_passes_with_empty_iterables(self):
        """ Tests that two empty iterables pass the sameIds test """
        iter_1 = []
        iter_2 = []
        self.assertSameIds(iter_1, iter_2)
    
    def test_same_ids_passes(self):
        """ Tests that two iterables with the same ids pass the sameIds test """
        iter_1 = [ItemWithId(1), ItemWithId(2)]
        iter_2 = [ItemWithId(1), ItemWithId(2)]
        self.assertSameIds(iter_1, iter_2)

    def test_same_ids_passes_unordered(self):
        """ Tests that two iterables with the same ids in different orders
            pass the sameIds test """
        iter_1 = [ItemWithId(1), ItemWithId(2)]
        iter_2 = [ItemWithId(2), ItemWithId(1)]
        self.assertSameIds(iter_1, iter_2)
    
    def test_same_ids_fails_with_duplicates(self):
        """ Test that an iterable with duplicate ids causes the sameIds test
            to fail (under the default duplicates_allowed=False) """
        iter_1 = [ItemWithId(1), ItemWithId(2)]
        iter_2 = [ItemWithId(1), ItemWithId(1), ItemWithId(2)]
        self.assertRaises(Exception, self.assertSameIds, iter_1, iter_2)
    
    def test_same_ids_passes_with_duplicates_and_flag(self):
        """ Tests that two iterables with the same ids, one containing
            duplicates, passes the sameIds test with duplicates_allowed=True """
        iter_1 = [ItemWithId(1), ItemWithId(2)]
        iter_2 = [ItemWithId(1), ItemWithId(1), ItemWithId(2)]
        self.assertSameIds(iter_1, iter_2, duplicates_allowed=True)
    
    def test_assert_raises_specific(self):
        """ Tests that the raisesSpecific test passes """
        message = "test exception message"
        def f():
            raise Exception(message)
        self.assertRaisesSpecific(Exception(message), f)
    
    def test_assert_raises_specific_fails_on_different_exception_message(self):
        """ Tests that raisesSpecific test fails on different exception messages """
        message1 = "test exception message 1"
        message2 = "test exception message 2"
        def f():
            raise Exception(message1)
        self.assertRaises(Exception, self.assertRaisesSpecific,
                          Exception(message2), f)
    
    def test_assert_raises_specific_fails_on_different_exception_type(self):
        """ Tests that raisesSpecific test fails on different exception classes """
        class OtherException(Exception):
            pass
        message = "test exception message"
        def f():
            raise Exception(message)
        self.assertRaises(Exception, self.assertRaisesSpecific,
                          OtherException(message), f)
    
    def test_assert_raises_specific_passes_on_child_with_same_message(self):
        """ Tests that raisesSpecific test passes if excpetion tested for is
            parent of the one raised and has the same message """
        class OtherException(Exception):
            pass
        message = "test exception message"
        def f():
            raise OtherException(message)
        self.assertRaisesSpecific(Exception(message), f)
    
    def test_assert_raises_specific_errors_on_non_deterministic(self):
        """ A non-deterministic function has odd behavior on assertRaisesSpecific
            if it raises an exception on its first run but not on its second.
            This tests that assertRaisesSpecific does error on this case.
            This test is fragile to changes in the implementation of
            UnitTest.assertRaises """
        self.do_raise = False
        message = "test exception message"
        def f(self):
            self.do_raise = not self.do_raise
            if self.do_raise:
                raise Exception(message)
        self.assertRaises(Exception, self.assertRaisesSpecific,
                          Exception(message), f, self)
    
    def test_create_test_experiment(self):
        """ Tests helper method via DB count """
        experiment_count = Experiment.objects.count()
        self.create_test_experiment()
        self.assertTrue(Experiment.objects.count() == experiment_count + 1)
    
    def test_create_test_track(self):
        """ Tests helper method via DB count """
        experiment_count = Experiment.objects.count()
        track_count = Track.objects.count()
        self.create_test_track()
        self.assertTrue(Experiment.objects.count() == experiment_count + 1)
        self.assertTrue(Track.objects.count() == track_count + 1)
    
    def test_create_test_track_weight(self):
        """ Tests helper method via DB count """
        experiment_count = Experiment.objects.count()
        track_count = Track.objects.count()
        weight_count = TrackProbabilityWeight.objects.count()
        self.create_test_track_weight()
        self.assertTrue(Experiment.objects.count() == experiment_count + 1)
        self.assertTrue(Track.objects.count() == track_count + 1)
        self.assertTrue(TrackProbabilityWeight.objects.count() == weight_count + 1)
    
    def test_create_test_intervention_point(self):
        """ Tests helper method via DB count """
        experiment_count = Experiment.objects.count()
        intervention_count = InterventionPoint.objects.count()
        self.create_test_intervention_point()
        self.assertTrue(Experiment.objects.count() == experiment_count + 1)
        self.assertTrue(InterventionPoint.objects.count() == intervention_count + 1)
