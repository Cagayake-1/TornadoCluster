import os.path
from tqdm import tqdm
import pandas as pd
import TornadoCluster
import utils
import Constant
import csv


# 找到用户的所有交易
def findUserTx(uSet, txDf, dList, wList):
    txs = pd.DataFrame()
    # 找到所有用户地址参与的交易
    for address in uSet:
        txs = pd.concat([txs, txDf[(txDf['from'] == address) | (txDf['to'] == address)]])
    if txs.size == 0:
        # 若不存在，则返回递归
        return uSet, txDf, dList, wList
    else:
        # 若用户地址还有其他交易，找出
        for index, row in txs.iterrows():
            cp = pd.DataFrame()
            # 若为存款交易
            if row['type'] == 'deposit':
                # 找是否有符合条件的取款交易对
                cp = pd.concat([cp, txDf[(txDf['timeStamp'] >= row['timeStamp'])
                                         & (txDf['timeStamp'] <= (row['timeStamp'] + 180))
                                         & (txDf['type'] == 'withdraw')
                                         & (txDf['hash'] != row['hash'])]])
                if cp.size != 0:
                    for i, r in cp.iterrows():
                        uSet.add(r['to'])
                        txDf = txDf.drop(txDf[txDf['hash'] == r['hash']].index)
                else:
                    dList.append(row)
            # 若为取款交易
            elif row['type'] == 'withdraw':
                # 找是否有符合条件的存款交易对
                cp = pd.concat([cp, txDf[(txDf['timeStamp'] <= row['timeStamp'])
                                         & (txDf['timeStamp'] >= (row['timeStamp'] - 180))
                                         & (txDf['type'] == 'deposit')
                                         & (txDf['hash'] != row['hash'])]])
                if cp.size != 0:
                    for i, r in cp.iterrows():
                        uSet.add(r['from'])
                        txDf = txDf.drop(txDf[txDf['hash'] == r['hash']].index)
                else:
                    wList.append(row)
            txDf = txDf.drop(txDf[txDf['hash'] == row['hash']].index)
        return findUserTx(uSet, txDf, dList, wList)


# 单笔存取款对
def singleDWCouple(txDf, uList, t):
    # 存款交易列表
    depositList = []
    # 取款交易列表
    withdrawList = []
    # 用户集合
    uClusterSet = set()
    # 对于每个交易，判断是否为存取款交易模式对，
    # 如果是存取款交易模式对，加入用户集合
    length = txDf.shape[0]
    for idx in tqdm(range(length)):
        tx = txDf.iloc[idx].to_dict()
        if tx['type'] == 'Deposit':
            # 若为存款交易，存入存款交易列表
            depositList.append(tx)
        elif tx['type'] == 'Withdrawal':
            # 若为取款交易，判断和上一个存款交易列表的最后一个存款交易是否为单笔存取款交易对的混币交易模式，聚类规则1
            if len(depositList) > 0 and tx['timeStamp'] - depositList[len(depositList) - 1]['timeStamp'] <= t:
                uClusterSet.add(depositList.pop()['from'])
                uClusterSet.add(tx['to'])
                utils.clusterAppend(uList, uClusterSet)
                uClusterSet = set()
            else:
                withdrawList.append(tx)
    uSet = set()
    for i in range(len(uList)):
        for j in uList[i]:
            uSet.add(j)
    return len(uList), len(uSet)

