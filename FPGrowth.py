from collections import OrderedDict
from tqdm import tqdm
import sys
import re
import os.path
import DataDivide
import csv

class treeNode:
    def __init__(self, nameValue, numOccur, parentNode):
        self.name = nameValue
        self.count = numOccur
        self.nodeLink = None
        self.parent = parentNode
        self.children = {}
    
    def inc(self, numOccur):
        """
        增加节点的出现次数
        :param numOccur:
        :return:
        """
        self.count += numOccur
    
    def disp(self, ind=1):
        """
        输出节点和子节点的FP树结构
        :param ind:
        :return:
        """
        print('  ' * ind, self.name, ' ', self.count) # 展示节点名称和出现的次数
        for child in self.children.values():
            child.disp(ind + 1) #打印时，子节点的缩进比父节点更深一级


def createInitSet(dataSet):
    '''
    把原始事务数据集处理成字典的形式，方面后面的函数调用
    frozenset() 返回一个冻结的集合，冻结后集合不能再添加或删除任何元素。
    '''
    retDict=OrderedDict() # retDict = {}
    for trans in dataSet:
        # 把每条数据记录冻结（frozenset函数）后作为字典的键，而每个键对应的值都是1
        retDict[frozenset(trans)] = retDict.get(frozenset(trans), 0) + 1
    return retDict

def createTree(dataSet, minSup=1):
    '''
    createTree(生成FP-tree)
    建造树，首先要扫描整个数据库，根据最小支持度，获得频繁1-项集。
    然后根据频繁1-项集为每一件事物数据按照降序排序，
    并调用update_tree来建造树。
    :param dataSet: dist{行: 出现次数}的样本数据
    :param minSup: 最小的支持度
    :return: retTree  FP-tree
             headerTable 满足minSup {所有的元素+(value, treeNode)}
    '''
    headerTable = {}  # 支持度>=minSup的dist{所有元素: 出现的次数}
    for trans in dataSet:  # 循环 dist{行: 出现次数}的样本数据
        # 对所有的行进行循环，得到行里面的所有元素
        # 统计每一行中，每个元素出现的总次数
        for item in trans:
            # 例如:  {'ababa': 3}  count(a)=3+3+3=9   count(b)=3+3=6
            # 计算每项元素的出现次数
            headerTable[item] = headerTable.get(item, 0) + dataSet[trans]
    # print("createTree 之前的 headerTable:  ", headerTable)
    # print("之前的 headerTable's length: %s" % len(headerTable))

    # 删除 headerTable中，元素次数<最小支持度的元素
    for k in list(headerTable.keys()):  # python3中.keys()返回的是迭代器不是list,不能在遍历时对其改变。
        if headerTable[k] < minSup:
            del (headerTable[k]) # 删除不满足最小支持度的元素
    # print("createTree 删除不满足最小支持度的元素后 headerTable:  ", headerTable)
    # print("删除不满足最小支持度的元素后 headerTable's length: %s" % len(headerTable))

    # 开始构建 FP树
    freqItemSet = set(headerTable.keys())  # 满足最小支持度的频繁项集 # 满足minSup: set(各元素集合)

    if len(freqItemSet) == 0: # 如果不存在，直接返回None
        return None, None

    for k in headerTable: # 我们在每个键对应的值中增加一个“None”，为后面的存储相似元素做准备
        headerTable[k] = [headerTable[k], None] # 格式化:  dist{元素key: [元素次数, None]}
    retTree = treeNode('Null Set', 1, None) # create tree

    '''
    读入每个项集也就是每条记录，并将其添加到一条已经存在的路径中。
    如果该路径不存在，则创建一条新路径。
    假设有集合{z,x,y}和{y,z,r}，
    为了保证相同项只出现一次，需要对每条记录里的元素项进行排序。
    在每条记录中，这种排序是根据每个元素出现的次数进行的，也就是说出现次数越多，排位越前。
    '''
    for tranSet, count in dataSet.items(): # 循环 dist{行: 出现次数}的样本数据
        # print('tranSet, count=', tranSet, count)
        localD = {} # localD = dist{元素key: 元素总出现次数}
        for item in tranSet:
            if item in freqItemSet:# 过滤，只取该样本中满足最小支持度的频繁项
                # print('headerTable[item][0]=', headerTable[item][0], headerTable[item])
                # 把headerTable中记录的该元素的出现次数赋值给localD中的对应键
                localD[item] = headerTable[item][0]
        # print('localD=', localD)
        # 对每一行的key 进行排序，然后开始往树添加枝丫，直到丰满
        # 第二次，如果在同一个排名下出现，那么就对该枝丫的值进行追加，继续递归调用！
        if len(localD) > 0: #如果该条记录有符合条件的元素
            # 根据全局频数从大到小对单样本排序
            # p=key,value; 所以是通过value值的大小，进行从大到小进行排序
            # orderedItems 表示取出元组的key值，也就是字母本身，但是字母本身是大到小的顺序
            # 元素按照支持度排序，支持度越大，排位越靠前
            orderedItems = [v[0] for v in sorted(localD.items(), key=lambda p: (-p[1],p[0]), reverse=True)]
            # 用过滤且排序后的样本更新树
            # print 'orderedItems=', orderedItems, 'headerTable', headerTable, '\n\n\n'
            # 填充树，通过有序的orderedItems的第一位，进行顺序填充 第一层的子节点。
            updateTree(orderedItems, retTree, headerTable, count)
    return retTree, headerTable

