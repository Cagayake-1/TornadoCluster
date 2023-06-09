import csv
import os
import time
import sys
import pandas as pd
import Constant
import TCluster1
import TCluster2
import TCluster3
import TCluster4
import TCluster5
import TCluster6
import FPGrowth
import utils

rp = Constant.resultPath
ap = Constant.addressPath
tx_path = Constant.tornadoTxPath
outer_tx_path = Constant.addressOuterTxPath
deltaT1 = Constant.deltaT1
deltaT2 = Constant.deltaT2
deltaT3 = Constant.deltaT3
deltaT3_dw = Constant.deltaT3_dw
values = Constant.values


def Cluster(tp, rule):
    path = Constant.resultPath
    res_dir = 'rule_result.csv'
    if os.path.exists(path+res_dir):
        cntdf = utils.readCsvFile(path+res_dir,0)
    else:
        cntdf = pd.DataFrame(index = values)
    for file_dir in os.listdir(tp + "CSV"):
        value = file_dir.split('_')[0]
        uList = []
        cluster_dir = rp + value + "_" + rule + ".csv"
        if os.path.exists(cluster_dir):
            continue
        print("{: ^100s}".format("Clustering the " + os.path.basename(file_dir) + "..."))
        time.sleep(2)
        userClusterNum, clusteredAddressNum = 0, 0
        
        if rule == "rule1":
            df = utils.readDataFromCsv(tp + 'csv/' + file_dir)
            userClusterNum, clusteredAddressNum = TCluster1.singleDWCouple(df, uList, deltaT1)
            col = ['U-'+rule,'A-'+rule]
        elif rule == "rule2":
            df = utils.readDataFromCsv(tp + 'csv/' + file_dir)
            userClusterNum, clusteredAddressNum = TCluster2.findSingleDWCouple(df, uList, deltaT2)
            col = ['U-'+rule,'A-'+rule]
        elif rule == "rule3":
            df = utils.readDataFromCsv(tp + 'csv/' + file_dir)
            userClusterNum, clusteredAddressNum = TCluster3.multiDWCouple(df, uList, deltaT3, deltaT3_dw)
            col = ['U-'+rule,'A-'+rule]
        elif rule == "rule4":
            df = utils.readDataFromCsv(tp + 'csv/' + file_dir)
            userClusterNum, clusteredAddressNum = TCluster4.fromToCouple(df, uList)
            col = ['U-'+rule,'A-'+rule]
        elif rule == "rule5":
            addr_df = pd.read_csv(ap + value + "_Address_Statics.csv", index_col=0, low_memory=False)
            if 'ETH' in value:
                norm_path = outer_tx_path + value + '_NormalTx'
                # internal_df = utils.readDataFromCsv(outer_tx_path + 'csv/' + value + '_OuterInternalTx')
                # normal_df = utils.readDataFromCsv(outer_tx_path + 'csv/' + value + '_OuterNormalTx')
                userClusterNum, clusteredAddressNum = \
                    TCluster5.ethOuterTxCluster(norm_path, addr_df, value, uList)
            else:
                df = utils.readDataFromCsv(outer_tx_path + 'csv/' + value + '_OuterTokenTx.csv')
                userClusterNum, clusteredAddressNum = TCluster5.outerTxCluster(df, addr_df, value, uList)
            col = ['U-'+rule,'A-'+rule]
        elif rule == "rule6":
            addr_df = pd.read_csv(ap + value + "_Address_Statics.csv", index_col=0, low_memory=False)
            if 'ETH' in value:
                norm_path = outer_tx_path + value + '_NormalTx'
                uList, userClusterNum, clusteredAddressNum = \
                    TCluster6.ethOuterPoolingTxCluster(norm_path, addr_df, value, uList)
            else:
                df = utils.readDataFromCsv(outer_tx_path + 'csv/' + value + '_OuterTokenTx.csv')
                uList, userClusterNum, clusteredAddressNum = TCluster6.OuterPoolTxCluster(df, addr_df, value, uList)
            col = ['U-'+rule+'-20','A-'+rule+'-20']
        elif rule == "mine":
            cnt = 3
            uList, userClusterNum, clusteredAddressNum = FPGrowth.count(value,cnt)
            col = ['U-'+rule+'-'+str(cnt),'A-'+rule+'-'+str(cnt)]
        cntdf.loc[value,col] = userClusterNum,clusteredAddressNum
        print("cluster size:", str(userClusterNum) + ", cluster address number:" + str(clusteredAddressNum))
        with open(cluster_dir, 'w', newline="") as f:
            w = csv.writer(f)
            for row in uList:
                w.writerow(row)
    
    utils.saveCsvFile(path+res_dir, cntdf)
    print("{: ^100s}".format(" Merge The Result "))
    allUserList = utils.clusterMerge(rp, rule)
    with open("Result/" + rule + ".csv", 'w', newline="") as f:
        w = csv.writer(f)
        for row in allUserList:
            w.writerow(row)


