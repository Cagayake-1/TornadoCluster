import time
import pandas as pd
import csv
import Constant
import json
import requests
import os.path
from shutil import copyfile
from tqdm import tqdm


def timeCounter(func):
    def wrapper(*args, **kwargs):
        s = time.perf_counter()
        res = func(*args, **kwargs)
        e = time.perf_counter()
        print("\n|", str(func.__name__).center(50), "|", str((e - s) * 1000).center(50), "|")
        return res

    return wrapper


# @timeCounter
def getApiText(url):
    maxTryNum = 80
    for tries in range(maxTryNum):
        try:
            r = requests.get(url)
            result = json.loads(r.text)
            r.close()
            return result
        except Exception as e:
            if tries < (maxTryNum - 1):
                continue
            else:
                print("Has tried %d times to access url %s, all failed! Error msg:%s" % (maxTryNum, url, e))
                break


# @timeCounter
def readPklFile(filePath):
    if os.path.exists(filePath):
        data = pd.read_pickle(filePath)
        return data
    else:
        return None


# @timeCounter
def savePklFile(filePath, data):
    data.to_pickle(filePath)


# @timeCounter
def readCsvFile(filePath, indexCol):
    if os.path.exists(filePath):
        data = pd.read_csv(filePath, index_col=indexCol)
        return data
    else:
        return None


# @timeCounter
def copyFile(sourcePath, targetPath):
    copyfile(sourcePath, targetPath)


# @timeCounter
def saveCsvFile(filePath, data):
    data.to_csv(filePath)


# 将字典里的值全部换为小写
def toLower(dicts):
    new_dicts = {}
    for key, value in dicts.items():
        new_dicts[key] = value.lower()
    return new_dicts


def isAddrInUList(addrSet, uList):
    res_list = list()
    for index, user in enumerate(uList):
        if addrSet & user:
            res_list.append(index)
    return res_list


def clusterAppend(uList, uClusterSet):
    if len(uList) == 0:
        uList.append(uClusterSet)
    else:
        mergeIndexList = isAddrInUList(uClusterSet, uList)
        if len(mergeIndexList) == 0:
            uList.append(uClusterSet)
        else:
            newClusterSet = set()
            for index in mergeIndexList:
                newClusterSet = uList[index] | newClusterSet
            for index in reversed(mergeIndexList):
                del uList[index]
            newClusterSet = newClusterSet | uClusterSet
            uList.append(newClusterSet)


# 单面额的数据集的匿名集大小
def anonymitySet(txDf, value):
    uSet = set()
    print(value, "transaction set size:", str(txDf.shape[0]))
    for i in range(txDf.shape[0]):
        tx = txDf.iloc[i].to_dict()
        if tx["type"] == "deposit":
            addr = tx["from"]
            uSet.add(addr)
        if tx["type"] == "withdraw":
            addr = tx["to"]
            uSet.add(addr)
    return len(uSet), uSet


# 整个数据集的匿名集大小
def allAnonymitySet(fileDir):
    uSet = set()
    for i in range(len(fileDir)):
        data = pd.read_csv(fileDir[i])
        df = pd.DataFrame(data)
        df = df[['hash', 'from', 'to', 'value', 'type', 'timeStamp']]
        for j in range(df.shape[0]):
            tx = df.iloc[j]
            if tx["type"] == "deposit":
                uSet.add(tx["from"])
            if tx["type"] == "withdraw":
                uSet.add(tx["to"])
    print("anonymous set size:", str(len(uSet)))
    return len(uSet)


def cntAnonymitySet(txDf, value):
    addrTx = pd.DataFrame(columns=[value + '_Dep', value + '_Wit'])
    dCnt = 0
    wCnt = 0
    for i in tqdm(range(txDf.shape[0])):
        tx = txDf.iloc[i].to_dict()
        if tx["type"] == "Deposit":
            addr = tx["from"]
            dCnt += 1
            if addr in addrTx.index.values:
                addrTx.loc[addr, value+'_Dep'] += 1
            else:
                addrTx.loc[addr, value+'_Dep':value+'_Wit'] = [1, 0]
        if tx["type"] == "Withdrawal":
            addr = tx["to"]
            wCnt += 1
            if addr in addrTx.index.values:
                addrTx.loc[addr, value+'_Wit'] += 1
            else:
                addrTx.loc[addr, value+'_Dep':value+'_Wit'] = [0, 1]
    asCnt = addrTx.shape[0]
    print("{: ^100s}".format(value, "transaction set size:", str(txDf.shape[0])))
    print("{: ^100s}".format("Deposit Tx: %d, Withdraw Tx: %d " % (dCnt, wCnt)))
    print("{: ^100s}".format("Deposit and Withdraw set size:", asCnt))
    return dCnt,wCnt,asCnt, addrTx

# 对各面额的聚类集合进行聚合整合
def clusterMerge(clusterDir, rule):
    uSet = set()
    uList = []
    for cluster_dir in os.listdir(clusterDir):
        if len(cluster_dir.split('_')) == 2:
            result = cluster_dir.split('_')[1].split('.csv')[0]
            if result == rule:
                with open(clusterDir + cluster_dir, "r") as csvFile:
                    reader = csv.reader(csvFile)
                    for line in reader:
                        uClusterSet = set(line)
                        clusterAppend(uList, uClusterSet)
                        for address in line:
                            uSet.add(address)
    print("Clustered user size:" + str(len(uList)))
    print("Clustered address size:", str(len(uSet)))
    return uList


def readDataFromCsv(fileDir):
    data = pd.read_csv(fileDir, low_memory=False)
    pd.set_option('display.max_columns', None)
    df = pd.DataFrame(data)
    return df


def findSingleUserTx(user, txDf, dList, wList):
    # 找到所有用户地址参与的交易
    txs = txDf[(txDf['from'] == user) | (txDf['to'] == user)]
    if txs.size == 0:
        # 若不存在，则返回递归
        return txDf, dList, wList
    else:
        # 若用户地址还有其他交易，找出
        for index, row in txs.iterrows():
            # 若为存款交易
            if row['type'] == 'deposit':
                # 找是否有符合条件的取款交易对
                dList.append(row)
            # 若为取款交易
            elif row['type'] == 'withdraw':
                # 找是否有符合条件的存款交易对
                wList.append(row)
            txDf = txDf.drop(txDf[txDf['hash'] == row['hash']].index)
        return findSingleUserTx(user, txDf, dList, wList)


def findTime(fileDir):
    time = 0
    alltime = 0
    num = 0
    for i in range(len(fileDir)):
        data = pd.read_csv(fileDir[i])
        df = pd.DataFrame(data)
        df = df[['hash', 'from', 'to', 'value', 'type', 'timeStamp']]
        for j in range(df.shape[0]):
            tx = df.iloc[j]
            if j == 0:
                time = tx["timeStamp"]
            else:
                time = tx["timeStamp"] - time
                alltime = alltime + time
                time = tx["timeStamp"]
        n = df.shape[0] / 2
        num = num + n
    print("alltime:", str(alltime))
    print("time:", str(alltime / num))


# 去重地新增字典列表
def listDicAppend(original, new):
    for data in new:
        original.extend(filter(lambda d: d not in original, data))


def deleteDuplicate(dict_list):
    return [dict(t) for t in set([tuple(d.items()) for d in dict_list])]


if __name__ == '__main__':
    findTime(Constant.fileDir)
