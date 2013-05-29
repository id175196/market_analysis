#theBrokeQuant
#Last Update: 4/30/2012



import os
import urllib
import sys
import random
import math

##USER DEFINED INPUT##

#Starting Date
StartDay = 1
StartMonth = 'January'
StartYear = 2005

#Ending Date
EndDay =31
EndMonth = 'December'
EndYear = 2012

TimeInterval = "Day"


#Starting Capital
startingValue = 10000

#cost per trade
flat_rate = 8.95

#slippage boundaries in buy/sell
slippage = .005

numTrials = 1000
#percentage of minimum for past 10 days
percentOfMin = 1
stopLoss = 0

daysInMA= 50
daysInLongMA = 100
numDaysTrack = 5
numDaysHold = 10

isSP500 = True
isBatch = False

batchTest = True
batchList = ['']

performedBest = False
topPerformers = 10



##BEGINNING OF PROGRAM##

#import data from file 
def importData(StartDay, StartMonth, StartYear, EndDay, EndMonth, EndYear, Ticker, TimeInterval):

       masterL = []
       Months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']


       #format begin date ex. 20120528 = 2012-05-28
       beginDate = str(StartYear)
       if len(beginDate) == 3:
              beginDate = beginDate + '0'
       if len(str(Months.index(StartMonth)+1)) >= 2:
              beginDate = beginDate + str(Months.index(StartMonth)+1)
       else:
              beginDate = beginDate + "0"+ str(Months.index(StartMonth)+1)
       if len(str(StartDay)) >= 2:
              beginDate = beginDate + str(StartDay)
       else:
              beginDate = beginDate + "0"+ str(StartDay)
       beginDate = int(beginDate)


       #format end date using the same method as above
       endDate = str(EndYear)
       if len(endDate) == 3:
              endDate = endDate + '0'
       if len(str(Months.index(EndMonth)+1)) >= 2:
              endDate = endDate + str(Months.index(EndMonth)+1)
       else:
              endDate = endDate + "0"+ str(Months.index(EndMonth)+1)
       if len(str(EndDay)) >= 2:
              endDate = endDate + str(EndDay)
       else:
              endDate = endDate + "0"+ str(EndDay)
       endDate = int(endDate)





       #open the ticker's respective file
       filename = "Tickers\\" + Ticker + ".txt"
       f = open(filename, "r")
       line = f.readline()

       grabbingDates = False


       #collect all the dates within the specified date range
       while line:
              line = line.split()

              #break if it's a header line
              if line[0][0] == 'D':
                  break

              #remove hyphen in data's date
              numDate = ""
              for char in line[0]:
                     if char != "-":
                            numDate = numDate + char

              #stop collecting data when the current lines data <= specified
              #end date
              if int(numDate) > endDate:
                     f.close()
                     return masterL                             
              if grabbingDates:
                     masterL.append(line)
              if int(numDate) == endDate:
                     f.close()
                     return masterL
             
              #begin collecting data if current line's data >= specified begin date
              if int(numDate) >= beginDate and not(grabbingDates):
                     masterL.append(line)
                     grabbingDates = True

              line = f.readline()

       f.close()
       return masterL

    

#find the previous X-days maximum high and minimum low
#works when list is sorted oldest to newest
def xDayLowHigh(L, days):

    #reverse the list and take the x most recent days
    tempList = []
    i = len(L) - 1
    while i >= 0:
        tempList.append(L[i])
        i = i - 1
    L = tempList[0:days]

    #find the minimum and maximum  
    maximum = 0
    minimum = sys.maxint
    for entry in L:
        if float(entry[2]) > maximum:
            maximum = float(entry[2])
        if float(entry[3]) < minimum:
            minimum = float(entry[3])

    return [minimum, maximum]



#calculate the X-day simple moving average
#works when list is sorted oldest to newest 
def movingAverage(L, days):

    #reverse the list and take the x most recent days
    tempList = []
    i = len(L) - 1
    while i >= 0:
        tempList.append(L[i])
        i = i - 1
    L = tempList[0:days]

    #calculate the average
    average = 0
    for entry in L:
        average = average + float(entry[4])

    return average/days
    


