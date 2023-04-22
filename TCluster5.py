# 用外部交易来关联混币交易地址
import Constant
from Constant import addressPath, addressOuterTxPath, contractAddr, resultPath
import os.path
from tqdm import tqdm
import pandas as pd
import utils
import csv


def clusterTx(value, f_addr, t_addr, addr_dict, u_list):
    u_cluster_set = set()
    from_addr = addr_dict[f_addr]
    to_addr = addr_dict[t_addr]
    from_addr_wit = from_addr[value + '_Wit'] - from_addr[value + '_Dep']
    to_addr_dep = to_addr[value + '_Dep'] - to_addr[value+'_Wit']
    if 0 < from_addr_wit <= to_addr_dep or from_addr[value + '_Wit'] == to_addr[value + '_Dep'] == 0:
        u_cluster_set.add(f_addr)
        u_cluster_set.add(t_addr)
        utils.clusterAppend(u_list, u_cluster_set)
    return u_list


def ethOuterTxCluster(normal_path, addresses, value, u_list):
    addr_dict = addresses.to_dict('index')
    # contract_addr = utils.toLower(contractAddr)
    cnt = 0
    fd = normal_path+'_'+str(cnt)+'.pkl'
    while os.path.exists(fd):
        cnt+=1
        fd = normal_path+'_'+str(cnt)+'.pkl'
    for i in tqdm(range(cnt), desc=value+' cluster transfer', colour='#ff858a'):
        fd = normal_path+'_'+str(i)+'.pkl'
        df = utils.readPklFile(fd)
        for item in tqdm(df.itertuples(), total=df.shape[0], desc='Normal_'+str(i),colour='#90ee90',leave=False):
            f = getattr(item,'_7')
            t = getattr(item,'to')
            if f != t and f in addr_dict and t in addr_dict:
                u_list = clusterTx(value, f, t, addr_dict, u_list)
            # elif item['from'] in addr_dict:
            #     internal_tx = internal_txs[internal_txs['hash'] == item['hash']]
            #     if len(internal_tx) > 0:
            #         internal_tx_f_addr = internal_tx.to_dict('records')[0]['from']
            #         internal_tx_t_addr = internal_tx.to_dict('records')[0]['to']
            #         if internal_tx_t_addr != item['from'] and internal_tx_f_addr not in contract_addr.values() and \
            #                 internal_tx_t_addr in addr_dict:
            #             u_list = clusterTx(value, item['from'], internal_tx.to_dict('records')[0]['to'], addr_dict, u_list)
    u_set = set()
    for i in range(len(u_list)):
        for j in u_list[i]:
            u_set.add(j)
    return len(u_list), len(u_set)

def outerTxCluster(txs, addresses, value, u_list):
    addr_dict = addresses.to_dict('index')
    tx_list = txs.to_dict('records')
    for tx_i, item in enumerate(tqdm(tx_list)):
        # if (item['to'] in contractAddr or item['to'] == item['from']) or \
        #         (item['to'] not in addr_dict or item['from'] not in addr_dict):
        if item['from'] != item['to'] and item['from'] in addr_dict and item['to'] in addr_dict:
            u_list = clusterTx(value, item['from'], item['to'], addr_dict, u_list)
    u_set = set()
    for i in range(len(u_list)):
        for j in u_list[i]:
            u_set.add(j)
    return len(u_list), len(u_set)

