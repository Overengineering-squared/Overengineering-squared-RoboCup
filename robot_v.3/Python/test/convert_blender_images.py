import os

import customtkinter as ctk
import cv2
import numpy as np
from PIL import Image

image_directory = r"C:\Users\Skillnoob_\Desktop\Overengineering-squared\Overengineering-squared\robot_v.3\Python\images"

image_hashmap = {}

yaw_range = np.arange(0, 360, 2)
pitch_range = np.arange(-30, 31, 2)

counter = 0

for pitch in pitch_range:
    for yaw in yaw_range:
        image_filename = f"{counter:04d}.png"
        print(yaw, pitch, image_filename)

        image_path = os.path.join(image_directory, image_filename)
        if os.path.exists(image_path):
            img = cv2.imread(image_path)
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            img_arr = Image.fromarray(img)
            img_ctks = ctk.CTkImage(img_arr, size=(200, 200))

            image_hashmap[(yaw, pitch)] = img_ctks

        counter += 1

for yaw in yaw_range:
    image_filename = f"{counter:04d}.png"

    image_path = os.path.join(image_directory, image_filename)
    if os.path.exists(image_path):
        img = cv2.imread(image_path)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img_arr = Image.fromarray(img)
        img_ctks = ctk.CTkImage(img_arr, size=(200, 200))

        image_hashmap[(yaw, 30)] = img_ctks

    counter += 1

np.savez_compressed("robot_model", image_hashmap=image_hashmap)
