import json
import os
import utils
import pandas as pd
import Constant


# 获取contract abi
def getContractABI():
    suffix = '_ABI.json'
    for key, value in contract_addr.items():
        abiDirectory = ap + key + suffix
        print("{: ^100s}".format(abiDirectory))
        url = 'http://api.etherscan.io/api?module=contract&action=getabi&' \
              'address=' + value + '&' \
              'apikey=' + api
        result = utils.getApiText(url)
        if result['status'] == '1':
            data = result['result']
            print(data)
            with open(abiDirectory, 'w') as wf:
                json.dump(data, wf)
            print("{:-^100s}".format('-'))


def getTx():
    suffix = ["_NormalTx.json", "_InternalTx.json"]
    action = ['txlist', 'txlistinternal']
    for index in range(len(suffix)):
        url = 'http://api.etherscan.io/api?module=account&action=' + action[index]
        for value in values:
            data_size, data, save_path = getTornadoTx(contract_addr, url, suffix[index], value)
            print("{: ^100s}".format("data size:%d" % data_size))
            if data is not None:
                data.to_json(save_path, orient='records')


def getERC20TX():
    action = 'tokentx'
    for value in values:
        if 'USDC' in value:
            suffix = '_USDCTx.json'
            tokenAddr = erc20Address.get('USDC')
        elif 'USDT' in value:
            suffix = '_USDTTx.json'
            tokenAddr = erc20Address.get('USDT')
        elif 'cDAI' in value:
            suffix = '_cDAITx.json'
            tokenAddr = erc20Address.get('cDAI')
        elif 'DAI' in value:
            suffix = '_DAITx.json'
            tokenAddr = erc20Address.get('DAI')
        elif 'WBTC' in value:
            suffix = '_WBTCTx.json'
            tokenAddr = erc20Address.get('WBTC')
        else:
            continue
        url = 'http://api.etherscan.io/api?module=account&action=' + action + '&contractaddress=' + tokenAddr
        data_size, data, save_path = getTornadoTx(contract_addr, url, suffix, value)
        print("{: ^100s}".format("data size:%d" % data_size))
        if data is not None:
            data.to_json(save_path, orient='records')


def getTornadoTx(contracts, pre_url, suffix, value):
    print("{:-^100s}".format('-'))
    save_path = tp + value + suffix
    print("{:-^100s}".format(save_path))
    print("{:-^100s}".format('-'))
    address = contracts.get(value)
    startblock = start_block
    lastblock = startblock
    endblock = end_block
    page = 1
    offset = 5000
    dataSize = 0
    newDataSize = dataSize
    # 获取交易数据
    if os.path.exists(save_path):
        data = pd.read_json(save_path, orient='records')
    else:
        data = None
    while dataSize == 0 or newDataSize != dataSize:
        dataSize = newDataSize
        if page*offset > 10000:
            startblock = lastblock
            page = 1
        url = pre_url + '&address=' + address + '&' \
            'startblock=' + startblock + '&endblock=' + endblock + '&' \
            'page=' + str(page) + '&offset=' + str(offset) + '&sort=asc&' \
            'apikey=' + api
        result = utils.getApiText(url)
        if result['status'] == '1':
            newRes = pd.DataFrame(result['result'])
            print("{: ^100s}".format("%s page:%d, data size:%d" % (os.path.basename(save_path), page, len(newRes))))
            if data is None:
                data = newRes
            else:
                data = data.append(newRes)
                data.drop_duplicates(inplace=True)
            lastblock = data.tail(1).iloc[0]['blockNumber']
            newDataSize = len(data)
            if len(newRes) < offset:
                return newDataSize, data, save_path
        elif result['message'] == 'No transactions found':
            return newDataSize, data, save_path
        page += 1
    return newDataSize, data, save_path


ap = Constant.abiPath
api = Constant.apiKey
contract_addr = Constant.contractAddr
tp = Constant.tornadoTxPath
values = Constant.values
erc20Address = Constant.ERC20TokenAddress
start_block = Constant.startBlock
end_block = Constant.endBlock

if __name__ == '__main__':
    # getContractABI()
    getTx()
    # getERC20TX()
