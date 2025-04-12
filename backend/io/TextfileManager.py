# class used for reading out values from text files
class TextfileManager:

    KEY_VALUE_SEPERATOR = '='

    # Reads a simple text file and returns the content as list (line for line)
    def getAsList(self, filepath: str) -> list:
        dataList = []
        with open(filepath, 'r', encoding='utf-8') as file:
            for line in file:
                line = line.strip()
                if line and not line.startswith('#'):  # Skip comments and empty lines
                    dataList.append(line)
        return dataList

    # returns all "key -> value" values from a given "key -> value" text file as dictionary
    def getKeyValueValueDict(self, filepath: str, valueSplitChar: str = None) -> dict:
        dataDict = {}

        with open(filepath, 'r', encoding='utf-8') as file:
            for line in file:
                # stripping removes leading and afterward coming empty spaces
                line = line.strip()
                if line and not line.startswith('#'):  # check whether line is empty or not. If empty, skip. Also if line starts with '#', skip
                    key, value = line.split(self.KEY_VALUE_SEPERATOR, 1)
                    if valueSplitChar:
                        dataDict[key.strip()] = [i.strip() for i in value.split(valueSplitChar)]
                    else:
                        dataDict[key.strip()] = value  # strip away empty spaces from key in files

        return dataDict