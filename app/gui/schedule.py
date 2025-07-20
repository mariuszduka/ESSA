'''
ESSA :: Electronic Grade Book Assistant
Copyright (C) 2025 Mariusz Duka
This file is part of ESSA and is licensed under the GNU GPLv3 or later.
See the LICENSE file for full text.
'''

import tkinter as tk
import ttkbootstrap as ttk
from tkinter.filedialog import askopenfilename

from functions import sort_human
from timetable import TimeTable

class Schedule(ttk.Frame):
    def __init__(self, parent, controller, platform): 
        ttk.Frame.__init__(self, parent, width=controller.view_width, height=controller.view_height)

        self.lock = False

        self.platform = platform
        self.controller = controller

        self.app_data_dir = self.controller.app_data_dir
        self.essa_config = self.controller.essa_config

        self.classes_checked = {}
        self.classes_available = {}
        self.classes_selected = {}

        # TOP FRAME
        self.main_frame = ttk.Frame(self)
        self.controller.top_menu_buttons(self.main_frame)

        self.req_data = {}
        self.req_data_idx = ''
        self.excel_dir = self.app_data_dir + '/' + self.essa_config['TimeTable.Excel']['ExcelFileDir']
        self.excel_file_name = self.essa_config['TimeTable.Excel']['ExcelFileName']
        self.excel_file_name_rooms = self.essa_config['TimeTable.Excel']['ExcelFileNameRooms']
        self.db_file = self.platform.db_dir + self.platform.db_timetable_file_name

        # LEFT FRAME
        self.left_frame = ttk.Frame(self)
        self.left_frame.pack(side='left', fill='none', padx=0, pady=(0,80), expand=True)

        label = ttk.Label(self.left_frame, width=45, text='STUNDU SARAKSTA VEIDOŠANA', font=(controller.default_font_name, 11, 'bold'))
        label.pack(fill='x', pady=(0,20), expand=True)

        # select lesson type to timetable
        self.timetable_lesson_s = ttk.BooleanVar()
        self.timetable_lesson_s.set(True)
        self.timetable_lesson_s_checkbox = ttk.Checkbutton(self.left_frame, text='Mācību stundas', variable=self.timetable_lesson_s, offvalue=False, onvalue=True)
        self.timetable_lesson_s_checkbox.pack(fill='x', anchor='w', expand=True, pady=(20,5))

        self.timetable_lesson_f = ttk.BooleanVar()
        self.timetable_lesson_f.set(True)
        self.timetable_lesson_f_checkbox = ttk.Checkbutton(self.left_frame, text='Fakultatīvi (F)', variable=self.timetable_lesson_f, offvalue=False, onvalue=True)
        self.timetable_lesson_f_checkbox.pack(fill='x', anchor='w', expand=True, pady=(5,5))

        self.timetable_lesson_i = ttk.BooleanVar()
        self.timetable_lesson_i.set(False)
        self.timetable_lesson_i_checkbox = ttk.Checkbutton(self.left_frame, text='Interešu izglītība (I)', variable=self.timetable_lesson_i, offvalue=False, onvalue=True)
        self.timetable_lesson_i_checkbox.pack(fill='x', anchor='w', expand=True, pady=(5,5))

        self.timetable_lesson_p = ttk.BooleanVar()
        self.timetable_lesson_p.set(False)
        self.timetable_lesson_p_checkbox = ttk.Checkbutton(self.left_frame, text='Pagarinātā dienas grupa (P)', variable=self.timetable_lesson_p, offvalue=False, onvalue=True)
        self.timetable_lesson_p_checkbox.pack(fill='x', anchor='w', expand=True, pady=(5,25))

        ttk.Label(self.left_frame, text = "Nedēļas dienu skaits:").pack(fill='none', anchor='w')
        self.timetable_days = ttk.IntVar()
        self.timetable_days.set(5)
        self.timetable_days_combobox = ttk.Combobox(self.left_frame, width=5, textvariable=self.timetable_days) 
        self.timetable_days_combobox['values'] = (1,2,3,4,5,6,7)
        self.timetable_days_combobox.pack(fill='none', anchor='w', expand=True, pady=(5,15))

        # create timetable
        self.create_timetable_button_1 = ttk.Button(self.left_frame, text='Klases', bootstyle='primary', command=lambda: self.create_timetable('C', self.timetable_lesson_s_checkbox.state(), self.timetable_lesson_f_checkbox.state(), self.timetable_lesson_i_checkbox.state(), self.timetable_lesson_p_checkbox.state()))
        self.create_timetable_button_1.pack(fill='none', anchor='w', side='left', expand=False, padx=(0,10), pady=(20,20))
        self.create_timetable_button_1.config(state='normal')

        self.create_timetable_button_2 = ttk.Button(self.left_frame, text='Telpas', bootstyle='primary', command=lambda: self.create_timetable('R', self.timetable_lesson_s_checkbox.state(), self.timetable_lesson_f_checkbox.state(), self.timetable_lesson_i_checkbox.state(), self.timetable_lesson_p_checkbox.state()))
        self.create_timetable_button_2.pack(fill='none', anchor='w', side='left', expand=False, pady=(20,20))
        self.create_timetable_button_2.config(state='normal')

        # create timetable
        self.open_excel_dir_button = ttk.Button(self.left_frame, text='Excel datu mape', bootstyle='primary', command=lambda: self.controller.open_dir(self.excel_dir))
        self.open_excel_dir_button.pack(fill='none', anchor='e', side='right', expand=False, pady=(20,20))

        # RIGHT FRAME
        right_frame = ttk.Frame(self)
        right_frame.pack(side='right', fill='none', padx=(10,140), pady=(0,80), expand=False)

        # FRAME 1
        self.scrolltext_label = ttk.Label(right_frame, text='KLASES', anchor='w', font=(controller.default_font_name, 11, 'bold'))
        self.scrolltext_label.pack(pady=(0,0), fill='x', expand=True)

        label = ttk.Label(right_frame, text='Izvēlies klases', anchor='w', font=(controller.default_font_name, 9, 'italic'))
        label.pack(pady=(0,0), fill='x', expand=False)

        self.scrolltext_timetable = ttk.ScrolledText(right_frame, width=34, height=14)
        self.scrolltext_timetable.pack(pady=(0,0), fill='x', expand=True)

        btn = ttk.Button(right_frame, text = '0', cursor='hand2', padding=3, command=lambda: self.select_classes('0')) 
        btn.pack(side='left', pady=5)
        btn = ttk.Button(right_frame, text = '1-3', cursor='hand2', padding=3, command=lambda: self.select_classes('1-3')) 
        btn.pack(side='left', padx=5, pady=5)
        btn = ttk.Button(right_frame, text = '4-6', cursor='hand2', padding=3, command=lambda: self.select_classes('4-6')) 
        btn.pack(side='left', pady=5)
        btn = ttk.Button(right_frame, text = '7-9', cursor='hand2', padding=3, command=lambda: self.select_classes('7-9')) 
        btn.pack(side='left', padx=5, pady=5)
        btn = ttk.Button(right_frame, text = '10-12', cursor='hand2', padding=3, command=lambda: self.select_classes('10-12')) 
        btn.pack(side='left', pady=5)
        btn = ttk.Button(right_frame, text = '+', cursor='hand2', padding=3, command=lambda: self.select_classes('+')) 
        btn.pack(side='right', pady=5)
        btn = ttk.Button(right_frame, text = '–', cursor='hand2', padding=3, command=lambda: self.select_classes('-')) 
        btn.pack(side='right', padx=5, pady=5)

        self.before()

    def before(self):
        self.classes_available = sort_human(self.platform.get_db_classes_names())
        self.scrolltext_timetable.delete(1.0, ttk.END)
        
        checked = []
        if len(self.classes_available) > 0:
            for idx, c in enumerate(self.classes_available):
                # print(c)
            
                self.classes_checked[idx] = ttk.IntVar(value=0)
                if c in self.classes_selected:
                    self.classes_checked[idx] = ttk.IntVar(value=1)
                    checked.append(self.classes_available[idx])

                cb = ttk.Checkbutton(self.scrolltext_timetable, text = c, 
                    variable = self.classes_checked[idx],
                    onvalue = 1, offvalue = 0, cursor = "hand2",
                    command = self.select_classes)

                self.scrolltext_timetable.window_create(ttk.END, window=cb)
                self.scrolltext_timetable.insert(ttk.END, '\t')

            self.req_data = checked
            self.req_data_idx = ','.join(checked)

        else:
            self.req_data = {}
            self.req_data_idx = ''

        # print(checked)
        # print(self.req_data)
    
    def after(self):
        pass

    def is_locked(self):
        return self.lock

    def select_classes(self, check=''):
        checked = []

        for idx, c in enumerate(self.classes_available):
            val = self.classes_checked[idx].get()
            # print(val)
            if val == 1:
                checked.append(self.classes_available[idx])
            # print(c)
            try:
                cl = int(c.split('.', 1)[0])
            except ValueError:
                cl = 0            
            # print(cl)
            if check == '+' or (check == '0' and int(cl) == 0) or (check == '1-3' and int(cl)>=1 and int(cl)<=3) or (check == '4-6' and int(cl)>=4 and int(cl)<=6) or (check == '7-9' and int(cl)>=7 and int(cl)<=9) or (check == '1-9' and int(cl)>=1 and int(cl)<=9) or (check == '10-12' and int(cl)>=10 and int(cl)<=12):
                if self.classes_available[idx] not in checked:
                    checked.append(self.classes_available[idx])

        if check == '-':
            checked = []
                
        self.req_data = checked
        self.req_data_idx = ','.join(checked)

        # print(self.req_data)
        # print(self.req_data_idx)
        
        self.classes_selected = checked
        self.before()

    def create_timetable(self, data = 'C', s=(), f=(), i=(), p=(), worksheet_name=''):
        # self.before()
        if len(self.req_data) == 0:
            self.controller.message_box('Informācija','Lai izveidot stundu sarakstu, izvēlies klases.')
            return False

        lesson_type = []
        if 'selected' in s:
            lesson_type.append('S')
        if 'selected' in f:
            lesson_type.append('F')
        if 'selected' in i:
            lesson_type.append('I')
        if 'selected' in p:
            lesson_type.append('P')

        # print(lesson_type)

        classes = {}
        rooms = {}
        if data == 'C': 
            classes = self.platform.get_db_classes_lessons(self.req_data, lesson_type, int(self.timetable_days.get()))
        elif data == 'R':
            rooms = self.platform.get_db_classes_rooms(self.req_data, lesson_type, int(self.timetable_days.get()))
        else:
            return False

        # print(classes)
        # print(self.platform.save_dir)

        if len(self.req_data)>0:
            # hack - update "for_classes"
            self.essa_config['TimeTable']['Classes'] = self.req_data_idx
            self.essa_config['TimeTable']['Days'] = str(self.timetable_days.get())

            try:
                timetable = TimeTable(classes=classes, rooms=rooms)
                timetable.set_config(self.essa_config)
                timetable.set_save_dir(self.app_data_dir)
                timetable.set_excel_worksheet_name(worksheet_name)
                timetable.set_excel_file_name(self.excel_file_name)
                timetable.set_excel_file_name_rooms(self.excel_file_name_rooms)
                timetable.set_excel_file_name_date(False)
                # print(timetable.getConfig())
                if data == 'C':
                    create = timetable.create_timetable_classes()
                elif data == 'R':
                    create = timetable.create_timetable_rooms()
                if create == True:
                    # print('Done!')
                    self.controller.open_dir(timetable.get_excel_full_file_name())
                elif create == -1:
                    self.controller.message_box('Informācija','Fails jau ir atvērts programmā Excel.\nLūdzu, aizver failu un mēģini vēlreiz.')
            except:
                self.controller.message_box('Kļūda','Veidojot stundu sarakstu, radās problēma.')