from file.json import Json as JsonFile
import sys, os

class Batch:
    
    def __init__(self, sourceDirectory, destinationDirectory, scriptPath):
        self.sourceDirectory = sourceDirectory
        self.destinationDirectory = destinationDirectory
        self.scriptPath = scriptPath
        return
    
    def process(self):
        file = JsonFile()
        data = file.read(self.sourceDirectory)
        if not data:
            print('No topics identified')
            return
        
        terms = []
        maxYear = 0
        minYear = 9999
        for year in data.keys():
            strYear = int(year)
            if strYear < minYear:
                minYear = strYear
            if strYear > maxYear:
                maxYear = strYear
            for month in data[year].keys():
                for day in data[year][month].keys():
                    for word in data[year][month][day].keys():
                        if data[year][month][day][word]['block_count'] > 1:
                            terms.append(word)
            if not len(terms):
                return False          
            for term in terms:
                command = "python3 " + self.scriptPath + "/code/scripts/rcReconstruct.py --word_key " + word + " --source_directory " + self.destinationDirectory + "/words --destination_directory " + self.destinationDirectory + ' --start_date ' + str(minYear) + '-01-01 --end_date ' + str(maxYear) + '-12-31 '
                print(command)
                os.system(command)
                
        return True
    
    
    