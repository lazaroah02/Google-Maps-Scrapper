#file to test the modules
import unittest
from get_mails_from_web import get_mails_from_web

results_expected = {
    "https://rred-duct.com":['info@rred-duct.com','keylidesigner@gmail.com'],
}

class TestGetMailsFromWeb(unittest.TestCase):
    
    def test_get_mails_from_web_results_expected(self):
        for key, value in results_expected.items():
            self.assertEqual(get_mails_from_web(key), value)

if __name__ == '__main__':
    unittest.main()            