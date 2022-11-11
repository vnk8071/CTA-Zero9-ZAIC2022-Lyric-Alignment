import json
import argparse
import numpy as np

def calculate_iou(ground_truth, prediction):
    """
    Calculate iou for forced aligment
    
    Inputs:
    ground_truth: parsed json
    prediction: parsed json

    Returns:
    Mean iou over aligment segments
    """
    rs = 0
    print(prediction)
    print("========")
    print(ground_truth)
    G = np.ravel([l['l'] for l in ground_truth])
    P = np.ravel([l['l'] for l in prediction])

    for j in range(len(G)):
        iou_ = (intersection(j, G, P) + 1e-10) / (union(j, G, P) + 1e-10)
        rs += iou_
    return rs / len(G)

def intersection(j, G, P):
    ss = 0
    ee = 0
    try:
        ss = max(G[j]['s'], P[j]['s'])
        ee = min(G[j]['e'], P[j]['e'])
    finally:
        return ee - ss

def union(j, G, P):
    GG = G[j]["e"] - G[j]["s"]
    PP = P[j]["e"] - P[j]["s"]
    return GG + PP - intersection(j, G, P)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--ground_truth', help='ground truth file',
        default="./data_eval/mfa_train_output_json/3130303230345f30.json")
    parser.add_argument('--predicted', help='predicted file',
        default="./data_eval/train_labels/3130303230345f30.json")
    args = parser.parse_args()
    GROUND_TRUTH = args.ground_truth
    PREDICTED = args.predicted

    with open(f'{GROUND_TRUTH}', 'r', encoding="UTF-8") as f:
        GROUND_TRUTH = json.load(f)
    with open(f'{PREDICTED}', 'r', encoding="UTF-8") as f:
        PREDICTED = json.load(f)

    iou_ = calculate_iou(GROUND_TRUTH, PREDICTED)

    print(iou_)