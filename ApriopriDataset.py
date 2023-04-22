import Constant
import utils
import os.path
import pandas as pd
from tqdm import tqdm
import Logging
import re
from AnonymSetNum import getOuterTxAppend
"""
        Log 信息处理

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
        if i == len(logs) - 1 or len(line.split('.csv')) == 1:
            wf.write(line + '\n')


#-------- 地址信息设置 ---------
addrSetFilePath = Constant.addressPath
outTxSetFilePath = Constant.addressOuterTxPath

values = Constant.values
for value in values:
    # value = '10000DAI'
    token = True
    type = ''.join(re.findall(r'[A-Za-z]', value))
    addrDir = ''
    if 'ETH' in value:
        token = False
        type = 'Normal'

value = '10000DAI'
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



"""
设计：

1. 初始化地址集合 addrDF DataFrame

2. 添加四个指标：GasPrice指标、交易金额指标、交易时间指标、交易活跃度指标
        
        GasPrice： 交易GasPrice/txCount（avg\mid\std）比较v
        
        Value：交易金额（avg\mid\std）比较v
        
        交易时间：活跃时区 计算账户最活跃的时刻（Hour)一标准时间v
        
        交易活跃度：交易时间间隔（inter（单位：sec））和交易数量（txCnt）

3. 查找相关交易

4. 混币中继器？

"""
file_list = os.listdir(outTxSetFilePath)
start = -1
# 读取断点位置
if len(logs) > 0 and logs[len(logs) - 1].split('_')[0] == value:
    if len(logs[len(logs) - 1].split('.csv')) == 2:
        start = int(logs[len(logs) - 1].split('_')[3])
begin = -1
read = []
# addrDF = addrDF.reindex(columns=addrDF.columns.tolist()+["NorGasPri_avg","NorGasPri_mid","NorGasPri_std","Value_avg","Value_mid","Value_std","Zone","Inter_avg","Inter_mid","Inter_std","Cnt","Activity"])
for i in tqdm(range(start+1, addrDF.shape[0])):
    addr = addrDF.index[i]
    txdf = pd.DataFrame()
    for j in range(begin+1, len(file_list)-1):
        file_dir = file_list[j]
        if len(file_dir.split('_'))>=2 and value in file_dir and type in file_dir.split('_')[1]:
            data = utils.readPklFile(outTxSetFilePath + file_dir)
            data = data.loc[(data['from'] == addr) | (data['to'] == addr)]
            if data.shape[0] == 0:
                continue
            else:
                addData = [txdf, data]
                txdf = pd.concat(addData)
                begin = j-1

    """
    -------------------------------------- 计算活跃度指标 ----------------------
    """
    # 交易量：
    if token:
        txCnt = addrDF.iloc[i,4]
    else:
        txCnt = addrDF.iloc[addr,2]
    addrDF.loc[addr,'Cnt'] = txCnt
    if txCnt == 0:
        continue
    elif txdf.empty:
        txdf = getOuterTxAppend(addr, type)
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

    """
    -------------------------------------- 计算活跃时刻 ----------------------
    """
    txdf['datetime'] = pd.to_datetime(txdf['timeStamp'],unit='s',utc=True)
    cnt = txdf.groupby(pd.Grouper(key='datetime',freq='H')).size().reset_index(name='count')
    cnt['datetime'] = cnt['datetime'].apply(lambda x: x.strftime('%H'))
    cnt['datetime'] = cnt['datetime'].astype(int)
    cnt = cnt.groupby(by=['datetime'])['count'].sum().reset_index()
    time = cnt[cnt['count']==cnt['count'].max()]['datetime'].values[0]
    addrDF.loc[addr,'Zone'] = time

    """
    -------------------------------------- 计算Gas Price指标 ----------------------
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
    # 归一化
    def calc(gasPrice, date, txNet):
        txnum = txNet.loc[txNet['date'] == date, 'txnum']
        return gasPrice / txnum.values[0]
    txdf['normalGasPrice'] = txdf.apply(lambda x: calc(x['gasPrice'],x['date'],txNet),axis=1)
    gavg = txdf.normalGasPrice.mean()
    gstd = txdf.normalGasPrice.std()
    gmid = txdf.normalGasPrice.median()
    addrDF.loc[addr,'NorGasPri_avg'] = gavg
    addrDF.loc[addr,'NorGasPri_mid'] = gstd
    addrDF.loc[addr,'NorGasPri_std'] = gmid

    """
    -------------------------------------- 计算交易金额指标 ----------------------
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

    utils.saveCsvFile(addrSetFilePath+addrDir, addrDF)
    
    logger.info(addrDir + '_' + str(i))

    
    