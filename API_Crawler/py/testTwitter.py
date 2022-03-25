import unittest
from twitter import TwitterAPI

class testTwitter(unittest.TestCase):
    
    def test_cut_emoji(self):
        result = TwitterAPI().cut_emoji("Thats a 😆 😛")
        self.assertEqual(result, "Thats a  ")
    
    def test_clean_tag(self):
        result = TwitterAPI().clean_tag("random text #randomhashtag")
        self.assertEqual(result, "random text ")
    
    def test_texttool(self):
        result = TwitterAPI().texttool("@RKSAlberta Even Boris Johnson gets it. https://t.co/zckxPuK1t5")
        self.assertEqual(result, "RKSAlberta Even Boris Johnson gets it. ")
    
if __name__ == "__main__":
    unittest.main()