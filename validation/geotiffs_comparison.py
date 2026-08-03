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

    tifs1 = {f for f in os.listdir(dir1) if f.endswith(".tif")}
    tifs2 = {f for f in os.listdir(dir2) if f.endswith(".tif")}

    compared = 0
    for filename in sorted(tifs1 & tifs2):
        print(f"Comparing {filename}...")
        compare_images(os.path.join(dir1, filename), os.path.join(dir2, filename))
        compared += 1
        print("-" * 40)

    # Without this the script exits 0 when it compared nothing at all - an empty
    # download directory, a container that produced no output, a rename upstream.
    # A validation job that cannot fail is worse than no validation job.
    if compared == 0:
        raise SystemExit(
            f"No GeoTIFFs were compared. No .tif in {dir1} had a counterpart "
            f"in {dir2}; nothing was validated."
        )

    # Checked in BOTH directions on purpose. A real run showed the JavaScript
    # container exporting only 3 of 8 bands while Python exported all 8: the
    # unmatched files were the *extra* ones, so a one-directional check saw
    # nothing wrong and the job passed having validated well under half the
    # output. Whichever side comes up short, it went unvalidated.
    unmatched = []
    if tifs1 - tifs2:
        unmatched.append(f"only in {dir1}: {', '.join(sorted(tifs1 - tifs2))}")
    if tifs2 - tifs1:
        unmatched.append(f"only in {dir2}: {', '.join(sorted(tifs2 - tifs1))}")
    if unmatched:
        raise SystemExit(
            f"Compared {compared} band(s), but the two sides do not match, so "
            f"some output went unvalidated - " + "; ".join(unmatched)
        )

    print(f"OK: all {compared} band(s) present on both sides, pixel-identical.")