#backtest a single ticker in the specified period of time. the output is a list
#of every possible trade that would have occurred in the specified date range
#L is the output of importData()
def backtest(L, StartDay, StartMonth, StartYear):

    returnsList = []

    #find the index of the beginning date
    Months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
    for entry in L:
        dateList = entry[0].split("-")

        #if there is a problem parsing the html, return nothing
        if len(dateList)!=3:
            return returnsList

        #otherwise continue
        if int(dateList[0]) == StartYear and int(dateList[1]) == Months.index(StartMonth)+1 and int(dateList[2]) == StartDay:
            index = L.index(entry)
            break
        elif (int(dateList[0]) == StartYear and int(dateList[1]) == Months.index(StartMonth)+1 and int(dateList[2]) > StartDay) or (int(dateList[0]) == StartYear and int(dateList[1]) > Months.index(StartMonth)+1 and int(dateList[2]) < StartDay) or (int(dateList[0]) > StartYear and int(dateList[1]) < Months.index(StartMonth)+1 and int(dateList[2]) < StartDay):
            index =  L.index(entry)
            break

    #if there is not enough data, return nothing
    if len(L) < 400:
        return returnsList


    #CYCLING THROUGH DAYS
    #begin cycling through data, starting at the specified begin date and walk
    #to the specified end date

       
    i = index
    while i < len(L):

       #calculate signals
       #minimum, maximum, shortMA, long mA
           
        minmaxList = xDayLowHigh(L[:i],numDaysTrack)
        movingaverage = movingAverage(L[:i], daysInMA)
        longMA = movingAverage(L[:i], daysInLongMA)
        


        #PURCHASE STATEMENT
        
        #if this a new minimum, price > than shortMA, and price > longMA
        #purchase the security
        if float(L[i][3]) < minmaxList[0]*percentOfMin and float(L[i][3]) > movingaverage and float(L[i][3]) > longMA:
            
            purchase = True
            purchaseDate = L[i][0]
            beginDayIndex = i


            #if the day opens above the minimum and crosses down, the purchase
            #price will be at the 10D minimum
            if float(L[i][1]) > minmaxList[0]*percentOfMin:
                purchasePrice = minmaxList[0]*percentOfMin
            #if the open price opens below the 10D minimum we will purchase
            #at open
            else:
                purchasePrice = float(L[i][1])

            #move onto the next day
            i = i + 1

            #for each day holding the security
            while purchase:


                #SELL STATEMENTS



                   
                #if we run out of dates to check sell at close and return
                #you will enter this when you're still holding the security
                #during your specified end date
                if i > len(L) - 1:
                    salePrice = float(L[i-1][4])
                    returnsList.append([purchaseDate, salePrice/purchasePrice, purchaseDate, round(purchasePrice,2), L[i-1][0], salePrice, round(salePrice/purchasePrice,3)])

                    return returnsList


                #if the day has a new xDay high, sell the security
                #lowhighList = xDayLowHigh(L[:i], 10)
                if purchase and float(L[i][2]) > minmaxList[1]:#lowhighList[1]:
                    #if the open is greater than the 10D high, we sell at open
                    if float(L[i][1]) > minmaxList[1]:#lowhighList[1]:
                        salePrice = float(L[i][1])
                    #if the open is lower than the 10D high, we sell the 10D high
                    else:
                        salePrice = minmaxList[1]#lowhighList[1]
                        
                    returnsList.append([purchaseDate, salePrice/purchasePrice, purchaseDate, round(purchasePrice,2), L[i][0], salePrice, round(salePrice/purchasePrice,3)])
                    i = i + 1
                    purchase = False


                #if the price drops below the short MA, sell the security
                newmovingaverage = movingAverage(L[:i], daysInMA)
                if purchase and float(L[i][3]) < newmovingaverage:
                    #if the open is less than the MA, we sell at the open
                    if float(L[i][1]) < minmaxList[1]:#lowhighList[1]:
                        salePrice = float(L[i][1])
                    #if the open is greater than the MA, we sell at the MA
                    else:
                        salePrice = newmovingaverage

                    returnsList.append([purchaseDate, salePrice/purchasePrice, purchaseDate, round(purchasePrice,2), L[i][0], salePrice, round(salePrice/purchasePrice,3)])
                    i = i + 1
                    purchase = False


                #if the price drops below our stop loss, sell the security
                minLoss = purchasePrice * stopLoss
                if purchase and float(L[i][3]) < minLoss:
                    #if the open is lower than the stop loss, we sell the open
                    if float(L[i][1]) < minLoss:
                        salePrice = float(L[i][3])
                    #oterwise we sell the stop loss
                    else:
                        salePrice = minLoss
                                       
                    returnsList.append([purchaseDate, salePrice/purchasePrice, purchaseDate, round(purchasePrice,2), L[i][0], round(salePrice,2), round(salePrice/purchasePrice,3)])
                    i = i + 1
                    purchase = False


                #if we've been holding for 10 days, sell at close
                if purchase and i - (numDaysHold + 1) == beginDayIndex:
                    salePrice = float(L[i-1][4])
                    returnsList.append([purchaseDate, salePrice/purchasePrice, purchaseDate, round(purchasePrice,2), L[i-1][0], round(salePrice,2), round(salePrice/purchasePrice,3)])
                    i = i + 1
                    purchase = False


                     

                     


                #if it's not a sale statement
                if purchase:
                    i = i + 1
        #if it's not a buy statement
        else:
            i = i + 1

    return returnsList






