import datetime  # for date/time formatting
import time  # need of time.mktime() to return utc from datetime object
import requests  # Module for http request
import json  # need json.dumps() for post request

"""settings to avoid raise of InsecureRequestWarning"""
from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


def utc_to_datetime(utcTime):
    """
    This function convert utc time into datetime.datetime object

    :param utcTime:
        (int) or (float) - the utc time to convert
    :return:
        converted datetime object if utcTime has the right format
        False if utcTime is not a int/float
    """

    if type(utcTime) == int or type(utcTime) == float:
        return datetime.datetime.fromtimestamp(utcTime)
    else:
        return False


def utc_to_string(utcTime):
    """
    This function convert utc time into string (converter str datetime object

    :param utcTime:
        (int) or (float) - the utc time to convert
    :return:
        (str) - the converted time
        False if utcTime is not (int) or (float)
    """

    if type(utcTime) == int or type(utcTime) == float:
        return str(datetime.datetime.fromtimestamp(utcTime))
    else:
        return False


def get_utc_now(ReturnFormat="utc"):
    """
    This function returns the actual time

    :param ReturnFormat:
        'utc', 'datetime' or 'string'
    :return:
        (int) if ReturnFormat='utc'
        (datetime) if ReturnFormat='datetime'
        (str(datetime)) if ReturnFormat='string'
        False if ReturnFormat is different
    """

    if ReturnFormat == "datetime":
        return datetime.datetime.utcnow()

    elif ReturnFormat == "string":
        return str(datetime.datetime.utcnow())[:19]

    elif ReturnFormat == "utc":
        return time.mktime(datetime.datetime.utcnow().timetuple())

    else:
        return False


def string_to_datetime(StringTime, DefConFormat="%Y-%m-%d %H:%M:%S"):
    """
    This function convert string into datetime object according to given format

    :param StringTime:
        The string to convert, must be fit with format given
    :param DefConFormat:
        The format of StringTime, according to: https://docs.python.org/2/library/datetime.html
        default value: '%Y-%m-%d %H:%M:%S'
    :return:
        (datetime) if conversion ok
        False if an error is detected
    """

    if type(StringTime) == str:
        try:
            RetValue = datetime.datetime.strptime(StringTime, DefConFormat)
        except:
            return False
        else:
            return RetValue


def string_to_utc(StringTime, ReturnFormat="ms", DefConFormat="%Y-%m-%d %H:%M:%S"):
    """
    This function converts string into utc time

    :param StringTime:
        The string object to convert
    :param ReturnFormat:
        'ms' --> return milliseconds
        's' --> return second
    :param DefConFormat:
        The format of StringTime, according to: https://docs.python.org/2/library/datetime.html
        default value: '%Y-%m-%d %H:%M:%S'default value: '%Y-%m-%d %H:%M:%S'
    :return:
        (int) object
    """
    #RetValue = time.mktime(datetime.datetime.strptime(StringTime, DefConFormat).timetuple())
    if type(StringTime) == str:
        try:
            RetValue = time.mktime(datetime.datetime.strptime(StringTime, DefConFormat).timetuple())
            if ReturnFormat == "ms":
                RetValue = RetValue * 1000
            elif ReturnFormat == "s":
                pass
            else:
                raise ValueError("error")
        except:
            return False
        else:
            return RetValue


