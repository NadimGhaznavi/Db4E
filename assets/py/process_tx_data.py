#!/usr/bin/python3

import csv
import sys
from datetime import datetime, timedelta

try:
    CsvFileName = sys.argv[1]
except:
    print("Usage: " + sys.argv[0] + " <CSV File>")
    exit(1)

outFileName = 'xmr-earnings.csv'

CsvFileHandle = open(CsvFileName)
CsvFile = csv.reader(CsvFileHandle)

rows = []
firstRow = True
for aRow in CsvFile:
    if firstRow == True:
        firstRow = False
    else:
        rows.append([aRow[2].split(' ',1)[0],float(aRow[4])])

rows.sort()
nRows = []

rCount = 0
nCount = 0
curTotal = 0
for aRow in rows:
    print("=====================================================================")
    print("rCount:", rCount)
    print("nCount:", nCount)
    print("---------------")

    curDate = aRow[0]
    curTx = aRow[1]
    print("Current Date  :", curDate)
    print("Current TX    :", curTx)
    print("---------------")

    curTotal = curTotal + curTx
    print("Current Total :", curTotal)

    if rCount == 0:
        print("Prev TX       : N/A")
        print("Prev Total    : N/A")
        print("Prev Date     : N/A")
        print("Prev Date + 1 : N/A")
        print("---------------")
        nRows.append([curDate, curTx, curTotal])
        print("                                     New Row:", curDate, " ", curTx, " ", curTotal)
        nCount = nCount + 1
        rCount = rCount + 1

    else:
        prevDate = nRows[nCount - 1][0]
        prevTx = nRows[nCount - 1][1]
        prevTotal = nRows[nCount -1][2]
        print("Prev TX       :", prevTx)
        print("Prev Total    :", prevTotal)
        print("Prev Date     :", prevDate)

        if curDate == prevDate:
            print("ADDITIONAL TRANSACTION ON SAME DAY")
            nRows[nCount - 1][1] = nRows[nCount - 1][1] + curTx
            nRows[nCount - 1][2] = nRows[nCount - 1][2] + curTx
            print("                                 Updated Row:", curDate, "...")
        else:
            nRows.append([curDate, curTx, curTotal])
            print("                                     New Row:", curDate, " ", curTx, " ", curTotal)
            nCount = nCount + 1
            rCount = rCount + 1


zRows = []
zRows.append(["Date","Amount","Total"])
zCount = 1

firstRow = True
rCount = 0
print("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
for aRow in nRows:
    print("=====================================================================")
    curDate = aRow[0]
    curTx = aRow[1]
    curTotalTx = aRow[2]
    print("Current Date  :", curDate)
    if rCount == 0:
        print("Prev Date     : N/A")
        zRows.append([curDate,curTx,curTotalTx])
        zCount = zCount + 1
        print("New Row :", zRows[zCount -1])
        rCount = rCount + 1
    else:
        prevDate = nRows[rCount - 1][0]
        print("Prev Date     :", prevDate)
        prevDatePlusOne = datetime.strptime(prevDate, "%Y-%m-%d") + timedelta(days=1)
        prevDatePlusOne = prevDatePlusOne.strftime("%Y-%m-%d")
        print("Prev Date + 1 :", prevDatePlusOne)
        while curDate != prevDatePlusOne:
            print("MISSING DATE :", prevDatePlusOne)
            zRows.append([prevDatePlusOne,"0",zRows[zCount -1][2]])
            zCount = zCount + 1
            print("New Row :", zRows[zCount - 1])
            prevDatePlusOne = datetime.strptime(prevDatePlusOne, "%Y-%m-%d") + timedelta(days=1)
            prevDatePlusOne = prevDatePlusOne.strftime("%Y-%m-%d")

        zRows.append([curDate,curTx,curTotalTx])
        zCount = zCount + 1
        print("New Row :", zRows[zCount - 1])
        rCount = rCount + 1

outFileHandle = open(outFileName, 'w')
for aRow in zRows:
    print("Writing Row :", aRow)
    if aRow[2] == 'Total':
      total = aRow[2]
    else:
      total = round(float(aRow[2]), 4)
  
    outFileHandle.write(aRow[0] + "," + str(total) + "\n")
outFileHandle.close()

print("Done. Results in:", outFileName)

