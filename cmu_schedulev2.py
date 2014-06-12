# Importing Necessary Modules
from Tkinter import *
import math
import os
import urllib
import string

#############################################
# Retrieve and process Schedule into a list #
#############################################

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

#############################################
#  Classes for courses and course sections  #
#############################################

class Course(object):
    # Helps select color based on order of courses added
    count = 0
    instances = []
    
    @classmethod
    def getinstances(cls):
        return Course.instances

    @classmethod
    def getcount(cls):
        if Course.count > 6:
            Course.count -= 6
        return Course.count

    def __init__(self,course):
        self.number = course[0]
        self.name = course[1]
        self.credits = course[2]
        self.sections = {}
        self.course = course
        Course.count += 1
        Course.instances += [self]
        count = Course.count
        print course
        for sectionList in course[3:]:
            locals()[sectionList[0]] = Section(sectionList,count)
            self.sections[sectionList[0]] = locals()[sectionList[0]]
    
    def getTotalTime(self, section):
        course = self.course
        totalTime = []
        self.sections[section].getCalendar(self.count)
        totalTime += [self.sections[section].courseTimes]
        try:
            self.sections['Lec'].getCalendar(self.count)
            totalTime += [self.sections['Lec'].courseTimes]
        except:
            pass
        self.totalTime = totalTime
        return totalTime

    def addToSchedule(self,section,canvas):
        print section
        self.getTotalTime(section)
        sched = canvas.data.cal
        for sect in self.totalTime:
            for x in xrange(len(sched)):
                cEnd = sect[x][2]
                cStart = sect[x][1]
                for min in xrange(cStart,cEnd):
                    sched[x][min] = sect[x][0]
        canvas.data.cal = sched
        canvas.data.courses[str(self.number)] = (self, section)
        return canvas
    
    def rmSched(self,canvas):
        section = canvas.data.courses[str(self.number)][1]
        self.getTotalTime(section)
        sched = canvas.data.cal
        for sect in self.totalTime:
            for x in xrange(len(sched)):
                cEnd = sect[x][2]
                cStart = sect[x][1]
                for min in xrange(cStart,cEnd):
                    sched[x][min] = 0
        canvas.data.cal = sched
        del(canvas.data.courses[str(self.number)])
        return canvas    

class Section(object):
    def __init__(self,sectionInfo,count):
        self.count = count
        self.sNum = sectionInfo[0]
        translateDay = {'M':0,'T':1,'W':2,'R':3,'F':4,'S':5,'U':6}
        self.days = ()
        for day in sectionInfo[1]:
            self.days += (translateDay[day],)
        startTime = 0
        endTime = 0
        pos = ((0,60),(1,6),(3,1))
        for i in pos:
            startTime += int(sectionInfo[2][i[0]])*i[1]
            endTime += int(sectionInfo[3][i[0]])*i[1]
        startTime += (12 if sectionInfo[2][5] == 'P' else 0) * 6
        endTime += ((12 if sectionInfo[2][5] == 'P' else 0) * 6) + 2
        self.startTime = startTime
        self.endTime = endTime

    def getCalendar(self,count):
        self.courseTimes = [ ([0] * 3) for x in xrange(7) ]
        cTimes = self.courseTimes
        start = self.startTime
        end = self.endTime
        for day in xrange(len(self.courseTimes)):
            if day in self.days:
                cTimes[day][0] = count
                cTimes[day][1] = start
                cTimes[day][2] = end
        return self.courseTimes

class Storage(object):
    def __init__(self,canvas):
        self.canvas = canvas
    

################################
#  Main interactive functions  #
################################

