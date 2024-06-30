from nltk.metrics import distance

test_strings = [
    ("RV-5", "RV-4"),
    ("DG800S", "DG-800 S")
]

if __name__ == '__main__':
    print(distance.jaro_similarity("RV-5", "RV-4"))
    print(distance.jaro_similarity("DG800S", "DG-800S"))