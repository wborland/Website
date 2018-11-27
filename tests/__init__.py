import os
import flaskapp
import unittest as ut
import json


class BaseTestCase(ut.TestCase):
    def setUp(self):
        self.app = flaskapp.app.test_client()
        self.app.testing = True


    def post(self, route, data, headers=None):
        if headers is not None:
            return self.app.post(route, data=json.dumps(data), 
                                 content_type='application/json', headers=headers)
        else:
            return self.app.post(route, data=json.dumps(data), content_type='application/json')


if __name__ == "__main__":
    ut.main()