import Constant
import utils
import re
import os.path
import pandas as pd
import numpy as np
import Apriori
import Logging
import csv

#-------- 地址信息设置 ---------
addrSetFilePath = Constant.addressPath
outTxSetFilePath = Constant.addressOuterTxPath
tctxFilePath = Constant.tornadoTxPath
values = Constant.values
resultPath = Constant.resultPath

def processZone(z, vdir, dfList, labels, index):
    logger.info("--------------- zone ---------------")
    for idx, df in enumerate(dfList):
        df = pd.DataFrame(df, columns=["Cnt","Zone"])
        df = df.loc[(df['Cnt'] != 0) & (df['Cnt'] != 1)]
        df = df.sort_values(by="Zone",ascending=False)
        df = df.drop_duplicates()
        logger.info(vdir[idx] + '-' + str(len(df)))
        df['zone_group'] = pd.cut(df.Zone,bins = z, labels=labels)
        groups = df.groupby(df.zone_group)
        for name, group in groups:
            logger.info(str(name) + '-' + str(len(group)))
            if group.shape[0] > 1:
                index[idx].append(list(group.index.values))
    return index

def processVolume(act, vdir, dfList, labels, index):
    logger.info("--------------- volume ---------------")
    for idx, df in enumerate(dfList):
        df = pd.DataFrame(df, columns=["Cnt","Inter_avg","Zone","NorGasPri_avg","Value_avg"])
        df = df.loc[(df['Cnt'] != 0) & (df['Cnt'] != 1) & df['Inter_avg']!=0]
        df['activity'] = df['Cnt']/df['Inter_avg'].abs()
        df = df.sort_values(by="activity",ascending=False)
        df = df.drop_duplicates()
        logger.info(vdir[idx] + '-' + str(len(df)))
        df['activity_group'] = pd.cut(df.activity,bins = act, labels=labels)
        groups = df.groupby(df.activity_group)
        for name, group in groups:
            logger.info(str(name) + '-' + str(len(group)))
            if group.shape[0] > 1:
                index[idx].append(list(group.index.values))
    return index

def processGas(bin, vdir, dfList, labels, index):
    logger.info("--------------- gasprice ---------------")
    for idx, df in enumerate(dfList):
        df = pd.DataFrame(df, columns=["Cnt","NorGasPri_avg"])
        df = df.loc[(df['Cnt'] != 0) & (df['Cnt'] != 1)]
        df = df.sort_values(by="NorGasPri_avg",ascending=False)
        df = df.drop_duplicates()
        logger.info(vdir[idx] + '-' + str(len(df)))
        df['norGasPrice_group'] = pd.cut(df.NorGasPri_avg,bins = bin, labels=labels)
        groups = df.groupby(df.norGasPrice_group)
        for name, group in groups:
            logger.info(str(name) + '-' + str(len(group)))
            if group.shape[0] > 1:
                index[idx].append(list(group.index.values))
    return index

def processValue(bin, vdir, dfList, labels, index):
    logger.info("--------------- value ---------------")
    for idx, df in enumerate(dfList):
        df = pd.DataFrame(df, columns=["Cnt","Value_avg"])
        df = df.loc[(df['Cnt'] != 0) & (df['Cnt'] != 1)]
        df = df.sort_values(by="Value_avg",ascending=False)
        df = df.drop_duplicates()
        logger.info(vdir[idx] + '-' + str(len(df)))
        df['value_group'] = pd.cut(df.Value_avg,bins = bin, labels=labels)
        groups = df.groupby(df.value_group)
        for name, group in groups:
            logger.info(str(name) + '-' + str(len(group)))
            if group.shape[0] > 1:
                index[idx].append(list(group.index.values))
    return index

def processTxCnt(dfList, index):
    logger.info("--------------- txcnt ---------------")
    for idx, df in enumerate(dfList):
        df = pd.DataFrame(df, columns=["Cnt"])
        df0 = df.loc[(df['Cnt'] == 0)]
        df1 = df.loc[(df['Cnt'] == 1)]
        l0 = list(df0.index.values)
        l1 = list(df1.index.values)
        logger.info(str(0) + '-' + str(len(l0)))
        logger.info(str(1) + '-' + str(len(l1)))
        if len(l0) > 1:
            index[idx].append(l0)
        if len(l1) > 1:
            index[idx].append(l1)
    return index

