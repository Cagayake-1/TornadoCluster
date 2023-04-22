import matplotlib.pyplot as plt
from matplotlib import ticker
import Constant
from tqdm import tqdm
import numpy as np

plt.rcParams["font.sans-serif"]=['SimHei']
plt.rcParams["font.family"]=['Times New Roman']
plt.rcParams["axes.unicode_minus"]=False
tp = Constant.tornadoTxPath
ap = Constant.addressPath
otp = Constant.addressOuterTxPath
txCsvPath = tp + 'CSV/'


def txCntFigure():
    values = ['0.1ETH', '1ETH', '10ETH', '100ETH',  
          '100DAI', '1000DAI', '10000DAI', '100000DAI',
         '100USDC', '1000USDC',
         '100USDT', '1000USDT',
        '0.1WBTC', '1WBTC', '10WBTC',
        '5000cDAI', '50000cDAI', '500000cDAI', '5000000cDAI'
        ]
    txCnts = [48405, 103194, 91696, 61078,  
            420, 2062, 5790, 6681,
            335,1463, 
            770,2733,
            353,2569,2220,
            9,239,181,236]
    dCnts = [25981,52984,46411,30987,  
            234,1087,2959,3444, 
            50,572,  
            359,1167,
            142,1202,1033,
            5,118,87,114]
    wCnts = [22410,50208,45282,30090,
            184,973,2831,3237,
            184,890,
            410,1565,
            211,1367,1187,
            3,121,94,122]

    asCnts = [24396,39882,36775,16936,
            306,883,2292,1801,
            208,607,
            457,723,
            109,251,301,
            5,17,24,43]
    # 设置y轴label的位置
    y_pos = np.arange(0.42*1.03+0.2,(len(values)+0.42)*1.03+0.2,1.03)
    # 设置每组柱状的宽度
    total_heighth, n = (0.84)*1.03, 3
    heighth = total_heighth / n

    # 
    fig = plt.figure(figsize=(1,2))
    gs = fig.add_gridspec(1,2,width_ratios=(2,1))
    ax1 = fig.add_subplot(gs[0,0])
    ax2 = fig.add_subplot(gs[0,1],sharey=ax1)


    ax1.set_yticks(y_pos, labels=values)
    # 将中间的坐标轴、边框设为不可见
    ax1.spines.right.set_visible(False) #边框不可见
    ax2.spines.left.set_visible(False)
    ax2.tick_params(left=False,labelleft=False) #刻度和label不可见
    #绘制破折线
    d = .5  # proportion of vertical to horizontal extent of the slanted line
    kwargs = dict(marker=[(-1, -d), (1, d)], markersize=12,
                linestyle="none", color='k', mec='k', mew=1, clip_on=False)
    ax1.plot([1, 1], [1, 0], transform=ax1.transAxes, **kwargs)
    ax2.plot([0, 0], [0, 1], transform=ax2.transAxes, **kwargs)

    # 设置边框距离
    fig.subplots_adjust(top=0.99,bottom=0.035,left=0.05,right=0.99,wspace=0.03)

    # 绘制柱形图
    barh_tx = ax1.barh(y_pos - heighth, txCnts,  height=heighth, label='transactions')
    barh_d = ax1.barh(y_pos , dCnts, height=heighth, label='deposit')
    barh_w = ax1.barh(y_pos, wCnts, height=heighth, left=dCnts, label='withdraw')
    barh_as = ax1.barh(y_pos + heighth, asCnts, heighth, label='anonymity set')

    barh_tx2 = ax2.barh(y_pos - heighth, txCnts,  height=heighth, label='transactions')
    barh_d2 = ax2.barh(y_pos, dCnts, height=heighth, label='deposit')
    barh_w2 = ax2.barh(y_pos, wCnts, height=heighth, left=dCnts, label='withdraw')
    barh_as2 = ax2.barh(y_pos + heighth, asCnts, heighth, label='anonymity set')

    # ax1.set_xscale('log')
    ax1.set_xlim(0,10000,auto=True)
    ax2.set_xlim(15000,110000)
    ax1.set_ylim((0,20),auto=True)
    ax1.bar_label(barh_tx,fmt='{:,.0f}')
    ax1.bar_label(barh_d,fmt='{:,.0f}')
    ax1.bar_label(barh_w, labels=wCnts, fmt='{:,.0f}')
    ax1.bar_label(barh_as,fmt='{:,.0f}')

    ax2.bar_label(barh_tx2,fmt='{:,.0f}')
    ax2.bar_label(barh_d2,fmt='{:,.0f}')
    ax2.bar_label(barh_w2, labels=wCnts, fmt='{:,.0f}')
    ax2.bar_label(barh_as2,fmt='{:,.0f}')

    ax1.invert_yaxis()
    ax2.legend(loc='lower right')


    plt.savefig('txCounts.png')
    plt.show()

