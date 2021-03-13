import datetime   

class DateProcessor():
    
    def __init__(self):
        self.maxDate = None
        self.minDate = None
        return
    
    def getFormattedMonthOrDay(self, number):
        if int(number) < 10:
            return '0' + number
        return number
        
    def getSplited(self, date):
        return [int(x) for x in date.split("-")]
    
    def unformattedStrToDate(self, date):
        year, month, day = self.getSplited(date)
        return self.strToDate(str(year) + '-' + str(self.getFormattedMonthOrDay(month)) + '-' + str(self.getFormattedMonthOrDay(day)))
    
    def setMinDate(self, date):
        if not self.minDate or (date < self.minDate):
            self.minDate = date
        return 
    
    def setMaxDate(self, date):
        if not self.maxDate or (date > self.maxDate):
            self.maxDate = date
        return 
    
    def strToDate(self, date):
        return datetime.datetime.strptime(date, '%Y-%m-%d')
    
    def dateToString(self, date):
        return str(date.year) + self.getFormattedMonthOrDay(str(date.month)) + self.getFormattedMonthOrDay(str(date.day))
        




