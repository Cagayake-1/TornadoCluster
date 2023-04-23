import Constant
import pandas as pd
from tqdm import tqdm
import utils
import os.path
import Logging


def countAnonymousSize(fileDir):
    anonymousAddrSet = set()
    for i, file_dir in enumerate(fileDir):
        df = utils.readDataFromCsv(file_dir)
        value = os.path.basename(file_dir).split('_')[0]
        anonymousSize, anonymousAddr = utils.anonymitySet(df, value)
        print("%s anonymous size: %d " % (file_dir, anonymousSize))
        anonymousAddrSet.update(anonymousAddr)
    print("All anonymous size:", len(anonymousAddrSet))


def addrSet(txDf, value):
    _, _, _, addrTx = utils.cntAnonymitySet(txDf, value)
    return addrTx


def getAllAddress():
    logFile = 'addressLog'
    logs = []
    if os.path.exists('./Logs/' + logFile + 'Info.txt'):
        with open('./Logs/' + logFile + 'Info.txt', "r") as rf:
            logs = rf.read().splitlines()
    logger = Logging.createLog(logFile)
    addrTx = pd.DataFrame()
    txCsvPath = tp + 'CSV/'
    for i, file_dir in enumerate(os.listdir(txCsvPath)):
        if file_dir in logs:
            continue
        df = utils.readDataFromCsv(txCsvPath + file_dir)
        value = os.path.basename(file_dir).split('_')[0]
        thisValueAddrTx = addrSet(df, value)
        thisValueAddrTx.to_csv(ap + value + "_Address_Statics.csv")
        addrTx = pd.concat([addrTx, thisValueAddrTx], sort=False)
        logger.info(file_dir)
    if "Address_Statics" not in logs:
        addrTx.to_csv(ap + "Address_Statics.csv")
        logger.info("Address_Statics")

def getOuterTxAppend(address, type):
    startblock = Constant.startBlock
    lastblock = startblock
    endblock = Constant.endBlock
    data = None
    page = 1
    offset = 5000
    newDataSize = 0
    if type == 'Normal':
        action = 'txlist'
        pre_url = 'http://api.etherscan.io/api?module=account&action=' + action
    
    else:
        action = 'tokentx'
        tokenAddr = Constant.ERC20TokenAddress.get(type)
        pre_url = 'http://api.etherscan.io/api?module=account&action=' + action + '&contractaddress=' + tokenAddr
    while True:
        if page * offset > 10000:
            startblock = lastblock
            page = 1
        url = pre_url + '&address=' + address + '&' \
            'startblock=' + startblock + '&endblock=' + endblock + '&' \
            'page=' + str(page) + '&offset=' + str(offset) + '&sort=asc&' \
            'apikey=' + Constant.apiKey
        result = utils.getApiText(url)
        if result['status'] == '1':
            newRes = pd.DataFrame(result['result'])
            for col in newRes.columns:
                newRes[col] = newRes[col].astype('category')
            if data is None:
                data = newRes
            else:
                frames = [data, newRes]
                data = pd.concat(frames)
                data = data.drop_duplicates(subset=['hash'], keep='last')
            lastblock = data.tail(1).iloc[0]['blockNumber']
            newDataSize += len(newRes)
            # crawl txlist > max capacity, save and get new directory
            # if data is not None and len(data) > ethPkl:
            #     utils.savePklFile(directory, data)
            #     utils.saveCsvFile(ap + file_dir, df)
            #     index += 1
            #     directory = otp + pkl_file + '_' + str(index) + '.pkl'
            #     logger.info(pkl_file + '_' + str(index))
            #     data = None
            if len(newRes) < offset:
                break
        # elif result['message'] == 'No transactions found':
        #     break
        page += 1
    return data
    
