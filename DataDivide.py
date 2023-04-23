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
tctxFilePath = Constant.tornadoTxPath
values = Constant.values
resultPath = Constant.resultPath

def processZone(z, dfList, labels, index):
    for idx, df in enumerate(dfList):
        df = pd.DataFrame(df, columns=["Cnt","Zone"])
        df = df.loc[(df['Cnt'] != 0) & (df['Cnt'] != 1)]
        df = df.sort_values(by="Zone",ascending=False)
        df = df.drop_duplicates()
        df['zone_group'] = pd.cut(df.Zone,bins = z, labels=labels)
        groups = df.groupby(df.zone_group)
        for name, group in groups:
            if group.shape[0] > 1:
                index[idx].append(list(group.index.values))
    return index

def processVolume(act, dfList, labels, index):
    for idx, df in enumerate(dfList):
        df = pd.DataFrame(df, columns=["Cnt","Inter_avg","Zone","NorGasPri_avg","Value_avg"])
        df = df.loc[(df['Cnt'] != 0) & (df['Cnt'] != 1) & df['Inter_avg']!=0]
        df['activity'] = df['Cnt']/df['Inter_avg'].abs()
        df = df.sort_values(by="activity",ascending=False)
        df = df.drop_duplicates()
        df['activity_group'] = pd.cut(df.activity,bins = act, labels=labels)
        groups = df.groupby(df.activity_group)
        for _, group in groups:
            if group.shape[0] > 1:
                index[idx].append(list(group.index.values))
    return index

def processGas(bin, dfList, labels, index):
    for idx, df in enumerate(dfList):
        df = pd.DataFrame(df, columns=["Cnt","NorGasPri_avg"])
        df = df.loc[(df['Cnt'] != 0) & (df['Cnt'] != 1)]
        df = df.sort_values(by="NorGasPri_avg",ascending=False)
        df = df.drop_duplicates()
        df['norGasPrice_group'] = pd.cut(df.NorGasPri_avg,bins = bin, labels=labels)
        groups = df.groupby(df.norGasPrice_group)
        for _, group in groups:
            if group.shape[0] > 1:
                index[idx].append(list(group.index.values))
    return index

def processValue(bin, dfList, labels, index):
    for idx, df in enumerate(dfList):
        df = pd.DataFrame(df, columns=["Cnt","Value_avg"])
        df = df.loc[(df['Cnt'] != 0) & (df['Cnt'] != 1)]
        df = df.sort_values(by="Value_avg",ascending=False)
        df = df.drop_duplicates()
        df['value_group'] = pd.cut(df.Value_avg,bins = bin, labels=labels)
        groups = df.groupby(df.value_group)
        for name, group in groups:
            if group.shape[0] > 1:
                index[idx].append(list(group.index.values))
    return index

def processTxCnt(dfList, index):
    for idx, df in enumerate(dfList):
        df = pd.DataFrame(df, columns=["Cnt"])
        df0 = df.loc[(df['Cnt'] == 0)]
        df1 = df.loc[(df['Cnt'] == 1)]
        l0 = list(df0.index.values)
        l1 = list(df1.index.values)
        if len(l0) > 1:
            index[idx].append(l0)
        if len(l1) > 1:
            index[idx].append(l1)
    return index

def processRelayer(vdir, dfList, index):
    for idx, _ in enumerate(dfList):
        tctxdir = tctxFilePath +'CSV/'+ vdir[idx]+'_DATA.csv'
        tctxdf = utils.readCsvFile(tctxdir,0)
        ddf = tctxdf.loc[(tctxdf['type'] == 'Withdrawal')]
        groups = ddf.groupby(ddf.relayer)
        for name, group in groups:
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
        index = processVolume(bins, dfList, labels, index)
    if feature == 'zone':
        index = processZone(bins, dfList, labels, index)
    if feature == 'gasPrice':
        index = processGas(bins, dfList, labels, index)
    if feature == 'value':
        index = processValue(bins, dfList, labels, index)
    if feature == 'txCnt':
        index = processTxCnt(dfList, index)
    if feature == 'relayer':
        index = processRelayer(vdir, dfList, index)
    return index

