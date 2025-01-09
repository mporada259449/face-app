# import torch
import numpy as np
import cv2
from models import FACE_DETECTOR, FACE_LANDMARKER

# def get_device() -> str:
#     """
#     Automatically determine the best device to use ('cuda' if available, else 'cpu').
#     """
#     try:
#         return "cuda" if torch.cuda.is_available() else "cpu"
#     except ImportError:
#         return "cpu"
    
    
def align_face(image, landmarks):

    # Define key points
    # C_r = np.mean([landmarks[133], landmarks[33]], axis=0)  # Right eye center
    # C_l = np.mean([landmarks[362], landmarks[263]], axis=0)  # Left eye center
    C_r = landmarks[468] # Right eye center
    C_l = landmarks[473] # Left eye center
    N = landmarks[4]  # Nose tip
    M_l = landmarks[291]  # Left mouth corner
    M_r = landmarks[61]  # Right mouth corner

    # Source and target points
    src_pts = np.array([C_r, C_l, N, M_r, M_l], dtype=np.float32)
    dst_pts = np.array([(251, 272), (364, 272), (308, 336), (262, 402), (355, 402)], dtype=np.float32)

    # Compute affine transformation
    T_matrix, _ = cv2.estimateAffinePartial2D(src_pts, dst_pts, method=cv2.LMEDS)
    if T_matrix is None or np.isnan(T_matrix).any():
        raise ValueError("Failed to compute affine transformation matrix.")

    # Transform image
    aligned_image = cv2.warpAffine(image, T_matrix, (616, 616), borderValue=(0, 0, 0))

    # Transform landmarks
    homogeneous_landmarks = np.hstack([landmarks, np.ones((landmarks.shape[0], 1), dtype=np.float32)])
    transformed_landmarks = (homogeneous_landmarks @ T_matrix.T)[:, :2]

    return aligned_image, transformed_landmarks

def detect_align_crop_face(image):
    #PROPER
    landmarks = FACE_LANDMARKER.detect_landmarks(image)
    if landmarks is None or landmarks.size == 0 or np.any(landmarks == None):
        print("No valid landmarks detected!")
        exit()

    aligned_image, aligned_landmarks = align_face(image, landmarks)

    face_coords = FACE_DETECTOR.detect_face(aligned_image)
    if not face_coords:
        print("No face detected!")
        exit()

    aligned_facial_image = FACE_DETECTOR.crop_face(aligned_image, face_coords)

    # # Draw landmarks
    # for x, y in aligned_landmarks:
    #     cv2.circle(aligned_facial_image, (int(x), int(y)), 2, (0, 255, 0), -1)
    
    # # Display the result
    # facial_image = cv2.cvtColor(facial_image, cv2.COLOR_RGB2BGR)
    # cv2.imshow("Cropped Face with Landmarks", facial_image)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()

    return aligned_facial_image, aligned_landmarks

def detect_crop_align_face(image):
    face_coords = FACE_DETECTOR.detect_face(image)
    if not face_coords:
        print("No face detected!")
        exit()

    facial_image = FACE_DETECTOR.crop_face(image, face_coords)


    landmarks = FACE_LANDMARKER.detect_landmarks(facial_image)
    if landmarks is None or landmarks.size == 0 or np.any(landmarks == None):
        print("No valid landmarks detected!")
        exit()

    aligned_facial_image, aligned_landmarks = align_face(facial_image, landmarks)

    # # Draw landmarks
    # for x, y in aligned_landmarks:
    #     cv2.circle(aligned_facial_image, (int(x), int(y)), 2, (0, 255, 0), -1)

    # # Display the result
    # aligned_facial_image = cv2.cvtColor(aligned_facial_image, cv2.COLOR_RGB2BGR)
    # cv2.imshow("Cropped Face with Landmarks", aligned_facial_image)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()

    return aligned_facial_image, aligned_landmarks

def cosine_similarity(embedding1, embedding2):
    """
    Calculate cosine similarity between two embeddings.
    """
    embedding1 = np.squeeze(embedding1) 
    embedding2 = np.squeeze(embedding2)
    dot_product = np.dot(embedding1, embedding2)
    return  dot_product / (np.linalg.norm(embedding1) * np.linalg.norm(embedding2))