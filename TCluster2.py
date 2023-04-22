import utils
import csv
import Constant
import os
from tqdm import tqdm


# 多个单笔存取款对
def findSingleDWCouple(txDf, uList, t):
    txCouple = []
    multiTxCouple = []
    uClusterSet = set()
    # 如果之前已经有了两对，并且他们的存款地址和当前的存款地址都相同，那么可以不考虑时间
    # 否则，需要考虑时间
    while txDf.shape[0] > 2:
        # 取一对存取款的交易
        tx1 = txDf.iloc[0].to_dict()
        tx2 = txDf.iloc[1].to_dict()
        txDf = txDf.drop(txDf[txDf['hash'] == tx1['hash']].index)
        if tx1['type'] == 'Deposit' and tx2['type'] == 'Withdrawal':
            # 找到一对存取款对
            if len(multiTxCouple) > 0 and (multiTxCouple[len(multiTxCouple) - 1][0]['from'] != tx1['from']) and (
                    multiTxCouple[len(multiTxCouple) - 1][1]['to'] != tx2['to']):
                # 和已有的存取款对不一样
                if len(multiTxCouple) > 1:
                    # 已有的存取款对数目大于1，则把所有存取款对的用户地址加入同一类
                    for cp in multiTxCouple:
                        uClusterSet.add(cp[0]['from'])
                        uClusterSet.add(cp[1]['to'])
                    utils.clusterAppend(uList, uClusterSet)
                    uClusterSet = set()
                multiTxCouple = []
            elif len(multiTxCouple) == 0:
                txCouple.append(tx1)
                txCouple.append(tx2)
                txDf = txDf.drop(txDf[txDf['hash'] == tx2['hash']].index)
                multiTxCouple.append(txCouple)
                txCouple = []
            elif multiTxCouple[len(multiTxCouple) - 1][0]['from'] == tx1['from']:
                if multiTxCouple[len(multiTxCouple) - 1][1]['to'] == tx2['to']:
                    txCouple.append(tx1)
                    txCouple.append(tx2)
                    txDf = txDf.drop(txDf[txDf['hash'] == tx2['hash']].index)
                    multiTxCouple.append(txCouple)
                    txCouple = []
                elif (multiTxCouple[len(multiTxCouple) - 1][1]['timeStamp'] -
                      multiTxCouple[len(multiTxCouple) - 1][0]['timeStamp']) <= t and (
                        tx2['timeStamp'] - tx1['timeStamp']) <= t:
                    txCouple.append(tx1)
                    txCouple.append(tx2)
                    txDf = txDf.drop(txDf[txDf['hash'] == tx2['hash']].index)
                    multiTxCouple.append(txCouple)
                    txCouple = []
            elif multiTxCouple[len(multiTxCouple) - 1][1]['to'] == tx2['to']:
                if (multiTxCouple[len(multiTxCouple) - 1][1]['timeStamp'] -
                    multiTxCouple[len(multiTxCouple) - 1][0]['timeStamp']) <= t and (
                        tx1['timeStamp'] - multiTxCouple[len(multiTxCouple) - 1][1]['timeStamp']) <= t:
                    txCouple.append(tx1)
                    txCouple.append(tx2)
                    txDf = txDf.drop(txDf[txDf['hash'] == tx2['hash']].index)
                    multiTxCouple.append(txCouple)
                    txCouple = []
    uSet = set()
    for i in range(len(uList)):
        for j in uList[i]:
            uSet.add(j)
    return len(uList), len(uSet)