def processRelayer(vdir, dfList, index):
    logger.info("--------------- relayer ---------------")
    for idx, df in enumerate(dfList):
        tctxdir = tctxFilePath +'CSV/'+ vdir[idx]+'_DATA.csv'
        tctxdf = utils.readCsvFile(tctxdir,0)
        ddf = tctxdf.loc[(tctxdf['type'] == 'Withdrawal')]
        groups = ddf.groupby(ddf.relayer)
        for name, group in groups:
            logger.info(str(name) + '-' + str(len(group)))
            if group.shape[0] > 1:
                index[idx].append(list(group.to.values))
    return index

def loadData(feature, vdir, bins=[]):
    vlen = len(vdir)
    dfList = [pd.DataFrame()]*vlen
    for addr_dir in os.listdir(addrSetFilePath):
        a = addr_dir.split('_')[0]
        if a in vdir:
            i = vdir.index(a)
            df = utils.readCsvFile(addrSetFilePath+addr_dir,0)
            newdf = [dfList[i], df]
            dfList[i] = pd.concat(newdf)
    binlen = len(bins)-1
    index = [[] for _ in range(vlen)] 
    labels = np.arange(binlen)
    if feature == 'activity':
        index = processVolume(bins, vdir, dfList, labels, index)
    if feature == 'zone':
        index = processZone(bins, vdir, dfList, labels, index)
    if feature == 'gasPrice':
        index = processGas(bins, vdir, dfList, labels, index)
    if feature == 'value':
        index = processValue(bins, vdir, dfList, labels, index)
    if feature == 'txCnt':
        index = processTxCnt( dfList, index)
    if feature == 'relayer':
        index = processRelayer(vdir, dfList, index)
    return index


def loadAllData(type):
    vdir = []
    for value in values:
        v_type = ''.join(re.findall(r'[A-Za-z]', value))
        if v_type == type:
            vdir.append(value)
        
    data = [0]*len(vdir)
    
    fe = 'txCnt'
    cnt_data = loadData(fe, vdir, [0,1,2])

    feature = 'activity'
    bins = Constant.ActBins[type]
    acti_data = loadData(feature, vdir, bins)

    fe = 'zone'
    bins = Constant.ZoneBins
    zone_data = loadData(fe, vdir, bins)

    fe = 'gasPrice'
    bins = Constant.GasBins[type]
    gas_data = loadData(fe, vdir, bins)

    fe = 'value'
    bins = Constant.ValBins[type]
    value_data = loadData(fe, vdir, bins)

    fe = 'relayer'
    relayer_data = loadData(fe, vdir)


    for i,_ in enumerate(vdir):
        data[i] = acti_data[i] + zone_data[i] + gas_data[i] + value_data[i] +  relayer_data[i] + cnt_data[i]
        data[i] = list(filter(lambda x: x!=0, data[i]))

    return vdir, data



if __name__ == '__main__':
    
    types = ['cDAI']
    cnt = 3
    topk = 500

    """--------- Log 信息处理 -----------"""
    for type in types:
        
        suffix = type + '_' + str(topk) + '_' + str(cnt) 
        logFile = 'AprDataPreLog_' + suffix + '_Info.txt'
        logs = []

        # 如果不存在log文件则创建；存在则读取
        if os.path.exists('./Logs/' + logFile):
            with open('./Logs/' + logFile, "r") as rf:
                logs = rf.read().splitlines()
        logger = Logging.createLog(logFile)

        vdir, data = loadAllData(type)
        for i,v in enumerate(vdir):
            # print(v)
            dataset  = data[i]
            print("|", str("Start " + str(v) + " Apriori").center(100),"|")
            L,suppData = Apriori.apriori(dataset,cnt)
            sortedFreqSet = Apriori.topK_apriori(L,suppData,topk)
            logger.info("--------------- apriori ---------------")
            logger.info(L)
            sp = []
            for k,c in sortedFreqSet.items():
                item = []
                item.append(c)
                for addr in k:
                    item.append(addr)
                sp.append(item)
            suf = v + '_Top_' + str(topk) + '_' + str(cnt) 
            resFile = 'Apriori_' + suf + '.csv'
            with open(resultPath + resFile, 'a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                for row in sp:
                    writer.writerow(row)

