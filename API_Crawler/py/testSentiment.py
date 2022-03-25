import unittest
from sentiment import Sentiment

class testSentiment(unittest.TestCase):

    def test_classify(self):
        result = Sentiment().classify("หิวข้าวจัง")
        self.assertEqual(result, "neg")

if __name__  == "__main__":
    unittest.main()