class PyLakeDriver():
    """
    this class is a driver to connect and manage data on Data Maestro Lake historian
    """

    def __init__(self, user, passwd, urlIp, DefaultDir="wintell/test/test2", timeout=5):
        """
        The constructor of the class

        :param user:
            User name for DMLake Login
        :param passwd:
            User password for DMLake login
        :param urlIp:
            DMLake IP address
        :param DefaultDir:
            Default directory, all functions will work with this doirectory unless it is specified otherwise

        :argument Session:
            requests.Session object
            authentification done with :param 'user' and 'passwd'
        :argument UrlIp:
            'https://'+ :param urlIp +'/tags/' --> DMLake address
        :argument DefaultDir:
            = :param DefaultDir
        """

        self.Session = requests.Session()
        self.Session.auth = (user, passwd)
        self.UrlIp = "https://{}/tags/".format(urlIp)
        self.DefaultDir = DefaultDir
        self.timeout=timeout

    def create_directory(self, DirName):
        """
        This method create a new directory at root wintell/

        :param DirName:
            The name of the created directory
        :return:
            True if OK
            False if not ok
        """

        try:
            parameter = {'directory': DirName}
            url = "{}{}".format(self.UrlIp, "createTagDirectories/")
            ReqResp = self.Session.get(url, verify=False, params=parameter, timeout=self.timeout)
            if ReqResp.status_code != 200:
                raise ValueError("error")

        except:
            return False

        else:
            return True

    def create_tags(self, TagName, TagType="double-float", TagUnit="", TagDescription="", TagTitle="",
                    TagDirParam=None):
        """
        This function create in a new tag

        :param TagName:
            (string) The name of the tag
        :param TagType:
            'double-float' or 'string', an exception is raised if not
            default value 'double-float'
        :param TagUnit:
            (string) the unit of the tag
            default value: ''
        :param TagDescription:
            (string) description of the tag
            default value: ''
        :param TagTitle:
            (string) Title of the tag
            default value: ''
        :param TagDirParam:
            (string) the directory where the tag must be inserted
            default value: self.DefaultDir (default dirrectory from contructor)
        :return:
            True if ok
            False if not
        """

        try:

            if TagType == "double-float" or TagType == "string":
                pass

            else:
                raise ValueError("error")

            if TagDirParam == None:
                TagDir = self.DefaultDir

            else:
                TagDir = TagDirParam

            parameter = {'directory': TagDir}
            payload = [
                {'name': TagName, 'type': TagType, 'unit': TagUnit, 'description': TagDescription, 'title': TagTitle}]
            url = "{}{}".format(self.UrlIp, "createTags/")
            ReqResp = self.Session.post(url, params=parameter, data=json.dumps(payload), verify=False, timeout=self.timeout)
            if ReqResp.status_code != 200:
                raise ValueError("error")

        except:
            return False

        else:
            return True

    def add_value(self, TagName, Time, Value, TagDirParam=None, DefConFormat="%Y-%m-%d %H:%M:%S"):
        """
        This class method add one value to one tag

        :param TagName:
            (string) the tag to attribute value
        :param Time:
            (string) or (int) the time related to the value
        :param Value:
            (float) or (string) depending on declaration, the value to add
        :param TagDirParam:
            (string) directory of the tag
            default value: self.DefaultDir
        :param DefConFormat:
            (string) format for string to timestamps conversion
            if = 'utc', no conversion is made and the parameter is sent directly
            Default value: '%Y-%m-%d %H:%M:%S', example: 2015-01-01 01:01:01
        :return:
            True if ok
            False if error
        """

        try:
            if TagDirParam == None:
                TagDir = self.DefaultDir

            else:
                TagDir = TagDirParam

            if DefConFormat == "utc":
                InputTime = int(Time)
            else:
                InputTime = int(string_to_utc(Time, DefConFormat=DefConFormat))

            url = "{}{}".format(self.UrlIp, "addTagValue/")
            parameter = {'tag': "{}/{}".format(TagDir, TagName), 'time': InputTime, 'value': Value}
            ReqResp = self.Session.get(url, verify=False, params=parameter, timeout=self.timeout)
            if ReqResp.status_code != 200:
                raise ValueError("error")
        except:
            return False
        else:
            return True

    def add_values(self, TagName, ValuesList, TagDirParam=None, DefConFormat="%Y-%m-%d %H:%M:%S"):
        """
        This class method add several values to one tag

        :param TagName:
            (string) the tag to attribute value
        :param ValuesList:
            (list) python list, example: [[time1,value1],[time2,value2],...]
        :param TagDirParam:
            (string) directory of the tag
            default value: self.DefaultDir
        :param DefConFormat:
            (string) format for string to timestamps conversion
            if = 'utc', no conversion is made and the parameter is sent directly
            Default value: '%Y-%m-%d %H:%M:%S', example: 2015-01-01 01:01:01
        :return:
            True if ok
            False if error
        """

        try:
            if TagDirParam == None:
                TagDir = self.DefaultDir

            else:
                TagDir = TagDirParam

            if DefConFormat == "utc":
                pass
            else:
                for elt in ValuesList:
                    elt[0] = int(string_to_utc(elt[0], DefConFormat=DefConFormat))

            url = "{}{}".format(self.UrlIp, "addTagValues/")
            payload = []
            for elt in ValuesList:
                payload.append([elt[0], [elt[1]]])

            parameter = {'tag': "{}/{}".format(TagDir, TagName)}
            ReqResp = self.Session.post(url, data=json.dumps(payload), verify=False, params=parameter, timeout=self.timeout)
            if ReqResp.status_code != 200:
                raise ValueError("error")
        except:
            return False
        else:
            return True

    def get_values(self, TagName, StartTimeParam, EndTimeParam, TagDirParam=None, DefConFormat="%Y-%m-%d %H:%M:%S"):
        """
        This class method return list of values from one tag

        :param TagName:
            (string) the tag we want values from
        :param StartTimeParam:
            (string) or (int) the values returned will start from this parameter
        :param EndTimeParam:
            (string) or (int) the values returned will stop from this parameter
        :param TagDirParam:
            (string) directory of the tag
            default value: self.DefaultDir
        :param DefConFormat:
            (string) format for string to timestamps conversion
            if = 'utc', no conversion is made and the parameter is sent directly
            Default value: '%Y-%m-%d %H:%M:%S', example: 2015-01-01 01:01:01
        :return:
            (list) python list, example [[time1,value1],[time2,value2]]
            False if an error has occured
        """
        try:
            if TagDirParam == None:
                TagDir = self.DefaultDir

            else:
                TagDir = TagDirParam

            if DefConFormat == "utc":
                StartTime = int(StartTimeParam)
                EndTime = int(EndTimeParam)
            else:
                StartTime = int(string_to_utc(StartTimeParam, DefConFormat=DefConFormat))
                EndTime = int(string_to_utc(EndTimeParam, DefConFormat=DefConFormat))

            url = "{}{}".format(self.UrlIp, "getRawTagValues/")
            parameter = {'tag': "{}/{}".format(TagDir, TagName), 'startTime': StartTime, 'endTime': EndTime}
            ReqResp = self.Session.get(url, verify=False, params=parameter, timeout=self.timeout)
            if ReqResp.status_code != 200:
                raise ValueError("error")
            RetList = []
            for elt in ReqResp.json():
                RetList.append([elt[0], elt[1][0]])
        except:
            return False
        else:
            return RetList

    def delete_tags(self, TagNameList, TagDirParam=None):
        """
        This class method deletes tags and its values

        :param TagNameList:
            (list) list of (string) beeing the tags names to be deleted, example: ['tag1','tag2']
        :param TagDirParam:
            string) directory of the tag
            default value: self.DefaultDir
        :return:
            True if ok
            False if error
        """

        try:
            if TagDirParam == None:
                TagDir = self.DefaultDir

            else:
                TagDir = TagDirParam

            url = "{}{}".format(self.UrlIp, "deleteTags/")
            payload = []
            for elt in TagNameList:
                payload.append("{}/{}".format(TagDir, elt))
            ReqResp = self.Session.post(url, data=json.dumps(payload), verify=False, timeout=self.timeout)
            if ReqResp.status_code != 200:
                raise ValueError("error")
        except:
            return False
        else:
            return True

    def truncate_tags(self, TagNameList, FromTimeParam, TagDirParam=None, DefConFormat="%Y-%m-%d %H:%M:%S"):
        """
        This class method deletes data from a given time to the last inserted value for several tags

        :param TagNameList:
            (list) the list of tags we want to apply the fucntion, example: ['tag1','tag2']
        :param FromTimeParam:
            (string) or (int) the time it starts to delete from
        :param TagDirParam:
            string) directory of the tag
            default value: self.DefaultDir
        :param DefConFormat:
            (string) format for string to timestamps conversion
            if = 'utc', no conversion is made and the parameter is sent directly
            Default value: '%Y-%m-%d %H:%M:%S', example: 2015-01-01 01:01:01
        :return:
            True if ok
            False if error
        """
        try:
            if TagDirParam == None:
                TagDir = self.DefaultDir

            else:
                TagDir = TagDirParam

            if DefConFormat == "utc":
                FromTime = int(FromTimeParam)
            else:
                FromTime = int(string_to_utc(FromTimeParam, DefConFormat=DefConFormat))

            parameter = {'time': FromTime}
            payload = []
            for elt in TagNameList:
                payload.append("{}/{}".format(TagDir, elt))

            url = "{}{}".format(self.UrlIp, "truncateTags/")
            ReqResp = self.Session.post(url, params=parameter, data=json.dumps(payload), verify=False, timeout=self.timeout)
            if ReqResp.status_code != 200:
                raise ValueError("error")
        except:
            return False
        else:
            return True

    def get_tag_list(self, TagDirParam=None):
        """
        This class method returns a list of tags inside a given directory

        :param TagDirParam:
            (string) directory of the tag
            default value: self.DefaultDir
        :return:
            False if error
            (list) of (string) with tags names
        """

        try:
            if TagDirParam == None:
                TagDir = self.DefaultDir

            else:
                TagDir = TagDirParam

            parameter = {'tagDirectory': TagDir}
            url = "{}{}".format(self.UrlIp, "getTags/")
            ReqResp = self.Session.get(url, verify=False, params=parameter, timeout=self.timeout)
            if ReqResp.status_code != 200:
                raise ValueError("error")
            ReturnList = []
            for elt in ReqResp.json():
                ReturnList.append(elt.split(TagDir + "/")[1])
        except:
            return False
        else:
            return ReturnList

    def get_tag_directories(self, TagDirParam=None):
        """
        This class method returns the list of tag directories

        :param TagDirParam:
            (string) directory of the tag
            default value: self.DefaultDir
        :return:
            False if error
            (list) of (string) with directory names
        """
        try:
            if TagDirParam == None:
                TagDir = "wintell/"

            else:
                TagDir = TagDirParam
            parameter = {'tagDirectory': TagDir}
            url = "{}{}".format(self.UrlIp, "getTagDirectories/")
            ReqResp = self.Session.get(url, verify=False, params=parameter, timeout=self.timeout)
            if ReqResp.status_code != 200:
                raise ValueError("error")
        except:
            return False
        else:
            return ReqResp.json()

    def get_tag_metadata_get(self, TagName, TagDirParam=None):
        """
        This class method returns the metadata from one tag

        :param TagName:
            (string) the tag from which the datadatas are wanted
        :param TagDirParam:
            (string) directory of the tag
            default value: self.DefaultDir
        :return:
            False if error
            (list) of (dict) with metadatas, example: [{'title': 'guy', 'name': 'test2', 'description': 'jklj', 'type': 'double-float', 'unit': 'hiluli'}]
        """
        try:
            if TagDirParam == None:
                TagDir = self.DefaultDir

            else:
                TagDir = TagDirParam

            parameter = {'tag': "{}/{}".format(TagDir, TagName)}
            url = "{}{}".format(self.UrlIp, "getTagMetadatas/")
            ReqResp = self.Session.get(url, verify=False, params=parameter, timeout=self.timeout)
            if ReqResp.status_code != 200:
                raise ValueError("error")
        except:
            return False
        else:
            return ReqResp.json()

    def get_tag_metadata_post(self, TagNameList, TagDirParam=None):
        """
        This class method return the metadatas for a list of tags

        :param TagNameList:
            (list) with tags names, they have to be in the same directory
        :param TagDirParam:
            (string) directory of the tag
            default value: self.DefaultDir
        :return:
            False if error
            (list) of (dict): example: [{'name': 'test2', 'title': 'guy', 'unit': 'hiluli', 'description': 'jklj', 'type': 'double-float'}, {'name': 'test', 'title': '', 'unit': '', 'description': '', 'type': 'double-float'}]
        """
        try:
            if TagDirParam == None:
                TagDir = self.DefaultDir

            else:
                TagDir = TagDirParam

            payload = []
            for elt in TagNameList:
                payload.append("{}/{}".format(TagDir, elt))

            url = "{}{}".format(self.UrlIp, "getTagMetadatas/")
            ReqResp = self.Session.post(url, data=json.dumps(payload), verify=False, timeout=self.timeout)
            if ReqResp.status_code != 200:
                raise ValueError("error")

        except:
            return False

        else:
            return ReqResp.json()

    def browse_directory(self, TagDirParam=None):
        """
        This class method return the content of one directory

        :param TagDirParam:
            (string) directory of the tag
            default value: self.DefaultDir
        :return:
            False if error
            (dict) of (dict): example:{'wintell/SR4/testag': {'name': 'testag', 'unit': '', 'type': 'double-float', 'description': '', 'title': ''}, 'wintell/SR4/test2': {'name': 'test2', 'unit': 'hiluli', 'type': 'double-float', 'description': 'jklj', 'title': 'guy'}, 'wintell/SR4/test': {'name': 'test', 'unit': '', 'type': 'double-float', 'description': '', 'title': ''}}

        """
        try:
            if TagDirParam == None:
                TagDir = self.DefaultDir

            else:
                TagDir = TagDirParam

            parameter = {'tagDirectory': TagDir}
            url = "{}{}".format(self.UrlIp, "browseTagDirectory/")
            ReqResp = self.Session.get(url, verify=False, params=parameter, timeout=self.timeout)
            if ReqResp.status_code != 200:
                raise ValueError("error")
        except:
            return False

        else:
            return ReqResp.json()


