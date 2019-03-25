# -*- coding: utf-8 -*-
"""
Created on Mon Mar 25 12:32:34 2019

@author: johan
"""

from tkinter import *
from tkinter import filedialog
from tkinter import messagebox
from tkinter.ttk import Progressbar
import preprocess_tool



prop = None

def getTifFilePath():
    
    input_file = filedialog.askopenfilename(filetypes = [("Tif Dateien", "*.tif")])
    if not input_file == "":
        tif_path_input.delete(0,END)
        tif_path_input.insert(0,input_file)
        print(input_file)

def getOutputDirectory():
    output_dir = filedialog.askdirectory()
    if not output_dir == "":
        output_path_input.delete(0,END)
        output_path_input.insert(0,output_dir)
        print(output_dir)
    
def run():
    if run_button['text'] == "Run":
        global prop
        prop = preprocess_tool.PreprocessTool()
        error = prop.preprocess(tif_path_input.get(),output_path_input.get(), process_callback)
        if error == "":
            run_button.configure(text="Cancel")
        else:
            messagebox.showinfo('Error', error)
    elif run_button['text'] == "Cancel":
        prop.stop()
        run_button['text'] = "Please Wait..."
    
def process_callback(progress):
    if progress == 999:
        run_button.configure(text="Run")
        progress_bar['value'] = 0.0
    else:
        progress_bar['value'] = progress*100
        if(progress == 1.0):
            messagebox.showinfo('Success', "Done")
            run_button.configure(text="Run")

    
window = Tk()
window.geometry('550x170')


window.columnconfigure(1, weight=1)
window.title("Image Preprocessing")

lbl = Label(window, justify=LEFT, text="Please select a Geo Referenced Image File and an output location and click 'Run'. \n\nThe program will output a folder which can then be copied onto an Android tablet for the annotation.")
lbl.grid(column=0, row=0, pady=5, padx = 5, columnspan=4, sticky=W)

open_tif_button = Button(window, text="Select Tif File",command=getTifFilePath)
open_tif_button.grid(column=3, row=10, pady=5, padx = 5, sticky=W)
open_tif_label = Label(window,justify=LEFT, text="Input File: ")
open_tif_label.grid(column=0, row=10, pady=5, padx = 5, columnspan=1, sticky=W)
tif_path_input = Entry(window, width=200)
tif_path_input.grid(column=1, row=10, pady=5, padx = 5, columnspan=2, sticky=W)


open_output_dir_button = Button(window, text="Select Output Folder",command=getOutputDirectory)
open_output_dir_button.grid(column=3, row=11, pady=5, padx = 5, sticky=W)
open_output_label = Label(window,justify=LEFT, text="Output Folder: ")
open_output_label.grid(column=0, row=11, pady=5, padx = 5, columnspan=1, sticky=W)
output_path_input = Entry(window,width=200)
output_path_input.grid(column=1, row=11, pady=5, padx = 5, columnspan=2, sticky=W)


run_button = Button(window, text="Run",command=run)
run_button.grid(column=3, row=12, pady=5, padx = 5, sticky=W)



progress_bar = Progressbar(window, length=10000)
progress_bar.grid(column=0, row=12, pady=5, padx = 5, sticky=W, columnspan=3)
progress_bar['value'] = 0



in_path = 'C:/Users/johan/Desktop/Resources/orthoJPEG.tif'
tif_path_input.insert(0,in_path)
out_path = 'C:/Users/johan/Desktop/Resources/Test/'
output_path_input.insert(0,out_path)



window.mainloop()