def getOuterTx(file_dir, pre_url, suffix, flag):
    value = os.path.basename(file_dir).split('_')[0]
    df = utils.readCsvFile(ap + file_dir, 0)
    print("|", str("Collect "+value+" "+suffix).center(50), "|")
    if flag not in df.columns.values:
        df[flag] = -1
    data = None
    if 'ETH' in value:
        logFile = 'getOuterTxLog'
        logs = []
        if os.path.exists('./Logs/'+logFile+'Info.txt'):
            with open('./Logs/' + logFile + 'Info.txt', "r") as rf:
                logs = rf.read().splitlines()
        logger = Logging.createLog(logFile)
        with open('./Logs/' + logFile + 'Info.txt', "w") as wf:
            for i, line in enumerate(logs):
                if i == len(logs) - 1 or len(line.split('_')) == 2:
                    wf.write(line + '\n')
        index = 0
        pkl_file = value + '_'  + suffix
        if len(logs) > 0 and logs[len(logs) - 1].split('_')[0] == value and logs[len(logs) - 1].split('_')[1] == suffix:
            if len(logs[len(logs)-1].split('_')) == 2:
                index = -1
            else:
                index = int(logs[len(logs) - 1].split('_')[2])
        if index >= 0:
            directory = otp + pkl_file + '_' + str(index) + '.pkl'
            data = utils.readPklFile(directory)
            # if data is not None and len(data) > ethPkl:
            #     index += 1
            #     directory = otp + pkl_file + '_' + str(index) + '.pkl'
            #     data = None
    else:
        directory = otp + value + '_' + suffix + '.pkl'
        data = utils.readPklFile(directory)
    search_df = df[df[flag] == -1]
    for cnt, address in enumerate(tqdm(search_df.index.values)):
        startblock = Constant.startBlock
        lastblock = startblock
        endblock = Constant.endBlock
        page = 1
        offset = 5000
        newDataSize = 0
        while True:
            if page * offset > 10000:
                startblock = lastblock
                page = 1
            url = pre_url + '&address=' + address + '&' \
                'startblock=' + startblock + '&endblock=' + endblock + '&' \
                'page=' + str(page) + '&offset=' + str(offset) + '&sort=asc&' \
                'apikey=' + Constant.apiKey
            result = utils.getApiText(url)
            if result['status'] == '1':
                newRes = pd.DataFrame(result['result'])
                for col in newRes.columns:
                    newRes[col] = newRes[col].astype('category')
                if data is None:
                    data = newRes
                else:
                    frames = [data, newRes]
                    data = pd.concat(frames)
                    data = data.drop_duplicates(subset=['hash'], keep='last')
                lastblock = data.tail(1).iloc[0]['blockNumber']
                newDataSize += len(newRes)
                # crawl txlist > max capacity, save and get new directory
                if data is not None and len(data) > ethPkl:
                    utils.savePklFile(directory, data)
                    utils.saveCsvFile(ap + file_dir, df)
                    index += 1
                    directory = otp + pkl_file + '_' + str(index) + '.pkl'
                    logger.info(pkl_file + '_' + str(index))
                    data = None
                if len(newRes) < offset:
                    break
            elif result['message'] == 'No transactions found':
                break
            page += 1
        df.loc[address, flag] = newDataSize
        # if data is not None and len(data) > ethPkl:
        #     utils.savePklFile(directory, data)
        #     utils.saveCsvFile(ap + file_dir, df)
        #     index += 1
        #     directory = otp + pkl_file + '_' + str(index) + '.pkl'
        #     logger.info(pkl_file + '_' + str(index))
        #     data = None
        if data is not None and cnt % 100 == 0:
            utils.savePklFile(directory, data)
            utils.saveCsvFile(ap + file_dir, df)
    if data is not None and search_df.shape[0] > 0:
        utils.savePklFile(directory, data)
        logger.info(pkl_file)
        utils.saveCsvFile(ap + file_dir, df)


def getAddressERC20Tx():
    action = 'tokentx'
    for i, file_dir in enumerate(os.listdir(ap)):
        if 'USDC' in file_dir:
            suffix = 'USDCTx'
            flag = 'USDCTxGot'
            tokenAddr = Constant.ERC20TokenAddress.get('USDC')
        elif 'USDT' in file_dir:
            suffix = 'USDTTx'
            flag = 'USDTTxGot'
            tokenAddr = Constant.ERC20TokenAddress.get('USDT')
        elif 'cDAI' in file_dir:
            suffix = 'cDAITx'
            flag = 'cDAITxGot'
            tokenAddr = Constant.ERC20TokenAddress.get('cDAI')
        elif 'DAI' in file_dir:
            suffix = 'DAITx'
            flag = 'DAITxGot'
            tokenAddr = Constant.ERC20TokenAddress.get('DAI')
        elif 'WBTC' in file_dir:
            suffix = 'WBTCTx'
            flag = 'WBTCTxGot'
            tokenAddr = Constant.ERC20TokenAddress.get('WBTC')
        else:
            continue
        url = 'http://api.etherscan.io/api?module=account&action=' + action + '&contractaddress=' + tokenAddr
        getOuterTx(file_dir, url, suffix, flag)


def getAddressTx():
    suffix = ["NormalTx", "InternalTx"]
    flag = ['txGot', 'inTxGot']
    action = ['txlist', 'txlistinternal']
    for i, file_dir in enumerate(os.listdir(ap)):
        for index in range(len(suffix)):
            if os.path.basename(file_dir).split('_')[0] == 'Address':
                continue
            url = 'http://api.etherscan.io/api?module=account&action=' + action[index]
            getOuterTx(file_dir, url, suffix[index], flag[index])


