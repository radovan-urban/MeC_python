import cv2
import numpy as np

def grayConversion(image):
    grayValue = 0.07 * image[:,:,2] + 0.72 * image[:,:,1] + 0.21 * image[:,:,0]
    gray_img = grayValue.astype(np.uint8)
    return gray_img

orig = cv2.imread(r'beach.jpg', 1)
#orig = cv2.imread('beach.png')
cv2.imshow("Original", orig)

"""
g = grayConversion(orig)

cv2.imshow("Original", orig)
cv2.imshow("GrayScale", g)
"""

cv2.waitKey(0)
cv2.destroyAllWindows()


"""
gray_image = image.dot([0.07, 0.72, 0.21])
gray_image = np.min(gray_image, 255).astype(np.uint8)
"""
