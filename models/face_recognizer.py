import os
import glob

import cv2
from tqdm import tqdm


COSINE_THRESHOLD = 0.5

class FaceRecognizer:
    def __init__(self, root):
        self.root = root
        WEIGHTS_DIR = os.path.join(root, "models\weights")
        DETECTOR_WEIGHTS = os.path.join(WEIGHTS_DIR, "yunet_s_640_640.onnx")
        self.detector = cv2.FaceDetectorYN_create(DETECTOR_WEIGHTS, "", (0, 0))
        RECOGNIZER_WEIGHTS = os.path.join(WEIGHTS_DIR, "face_recognizer_fast.onnx")
        self.recognizer = cv2.FaceRecognizerSF_create(RECOGNIZER_WEIGHTS, "")
        self.face_data = self.load_faces()

    def run(self, image):
        features, faces = self.get_face_feats(image)
        if faces is not None:
            for idx, (face, feature) in enumerate(zip(faces, features)):
                result, user = self.match(feature, self.face_data)
                box = list(map(int, face[:4]))
                color = (0, 255, 0) if result else (0, 0, 255)
                thickness = 2
                image = cv2.rectangle(image, box, color, thickness, cv2.LINE_AA)

                id_name, score = user if result else (f"unknown_{idx}", 0.0)
                text = "{0} ({1:.2f})".format(id_name, score)
                position = (box[0], box[1] - 10)
                font = cv2.FONT_HERSHEY_SIMPLEX
                scale = 0.6
                image = cv2.putText(image, text, position, font, scale,
                            color, thickness, cv2.LINE_AA)      
        return image

    def get_face_feats(self, image):
        _, faces = self.detect_faces(image)
        faces = [] if faces is None else faces
        features = []
        # rts = time.time()
        for face in faces:
            aligned_face = self.recognizer.alignCrop(image, face)
            feat = self.recognizer.feature(aligned_face)
            features.append(feat)
        
        return features, faces

    def match(self, feature_comp, face_data:dict):
        max_score = 0.0
        sim_user_id = ""
        for user_id, feature in zip(face_data.keys(), face_data.values()):
            score = self.recognizer.match(
                feature_comp, feature, cv2.FaceRecognizerSF_FR_COSINE)
            if score >= max_score:
                max_score = score
                sim_user_id = user_id
        if max_score < COSINE_THRESHOLD:
            return False, ("", 0.0)
        return True, (sim_user_id, max_score)
    
    def detect_faces(self, image):
        # dts = time.time()
        h, w, _ = image.shape
        self.detector.setInputSize((w, h))
        num_faces, faces = self.detector.detect(image)
        # print(f'time detection  = {time.time() - dts}')

        return num_faces, faces

    def load_faces(self, data_dir="images"):
        # Get registered photos and return as npy files
        # File name = id name, embeddings of a photo is the representative for the id
        # If many files have the same name, an average embedding is used
        dictionary = {}
        # the tuple of file types, please ADD MORE if you want
        types = ('*.jpg', '*.png')
        files = []
        for a_type in types:
            files.extend(glob.glob(os.path.join(self.root, data_dir, a_type)))

        files = list(set(files))
        for file in tqdm(files):
            image = cv2.imread(file)
            features, faces = self.get_face_feats(image)
            if faces is None:
                continue
            user_id = os.path.splitext(os.path.basename(file))[0]
            dictionary[user_id] = features[0]

        print(f'{len(dictionary)} faces loaded.')

        return dictionary
    
