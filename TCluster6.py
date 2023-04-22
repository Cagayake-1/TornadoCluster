
from tqdm import tqdm
import pandas as pd
import os.path
import utils
from Constant import contractAddr, apiKey

condict = set()
nordict = set()
def isContractAddr(addr, api):
    if addr in condict:
        return True
    elif addr in nordict:
        return False
    else:
        url = 'https://api.etherscan.io/api?module=proxy&action=eth_getCode&address='+addr+'&tag=latest&apikey=' + api
        res = utils.getApiText(url)
        isContract = res['result']!='0x'
        if isContract:
            condict.add(addr)
        else:
            nordict.add(addr)
        return isContract


def clusterUser(tcad, oa, value, addr_dict,user_set, key_set):
    tc_dep = addr_dict[tcad][value+'_Dep']
    tc_wit = addr_dict[tcad][value+'_Wit']
    
    # tcaddrs是存款地址
    # if tc_dep>0 and tc_wit == 0 and isContractAddr(oa, apiKey) == False:
    if tc_dep>0 and tc_wit == 0:
        key = oa+'_dep'    
        if key in user_set:
            if len(user_set[key]) > 10:
                key_set.add(key)
            else:
                user_set[key].append(tcad)
        else:
            user_set[key] = [tcad]
    # tcaddrs是取款地址
    # if tc_wit>0 and tc_dep == 0 and isContractAddr(oa, apiKey) == False:
    if tc_wit>0 and tc_dep == 0:
        key = oa+'_dep'
        if key in user_set:
            if len(user_set[key]) > 10:
                key_set.add(key)
            else:
                user_set[key].append(tcad)
        else:
            user_set[key] = [tcad]
        
    return user_set

def setTList(userSet, keySet):
    u_list = []
    for key , item in userSet.items():
        if key not in keySet and len(item) >=2:
            u_cluster_set = set(item)
            utils.clusterAppend(u_list, u_cluster_set)
    return u_list


def ethOuterPoolingTxCluster(normal_path,adf,value, u_list):
    addr_dict = adf.to_dict('index')
    df = pd.DataFrame()
    cnt = 0
    fd = normal_path+'_'+str(cnt)+'.pkl'
    userSet = {}
    keySet = set()
    while os.path.exists(fd):
        cnt+=1
        fd = normal_path+'_'+str(cnt)+'.pkl'
    for i in tqdm(range(cnt), desc=value+' cluster pooling', colour='#ffc0cb'):
        fd = normal_path+'_'+str(i)+'.pkl'
        df = utils.readPklFile(fd)
        last = ''
        for tx in tqdm(df.itertuples(), total=df.shape[0], desc='Normal'+str(i),colour='#cff0ec', leave=False):
            f = getattr(tx,'_7')
            t = getattr(tx,'to')
            if t!= ''  and f in addr_dict and f != last:
                userSet = clusterUser(f,t, value, addr_dict, userSet, keySet)
                last = f
    u_list = setTList(userSet,keySet)
    u_set = set()
    print(">50 key len:", str(len(keySet)))
    for i in range(len(u_list)):
        for j in u_list[i]:
            u_set.add(j)
    return u_list, len(u_list), len(u_set)

def OuterPoolTxCluster(txdf, adf, value, u_list):
    addr_dict = adf.to_dict('index')
    last = ''
    userSet = {}
    keySet = set()
    for i in tqdm(txdf.itertuples(),  total=txdf.shape[0], desc=value,colour='#ffd9e6'):
        f = getattr(i,'_5')
        t = getattr(i,'to')
        if t!= ''  and f in addr_dict and f != last:
            userSet = clusterUser(f,t, value, addr_dict,userSet, keySet)
            last = f
    u_list = setTList(userSet,keySet)
    u_set = set()
    for i in range(len(u_list)):
        for j in u_list[i]:
            u_set.add(j)
    return u_list, len(u_list), len(u_set)