def mousePressed(event):
    canvas = storCanv.canvas
    bC = canvas.data.bC
    if (bC[0][0] <= event.x <= bC[0][2]) and (bC[0][1] <= event.y <= bC[0][3]):    
        litBox = Tk()
        e = Entry(litBox)
        e.pack()
        e.focus_set()
        text = e.get()
        def callback():
            print e.get()
            canvas = storCanv.canvas
            canvas.delete('search')
            canvas.data.search = e.get()
            storCanv.canvas = searchCourse(canvas)
            return canvas
        b = Button(litBox, text="search", width=10, command=callback)
        b.pack()
        mainloop()
    elif ((bC[1][0] <= event.x <= bC[1][2]) and
          (bC[1][1] <= event.y <= bC[1][3])):
        litBox = Tk()
        e = Entry(litBox)
        e.pack()
        e.focus_set()
        text = e.get()
        def callback():
            print 'text: ', e.get()
            canvas = storCanv.canvas
            addCourse(canvas,e.get().upper())
            del(canvas.data.search)
            storCanv.canvas = canvas
        b = Button(litBox, text="Enter Section", width=10, command=callback)
        b.pack()
        mainloop()
    elif ((bC[2][0] <= event.x <= bC[2][2]) and
          (bC[2][1] <= event.y <= bC[2][3])):
        litBox = Tk()
        e = Entry(litBox)
        e.pack()
        e.focus_set()
        text = e.get()
        def callback():
            print 'text: ', e.get()
            canvas = storCanv.canvas
            if e.get().isdigit() and (len(e.get()) == 5):
                canvas = canvas.data.courses[e.get()][0].rmSched(canvas)
                canvas.delete(e.get())
                reDrawAll(canvas)
            storCanv.canvas = canvas
        b = Button(litBox, text="Rmv Course", width=10, command=callback)
        b.pack()
        mainloop()
    elif ((bC[3][0] <= event.x <= bC[3][2]) and
          (bC[3][1] <= event.y <= bC[3][3])):
        litBox = Tk()
        e = Canvas(litBox,width=450,height=200)
        e.pack()
        e.create_text(20,20,text='Instructions for use:',anchor=NW)
        e.create_rectangle(18,45,440,112,fill='#CCFFCC')
        e.create_text(20,50,text='To search for or add a course:',anchor=NW)
        e.create_text(20,65,text='\t1. Press the search button',anchor=NW)
        e.create_text(20,80,text='\t2. Enter desired course number in' +
                           ' the window',anchor=NW)
        e.create_text(20,95,text='\t3. Press the add button and type'+
                           ' the desired section',anchor=NW)
        e.create_rectangle(18,114,440,170,fill='#FFFFCC')
        e.create_text(20,115,text='To remove a course:',anchor=NW)
        e.create_text(20,130,text='\t1. Press the remove button',anchor=NW)
        e.create_text(20,145,text='\t2. enter the course number to remove',
                      anchor=NW)
        mainloop()
    
#def keyPressed(event):
#    if event.keysym ==    

def addCourse(canvas,section):
    vars()[str(canvas.data.search)] = Course(canvas.data.selCourse)
    vars()[str(canvas.data.search)].addToSchedule(section,canvas)
    reDrawAll(canvas)

def searchCourse(canvas):
    sString = canvas.data.search
    cSched = canvas.data.cList
    for course in cSched:
        if str(course[0]) == sString:
            drawSearch(canvas,course)
            canvas.data.selCourse = course
    return canvas
        #vars()[str(course[0])] = Course(course)
        
    

    #def selectCourse(canvas,section,course):
        

##############################################
#  Main Graphical and canvas.data functions  #
##############################################

def drawSearch(canvas,course):
    marg = canvas.data.margins
    h = canvas.data.cHeight
    w = canvas.data.cWidth
    xPos = w
    yPos = marg + 20
    courseInfo = course[:3]
    sectionInfo = course[3:]
    canvas.create_text((xPos-marg)+10,yPos+30,text='Course Info:',width=300,
                       anchor=NW,tag='search',font=('Times',14,'bold'))
    for c in xrange(len(courseInfo)):
        canvas.create_text((xPos-marg)+10,yPos+50+(15*c),text=(courseInfo[c]),
                        width=300,anchor=NW,tag='search')
    canvas.create_text((xPos-marg)+10,yPos+110,text='Sections:',width=300,
                       anchor=NW,tag='search',font=('Times',14,'bold'))
    for sect in xrange(len(sectionInfo)):    
        section = string.join(sectionInfo[sect],'  ')
        if len(section) > 50:
            section = section[:50]
        canvas.create_text((xPos-marg)+10,yPos+150+(30*sect),
                            anchor=NW,text=section,tag='search')
    
