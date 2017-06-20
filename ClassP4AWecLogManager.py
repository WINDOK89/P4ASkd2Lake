import os
from PyLakeDriver import get_utc_now
import csv

class P4ALogManager():
    def __init__(self, IpWec):
        IpWecSplit=IpWec.split(".")
        self.LogPath="./log"
        self.LogBaseName="LOG-"+"_".join(IpWecSplit)+"_"
        self.FullLogPath=self.LogPath+"/"+self.LogBaseName

    def write_log(self, message, event_type="event"):
        with open(self.FullLogPath+get_utc_now(ReturnFormat="string")[:10],'a') as f:
            f.write(get_utc_now(ReturnFormat="string")+";"+message+";"+event_type+"\n")

    def check_how_much(self):

        RetList = os.listdir(self.LogPath)
        RelevantRetList=[]
        for elt in sorted(RetList):
            if elt.startswith(self.LogBaseName):
                RelevantRetList.append(elt)

        if len(RelevantRetList)>15:
            for elt in RelevantRetList[:len(RelevantRetList)-15]:
                os.remove(self.LogPath+"/"+elt)

    def get_log_dict(self, index):
        RetDic={'time':[], 'log':[], 'type':[]}
        RetList = os.listdir(self.LogPath)
        RelevantRetList = []
        for elt in sorted(RetList, reverse=True):
            if elt.startswith(self.LogBaseName):
                RelevantRetList.append(elt)

        try:
            FileName=self.LogPath+"/"+RelevantRetList[int(index)]
            with open(FileName, 'r', encoding='latin-1') as f:
                reader=csv.reader(f, delimiter=";")
                for i, elt in enumerate(reader):
                    RetDic['time'].append(elt[0])
                    RetDic['log'].append(elt[1])
                    RetDic['type'].append(elt[2])
        except:
            return RetDic
        else:
            return RetDic




if __name__=="__main__":
    pass
    """a=P4ALogManager("10.32.22.73")
    a.write_log("test","error")
    a.check_how_much()
    b=a.get_log_dict("2")
    for i in range(len(b['time'])):
        print("{} __ {} __ {}".format(b['time'][i], b['log'][i], b['type'][i]))"""

