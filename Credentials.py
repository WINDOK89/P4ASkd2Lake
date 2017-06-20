import pickle

class Credentials():
    def __init__(self):
        self.LakeInfo={"user":"", "passwd":"", "url":"", "DefaultDir":""}
        self.load_lake()
        self.ProcessParam={"DELAY":60, "NODATA":20}
        self.load_process_param()

    def load_lake(self):
        try:

            with open('lake.pick', 'rb') as f:
                mp = pickle.Unpickler(f)
                self.LakeInfo = mp.load()

        except:
            return False

        else:
            return True

    def store_lake(self):
        try:
            with open('lake.pick', 'wb') as f:
                mp = pickle.Pickler(f)
                mp.dump(self.LakeInfo)

        except:
            return False

        else:
            return True

    def load_process_param(self):
        try:

            with open('process.pick', 'rb') as f:
                mp = pickle.Unpickler(f)
                self.ProcessParam = mp.load()

        except:
            return False

        else:
            return True

    def store_process_param(self):
        try:
            with open('process.pick', 'wb') as f:
                mp = pickle.Pickler(f)
                mp.dump(self.ProcessParam)

        except:
            return False

        else:
            return True