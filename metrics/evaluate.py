import IOU
import os
import json
import argparse
import numpy as np
import glob

def calculate(file_name, ground_truth_dir, predicted_dir):
    # print(f'{ground_truth_dir}/{file_name}.json')
    with open(f'{ground_truth_dir}/{file_name}.json', 'r', encoding="UTF-8") as file_1:
        ground_truth = json.load(file_1)
    # print(f'{predicted_dir}/{file_name}.json')
    with open(f'{predicted_dir}/{file_name}.json', 'r', encoding="UTF-8") as file_2:
        prediction = json.load(file_2)
    print(ground_truth)
    # print(prediction)
    print("===========")
    return IOU.calculate_iou(ground_truth, prediction)




if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--ground_truth', help='ground truth folder',
        default="./")
    parser.add_argument('--predicted', help='predicted folder',
        default="./")
    args = parser.parse_args()
    ground_truth_dir = args.ground_truth
    predicted_dir = args.predicted

    # print(ground_truth_dir)
    file_names = [x.split(os.sep)[-1][:-5] for x in glob.glob(f"{ground_truth_dir}/*.json")]
    for file_name in file_names:
        # print(file_names)
        # print(file_name)
        if file_name == "3130303230345f30":
            print(file_name)
            print(calculate(file_name, ground_truth_dir, predicted_dir))
        break
    