#Sort date from oldest to newest
def sortList(L):
    newL = []

    for entry in L:
        temp = []
        string = ""
        for i in entry[0].split("-"):
            string = string + i
        temp.extend([int(string)] + entry[1:8])
        newL.append(temp)
    
    masterSort = []

    while len(newL)>0:
        minValue = sys.maxint
        minIndex = 0
        i = 0
        while i < len(newL):
            if int(newL[i][0]) < minValue:
                minValue = int(newL[i][0])
                minIndex = i
            i = i + 1

        masterSort.append(newL[minIndex])
        del newL[minIndex]

    for entry in masterSort:
        entry[0] = str(entry[0])[0:4] + "-" + str(entry[0])[4:6]  + "-" + str(entry[0])[6:8]

    return masterSort


#sort a list of numbers in descending order
def sortDescendingInts(L):
    
    masterSort = []

    while L:
        maxValue = 0
        minIndex = 0
        i = 0
        for entry in L:
            if entry[0] > maxValue:
                maxValue = entry[0]
                maxIndex = i
            i = i + 1

        masterSort.append(L[maxIndex])
        del L[maxIndex]
        if not(L):
               return masterSort





#Takes a list of tickers, backtests each one of them, collects all possible trades, 
#puts them in a dictionary sorted by the purchase date, runs scenarios of possible
#outcomes, and calculates the average return
def backtestBatch(tickerList, numTrials):
       MasterList = []

       #get all possible trades that could have occured
       for Ticker in tickerList:
           try:
               #print Ticker
               L = importData(StartDay, StartMonth, StartYear - 2, EndDay, EndMonth, EndYear, Ticker, TimeInterval)
               for entry in backtest(L, StartDay, StartMonth, StartYear):
                    MasterList.append(entry+[Ticker])
           except:
               print "Unknown error, skipped ticker", Ticker



       #sorted list of all possible trades (sorted by date)
       sortedList = sortList(MasterList)
       #dictionary of all possible trades
       purchaseDict = {}
       #sequence of trades
       tradesList = []


       #place all trades occuring on the same day in a dictionary with key
       #equal to the purchase date
       tempList = []
       listOfDates = []
       i = 0
       while i < len(sortedList):
    
           if tempList:
               if tempList[0][0] == sortedList[i][0]:
                    tempList.append(sortedList[i])
                    i = i + 1
               else:
                   purchaseDict.update({tempList[0][0]:tempList})
                   listOfDates.append(tempList[0][0])
                   tempList = []
           else:
               tempList.append(sortedList[i])
               i = i + 1
       if tempList:
           purchaseDict.update({tempList[0][0]: tempList})
           listOfDates.append(tempList[0][0])

       #Run an analysis looping through numTrials random combinations of trades
       AverageReturns = []
       loops = 0
       while loops < numTrials and len(listOfDates) > 0:
              i = 0
       
              buyDate = listOfDates[0]

              while buyDate:

                  #chose a random trade that occured on the curent purchase date                     
                  randomInt = random.randrange(len(purchaseDict[buyDate]))
                  tradesList.append(purchaseDict[buyDate][randomInt])

                  #retrieve the date that security would have been sold
                  saleDate = purchaseDict[buyDate][randomInt][4] #saleDate, ha. oops. 

                  #get the index of the next possible trade (this would come
                  #after the sell date)
                  indexOfNextEntry = None
                  for entry in listOfDates:

                      #format possible purchase date
                      entryDate = ""
                      for char in entry:
                          if char!= "-":
                              entryDate = entryDate + char
                      entryDate = int(entryDate)

                      #format sell date
                      intsaleDate = ""
                      for char in saleDate:
                          if char!= "-":
                              intsaleDate = intsaleDate + char
                      intsaleDate = int(intsaleDate)

                     #next purchase date found
                      if intsaleDate < entryDate:
                          indexOfNextEntry = listOfDates.index(entry)
                          break

                  #if there are no more possible purchases then end the loop
                  if indexOfNextEntry == None:
                      buyDate = False
                  #otherwise repeat with the next possible purchase
                  else:
                      buyDate = listOfDates[indexOfNextEntry]



              #if you wanted to see the sequence of purchses, the remove
              #the hashtags from the following print statements
                                       
              #print "Purchase Date, Price, Sale Date, Price, Return, Ticker"
              returns = startingValue
              for entry in tradesList:
                  returns = returns*((entry[5]*(1-slippage*random.random()))/(entry[3]*(1 + slippage*random.random())))-2*flat_rate
                  #print entry[2:]
                                       
              tradesList = []
              AverageReturns.append(returns)

              loops = loops + 1




       #calculate the average return and stand deviation
       if len(AverageReturns) > 0:
              #average
              ave = 0
              for entry in AverageReturns:
                     ave = ave + entry
              average = ave/len(AverageReturns)

              #standard deviation
              stdev = 0
              if numTrials > 1:
                     for entry in AverageReturns:
                            #print entry
                            stdev = stdev + (entry - average)*(entry - average)
                     #print len(AverageReturns)
                     standardDev = math.sqrt(stdev/(len(AverageReturns)-1))
              else:
                     standardDev = "N/A"


       #will return false if no trades occurred 
              return [average, standardDev]
       else:
              return False



