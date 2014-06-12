from Tkinter import *
import math
import os
import urllib
import string

def getSchedule():
    # Retrieves the current schedule and saves the string
    schedule = urllib.urlopen("https://enr-apps.as.cmu.edu/assets/SOC/" +
                               "sched_layout_spring.dat").read()
    schedulelist = processSchedule(schedule)
    return schedulelist

def processSchedule(schedule):
    # This is a 2d list of all classes, with each sublist containing all the 
    # data about the class, as well as a sublist for each section containing
    # its time.
    schedList = []
    # This starts by making the first element in the list the semester and year
    # and the next element the date (which is always the last day it was 
    # retrievd).
    schedList += findDate(schedule)
    # Cycles through each set of 5 elements in the string and attempts to find
    # 5 digit numbers in the string (which signify course numbers). Once found
    # it adds the string to a sublist in schedList and extracts all the info
    # about the course.
    rawList = []
    splitSched = schedule.replace('\t','\n').splitlines()
    for line in splitSched:
        if line:
            rawList += [line]
    for i in xrange(len(rawList)):
        if (len(rawList[i]) == 5) and rawList[i].isdigit():
            courseNumber = int(rawList[i])
        else:
            continue
        courseName = rawList[i+1]
        credits = rawList[i+2]
        courseInfo = [courseNumber, courseName, credits]    
        x = 3
        while True:
            if (rawList[i+x].isalnum() and (not rawList[i+x].isdigit()) and 
                (len(rawList[i+x]) <= 3)):
                section = [rawList[i+x]]
                x += 1
                if rawList[i+x] == 'TBA':
                    x += 1
                    section += ['TBA','TBA','TBA']
                else: 
                    section += [rawList[i+x]]
                    x += 1
                    section += [rawList[i+x]] 
                    x += 1
                    section += [rawList[i+x]] 
                    x += 1
                section += [rawList[i+x]]
                x += 1
                section += [rawList[i+x]]
                x += 1
                courseInfo += [section]
                try: rawList[i+x]
                except: break
            else:
                break
        schedList += [courseInfo]
        del(courseNumber)
    return schedList

def findDate(schedule):
        semesterIndex = schedule.find('Semester:') + 10
        indexEnd = schedule.find('\n',semesterIndex)
        semester = schedule[semesterIndex:indexEnd]
        dateIndex = schedule.find('Run Date:') + 10
        indexEnd = schedule.find(' ',dateIndex)
        date = schedule[dateIndex:indexEnd]
        return [semester, date]

def findCourseInfo(i,line,schedule):
    courseNumber = schedule[i:i+5]
    

def drawCalendar(canvas,cWidth,cHeight):
    # sets a margin of 1.5 times the with where it starts drawing the calender
    xmargin = int(1.5*(cWidth/10))
    ymargin = cHeight/14
    # The width of a calendar column (aka a day)
    colWidth = (cWidth-(2*xmargin))/5 
    # This is the box of the weekly calendar
    week = ['Monday','Tuesday','Wednesday','Thursday','Friday',
            'Saturday','Sunday']
    canvas.create_rectangle(xmargin,ymargin,cWidth-xmargin,cHeight-ymargin,
                            fill="#808000")
    # Creates the lines for seperating each day of the week
    for column in xrange(1,6):
        canvas.create_line(xmargin+(colWidth*column),ymargin,
                           xmargin+(colWidth*column),cHeight-ymargin)
        canvas.create_text(xmargin+int(colWidth*(column-0.5)),ymargin-12,
                           text=week[column-1])
    # Default hours are 7AM to 6PM. So 11 hours (5+6) are displayed,
    # in increments of 10 minutes (so times 6)
    hourline = 11
    tenminuteline = 11*6
    hourheight = (cHeight-ymargin)/hourline
    # Loops to draw a line for each hour mark, and a dotted line for each
    # half hour
    for row in xrange(hourline-1):
        canvas.create_line(xmargin,ymargin+(row*hourheight),
                           cWidth-xmargin,ymargin+(row*hourheight))


def init(canvas):
    canvasWidth = canvas.data.canvasWidth
    canvasHeight = canvas.data.canvasHeight
    drawCalendar(canvas,canvasWidth,canvasHeight)

def run(wid=1000): # The default canvas size values (it is resizable)
    root = Tk()
    # The canvas size is is whatever width value is given, and (wid/10)*7
    high = 7*(wid/10)
    canvas = Canvas(root, width=wid, height=high, background="#808000")
    canvas.pack()
    root.resizable(width=0,height=0)
    class Struct: pass
    canvas.data = Struct()
    # Saving the canvas size data
    canvas.data.canvasWidth = wid
    canvas.data.canvasHeight = high
    init(canvas)
    #root.bind("<Button-1>", mousePressed)
    #root.bind("<Key>", keyPressed)
    root.mainloop()
    
#run()


