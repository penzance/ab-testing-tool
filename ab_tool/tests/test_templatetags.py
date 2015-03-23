from unittest import TestCase
from ab_tool.templatetags.util_tags import lookup_in


class ABToolTagsTest(TestCase):
    longMessage = True

    def test_lookup_in(self):
        """
        Correct value returned based on looking up key (param value) in dict object (param arg)
        """
        test_dict = {0: 'a', 1: 'b', 2: 'c'}
        lookup_key = 0
        res = lookup_in(lookup_key, test_dict)
        self.assertEqual(res, test_dict[lookup_key], 'Expected %s' % test_dict[lookup_key])
