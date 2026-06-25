"""torch-free constants for the currency CV, so the features-only path imports
cleanly without torch installed."""
IMG_SIZE = 128
CLASSES = ["genuine", "fake"]   # index 0 = genuine, 1 = fake/counterfeit
