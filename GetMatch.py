import os
import pandas as pd
from tqdm import tqdm
tx_path = 'Dataset/TornadoTx/CSV/'
addr_path = 'Dataset/AnonymousAddress/'
def getMatchTx():
    for file_dir in os.listdir(tx_path):
        value = file_dir.split('_')[0]
        if 'ETH' in file_dir:
            print("{: ^100s}".format(" value: " + file_dir+ "..."))
            result_dir = tx_path + value + "_sameAddr.csv"
            addr_df = pd.read_csv(addr_path + value + "_Address_Statics.csv", index_col=0, low_memory=False)
            addr_dict = addr_df.to_dict('index')
            tx_data = pd.read_csv(tx_path + file_dir, low_memory=False)
            pd.set_option('display.max_columns', None)
            tx_df = pd.DataFrame(tx_data)
            length = tx_df.shape[0]
            result_df = pd.DataFrame()
            for idx in tqdm(range(length)):
                tx = tx_df.iloc[idx].to_dict()
                if tx['from'] in addr_dict and addr_dict[tx['from']][value + '_Wit']>0 and addr_dict[tx['from']][value + '_Dep']>0:
                    result_df = result_df.append(tx, ignore_index=True)
            result_df.to_csv(result_dir, index=False)

if __name__ == '__main__':
    getMatchTx()