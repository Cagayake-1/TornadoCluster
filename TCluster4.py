import utils
import csv
import Constant
import os
from tqdm import tqdm

# relayer交易费为0
def fromToCouple(txDf, uList):
    uClusterSet = set()
    length = txDf.shape[0]
    for idx in tqdm(range(length)):
        tx = txDf.iloc[idx].to_dict()
        if tx['type'] == 'Withdrawal' and tx['from'] != tx['to'] and tx['from'] != tx['relayer']:
            if tx['fee'] == "0":
                uClusterSet.add(tx['from'])
                uClusterSet.add(tx['to'])
                utils.clusterAppend(uList, uClusterSet)
                uClusterSet = set()
    uSet = set()
    for i in range(len(uList)):
        for j in uList[i]:
            uSet.add(j)
    return len(uList), len(uSet)