def ethCnt():
    values = ['0.1ETH', '1ETH', '10ETH', '100ETH']
    txCnts = [48405, 103194, 91696, 61078]
    dCnts = [25981,52984,46411,30987]
    wCnts = [22410,50208,45282,30090]
    asCnts = [24396,39882,36775,16936]
    # 设置y轴label的位置
    y_pos = np.arange(0.42*1.15+0.2,(len(values)+0.42)*1.15+0.2,1*1.15)
    # 设置每组柱状的宽度
    total_heighth, n = (0.84)*1.15, 3
    heighth = total_heighth / n

    # 
    fig,ax = plt.subplots(dpi=200)


    ax.set_yticks(y_pos, labels=values, fontsize=16, fontname='Times New Roman',fontweight='bold')
    # 将中间的坐标轴、边框设为不可见
    ax.spines.right.set_visible(False) #边框不可见
    ax.spines.top.set_visible(False)

    # 设置边框距离
    fig.subplots_adjust(top=0.99,bottom=0.115,left=0.14,right=0.920)

    # 绘制柱形图
    barh_tx = ax.barh(y_pos - heighth, txCnts,  height=heighth, label='Transactions',color='#2878b5')
    barh_d = ax.barh(y_pos , dCnts, height=heighth, label='Deposit',color='#9ac9db')
    barh_w = ax.barh(y_pos, wCnts, height=heighth, left=dCnts, label='Withdraw',color='#f8ac8c')
    barh_as = ax.barh(y_pos + heighth, asCnts, heighth, label='Anonymity Set',color='#c82423')

    
    ax.set_xlim(0,105000,auto=True)
    kwargs=dict(fontproperties='Times New Roman',fontstyle='italic',size=12,fontweight='demibold')
    ax.set_xticks(np.arange(0,105000,10000),labels=np.arange(0,105000,10000),**kwargs)
    # ax.ticklabel_format(style='sci',scilimits=(-1,2),axis='x')
    ax.set_ylim((0,5),auto=True)
    kwargs=dict(fontsize=12,fontname='Times New Roman',fontweight='demi')
    ax.bar_label(barh_tx,fmt='{:,.0f}',padding=2,**kwargs)
    ax.bar_label(barh_d,fmt='{:,.0f}',padding=-10,**kwargs)
    ax.bar_label(barh_w, labels=['{:,.0f}'.format(w) for w in wCnts],padding=2,**kwargs)
    ax.bar_label(barh_as,fmt='{:,.0f}',padding=2,**kwargs)

    #科学计数法
    formatter = ticker.ScalarFormatter(useMathText=True)
    formatter.set_scientific(True)
    formatter.set_powerlimits((0,0))
   
    ax.xaxis.set_major_formatter(formatter)


    ax.invert_yaxis()

    plt.savefig('ethCount.png')
    plt.show()

