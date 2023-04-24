import Constant
import utils
import os.path
import pandas as pd
from tqdm import tqdm
import Logging
import re
from AnonymSetNum import getOuterTxAppend
import numpy as np

pd.set_option('mode.chained_assignment', None)
"""
--------- Log 信息处理 -----------
"""
logFile = 'AprioriDataProcessLog'
logs = []
# 如果不存在log文件则创建；存在则读取
if os.path.exists('./Logs/' + logFile + 'Info.txt'):
    with open('./Logs/' + logFile + 'Info.txt', "r") as rf:
        logs = rf.read().splitlines()
logger = Logging.createLog(logFile)
with open('./Logs/' + logFile + 'Info.txt', "w") as wf:
    for i, line in enumerate(logs):
        # 保留必要信息：最后的断点位置、已完成的文件
        if i == len(logs) - 1 or len(line.split('.csv')) <= 1:
            wf.write(line + '\n')


#-------- 地址信息设置 ---------
addrSetFilePath = Constant.addressPath
outTxSetFilePath = Constant.addressOuterTxPath

values = Constant.values
values = ['0.1ETH', '1ETH', '10ETH', '100ETH']
 
@utils.timeCounter
def initPklTxlist(start, value, type, file_list):
    index = start
    txdf = pd.DataFrame()
    for file_dir in file_list:
        if len(file_dir.split('_'))>=2 and \
            value == file_dir.split('_')[0] and \
            type in file_dir.split('_')[1] and \
            index == int(file_dir.split('_')[2].split('.pkl')[0]):
            print("\n|", str("Read Pickle File: " + str(outTxSetFilePath + file_dir)).center(100),"|")
            data = utils.readPklFile(outTxSetFilePath + file_dir)
            addData = [txdf, data]
            txdf = pd.concat(addData)
            break
    return txdf

def calcFeature(addr, addrDF, txdf):
    """
    ---------------------- 计算活跃度指标 ----------------------
    """
    # 交易时间间隔
    txdf['timeStamp'] = txdf['timeStamp'].astype(int)
    txdf['inter'] = txdf['timeStamp'].shift(-1) - txdf['timeStamp']
    txInter = txdf.dropna(subset=['inter'])['inter']
    iavg = txInter.mean()
    imid = txInter.median()
    istd = txInter.std()
    
    addrDF.loc[addr,'Inter_avg'] = iavg
    addrDF.loc[addr,'Inter_mid'] = imid
    addrDF.loc[addr,'Inter_std'] = istd
    addrDF.loc[addr,'txCnt'] = txdf.shape[0]

    """
    ---------------------- 计算活跃时刻 ----------------------
    """
    txdf['datetime'] = pd.to_datetime(txdf['timeStamp'],unit='s',utc=True)
    cnt = txdf.groupby(pd.Grouper(key='datetime',freq='H')).size().reset_index(name='count')
    cnt['datetime'] = cnt['datetime'].apply(lambda x: x.strftime('%H'))
    cnt['datetime'] = cnt['datetime'].astype(int)
    cnt = cnt.groupby(by=['datetime'])['count'].sum().reset_index()
    time = cnt[cnt['count']==cnt['count'].max()]['datetime'].values[0]

    addrDF.loc[addr,'Zone'] = time

    """
    ---------------------- 计算Gas Price指标 ----------------------
    """
    # 交易手续费Gas Price单位（GWei）
    txdf['gasPrice'] = txdf['gasPrice'].str.slice(stop=-9) + '.' + txdf['gasPrice'].str.slice(start=-9)
    txdf.gasPrice = txdf.gasPrice.astype('float64')
    # 将timestamp转换成datatime
    txdf['date'] = pd.to_datetime(txdf['timeStamp'],unit='s', utc=True)
    txdf['date'] = txdf['date'].apply(lambda x: x.strftime('%d.%m.%Y'))
    # 网络交易数量
    txNet = pd.read_csv('Dataset/txPerSecond.tsv', sep='\t')
    txNet.columns=['date','txnum']
    txNet['date'] = txNet['date'].astype(str)
    txdf['date'] = txdf['date'].astype(str)
    # 归一化
    txdf = txdf.join(txNet.set_index('date'), on='date')
    txdf['normalGasPrice'] = txdf['gasPrice']/txdf['txnum']
    gavg = txdf.normalGasPrice.mean()
    gstd = txdf.normalGasPrice.std()
    gmid = txdf.normalGasPrice.median()

    addrDF.loc[addr,'NorGasPri_avg'] = gavg
    addrDF.loc[addr,'NorGasPri_mid'] = gstd
    addrDF.loc[addr,'NorGasPri_std'] = gmid

    """
    ---------------------- 计算交易金额指标 ----------------------
    """
    # 单位wei转换成ETH
    txdf['value'] = txdf['value'].str.slice(stop=-18) + '.' + txdf['value'].str.slice(start=-18)
    # 字符串类类型转换
    txdf.value = txdf.value.astype('float64')
    vavg = txdf.value.mean()    # 平均数
    vmid = txdf.value.median()  # 中位数
    vstd = txdf.value.std()     # 标准差

    addrDF.loc[addr,'Value_avg'] = vavg
    addrDF.loc[addr,'Value_mid'] = vmid
    addrDF.loc[addr,'Value_std'] = vstd

    return addrDF
    
