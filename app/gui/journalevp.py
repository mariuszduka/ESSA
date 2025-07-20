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

from functions import sort_human

import locale
locale.setlocale(locale.LC_ALL, "lv_LV.UTF-8")

class JournalEVPupil(ttk.Frame):
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
        self.excel_file_name = self.essa_config['Journal.Excel']['ExcelEVFileName']
        self.excel_file_name_ext = self.essa_config['Journal.Excel']['ExcelFileNameExt']

        # TOP FRAME
        self.main_frame = ttk.Frame(self)
        self.controller.top_menu_buttons(self.main_frame)

        # LEFT FRAME
        self.left_frame_ev = ttk.Frame(self)
        self.left_frame_ev.pack(fill='none', padx=10, pady=(0,10), expand=True)

        label = ttk.Label(self.left_frame_ev, text='SKOLAS ŽURNĀLA ANALĪZE', justify='center', font=(controller.default_font_name, 11, 'bold'))
        label.pack(pady=(0,0), expand=True)

        label = ttk.Label(self.left_frame_ev, text='Informācija par vērtēšanu (citā krāsā - skolēniem ir “nv” no “PD”)', justify='center', font=(controller.default_font_name, 9, 'italic'))
        label.pack(pady=(0,10), expand=False)

        style = ttk.Style()
        style.configure("mystyle.Treeview", highlightthickness=0, bd=0, font=(controller.default_font_name, 9, 'normal')) # Modify the font of the body
        style.configure("mystyle.Treeview.Heading", font=(controller.default_font_name, 9, 'bold')) # Modify the font of the headings
        # style.layout("mystyle.Treeview", [('mystyle.Treeview.treearea', {'sticky': 'nswe'})])

        tree_scroll_x = ttk.Scrollbar(self.left_frame_ev, orient=tk.HORIZONTAL)
        tree_scroll_y = ttk.Scrollbar(self.left_frame_ev, orient=tk.VERTICAL)

        # EV
        self.tree_column_name = ('pupil', 'class', 'e_n', 'e_nv', 'e_nv_pd', 'e_i', 'e_ni', 'e_1_10_avg', 'e_perc_avg', 'e_1', 'e_2', 'e_3', 'e_4', 'e_5', 'e_6', 'e_7', 'e_8', 'e_9', 'e_10', 'e_s', 'e_t', 'e_a', 'e_p', 'v_d', 'v_a')
        self.tree_column_about = ('Skolēns', 'Klase', 'n', 'nv', 'nv(PD)', 'i', 'ni', '1-10', '%', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'S', 'T', 'A', 'P', 'V(D)', 'V(A)')
        self.tree_column_weight = (200, 50, 40, 40, 55, 40, 30, 45, 45, 40, 30, 30, 30, 30, 30, 30, 30, 30, 30, 40, 30, 30, 30, 40, 40)
        
        self.tree = ttk.Treeview(self.left_frame_ev, columns=self.tree_column_name, show='headings', height=17, cursor="hand2", style="mystyle.Treeview", xscrollcommand=tree_scroll_x.set, yscrollcommand=tree_scroll_y.set)

        self.tree.heading(self.tree_column_name[0], text=self.tree_column_about[0], anchor='w', command=lambda: self.treeview_sort_column(self.tree, 'pupil', False))
        self.tree.column(self.tree_column_name[0], minwidth=50, width=200, anchor='w', stretch=False)

        self.tree.heading(self.tree_column_name[1], text=self.tree_column_about[1], anchor='e', command=lambda: self.treeview_sort_column(self.tree, 'class', False))
        self.tree.column(self.tree_column_name[1], minwidth=50, width=50, anchor='e', stretch=False)

        self.tree.heading(self.tree_column_name[2], text=self.tree_column_about[2], anchor='e', command=lambda: self.treeview_sort_column(self.tree, 'e_n', False))
        self.tree.column(self.tree_column_name[2], minwidth=40, width=40, anchor='e', stretch=False)

        self.tree.heading(self.tree_column_name[3], text=self.tree_column_about[3], anchor='e', command=lambda: self.treeview_sort_column(self.tree, 'e_nv', False))
        self.tree.column(self.tree_column_name[3], minwidth=40, width=40, anchor='e', stretch=False)       

        self.tree.heading(self.tree_column_name[4], text=self.tree_column_about[4], anchor='e', command=lambda: self.treeview_sort_column(self.tree, 'e_nv_pd', False))
        self.tree.column(self.tree_column_name[4], minwidth=55, width=55, anchor='e', stretch=False)       

        self.tree.heading(self.tree_column_name[5], text=self.tree_column_about[5], anchor='e', command=lambda: self.treeview_sort_column(self.tree, 'e_i', False))
        self.tree.column(self.tree_column_name[5], minwidth=40, width=40, anchor='e', stretch=False)

        self.tree.heading(self.tree_column_name[6], text=self.tree_column_about[6], anchor='e', command=lambda: self.treeview_sort_column(self.tree, 'e_ni', False))
        self.tree.column(self.tree_column_name[6], minwidth=30, width=30, anchor='e', stretch=False)

        self.tree.heading(self.tree_column_name[7], text=self.tree_column_about[7], anchor='e', command=lambda: self.treeview_sort_column(self.tree, 'e_1_10_avg', False))
        self.tree.column(self.tree_column_name[7], minwidth=40, width=45, anchor='e', stretch=False)

        self.tree.heading(self.tree_column_name[8], text=self.tree_column_about[8], anchor='e', command=lambda: self.treeview_sort_column(self.tree, 'e_perc_avg', False))
        self.tree.column(self.tree_column_name[8], minwidth=40, width=45, anchor='e', stretch=False)

        self.tree.heading(self.tree_column_name[9], text=self.tree_column_about[9], anchor='e', command=lambda: self.treeview_sort_column(self.tree, 'e_1', False))
        self.tree.column(self.tree_column_name[9], minwidth=40, width=40, anchor='e', stretch=False)

        self.tree.heading(self.tree_column_name[10], text=self.tree_column_about[10], anchor='e', command=lambda: self.treeview_sort_column(self.tree, 'e_2', False))
        self.tree.column(self.tree_column_name[10], minwidth=30, width=30, anchor='e', stretch=False)       

        self.tree.heading(self.tree_column_name[11], text=self.tree_column_about[11], anchor='e', command=lambda: self.treeview_sort_column(self.tree, 'e_3', False))
        self.tree.column(self.tree_column_name[11], minwidth=30, width=30, anchor='e', stretch=False)       

        self.tree.heading(self.tree_column_name[12], text=self.tree_column_about[12], anchor='e', command=lambda: self.treeview_sort_column(self.tree, 'e_4', False))
        self.tree.column(self.tree_column_name[12], minwidth=30, width=30, anchor='e', stretch=False)       

        self.tree.heading(self.tree_column_name[13], text=self.tree_column_about[13], anchor='e', command=lambda: self.treeview_sort_column(self.tree, 'e_5', False))
        self.tree.column(self.tree_column_name[13], minwidth=30, width=30, anchor='e', stretch=False)       

        self.tree.heading(self.tree_column_name[14], text=self.tree_column_about[14], anchor='e', command=lambda: self.treeview_sort_column(self.tree, 'e_6', False))
        self.tree.column(self.tree_column_name[14], minwidth=30, width=30, anchor='e', stretch=False)       

        self.tree.heading(self.tree_column_name[15], text=self.tree_column_about[15], anchor='e', command=lambda: self.treeview_sort_column(self.tree, 'e_7', False))
        self.tree.column(self.tree_column_name[15], minwidth=30, width=30, anchor='e', stretch=False)       

        self.tree.heading(self.tree_column_name[16], text=self.tree_column_about[16], anchor='e', command=lambda: self.treeview_sort_column(self.tree, 'e_8', False))
        self.tree.column(self.tree_column_name[16], minwidth=30, width=30, anchor='e', stretch=False)       

        self.tree.heading(self.tree_column_name[17], text=self.tree_column_about[17], anchor='e', command=lambda: self.treeview_sort_column(self.tree, 'e_9', False))
        self.tree.column(self.tree_column_name[17], minwidth=30, width=30, anchor='e', stretch=False)       

        self.tree.heading(self.tree_column_name[18], text=self.tree_column_about[18], anchor='e', command=lambda: self.treeview_sort_column(self.tree, 'e_10', False))
        self.tree.column(self.tree_column_name[18], minwidth=30, width=30, anchor='e', stretch=False)       

        self.tree.heading(self.tree_column_name[19], text=self.tree_column_about[19], anchor='e', command=lambda: self.treeview_sort_column(self.tree, 'e_s', False))
        self.tree.column(self.tree_column_name[19], minwidth=40, width=40, anchor='e', stretch=False)       

        self.tree.heading(self.tree_column_name[20], text=self.tree_column_about[20], anchor='e', command=lambda: self.treeview_sort_column(self.tree, 'e_t', False))
        self.tree.column(self.tree_column_name[20], minwidth=30, width=30, anchor='e', stretch=False)       

        self.tree.heading(self.tree_column_name[21], text=self.tree_column_about[21], anchor='e', command=lambda: self.treeview_sort_column(self.tree, 'e_a', False))
        self.tree.column(self.tree_column_name[21], minwidth=30, width=30, anchor='e', stretch=False)       

        self.tree.heading(self.tree_column_name[22], text=self.tree_column_about[22], anchor='e', command=lambda: self.treeview_sort_column(self.tree, 'e_p', False))
        self.tree.column(self.tree_column_name[22], minwidth=30, width=30, anchor='e', stretch=False)       

        self.tree.heading(self.tree_column_name[23], text=self.tree_column_about[23], anchor='e', command=lambda: self.treeview_sort_column(self.tree, 'v_d', False))
        self.tree.column(self.tree_column_name[23], minwidth=40, width=40, anchor='e', stretch=False)       

        self.tree.heading(self.tree_column_name[24], text=self.tree_column_about[24], anchor='e', command=lambda: self.treeview_sort_column(self.tree, 'v_a', False))
        self.tree.column(self.tree_column_name[24], minwidth=40, width=40, anchor='e', stretch=False)       

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

        password_label = ttk.Label(self.bottom_frame_title, text='Skolēns', width=29, font=(controller.default_font_name, 9, 'bold'))
        password_label.pack(side='left', padx=(0,10))

        password_label = ttk.Label(self.bottom_frame_title, text='Klase', width=25, font=(controller.default_font_name, 9, 'bold'))
        password_label.pack(side='left', padx=(0,10))

        # BOTTOM FRAME
        self.bottom_frame = ttk.Frame(self)
        self.bottom_frame.pack(fill='none', padx=(10,10), pady=(0,100))

        self.pupil_selected = ttk.StringVar()
        self.pupil_combo = ttk.Combobox(self.bottom_frame, width=30, textvariable=self.pupil_selected)      
        self.pupil_combo.bind('<<ComboboxSelected>>', self.pupil_combo_selected)
        self.pupil_combo.pack(side='left', padx=(0,10))        

        self.classes_selected = ttk.StringVar()
        self.classes_combo = ttk.Combobox(self.bottom_frame, width=10, textvariable=self.classes_selected)
        self.classes_combo.bind('<<ComboboxSelected>>', self.classes_combo_selected)
        self.classes_combo.pack(side='left', padx=(0,10))

        self.excel_button = ttk.Button(self.bottom_frame, text='↓ Excel', cursor='hand2', command=lambda: self.save_to_excel(True)) 
        self.excel_button.pack(side='left', padx=(20,0))

    def fix_tree_column(self):
        pass

    def before(self):
        pupils, classes = self.sql_select_params()

        prefix = '––– VISS –––'

        if len(pupils) > 0: 
            if pupils[0] != prefix:
                pupils.insert(0, prefix)
            self.pupil_combo['values'] = pupils
            try:
                self.pupil_combo.set(self.sql_query_params['pupil'])
            except:
                self.pupil_combo.current(0)

        if len(classes) > 0:
            if classes[0] != prefix:
                classes.insert(0, prefix)
            self.classes_combo['values'] = classes
            try:
                self.classes_combo.set(self.sql_query_params['class'])
            except:
                self.classes_combo.current(0)

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

                sql_query = """SELECT pupil_id, pupil_first_name, pupil_last_name, class_name, evaluations_n, evaluations_nv, evaluations_nv_pd, evaluations_i, evaluations_ni, evaluations_1_10_avg, evaluations_perc_avg, evaluations_1, evaluations_2, evaluations_3, evaluations_4, evaluations_5, evaluations_6, evaluations_7, evaluations_8, evaluations_9, evaluations_10, evaluations_s, evaluations_t, evaluations_a, evaluations_p, evaluations_vam_d, evaluations_vam_a FROM "main"."v_evaluations_2" """
                
                sql_where = []
                try:
                    if self.sql_query_params['pupil'] != '':
                        sql_where.append('concat(pupil_last_name, " ", pupil_first_name) = "' + self.sql_query_params['pupil'] + '"')
                except:
                    pass
                try:
                    if self.sql_query_params['class'] != '':
                        sql_where.append('class_name = "' + self.sql_query_params['class'] + '"')
                except:
                    pass

                if len(sql_where) > 0:
                    sql_query +='WHERE ' + ' AND '.join(sql_where)

                sql_query += """ ORDER BY pupil_last_name ASC, pupil_first_name ASC LIMIT 49999 OFFSET 0;"""

                # print(sql_query)

                cur.execute(sql_query)
                
                self.sql_query_result = cur.fetchall()
                # self.sql_query_result.sort(key=lambda x: x[0])

                # print("Total rows are:", len(self.sql_query_result))
                # print(records[0])

                cur.close()

                # reset treeview
                for row in self.tree.get_children():
                    self.tree.delete(row)

                '''
                 0 - pupil_id
                 1 - pupil_first_name
                 2 - pupil_last_name
                 3 - class_name
                 4 - evaluations_n
                 5 - evaluations_nv
                 6 - evaluations_nv_pd
                 7 - evaluations_i
                 8 - evaluations_ni
                 9 - evaluations_1_10_avg
                10 - evaluations_perc_avg
                11 - evaluations_1
                12 - evaluations_2
                13 - evaluations_3
                14 - evaluations_4
                15 - evaluations_5
                16 - evaluations_6
                17 - evaluations_7
                18 - evaluations_8
                19 - evaluations_9
                20 - evaluations_10
                21 - evaluations_s
                22 - evaluations_t
                23 - evaluations_a
                24 - evaluations_p
                25 - evaluations_vam_d
                26 - evaluations_vam_a
                '''

                for idx, record in enumerate(self.sql_query_result):
                    # prepare data to row
                    pupil = record[2]+' '+record[1]
                    class_ = record[3]

                    e_n = str(record[4])
                    e_nv = str(record[5])
                    e_nv_pd = str(record[6])
                    e_i = str(record[7])
                    e_ni = str(record[8])
                    e_1_10_avg = str('%0.1f' % round(float(record[9]),1)) if record[9] != '' else '-'
                    e_perc_avg = str('%0.1f' % round(float(record[10]),1)) if record[10] != '' else '-'
                    e_1 = str(record[11])
                    e_2 = str(record[12])
                    e_3 = str(record[13])
                    e_4 = str(record[14])
                    e_5 = str(record[15])
                    e_6 = str(record[16])
                    e_7 = str(record[17])
                    e_8 = str(record[18])
                    e_9 = str(record[19])
                    e_10 = str(record[20])
                    e_s = str(record[21])
                    e_t = str(record[22])
                    e_a = str(record[23])
                    e_p = str(record[24])
                    e_vam_d = str(record[25])
                    e_vam_a = str(record[26])
                    
                    # check PD
                    tag = ''
                    if int(record[6]) > 0:
                        tag = 'mark'

                    # 'pupil', 'class', 'e_n', 'e_nv', 'e_nv_pd', 'e_i', 'e_ni', 'e_1_10_avg', 'e_perc_avg', 'e_1', 'e_2', 'e_3', 'e_4', 'e_5', 'e_6', 'e_7', 'e_8', 'e_9', 'e_10', 'e_s', 'e_t', 'e_a', 'e_p', 'v_d', 'v_a'
                    values = (pupil, class_, e_n, e_nv, e_nv_pd, e_i, e_ni, e_1_10_avg, e_perc_avg, e_1, e_2, e_3, e_4, e_5, e_6, e_7, e_8, e_9, e_10, e_s, e_t, e_a, e_p, e_vam_d, e_vam_a)

                    self.tree.insert('', tk.END, iid=idx, values=values, tags=(tag))

                    # print(idx)

            conn.close()

        except sqlite3.Error as error:
            print("Failed to read data from sqlite table", error)

        finally:
            self.unlock_frame()
            return self.sql_query_result

    def sql_select_params(self):

        pupils = []
        classes = []

        # check cache
        if self.controller.pupil_sql_query_params_cache != []:
            return self.controller.pupil_sql_query_params_cache

        db_file_name = self.platform.db_dir + self.platform.db_journal_file_name

        if not os.path.exists(db_file_name):
            return pupils, classes

        try:
            with sqlite3.connect(db_file_name) as conn:                
                cur = conn.cursor()

                if self.platform.db_encrypt:
                    if not self.platform.set_db_pragma(conn):
                        return False

                sql_query = """SELECT DISTINCT pupil_first_name, pupil_last_name, class_name FROM "main"."v_evaluations_2" LIMIT 49999 OFFSET 0;"""
                cur.execute(sql_query)
                records = cur.fetchall()
                # print("Total rows are:", len(records))
                # print(records[0])

                cur.close()

                for record in records:
                    pupils.append(record[1]+' '+record[0])
                    classes.append(record[2])

                pupils.sort()
                pupils = list(dict.fromkeys(pupils))
                # print(pupils)

                classes = sort_human(classes)
                classes = list(dict.fromkeys(classes))
                # print(classes)

            conn.close()

        except sqlite3.Error as error:
            print("Failed to read data from sqlite table", error)

        finally:
            self.controller.pupils_sql_query_params_cache = (pupils, classes)
            return self.controller.pupils_sql_query_params_cache

    def pupil_combo_selected(self, event):        
        # print(self.pupil_selected.get())
        self.sql_query_params['pupil'] = self.pupil_selected.get() if self.pupil_selected.get() != '––– VISS –––' else ''
        self.update_list()

    def classes_combo_selected(self, event):
        # print(self.classes_selected.get())
        self.sql_query_params['class'] = self.classes_selected.get() if self.classes_selected.get() != '––– VISS –––' else ''
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
                'Informācija',record[2]+' '+record[1]+', '+record[3],
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
            worksheet.write('A1', 'Skolēns', bold)
            worksheet.write('B1', 'Klase', bold)

            #'pupil', 'class', 'e_n', 'e_nv', 'e_nv_pd', 'e_i', 'e_ni', 'e_1_10_avg', 'e_perc_avg', 'e_1', 'e_2', 'e_3', 'e_4', 'e_5', 'e_6', 'e_7', 'e_8', 'e_9', 'e_10', 'e_s', 'e_t', 'e_a', 'e_p', 'v_d', 'v_a'

            # EV
            # 'PD(%)', 'V(max)', 'V(b)', 'V(%)', 'V(stap)', 'V(i)', 'V(ni)', 'V(nv)', 'V(n)'
            worksheet.write('C1', 'V(n)', bold)
            worksheet.write('D1', 'V(nv)', bold)
            worksheet.write('E1', 'V(nv[PD])', bold)
            worksheet.write('F1', 'V(i)', bold)
            worksheet.write('G1', 'V(ni)', bold)
            worksheet.write('H1', 'V(1-10)', bold)
            worksheet.write('I1', 'V(%)', bold)
            worksheet.write('J1', 'V(1)', bold)
            worksheet.write('K1', 'V(2)', bold)
            worksheet.write('L1', 'V(3)', bold)
            worksheet.write('M1', 'V(4)', bold)
            worksheet.write('N1', 'V(5)', bold)
            worksheet.write('O1', 'V(6)', bold)
            worksheet.write('P1', 'V(7)', bold)
            worksheet.write('Q1', 'V(8)', bold)
            worksheet.write('R1', 'V(9)', bold)
            worksheet.write('S1', 'V(10)', bold)
            worksheet.write('T1', 'V(S)', bold)
            worksheet.write('U1', 'V(T)', bold)
            worksheet.write('V1', 'V(A)', bold)
            worksheet.write('W1', 'V(P)', bold)
            worksheet.write('X1', 'V(VAM[D])', bold)
            worksheet.write('Y1', 'V(VAM[A])', bold)

            row = 1
            col = 0

            for record in self.sql_query_result:
                worksheet.write(row, col,   record[2]+' '+record[1])
                worksheet.write(row, col+1, record[3])

                # EV
                worksheet.write(row, col+2, int(record[4]))
                worksheet.write(row, col+3, int(record[5]))
                worksheet.write(row, col+4, int(record[6]))
                worksheet.write(row, col+5, int(record[7]))
                worksheet.write(row, col+6, int(record[8]))
                worksheet.write(row, col+7, float(record[9]) if record[9] != '' else '')
                worksheet.write(row, col+8, float(record[10]) if record[10] != '' else '')
                worksheet.write(row, col+9, int(record[11]))
                worksheet.write(row, col+10, int(record[12]))
                worksheet.write(row, col+11, int(record[13]))
                worksheet.write(row, col+12, int(record[14]))
                worksheet.write(row, col+13, int(record[15]))
                worksheet.write(row, col+14, int(record[16]))
                worksheet.write(row, col+15, int(record[17]))
                worksheet.write(row, col+16, int(record[18]))
                worksheet.write(row, col+17, int(record[19]))
                worksheet.write(row, col+18, int(record[20]))
                worksheet.write(row, col+19, int(record[21]))
                worksheet.write(row, col+20, int(record[22]))
                worksheet.write(row, col+21, int(record[23]))
                worksheet.write(row, col+22, int(record[24]))
                worksheet.write(row, col+23, int(record[25]))
                worksheet.write(row, col+24, int(record[26]))
                                
                row += 1

            workbook.close()

            if open_file:
                self.controller.open_dir(self.excel_dir + '/' + self.excel_file_name + '.' + self.excel_file_name_ext)
        except:
            pass