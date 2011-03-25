"""
This file demonstrates two different styles of tests (one doctest and one
unittest). These will both pass when you run "manage.py test".

Replace these with more appropriate tests for your application.
"""

from django.test import TestCase

class SimpleTest(TestCase):
    def test_basic_addition(self):
        """
        Tests that 1 + 1 always equals 2.
        """
        self.failUnlessEqual(1 + 1, 2)


"""
Info for the tests:

    lund = '55.705, 13.200'
    lomma = '55.671, 13.063'
    malmo = '55.603, 12.986'
    kastrup = '55.634, 12.640'
    kopenhamn = '55.6931, 12.548'

    waypoints = [lund, kastrup, lomma, malmo, kopenhamn]
    
    response = google_TSP(waypoints)

should work


    lund = '55.705, 13.200'
    lomma = '55.671, 13.063'
    malmo = '55.603, 12.986'
    kastrup = '55.634, 12.640'
    kopenhamn = '55.6931, 12.548'

    waypoints = [lund, kastrup, lomma, malmo, kopenhamn, malmo, kopenhamn, kastrup, lomma, malmo, kopenhamn]
    
    response = google_TSP(waypoints)

max waypoints exeded
"""


__test__ = {"doctest": """
Another way to test that 1 + 1 is equal to 2.

>>> 1 + 1 == 2
True
"""}

