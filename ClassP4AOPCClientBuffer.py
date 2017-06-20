import pickle

class P4AOPCClientBuffer():
    def __init__(self):
        self.OPCProcessInfo={"SERVER":"", "DELAY":1,"PATH":None,"TAGLIST":[],"ACTIVETAGLIST":[],"TAGDIC":{},"FTPDELAY":600}

    def load_opc_settings(self):
        try:

            with open('./data/OPCSettingsInfo.pick', 'rb') as f:
                mp = pickle.Unpickler(f)
                self.OPCProcessInfo = mp.load()

        except:
            return False

        else:
            return True

    def store_opc_settings(self):
        try:
            with open('./data/OPCSettingsInfo.pick', 'wb') as f:
                mp = pickle.Pickler(f)
                mp.dump(self.OPCProcessInfo)

        except:
            return False

        else:
            return True

if __name__=="__main__":
    a=P4AOPCClientBuffer()
    
