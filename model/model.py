class FaceModel():
    def __init__(self):
        print("model initialization")

    def predict(self, img1 ,img2):
        print(f"prediction for images {img1} {img2}")
        return True

def load_model():
    face_model = FaceModel()
    return face_model