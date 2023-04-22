values = ['0.1ETH', '1ETH', '10ETH', '100ETH',
          '100DAI', '1000DAI', '10000DAI', '100000DAI',
          '100USDT', '1000USDT',
          '100USDC', '1000USDC',
          '0.1WBTC', '1WBTC', '10WBTC',
          '5000cDAI', '50000cDAI', '500000cDAI', '5000000cDAI'
          ]

contractAddr = {'0.1ETH': '0x12D66f87A04A9E220743712cE6d9bB1B5616B8Fc',
                '1ETH': '0x47CE0C6eD5B0Ce3d3A51fdb1C52DC66a7c3c2936',
                '10ETH': '0x910Cbd523D972eb0a6f4cAe4618aD62622b39DbF',
                '100ETH': '0xA160cdAB225685dA1d56aa342Ad8841c3b53f291',
                '100DAI': '0xD4B88Df4D29F5CedD6857912842cff3b20C8Cfa3',
                '1000DAI': '0xFD8610d20aA15b7B2E3Be39B396a1bC3516c7144',
                '10000DAI': '0x07687e702b410Fa43f4cB4Af7FA097918ffD2730',
                '100000DAI': '0x23773E65ed146A459791799d01336DB287f25334',
                '5000cDAI': '0x22aaA7720ddd5388A3c0A3333430953C68f1849b',
                '50000cDAI': '0x03893a7c7463AE47D46bc7f091665f1893656003',
                '500000cDAI': '0x2717c5e28cf931547B621a5dddb772Ab6A35B701',
                '5000000cDAI': '0xD21be7248e0197Ee08E0c20D4a96DEBdaC3D20Af',
                '100USDC': '0xd96f2B1c14Db8458374d9Aca76E26c3D18364307',
                '1000USDC': '0x4736dCf1b7A3d580672CcE6E7c65cd5cc9cFBa9D',
                '100USDT': '0x169AD27A470D064DEDE56a2D3ff727986b15D52B',
                '1000USDT': '0x0836222F2B2B24A3F36f98668Ed8F0B38D1a872f',
                '0.1WBTC': '0x178169B423a011fff22B9e3F3abeA13414dDD0F1',
                '1WBTC': '0x610B717796ad172B316836AC95a2ffad065CeaB4',
                '10WBTC': '0xbB93e510BbCD0B7beb5A853875f9eC60275CF498',
                'Proxy': '0x722122dF12D4e14e13Ac3b6895a86e84145b6967',
                'OldProxy': '0x905b63fff465b9ffbf41dea908ceb12478ec7601'}

ERC20TokenAddress = {'DAI': '0x6b175474e89094c44da98b954eedeac495271d0f',
                     'cDAI': '0x5d3a536E4D6DbD6114cc1Ead35777bAB948E3643',
                     'USDT': '0xdAC17F958D2ee523a2206206994597C13D831ec7',
                     'USDC': '0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48',
                     'WBTC': '0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599'}

addressPath = 'Dataset/AnonymousAddress/'
addressOuterTxPath = 'Dataset/OuterTx/'
abiPath = 'ABI/'
tornadoTxPath = 'Dataset/TornadoTx/'
apiKey = '968YP1WBG4C39V2JFAT9QESNB3WJJ5MYA4'
resultPath = 'Result/'
startBlock = '9116966' # Dec-16-2019 07:08:43 PM +UTC (Tornado Cash 0.1Eth created)
endBlock = '16530247' # Jan-31-2023 11:59:59 PM +UTC
deltaT1 = 10*60
deltaT2 = 20*60
deltaT3 = 10*60
deltaT3_dw = 30 * 60

#以太坊伦敦升级的时间
LondonBlockHeight = 12965000
LondonBlockHash = '0x9b83c12c69edb74f6c8dd5d052765c1adf940e320bd1291696e6fa07829eee71'
LondonBlockTimeStamp = 1628166822
# totalAddrSize = [6087, 6160, 5660, 2767,
#                  204, 254, 4,
#                  55, 138, 1,
#                  227, 301, 10, 1]
# totalAddrAll = 17237
# anonymitySize = [6032, 6089, 5570, 2686,
#                  181, 222, 2,
#                  42, 110, 0,
#                  201, 254, 6, 0]
# anonymitySizeAll = 17152