def typeCnt():
    values = ['ETH','DAI','USDC','USDT','WBTC','cDAI']
    txCnts = [48405+103194+91696+61078,  
            14953,
            335+1463, 
            770+2733,
            353+2569+2220,
            9+239+181+236]
    dCnts = [25981+52984+46411+30987,  
            234+1087+2959+3444, 
            50+572,  
            359+1167,
            142+1202+1033,
            5+118+87+114]
    wCnts = [22410+50208+45282+30090,
                7225,
                1074,
                1975,
                2765,
                340]
    asCnts = [24396+39882+36775+16936,
            306+883+2292+1801,
            208+607,
            457+723,
            109+251+301,
            5+17+24+43]
        # 设置y轴label的位置
    y_pos = np.arange(0.42*1.1+0.2,(len(values)+0.42)*1.1+0.2,1.1)
    # 设置每组柱状的宽度
    total_heighth, n = (0.84)*1.1, 3
    heighth = total_heighth / n

    # 
    fig = plt.figure(figsize=(1,2),dpi=180)
    gs = fig.add_gridspec(1,2,width_ratios=(4,1))
    ax1 = fig.add_subplot(gs[0,0])
    ax2 = fig.add_subplot(gs[0,1],sharey=ax1)


    ax1.set_yticks(y_pos, labels=values, fontsize=16, fontname='Times New Roman',fontweight='bold')
    # 将中间的坐标轴、边框设为不可见
    ax1.spines.right.set_visible(False) #边框不可见
    ax1.spines.top.set_visible(False)
    ax2.spines.left.set_visible(False)
    ax2.spines.right.set_visible(False)
    ax2.spines.top.set_visible(False)
    ax2.tick_params(left=False,labelleft=False) #刻度和label不可见
    #绘制破折线
    d = .5  # proportion of vertical to horizontal extent of the slanted line
    kwargs = dict(marker=[(-1, -d), (1, d)], markersize=12,
                linestyle="none", color='k', mec='k', mew=1, clip_on=False)
    ax1.plot( [1, 1],[0,0], transform=ax1.transAxes, **kwargs)
    ax2.plot([0, 0],[0,0], transform=ax2.transAxes, **kwargs)

    # 设置边框距离
    fig.subplots_adjust(top=0.99,bottom=0.05,left=0.07,right=0.98,wspace=0.03)

    # 绘制柱形图
    barh_tx = ax1.barh(y_pos - heighth, txCnts,  height=heighth, label='Transactions',color='#2878b5')
    barh_d = ax1.barh(y_pos , dCnts, height=heighth, label='Deposit',color='#9ac9db')
    barh_w = ax1.barh(y_pos, wCnts, height=heighth, left=dCnts, label='Withdraw',color='#f8ac8c')
    barh_as = ax1.barh(y_pos + heighth, asCnts, heighth, label='Anonymity Set',color='#c82423')

    barh_tx2 = ax2.barh(y_pos - heighth, txCnts,  height=heighth, label='Transactions',color='#2878b5')
    barh_d2 = ax2.barh(y_pos, dCnts, height=heighth, label='Deposit',color='#9ac9db')
    barh_w2 = ax2.barh(y_pos, wCnts, height=heighth, left=dCnts, label='Withdraw',color='#f8ac8c')
    barh_as2 = ax2.barh(y_pos + heighth, asCnts, heighth, label='Anonymity Set',color='#c82423')

    # ax1.set_xscale('log')
    ax1.set_xlim(0,16000,auto=True)
    kwargs=dict(fontproperties='Times New Roman',fontstyle='italic',size=12,fontweight='demibold')
    ax1.set_xticks(np.arange(0,16000,1500),labels=np.arange(0,0.16000,0.01500),**kwargs)
    
    ax2.set_xlim(110000,320000)
    ax2.set_xticks(np.arange(150000,350000,50000),labels=np.arange(150000,350000,50000),**kwargs)
    

    ax1.set_ylim((0,7),auto=True)
    kwargs=dict(fontsize=13,fontname='Times New Roman',fontweight='demi')
    ax1.bar_label(barh_tx,fmt='{:,.0f}',padding=2,**kwargs)
    ax1.bar_label(barh_d,fmt='{:,.0f}',padding=-10,**kwargs)
    ax1.bar_label(barh_w, labels=['{:,.0f}'.format(w) for w in wCnts],padding=2,**kwargs)
    ax1.bar_label(barh_as,fmt='{:,.0f}',padding=2,**kwargs)

    ax2.bar_label(barh_tx2,fmt='{:,.0f}',padding=2,**kwargs)
    ax2.bar_label(barh_d2,fmt='{:,.0f}',padding=-20,**kwargs)
    ax2.bar_label(barh_w2, labels=['{:,.0f}'.format(w) for w in wCnts],padding=2,**kwargs)
    ax2.bar_label(barh_as2,fmt='{:,.0f}',padding=2,**kwargs)

    ax1.invert_yaxis()
    ax2.legend(loc='lower right',prop={'family':'Times New Roman','size':17})

    #科学计数法
    formatter = ticker.ScalarFormatter(useMathText=True)
    formatter.set_scientific(True)
    formatter.set_powerlimits((0,3))
   
    # ax1.xaxis.set_major_formatter(formatter)
    ax2.xaxis.set_major_formatter(formatter)

    plt.savefig('typeCnt.png')
    plt.show()

