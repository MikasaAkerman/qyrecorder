import unittest
import requests
from acfun import AcFun


class MyTestCase(unittest.TestCase):
    def setUp(self):
        self.session = requests.session()
        self.recorder = AcFun(self.session, "378269", "videos")

    def test_ac_fun(self):
        self.recorder.live_page()
        self.recorder.login()
        url = self.recorder.start_play()
        self.recorder.record(url)

        self.assertEqual(self.recorder.user_info.result, 0)


if __name__ == '__main__':
    unittest.main()
