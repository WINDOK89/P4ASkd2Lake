#!/usr/bin/python3.5
from Credentials import Credentials
from ModuleStdTerminal import *
from PyLakeDriver import utc_to_string, string_to_utc,PyLakeDriver
from P4ASkd2LakeProcess import P4ASkd2LakeProcess
from ClassP4AOPCClientBuffer import P4AOPCClientBuffer
from ClassSKMPSendMail import SKMPSendMail

class P4ASkd2LakeClient(StandardTerminal):
    def __init__(self):
        StandardTerminal.__init__(self)
        self.Credential = Credentials()
        self.CommandMemory = DirMemory(["auto-create-tag","set-process-settings","show-process-settings","help","quit","show-lake","set-lake","start-process","stop-process","read-log","show-opc-settings","load-opc-settings"])

        self.OPCSettings=P4AOPCClientBuffer()
        self.OPCSettings.load_opc_settings()
        self.Skd2LakeProcess = P4ASkd2LakeProcess(self.Credential, self.OPCSettings)
        self.DirChoiceWindow = DisplayWindow(self.stdscr, self.InputWindow)
        top_panel(self.OutputWindow.panel)

        self.start_loop()


    def start_loop(self):
        while (self.cmd != "quit" or self.Skd2LakeProcess.IsRunning):
            key = self.InputWindow.get_char(message=" {} # Terminal >> ".format("Skd2Lake"),
                                            buf="".join(self.Buffer))
            self.manage_buffer(key)
            mvaddstr(0, 0, "   ")
            mvaddstr(0, 0, str(key))

        endwin()

    def manage_buffer(self, key):

        top_panel(self.OutputWindow.panel)
        bottom_panel(self.DirChoiceWindow.panel)
        self.OutputWindow.show_changes()

        if key == 9:
            """initialize the quit flag so we can use the menu again"""
            self.DirChoiceWindow.quitRequest = True

            """get possibbility list"""
            PosTag, lastSection = self.CommandMemory.get_next(
                self.Buffer[:self.InputWindow.PosCur - len(self.InputWindow.message)])

            """if only 1, we display it in input window"""
            if len(PosTag) == 1:
                NewPositionCursor = len(self.InputWindow.message) + len(
                    self.Buffer[:self.InputWindow.PosCur - len(self.InputWindow.message)] + list(PosTag[0])[
                                                                                            len(lastSection):])
                self.Buffer = self.Buffer[:self.InputWindow.PosCur - len(self.InputWindow.message)] + list(PosTag[0])[
                                                                                                      len(
                                                                                                          lastSection):] + self.Buffer[
                                                                                                                           self.InputWindow.PosCur - len(
                                                                                                                               self.InputWindow.message):]
                self.InputWindow.PosCur = NewPositionCursor

                """if more than 1 we show the panel with everything possible"""
            elif len(PosTag) > 1:
                self.DirChoiceWindow.clear_display()
                top_panel(self.DirChoiceWindow.panel)
                bottom_panel(self.OutputWindow.panel)
                for elt in PosTag:
                    self.DirChoiceWindow.add_text(" --> {}".format(elt), color=8, attribute=A_REVERSE)
                self.DirChoiceWindow.show_changes()

            else:
                pass
        elif key == KEY_BTAB:
            pass
        else:
            StandardTerminal.manage_buffer(self, key)

    def get_validation(self):
        response = ""
        while response != "y" and response != "n":
            wclear(self.InputWindow.window)
            waddstr(self.InputWindow.window, ' Confirm action ? (y/n) >> ', color_pair(6) + A_BOLD)
            response = wgetstr(self.InputWindow.window).decode('utf-8')

        return response

    def get_string(self, prefix=None):
        wclear(self.InputWindow.window)
        if prefix==None:
            prefix=" wintell >>"
        waddstr(self.InputWindow.window, prefix, color_pair(6) + A_BOLD)
        toreturn=wgetstr(self.InputWindow.window).decode('utf-8')
        wclear(self.InputWindow.window)
        return toreturn

    def get_integer(self, prefix=None):
        if prefix==None:
            prefix=" wintell >>"
        wclear(self.InputWindow.window)
        waddstr(self.InputWindow.window, prefix, color_pair(6) + A_BOLD)
        idlog = wgetstr(self.InputWindow.window).decode('utf-8')
        wclear(self.InputWindow.window)
        toreturn=int(idlog)
        return toreturn


    def cmd_manager(self):

        cmdlist = self.cmd.split(" :")
        if cmdlist[0] == "help":
            self.OutputWindow.clear_display()
            self.OutputWindow.add_text("HELP CONTENT", color=2, attribute=A_BOLD + A_UNDERLINE)
            self.OutputWindow.add_text("")
            self.OutputWindow.add_text("cmd 'quit':", color=3, attribute=A_UNDERLINE)
            self.OutputWindow.add_text("")
            self.OutputWindow.add_text("    --> exit terminal")
            self.OutputWindow.add_text("")

            self.OutputWindow.quitRequest = True

        elif cmdlist[0] == "read-log":
            self.OutputWindow.clear_display()
            self.OutputWindow.add_text("READ-LOG", color=2, attribute=A_BOLD + A_UNDERLINE)
            self.OutputWindow.add_text("")
            self.OutputWindow.add_text("Follow instruction:", color=3, attribute=A_UNDERLINE)
            self.OutputWindow.add_text("")
            if len(cmdlist) == 1:
                try:
                    wclear(self.InputWindow.window)
                    waddstr(self.InputWindow.window, ' LOG id >> ', color_pair(6) + A_BOLD)
                    idlog = wgetstr(self.InputWindow.window).decode('utf-8')
                    event = self.Skd2LakeProcess.MyLog.get_log_dict(idlog)
                    if len(event['time']) == 0:
                        self.OutputWindow.add_text("Log file empty")
                        raise ValueError

                except:
                    self.OutputWindow.add_text("Reading error or Not a valid index")
                else:
                    self.OutputWindow.add_text("the parameter are valid, reading starts")
                    self.OutputWindow.add_text("")
                    for i in range(len(event['time'])):
                        if event['type'][i] == "event":
                            self.OutputWindow.add_text("{} --> {}".format(event['time'][i], event['log'][i]), color=3)
                        elif event['type'][i] == "success":
                            self.OutputWindow.add_text("{} --> {}".format(event['time'][i], event['log'][i]), color=6)
                        elif event['type'][i] == "error":
                            self.OutputWindow.add_text("{} --> {}".format(event['time'][i], event['log'][i]), color=2)
                        else:
                            self.OutputWindow.add_text("{} --> {}".format(event['time'][i], event['log'][i]))
            elif len(cmdlist) == 3:
                try:
                    logid = int(cmdlist[1])
                    datems = string_to_utc(cmdlist[2])
                    event = self.Skd2LakeProcess.MyLog.get_log_dict(logid)
                    if len(event['time']) == 0:
                        self.OutputWindow.add_text("Log file empty")
                        raise ValueError
                    if datems < 1000:
                        raise ValueError
                except:
                    self.OutputWindow.add_text("--> not the right format cmd", color=2)
                else:
                    self.OutputWindow.add_text("the parameter are valid, reading starts")
                    self.OutputWindow.add_text("")
                    for i in range(len(event['time'])):
                        if datems <= string_to_utc(event['time'][i]):
                            if event['type'][i] == "event":
                                self.OutputWindow.add_text("{} --> {}".format(event['time'][i], event['log'][i]),
                                                           color=3)
                            elif event['type'][i] == "success":
                                self.OutputWindow.add_text("{} --> {}".format(event['time'][i], event['log'][i]),
                                                           color=6)
                            elif event['type'][i] == "error":
                                self.OutputWindow.add_text("{} --> {}".format(event['time'][i], event['log'][i]),
                                                           color=2)
                            else:
                                self.OutputWindow.add_text("{} --> {}".format(event['time'][i], event['log'][i]))

            else:
                self.OutputWindow.add_text("--> not the right format cmd", color=2)

            self.OutputWindow.quitRequest = True

        elif cmdlist[0] == "show-lake":
            self.OutputWindow.clear_display()
            self.OutputWindow.add_text("SHOW-LAKE", color=2, attribute=A_BOLD + A_UNDERLINE)
            self.OutputWindow.add_text("")
            self.OutputWindow.add_text("PyLakeDriver settings:", color=3, attribute=A_UNDERLINE)
            self.OutputWindow.add_text("")
            self.OutputWindow.add_text("    DataLake url --> {}".format(self.Credential.LakeInfo['url']))
            self.OutputWindow.add_text("    DataLake user --> {}".format(self.Credential.LakeInfo['user']))
            self.OutputWindow.add_text("    DataLake pass --> {}".format(self.Credential.LakeInfo['passwd']))
            self.OutputWindow.add_text("    DataLake default dir --> {}".format(self.Credential.LakeInfo['DefaultDir']))
            self.OutputWindow.quitRequest = True

        elif cmdlist[0] == "show-process-settings":
            self.OutputWindow.clear_display()
            self.OutputWindow.add_text("SHOW-PROCESS-SETTINGS", color=2, attribute=A_BOLD + A_UNDERLINE)
            self.OutputWindow.add_text("")
            self.OutputWindow.add_text("Process settings:", color=3, attribute=A_UNDERLINE)
            self.OutputWindow.add_text("")
            for key,val in self.Credential.ProcessParam.items():
                self.OutputWindow.add_text("    {} --> {}".format(key,val))
            self.OutputWindow.quitRequest = True

        elif cmdlist[0] == "set-process-settings":
            self.OutputWindow.clear_display()
            self.OutputWindow.add_text("SET-PROCESS-SETTINGS", color=2, attribute=A_BOLD + A_UNDERLINE)
            self.OutputWindow.add_text("")
            self.OutputWindow.add_text("Follow instructions:", color=3, attribute=A_UNDERLINE)
            self.OutputWindow.add_text("")
            if self.Skd2LakeProcess.IsRunning: #self.ISeeLakeProcess.IsRunning:
                self.OutputWindow.add_text("access denied: the process is currently running", color=2)
            else:
                try:
                    Delay=self.get_integer(" Delay >>")
                    NoData = self.get_integer(" No Data >>")

                except:
                    self.OutputWindow.add_text("An error has occured, maybe not an integer", color=3)
                else:
                    answer=self.get_validation()
                    if answer=="y":
                        self.Credential.ProcessParam["NODATA"] = NoData
                        self.Credential.ProcessParam["DELAY"] = Delay
                        self.Credential.store_process_param()
                        self.OutputWindow.add_text("Successfully set", color=6)
                    else:
                        self.OutputWindow.add_text("Not saved", color=3)

            self.OutputWindow.quitRequest = True

        elif cmdlist[0] == "auto-create-tag":
            self.OutputWindow.clear_display()
            self.OutputWindow.add_text("AUTO-CREATE-TAG", color=2, attribute=A_BOLD + A_UNDERLINE)
            self.OutputWindow.add_text("")
            self.OutputWindow.add_text("Follow instructions:", color=3, attribute=A_UNDERLINE)
            self.OutputWindow.add_text("")
            if self.Skd2LakeProcess.IsRunning: #self.ISeeLakeProcess.IsRunning:
                self.OutputWindow.add_text("access denied: the process is currently running", color=2)
            else:
                MyLake = PyLakeDriver(self.Credential.LakeInfo["user"], self.Credential.LakeInfo["passwd"],
                                           self.Credential.LakeInfo["url"],
                                           self.Credential.LakeInfo["DefaultDir"])
                try:
                    for key,val in self.OPCSettings.OPCProcessInfo["TAGDIC"].items():
                        self.OutputWindow.add_text("")
                        self.OutputWindow.add_text("--> tag {}".format(key), color=3)
                        for k,v in val.items():
                            if k=="PROPERTIES" or k=="ISACTIVE":
                                pass
                            else:
                                self.OutputWindow.add_text("    {} --> {}".format(k,v))
                        self.OutputWindow.add_text("--> do you want to insert this tag ?")
                        answer=self.get_validation()
                        if answer =="y":
                            if MyLake.create_tags(val["NAME"],val["TYPE"],val["UNIT"],val["DESCRIPTION"],val["TITLE"],TagDirParam=val["LAKEDIR"]):
                                self.OutputWindow.add_text("successfully created", color=6)
                            else:
                                self.OutputWindow.add_text("PyLakeDriver error", color=2)
                        else:
                            self.OutputWindow.add_text("not inserted")

                except:
                    self.OutputWindow.add_text("An error has occured, during handeling tag creation", color=3)
                else:
                    pass

            self.OutputWindow.quitRequest = True

        elif cmdlist[0] == "start-process":
            self.OutputWindow.clear_display()
            self.OutputWindow.add_text("START-PROCESS", color=2, attribute=A_BOLD + A_UNDERLINE)
            self.OutputWindow.add_text("")
            self.OutputWindow.add_text("starting info:", color=3, attribute=A_UNDERLINE)
            self.OutputWindow.add_text("")

            if self.Skd2LakeProcess.IsRunning and self.Skd2LakeProcess.KeepRunning == False:
                self.OutputWindow.add_text(
                    "The process is in stop sequence, wait until the process is stopped completely than try again",
                    color=2)
            elif self.Skd2LakeProcess.IsRunning and self.Skd2LakeProcess.KeepRunning:
                self.OutputWindow.add_text(
                    "The process is already running",
                    color=6)
            elif not (self.Skd2LakeProcess.IsRunning and self.Skd2LakeProcess.KeepRunning):
                self.Skd2LakeProcess = None
                self.Skd2LakeProcess = P4ASkd2LakeProcess(self.Credential, self.OPCSettings)
                self.Skd2LakeProcess.start()
                self.OutputWindow.add_text("process started")

            self.OutputWindow.quitRequest = True

        elif cmdlist[0] == "stop-process":
            self.OutputWindow.clear_display()
            self.OutputWindow.add_text("STOP-PROCESS", color=2, attribute=A_BOLD + A_UNDERLINE)
            self.OutputWindow.add_text("")
            self.OutputWindow.add_text("stopping info:", color=3, attribute=A_UNDERLINE)
            self.OutputWindow.add_text("")

            if self.Skd2LakeProcess.IsRunning and self.Skd2LakeProcess.KeepRunning == False:
                self.OutputWindow.add_text(
                    "The process is in stop sequence, wait until the process is stopped completely than try again",
                    color=2)
            elif self.Skd2LakeProcess.IsRunning and self.Skd2LakeProcess.KeepRunning:
                self.Skd2LakeProcess.KeepRunning = False
                self.OutputWindow.add_text(
                    "stop sequence in process",
                    color=6)
            elif not (self.Skd2LakeProcess.IsRunning and self.Skd2LakeProcess.KeepRunning):
                self.OutputWindow.add_text("process already stopped")

            self.OutputWindow.quitRequest = True

        elif cmdlist[0] == "quit":
            self.OutputWindow.clear_display()
            self.OutputWindow.add_text("QUIT", color=2, attribute=A_BOLD + A_UNDERLINE)
            self.OutputWindow.add_text("")
            self.OutputWindow.add_text("cannot quit if process is running", color=2, attribute=A_UNDERLINE)
            self.OutputWindow.add_text("")
            self.OutputWindow.quitRequest = True

        elif cmdlist[0] == "show-opc-settings":
            self.OutputWindow.clear_display()
            self.OutputWindow.add_text("SHOW-OPC-SETTINGS", color=2)
            self.OutputWindow.add_text("")
            self.OutputWindow.add_text("OPC settings:", color=3)
            self.OutputWindow.add_text("")
            for key, value in sorted(self.OPCSettings.OPCProcessInfo.items()):
                if type(value) == list:
                    self.OutputWindow.add_text("    {} :".format(key), color=5)
                    for i, elt in enumerate(value):
                        self.OutputWindow.add_text("        ({}) --> {}".format(i, elt))
                elif type(value) == dict:
                    self.OutputWindow.add_text("    {} :".format(key), color=5)
                    for k, v in sorted(value.items()):
                        if type(v) == dict:
                            self.OutputWindow.add_text("        {} :".format(k), color=6)
                            for k2, v2 in sorted(v.items()):
                                self.OutputWindow.add_text("            ({}) --> {}".format(k2, v2))

                        else:
                            self.OutputWindow.add_text("        ({}) --> {}".format(k, v))
                else:
                    self.OutputWindow.add_text("    {} --> {}".format(key, value), color=5)

            self.OutputWindow.quitRequest = True

        elif cmdlist[0] == "load-opc-settings":
            self.OutputWindow.clear_display()
            self.OutputWindow.add_text("LOAD-OPC-SETTINGS", color=2)
            self.OutputWindow.add_text("")
            self.OutputWindow.add_text("OPC settings:", color=3)
            self.OutputWindow.add_text("")
            if self.Skd2LakeProcess.IsRunning: #self.ISeeLakeProcess.IsRunning:
                self.OutputWindow.add_text("access denied: the process is currently running", color=2)
            else:
                self.OPCSettings=None
                self.OPCSettings=P4AOPCClientBuffer()
                if self.OPCSettings.load_opc_settings():
                    self.OutputWindow.add_text("--> successfully loaded", color=6)
                else:
                    self.OutputWindow.add_text("--> incorrectly loaded", color=2)

            self.OutputWindow.quitRequest = True

        elif cmdlist[0] == "set-lake":
            self.OutputWindow.clear_display()
            self.OutputWindow.add_text("SET-LAKE", color=2, attribute=A_BOLD + A_UNDERLINE)
            self.OutputWindow.add_text("")
            self.OutputWindow.add_text("Follow instruction:", color=3, attribute=A_UNDERLINE)
            self.OutputWindow.add_text("")

            if self.Skd2LakeProcess.IsRunning: #self.ISeeLakeProcess.IsRunning:
                self.OutputWindow.add_text("access denied: the process is currently running", color=2)
            else:

                dlakeurl = self.get_string(" DMLake url >>")
                self.OutputWindow.add_text("    DataLake url --> {}".format(dlakeurl))

                dlakeuser =self.get_string(" DMLake user >>")
                self.OutputWindow.add_text("    DataLake user --> {}".format(dlakeuser))

                dlakepass = self.get_string(" DMLake pass >>")
                self.OutputWindow.add_text("    DataLake pass --> {}".format(dlakepass))

                dlakeddir = self.get_string(" DMLake default dir >>")
                self.OutputWindow.add_text("    DataLake default dir --> {}".format(dlakeddir))

                waddstr(self.InputWindow.window, ' Validation (y/n) >> ', color_pair(6) + A_BOLD)
                answer = wgetstr(self.InputWindow.window).decode('utf-8')
                if answer == "y":
                    self.Credential.LakeInfo['url'] = dlakeurl
                    self.Credential.LakeInfo['user'] = dlakeuser
                    self.Credential.LakeInfo['passwd'] = dlakepass
                    self.Credential.LakeInfo['DefaultDir'] = dlakeddir
                    self.Credential.store_lake()
                    self.OutputWindow.clear_display()
                    self.OutputWindow.add_text("SET-LAKE", color=2, attribute=A_BOLD + A_UNDERLINE)
                    self.OutputWindow.add_text("")
                    self.OutputWindow.add_text("Set PyLakeDriver succesfully", color=3, attribute=A_UNDERLINE)
                    self.OutputWindow.add_text("")
                    # if not (self.ISeeLakeProcess.IsRunning and self.ISeeLakeProcess.KeepRunning):
                    #     self.ISeeLakeProcess = None
                    #     self.ISeeLakeProcess = P4AISeeCollectorProcess(MyLakeParam=self.Credential.LakeInfo,
                    #                                                    MyISeeParam=self.Credential.ISeeInfo)
                else:
                    self.OutputWindow.clear_display()
                    self.OutputWindow.add_text("SET-LAKE", color=2, attribute=A_BOLD + A_UNDERLINE)
                    self.OutputWindow.add_text("")
                    self.OutputWindow.add_text("ABORTION", color=3, attribute=A_UNDERLINE)
                    self.OutputWindow.add_text("")

            self.OutputWindow.quitRequest = True

        else:
            self.OutputWindow.clear_display()
            self.OutputWindow.add_text("    !! WRONG FORMAT, CONSULT HELP !!", color=2)

            """to allow again the display object to run"""
            self.OutputWindow.quitRequest = True

if __name__=="__main__":

    try:
        a=P4ASkd2LakeClient()
    except Exception as ex:
        SKMPSendMail(message="ISee-Lake process admin tool has been stopped",subject="ISeeLakeLink info",nameShow="ISeeLake Watchdog")
        print(ex)