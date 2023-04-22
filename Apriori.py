from numpy import *
from tqdm.auto import tqdm
import csv
import pandas as pd
import Constant
# 构造数据
def loadDataSet():
    
    return [[1, 3, 4], [2, 3, 5], [1, 2, 3, 5], [2, 5]]

# 创建初始的频繁一项集
# 将所有元素转换为frozenset型字典，存放到列表中

def createC1(dataSet):
    C1 = []
    for transaction in tqdm(dataSet, desc='dataSet', colour='#0a5a0a'):
        for item in tqdm(transaction, desc='tx', leave=False, delay=3):
            if not [item] in C1:
                C1.append([item])
    C1.sort()
    # 使用frozenset是为了后面可以将这些值作为字典的键
    return list(map(frozenset, C1))  # frozenset一种不可变的集合，set可变集合

# 过滤掉不符合支持度的集合
# 返回 频繁项集列表retList 所有元素的支持度字典
def scanD(D, Ck, minSupport):
    ssCnt = {}
    for tid in tqdm(D, desc='Dataset', colour = '#075373'): #D:dataset
        for can in tqdm(Ck,desc='遍历Ck项集', leave=False, colour='#bfd4d4',delay=3): #Ck：k项集
            if can.issubset(tid):   # 判断can是否是tid的《子集》 （这里使用子集的方式来判断两者的关系）
                if can not in ssCnt:    # 统计该值在整个记录中满足子集的次数（以字典的形式记录，frozenset为键）
                    ssCnt[can] = 1
                else:
                    ssCnt[can] += 1
    # numItems = float(len(D))
    retList = []        # 重新记录满足条件的数据值（即支持度大于阈值的数据）
    supportData = {}    # 每个数据值的支持度
    for key in tqdm(ssCnt, desc='筛选支持度', leave=False, colour='#ffa77f',delay=3):
        # support = ssCnt[key] / numItems
        # if support >= minSupport: # 符合支持度的集合加入retList
        support = ssCnt[key]
        if support >= minSupport:
            retList.insert(0, key)
        supportData[key] = support
    return retList, supportData # 排除不符合支持度元素后的元素 每个元素支持度

# 生成所有可以组合的集合
# 频繁项集列表Lk 项集元素个数k  [frozenset({2, 3}), frozenset({3, 5})] -> [frozenset({2, 3, 5})]
def aprioriGen(Lk, k):
    retList = []
    lenLk = len(Lk)
    for i in tqdm(range(lenLk), desc='对于Lk中每个元素', colour='#0a5a0a'): # 两层循环比较Lk中的每个元素与其它元素
        for j in tqdm(range(i+1, lenLk),desc='比较两个list的前k-个元素是否相等', leave=False, colour='#bfd4d4',delay=3):
            L1 = list(Lk[i])[:k-2]  # 将集合转为list后取值
            L2 = list(Lk[j])[:k-2]
            L1.sort(); L2.sort()        # 这里说明一下：该函数每次比较两个list的前k-2个元素，如果相同则求并集得到k个元素的集合
            if L1==L2:
                retList.append(Lk[i] | Lk[j]) # 求并集
    return retList  # 返回频繁项集列表Ck

# apriori算法主函数
# 封装所有步骤的函数
# 返回 所有满足大于阈值的组合 集合支持度列表

def apriori(dataSet, minSupport):
    # dataSet = [[1, 3, 4], [2, 3, 5], [1, 2, 3, 5], [2, 5]]
    D = list(map(set, tuple(dataSet))) # 转换列表记录为字典  [{1, 3, 4}, {2, 3, 5}, {1, 2, 3, 5}, {2, 5}]
    print("|", str("Create Fozenset C1").center(100),"|")
    C1 = createC1(dataSet)      # 将每个元素转会为frozenset字典 （一个冻结的集合，冻结后集合不能再添加或删除任何元素）   [frozenset({1}), frozenset({2}), frozenset({3}), frozenset({4}), frozenset({5})]
    print("|", str("C1 len:" + str(len(C1))).center(100),"|")
    print("|", str("Scan L1").center(100),"|")
    L1, supportData = scanD(D, C1, minSupport)  # 过滤数据
    # 删除k=1的支持度值（用不上
    supportData = {}
    print("|", str("L1 len:" + str(len(L1))).center(100),"|")
    L = [L1]
    k = 2
    while (len(L[k-2]) > 0):    # 若仍有满足支持度的集合则继续做关联分析
        
        print("|", str("Apriori Gen C"+str(k)).center(100),"|")
        Ck = aprioriGen(L[k-2], k)  # Ck候选频繁项集
        print("|", str("C"+str(k)+" len:" + str(len(Ck))).center(100),"|")
        print("|", str("Scan L"+str(k)).center(100),"|")
        Lk, supK = scanD(D, Ck, minSupport) # Lk频繁项集
        print("|", str("L"+str(k)+" len:" + str(len(Lk))).center(100),"|")
        print("|", str("Update Fozenset ...").center(100),"|")
        supportData.update(supK)    # 更新字典（把新出现的集合:支持度加入到supportData中）
        L.append(Lk)
        k += 1  # 每次新组合的元素都只增加了一个，所以k也+1（k表示元素个数）
    return L, supportData
 

def topK_apriori(L, supportData, k=10):
    maxFreqSet = []
    # 将频繁项集输出到一个列表
    for i in range(len(L)):
        maxFreqSet += L[i]
       
    topk={} # 记录前k个频繁项集
    uniqueSet = set() # 记录已经加入topk频繁项集的元素
    while(len(maxFreqSet)>0 and k>0): # 当剩下的频繁项集不为空，且不满k个频繁项集
        freSet = maxFreqSet.pop() # 对每个频繁项集做处理
        if len(freSet) == 1:
            continue
        topk[freSet] = supportData[freSet] # 加入到划分集中
        for item in freSet: # 记录已经加入topk频繁项集的元素
            uniqueSet.add(item)
        next_maxFreqSet = [] # 记录剔除已被划分的元素
        for fs in maxFreqSet:
            flag = True
            for s in fs:
                if s in uniqueSet:
                    flag = False
                    break
            if flag:
                next_maxFreqSet.append(fs)   
        maxFreqSet = next_maxFreqSet # 更新频繁项集
        k -= 1
    return topk


def ResCnt():
    topk = 500
    cnt = 3
    values = Constant.values
    cntdf = pd.DataFrame(index=values)
    values = ['100DAI', '1000DAI', '10000DAI', '100000DAI',
              '5000cDAI', '50000cDAI', '500000cDAI', '5000000cDAI',
              '100USDC', '1000USDC',
              '100USDT', '1000USDT',
              '0.1WBTC', '1WBTC', '10WBTC']
    for v in values:
        path = Constant.resultPath
        suf = v + '_Top_' + str(topk) + '_' + str(cnt) 
        filepath =  path + 'Apriori_' + suf +'.csv'
        ucnt = 0
        acnt = 0
        maxapu = -1
        with open(filepath) as f:
            reader = csv.reader(f)
            for row in reader:
                ucnt += 1
                apu = len(row) - 1
                acnt += apu
                maxapu = max(apu, maxapu)
        col = ['ucnt-'+str(topk)+'-'+str(cnt),'acnt-'+str(topk)+'-'+str(cnt),'maxapu-'+str(topk)+'-'+str(cnt)]
        cntdf.loc[v,col] = ucnt,acnt,maxapu
    cntdf.to_excel(path + 'apriori_result.xlsx', sheet_name='Apriori')


if __name__ == '__main__':
    ResCnt()
