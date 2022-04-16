import cv2

cap = cv2.VideoCapture(1)

# cap.set(cv2.CAP_PROP_FRAME_WIDTH,1920)
# cap.set(cv2.CAP_PROP_FRAME_HEIGHT,1080)

fourcc = cv2.VideoWriter_fourcc('X', 'V', 'I', 'D')
videoWriter = cv2.VideoWriter('C:/Users/User/PycharmProjects/NoamCamCodeFromGit/video.avi', fourcc, 20.0, (640, 480))


# Check if the webcam is opened correctly
if not cap.isOpened():
    raise IOError("Cannot open webcam")

while True:
    ret, frame = cap.read()
    frame = cv2.resize(frame, None, fx=1, fy=1, interpolation=cv2.INTER_AREA)
    if ret:
        cv2.imshow('Video', frame)
        videoWriter.write(frame)

    c = cv2.waitKey(1)
    if c == 27:
        break

cap.release()
videoWriter.release()
cv2.destroyAllWindows()
