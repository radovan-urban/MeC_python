import numpy as np
import cv2
import time

print("Usage: press 'q' to quit.")
print("Prints frame-rate every 5 seconds.")

cap = cv2.VideoCapture(0)
start_time = time.time()
frame_counter=0
#print("Frame rate [frames/second]:  ", end="")
while(True):
    delta_time = time.time() - start_time
    #print(time.time())
    if (delta_time > 1):
        frate = frame_counter / delta_time
        print("Frame rate [frames/second]:  {:4.2f}  ".format(frate), end="")
        print("\r", end='')
        start_time = time.time()
        frame_counter = 0
    
    # Capture frame-by-frame
    ret, frame = cap.read()

    # Our operations on the frame come here
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Display the resulting frame
    cv2.imshow('frame',gray)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
    frame_counter += 1

# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()
