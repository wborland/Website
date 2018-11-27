from tests import BaseTestCase 

import unittest as ut
import json


class UserTestCase(BaseTestCase):
    def test_true(self):
        self.assertTrue(True)

    def test_false(self):
        r = self.app.get('/')
        self.assertEqual(r.status_code, 200)