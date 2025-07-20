'''
ESSA :: Electronic Grade Book Assistant
Copyright (C) 2025 Mariusz Duka
This file is part of ESSA and is licensed under the GNU GPLv3 or later.
See the LICENSE file for full text.
'''

import os
import ttkbootstrap as ttk
from functions import get_names_by_date, get_semester_and_holiday_info
from essa import GITHUB, HOMEPAGE
from essa.version import SQL_SCHEMA_VERSION_JOURNAL, SQL_SCHEMA_VERSION_TIMETABLE

# encrypt SQLite3
try:
    from sqlcipher3 import dbapi2 as sqlite3
except ModuleNotFoundError as err:
    import sqlite3

class StartPage(ttk.Frame):
    def __init__(self, parent, controller, platform): 
        ttk.Frame.__init__(self, parent, width=controller.view_width, height=controller.view_height)

        self.lock = False

        self.platform = platform
        self.controller = controller

        self.app_passwd = self.controller.app_passwd
        self.app_expire = self.controller.app_expire

        background = ttk.Label(self, image=controller.background_image)
        background.place(x=735, y=510, anchor='w')

        # TOP FRAME
        self.main_frame = ttk.Frame(self)
        self.controller.top_menu_buttons(self.main_frame)

        # LOGIN FRAME
        self.login_frame = ttk.Frame(self)
        self.login_frame.pack(fill='none', padx=0, pady=(0,0), expand=True)

        password_label = ttk.Label(self.login_frame, text="Parole:", font=(controller.default_font_name, 12, 'bold'))
        password_label.pack(fill='x', expand=True)

        bullet = "\u2022"
        self.password_entry_text = ttk.StringVar()
        password_entry = ttk.Entry(self.login_frame, textvariable=self.password_entry_text, font=(controller.default_font_name, 12, 'normal'), show=bullet)
        password_entry.pack(fill='x', expand=True)
        password_entry.bind('<Return>', self.check_pwd)

        download_button = ttk.Button(self.login_frame, text='Ielogojies', bootstyle='primary', command=self.check_pwd)
        download_button.pack(fill='x', anchor='w', expand=True, pady=(10,40))
        download_button.config(state='normal')
        
        # BOTTOM FRAME
        self.bottom_frame = ttk.Frame(self)
        self.bottom_frame.pack(fill='none', side='bottom', anchor='w', padx=(20,10), pady=(0,95))

        self.date_label = ttk.Label(self.bottom_frame, text='', font=(controller.default_font_name, 9, 'normal'))
        self.date_label.pack(side='left', expand=True, padx=(40,0))

        # START FRAME
        self.start_frame = ttk.Frame(self)
        self.start_frame.pack(side='left')

        # print(get_semester_and_holiday_info())
        
        events = get_semester_and_holiday_info()        
        names = get_names_by_date()
        if names:
            names_text = ', '.join(names)
            events += f"\nŠodien vārda dienu svin:\n{names_text}."
                        
        if events:
            lines = len(events.splitlines()) + 1
            events_text = ttk.Text(self.start_frame, font=self.controller.default_font, wrap='word', height=lines, width=50, highlightthickness=0, borderwidth=0)
            events_text.insert('1.0', events)
            events_text.tag_configure('bold1', font=(self.controller.default_font_name, self.controller.default_font_size-1, 'bold'))
            events_text.tag_configure('bold2', font=(self.controller.default_font_name, self.controller.default_font_size, 'bold'))

            # Apply bold only if the line starts and ends with '*'
            for line_number, line in enumerate(events.splitlines(), start=1):
                if line.startswith(('*', '#')) and line.endswith(('*', '#')): 
                    markers = ('*', '#') if line.startswith('*') else ('#', '*')
                    clean_line = line.strip(''.join(markers))  # Remove markers from the start and end
                    events_text.delete(f'{line_number}.0', f'{line_number}.end')  # Clear the line
                    events_text.insert(f'{line_number}.0', clean_line)  # Insert the cleaned line
                    tag = 'bold1' if markers[0] == '*' else 'bold2'
                    events_text.tag_add(tag, f'{line_number}.0', f'{line_number}.end')  # Apply bold

            events_text.config(state='disabled', cursor='arrow', background='#f2f2f2', highlightthickness=0, borderwidth=0, takefocus=0)  # Make the Text widget read-only, disable text selection, set background, and remove border
            events_text.bind("<1>", lambda e: "break")  # Disable text selection by blocking mouse clicks
            events_text.pack(anchor='w', padx=(60, 0), pady=(0, 0))

        logo = ttk.Label(self, image=controller.logo_image)
        logo.pack(side='right', anchor='n', padx=(0,60), pady=(80,0))

    def before(self):
        self.start_frame.pack_forget()
        self.login_frame.pack_forget()
        self.password_entry_text.set('')
        
        if self.controller.show_login_frame:
            # self.lock_frame()
            self.login_frame.pack(fill='none', padx=0, pady=(0,0), expand=True)
        else:
            self.start_frame.pack(side='left')

        self.date_label.config(text=self.controller.db_last_update())
    
        self.controller.after(500, lambda: self.check_sql_schema_version_and_notify())

    def after(self):
        # print('startpage after')
        pass

    def is_locked(self):
        return self.lock

    def lock_frame(self):
        self.lock = True
        self.controller.update_menu_states(ttk.DISABLED)

    def unlock_frame(self):
        self.lock = False
        self.controller.update_menu_states(ttk.NORMAL)

    def check_pwd(self, event=None):
        pwd = str(self.password_entry_text.get())

        if pwd != self.app_passwd:
            self.controller.message_box('Informācija','Nepareiza parole.')
            return False

        self.controller.user_auth = True
        self.login_frame.pack_forget()
        self.unlock_frame()
        self.start_frame.pack(side='left')
        
        if self.controller.frame_before != None:
            if isinstance(self.controller.frame_before, str):
                self.controller.show_frame_name(self.controller.frame_before)
            else:
                self.controller.show_frame(self.controller.frame_before)            

    def treeview_sort_column(self, tv, col, reverse):
        l = [(tv.set(k, col), k) for k in tv.get_children('')]
        try:
            l.sort(key=lambda t: float(t[0]) if t[0] != '-' else 0, reverse=reverse)
        except ValueError:
            l.sort(reverse=reverse)

        for index, (val, k) in enumerate(l):
            tv.move(k, '', index)

        tv.heading(col, command=lambda: self.treeview_sort_column(tv, col, not reverse))

    def check_sql_schema_version_and_notify(self):
        if self.platform.db_encrypt and self.platform.db_decrypted == False:
            self.controller.message_box('Uzmanību!','Ir problēma ar datubāzes failiem. Iespējams, ka dati ir bojāti.\nVari izdzēst visus programmas datus (Uzstādījumi) un palaist programmu vēlreiz.')

        if not self.check_sql_schema_version():
            self.controller.message_box('Uzmanību!','Pašreizējā programmas versijā ir nepieciešams cits datubāzes formāts.\n\nKas tev jādara?\n1. Izdzēst visus programmas datus (Uzstādījumi)\n2. Palaist programmu vēlreiz.\n3. Lejupielādē datus no elektroniskās skolvadības sistēmas.', window_height=220)
        
    def check_sql_schema_version(self):       
        db_file_names = [self.platform.db_dir + self.platform.db_journal_file_name, self.platform.db_dir + self.platform.db_timetable_file_name]
        db_schema_versions = [SQL_SCHEMA_VERSION_JOURNAL, SQL_SCHEMA_VERSION_TIMETABLE]
        db_checks = [True, True]
        
        for index, db_file_name in enumerate(db_file_names):
            # print(index, db_file_name)
            if os.path.exists(db_file_name):            
                try:
                    with sqlite3.connect(db_file_name) as conn: 
                        cur = conn.cursor()

                        if self.platform.db_encrypt:
                            if not self.platform.set_db_pragma(conn):
                                return False

                        # Check if the table "main"."essa" exists
                        sql_check_table = """SELECT name FROM sqlite_master WHERE type='table' AND name='essa';"""
                        cur.execute(sql_check_table)
                        table_exists = cur.fetchone()
                        if not table_exists:
                            cur.close()
                            print(f"Table 'essa' does not exist in {db_file_name}.")
                            return False

                        sql_query = """SELECT value FROM "main"."essa" WHERE param = 'sql_schema_version';"""
                        
                        cur.execute(sql_query)
                        
                        result = cur.fetchone()
                        if result is None:
                            result = 0
                        else:
                            result = result[0]
                            
                        cur.close()                    

                    conn.close()
                    
                    if int(result) != int(db_schema_versions[index]):
                        db_checks[index] = False
                        
                except sqlite3.Error as error:
                    print("Failed to read data from sqlite table", error)
                
        # print(db_checks)
        
        # return True if both databases have the correct schema version, otherwise False        
        return db_checks[0] and db_checks[1]        