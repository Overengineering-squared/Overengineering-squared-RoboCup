import os
import shutil
from itertools import combinations
from math import comb
from multiprocessing import Process

import cv2
from skimage.metrics import structural_similarity as ssim
from tqdm import tqdm


def compare_images(img1, img2):
    try:
        if img1.shape != img2.shape:
            img2 = cv2.resize(img2, (img1.shape[1], img1.shape[0]))

        return ssim(img1, img2)
    except Exception:
        return -1


def find_similar_images(target_dir, paths_to_check, images, num, tqdm_bar_name, position):
    similarity_threshold = .85

    progress_bar = tqdm(total=num, desc=tqdm_bar_name, ncols=70, position=position)

    similar_images = []

    update_counter = 0
    for img_path1, img_path2 in paths_to_check:
        similarity = compare_images(images[img_path1], images[img_path2])

        if similarity >= similarity_threshold:
            similar_images.append(img_path2)
        update_counter += 1
        if update_counter >= 100:
            update_counter = 0
            progress_bar.update(100)

    progress_bar.close()

    for img_path in similar_images:
        try:
            shutil.move(img_path, target_dir)
            print(f"Moved {img_path}")
        except Exception:
            print(f"Could not move {img_path}")
            continue


def get_image(img_path):
    img = cv2.imread(img_path)
    return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)


# This works but takes ages to run, ages as in multiple hours with 4 processes
# This moves the images that are too similar into a different directory to clear up the dataset
def main(num_processes):
    source_dir = r'C:\Users\Skillnoob_\Desktop\raw_silver_dataset\train\Line'
    target_dir = r'C:\Users\Skillnoob_\Desktop\raw_silver_dataset\duplicates\Line'

    image_paths = [os.path.join(source_dir, filename) for filename in os.listdir(source_dir) if filename.endswith(('.png', '.jpg', '.jpeg'))]
    images = {img_path: get_image(img_path) for img_path in image_paths}

    total_combinations = comb(len(image_paths), 2) // num_processes
    combs = list(combinations(image_paths, 2))

    divided_image_paths = [combs[i::num_processes] for i in range(num_processes)]

    processes = []

    for i in range(num_processes):
        process = Process(target=find_similar_images, args=(target_dir, divided_image_paths[i], images, total_combinations, f"Progress {i + 1}", i))
        processes.append(process)
        process.start()

    for process in processes:
        process.join()


if __name__ == "__main__":
    main(4)
