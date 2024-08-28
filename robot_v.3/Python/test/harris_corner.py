import cv2
import numpy as np


def main():
    camera_x = 448
    camera_y = 252
    black_min = np.array([0, 0, 0])
    kernal = np.ones((3, 3), np.uint8)

    black_max_normal_top = np.array([90, 90, 90])
    black_max_normal_bottom = np.array([135, 135, 135])

    img = cv2.imread('')

    green_min = np.array([58, 95, 39])
    green_max = np.array([98, 255, 255])
    green_image = cv2.inRange(img, green_min, green_max)

    black_image = cv2.inRange(img, black_min, black_max_normal_bottom)
    black_image[0:int(camera_y * .4), 0:camera_x] = cv2.inRange(img, black_min, black_max_normal_top)[0:int(camera_y * .4), 0:camera_x]

    black_image -= green_image
    black_image[black_image < 2] = 0

    black_image = cv2.erode(black_image, kernal, iterations=1)
    black_image = cv2.dilate(black_image, kernal, iterations=11)
    black_image = cv2.erode(black_image, kernal, iterations=9)

    contours = cv2.findContours(black_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours = contours[0] if len(contours) == 2 else contours[1]
    big_contour = max(contours, key=cv2.contourArea)

    mask = np.zeros_like(black_image)
    cv2.drawContours(mask, [big_contour], 0, 255, -1)

    result = black_image.copy()
    result[mask == 0] = 0

    corners = cv2.cornerHarris(result, 7, 5, 0.04)
    corners = cv2.dilate(corners, None)
    img[corners > 0.01 * corners.max()] = [255, 0, 0]

    cv2.imshow('Image', img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