def staticAnonymity(type):
    path = Constant.resultPath
    res_dir = 'deanonymity_result.csv'
    if os.path.exists(path + res_dir):
        cntdf = utils.readCsvFile(path + res_dir,0)
    else:
        cntdf = pd.DataFrame(index = values)
    for value in values:
        uSet = set()
        allUserList = []
        if 'heuristic' in type:
            suffix = ['_rule1','_rule2','_rule3']
            for suf in suffix:
                file = value + suf +'.csv'
                dir = path + file
                with open(dir, "r") as f:
                    reader = csv.reader(f)
                    for line in reader:
                        uClusterSet = set(line)
                        utils.clusterAppend(allUserList, uClusterSet)
                        for address in line:
                            uSet.add(address)
            u = len(allUserList)
            a = len(uSet)
            print("[Heuristic] Total clustered "+ value +" user size:" + str(u))
            print("[Heuristic] Total clustered "+ value +" address size:", str(a))
            col = ['U-Heuristic','De-ASet-Heuristic']
            cntdf.loc[value,col] = u,a
        base_u = allUserList.copy()
        base_a = uSet.copy()
        if 'mode' in type:
            suffix = ['_rule5','_rule6']
            for suf in suffix:
                uthis = allUserList.copy()
                athis = uSet.copy()
                file = value + suf +'.csv'
                dir = path + file
                with open(dir, "r") as f:
                    reader = csv.reader(f)
                    for line in reader:
                        uClusterSet = set(line)
                        utils.clusterAppend(uthis, uClusterSet)
                        for address in line:
                            athis.add(address)
                u = len(uthis)
                a = len(athis)
                print("[Mode" + suf + "] Add clustered "+ value +" user size:" + str(u))
                print("[Mode" + suf + "] Add clustered "+ value +" address size:", str(a))
                col = ['U'+suf,'De-ASet'+suf]
                cntdf.loc[value,col] = u,a
            for suf in suffix:
                file = value + suf +'.csv'
                dir = path + file
                with open(dir, "r") as f:
                    reader = csv.reader(f)
                    for line in reader:
                        uClusterSet = set(line)
                        utils.clusterAppend(allUserList, uClusterSet)
                        for address in line:
                            uSet.add(address)
            u = len(allUserList)
            a = len(uSet)
            print("[Mode] Add clustered "+ value +" user size:" + str(u))
            print("[Mode] Add clustered "+ value +" address size:", str(a))
            col = ['U-mode','De-ASet-mode']
            cntdf.loc[value,col] = u,a
        if 'mine' in type:
            suffix = '_mine'
            file = value + suffix + '.csv'
            dir = path + file
            if os.path.exists(dir):
                with open(dir, "r") as f:
                    reader = csv.reader(f)
                    for line in reader:
                        uClusterSet = set(line)
                        utils.clusterAppend(allUserList, uClusterSet)
                        for address in uClusterSet:
                            uSet.add(address)
                u = len(allUserList)
                a = len(uSet)
                print("[Mine] Add clustered "+ value +" user size:" + str(len(allUserList)))
                print("[Mine] Add clustered "+ value +" address size:", str(len(uSet)))
                col = ['U'+suffix,'De-ASet'+suffix]
                cntdf.loc[value,col] = u,a
                print(len(base_u))
                print(len(base_a))
                with open(dir, "r") as f:
                    reader = csv.reader(f)
                    for line in reader:
                        uClusterSet = set(line)
                        utils.clusterAppend(base_u, uClusterSet)
                        for address in uClusterSet:
                            base_a.add(address)
                u = len(base_u)
                a = len(base_a)
                print("[FP-Growth] Add clustered "+ value +" user size:" + str(u))
                print("[FP-Growth] Add clustered "+ value +" address size:", str(a))
                suffix = '_fp'
                col = ['U'+suffix,'De-ASet'+suffix]
                cntdf.loc[value,col] = u,a
            else:
                print(dir + " doesnt exist!!")
    utils.saveCsvFile(path + res_dir,cntdf)

