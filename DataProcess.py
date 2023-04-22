import datetime
import json
import os
import pandas as pd
from web3_input_decoder import decode_constructor, decode_function, exceptions
from eth_log.models.contract import Contract
from tqdm import tqdm
import Constant
import utils
import Logging

logFile = 'tornadoTxLog'
logs = []
if os.path.exists('./Logs/' + logFile + 'Info.txt'):
    with open('./Logs/' + logFile + 'Info.txt', "r") as rf:
        logs = rf.read().splitlines()
logger = Logging.createLog(logFile)
with open('./Logs/' + logFile + 'Info.txt', "w") as wf:
    for i, line in enumerate(logs):
        if i == len(logs) - 1 or len(line.split('.json')) == 2:
            wf.write(line + '\n')


def processData():
    for file_dir in os.listdir(tp):
        if file_dir in logs or len(file_dir.split('_')) <= 1:
            continue
        value = file_dir.split('_')[0]
        tx_type = file_dir.split('_')[1]
        suffix = '_DATA.csv'
        tx_save_path = tp + 'CSV/' + value + suffix
        with open(tp + file_dir, 'r', encoding='utf-8') as f:
            tx_data = json.load(f)
        if os.path.exists(tx_save_path):
            decode_txlist = pd.read_csv(tx_save_path).to_dict('records')
        else:
            decode_txlist = []
        begin = -1
        if len(logs) > 0 and logs[len(logs) - 1].split('_')[0] == value and logs[len(logs) - 1].split('_')[1] in tx_type and len(logs[len(logs) - 1].split('.json')) == 1:
            begin = int(logs[len(logs) - 1].split('_')[2])
        if 'Normal' in tx_type:
            decode_txlist = processNormalTx(decode_txlist, file_dir, tx_data, value, begin, tx_save_path)
        else:
            decode_txlist = processInternalTx(decode_txlist, file_dir, tx_data, value, begin, tx_save_path)
        txlist = utils.deleteDuplicate(decode_txlist)
        print("{: ^100s}".format("%s, txlist size:%d" % (file_dir, len(txlist))))
        if len(txlist) > 0:
            txlist = pd.DataFrame(txlist)
            txlist['timeStamp'] = txlist['timeStamp'].astype(int)
            txlist = txlist.sort_values(by='timeStamp', ascending=True)
            txlist.to_csv(tx_save_path, index=False)
        logger.info(file_dir)


def processNormalTx(txlist, file_dir, tx, value, begin, save_path):
    contract_abi_path = abi_path + value + '_ABI.json'
    with open(contract_abi_path, 'r') as f:
        file = f.read()
        contract_abi = json.loads(json.loads(file))
    for idx in tqdm(range(begin+1, len(tx))):
        item = tx[idx]
        if item['isError'] == '1':
            logger.info(file_dir.split('.json')[0] + '_' + str(idx))
            continue
        decode_tx = dict()
        decode_tx['contractValue'] = value
        decode_tx['hash'] = item['hash']
        decode_tx['timeStamp'] = item['timeStamp']
        decode_tx['dateTime'] = datetime.datetime.utcfromtimestamp(int(item['timeStamp']))
        decode_tx['dateTime'] = pd.to_datetime(decode_tx['dateTime'])
        decode_tx['nonce'] = item['nonce']
        decode_tx['type'] = 'Others'
        decode_tx['from'] = item['from']
        decode_tx['to'] = item['to']
        decode_tx['relayer'] = 'None'
        decode_tx['proxy'] = 'None'
        decode_tx['fee'] = 'None'
        try:
            decode_constructor(contract_abi, item['input'])
        except:
            try:
                tx_input = decode_function(contract_abi, item['input'])
            except:
                # 对少部分无法解析的input单独处理
                pass
            else:
                if len(tx_input) == 1 and tx_input[0][1] == '_commitment':
                    decode_tx['type'] = 'Deposit'
                elif len(tx_input) == 7 and tx_input[0][1] == '_proof':
                    decode_tx['type'] = 'Withdrawal'
                    decode_tx['to'] = tx_input[3][2]
                    decode_tx['relayer'] = tx_input[4][2]
                    decode_tx['fee'] = tx_input[5][2]
                else:
                    pass
        else:
            decode_tx['type'] = 'Create'
            decode_tx['to'] = item['contractAddress']
        decode_tx['gasLimit'] = item['gas']
        decode_tx['gasPrice'] = item['gasPrice']
        decode_tx['gasUsed'] = item['gasUsed']
        txlist.append(decode_tx)
        pd.DataFrame(txlist).to_csv(save_path, index=False)
        logger.info(file_dir.split('.json')[0] + '_' + str(idx))
    return txlist


def processInternalTx(txlist, file_dir, tx, value, begin, save_path):
    for idx in tqdm(range(begin+1, len(tx))):
        item = tx[idx]
        if 'isError' in item and item['isError'] == '1':
            logger.info(file_dir.split('.json')[0] + '_' + str(idx))
            continue
        tx_hash = item['hash']
        tx_url = 'http://api.etherscan.io/api?module=proxy&action=eth_getTransactionByHash&' \
                 'txhash=' + tx_hash + '&apikey=' + api
        result = utils.getApiText(tx_url)
        normal_tx = result['result']
        if normal_tx['to'] == Constant.contractAddr.get(value).lower():
            logger.info(file_dir.split('.json')[0] + '_' + str(idx))
            continue
        elif normal_tx['to'] == Constant.contractAddr.get('Proxy').lower():
            decode_tx = decodeProxyTx(value, normal_tx, item, 'Proxy')
        elif normal_tx['to'] == Constant.contractAddr.get('OldProxy').lower():
            decode_tx = decodeProxyTx(value, normal_tx, item, 'OldProxy')
        else:
            decode_tx = decodeOtherTx(value, normal_tx, item)
        for decode_tx_item in decode_tx:
            if len(txlist) == 0 or txlist[len(txlist) - 1]['hash'] != decode_tx_item['hash']:
                txlist.extend(decode_tx)
        pd.DataFrame(txlist).to_csv(save_path, index=False)
        logger.info(file_dir.split('.json')[0] + '_' + str(idx))
    return txlist