#test each ticker one by one and return list of best performers
def findBestPerformers(tickerList):
       masterAverage = []
       for Ticker in tickerList:
              tickerAverage = backtestBatch([Ticker], numTrials)[0]
              if tickerAverage:
                     masterAverage.append([tickerAverage, Ticker])

       masterAverage = sortDescendingInts(masterAverage)
       return masterAverage

              

#open SP500 list and import tickers
tickerList = []
f= open("SP500.txt","r")
lines = f.readline()
while lines:
    tickerList.append((lines.split('\n'))[0])
    lines = f.readline()
f.close()


#test group of tickers and get average return of numTrials
#possible combinations of trades
if batchTest:
       if isSP500:
              tickers = tickerList
       if isBatch:
              tickers = batchList

       #i = 1
       #while i >= .89:
              #percentOfMin = i
       batchtestresults = backtestBatch(tickers, numTrials)
       if batchtestresults:
              endingValue = batchtestresults[0]
                     #print "Year:", entry                     
                     #print "Percent of Min:", i

              print "Starting Value:", startingValue
              if endingValue:
                     print "Ending Value:", round(endingValue,2)
                     print "Return:", round((endingValue/startingValue - 1)*100,3), "%"
                     print "Stdev:", batchtestresults[1]
                     print ""
              else:
                     print "Ending Value:", startingValue
                     print "Return:", "0%"
       else:
              #print "Year:", entry
              #print "Percent of Min:", i
              print "No trades"
              #i = i - .01


#test each ticker one by one and return list of best performers        
if performedBest:
       
       if isSP500:
              tickers = tickerList
       if isBatch:
              tickers = batchList
       bestPerformers = findBestPerformers(tickers)[:topPerformers+1]
       bestList = []
       for entry in bestPerformers:
              bestList.append(entry[1])
              print entry
       print bestList
