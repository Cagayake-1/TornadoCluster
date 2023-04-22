import logging


def createLog(logFile):
    # 第一步，创建一个logger
    logger = logging.getLogger(logFile)
    logger.setLevel(logging.DEBUG)

    # 第二步，创建一个handler，用于写入Info日志文件
    logfile = './Logs/'+logFile+'Info.txt'
    info_fh = logging.FileHandler(logfile, mode='a')
    info_fh.setLevel(logging.INFO)

    # 第三步，定义handler的输出格式
    fileFormatter = logging.Formatter("%(message)s")
    info_fh.setFormatter(fileFormatter)

    # 第四步，将logger添加到handler里面
    logger.addHandler(info_fh)

    return logger
