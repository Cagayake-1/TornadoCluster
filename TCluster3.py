import utils
import Constant
import csv
import os


# 多笔存取款对
def multiDWCouple(txDf, uList, deltaT, deltaT_dw):
    # 存款交易列表
    depositList = [[] for i in range(10)]
    # 取款交易列表
    withdrawList = [[] for i in range(10)]
    # 用户集合
    uClusterSet = set()
    while txDf.shape[0] >= 2:
        tx = txDf.iloc[0].to_dict()
        txDf = txDf.drop(txDf[txDf['hash'] == tx['hash']].index)
        if tx['type'] == 'Deposit':
            # 若为存款交易，存入存款交易列表
            num = 1
            while not txDf.empty:
                nextTx = txDf.iloc[0]
                if nextTx['type'] == 'Deposit' \
                        and (nextTx['timeStamp'] - tx['timeStamp']) < deltaT and nextTx['from'] == tx['from']:
                    tx = nextTx
                    txDf = txDf.drop(txDf[txDf['hash'] == tx['hash']].index)
                    num += 1
                else:
                    break
            if 2 <= num <= 10:
                # 将最后一笔存款交易存入对应长度的存款列表中保存
                depositList[num - 1].append(tx)
        if tx['type'] == 'Withdrawal':
            num = 1
            while not txDf.empty:
                nextTx = txDf.iloc[0]
                if nextTx['type'] == 'Withdrawal' and \
                        (nextTx['timeStamp'] - tx['timeStamp']) <= deltaT and nextTx['to'] == tx['to']:
                    tx = nextTx
                    txDf = txDf.drop(txDf[txDf['hash'] == tx['hash']].index)
                    num += 1
                else:
                    break
            if 2 <= num <= 10:
                txlist = depositList[num - 1]
                if len(txlist) > 0:
                    if (tx['timeStamp'] - txlist[len(txlist) - 1]['timeStamp']) <= num * deltaT_dw:
                        uClusterSet.add(depositList[num - 1].pop()['from'])
                        uClusterSet.add(tx['to'])
                        utils.clusterAppend(uList, uClusterSet)
                        uClusterSet = set()
                    else:
                        withdrawList[num - 1].append(tx)
    uSet = set()
    for i in range(len(uList)):
        for j in uList[i]:
            uSet.add(j)
    return len(uList), len(uSet)