def buttonCoords(xPos,yPos,buttons):
    bC = []
    for b in xrange(buttons):
        xL = xPos-30+(60*b)
        xR = xL+50
        yT = yPos
        yB = yPos+20
        bC += [[xL,yT,xR,yB]]
    return bC
    
def drawButtons(canvas):
    marg = canvas.data.margins
    h = canvas.data.cHeight
    w = canvas.data.cWidth
    xPos = w
    yPos = marg + 20
    bC = buttonCoords(xPos,yPos,5)
    extraw = canvas.data.extraw
    canvas.create_rectangle(w-marg,0,w+extraw,h,fill="#FFCCFF")
    canvas.create_rectangle((xPos-marg)+5,marg+45,w+extraw-5,h,
                            fill="#CCCCFF")
    canvas.create_line((xPos-marg)+5,yPos+100,w+extraw-5,yPos+100)
    canvas.create_text(xPos-marg+10,marg,anchor=NW,
                       text='Click below to search a course, then add'
                             + ' or remove it')
    canvas.create_rectangle(bC[1][0],bC[1][1],bC[1][2],bC[1][3],fill='#EEEEBB',
                            activefill='#EEEE55')
    canvas.create_text(bC[1][0]+25,bC[1][1]+10,text='Add',state=DISABLED)
    canvas.create_rectangle(bC[0][0],bC[0][1],bC[0][2],bC[0][3],fill='#EEEEBB',
                            activefill='#EEEE55')
    canvas.create_text(bC[0][0]+25,bC[0][1]+10,text='Search',state=DISABLED)
    canvas.create_rectangle(bC[2][0],bC[2][1],bC[2][2],bC[2][3],fill='#EEEEBB',
                            activefill='#EEEE55')
    canvas.create_text(bC[2][0]+25,bC[2][1]+10,text='Remove',state=DISABLED)
    canvas.create_rectangle(bC[3][0],bC[3][1],bC[3][2],bC[3][3],fill='#EEEEBB',
                            activefill='#EEEE55')
    canvas.create_text(bC[3][0]+25,bC[3][1]+10,text='Help',state=DISABLED)
    canvas.data.bC = bC
    return canvas

def splitName(nList):
    if len(nList) < 24:
        return [nList]
    newList = nList
    n = 0
    sAdd = 0
    for x in xrange(len(nList)):
        if nList[x] == ' ':
            if len(nList[n:x]) > 23:
                n = x-1
                while nList[n] != ' ':
                    n -= 1
                newList = newList[:n+sAdd] + ' ' + newList[n+sAdd:]
                x = n+1
                sAdd += 1
    return string.split(newList,'  ')[:2]

def getCBlocks(canvas):
    cal = canvas.data.cal
    cBlocks = []
    cBlock = (0,0,0,0)
    for x in xrange(len(cal)):
        cStart = 0
        for i in xrange(len(cal[x])-1):
            if cal[x][i]:
                if cal[x][i] != cal[x][i-1]:
                    cStart = i
                elif cal[x][i] != cal[x][i+1]:
                    cEnd = i
                    cBlocks += [(x,cal[x][i],cStart,cEnd)]
    return cBlocks

def drawCourses(canvas,w,h,marg,dayX,dayY,yTop,yBot,days,dStart,dEnd,tMins):
    colors = canvas.data.colors
    cBlock = getCBlocks(canvas)
    for block in cBlock:
        day = block[0]
        cStart = block[2] - dStart
        cEnd = block[3] - dStart
        cColor = colors[block[1]]
        xPos = marg+(dayX*day)
        yPosTop = marg+(dayY*cStart)
        yPosBot = marg+(dayY*cEnd)
        hDayX = dayX/2
        hDayY = dayY/2
        cNumb = str(Course.instances[block[1]-1].number)
        cName = splitName(Course.instances[block[1]-1].name)
        canvas.create_rectangle(xPos,yPosTop,xPos+dayX,yPosBot,fill=cColor,
                                tag=str(cNumb))
        canvas.create_text(xPos+hDayX,yPosTop+10,text=cNumb,tag=str(cNumb))
        for x in xrange(len(cName)):
            yOffset = 24 + (x*12)
            canvas.create_text(xPos+hDayX,yPosTop+yOffset,text=cName[x],
                               tag=str(cNumb))

