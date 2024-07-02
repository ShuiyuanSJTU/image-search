import os
import sys
import time
from PIL import Image

# import imagehash
import cv2


def phash(hash, path: str):
    # return imagehash.phash(Image.open(path))
    # use cv2.img_hash to hash
    img = cv2.imread(path)
    if img is None:
        return None
    return hash.compute(img)


if __name__ == "__main__":
    # use the first param as the image file path
    # image_path = sys.argv[1]
    # image_path2 = sys.argv[2]
    # hash = imagehash.average_hash(Image.open(image_path))
    # hash2 = imagehash.average_hash(Image.open(image_path2))
    # print(hash)
    # print(hash2)

    # use the first param as the image directory path
    image_dir = sys.argv[1]

    # use the second param as the template image file path
    template_image_path = sys.argv[2]

    # get every image real file name in the directory
    files = os.listdir(image_dir)
    hash = cv2.img_hash_PHash.create()
    absoulte_files = [os.path.join(image_dir, f) for f in files]
    template_hash = phash(hash, template_image_path)
    print("Template image hash value: ", template_hash)
    img2hash = {}

    time_start = time.time()
    # get the hash value of the image in the directory
    for f in absoulte_files:
        hash_value = phash(hash, f)
        # print(f, hash_value)
        img2hash[f] = hash_value

    time_end = time.time()
    print("Time cost: ", time_end - time_start, "s")
    print("Avage time cost: ", (time_end - time_start) / len(absoulte_files), "s")

    print(
        "Compare the hash value of the template image with the images in the directory"
    )
    min_diff = 100
    similar_image = None
    time_start = time.time()
    for k, v in img2hash.items():
        if v is not None:
            diff = hash.compare(template_hash, v)
            if diff < min_diff and k != template_image_path:
                min_diff = diff
                similar_image = k
            # print(k, diff)
    time_end = time.time()
    print("The most similar image: ", similar_image)
    print("The difference value: ", min_diff)
    print("Time cost: ", time_end - time_start, "s")
    print("Avage time cost: ", (time_end - time_start) / len(absoulte_files), "s")

    min_diff_in_dir = 100
    threshold = 3.0
    same_image = {}
    similar_image = None
    similar_image2 = None
    time_start = time.time()
    for k, v in img2hash.items():
        if v is not None:
            for k2, v2 in img2hash.items():
                if k2 != k and v2 is not None and same_image.get(k2) != k:
                    diff = hash.compare(v, v2)
                    if diff <= threshold:
                        same_image[k] = k2
                    elif diff < min_diff_in_dir and k != k2:
                        min_diff_in_dir = diff
                        similar_image = k
                        similar_image2 = k2

    time_end = time.time()
    print("Time cost: ", time_end - time_start, "s")
    for k, v in same_image.items():
        print(f"{k} is the same as {v}")
    print("The most similar image in the directory: ", similar_image, similar_image2)
    print("The difference value: ", min_diff_in_dir)