def txCntByType():
    values = ['0.1ETH', '1ETH', '10ETH', '100ETH',  
          'DAI',
         'USDC',
         'USDT',
        'WBTC',
        'cDAI'
        ]
    txCnts = [48405, 103194, 91696, 61078,  
           14953,
            335+1463, 
            770+2733,
            353+2569+2220,
            9+239+181+236]
    dCnts = [25981,52984,46411,30987,  
            234+1087+2959+3444, 
            50+572,  
            359+1167,
            142+1202+1033,
            5+118+87+114]
    wCnts = [22410,50208,45282,30090,
            7225,
            1074,
            1975,
            2765,
            340]
    asCnts = [24396,39882,36775,16936,
            306+883+2292+1801,
            208+607,
            457+723,
            109+251+301,
        5+17+24+43]
     # 设置y轴label的位置
    y_pos = np.arange(0.42*1.0666+0.2,(len(values)+0.42)*1.0666+0.2,1.0666)
    # 设置每组柱状的宽度
    total_heighth, n = (0.84)*1.0666, 3
    heighth = total_heighth / n

    # 
    fig = plt.figure(figsize=(1,2))
    gs = fig.add_gridspec(1,2,width_ratios=(1,1))
    ax1 = fig.add_subplot(gs[0,0])
    ax2 = fig.add_subplot(gs[0,1],sharey=ax1)


    ax1.set_yticks(y_pos, labels=values, fontsize=18, fontname='Times New Roman',fontweight='bold')
    # 将中间的坐标轴、边框设为不可见
    ax1.spines.right.set_visible(False) #边框不可见
    ax1.spines.top.set_visible(False)
    ax2.spines.left.set_visible(False)
    ax2.spines.right.set_visible(False)
    ax2.spines.top.set_visible(False)
    ax2.tick_params(left=False,labelleft=False) #刻度和label不可见
    #绘制破折线
    d = .5  # proportion of vertical to horizontal extent of the slanted line
    kwargs = dict(marker=[(-1, -d), (1, d)], markersize=12,
                linestyle="none", color='k', mec='k', mew=1, clip_on=False)
    ax1.plot( [1, 1],[0,0], transform=ax1.transAxes, **kwargs)
    ax2.plot([0, 0],[0,0], transform=ax2.transAxes, **kwargs)

    # 设置边框距离
    fig.subplots_adjust(top=0.99,bottom=0.035,left=0.07,right=0.98,wspace=0.03)

    # 绘制柱形图
    barh_tx = ax1.barh(y_pos - heighth, txCnts,  height=heighth, label='Transactions',color='#2878b5')
    barh_d = ax1.barh(y_pos , dCnts, height=heighth, label='Deposit',color='#9ac9db')
    barh_w = ax1.barh(y_pos, wCnts, height=heighth, left=dCnts, label='Withdraw',color='#f8ac8c')
    barh_as = ax1.barh(y_pos + heighth, asCnts, heighth, label='Anonymity Set',color='#c82423')

    barh_tx2 = ax2.barh(y_pos - heighth, txCnts,  height=heighth, label='Transactions',color='#2878b5')
    barh_d2 = ax2.barh(y_pos, dCnts, height=heighth, label='Deposit',color='#9ac9db')
    barh_w2 = ax2.barh(y_pos, wCnts, height=heighth, left=dCnts, label='Withdraw',color='#f8ac8c')
    barh_as2 = ax2.barh(y_pos + heighth, asCnts, heighth, label='Anonymity Set',color='#c82423')

    # ax1.set_xscale('log')
    ax1.set_xlim(0,8000,auto=True)
    kwargs=dict(fontproperties='Times New Roman',fontstyle='italic',size=14,fontweight='demibold')
    ax1.set_xticks(np.arange(0,8000,1000),labels=np.arange(0,8000,1000),**kwargs)
    ax2.set_xlim(14000,110000)
    ax2.set_xticks(np.arange(15000,110000,10000),labels=np.arange(15000,110000,10000),**kwargs)
    ax1.set_ylim((0,10),auto=True)
    kwargs=dict(fontsize=15,fontname='Times New Roman',fontweight='demi')
    ax1.bar_label(barh_tx,fmt='{:,.0f}',padding=2,**kwargs)
    ax1.bar_label(barh_d,fmt='{:,.0f}',padding=-10,**kwargs)
    ax1.bar_label(barh_w, labels=['{:,.0f}'.format(w) for w in wCnts],padding=2,**kwargs)
    ax1.bar_label(barh_as,fmt='{:,.0f}',padding=2,**kwargs)

    ax2.bar_label(barh_tx2,fmt='{:,.0f}',padding=2,**kwargs)
    ax2.bar_label(barh_d2,fmt='{:,.0f}',padding=-20,**kwargs)
    ax2.bar_label(barh_w2, labels=['{:,.0f}'.format(w) for w in wCnts],padding=2,**kwargs)
    ax2.bar_label(barh_as2,fmt='{:,.0f}',padding=2,**kwargs)

    ax1.invert_yaxis()
    ax2.legend(loc='lower right',prop={'family':'Times New Roman','size':20})


    plt.savefig('txCounts.png')
    plt.show()
    
