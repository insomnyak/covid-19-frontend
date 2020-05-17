import pandas as pd
import re
import os

import creds
from sources import sources

import sys
if sys.version_info[0] < 3:
    from StringIO import StringIO
else:
    from io import StringIO

class Covid19DL():

    def __init__(self):
        self.client, self.bucket_name, self.staging, self.target, self.archive, self.log \
            = creds.storageClient()
        print('')
        self.bucket = self.client.bucket(self.bucket_name)
        # self.bucket.versioning_enabled = False

    def getFilename(self, key, url, regex=r'(?i).*[/]((.*)[.]csv)', group=1, desc=''):
        reg = re.match(r'(?i).*[/]((.*)[.]csv)', url)
        filename = key.lower() \
            + (('-' + desc) if desc else '') \
            + '-' + reg.group(1)
        return filename

    def getAllTargetData(self, printPaths=False):
        print('Retrieving data from GCS')
        dfDict = dict()
        try:
            for source in sources:
                if source == 'JHU':
                    filename = 'jhu-target.csv'
                    path = '{0}{1}'.format(self.target, filename)
                    if printPaths: print(path)
                    blobTarget = self.bucket.blob(path)
                    downloadFile = blobTarget.download_as_string()
                    downloadFile = StringIO(str(downloadFile, encoding="utf-8"))
                    if source not in dfDict.keys():
                        dfDict[source] = dict()
                    dfDict[source]['ProvinceState'] = pd.read_csv(downloadFile, delimiter= ",")
                else:
                    for key in sources[source]:
                        filename = self.getFilename(source, sources[source][key], desc=key)
                        path = '{0}{1}'.format(self.target, filename)
                        if printPaths: print(path)
                        blobTarget = self.bucket.blob(path)
                        downloadFile = blobTarget.download_as_string()
                        downloadFile = StringIO(str(downloadFile, encoding="utf-8"))
                        if source not in dfDict.keys():
                            dfDict[source] = dict()
                        dfDict[source][key] = pd.read_csv(downloadFile, delimiter= ",")
            print('Retrieved data from GCS')
            print(dfDict.keys())
        except Exception as e:
            print('Failed data retrieval from GCS')
            print(e)
        return dfDict

# covid19 = Covid19DataRetrieval()
# data = covid19.getAllTargetData()
