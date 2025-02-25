# class used for reading out values from text files
class TextfileManager:

    KEY_VALUE_SEPERATOR = '='

    # returns all "key -> value" values from a given "key -> value" text file
    def getKeyValueValues(self, filepath: str) -> dict:
        dataDict = {}

        with open(filepath, 'r') as file:
            for line in file:
                # stripping removes leading and afterward coming empty spaces
                line = line.strip()
                if line: # check whether line is empty or not. If empty, skip
                    key, value = line.split(self.KEY_VALUE_SEPERATOR, 1)
                    dataDict[key.strip()] = value # strip away empty spaces from key in files

        return dataDict