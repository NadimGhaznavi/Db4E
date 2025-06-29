"""
bin/db4e-baby.py

This script was the precursor to the *db4e* application. It accepts
the CSV file that the Monero GUI wallet creates when you export
your transactions and generates a new CSV with daily totals.

It is *not* fit for production use as it doesn't handle floating 
point arithmatic to 12 decimal places: You will end up with 
rounding errors.

See https://github.com/NadimGhaznavi/kb/wiki/Handling-Floating-Point-Math-with-Python-and-MongoDb
for more information on this issue.


  This file is part of *db4e*, the *Database 4 Everything* project
  <https://github.com/NadimGhaznavi/db4e>, developed independently
  by Nadim-Daniel Ghaznavi. Copyright (c) 2024-2025 NadimGhaznavi
  <https://github.com/NadimGhaznavi/db4e>.
 
  This program is free software: you can redistribute it and/or 
  modify it under the terms of the GNU General Public License as 
  published by the Free Software Foundation, version 3.
 
  This program is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
  General Public License for more details.

  You should have received a copy (LICENSE.txt) of the GNU General 
  Public License along with this program. If not, see 
  <http://www.gnu.org/licenses/>.
"""


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
    curDate = aRow[0]
    curTx = aRow[1]
    curTotal = curTotal + curTx

    if rCount == 0:
        nRows.append([curDate, curTx, curTotal])
        nCount = nCount + 1
        rCount = rCount + 1

    else:
        prevDate = nRows[nCount - 1][0]
        prevTx = nRows[nCount - 1][1]
        prevTotal = nRows[nCount -1][2]

        if curDate == prevDate:
            nRows[nCount - 1][1] = nRows[nCount - 1][1] + curTx
            nRows[nCount - 1][2] = nRows[nCount - 1][2] + curTx
        else:
            nRows.append([curDate, curTx, curTotal])
            nCount = nCount + 1
            rCount = rCount + 1

zRows = []
zRows.append(["Date","Amount","Total"])
zCount = 1

firstRow = True
rCount = 0
for aRow in nRows:
    curDate = aRow[0]
    curTx = aRow[1]
    curTotalTx = aRow[2]
    if rCount == 0:
        zRows.append([curDate,curTx,curTotalTx])
        zCount = zCount + 1
        rCount = rCount + 1
    else:
        prevDate = nRows[rCount - 1][0]
        prevDatePlusOne = datetime.strptime(prevDate, "%Y-%m-%d") + timedelta(days=1)
        prevDatePlusOne = prevDatePlusOne.strftime("%Y-%m-%d")
        while curDate != prevDatePlusOne:
            zRows.append([prevDatePlusOne,"0",zRows[zCount -1][2]])
            zCount = zCount + 1
            prevDatePlusOne = datetime.strptime(prevDatePlusOne, "%Y-%m-%d") + timedelta(days=1)
            prevDatePlusOne = prevDatePlusOne.strftime("%Y-%m-%d")

        zRows.append([curDate,curTx,curTotalTx])
        zCount = zCount + 1
        rCount = rCount + 1

outFileHandle = open(outFileName, 'w')
for aRow in zRows:
    if aRow[2] == 'Total':
      total = aRow[2]
    else:
      total = round(float(aRow[2]), 4)
  
    outFileHandle.write(aRow[0] + "," + str(total) + "\n")
outFileHandle.close()
print("Done. Results in:", outFileName)