def decodeProxyTx(value, normal_tx, internal_tx, proxy):
    tx_hash = normal_tx['hash']
    url = 'http://api.etherscan.io/api?module=proxy&action=eth_getTransactionReceipt' \
          '&txhash=' + tx_hash + \
          '&apikey=' + api
    log_result = utils.getApiText(url)['result']
    contract_abi_path = abi_path + proxy + '_ABI.json'
    with open(contract_abi_path, 'r') as f:
        file = f.read()
        contract_abi = json.loads(json.loads(file))
    decode_txlist = []
    decode_tx = dict()
    decode_tx['contractValue'] = value
    decode_tx['hash'] = normal_tx['hash']
    decode_tx['timeStamp'] = internal_tx['timeStamp']
    decode_tx['dateTime'] = datetime.datetime.utcfromtimestamp(int(decode_tx['timeStamp']))
    decode_tx['dateTime'] = pd.to_datetime(decode_tx['dateTime'])
    decode_tx['nonce'] = int(normal_tx['nonce'], 16)
    decode_tx['type'] = 'Others'
    decode_tx['from'] = normal_tx['from']
    decode_tx['to'] = normal_tx['to']
    decode_tx['relayer'] = 'None'
    decode_tx['proxy'] = Constant.contractAddr.get(proxy)
    decode_tx['fee'] = 'None'
    decode_tx['refund'] = 'None'
    try:
        decode_constructor(contract_abi, normal_tx['input'])
    except:
        try:
            tx_input = decode_function(contract_abi, normal_tx['input'])
        except:
            # 对少部分无法解析的input单独处理
            pass
        else:
            if len(tx_input) == 3 and tx_input[1][1] == '_commitment':
                decode_tx['type'] = 'Deposit'
                decode_tx['to'] = tx_input[0][2]
            elif len(tx_input) == 8 and tx_input[1][1] == '_proof':
                decode_tx['type'] = 'Withdrawal'
                decode_tx['to'] = tx_input[4][2]
                decode_tx['relayer'] = tx_input[5][2]
                decode_tx['fee'] = tx_input[6][2]
                decode_tx['refund'] = tx_input[7][2]
            else:
                pass
    else:
        decode_tx['type'] = 'Create'
        decode_tx['to'] = normal_tx['contractAddress']
    decode_tx['gasLimit'] = int(normal_tx['gas'], 16)
    decode_tx['gasPrice'] = int(normal_tx['gasPrice'], 16)
    decode_tx['gasUsed'] = int(log_result['gasUsed'], 16)
    decode_txlist.append(decode_tx)
    return decode_txlist


def decodeOtherTx(value, normal_tx, internal_tx):
    tx_hash = normal_tx['hash']
    url = 'http://api.etherscan.io/api?module=proxy&action=eth_getTransactionReceipt' \
          '&txhash=' + tx_hash + \
          '&apikey=' + api
    log_result = utils.getApiText(url)['result']
    log_event = log_result['logs']
    decode_txlist = []
    for log in log_event:
        if log['address'] == Constant.contractAddr.get(value).lower():
            decode_tx = dict()
            decode_tx['contractValue'] = value
            decode_tx['hash'] = normal_tx['hash']
            decode_tx['timeStamp'] = internal_tx['timeStamp']
            decode_tx['dateTime'] = datetime.datetime.utcfromtimestamp(int(decode_tx['timeStamp']))
            decode_tx['dateTime'] = pd.to_datetime(decode_tx['dateTime'])
            decode_tx['nonce'] = int(normal_tx['nonce'], 16)
            contract_abi_path = Constant.abiPath + value + '_ABI.json'
            with open(contract_abi_path, 'r') as f:
                file = f.read()
                contract_abi = json.loads(file)
            contract_address = Constant.contractAddr.get(value)
            contract = Contract(contract_address, contract_abi)
            topics = dict()
            for topic in contract.get_topics():
                topics[topic.fingerprint] = topic.description
            decode_tx['type'] = topics[log['topics'][0]].split('(')[0]
            decode_tx['from'] = normal_tx['from']
            if decode_tx['type'] == 'Withdrawal':
                decode_tx['to'] = '0x' + log['data'][2:][0:64][-40:]
                decode_tx['relayer'] = '0x' + log['topics'][1][-40:]
                decode_tx['proxy'] = normal_tx['to']
                decode_tx['fee'] = int('0x' + log['data'][2:][-64:], 16)
            elif decode_tx['type'] == 'Deposit':
                decode_tx['to'] = internal_tx['to']
                decode_tx['relayer'] = 'None'
                decode_tx['proxy'] = internal_tx['from']
                if normal_tx['to'] != decode_tx['proxy']:
                    decode_tx['relayer'] = normal_tx['to']
                decode_tx['fee'] = 'None'
            decode_tx['refund'] = 'None'
            decode_tx['gasLimit'] = int(normal_tx['gas'], 16)
            decode_tx['gasPrice'] = int(normal_tx['gasPrice'],  16)
            decode_tx['gasUsed'] = int(log_result['gasUsed'], 16)
            decode_txlist.append(decode_tx)
    return decode_txlist


tp = Constant.tornadoTxPath
abi_path = Constant.abiPath
api = Constant.apiKey

if __name__ == '__main__':
    processData()
