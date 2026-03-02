import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter.ttk import *
from tkinter import scrolledtext
from tkinter.font import Font
from tkinter import Menu
from tkinter.dnd import DndHandler
import os
import sys

class MainUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("HesterIDE-alpha1.0")
        self.geometry("800x600")
        self.create_widget()
    def create_widget(self):
        self.menu=Menu(self)
        self.file=Menu(self.menu)
        self.edit=Menu(self.menu)
        
        self.file.add_command(label="New",command=self.callback)
        self.file.add_command(label="Open",command=self.callback)
        self.file.add_command(label="Save",command=self.callback)
        self.file.add_command(label="Save as",command=self.callback)
        self.menu.add_cascade(label="File",menu=self.file)
        self.edit.add_command(label="Undo",command=self.callback)
        self.edit.add_command(label="Redo",command=self.callback)
        self.edit.add_command(label="Cut",command=self.callback)
        self.edit.add_command(label="Copy",command=self.callback)
        self.edit.add_command(label="Paste",command=self.callback)
        self.edit.add_command(label="Search",command=self.callback)
        self.menu.add_cascade(label="Edit",menu=self.edit)
        self.config(menu=self.menu)
        # 编辑区：先创建容器，再创建 Text 和 Scrollbar，正确关联它们
        self.textarea = tk.Frame(self)
        self.text = tk.Text(self.textarea, width=80, height=30)
        self.sb = tk.Scrollbar(self.textarea, orient=tk.VERTICAL,
                               command=self.text.yview)
        self.text.configure(yscrollcommand=self.sb.set)
        self.text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.sb.pack(side=tk.RIGHT, fill=tk.Y)
        self.textarea.pack(fill=tk.BOTH, expand=True)
        
        
       

    
    def callback(self):
        pass

if __name__ == "__main__":
    app=MainUI()
    app.mainloop()