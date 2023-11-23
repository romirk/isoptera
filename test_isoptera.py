from unittest import TestCase

from isoptera import EXPANDING_FRAME, Isoptera


class TestIsoptera(TestCase):
    def test_step(self):
        iso = Isoptera(800, 800, EXPANDING_FRAME, 0, 2)
        o = iso.orientation
        p = iso.pos

        for i in range(20):
            iso.step()
            print(iso.orientation, iso.pos)
        self.fail()
