import json
import requests
import datetime
import urllib
import os
import tkinter as tk
from tkinter import ttk
import re
import matplotlib.pyplot as plt
import calendar
import threading

#define
CURRENT_YEAR = datetime.datetime.now().year
CURRENT_MONTH = datetime.datetime.now().month
DATA_LINK = "https://www.accuweather.com/en/vn/hanoi/353412/"
MONTH = ["","january", "february", "march", "april", "may", "june", "july", "august", "september", "october", "november", "december"]
headers = {"Accept-Language": "en-US,en;q=0.5", "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:40.0) Gecko/20100101 Firefox/40.0"}



def currentData():
    url = "http://wttr.in/hanoi?format=j1"
    req = requests.get(url,headers=headers)
    dataStr = req.text
    dataJson = json.loads(dataStr)
    if(dataJson["current_condition"][0]):
        return dataJson["current_condition"][0]
    else:
        return nil
        
class YearList(ttk.Frame):
    def __init__(self, master,width, height):
        ttk.Frame.__init__(self, master)
        self.height = height
        self.width = width
        self.yearpoint = CURRENT_YEAR
        dictArray = list(range(CURRENT_YEAR-19, CURRENT_YEAR))
        self.comboBox = ttk.Combobox(self,state = "readonly", value=dictArray)
        self.comboBox.grid(column = 1, row = 0)
        self.comboBox.current(0)
        self.comboBox.bind("<<ComboboxSelected>>", self.showData)
        self.labelYear = tk.Label(self, text = "Year")
        self.labelYear.grid(column = 0, row = 0)
        curData = currentData()
        if(curData):
            self.labelNow = tk.Label(self, text = "Now: "+ str(curData["temp_C"]) + " °" + "| Humidity: " + str(curData["humidity"]) + " %")
            self.labelNow.grid(columnspan = 2, row = 1)
            self.progress = ttk.Progressbar(self, orient="horizontal",
                                        length=200, mode="determinate")
        
            self.progress["value"] = 0
            self.progress["maximum"] = 100

    def showData(self, event):
        self.yearpoint = int(self.comboBox.get())
        thread = threading.Thread(target = self.downloadPastData, args = (self.yearpoint,))
        thread.daemon = True
        thread.start()
        
    def downloadPastData(self,yearPoint):
        self.progress.grid(columnspan = 2, row =2)
        self.progress["value"] = 0
        nowMonth = datetime.datetime.now().month
        nowYear = yearPoint
        month = [""]
        year = [""]
        if (nowMonth == 1):
            month = [MONTH[12], MONTH[1], MONTH[2]]
            year = [str(nowYear-1),str(nowYear), str(nowYear)]
        elif (nowMonth == 12):
            month = [MONTH[11], MONTH[12], MONTH[1]]
            year = [str(nowYear),str(nowYear), str(nowYear+1)]
        else:
            month = [MONTH[nowMonth-1], MONTH[nowMonth], MONTH[nowMonth+1]]
            year = [str(nowYear),str(nowYear), str(nowYear)]
        temp = []
        day = []
        x =[]
        dataDict = {"":""}
        dateAxis = []
        dayAxis = []
        nightAxis = []
        idx = 0
        self.progress["value"] = 10
        for i in range(3):
            self.progress["value"] = 10*(i+1)
            fileName = year[i] + "-" + month[i] + ".txt"
            if os.path.exists(fileName):
                f = open(fileName, 'r')
                jsonData = json.loads(f.read())
            else:
                url = DATA_LINK + month[i] + "-weather/" + "353412?year=" + year[i] + "&view=list"
                r = requests.get(url,headers=headers)
                data = r.text
                m = re.findall('var dailyForecast = (.*?);\nvar', data)
                jsonData = json.loads(m[0])
                with open(fileName, 'a') as f:
                    f.write("[")
                    for j in jsonData:
                        json.dump(j, f)
                        if(jsonData.index(j) != len(jsonData)-1):
                            f.write(",")
                    f.write("]")
                f.close()
            for j in jsonData:
                date_time_obj = datetime.datetime.strptime(j["dateTime"], "%Y-%m-%dT%H:%M:%S%z")
                dateValue = date_time_obj.date()
                if ((dateValue >= datetime.date(nowYear, MONTH.index(month[i]), 1)) & (dateValue <= datetime.date(nowYear, MONTH.index(month[i]), calendar.monthrange(nowYear,MONTH.index(month[i]))[1]))):  
                    idx+=1
                    x.append(idx)
                    dayAxis.append(j["day"]["actual"])
                    nightAxis.append(j["night"]["actual"])
                    if(((dateValue.day == calendar.monthrange(nowYear,MONTH.index(month[i]))[1]) & (i==2))
                       |((dateValue.day == 1) & (i!=2))
                       | ((dateValue.day == datetime.datetime.now().day) & (dateValue.month == CURRENT_MONTH))):
                        dateAxis.append(date_time_obj.date().strftime("%m-%d"))
                    else:
                        dateAxis.append("")

        self.progress["value"] = 95
        
        self.drawChart(x, dateAxis,dayAxis, nightAxis, self.yearpoint)
        return 1
    def drawChart(self,x, dateAxis,dayAxis, nightAxis,yearPoint):
        plt.clf()
        plt.xticks(x,dateAxis)
        plt.plot(x, dayAxis,marker='o', color='red');
        plt.plot(x, nightAxis,marker='o', color='blue');
        plt.title(yearPoint)
        self.progress["value"] = 100
        self.progress.grid_forget()
        plt.grid()
        plt.show()
        return 1

def main():
    app = tk.Tk()
    app.resizable(False, False)
    frame = YearList(app, width = 200, height = 100)
    frame.pack()
    #app.after(2000, app.destroy())
    app.mainloop()

if __name__ == "__main__":
    main()