def updateTree(items, inTree, headerTable, count):
    '''
    使用频繁项集使FP树生长 (更新FP-tree，第二次遍历)
    更新树是一种递归的思想，首先判断节点是否存在，
    如果存在，则节点合并，并且记录节点的个数加一，
    否则创建新的节点，并更新项头表。
    # 针对每一行的数据
    # 最大的key,  添加
    :param items: 满足minSup 排序后的元素key的数组（大到小的排序）
    :param inTree: 空的Tree对象
    :param headerTable: 满足minSup {所有的元素+(value, treeNode)}
    :param count: 原数据集中每一组Kay出现的次数
    :return: 
    '''
    # 取出 元素 出现次数最高的
    # 如果该元素在 inTree.children 这个字典中，就进行累加
    # 如果该元素不存在 就 inTree.children 字典中新增key，value为初始化的 treeNode 对象
    if items[0] in inTree.children: #如果inTree的子节点中已经存在该元素
        # 更新 最大元素，对应的 treeNode 对象的count进行叠加，增加的值为该元素所在记录的出现次数
        inTree.children[items[0]].inc(count)
    else:
        # 如果不存在子节点，我们为该inTree添加子节点
        inTree.children[items[0]] = treeNode(items[0], count, inTree)
        # 如果满足minSup的dist字典的value值第二位为null， 我们就设置该元素为 本节点对应的tree节点
        # 如果元素第二位不为null，我们就更新header节点
        if headerTable[items[0]][1] is None: #如果在相似元素的字典headerTable中，该元素键对应的列表值中，起始元素为None
            # headerTable只记录第一次节点出现的位置
            headerTable[items[0]][1] = inTree.children[items[0]] #把新创建的这个节点赋值给起始元素
        else:
            # 本质上是修改headerTable的key对应的Tree，的nodeLink值
            # 如果在相似元素字典headerTable中，该元素键对应的值列表中已经有了起始元素，那么把这个新建的节点放到值列表的最后
            updateHeader(headerTable[items[0]][1], inTree.children[items[0]])
    if len(items) > 1:
        # 递归的调用，在items[0]的基础上，添加item0[1]做子节点， count只要循环的进行累计加和而已，统计出节点的最后的统计值。
        updateTree(items[1::], inTree.children[items[0]], headerTable, count)


def updateHeader(nodeToTest, targetNode):
    """
    更新项头表：
    项头表可以使遍历树更加快速，它是一个横向迭代向前并判断的思想。
    更新头指针表，确保节点链接指向树中该元素项的每一个实例
    (更新头指针，建立相同元素之间的关系，
    例如:  左边的r指向右边的r值，就是后出现的相同元素 指向 已经出现的元素)
    从头指针的nodeLink开始，一直沿着nodeLink直到到达链表末尾。这就是链表。
    性能: 如果链表很长可能会遇到迭代调用的次数限制。
    :param nodeToTest: 满足minSup {所有的元素+(value, treeNode)}
    :param targetNode: Tree对象的子节点
    :return:
    """

    while nodeToTest.nodeLink is not None:
        nodeToTest = nodeToTest.nodeLink
    nodeToTest.nodeLink = targetNode


# part 4 ：挖掘频繁项集
def ascendTree(leafNode, prefixPath):
    '''
    # 挖掘频繁项集
    # 递归回溯
    (如果存在父节点，就记录当前节点的name值)
    #该函数找出元素节点leafNode的所有前缀路径，
    并把包括该leafNode及其前缀路径的各个节点的名称保存在prefixPath中
    :param leafNode: 查询的节点对于的nodeTree
    :param prefixPath: 要查询的节点值
    :return:
    '''
    if leafNode.parent is not None:
        prefixPath.append(leafNode.name)
        ascendTree(leafNode.parent, prefixPath)


