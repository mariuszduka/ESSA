'''
ESSA :: Electronic Grade Book Assistant
Copyright (C) 2025 Mariusz Duka
This file is part of ESSA and is licensed under the GNU GPLv3 or later.
See the LICENSE file for full text.
'''

from datetime import datetime
from threading import Thread
import ttkbootstrap as ttk

from functions import sort_human

class EKlaseGetData(ttk.Frame):
    def __init__(self, parent, controller, platform):
        ttk.Frame.__init__(self, parent, width=controller.view_width, height=controller.view_height)

        self.lock = False

        self.platform = platform
        self.controller = controller
        self.in_progress = False
        self.progress_var = ttk.DoubleVar()

        self.essa_config = self.controller.essa_config
        self.create_dump_db_files = False

        self.classes_checked = {}
        self.classes_available = {}
        self.classes_selected = {}

        self.next_monday = self.platform.get_next_monday()
        next_monday_obj = datetime.strptime(self.next_monday, '%Y-%m-%d')
        self.show_transfer_message_box = False

        # TOP FRAME
        self.main_frame = ttk.Frame(self)
        self.controller.top_menu_buttons(self.main_frame)

        # LEFT FRAME
        left_frame = ttk.Frame(self)
        left_frame.pack(side='left', fill='none', padx=10, pady=(0,80), expand=True)

        label = ttk.Label(left_frame, text='DATU LEJUPIELĀDĒŠANA', justify='center', font=(controller.default_font_name, 11, 'bold'))
        label.pack(pady=(0,20), expand=True)

        # date
        date_label = ttk.Label(left_frame, text='Stundu saraksts no:')
        date_label.pack(fill='x', anchor='w', expand=True)

        date_entry = ttk.DateEntry(left_frame, bootstyle='primary', firstweekday=0, dateformat='%Y-%m-%d', startdate=next_monday_obj)
        date_entry.pack(fill='x', anchor='w', expand=True, pady=(0,10))

        # select data to download
        self.timetable_status = ttk.BooleanVar()
        self.timetable_status.set(False)
        self.timetable_checkbox = ttk.Checkbutton(left_frame, text ='Stundu saraksts', variable=self.timetable_status, offvalue=False, onvalue=True)
        self.timetable_checkbox.pack(fill='x', anchor='w', expand=True, pady=(0,5))

        self.journal_status = ttk.BooleanVar()
        self.journal_status.set(False)
        self.journal_checkbox = ttk.Checkbutton(left_frame, text ='Žurnāls (šis semestris)', variable=self.journal_status, offvalue=False, onvalue=True, command=lambda: self.transfer_message_box(self.journal_checkbox.state()))
        self.journal_checkbox.pack(fill='x', anchor='w', expand=True, pady=(5,25))

        self.db_update = ttk.BooleanVar()
        self.db_update.set(True)
        self.db_update_checkbox = ttk.Checkbutton(left_frame, text ='Pievieno esošajiem datiem', variable=self.db_update, offvalue=False, onvalue=True)
        self.db_update_checkbox.pack(fill='x', anchor='w', expand=True, pady=(5,5))

        self.db_archive = ttk.BooleanVar()
        self.db_archive.set(False)
        self.db_archive_checkbox = ttk.Checkbutton(left_frame, text ='Izveido datubāzes arhīvu', variable=self.db_archive, offvalue=False, onvalue=True)
        self.db_archive_checkbox.pack(fill='x', anchor='w', expand=True, pady=(5,30))

        # download classes
        self.download_button = ttk.Button(left_frame, text='Lejupielāde', bootstyle='primary', command=lambda: self.get_data(date_entry.entry.get(), self.timetable_checkbox.state(), self.journal_checkbox.state(), self.db_update_checkbox.state(), self.db_archive_checkbox.state()))
        self.download_button.pack(fill='x', anchor='w', expand=True, pady=(10,20))
        self.download_button.config(state='normal')

        # progressbar
        self.pb = ttk.Progressbar(left_frame, orient='horizontal', mode='determinate', variable=self.progress_var)
        self.pb.pack(fill='x', anchor='w', expand=True, pady=(0,0))
        self.pb.configure(maximum=100)
        # self.pb.pack_forget()

        # RIGHT FRAME
        right_frame = ttk.Frame(self)
        right_frame.pack(side='right', fill='none', padx=(40,160), pady=(0,80), expand=False)

        self.scrolltext_label = ttk.Label(right_frame, text='KLASES', anchor='w', font=(controller.default_font_name, 11, 'bold'))
        self.scrolltext_label.pack(pady=(0,0), fill='x', expand=True)

        label = ttk.Label(right_frame, text='Izvēlies klases (redzēsi pēc autorizācijas)', anchor='w', font=(controller.default_font_name, 9, 'italic'))
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

    def before(self):
        if not self.platform.is_authenticated:
            self.controller.show_frame_name('EKlaseAuth')  

        self.classes_available = sort_human(self.platform.get_classes_available())
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

        # print(checked)

    def after(self):
        self.classes_selected = []

    def is_locked(self):
        return self.lock

    def lock_frame(self):
        self.lock = True
        self.in_progress = True
        self.download_button.config(state='disabled')
        self.controller.update_menu_states(ttk.DISABLED)

    def unlock_frame(self):
        self.lock = False
        self.in_progress = False
        self.download_button.config(state='normal')
        self.controller.update_menu_states(ttk.NORMAL)

    def set_netx_monday(self, date):
        self.next_monday = date

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
                
        # print(checked)
        
        self.classes_selected = checked
        self.before()

    def get_data(self, date, timetable=(), journal=(), db_update=(), db_archive=()):
        if not self.platform.is_authenticated:
            self.controller.show_frame_name('EKlaseAuth')            
            return False

        timetable = True if 'selected' in timetable else False
        journal = True if 'selected' in journal else False
        db_update = True if 'selected' in db_update else False
        db_archive = True if 'selected' in db_archive else False

        if not timetable and not journal:
            self.controller.message_box(
                title='Informācija', 
                message='Izvēlies datus (stundu saraksts vai/un žurnāls), kurus gribi lejupielādēt.')
            return False

        if len(self.classes_selected) == 0:
            self.controller.message_box(
                title='Informācija', 
                message='Lai lejupielādētu datus, izvēlies klases.')
            return False

        self.platform.set_date(date)
        self.lock_frame()

        Thread(target=lambda:self.download(timetable, journal, db_update, db_archive)).start()
        return True

    def download(self, timetable=False, journal=False, db_update=True, db_archive=False):
        
        '''
        self.controller.bottom_bar('Datu lejupielādēšana: Stundu saraksts. Lūdzu, pagaidi brīdi...')
        for i in [10, 30, 60, 80, 100]:
            print(i)
            self.progress_var.set(i)
            sleep(1)

        self.controller.bottom_bar('Datu lejupielādēšana: Žurnāls (šo semestri). Lūdzu, pagaidi brīdi...')
        for i in [10, 30, 60, 80, 100]:
            print(i)
            self.progress_var.set(i)
            sleep(1)

        self.controller.bottom_bar()
        '''

        if not self.platform.is_authenticated:
            self.controller.show_frame_name('EKlaseAuth')            
            return False

        if len(self.classes_selected) == 0:
            self.unlock_frame()
            return False

        if timetable:
            self.progress_var.set(0)
            self.controller.bottom_bar('Datu lejupielādēšana: Stundu saraksts. Lūdzu, pagaidi brīdi...')
            try:
                if self.platform.req_classes_data(self.classes_selected, progress_bar=self.progress_var, json_save=False, show_info=False):
                    self.platform.sqlite_classes_data(self.classes_selected, db_update=db_update, db_file_archive=db_archive, show_info=False)
            except:
                pass

        if journal:
            self.progress_var.set(0)
            self.controller.bottom_bar('Datu lejupielādēšana: Žurnāls (šo semestri). Lūdzu, pagaidi brīdi...')
            try:
                if self.platform.req_journals_data(self.classes_selected, progress_bar=self.progress_var, json_save=False, show_info=False):
                    self.platform.sqlite_journal_data(self.classes_selected, db_update=db_update, db_file_archive=db_archive, load_classes_from_json=False, show_info=False)
                    
                # self.platform.sqlite_journal_data(self.classes_selected, db_update=db_update, db_file_archive=db_archive, load_classes_from_json=True, show_info=True)
            except:
                pass

        self.progress_var.set(0)
        self.controller.bottom_bar()
        self.unlock_frame()

        # reset cache
        self.controller.journal_sql_query_params_cache = []
        self.controller.pupil_sql_query_params_cache = []

        # self.controller.show_frame_name('Schedule')
        self.controller.show_frame_name('StartPage')

    def transfer_message_box(self, journal=()):        
        journal = True if 'selected' in journal else False
        if journal and not self.show_transfer_message_box:
            self.controller.message_box(
                title='Informācija', 
                message='Žurnāla datu lejupielāde var aizņemt līdz pat vairākām minūtēm! Tāpēc labāk izvēlies tikai vajadzīgās klases.')
            self.show_transfer_message_box = True
            return False