"""in case the fileis executed"""
if __name__ == "__main__":
    a=string_to_utc("Wed, 25 Jan 2017 11:29:39 GMT", DefConFormat="%a, %d %b %Y %H:%M:%S GMT")
    print(utc_to_string(a/1000))
    myLake = PyLakeDriver("wintell", "wintell347", "148.251.51.21", DefaultDir="wintell/SR4")
    a = myLake.get_tag_directories()
    print(a)
    b=['wintell/JTEK', 'wintell/JTEK/BE', 'wintell/JTEK/BE/Manage', 'wintell/JTEK/BE/Manage/Line 1', 'wintell/JTEK/BE/Manage/Line 1/Power', 'wintell/JTEK/BE/Manage/Line 1/Power/curclamp1', 'wintell/JTEK/BE/Manage/Line 1/Power/curclamp2', 'wintell/JTEK/BE/Manage/Line 1/Power/curclamp3', 'wintell/JTEK/BE/Manage/Line 1/Power/curclamp4', 'wintell/JTEK/BE/Manage/Line 1/Power/curclamp5', 'wintell/JTEK/BE/Manage/Line 1/Power/curclamp6', 'wintell/JTEK/BE/Manage/Line 1/Power/voltprobe1', 'wintell/JTEK/BE/Manage/Line 1/Power/voltprobe2', 'wintell/JTEK/BE/Manage/Line 1/Speed', 'wintell/JTEK/BE/Manage/Line 1/Speed/tach1', 'wintell/JTEK/BE/Manage/Line 1/Speed/tach2', 'wintell/JTEK/BE/Manage/Line 1/Temperatures', 'wintell/JTEK/BE/Manage/Line 1/Temperatures/temp1', 'wintell/JTEK/BE/Manage/Line 1/Temperatures/temp10', 'wintell/JTEK/BE/Manage/Line 1/Temperatures/temp2', 'wintell/JTEK/BE/Manage/Line 1/Temperatures/temp3', 'wintell/JTEK/BE/Manage/Line 1/Temperatures/temp4', 'wintell/JTEK/BE/Manage/Line 1/Temperatures/temp5', 'wintell/JTEK/BE/Manage/Line 1/Temperatures/temp6', 'wintell/JTEK/BE/Manage/Line 1/Temperatures/temp7', 'wintell/JTEK/BE/Manage/Line 1/Temperatures/temp8', 'wintell/JTEK/BE/Manage/Line 1/Temperatures/temp9', 'wintell/JTEK/BE/Manage/Line 1/Vibrations', 'wintell/JTEK/BE/Manage/Line 1/Vibrations/vib1', 'wintell/JTEK/BE/Manage/Line 1/Vibrations/vib10', 'wintell/JTEK/BE/Manage/Line 1/Vibrations/vib2', 'wintell/JTEK/BE/Manage/Line 1/Vibrations/vib3', 'wintell/JTEK/BE/Manage/Line 1/Vibrations/vib4', 'wintell/JTEK/BE/Manage/Line 1/Vibrations/vib5', 'wintell/JTEK/BE/Manage/Line 1/Vibrations/vib6', 'wintell/JTEK/BE/Manage/Line 1/Vibrations/vib7', 'wintell/JTEK/BE/Manage/Line 1/Vibrations/vib8', 'wintell/JTEK/BE/Manage/Line 1/Vibrations/vib9']
    for elt in b:
        c=myLake.get_tag_list(TagDirParam=elt)
        myLake.delete_tags(c,TagDirParam=elt)
        print(c)
    """a=myLake.get_tag_list()
    print(a)"""



    # print(myLake.get_tag_metadata_post(["test2","test"]))
    # print(myLake.get_tag_metadata_get("test2"))
    # print(myLake.get_tag_directories())
    # a=myLake.get_tag_list()
    # print(a)
    # print(myLake.truncate_tags(["testag"], 74000, DefConFormat="utc"))
    # print(myLake.delete_tags(["test"]))
    # myLake.create_tags("test2", TagTitle="guy",TagDescription="jklj",TagUnit="hiluli")
    # a=myLake.get_values("testag",1,81000,DefConFormat="utc")
    # print(a)
    # print(myLake.create_directory("SR4"))
    # print(myLake.create_tags("testag3",TagDirParam="wintell/test/",TagType="string", TagUnit="hz", TagDescription="frequence",TagTitle="tuj"))
    #print(myLake.add_value("TagTempGearBox","2015-01-01 00:00:00",45))
    # print(myLake.add_values("testag",[[73000,25],[74000,26]], DefConFormat="utc"))
    # speed test --> result: 4,5 seconds for 100 requests
    # for i in range(100):
    #    myLake.add_value("testag",74000+i,52,DefConFormat="utc")


    # print(utc_to_datetime(180))
    # print(type(get_utc_now(ReturnFormat="utc")))
    # print(get_utc_now(ReturnFormat="utc"))
    # print(utc_to_string(60))
    # a=get_utc_now()
    # print(utc_to_datetime(a))
    # print(string_to_datetime("2015-01-05 13:15:25"))
    # print(type(string_to_datetime("2015-01-05 13:15:25")))
    # print(string_to_utc("1970-01-01 01:01:00",ReturnFormat="s"))
