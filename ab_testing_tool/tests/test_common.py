from ab_testing_tool.tests.common import SessionTestCase

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
