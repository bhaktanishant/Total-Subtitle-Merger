#!/usr/bin/env python

from Tkinter import Tk, Listbox, Button, Scrollbar, Canvas, Frame, Label
from subprocess import call
from threading import Thread
import os, tkMessageBox
from time import sleep

class MergeApp:
    
    def __init__(self, root):
        self.root = root
        self.title = "Subtitle Merger By - Nishant Bhakta"
        self.messageBoxTitle = "Message Box"
        self.cancelWarning = "The video which has been started to merge will be merge, rest will be cancel."
        self.movieListBox = Listbox(self.root)
        self.scrollBar = Scrollbar(self.root)
        self.startButton = Button(self.root, text = "start", state = "disable", command = self.startMerging)
        self.cancelButton = Button(self.root, text = "Stop", state = "disable", command = self.stopMerging)
        self.finishButton = Button(self.root, text = "Exit", state = "normal", command = self.endApplication)
        self.loadingLabel = Label(self.root)
        self.processState = Label(self.root)
        self.movieMap = {}
        self.keyList = []
        self.loadingIcons = ["--", "\\", "|", "/"]
        self.wantToMerge = True
        self.loading = False
        self.warningMessageLoaded = False
        
    def start(self):
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        # calculate position x and y coordinates
        x = (screen_width/2) - (700/2)
        y = (screen_height/2) - (300/2)
        self.root.geometry('%dx%d+%d+%d' % (700, 300, x, y))
        
        self.root.title(self.title)
        self.movieListBox.config(width = 68, yscrollcommand = self.scrollBar.set)
        self.movieListBox.pack(side = "left", fill = "y")
        self.scrollBar.config(command = self.movieListBox.yview)
        self.scrollBar.pack(fill = "y", side = "left")
        self.startButton.pack(fill = "x")
        self.cancelButton.pack(fill = "x")
        self.finishButton.pack(fill = "x")
        self.processState.pack(fill = "x", side = "bottom")        
        self.loadingLabel.pack(fill = "x", side = "bottom")
        Thread(target = self.createMovieMap).start()
        self.mainThread = Thread(target = self.startMerge)
        self.root.protocol("WM_DELETE_WINDOW", self.ifCloseWindow)
        self.root.mainloop()
        
    def createMovieMap(self):
        #Looking for subtitle
        index = 0
        Thread(target = self.startLoading, args = (True, )).start()
        self.processState.config(text = "Searching Videos..")
        for oneWalk in os.walk(os.getcwd()):
            for fileName in oneWalk[2]:
                if ".srt" in fileName:
                    subtitleName = fileName
                    #Now looking for movie with the name of subtitle
                    for oneWalk in os.walk(os.getcwd()):
                        for fileName in oneWalk[2]:
                            if ".srt" not in fileName:
                                key = subtitleName.replace(".srt", "")
                                if key in fileName:
                                    movieName = fileName
                                    if key not in self.movieMap:
                                        self.movieMap[key] = dict([("subtitleUri", oneWalk[0] + "/" + subtitleName)
                                            , ("movieUri", oneWalk[0] + "/" + movieName)
                                            , ("moviePath", oneWalk[0])])
                                        self.movieListBox.insert(index, " Queued - " + key)
                                        self.keyList.append(key)
                                        index += 1
        self.startButton.config(state = "normal")
        self.processState.config(text = "Search Complete.")
        self.loading = False
        
    def startMerge(self):
        self.changeButtonState()
        for key, value in self.movieMap.iteritems():
            if self.wantToMerge:
                self.processState.config(text = "Merging Video..")
                Thread(target = self.startLoading, args = (True, )).start()
                index = self.keyList.index(key)
                self.movieListBox.delete(index)
                self.movieListBox.insert(index, " Merging - " + key)
                self.movieListBox.itemconfig(index, bg = "yellow")
                if (call(["mkvmerge", "-o", value['moviePath'] + "/merging", value['movieUri'], value['subtitleUri']]) == 0):
                    call(["rm", value['movieUri'], value['subtitleUri']])
                    call(["mv", value['moviePath'] + "/merging", value['moviePath'] + "/"+ key + ".mkv"])
                    self.movieListBox.delete(index)
                    self.movieListBox.insert(index, " Successful - " + key)
                    self.movieListBox.itemconfig(index, bg = "green")
                else:
                    for name in os.listdir(value['moviePath'] + "/"):
                        if name == "merging":
                            call(["rm", value['moviePath'] + "/merging"])
                    self.movieListBox.delete(index)
                    self.movieListBox.insert(index, " Failed - "+ key)
                    self.movieListBox.itemconfig(index, bg = "red", foreground = "white")
            else:
                break
        self.loading = False
       	self.cancelButton.config(state = "disable")
       	self.finishButton.config(state = "normal")
        if self.wantToMerge:
            self.processState.config(text = "Merge Complete.")
            
    def startLoading(self, loadOrNot):
        self.loading = loadOrNot
        while self.loading:
            for icon in self.loadingIcons:
                self.loadingLabel.config(text = icon)
                sleep(.2)
                
    def startMerging(self):
        self.mainThread.start()
        
    def changeButtonState(self):
        self.startButton.config(state = "disable")
        self.cancelButton.config(state = "normal")
        self.finishButton.config(state = "disable")  
        
    def stopMerging(self):
        self.wantToMerge = False
        self.startButton.config(state = "disable")
        self.cancelButton.config(state = "disable")
        self.finishButton.config(state = "normal")
        self.processState.config(text = "Merge Canceled.")
        if not self.warningMessageLoaded:
            tkMessageBox.showwarning(self.messageBoxTitle, self.cancelWarning)
            self.warningMessageLoaded = True
       
    def endApplication(self):
        self.root.destroy()
    
    def ifCloseWindow(self):
        if self.mainThread.is_alive():
            self.stopMerging()
        self.endApplication()
        
if __name__ == "__main__":
    tk = Tk()
    app = MergeApp(tk)
    app.start()
