import os
import rasterio as rst
import numpy as np


def compare_images(img_path1, img_path2):
    with rst.open(img_path1) as src1, rst.open(img_path2) as src2:
        # Check and report size difference
        h1, w1 = src1.shape
        h2, w2 = src2.shape

        diff_h = abs(h1 - h2)
        diff_w = abs(w1 - w2)

        size_diff_percent = max(diff_h / max(h1, h2), diff_w / max(w1, w2)) * 100

        print(f"Size difference: {size_diff_percent:.2f}%")
        if size_diff_percent > 0.5:
            raise ValueError("Size difference exceeds threshold!")

        # Crop if necessary
        target_h = min(h1, h2)
        target_w = min(w1, w2)

        start_row_1 = h1 - target_h
        start_row_2 = h2 - target_h

        data1 = src1.read(
            1, window=rst.windows.Window(0, start_row_1, target_w, target_h)
        )
        data2 = src2.read(
            1, window=rst.windows.Window(0, start_row_2, target_w, target_h)
        )

        # Calculate the difference
        difference = data1 - data2

        # Calculate some statistics about the difference
        mean_diff = np.nanmean(difference)
        max_diff = np.nanmax(difference)
        min_diff = np.nanmin(difference)

        # Output the statistics
        print(f"Mean Difference: {mean_diff:.2f}")
        print(f"Max Difference: {max_diff:.2f}")
        print(f"Min Difference: {min_diff:.2f}")

        if mean_diff != 0:
            raise ValueError("Pixel value differences detected!")
        if max_diff != 0:
            raise ValueError("Pixel value differences detected!")
        if min_diff != 0:
            raise ValueError("Pixel value differences detected!")

        # Optionally, save the difference as a new GeoTIFF
        # output_path = "difference.tif"
        # with rst.open(output_path, 'w', driver='GTiff',
        #               height=difference.shape[0], width=difference.shape[1], count=1,
        #               dtype=difference.dtype, crs=src1.crs,
        #               transform=src1.transform) as dst:
        #     dst.write(difference, 1)
        # print(f"Difference saved to {output_path}")


if __name__ == "__main__":
    # img1_path = "./python_downloads/LST.tif"
    # img2_path = "./nodejs_downloads/LST.tif"
    # compare_images(img1_path, img2_path)

    dir1 = "./nodejs_downloads"
    dir2 = "./python_downloads"

    for d in (dir1, dir2):
        if not os.path.isdir(d):
            raise SystemExit(f"{d} does not exist - did the container run?")

    compared = 0
    skipped = []

    for filename in sorted(os.listdir(dir1)):
        if filename.endswith(".tif"):
            img1_path = os.path.join(dir1, filename)
            img2_path = os.path.join(dir2, filename)

            if os.path.exists(img2_path):
                print(f"Comparing {filename}...")
                compare_images(img1_path, img2_path)
                compared += 1
                print("-" * 40)
            else:
                skipped.append(filename)
                print(f"Warning: {filename} not found in {dir2}. Skipping comparison.")

    # Without this the script exits 0 when it compared nothing at all - an empty
    # download directory, a container that produced no output, a rename upstream.
    # A validation job that cannot fail is worse than no validation job.
    if compared == 0:
        raise SystemExit(
            f"No GeoTIFFs were compared. {dir1} contained no .tif with a "
            f"counterpart in {dir2}; nothing was validated."
        )

    if skipped:
        raise SystemExit(
            f"{len(skipped)} file(s) present in {dir1} had no counterpart in "
            f"{dir2} and went unchecked: {', '.join(skipped)}"
        )

    print(f"OK: {compared} GeoTIFF(s) compared, all pixel-identical.")
