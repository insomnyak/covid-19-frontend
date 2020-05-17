import re

def getParam(key, queryString):
    try:
        res = re.search('[&?]%s=([^&]+)' % key, queryString)
        print(True)
        return res.group(1)
    except:
        return 0
