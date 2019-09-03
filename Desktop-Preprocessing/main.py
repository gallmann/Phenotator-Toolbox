# -*- coding: utf-8 -*-
"""
Created on Mon Mar 25 12:32:34 2019

This class uses tkinter to build and handle the UI for the Proprocessing Tool

@author: johan
"""



from tkinter import Tk
from tkinter import END
from tkinter import Label
from tkinter import LEFT
from tkinter import W
from tkinter import Button
from tkinter import Entry
from tkinter import filedialog
from tkinter import messagebox
from tkinter.ttk import Progressbar
from tkinter.ttk import Notebook
from tkinter.ttk import Frame
import preprocess_tool
import sys
import os
import postprocessing

pre_tool = None
post_tool = None

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def getPostProcessingInputFolder():
    input_dir = filedialog.askdirectory()
    if not input_dir == "":
        #Update UI
        input_folder_input_2.delete(0,END)
        input_folder_input_2.insert(0,input_dir)
        print(input_dir)

def getPostProcessingOutputFolder():
    output_dir = filedialog.askdirectory()
    if not output_dir == "":
        #Update UI
        output_path_input_2.delete(0,END)
        output_path_input_2.insert(0,output_dir)
        print(output_dir)


def getTifFilePath():
    input_file = filedialog.askopenfilename(filetypes = [("Tif Dateien", "*.tif")])
    if not input_file == "":
        #Update UI
        tif_path_input.delete(0,END)
        tif_path_input.insert(0,input_file)
        print(input_file)

def getOutputDirectory():
    output_dir = filedialog.askdirectory()
    if not output_dir == "":
        #Update UI
        output_path_input.delete(0,END)
        output_path_input.insert(0,output_dir)
        print(output_dir)

def run_postprocessing():
    progress_bar_2['value'] = 0.01
    global post_tool
    post_tool = postprocessing.PostprocessTool()
    error = post_tool.make_shape_files(input_folder_input_2.get(),output_path_input_2.get())
    if not error == "":
        messagebox.showinfo('Error', error)
    else:
        progress_bar_2['value'] = 100
        messagebox.showinfo('Success', "Done")
        progress_bar_2['value'] = 0

    
def run_preprocessing():
    if run_button['text'] == "Run":
        
        global pre_tool
        pre_tool = preprocess_tool.PreprocessTool()
        error = pre_tool.preprocess(tif_path_input.get(),output_path_input.get(), process_callback)
        if error == "":
            run_button.configure(text="Cancel")
        else:
            messagebox.showinfo('Error', error)
    elif run_button['text'] == "Cancel":
        pre_tool.stop()
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

    
    

main_window = Tk()
main_window.geometry('550x195')
main_window.iconbitmap(resource_path('flower.ico'))


main_window.title("Image Processing")

tabControl = Notebook(main_window)





'''Init Tab 1'''
tab1 = Frame(tabControl)
tab1.columnconfigure(1, weight=1)


lbl = Label(tab1, justify=LEFT, text="Please select a Geo Referenced Image File and an output location and click 'Run'. \n\nThe program will output a folder which can then be copied onto an Android tablet for the annotation.")
lbl.grid(column=0, row=0, pady=5, padx = 5, columnspan=4, sticky=W)

open_tif_button = Button(tab1, text="Select Tif File",command=getTifFilePath)
open_tif_button.grid(column=3, row=10, pady=5, padx = 5, sticky=W)
open_tif_label = Label(tab1,justify=LEFT, text="Input File: ")
open_tif_label.grid(column=0, row=10, pady=5, padx = 5, columnspan=1, sticky=W)
tif_path_input = Entry(tab1, width=200)
tif_path_input.grid(column=1, row=10, pady=5, padx = 5, columnspan=2, sticky=W)


open_output_dir_button = Button(tab1, text="Select Output Folder",command=getOutputDirectory)
open_output_dir_button.grid(column=3, row=11, pady=5, padx = 5, sticky=W)
open_output_label = Label(tab1,justify=LEFT, text="Output Folder: ")
open_output_label.grid(column=0, row=11, pady=5, padx = 5, columnspan=1, sticky=W)
output_path_input = Entry(tab1,width=200)
output_path_input.grid(column=1, row=11, pady=5, padx = 5, columnspan=2, sticky=W)


run_button = Button(tab1, text="Run",command=run_preprocessing)
run_button.grid(column=3, row=12, pady=5, padx = 5, sticky=W)



progress_bar = Progressbar(tab1, length=10000)
progress_bar.grid(column=0, row=12, pady=5, padx = 5, sticky=W, columnspan=3)
progress_bar['value'] = 0

tabControl.add(tab1, text='Preprocessing')




'''Init tab 2'''

tab2 = Frame(tabControl)
tab2.columnconfigure(1, weight=1)

lbl_2 = Label(tab2, justify=LEFT, text="Please select an input folder and an output folder and click 'Export'.\n\nThis will export all Annotations from the input folder to the output folder as shape files.")
lbl_2.grid(column=0, row=0, pady=5, padx = 5, columnspan=4, sticky=W)

select_input_folder_button = Button(tab2, text="Select Input Folder",command=getPostProcessingInputFolder)
select_input_folder_button.grid(column=3, row=10, pady=5, padx = 5, sticky=W)
input_folder_label = Label(tab2,justify=LEFT, text="Input Folder: ")
input_folder_label.grid(column=0, row=10, pady=5, padx = 5, columnspan=1, sticky=W)
input_folder_input_2 = Entry(tab2, width=200)
input_folder_input_2.grid(column=1, row=10, pady=5, padx = 5, columnspan=2, sticky=W)


select_output_folder_button = Button(tab2, text="Select Output Folder",command=getPostProcessingOutputFolder)
select_output_folder_button.grid(column=3, row=11, pady=5, padx = 5, sticky=W)
open_output_label_2 = Label(tab2,justify=LEFT, text="Output Folder: ")
open_output_label_2.grid(column=0, row=11, pady=5, padx = 5, columnspan=1, sticky=W)
output_path_input_2 = Entry(tab2,width=200)
output_path_input_2.grid(column=1, row=11, pady=5, padx = 5, columnspan=2, sticky=W)


export_button = Button(tab2, text="Export",command=run_postprocessing)
export_button.grid(column=3, row=12, pady=5, padx = 5, sticky=W)



progress_bar_2 = Progressbar(tab2, length=10000)
progress_bar_2.grid(column=0, row=12, pady=5, padx = 5, sticky=W, columnspan=3)
progress_bar_2['value'] = 0

tabControl.add(tab2, text="Postprocessing")

tabControl.pack(expand=True, fill="both")  # Pack to make visible





'''
in_path = 'C:/Users/johan/Desktop/test/ortho_june06.tif'
tif_path_input.insert(0,in_path)
out_path = 'C:/Users/johan/Desktop/test1'
output_path_input.insert(0,out_path)
'''


main_window.mainloop()
