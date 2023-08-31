from time import sleep

import cv2
import cvzone
import serial
from cvzone.FaceMeshModule import FaceMeshDetector

ser = serial.Serial('COM3', 9600)  # Change the COM port to the one you are using

cap = cv2.VideoCapture(1)
detector = FaceMeshDetector(maxFaces=1)

# Get the total number of frames in the video
total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

idList = [22, 23, 24, 26, 110, 157, 158, 159, 160, 161, 130, 243]
ratioList = []
blinkCounter = 0
counter = 0
warningText = 0

while True:
    success, img = cap.read()
    img, faces = detector.findFaceMesh(img, draw=False)

    if faces:
        face = faces[0]
        for id in idList:
            lm = face[id]
            cv2.circle(img, lm, 2, (255, 0, 255), cv2.FILLED)

        leftUp = face[159]
        leftDown = face[23]
        leftLeft = face[130]
        leftRight = face[243]
        lengthVer, _ = detector.findDistance(leftUp, leftDown)
        lengthHor, _ = detector.findDistance(leftLeft, leftRight)
        cv2.line(img, leftUp, leftDown, (255, 0, 255), 3)
        cv2.line(img, leftLeft, leftRight, (255, 0, 255), 3)

        ratio = int((lengthVer / lengthHor) * 100)
        ratioList.append(ratio)
        if len(ratioList) > 3:
            ratioList.pop(0)
        ratioAvg = sum(ratioList) / len(ratioList)

        if ratioAvg < 38 and counter == 0:
            blinkCounter += 1
            counter = 1
            if blinkCounter > 5:
                print("sleep")  # Print "sleep" to the console
                ser.write(str("1").encode())

                blinkCounter = 0
                warningText = 1
        elif ratioAvg > 38 and counter == 0:
            blinkCounter = 0
            warningText = 0

        if counter != 0:
            counter += 1
            if counter > 10:
                counter = 0
        if warningText == 1:
            cv2.putText(img, "You Are Sleep", (10, 100), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 250), 2)
        else:
            text = 'You Are Awake '
            cv2.putText(img, text, (10, 100), cv2.FONT_HERSHEY_COMPLEX, 1, (100, 255, 0), 2)
        text = 'Sleep Timer: ' + str(blinkCounter)
        cv2.putText(img, text, (10, 50), cv2.FONT_HERSHEY_COMPLEX, 1, (200, 50, 10), 2)
        print(ratioAvg, blinkCounter)

    img = cv2.resize(img, (1280, 720))
    cv2.imshow("Image", img)

    if cv2.waitKey(25) == 27:
        break

    # Check if the video has looped and break the loop if needed
    if cap.get(cv2.CAP_PROP_POS_FRAMES) == total_frames:
        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)

cap.release()
cv2.destroyAllWindows()