def dealPkl():
    for i, file_dir in enumerate(os.listdir(otp)):
        file_path = otp + file_dir
        if len(file_dir.split('_')) == 1:
            continue
        value = file_dir.split('_')[0]
        tx_type = file_dir.split('_')[1].split('.pkl')[0]
        os.rename(file_path, otp + tx_type + "_" + value + ".pkl")
        value = file_dir.split('_')[1].split('.pkl')[0]
        tx_type = file_dir.split('_')[0]
        if "ETH" not in value:
            if tx_type in ["NormalTx", "InternalTx"]:
                os.remove(file_path)


def pklToCsv():
    for i, file_dir in enumerate(os.listdir(otp)):
        file_path = otp + file_dir
        if len(file_dir.split('_')) == 1:
            continue
        value =  file_dir.split('_')[0]
        tx_type = file_dir.split('_')[1].split('.pkl')[0]
        suffix = '_OuterTokenTx.csv'
        tx_save_path = otp + 'CSV/' +value + suffix
        data = utils.readPklFile(file_path)
        # print(data.dtypes)
        if 'Normal' in tx_type or 'Internal' in tx_type:
            if 'ETH' in value:
                index = file_dir.split('_')[2].split('.pkl')[0]
                tx_save_path = otp + 'CSV/' + value + '_Outer'  + tx_type + '_' + index + '.csv'
            else:
                tx_save_path = otp + 'CSV/' + value + '_Outer' + tx_type.split('.pkl')[0] + '.csv'
        else:
            if('nonce' in data.keys()):
                del data['nonce']
            if('blockHash' in data.keys()):
                del data['blockHash']
            if('transactionIndex' in data.keys()):
                del data['transactionIndex']
            if('tokenName' in data.keys()):
                del data['tokenName']
            if('tokenSymbol' in data.keys()):
                del data['tokenSymbol']
            if('tokenDecimal' in data.keys()):
                del data['tokenDecimal']
            if('cumulativeGasUsed' in data.keys()):
                del data['cumulativeGasUsed']
            # del data['gasPrice']
            if('confirmations' in data.keys()):
                del data['confirmations']
        print('save file:' + file_path + ' to:' + tx_save_path)
        utils.saveCsvFile(tx_save_path, data)


def OuterTxSize():
    record_path = otp+'CSV/OutTxCountNew.xlsx'
    record_df = pd.DataFrame(columns=['Index', 'Value', 'Normal', 'Internal', 'Token'])
    # 设置索引
    # record_df = pd.DataFrame(record_df).set_index(['Index','Value'])
    for _, file_dir in enumerate(os.listdir(otp+'CSV/')):
        file_path = otp + 'CSV/' + file_dir
        if len(file_dir.split('_')) == 1:
            continue
        data = pd.read_csv(file_path, low_memory=False)
        length = len(data)
        print(file_dir + ": " + str(length))
        value = file_dir.split('_')[0]
        index = 0
        if len(file_dir.split('_')) == 3:
            index = int((file_dir.split('_')[2]).split('.csv')[0])
        if 'Normal' in file_dir:
            if record_df.loc[(record_df['Value']==value) & (record_df['Index']==index)].size != 0:
                record_df.loc[(record_df['Value']==value) & (record_df['Index']==index),'Normal'] = length
            else:
                new_record = {'Index':index, 'Value':value, 'Normal':length}
                df = [record_df,pd.DataFrame(new_record, index=[0])]
                record_df = pd.concat(df)
        elif 'Internal' in file_dir:
            if record_df.loc[(record_df['Value']==value) & (record_df['Index']==index)].size != 0:
                record_df.loc[(record_df['Value']==value) & (record_df['Index']==index),'Internal'] = length
                # record_df[record_df['Value'] == value & record_df['Index']==index]
                # record_df[record_df.Value == value & record_df.Index == index].Internal = length
            else:
                new_record = {'Index':index, 'Value':value, 'Internal':length}
                df = [record_df,pd.DataFrame(new_record, index=[0])]
                record_df = pd.concat(df)
        elif 'Token' in file_dir:
            if record_df.loc[(record_df['Value']==value) & (record_df['Index']==index)].size != 0:
                record_df.loc[(record_df['Value']==value) & (record_df['Index']==index),'Token'] = length
            else:
                new_record = {'Index':index, 'Value':value, 'Token':length}
                df = [record_df,pd.DataFrame(new_record, index=[0])]
                record_df = pd.concat(df)
        
    record_df.to_excel(record_path, index=False)

tp = Constant.tornadoTxPath
ap = Constant.addressPath
otp = Constant.addressOuterTxPath
ethPkl = Constant.pklFileCnt
if __name__ == '__main__':
    getAllAddress()
    getAddressTx()
    # getAddressERC20Tx()
    # pklToCsv()
    OuterTxSize()
