import cv2
import numpy as np

camera_x = 448
camera_y = 252


def get_silver_angle(box):
    box = box[box[:, 0].argsort()]

    left_points = box[:2]
    right_points = box[2:]

    left_points = left_points[left_points[:, 1].argsort()]
    right_points = right_points[right_points[:, 1].argsort()]

    vector = left_points[0] - right_points[0]
    angle = np.arccos(np.dot(vector, [1, 0]) / (np.linalg.norm(vector) * np.linalg.norm([1, 0]))) * 180 / np.pi
    angle = -angle if left_points[0][1] < right_points[0][1] else angle
    if angle == 180:
        angle = 0

    return left_points[0], right_points[0], angle


def main():
    cv2_img = cv2.imread('0030.png')
    silver_image = cv2.inRange(cv2_img, np.array([200, 200, 200]), np.array([255, 255, 255]))

    silver_first_row = silver_image[0, :].copy()
    white_pixel_index = np.where(silver_first_row == 255)[0]
    if len(white_pixel_index) > 0:
        first_white_pixel_index = white_pixel_index[0]
        last_white_pixel_index = white_pixel_index[-1]

        cv2.rectangle(silver_image, (first_white_pixel_index, 0), (last_white_pixel_index, camera_y), 0, -1)

    silver_last_row = silver_image[-1, :].copy()
    white_pixel_index = np.where(silver_last_row == 255)[0]
    if len(white_pixel_index) > 0:
        first_white_pixel_index = white_pixel_index[0]
        last_white_pixel_index = white_pixel_index[-1]

        cv2.rectangle(silver_image, (first_white_pixel_index, 0), (last_white_pixel_index, camera_y), 0, -1)

    cv2.rectangle(silver_image, (0, 0), (20, camera_y), 0, -1)
    cv2.rectangle(silver_image, (camera_x - 20, 0), (camera_x, camera_y), 0, -1)

    contours_silver, _ = cv2.findContours(silver_image, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)

    if len(contours_silver) > 0:
        largest_silver_contour = max(contours_silver, key=cv2.contourArea)
        cv2.drawContours(cv2_img, [np.int0(cv2.boxPoints(cv2.minAreaRect(largest_silver_contour)))], 0, (255, 255, 0), 2)
        p1, p2, angle = get_silver_angle(cv2.boxPoints(cv2.minAreaRect(largest_silver_contour)))
        if p1[1] < camera_y * 0.95 and p2[1] < camera_y * 0.95:
            cv2.line(cv2_img, (int(p1[0]), int(p1[1])), (int(p2[0]), int(p2[1])), (0, 255, 0), 2)

    cv2.imshow('Image', cv2_img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