def daiCnt():
    values = ['100DAI', '1000DAI', '1w DAI', '10w DAI']
    txCnts = [420, 2062, 5790, 6681]
    dCnts = [234,1087,2959,3444]
    wCnts = [184,973,2831,3237]
    asCnts = [306,883,2292,1801]
     # 设置y轴label的位置
    y_pos = np.arange(0.42*1.15+0.2,(len(values)+0.42)*1.15+0.2,1*1.15)
    # 设置每组柱状的宽度
    total_heighth, n = (0.84)*1.15, 3
    heighth = total_heighth / n

    # 
    fig,ax = plt.subplots(dpi=200)


    ax.set_yticks(y_pos, labels=values, fontsize=18, fontname='Times New Roman',fontweight='bold')
    # 将中间的坐标轴、边框设为不可见
    ax.spines.right.set_visible(False) #边框不可见
    ax.spines.top.set_visible(False)

    # 设置边框距离
    fig.subplots_adjust(top=0.99,bottom=0.08,left=0.15,right=0.96)

    # 绘制柱形图
    barh_tx = ax.barh(y_pos - heighth, txCnts,  height=heighth, label='Transactions',color='#2878b5')
    barh_d = ax.barh(y_pos , dCnts, height=heighth, label='Deposit',color='#9ac9db')
    barh_w = ax.barh(y_pos, wCnts, height=heighth, left=dCnts, label='Withdraw',color='#f8ac8c')
    barh_as = ax.barh(y_pos + heighth, asCnts, heighth, label='Anonymity Set',color='#c82423')

    ax.set_xlim(0,7000,auto=True)
    kwargs=dict(fontproperties='Times New Roman',fontstyle='italic',size=14,fontweight='demibold')
    ax.set_xticks(np.arange(0,7100,1000),labels=np.arange(0,7100,1000),**kwargs)
   
    ax.set_ylim((0,5),auto=True)
    kwargs=dict(fontsize=14,fontname='Times New Roman',fontweight='demi')
    ax.bar_label(barh_tx,fmt='{:,.0f}',padding=2,**kwargs)
    ax.bar_label(barh_d,fmt='{:,.0f}',padding=-10,**kwargs)
    ax.bar_label(barh_w, labels=['{:,.0f}'.format(w) for w in wCnts],padding=2,**kwargs)
    ax.bar_label(barh_as,fmt='{:,.0f}',padding=2,**kwargs)

    ax.invert_yaxis()

    plt.savefig('daiCount.png')
    plt.show()

