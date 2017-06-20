from threading import Thread
from PyLakeDriver import *
from ClassSKMPSendMail import *
from ClassP4AWecLogManager import *
from ClassP4AOPCClientBuffer import P4AOPCClientBuffer
import os
import pickle
import time

class P4ASkd2LakeProcess(Thread):
    def __init__(self, Credentials, OpcSettings):
        self.Credentials=Credentials
        self.MyLake = PyLakeDriver(self.Credentials.LakeInfo["user"], self.Credentials.LakeInfo["passwd"], self.Credentials.LakeInfo["url"],
                                   self.Credentials.LakeInfo["DefaultDir"])
        self.IsRunning=False
        self.KeepRunning=False
        self.OPCSettings=OpcSettings
        self.MyLog = P4ALogManager("Skd2Lake")
        Thread.__init__(self)

    def run(self):
        self.IsRunning=True
        self.KeepRunning=True
        self.MyLog.write_log("start process")
        cpt=0
        while self.KeepRunning:
            try:
                if cpt%self.Credentials.ProcessParam["DELAY"]==0:
                    FileList=sorted(os.listdir("./data"))
                    self.MyLog.write_log("{} files were found".format(len(FileList)))
                    for filename in FileList:
                        if len(filename)==39:

                            self.MyLog.write_log("file --> {}".format(filename))
                            TempDic=self.get_pick_content(filename)
                            if TempDic==False:
                                self.MyLog.write_log("problem retrieving data from file", "error")
                                os.remove("./data/" + filename)
                            else:
                                self.MyLog.write_log("data retrieved", "success")
                                for key in TempDic.keys():
                                    LakePath=self.OPCSettings.OPCProcessInfo["TAGDIC"][key]["LAKEDIR"]
                                    if len(LakePath)==0:
                                        self.MyLog.write_log("No lake path set for {}".format(key), "error")
                                    else:
                                        self.MyLog.write_log("trying to insert {} at lake directory {}".format(key,LakePath))
                                        if self.MyLake.add_values(key,TempDic[key],TagDirParam=LakePath,DefConFormat="utc"):
                                            self.MyLog.write_log("successfully inserted", "success")

                                        else:
                                            self.MyLog.write_log("failed to insert", "error")
                                            flag=False

                                os.remove("./data/" + filename)

                        elif filename=="None __ None.pick":
                            self.MyLog.write_log("empty data file", "error")
                            os.remove("./data/"+filename)
                        else:
                            pass

            except Exception as ex:
                self.MyLog.write_log(str(ex), "error")

            cpt += 1
            time.sleep(1)   #self.Credentials.ProcessParam["DELAY"]

        self.IsRunning=False

    def get_pick_content(self,filename):
        try:

            with open("./data/"+filename, 'rb') as f:
                mp = pickle.Unpickler(f)
                RetList = mp.load()

        except:
            return False

        else:
            return RetList
