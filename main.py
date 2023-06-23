import cv2
import cvzone
import numpy as np
import requests

"""from matplotlib.pyplot import contour"""
from cvzone.ColorModule import ColorFinder

myColorFinder = ColorFinder(True)

cap = cv2.VideoCapture(0)
cap.set(3, 640)
cap.set(4, 480)

totalMoney = 0

myColorFinder = ColorFinder(False)

# golden
hsvVals = {'hmin': 16, 'smin': 14, 'vmin': 150, 'hmax': 179, 'smax': 202, 'vmax': 255}


def empty(a):
    pass


cv2.namedWindow("Settings")
cv2.resizeWindow("Settings", 640, 240)
cv2.createTrackbar("Threshold1", "Settings", 219, 255, empty)
cv2.createTrackbar("Threshold2", "Settings", 233, 255, empty)


def pre_process(img):
    img_pre = cv2.GaussianBlur(img, (5, 5), 3)
    thresh1 = cv2.getTrackbarPos("Threshold1", "Settings")
    thresh2 = cv2.getTrackbarPos("Threshold2", "Settings")

    img_pre = cv2.Canny(img_pre, thresh1, thresh2)
    kernel = np.ones((3, 3), np.uint8)
    img_pre = cv2.dilate(img_pre, kernel, iterations=1)
    img_pre = cv2.morphologyEx(img_pre, cv2.MORPH_CLOSE, kernel)

    return img_pre


while True:
    success, img = cap.read()
    img_pre = pre_process(img)
    imgContours, conFound = cvzone.findContours(img, img_pre, minArea=20)
    totalMoney = 0
    imgCount = np.zeros((480, 640, 3), np.uint8)
    if conFound:
        for count, contour in enumerate(conFound):
            peri = cv2.arcLength(contour['cnt'], True)
            approx = cv2.approxPolyDP(contour['cnt'], 0.02 * peri, True)
            if len(approx) > 5:
                # print(contour['area'])
                area = contour['area']
                x, y, w, h = contour['bbox']
                imgCrop = img[y:y + h, x:x + w]
                # cv2.imshow(str(count),imgCrop)
                imgColor, mask = myColorFinder.update(imgCrop, hsvVals)
                goldenPixelCount = cv2.countNonZero(mask)
                # print(goldenPixelCount)
                if area > 6500:
                    totalMoney += 0.50
                elif 4500 < area < 6500 and goldenPixelCount > 500:
                    totalMoney += 0.10
                elif 4500 < area < 6500:
                    totalMoney += 0.02
                else:
                    totalMoney += 0.01
    print(totalMoney)
    data = {
        'coinSum': totalMoney,
    }
    #Making an HTTP POST request to the Flask server
    response = requests.post('http://localhost:5000/update_coin_sum', json=data)
   
    # Check the response status
    if response.status_code == 200:
         print('Data sent successfully!')
    else:
         print('Error sending data:', response.text)
    cvzone.putTextRect(imgCount, f"{totalMoney} EURO", (100, 200), scale=10, offset=30, thickness=7)
    imgStacked = cvzone.stackImages([img, img_pre, imgContours, imgCount], 2, 1)

    cvzone.putTextRect(imgStacked, f"{totalMoney} EURO", (50, 50))
    # print(len(approx))
    cv2.imshow("Image Preprocess", imgStacked)
    # cv2.imshow("Image Color", imgColor)

    # cv2.imshow("Money Count", img)
    cv2.waitKey(1)