pklFileCnt = 200000

ZoneBins = [-1,0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23]


# cDAI
ValBins = {
    'ETH':[0,1e-1,2e-1,3e-1,4e-1,5e-1,6e-1,7e-1,9e-1,1,2,3,5,8,10,20,30,40,50,60,70,80,1e2,5e5],
    'USDC':[0,50,70,80,90,100,300,500,600,850,1000,1700,2500,3000,4000,6000,8000,1e4,1.5e4,2.5e4,5e4,3e6],
    'USDT':[0,50,70,90,100,200,300,500,600,700,900,1e3,1.5e3,2e3,3e3,4e3,5e3,9e3,1.5e4,2.5e4,5e4,2e6],
    'WBTC':[0,2,3,7,10,100],
    'DAI': [0,50,80,100,200,400,560,700,800,1.3e3,2e3,3.5e3,5e3,6e3,9e3,1e4,2e4,3e4,4e4,6e4,8e4,1e5,2e5,6e6],
    'cDAI': [0,4e4,6e4,9e4,1e5,2.5e5,5e5,7e5,8e5,1e6,1.8e6,2.5e6,3.3e6,3.8e6,4.3e6,5e6,5.7e6,6e6,7e6,9e6,2e7]
}
ActBins ={
    # 'ETH':[-1,1e-6,4e-6,6e-6,1e-5,1.5e-5,3e-5,5e-5,7e-5,1e-4,2e-4,3e-4,5e-4,8e-4,1e-3,3e-3,6e-3,1e-2,5e-2,0.1,1,5e5],
    'USDC':[0,5e-7,2e-6,5e-6,7e-6,1e-5,1.5e-5,2.5e-5,4e-5,6e-5,9e-5,1.5e-4,2e-4,3e-4,5.5e-4,9e-4,2e-3,4e-3,7e-3,1.2e-2,1.5e-1],
    'USDT':[0,1e-6,2e-6,4e-6,8e-6,1e-5,2e-5,3e-5,5e-5,7e-5,1e-4,1.6e-4,3e-4,5e-4,8e-4,1.5e-3,2e-3,4e-3,7e-3,1.5e-2,50],
    'WBTC':[0,1e-6,2e-6,5e-6,7e-6,1e-5,2e-5,3e-5,5e-5,7e-5,1e-4,3e-4,4e-4,1e-3,3e-3,6e-3,1e-2,2e-2,1],
    'DAI': [0,1e-6,3e-6,4e-6,6e-6,1e-5,1.5e-5,2.5e-5,3e-5,5e-5,7e-5,9e-5,2e-4,4e-4,1e-3,2e-3,5e-3,8e-3,1e-2,3e-2,60],
    'cDAI': [0,4e-7,1e-6,2e-6,4e-6,6e-6,1e-5,1.5e-5,2e-5,2.5e-5,4e-5,7e-5,2e-4,4e-4,8e-4,2e-3,2.5e-3,6e-3,1e-2,1e-1,80]
    }

GasBins = {
    'ETH':[0,1,1.8,2.0,2.5,3.0,3.3,3.8,4.0,4.3,4.6,5.0,5.5,6,6.5,6.8,7.4,8,9,10,1e4],
    'USDC':[0,0.9,1,1.5,1.7,1.9,2.1,2.5,2.7,2.9,3.2,3.5,3.8,4,4.5,5,5.8,6.5,7.5,30],
    'USDT':[0,0.9,1.2,1.5,1.8,2,2.5,2.7,2.9,3.2,3.5,3.8,4.5,4.9,5.2,5.7,6.4,7,8,9,20],
    'WBTC':[0,1,1.5,2,2.5,3,3.5,4,4.5,4.8,5.5,6,6.6,7,8.5,10,40],
    'DAI': [0,0.6,1.2,1.5,1.8,2,2.3,2.6,3,3.4,3.6,3.9,4.2,4.8,5,6,7,10,21],
    'cDAI': [0,1,1.3,1.5,2,2.3,2.5,2.7,2.8,3,3.3,3.6,3.9,4,4.3,4.5,5,5.5,6.4,6.8,10]
    }