def usdcCnt():
    values = ['100USDC', '1000USDC']
    txCnts = [335,1463]
    dCnts = [150,572]
    wCnts = [184,890]
    asCnts = [208,607]
     # 设置y轴label的位置
    y_pos = np.arange(0.42*1.3+0.2,(len(values)+0.42)*1.3+0.2,1*1.3)
    # 设置每组柱状的宽度
    total_heighth, n = (0.84)*1.3, 3
    heighth = total_heighth / n

    # 
    fig,ax = plt.subplots(dpi=200)


    ax.set_yticks(y_pos, labels=values, fontsize=18, fontname='Times New Roman',fontweight='bold')
    # 将中间的坐标轴、边框设为不可见
    ax.spines.right.set_visible(False) #边框不可见
    ax.spines.top.set_visible(False)

    
    # 设置边框距离
    fig.subplots_adjust(top=0.99,bottom=0.1,left=0.18,right=0.97)

    # 绘制柱形图
    barh_tx = ax.barh(y_pos - heighth, txCnts,  height=heighth, label='Transactions',color='#2878b5')
    barh_d = ax.barh(y_pos , dCnts, height=heighth, label='Deposit',color='#9ac9db')
    barh_w = ax.barh(y_pos, wCnts, height=heighth, left=dCnts, label='Withdraw',color='#f8ac8c')
    barh_as = ax.barh(y_pos + heighth, asCnts, heighth, label='Anonymity Set',color='#c82423')

    ax.set_xlim(0,1500,auto=True)
    kwargs=dict(fontproperties='Times New Roman',fontstyle='italic',size=14,fontweight='demibold')
    ax.set_xticks(np.arange(0,1600,300),labels=np.arange(0,1600,300),**kwargs)
   
    ax.set_ylim((0,3),auto=True)
    kwargs=dict(fontsize=15,fontname='Times New Roman',fontweight='demi')
    ax.bar_label(barh_tx,fmt='{:,.0f}',padding=2,**kwargs)
    ax.bar_label(barh_d,fmt='{:,.0f}',padding=-10,**kwargs)
    ax.bar_label(barh_w, labels=['{:,.0f}'.format(w) for w in wCnts],padding=2,**kwargs)
    ax.bar_label(barh_as,fmt='{:,.0f}',padding=2,**kwargs)

    ax.invert_yaxis()

    plt.savefig('USDCCount.png')
    plt.show()

def usdtCnt():
    values = ['100USDT', '1000USDT']
    txCnts = [770,2733]
    dCnts = [359,1167]
    wCnts = [410,1565]
    asCnts = [457,723]
     # 设置y轴label的位置
    y_pos = np.arange(0.42*1.3+0.2,(len(values)+0.42)*1.3+0.2,1*1.3)
    # 设置每组柱状的宽度
    total_heighth, n = (0.84)*1.3, 3
    heighth = total_heighth / n

    # 
    fig,ax = plt.subplots(dpi=200)


    ax.set_yticks(y_pos, labels=values, fontsize=18, fontname='Times New Roman',fontweight='bold')
    # 将中间的坐标轴、边框设为不可见
    ax.spines.right.set_visible(False) #边框不可见
    ax.spines.top.set_visible(False)

    # 设置边框距离
    fig.subplots_adjust(top=0.99,bottom=0.1,left=0.18,right=0.97)

    # 绘制柱形图
    barh_tx = ax.barh(y_pos - heighth, txCnts,  height=heighth, label='Transactions',color='#2878b5')
    barh_d = ax.barh(y_pos , dCnts, height=heighth, label='Deposit',color='#9ac9db')
    barh_w = ax.barh(y_pos, wCnts, height=heighth, left=dCnts, label='Withdraw',color='#f8ac8c')
    barh_as = ax.barh(y_pos + heighth, asCnts, heighth, label='Anonymity Set',color='#c82423')

    ax.set_xlim(0,2900,auto=True)
    kwargs=dict(fontproperties='Times New Roman',fontstyle='italic',size=14,fontweight='demibold')
    ax.set_xticks(np.arange(0,2900,400),labels=np.arange(0,2900,400),**kwargs)
   
    ax.set_ylim((0,3),auto=True)
    kwargs=dict(fontsize=15,fontname='Times New Roman',fontweight='demi')
    ax.bar_label(barh_tx,fmt='{:,.0f}',padding=2,**kwargs)
    ax.bar_label(barh_d,fmt='{:,.0f}',padding=-10,**kwargs)
    ax.bar_label(barh_w, labels=['{:,.0f}'.format(w) for w in wCnts],padding=2,**kwargs)
    ax.bar_label(barh_as,fmt='{:,.0f}',padding=2,**kwargs)

    ax.invert_yaxis()

    plt.savefig('usdtCount.png')
    plt.show()