def isCalc(value, addr, addrDF, addrDir):
    if 'Value_avg' in addrDF.columns.values and np.isnan(addrDF.loc[addr,'Cnt']) == False:
        return True
    oldPath = addrSetFilePath + value + '_Address_Statics_less.csv'
    if os.path.exists(oldPath):
        old = utils.readCsvFile(oldPath, 0)
        if addr in old.index.values and np.isnan(old.loc[addr,'Cnt']) == False:
            addrDF.loc[addr,'Inter_avg'] = old.loc[addr,'Inter_avg']
            addrDF.loc[addr,'Inter_mid'] = old.loc[addr,'Inter_mid']
            addrDF.loc[addr,'Inter_std'] = old.loc[addr,'Inter_std']
            addrDF.loc[addr,'txCnt'] = old.loc[addr,'txCnt']
            addrDF.loc[addr,'Cnt'] = old.loc[addr,'Cnt']
            addrDF.loc[addr,'Zone'] = old.loc[addr,'Zone']
            addrDF.loc[addr,'NorGasPri_avg'] = old.loc[addr,'NorGasPri_avg']
            addrDF.loc[addr,'NorGasPri_mid'] = old.loc[addr,'NorGasPri_mid']
            addrDF.loc[addr,'NorGasPri_std'] = old.loc[addr,'NorGasPri_std']
            addrDF.loc[addr,'Value_avg'] = old.loc[addr,'Value_avg']
            addrDF.loc[addr,'Value_mid'] = old.loc[addr,'Value_mid']
            addrDF.loc[addr,'Value_std'] = old.loc[addr,'Value_std']
            utils.saveCsvFile(addrSetFilePath + addrDir, addrDF)
            return True
    return False
    
    
def dealOutTxDf(value, type, addrDF, addrDir):
    file_list = os.listdir(outTxSetFilePath)
    start_a = -1
    start_t = 0
    # 读取断点位置
    if len(logs) > 0 and logs[len(logs) - 1].split('_')[0] == value:
        if len(logs[len(logs) - 1].split('.csv')) == 2:
            start_a = int(logs[len(logs) - 1].split('-')[1])
            start_t = int(logs[len(logs) - 1].split('-')[2])
    # ----------- 读取地址处理断点位置、外部文件读取位置 --- 结束 ------
    addrDF[~addrDF.index.duplicated(keep='first')]
    print(addrDF.shape[0])
    txdf = initPklTxlist(start_t, value, type, file_list)
    print("|", str("Start  addr:" + str(start_a+1) + " pkl:" + str(start_t)).center(50), "|", str("Calculate " + value + " ").center(50), "|")
    for i in tqdm(range(0, addrDF.shape[0])):
        if i < start_a+1:
            continue
        addr = addrDF.index[i]
        if isCalc(value, addr, addrDF, addrDir):
            continue
        addr_txdf = txdf.loc[(txdf['from'] == addr) | (txdf['to'] == addr)]
        # 交易量：
        if token:
            txCnt = addrDF.iloc[i,4]
        else:
            txCnt = addrDF.iloc[i,2]
        addrDF.loc[addr,'Cnt'] = txCnt
        if txCnt == 0:
            continue
        # 如果交易数不相等、并且txdf不为零，并且误差小于10 则输出一条信息
        elif txCnt != addr_txdf.shape[0] and addr_txdf.shape[0] !=0 and abs(txCnt - addr_txdf.shape[0]) <= 10:
            print("\n|", str("ATTENTION: " + str(addr) + " abs ( txCnt:" + str(txCnt) + " - txdf:" + str(addr_txdf.shape[0]) + " ) <= 10").center(100), "|")
        else:
            # txdf为零 或 误差大于10
            index = start_t + 1
            while addr_txdf.shape[0]==0 or (abs(txCnt - addr_txdf.shape[0])  > 10 and addr_txdf.shape[0] < txCnt):
                len_old= addr_txdf.shape[0]
                next_txdf = initPklTxlist(index, value, type, file_list)
                n_txdf = next_txdf.loc[(next_txdf['from'] == addr) | (next_txdf['to'] == addr)]
                addr_txdf = [addr_txdf, n_txdf]
                addr_txdf = pd.concat(addr_txdf)
                addr_txdf = addr_txdf.drop_duplicates(subset=['hash'], keep='last')
                len_new = addr_txdf.shape[0]
                if len_old - len_new == 0:
                    # addr_txdf = getOuterTxAppend(addr, type)
                    if abs(txCnt - addr_txdf.shape[0]) > 10:
                        print("\n|", str("ATTENTION: 数据对不上 " + str(addr) + " abs ( txCnt:" + str(txCnt) + " - txdf:" + str(addr_txdf.shape[0]) + " ) = " + str(txCnt - addr_txdf.shape[0])).center(100), "|")
                    break
                else:
                    index = index + 1
                    txdf = next_txdf
            start_t = index - 1
        print(value," len:", addrDF.shape[0])
        addrDF = calcFeature(addr, addrDF, addr_txdf)
        utils.saveCsvFile(addrSetFilePath + addrDir, addrDF)
        logger.info(addrDir + '-' + str(i) + '-' + str(start_t))
    logger.info(value)
    
    print(addrDF.shape[0])


if __name__ == '__main__':
    for value in values:
        if value in logs:
            continue
        token = True
        type = ''.join(re.findall(r'[A-Za-z]', value))
        addrDir = ''
        if 'ETH' in value:
            token = False
            type = 'Normal'
        # 对地址文件进行查询
        for addr_dir in os.listdir(addrSetFilePath):
            if addr_dir.split('_')[0] == value:
                addrDir = addr_dir
                addrDF = utils.readCsvFile(addrSetFilePath+addr_dir,0)
                break
        print(addrDF.shape[0])
        dealOutTxDf(value, type, addrDF, addrDir)