if __name__ == '__main__':
    # 0000000
    rules = str(sys.argv[1])
    
    type1 = 'heuristic'
    if rules[0] == '1':
        print("{: ^100s}".format(" RULE1: SINGLE DW "))
        print("{: ^100s}".format("----------------------------------------------------------------"))
        Cluster(tx_path, "rule1")
    if rules[1] == '1':
        print("{: ^100s}".format(" RULE2: MULTI SINGLE DW "))
        print("{: ^100s}".format("----------------------------------------------------------------"))
        Cluster(tx_path, "rule2")
    if rules[2] == '1':
        print("{: ^100s}".format(" RULE3: MULTI DW "))
        print("{: ^100s}".format("----------------------------------------------------------------"))
        Cluster(tx_path, "rule3")
    if rules[3] == '1':
        print("{: ^100s}".format(" RULE4: WITHDRAW FROM-TO-DIF and FEE-0 "))
        print("{: ^100s}".format("----------------------------------------------------------------"))
        Cluster(tx_path, "rule4")

    type2 = 'mode'
    if rules[4] == '1':
        print("{: ^100s}".format(" RULE: TRANSFER MODE"))
        print("{: ^100s}".format("----------------------------------------------------------------"))
        Cluster(tx_path, "rule5")
    if rules[5] == '1':
        print("{: ^100s}".format(" RULE: POOLING MODE"))
        print("{: ^100s}".format("----------------------------------------------------------------"))
        Cluster(tx_path, "rule6")

    type3 = 'mine'
    if rules[6] == '1':
        print("{: ^100s}".format(" FPGrowth MINING "))
        print("{: ^100s}".format("----------------------------------------------------------------"))
        Cluster(tx_path, "mine")
        
    # staticAnonymity([type1,type3])

    # print("{: ^100s}".format(" FINAL RESULT"))
    # print("{: ^100s}".format("----------------------------------------------------------------"))
    
    # type3 = 'apriori'
    # print("{: ^100s}".format(" FINAL RESULT"))
    # print("{: ^100s}".format("----------------------------------------------------------------"))
    # uSet = set()
    # allUserList = []
    # for cluster_dir in os.listdir(rp):
    #     if len(cluster_dir.split('_')) == 1:
    #         with open(rp + cluster_dir, "r") as csvFile:
    #             reader = csv.reader(csvFile)
    #             for line in reader:
    #                 uClusterSet = set(line)
    #                 utils.clusterAppend(allUserList, uClusterSet)
    #                 for address in line:
    #                     uSet.add(address)
    # print("Total clustered user size:" + str(len(allUserList)))
    # print("Total clustered address size:", str(len(uSet)))
    # with open("Result/finalResult.csv", 'w', newline="") as f:
    #     w = csv.writer(f)
    #     for row in allUserList:
    #         w.writerow(row)
