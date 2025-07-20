'''
ESSA :: Electronic Grade Book Assistant
Copyright (C) 2025 Mariusz Duka
This file is part of ESSA and is licensed under the GNU GPLv3 or later.
See the LICENSE file for full text.
'''

import os
import tkinter as tk
import ttkbootstrap as ttk
import xlsxwriter
from datetime import date

# encrypt SQLite3
try:
    from sqlcipher3 import dbapi2 as sqlite3
except ModuleNotFoundError as err:
    import sqlite3

from functions import remove_html_tags
from functions import sort_human

import locale
locale.setlocale(locale.LC_ALL, "lv_LV.UTF-8")

class JournalSR(ttk.Frame):
    def __init__(self, parent, controller, platform): 
        ttk.Frame.__init__(self, parent, width=controller.view_width, height=controller.view_height)

        self.bind("<<ShowFrame>>", self.on_show_frame)

        self.lock = False

        self.platform = platform
        self.controller = controller

        self.app_data_dir = self.controller.app_data_dir
        self.essa_config = self.controller.essa_config

        self.sql_query = ''
        self.sql_query_params = {}
        self.sql_query_result = []

        self.excel_dir = self.app_data_dir + '/' + self.essa_config['Journal.Excel']['ExcelFileDir']
        self.excel_file_name = self.essa_config['Journal.Excel']['ExcelSRFileName']
        self.excel_file_name_ext = self.essa_config['Journal.Excel']['ExcelFileNameExt']

        # TOP FRAME
        self.main_frame = ttk.Frame(self)
        self.controller.top_menu_buttons(self.main_frame)

        # LEFT FRAME
        self.left_frame_sr = ttk.Frame(self)
        self.left_frame_sr.pack(fill='none', padx=10, pady=(0,10), expand=True)

        label = ttk.Label(self.left_frame_sr, text='SKOLAS ŽURNĀLA ANALĪZE', justify='center', font=(controller.default_font_name, 11, 'bold'))
        label.pack(pady=(0,0), expand=True)

        label = ttk.Label(self.left_frame_sr, text='Informācija par mācību stundu tēmām (citā krāsā - nav norādīts “SR”)', justify='center', font=(controller.default_font_name, 9, 'italic'))
        label.pack(pady=(0,10), expand=False)

        style = ttk.Style()
        style.configure("mystyle.Treeview", highlightthickness=0, bd=0, font=(controller.default_font_name, 9, 'normal')) # Modify the font of the body
        style.configure("mystyle.Treeview.Heading", font=(controller.default_font_name, 9, 'bold')) # Modify the font of the headings
        # style.layout("mystyle.Treeview", [('mystyle.Treeview.treearea', {'sticky': 'nswe'})])

        tree_scroll_x = ttk.Scrollbar(self.left_frame_sr, orient=tk.HORIZONTAL)
        tree_scroll_y = ttk.Scrollbar(self.left_frame_sr, orient=tk.VERTICAL)

        # SR
        columns = ('date', 'class', 'teacher', 'discipline', 'type', 'subject')
        self.tree = ttk.Treeview(self.left_frame_sr, columns=columns, show='headings', height=17, cursor="hand2", style="mystyle.Treeview", xscrollcommand=tree_scroll_x.set, yscrollcommand=tree_scroll_y.set)

        self.tree.heading('date', text='Datums', anchor='w', command=lambda: self.treeview_sort_column(self.tree, 'date', False))
        self.tree.column('date', minwidth=70, width=80, stretch=False)

        self.tree.heading('class', text='Klase', anchor='w', command=lambda: self.treeview_sort_column(self.tree, 'class', False))
        self.tree.column('class', minwidth=50, width=50, anchor='e', stretch=False)

        self.tree.heading('teacher', text='Skolotājs', anchor='w', command=lambda: self.treeview_sort_column(self.tree, 'teacher', False))
        self.tree.column('teacher', minwidth=50, width=205, stretch=False)

        self.tree.heading('discipline', text='Priekšmets', anchor='w', command=lambda: self.treeview_sort_column(self.tree, 'discipline', False))
        self.tree.column('discipline', minwidth=50, width=200, stretch=False)

        self.tree.heading('type', text='Met.', anchor='w', command=lambda: self.treeview_sort_column(self.tree, 'type', False))
        self.tree.column('type', minwidth=40, width=40, stretch=False)

        self.tree.heading('subject', text='Tēma (SR)', anchor='w', command=lambda: self.treeview_sort_column(self.tree, 'subject', False))
        self.tree.column('subject', minwidth=50, width=490, stretch=False)

        # attach a scrollbar to the frame
        tree_scroll_x.config(command=self.tree.xview)
        tree_scroll_x.pack(side=tk.BOTTOM, fill=tk.X)

        tree_scroll_y.config(command=self.tree.yview)
        tree_scroll_y.pack(side=tk.RIGHT, fill=tk.Y)

        self.tree.tag_configure('mark', foreground='#993300')
        self.tree.bind('<<TreeviewSelect>>', self.item_selected)
        self.tree.bind("<Double-1>", self.item_show_info)

        self.tree.tag_configure('highlight', background='LightSalmon')
        self.tree.bind("<Motion>", self.highlight_row)

        self.tree.pack()

        # BOTTOM FRAME TITLE
        self.bottom_frame_title = ttk.Frame(self)
        self.bottom_frame_title.pack(fill='none', padx=(0,0), pady=(0,0))

        password_label = ttk.Label(self.bottom_frame_title, text='Skolotājs', width=29, font=(controller.default_font_name, 9, 'bold'))
        password_label.pack(side='left', padx=(0,10))

        password_label = ttk.Label(self.bottom_frame_title, text='Klase', width=12, font=(controller.default_font_name, 9, 'bold'))
        password_label.pack(side='left', padx=(0,10))

        password_label = ttk.Label(self.bottom_frame_title, text='Veids', width=12, font=(controller.default_font_name, 9, 'bold'))
        password_label.pack(side='left', padx=(0,10))

        password_label = ttk.Label(self.bottom_frame_title, text='Priekšmets', width=42, font=(controller.default_font_name, 9, 'bold'))
        password_label.pack(side='left', padx=(0,10))

        # BOTTOM FRAME
        self.bottom_frame = ttk.Frame(self)
        self.bottom_frame.pack(fill='none', padx=(10,10), pady=(0,100))

        self.teacher_selected = ttk.StringVar()
        self.teacher_combo = ttk.Combobox(self.bottom_frame, width=30, textvariable=self.teacher_selected)      
        self.teacher_combo.bind('<<ComboboxSelected>>', self.teacher_combo_selected)
        self.teacher_combo.pack(side='left', padx=(0,10))        

        self.classes_selected = ttk.StringVar()
        self.classes_combo = ttk.Combobox(self.bottom_frame, width=10, textvariable=self.classes_selected)
        self.classes_combo.bind('<<ComboboxSelected>>', self.classes_combo_selected)
        self.classes_combo.pack(side='left', padx=(0,10))

        self.discipline_type_selected = ttk.StringVar()
        self.discipline_type_combo = ttk.Combobox(self.bottom_frame, width=10, textvariable=self.discipline_type_selected)
        self.discipline_type_combo.bind('<<ComboboxSelected>>', self.discipline_type_combo_selected)
        self.discipline_type_combo.pack(side='left', padx=(0,10))

        self.discipline_selected = ttk.StringVar()
        self.discipline_combo = ttk.Combobox(self.bottom_frame, width=30, textvariable=self.discipline_selected)
        self.discipline_combo.bind('<<ComboboxSelected>>', self.discipline_combo_selected)
        self.discipline_combo.pack(side='left', padx=(0,10))

        self.excel_button = ttk.Button(self.bottom_frame, text='↓ Excel', cursor='hand2', command=lambda: self.save_to_excel(True)) 
        self.excel_button.pack(side='left', padx=(20,0))

    def fix_tree_column(self):
        self.tree.column('subject', width=2000)

    def before(self):
        teachers, classes, disciplines, discipline_types = self.sql_select_params()

        prefix = '––– VISS –––'

        if len(teachers) > 0: 
            if teachers[0] != prefix:
                teachers.insert(0, prefix)
            self.teacher_combo['values'] = teachers
            try:
                self.teacher_combo.set(self.sql_query_params['teacher'])
            except:
                self.teacher_combo.current(0)

        if len(classes) > 0:
            if classes[0] != prefix:
                classes.insert(0, prefix)
            self.classes_combo['values'] = classes
            try:
                self.classes_combo.set(self.sql_query_params['class'])
            except:
                self.classes_combo.current(0)

        if len(disciplines) > 0:
            if disciplines[0] != prefix:
                disciplines.insert(0, prefix)
            self.discipline_combo['values'] = disciplines
            try:
                self.discipline_combo.set(self.sql_query_params['discipline'])
            except:
                self.discipline_combo.current(0)

        if len(discipline_types) > 0:
            if discipline_types[0] != prefix:
                discipline_types.insert(0, prefix)
            self.discipline_type_combo['values'] = discipline_types
            try:
                self.discipline_type_combo.set(self.sql_query_params['discipline_type'])
            except:
                self.discipline_type_combo.current(0)

        self.fix_tree_column()
        self.update_list()

    def after(self):
        pass

    def on_show_frame(self, event):
        # print("I am being shown...")
        pass

    def is_locked(self):
        return self.lock

    def lock_frame(self):
        self.lock = True
        self.excel_button.config(state='disabled')
        self.controller.update_menu_states(ttk.DISABLED)

    def unlock_frame(self):
        self.lock = False
        self.excel_button.config(state='normal')
        self.controller.update_menu_states(ttk.NORMAL)

    def update_list(self):
        self.lock_frame()

        today = date.today()
        self.sql_query_result = []
        db_file_name = self.platform.db_dir + self.platform.db_journal_file_name

        if not os.path.exists(db_file_name):
            # reset treeview
            for row in self.tree.get_children():
                self.tree.delete(row)
            self.unlock_frame()
            return self.sql_query_result

        try:
            with sqlite3.connect(db_file_name) as conn: 
                cur = conn.cursor()

                if self.platform.db_encrypt:
                    if not self.platform.set_db_pragma(conn):
                        return False

                sql_query = """SELECT lesson_date, class_name, teacher_first_name, teacher_last_name, discipline_name, discipline_type, lesson_subject, lesson_type_id, lesson_type_name FROM "main"."v_teacher_lessons" """
                
                sql_where = []
                try:
                    if self.sql_query_params['teacher'] != '':
                        sql_where.append('concat(teacher_last_name, " ", teacher_first_name) = "' + self.sql_query_params['teacher'] + '"')
                except:
                    pass
                try:
                    if self.sql_query_params['class'] != '':
                        sql_where.append('class_name = "' + self.sql_query_params['class'] + '"')
                except:
                    pass
                try:
                    if self.sql_query_params['discipline'] != '':
                        sql_where.append('discipline_name = "' + self.sql_query_params['discipline'] + '"')
                except:
                    pass
                try:
                    if self.sql_query_params['discipline_type'] != '':
                        discipline_type = self.sql_query_params['discipline_type'].lower()
                        if '(f)' in discipline_type:
                            discipline_type = 'F'
                        elif '(i)' in discipline_type:
                            discipline_type = 'I'
                        else:
                            discipline_type = 'S'
                        sql_where.append('discipline_type = "' + discipline_type + '"')
                except:
                    pass

                if len(sql_where) > 0:
                    sql_query +='WHERE ' + ' AND '.join(sql_where)

                sql_query += """ ORDER BY lesson_date DESC, teacher_last_name ASC LIMIT 49999 OFFSET 0;"""

                # print(sql_query)

                cur.execute(sql_query)
                
                self.sql_query_result = cur.fetchall()
                # self.sql_query_result.sort(key=lambda x: x[0])

                # print("Total rows are:", len(self.sql_query_result))
                # print(records[0])

                cur.close()

                # update treeview
                for row in self.tree.get_children():
                    self.tree.delete(row)

                search_list = tuple(x.strip() for x in self.essa_config['Journal']['ExpectedResultsTags'].split(','))
                # print(search_list)

                for idx, record in enumerate(self.sql_query_result):
                    subject = remove_html_tags(record[6]) # re.sub(r"<.*?>", "", record[6])
                    subject_lower = subject.lower()
                    discipline_lower = record[4].lower()
                    tag = 'mark'
                    for word in search_list:
                        if record[5] != 'S' or discipline_lower == 'klases stunda' or discipline_lower[-3:] == '(p)' or (str(record[0][:10]) > str(today)) or word.lower() in subject_lower:
                            tag = ''
                            break

                    # 'date', 'class', 'teacher', 'discipline', 'type', 'subject'
                    values = (record[0][:10], record[1], record[3]+' '+record[2], record[4], record[8][:3]+'.', subject)

                    self.tree.insert('', tk.END, iid=idx, values=values, tags=(tag))

            conn.close()

        except sqlite3.Error as error:
            print("Failed to read data from sqlite table", error)

        finally:
            self.unlock_frame()
            return self.sql_query_result

    def sql_select_params(self):        

        teachers = []
        classes = []
        disciplines = []
        # discipline_types = ['Stundas', 'Fakultatīvi (F)', 'Pulciņi (I)']
        discipline_types = []

        # check cache
        if self.controller.journal_sql_query_params_cache != []:
            return self.controller.journal_sql_query_params_cache

        db_file_name = self.platform.db_dir + self.platform.db_journal_file_name
        
        if not os.path.exists(db_file_name):
            return teachers, classes, disciplines, discipline_types

        try:
            with sqlite3.connect(db_file_name) as conn:                
                cur = conn.cursor()

                if self.platform.db_encrypt:
                    if not self.platform.set_db_pragma(conn):
                        return False

                sql_query = """SELECT DISTINCT teacher_first_name, teacher_last_name, class_name, discipline_name, discipline_type FROM "main"."v_teacher_lessons" LIMIT 49999 OFFSET 0;"""
                cur.execute(sql_query)
                records = cur.fetchall()
                # print("Total rows are:", len(records))
                # print(records[0])

                cur.close()

                for record in records:
                    teachers.append(record[1]+' '+record[0])
                    classes.append(record[2])
                    disciplines.append(record[3])
                    discipline_types.append(record[4])

                teachers.sort()
                teachers = list(dict.fromkeys(teachers))
                # print(teachers)

                classes = sort_human(classes)
                classes = list(dict.fromkeys(classes))
                # print(classes)

                disciplines.sort()
                disciplines = list(dict.fromkeys(disciplines))
                # print(disciplines)
            
                discipline_types.sort()
                discipline_types = list(dict.fromkeys(discipline_types))
                # print(discipline_types)

                tmp = []
                if 'S' in discipline_types:
                    tmp.append('Stundas')
                if 'F' in discipline_types:
                    tmp.append('Fakultatīvi (F)')
                if 'I' in discipline_types:
                    tmp.append('Pulciņi (I)')
                discipline_types = tmp

            conn.close()

        except sqlite3.Error as error:
            print("Failed to read data from sqlite table", error)

        finally:
            self.controller.journal_sql_query_params_cache = (teachers, classes, disciplines, discipline_types)
            return self.controller.journal_sql_query_params_cache

    def teacher_combo_selected(self, event):        
        # print(self.teacher_selected.get())
        self.sql_query_params['teacher'] = self.teacher_selected.get() if self.teacher_selected.get() != '––– VISS –––' else ''
        self.update_list()

    def classes_combo_selected(self, event):
        # print(self.classes_selected.get())
        self.sql_query_params['class'] = self.classes_selected.get() if self.classes_selected.get() != '––– VISS –––' else ''
        self.update_list()

    def discipline_combo_selected(self, event):
        # print(self.discipline_selected.get())
        self.sql_query_params['discipline'] = self.discipline_selected.get() if self.discipline_selected.get() != '––– VISS –––' else ''
        self.update_list()        

    def discipline_type_combo_selected(self, event):
        # print(self.discipline_type_selected.get())
        self.sql_query_params['discipline_type'] = self.discipline_type_selected.get() if self.discipline_type_selected.get() != '––– VISS –––' else ''
        self.update_list()

    def item_selected(self, event):
        for selected_item in self.tree.selection():
            item = self.tree.item(selected_item)
            record = item['values']
            # show a message
            # print(','.join(record))

    def item_show_info(self, event):
        iid = self.tree.focus()
        if iid != '':
            record = self.sql_query_result[int(iid)]
            # print(record)
            self.controller.message_box(
                'Informācija',record[2]+' '+record[3]+', '+record[1]+' '+record[4]+', '+record[0][:10]+'\n\nMetodika: '+record[8]+'\n\nTēma (SR): '+remove_html_tags(record[6]),
                window_width=600, window_height=300)

    def highlight_row(self, event):
        tree = event.widget
        item = self.tree.identify_row(event.y)
        tree.tk.call(tree, "tag", "remove", "highlight")
        tree.tk.call(tree, "tag", "add", "highlight", item)

    def treeview_sort_column(self, tv, col, reverse):
        l = [(tv.set(k, col), k) for k in tv.get_children('')]
        try:
            l.sort(key=lambda t: float(t[0]) if t[0] != '-' else 0, reverse=reverse)
        except ValueError:
            l.sort(reverse=reverse)

        for index, (val, k) in enumerate(l):
            tv.move(k, '', index)

        tv.heading(col, command=lambda: self.treeview_sort_column(tv, col, not reverse))

    def save_to_excel(self, open_file=False):
        try:
            workbook = xlsxwriter.Workbook(self.excel_dir + '/' + self.excel_file_name + '.' + self.excel_file_name_ext)
            worksheet = workbook.add_worksheet()

            bold = workbook.add_format({'bold': True})
            worksheet.write('A1', 'Datums', bold)
            worksheet.write('B1', 'Klase', bold)
            worksheet.write('C1', 'Skolotājs', bold)
            worksheet.write('D1', 'Priekšmets', bold)
            worksheet.write('E1', 'Metodika', bold)

            # SR
            worksheet.write('F1', 'Tēma', bold)

            row = 1
            col = 0

            for record in self.sql_query_result:
                worksheet.write(row, col,   record[0][:10])
                worksheet.write(row, col+1, record[1])
                worksheet.write(row, col+2, record[2]+' '+record[3])
                worksheet.write(row, col+3, record[4])
                worksheet.write(row, col+4, record[8])

                # SR
                worksheet.write(row, col+5, remove_html_tags(record[6])) # re.sub(r"<.*?>", "", record[6])

                row += 1

            workbook.close()

            if open_file:
                self.controller.open_dir(self.excel_dir + '/' + self.excel_file_name + '.' + self.excel_file_name_ext)
        except:
            pass