def drawCalendar(canvas):
    w = canvas.data.cWidth
    h = canvas.data.cHeight
    marg = canvas.data.margins
    week = canvas.data.week
    days, dStart, dEnd = findDays(canvas) 
    # The following creates boxes for each hour as a blank calendar
    yTop = marg
    yBot = h-marg
    tMins = dEnd-dStart
    dayX = (w-(2*marg))/days
    dayY = (h-(2*marg))/(tMins)
    canvas.create_rectangle(0,0,w-marg,h,fill='#CCCCFF')
    canvas.create_text(w/2,(marg/2)-10,
                        text='CMU Schedule Manager',font=('Times',20,"bold"))
    for day in xrange(1, days+1):
        xMid = marg+int(dayX*(day-0.5))
        yMid = marg - 12
        canvas.create_text(xMid,yMid,text=week[day-1])
        xLeft = marg+(dayX*(day-1))
        xRight = xLeft + dayX  
        canvas.create_rectangle(xLeft,yTop,xRight,yBot,fill='#CCCCCC')
    for mins in xrange(tMins+4):
        if ((mins+1)%3)%2:
            cLeft = marg
            cRight = w-marg
            y = marg+(dayY*mins)
            hour = (dStart + mins)/6
            ampm = 'AM' if hour < 12 else 'PM'
            hour = str((hour - 12) if hour > 12 else hour)
            minute = str(3*(mins%2))
            displayTime= hour + ':' + minute + '0' + ampm
            xOffset = 30 if (len(displayTime) == 7) else 25
            if mins%2:
                canvas.create_line(cLeft,y,cRight,y,dash=5,fill='#333333')
            else:
                canvas.create_line(cLeft,y,cRight,y)
                canvas.create_text(cLeft-xOffset,y,text=displayTime)
    drawCourses(canvas,w,h,marg,dayX,dayY,yTop,yBot,days,dStart,dEnd,tMins)    
    
def findDays(canvas):
    cal = canvas.data.cal
    days = 5
    dStart = 8 * 6
    dEnd = 17 * 6
    for day in xrange(len(cal)):
        count = 0
        for mins in xrange(len(cal[day])):
            if cal[day][mins] and (day >= 5) and (count == 0):
                days += 1 if ((day == 5) or (days == 6)) else 2
                count = 1
            if cal[day][mins]:
                dStart = int(math.ceil(min(dStart,mins)/6.0)*6)
                dEnd = int(math.ceil(max(dEnd,mins)/6.0)*6)
    return days, dStart, dEnd

def reDrawAll(canvas):
    canvas.delete(ALL)
    drawCalendar(canvas)
    drawButtons(canvas)

def loadCalendar(canvas):
    canvas.data.cal = [ ( [0] * (24*6) ) for i in xrange(7) ]    
    #vars()['48095'] = Course(getSchedule()[11])
    #vars()['48095'].addToSchedule('W',canvas)
    #class1 = Course(getSchedule()[493])
    #class1.addToSchedule('D',canvas)
    return canvas

def init(canvas):
    canvas.data.cList = getSchedule()
    canvas = loadCalendar(canvas)
    canvas = drawButtons(canvas)
    drawCalendar(canvas)
    global storCanv
    storCanv = Storage(canvas)
    

def run(wid=1000): # The default canvas size values (it is resizable)
    root = Tk()
    # The canvas size is is whatever width value is given, and (wid/10)*7
    high = 7*(wid/10)
    extraw = 300
    canvas = Canvas(root, width=wid+extraw, height=high, background="white")
    canvas.pack()
    root.resizable(width=0,height=0)
    class Struct: pass
    canvas.data = Struct()
    # Saving the canvas size data
    canvas.data.cWidth = wid
    canvas.data.cHeight = high
    canvas.data.extraw = extraw
    canvas.data.margins = wid/16
    canvas.data.week = ['Monday','Tuesday','Wednesday','Thursday','Friday',
                        'Saturday','Sunday']
    canvas.data.colors = ['#CCFFCC','#CCCCFF','#FFFFCC',
                          '#FFCCCC','#CCFFFF','#FFCCFF']
    canvas.data.courses = {}
    init(canvas)
    root.bind("<Button-1>", mousePressed)
    #root.bind("<Key>", keyPressed)
    root.mainloop()

run()