def wbtcCnt():
    values = ['0.1WBTC', '1WBTC', '10WBTC']
    txCnts = [353,2569,2220]
    dCnts = [142,1202,1033]
    wCnts = [211,1367,1187]
    asCnts = [109,251,301]
     # 设置y轴label的位置
    y_pos = np.arange(0.42*1.26+0.2,(len(values)+0.42)*1.26+0.2,1*1.26)
    # 设置每组柱状的宽度
    total_heighth, n = (0.84)*1.26, 3
    heighth = total_heighth / n

    # 
    fig,ax = plt.subplots(dpi=200)


    ax.set_yticks(y_pos, labels=values, fontsize=18, fontname='Times New Roman',fontweight='bold')
    # 将中间的坐标轴、边框设为不可见
    ax.spines.right.set_visible(False) #边框不可见
    ax.spines.top.set_visible(False)

    # 设置边框距离
    fig.subplots_adjust(top=0.99,bottom=0.085,left=0.17,right=0.935)

    # 绘制柱形图
    barh_tx = ax.barh(y_pos - heighth, txCnts,  height=heighth, label='Transactions',color='#2878b5')
    barh_d = ax.barh(y_pos , dCnts, height=heighth, label='Deposit',color='#9ac9db')
    barh_w = ax.barh(y_pos, wCnts, height=heighth, left=dCnts, label='Withdraw',color='#f8ac8c')
    barh_as = ax.barh(y_pos + heighth, asCnts, heighth, label='Anonymity Set',color='#c82423')

    ax.set_xlim(0,2600,auto=True)
    kwargs=dict(fontproperties='Times New Roman',fontstyle='italic',size=14,fontweight='demibold')
    ax.set_xticks(np.arange(0,2600,500),labels=np.arange(0,2600,500),**kwargs)
   
    ax.set_ylim((0,4),auto=True)
    kwargs=dict(fontsize=15,fontname='Times New Roman',fontweight='demi')
    ax.bar_label(barh_tx,fmt='{:,.0f}',padding=2,**kwargs)
    ax.bar_label(barh_d,fmt='{:,.0f}',padding=-10,**kwargs)
    ax.bar_label(barh_w, labels=['{:,.0f}'.format(w) for w in wCnts],padding=2,**kwargs)
    ax.bar_label(barh_as,fmt='{:,.0f}',padding=2,**kwargs)

    ax.invert_yaxis()

    plt.savefig('wbtcCount.png')
    plt.show()

def cdaiCnt():
    values = [ '5000cDAI', '5w cDAI', '50w cDAI', '500w cDAI']
    txCnts = [9,239,181,236]
    dCnts = [5,118,87,114]
    wCnts = [3,121,94,122]
    asCnts = [3,121,94,122]
     # 设置y轴label的位置
    y_pos = np.arange(0.42*1.15+0.2,(len(values)+0.42)*1.15+0.2,1*1.15)
    # 设置每组柱状的宽度
    total_heighth, n = (0.84)*1.15, 3
    heighth = total_heighth / n

    # 
    fig,ax = plt.subplots(dpi=200)


    ax.set_yticks(y_pos, labels=values, fontsize=18, fontname='Times New Roman',fontweight='bold')
    # 将中间的坐标轴、边框设为不可见
    ax.spines.right.set_visible(False) #边框不可见
    ax.spines.top.set_visible(False)

    # 设置边框距离
    fig.subplots_adjust(top=0.99,bottom=0.08,left=0.18,right=0.98)

    # 绘制柱形图
    barh_tx = ax.barh(y_pos - heighth, txCnts,  height=heighth, label='Transactions',color='#2878b5')
    barh_d = ax.barh(y_pos , dCnts, height=heighth, label='Deposit',color='#9ac9db')
    barh_w = ax.barh(y_pos, wCnts, height=heighth, left=dCnts, label='Withdraw',color='#f8ac8c')
    barh_as = ax.barh(y_pos + heighth, asCnts, heighth, label='Anonymity Set',color='#c82423')

    ax.set_xlim(0,250,auto=True)
    kwargs=dict(fontproperties='Times New Roman',fontstyle='italic',size=14,fontweight='demibold')
    ax.set_xticks(np.arange(0,250,40),labels=np.arange(0,250,40),**kwargs)
   
    ax.set_ylim((0,5),auto=True)
    kwargs=dict(fontsize=14,fontname='Times New Roman',fontweight='demi')
    ax.bar_label(barh_tx,fmt='{:,.0f}',padding=2,**kwargs)
    ax.bar_label(barh_d,fmt='{:,.0f}',padding=-8,**kwargs)
    ax.bar_label(barh_w, labels=['{:,.0f}'.format(w) for w in wCnts],padding=2,**kwargs)
    ax.bar_label(barh_as,fmt='{:,.0f}',padding=2,**kwargs)

    ax.invert_yaxis()

    plt.savefig('cdaiCount.png')
    plt.show()
# txCntByType()
# ethCnt()
# typeCnt()
# daiCnt()
# cdaiCnt()
# wbtcCnt()
usdcCnt()
# usdtCnt()