def loadGasBins(value, binsnum):
    for addr_dir in os.listdir(addrSetFilePath):
        a = addr_dir.split('_')[0]
        if a == value:
            df = utils.readCsvFile(addrSetFilePath+addr_dir,0)
            break
    print(addrSetFilePath+addr_dir)
    print("addr len:",len(df))
    df = pd.DataFrame(df, columns=["Cnt","NorGasPri_avg"])
    df = df.loc[(df['Cnt'] != 0) & (df['Cnt'] != 1)]
    df = df.sort_values(by="NorGasPri_avg",ascending=False)
    df = df.drop_duplicates()
    print("addr len:",len(df))
    groups,bin_edges = pd.qcut(df.NorGasPri_avg,binsnum,retbins = True)
    pd.set_option('expand_frame_repr', False)
    bins = bin_edges.tolist()
    return bins

def loadActBins(value, binsnum):
    for addr_dir in os.listdir(addrSetFilePath):
        a = addr_dir.split('_')[0]
        if a == value:
            df = utils.readCsvFile(addrSetFilePath+addr_dir,0)
    print("addr len:",len(df))
    df = pd.DataFrame(df, columns=["Cnt","Inter_avg"])
    df = df.loc[(df['Cnt'] != 0) & (df['Cnt'] != 1) & df['Inter_avg']!=0]
    df['activity'] = df['Cnt']/df['Inter_avg'].abs()
    df = df.sort_values(by="activity",ascending=False)
    df = df.drop_duplicates()
    print("addr len:",len(df))
    groups,bin_edges = pd.qcut(df.activity,binsnum,retbins = True)
    pd.set_option('expand_frame_repr', False)
    bins = bin_edges.tolist()
    return bins

def loadValBins(value, binsnum):
    for addr_dir in os.listdir(addrSetFilePath):
        a = addr_dir.split('_')[0]
        if a == value:
            df = utils.readCsvFile(addrSetFilePath+addr_dir,0)
    print(len(df))
    df = pd.DataFrame(df, columns=["Cnt","Value_avg"])
    df = df.loc[(df['Cnt'] != 0) & (df['Cnt'] != 1)]
    df = df.sort_values(by="Value_avg",ascending=False)
    df = df.drop_duplicates()
    print(len(df))
    groups,bin_edges = pd.qcut(df.Value_avg,binsnum,retbins = True, duplicates='drop')
    pd.set_option('expand_frame_repr', False)
    bins = bin_edges.tolist()
    return bins

def loadAllData(type, value, binsnum):
    vdir = []
    for v in values:
        v_type = ''.join(re.findall(r'[A-Za-z]', v))
        if v_type == type:
            vdir.append(v)
        
    data = [0]*len(vdir)
        
    
    fe = 'txCnt'
    cnt_data = loadData(fe, vdir, [0,1,2])

    fe = 'zone'
    bins = Constant.ZoneBins
    zone_data = loadData(fe, vdir, bins)

    fe = 'relayer'
    relayer_data = loadData(fe, vdir)

    if type == 'ETH':
        vdir = [value]
        fe = 'activity'
        bins = loadActBins(value, binsnum)
        acti_data = loadData(fe, vdir, bins)

        fe = 'gasPrice'
        bins = loadGasBins(value, binsnum)
        gas_data = loadData(fe, vdir, bins)

        fe = 'value'
        bins = loadValBins(value, binsnum)
        value_data = loadData(fe,vdir, bins)

    else:
        fe = 'activity'
        bins = Constant.ActBins[type]
        acti_data = loadData(fe,vdir, bins)

        fe = 'gasPrice'
        bins = Constant.GasBins[type]
        gas_data = loadData(fe,vdir, bins)

        fe = 'value'
        bins = Constant.ValBins[type]
        value_data = loadData(fe,vdir, bins)

    for i,_ in enumerate(vdir):
        data[i] = acti_data[i] + zone_data[i] + gas_data[i] + value_data[i] +  relayer_data[i] + cnt_data[i]
        data[i] = list(filter(lambda x: x!=0, data[i]))

    return vdir, data

if __name__ == '__main__':
    type = 'ETH'
    cnt = 4
    topk = 2000
    suffix = type + '_' + str(topk) + '_' + str(cnt) 
   
    vdir, data = loadAllData(type)
    for i,v in enumerate(vdir):
        dataset  = data[i]
        print("|", str("Start " + str(v) + " Apriori").center(100),"|")
        L,suppData = Apriori.apriori(dataset,cnt)
        sortedFreqSet = Apriori.topK_apriori(L,suppData,topk)
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