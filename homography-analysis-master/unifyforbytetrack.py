import json
import numpy as np
import os
import cv2

# Input JSON files
JSON_FILES = {
    "filtered_left_intersections.json": "left",
    "left_non_intersections.json": "left",
    "filtered_right_intersections.json": "right",
    "right_non_intersections.json": "right"
}

# Homography matrices
HOMOGRAPHY_MATRIX_LEFT = "al2_homography_matrix.txt"
HOMOGRAPHY_MATRIX_RIGHT = "al1_homography_matrix.txt"

# Output JSON file
OUTPUT_JSON = "merged_output_with_transformed_center.json"


def load_homography_matrices():
    """
    Load homography matrices from file.
    """
    homography_matrix_left = np.loadtxt(HOMOGRAPHY_MATRIX_LEFT, delimiter=' ')
    homography_matrix_right = np.loadtxt(HOMOGRAPHY_MATRIX_RIGHT, delimiter=' ')
    return homography_matrix_left, homography_matrix_right


def transform_point(point, homography_matrix):
    """
    Transform a single point using a homography matrix.
    """
    point = np.array([[point]], dtype=np.float32)
    transformed_point = cv2.perspectiveTransform(point, homography_matrix)
    return transformed_point[0][0].tolist()  # Convert to a list for JSON compatibility


def merge_jsons(json_files, homography_matrix_left, homography_matrix_right):
    """
    Merge multiple JSON files, grouping objects by frame_index and adding a source field and transformed_center.
    """
    merged_data = {}

    for json_file, source in json_files.items():
        if not os.path.exists(json_file):
            print(f"Error: File '{json_file}' not found.")
            continue

        with open(json_file, "r") as f:
            data = json.load(f)

        for frame in data:
            frame_index = frame["frame_index"]
            objects = frame.get("objects", [])

            for obj in objects:
                # Add source field
                obj["source"] = source

                # Compute transformed center using the appropriate homography matrix
                homography_matrix = homography_matrix_left if source == "left" else homography_matrix_right
                obj["transformed_center"] = transform_point(obj["center"], homography_matrix)

            if frame_index not in merged_data:
                merged_data[frame_index] = {"frame_index": frame_index, "objects": []}

            # Append objects to the appropriate frame
            merged_data[frame_index]["objects"].extend(objects)

    # Convert merged_data to a list sorted by frame_index
    return sorted(merged_data.values(), key=lambda x: x["frame_index"])


def save_json(data, output_file):
    """
    Save the merged JSON data to a file.
    """
    with open(output_file, "w") as f:
        json.dump(data, f, indent=2)
    print(f"Merged JSON saved as '{output_file}'")


def main():
    # Load homography matrices
    homography_matrix_left, homography_matrix_right = load_homography_matrices()

    # Merge the JSON files
    merged_data = merge_jsons(JSON_FILES, homography_matrix_left, homography_matrix_right)

    # Save the merged data to a new JSON file
    save_json(merged_data, OUTPUT_JSON)


if __name__ == "__main__":
    main()