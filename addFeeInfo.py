import Constant
import os
import pandas as pd
import utils
from tqdm import tqdm
import Logging

logFile = 'addFeeLog'
logs = []
if os.path.exists('./Logs/' + logFile + 'Info.txt'):
    with open('./Logs/' + logFile + 'Info.txt', "r") as rf:
        logs = rf.read().splitlines()
logger = Logging.createLog(logFile)
with open('./Logs/' + logFile + 'Info.txt', "w") as wf:
    for i, line in enumerate(logs):
        if i == len(logs) - 1 or len(line.split('.csv')) == 2:
            wf.write(line + '\n')

def addFeeInfo():
    for file_dir in os.listdir(tp+'CSV/'):
        if file_dir in logs:
            continue
        value = file_dir.split('_')[0]
        suffix = '_DATA.csv'
        tx_save_path = tp + 'CSV/' + value + suffix
        txlist = pd.read_csv(tx_save_path).to_dict('records')
        begin = -1
        if len(logs)>0 and logs[len(logs)-1].split('_')[0]==value:
            begin = int(logs[len(logs) - 1].split('_')[2])
        for idx in tqdm(range(begin+1, len(txlist))):
            item = txlist[idx]
            if item['timeStamp']<Constant.LondonBlockTimeStamp:
                logger.info(file_dir.split('.csv')[0] + '_' + str(idx))
                continue
            elif 'maxFee' in item.keys() and pd.isna(item['maxFee'])==False:
                logger.info(file_dir.split('.csv')[0] + '_' + str(idx))
                continue
            else:
                tx_hash = item['hash']
                tx_url = 'http://api.etherscan.io/api?module=proxy&action=eth_getTransactionByHash&' \
                 'txhash=' + tx_hash + '&apikey=' + api
                result = utils.getApiText(tx_url)
                tx = result['result']
                if 'maxFeePerGas' in tx.keys():
                    item['maxFee'] = int(tx['maxFeePerGas'],16)
                if 'maxPriorityFeePerGas' in tx.keys():
                    item['maxPriorityFee'] = int(tx['maxPriorityFeePerGas'],16)
            txlist[idx] = item
            logger.info(file_dir.split('.csv')[0] + '_' + str(idx))
        pd.DataFrame(txlist).to_csv(tx_save_path, index=False)  
        logger.info(file_dir)

tp = Constant.tornadoTxPath
abi_path = Constant.abiPath
api = 'IHBZ6846ZQ8VNYJ6RF9MGIH771GZI1YAKZ'
if __name__ == '__main__':
    addFeeInfo()
