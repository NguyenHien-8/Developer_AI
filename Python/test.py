import cv2

def test_camera_numbers(max_cameras=5):
    """Tests camera indices and returns the working ones."""
    working_cameras = []
    for i in range(max_cameras):
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            print(f"Camera {i} is working.")
            working_cameras.append(i)
            cap.release()
    return working_cameras

if __name__ == "__main__":
    print("Testing camera indices...")
    available_cameras = test_camera_numbers()
    if available_cameras:
        print("Available cameras:", available_cameras)
    else:
        print("No cameras found.")