def findPrefixPath(basePat, treeNode):

    '''
    # 条件模式基
    :param basePat: 要查询的节点值
    :param treeNode: 查询的节点所在的当前nodeTree
    :return:  condPats 对非basePat的倒叙值作为key,赋值为count数
    '''
    condPats = {}
    while treeNode is not None: # 对 treeNode的link进行循环
        prefixPath = []
        ascendTree(treeNode, prefixPath) # 寻找改节点的父节点，相当于找到了该节点的频繁项集
        if len(prefixPath) > 1: # 排除自身这个元素，判断是否存在父元素（所以要>1, 说明存在父元素）
            # 对非basePat的倒叙值作为key,赋值为count数
            # prefixPath[1:] 变frozenset后，字母就变无序了
            # condPats[frozenset(prefixPath)] = treeNode.count
            # 某个元素的前缀路径不包括该元素本身
            condPats[frozenset(prefixPath[1:])] = treeNode.count
        # 递归，寻找改节点的下一个 相同值的链接节点 #下一个相似元素
        treeNode = treeNode.nodeLink
        # print(treeNode)
    # condPats存储的是元素节点treeNode及其所有相似元素节点的前缀路径和它的计数
    return condPats

# part 5 : 递归查找频繁项集
def mineTree(inTree, headerTable, minSup, preFix, freqItemList):
    '''
    递归查找频繁项集
   (创建条件FP树)
    :param inTree: myFPtree
    :param headerTable: 满足minSup {所有的元素+(value, treeNode)}
    :param minSup: 最小支持项集
    :param preFix: preFix为newFreqSet上一次的存储记录，一旦没有myHead，就不会更新
    :param freqItemList: 用来存储频繁子项的列表
    :return:
    '''
    # 通过value进行从小到大的排序， 得到频繁项集的key
    # 最小支持项集的key的list集合
    bigL = [v[0] for v in sorted(headerTable.items(), key=lambda p: str(p[1]))]
    # print('-----', sorted(headerTable.items(), key=lambda p: p[1][0]))
    # print('bigL=', bigL)
    # 循环遍历 最频繁项集的key，从小到大的递归寻找对应的频繁项集
    for basePat in tqdm(bigL,total=len(bigL), colour='#cff0ec', leave=False):
        newFreqSet = preFix.copy() # preFix为newFreqSet上一次的存储记录，一旦没有myHead，就不会更新
        newFreqSet.add(basePat)
        # print('newFreqSet=', newFreqSet, preFix)

        freqItemList.append(newFreqSet)
        # print('freqItemList=', freqItemList)

        condPathBases = findPrefixPath(basePat, headerTable[basePat][1])
        myCondTree, myHead = createTree(condPathBases, minSup)
        # print('myHead=', myHead)
        # 挖掘条件 FP-tree, 如果myHead不为空，表示满足minSup {所有的元素+(value, treeNode)}
        if myHead is not None:
            # myCondTree.disp(1)
            # print('\n\n\n')
            # 递归 myHead 找出频繁项集
            # print('conditional tree for:', newFreqSet)
            mineTree(myCondTree, myHead, minSup, newFreqSet, freqItemList)
        # print('\n\n\n')

def count(value, cnt = 6):
    file = "Result/FPGrowth_"+value+'_'+str(cnt)+'.csv'
    uSet = set()
    uList = []
    real_u = []
    if os.path.exists(file):
        with open(file, "r") as csvFile:
            reader = csv.reader(csvFile)
            for line in reader:
                uList.append(line)
                # uClusterSet = set(line)
                # utils.clusterAppend(uList, uClusterSet)
                # for address in line:
                #     uSet.add(address)
        uList = sorted(uList,key=lambda i : len(i), reverse=True)
        for cluster in uList:
            uClusterSet = set(cluster)
            if len(uSet.intersection(uClusterSet)) == 0:
                uSet = uSet.union(uClusterSet)
                real_u.append(uClusterSet)
    else:
        print(file,"does not exist!!")
    return real_u, len(real_u), len(uSet)

if __name__ == '__main__':

    value = sys.argv[1]
    cnt = int(sys.argv[2])
    print("|", str("Start divide " + str(value) + " support:" + str(cnt)).center(100),"|")
    suffix = value + '_' + str(cnt) 
    type = ''.join(re.findall(r'[A-Za-z]', value))
    vdir, data = DataDivide.loadAllData(type)
    i = vdir.index(value)
    v = value
    dataset  = data[i]
    print("|", str("Start " + str(v) + " FPGrowth").center(100),"|")
    initSet = createInitSet(dataset)
    fpTree, headerTab = createTree(initSet, cnt)
    freqItemList = []
    mineTree(fpTree, headerTab, cnt, set([]), freqItemList)

    with open('Result/FPGrowth_'+value+'_'+str(cnt)+'.csv','w', newline='') as f:
        writer = csv.writer(f)
        for row in freqItemList:
            if len(row) > 1:
                writer.writerow(row)