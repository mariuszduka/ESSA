'''        
ESSA :: Electronic Grade Book Assistant
Copyright (C) 2025 Mariusz Duka
This file is part of ESSA and is licensed under the GNU GPLv3 or later.
See the LICENSE file for full text.
'''

import os
import sys
import pathlib
import webbrowser
import shutil
import base64
from datetime import datetime, date

sys.path.append('./connect/src/')
sys.path.append('./libs/')
sys.path.append('./app/connect/src/')
sys.path.append('./app/libs/')

import locale
locale.setlocale(locale.LC_ALL, 'lv_LV.UTF-8')

from essa import essa_config
from essa import GITHUB, HOMEPAGE
from essa.version import VERSION as ESSA_VERSION
from essa.platform.eklaselv.connect import Connect

import tkinter as tk
from tkinter import font
import ttkbootstrap as ttk

from gui.about import About
from gui.contact import Contact
from gui.license import License
from gui.schedule import Schedule
from gui.journalevt import JournalEVTeacher
from gui.journalevp import JournalEVPupil
from gui.journalsr import JournalSR
from gui.settings import Settings
from gui.startpage import StartPage
from gui.eklaseauth import EKlaseAuth
from gui.eklasedata import EKlaseGetData
from gui.version import VERSION as GUI_VERSION

# app protection
from gui import app_protection_config

app_passwd = app_protection_config.get('app_passwd', '')
app_expire = app_protection_config.get('app_expire', '')
app_db_encrypt = app_protection_config.get('app_db_encrypt', False)
app_db_password = app_protection_config.get('app_db_password', '')

from functions import days_between, copyright_notice, is_module_available

# app root directory
app_data_dir_prefix = '/../data/'
if getattr(sys, 'frozen', False):
    import pyi_splash
    
    app_dir = os.getcwd()    
    app_data_dir_prefix = '/data/'
    app_data_dir = app_dir + app_data_dir_prefix
        
    if not os.path.exists(app_data_dir):
        # print(sys._MEIPASS + app_data_dir_prefix, app_data_dir)
        shutil.copytree(sys._MEIPASS + '/data', app_dir + '/data', dirs_exist_ok=True) # data directory
        shutil.copytree(sys._MEIPASS + '/docs', app_dir + '/docs', dirs_exist_ok=True) # web documentation
        shutil.copyfile(sys._MEIPASS + '/data/LICENSE.txt', app_dir + '/LICENSE.txt') # license file
            
    HOMEPAGE = app_data_dir + '../docs/index.html' # local webpage
else:
    app_dir = os.path.dirname(os.path.abspath(__file__))
    app_data_dir_prefix = '/../data/'
    app_data_dir = app_dir + app_data_dir_prefix
    # print(app_dir, app_data_dir)
    HOMEPAGE = app_dir + '/../docs/index.html' # local webpage

# load configuration files
try:
    essa_config.read(app_data_dir + '/conf/essa.conf', encoding='utf8')
    essa_config.read(app_data_dir + '/conf/gui.conf', encoding='utf8')
    essa_config.read(app_data_dir + '/conf/journal.conf', encoding='utf8')
    essa_config.read(app_data_dir + '/conf/timetable.conf', encoding='utf8')
    essa_config.read(app_data_dir + '/conf/custom.conf', encoding='utf8')
except:
    pass

class App(tk.Tk):
    def __init__(self, platform=None, window_width=1100, window_height=600, window_center=True, window_menu=True):
        super().__init__()

        self.platform = platform
        self.app_dir = app_dir
        self.app_data_dir = app_data_dir
        self.essa_config = essa_config

        # auth and expire app
        self.app_passwd = app_passwd
        self.app_expire = app_expire

        self.show_login_frame = False
        self.user_auth = True if self.app_passwd == '' else False
        self.enable_check_expiration = False
        
        # encrypt db if needed
        
        self.platform.set_db_encrypt(app_db_encrypt if is_module_available('sqlcipher3') else False)
        self.platform.set_db_decrypted(None)
        self.platform.set_db_cipher_compatibility(4)
        self.platform.set_db_password(str(base64.b64decode(app_db_password).decode('ascii')))

        # main
        self.title('ESSA :: Elektroniskās Skolvadības Sistēmas Asistents')
        self.homepage = HOMEPAGE
        
        # images
        if os.path.exists(self.app_data_dir + '/gfx/essa.ico'):
            self.iconbitmap(bitmap=self.app_data_dir + '/gfx/essa.ico')
            
        if os.path.exists(self.app_data_dir + '/gfx/essa_idea.png'):
            self.background_image = tk.PhotoImage(file=self.app_data_dir + '/gfx/essa_idea.png')
        else:
            self.background_image = None

        if os.path.exists(self.app_data_dir + '/gfx/essa_splash_400.png'):
            self.logo_image = tk.PhotoImage(file=self.app_data_dir + '/gfx/essa_splash_400.png')
        else:
            self.logo_image = None

        # get theme from config
        try:
            theme = self.essa_config['GUI.Style']['Theme']
        except:
            theme = 'united'
        
        self.style = ttk.Style()
        
        if theme == 'essa':
            self.style.load_user_themes(self.app_data_dir + '/conf/themes.json')
            self.style.theme_use('essa')
        else:
            self.style.theme_use(theme)

        # font
        self.default_font_name = 'Arial'
        self.default_font_size = 11
        self.default_font = font.nametofont('TkDefaultFont') 
        self.default_font.configure(family=self.default_font_name, size=self.default_font_size, weight=font.NORMAL) 

        # window position
        if window_center:
            screen_width = self.winfo_screenwidth()
            screen_height = self.winfo_screenheight()
            center_x = int((screen_width - window_width)/2)
            center_y = int((screen_height - window_height)/2)
            # fix position
            center_x -= 5
            center_y -= 50
            self.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')
        else:
            self.geometry(f'{window_width}x{window_height}')
        
        self.wait_visibility()
        self.resizable(False, False)
        # self.attributes('-alpha', 0.6)
        # self.wm_attributes('-disabled', True)

        # topmost window
        self.attributes('-topmost', True)
        self.after(1000, lambda: self.attributes('-topmost', False))

        self.view_width = window_width
        self.view_height = window_height

        # main menu
        if window_menu:
            self.view_height -= 20

            self.menubar = ttk.Menu(self)
            self.config(menu=self.menubar)

            # platform menu        
            tools_menu = ttk.Menu(self.menubar, tearoff=0)
            tools_menu.add_command(label='Sākums', command=lambda: self.show_frame(StartPage))
            tools_menu.add_separator()
            tools_menu.add_command(label='Stundu sarakstu veidošana', command=lambda: self.show_frame(Schedule))
            tools_menu.add_command(label='Žurnāla analīze “EV” - Skolotāji', command=lambda: self.show_frame(JournalEVTeacher))
            tools_menu.add_command(label='Žurnāla analīze “EV” - Skolēni', command=lambda: self.show_frame(JournalEVPupil))
            tools_menu.add_command(label='Žurnāla analīze “SR”', command=lambda: self.show_frame(JournalSR))
            tools_menu.add_separator()
            tools_menu.add_command(label='Excel datu mape', command=lambda: self.open_dir(self.excel_dir))
            tools_menu.add_separator()
            tools_menu.add_command(label='Exit', command=self.destroy)

            # add the platform menu to the menubar
            self.menubar.add_cascade(label='Rīki', menu=tools_menu)

            # platform menu        
            platform_menu = ttk.Menu(self.menubar, tearoff=0)
            platform_menu.add_command(label='Autorizācija', command=lambda: self.show_frame(EKlaseAuth))
            platform_menu.add_command(label='Datu lejupielādēšana', command=lambda: self.show_frame(EKlaseGetData))          

            # add the platform menu to the menubar
            self.menubar.add_cascade(label='E-klase', menu=platform_menu)

            # settings menu
            settings_menu = ttk.Menu(self.menubar, tearoff=0)
            settings_menu.add_command(label='Uzstādījumi', command=lambda: self.show_frame(Settings))
            settings_menu.add_separator()
            settings_menu.add_command(label='Dzēst Excel failu no mapes', command=self.remove_excel_data_dir)
            settings_menu.add_command(label='Dzēst DB failu no mapes', command=self.remove_db_data_dir)
            if getattr(sys, 'frozen', False):
                settings_menu.add_separator()
                settings_menu.add_command(label='Dzēst visus programmas datus', command=self.remove_all_data_dir)

            # add the help menu to the menubar
            self.menubar.add_cascade(label='Uzstādījumi', menu=settings_menu)

            # help menu
            help_menu = ttk.Menu(self.menubar, tearoff=0)
            help_menu.add_command(label='Par ESSA', command=lambda: self.show_frame(About))
            help_menu.add_command(label='Programmas lietošanas instrukcija', command=lambda: webbrowser.open(HOMEPAGE))
            help_menu.add_separator()
            help_menu.add_command(label='Kontakti', command=lambda: self.show_frame(Contact))
            help_menu.add_command(label='GitHub repozitorijs', command=lambda: webbrowser.open(GITHUB))
            help_menu.add_separator()
            help_menu.add_command(label='Licence', command=lambda: self.show_frame(License))
        
            # add the help menu to the menubar
            self.menubar.add_cascade(label='Palīdzība', menu=help_menu)

        # settings for eklase.lv
        self.platform.set_date(self.platform.get_next_monday()) # next monday, format YYYY-MM-DD
        self.platform.set_default_urls()
        self.platform.set_req_user_agent(essa_config['Request']['UserAgent'])
        self.platform.set_save_dir(self.app_data_dir + '/platform')
        self.platform.check_save_dir()
        self.platform.set_sleep_time(float(essa_config['Request']['SleepTime']))

        # excel
        self.excel_dir = self.app_data_dir + '/' + essa_config['TimeTable.Excel']['ExcelFileDir']
        if not os.path.exists(self.excel_dir):
            os.makedirs(self.excel_dir)

        # cache
        self.journal_sql_query_params_cache = []
        self.pupil_sql_query_params_cache = []

        # creating a container
        container = ttk.Frame(self)
        container.pack(side='top', fill='both', expand=True)       

        # initializing frames
        self.frames = {}

        # iterating through a tuple consisting of the different page layouts
        for F in (StartPage, About, Contact, License, Schedule, JournalEVTeacher, JournalEVPupil, JournalSR, Settings, EKlaseAuth, EKlaseGetData):
            frame = F(container, self, self.platform)
            self.frames[F] = frame 
            frame.grid(row=0, column=0, sticky='nsew')
  
        self.frame_before = None
        self.frame = None
        self.show_frame(StartPage)

    def show_frame(self, container):
        if not self.check_expiration():
            # self.frame.lock_frame()
            return False
                    
        if self.frame:            
            self.frame.after()
            if self.frame.is_locked():
                return False

        if container in [Schedule, JournalEVTeacher, JournalEVPupil, JournalSR, Settings, EKlaseAuth, EKlaseGetData]:
            if not self.user_auth:
                self.frame_before = container
                self.show_login_frame = True
                self.show_frame(StartPage)
                return False

        self.frame = self.frames[container]
        self.frame.before()
        self.frame.tkraise()
        self.frame.event_generate("<<ShowFrame>>")

        self.bottom_bar()

    def show_frame_name(self, name):
        if not self.check_expiration():
            # self.frame.lock_frame()
            return False
                
        if name in ['Schedule', 'JournalEVTeacher', 'JournalEVPupil', 'JournalSR', 'Settings', 'EKlaseAuth', 'EKlaseGetData']:
            if not self.user_auth:
                self.frame_before = name
                self.show_login_frame = True
                self.show_frame(StartPage)
                return False

        if name == 'StartPage':
            self.show_login_frame = False
            self.show_frame(StartPage)
        elif name == 'About':
            self.show_frame(About)
        elif name == 'Contact':
            self.show_frame(Contact)
        elif name == 'License':
            self.show_frame(License)
        elif name == 'Schedule':
            self.show_frame(Schedule)
        elif name == 'JournalEVTeacher':
            self.show_frame(JournalEVTeacher)
        elif name == 'JournalEVPupil':
            self.show_frame(JournalEVPupil)
        elif name == 'JournalSR':
            self.show_frame(JournalSR)
        elif name == 'Settings':
            self.show_frame(Settings)
        elif name == 'EKlaseAuth':
            self.show_frame(EKlaseAuth)
        elif name == 'EKlaseGetData':
            self.show_frame(EKlaseGetData)

    def update_menu_states(self, new_state):
        menulabels = ['Rīki', 'E-klase', 'Uzstādījumi', 'Palīdzība']
        for menulabel in menulabels:
            self.menubar.entryconfig(menulabel, state=new_state)

    def message_box(self, title='', message='', yesno=False, callback=None, window_width=380, window_height=180):
        box = ttk.Toplevel(self, windowtype='')
        box.attributes('-toolwindow', 1)
        box.attributes('-topmost', 1)
        box.wait_visibility()

        parent_pos_x = self.winfo_x()
        parent_pos_y = self.winfo_y()
        parent_width = self.winfo_width()
        parent_height = self.winfo_height()
        
        center_x = parent_pos_x + int((parent_width - window_width)/2)
        center_y = parent_pos_y + int((parent_height - window_height)/2)

        box.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')

        box.title(title)
        ttk.Label(box, text=message, font=(self.default_font_name, 10, 'normal'), wraplength=(window_width-20)).pack(padx=10, pady=(20,10), fill='both')
        
        if yesno:
            ttk.Button(box, text='Jā', command=lambda:(callback(), box.destroy()), width=10).pack(padx=(50,0), pady=(10,30), fill='x', side='left', anchor='s')
            ttk.Button(box, text='Nē', command=box.destroy, width=10).pack(padx=(0,50), pady=(10,30), fill='x', side='right', anchor='s')
        else:
            ttk.Button(box, text='Ok', command=box.destroy).pack(ipadx=30, padx=10, pady=(10,30), fill='none', side='bottom', anchor='s')

        box.focus()

        # required to make window show before the program gets to the mainloop
        self.update()

    def top_menu_buttons(self, frame):
        sf = ttk.Style()
        sf.configure('my.TFrame', background="#f8dbb1")

        frame.pack(fill='x', anchor='w', padx=(0,0), pady=(0,0), ipady=10, expand=False)
        frame.config(style='my.TFrame')

        sb = ttk.Style()
        sb.configure('my.TButton', font=(self.default_font_name, 9, 'bold'), background="#e57813")

        button = ttk.Button(frame, text='STUNDU\nSARAKSTS', bootstyle='primary.outline.TButton', style='my.TButton', width=12, padding=6, command=lambda: self.show_frame_name('Schedule'))            
        button.pack(fill='none', side='left', padx=(10,10))

        button = ttk.Button(frame, text='ANALĪZE “EV”\nSKOLOTĀJI', bootstyle='primary.outline.TButton', style='my.TButton', width=12, padding=6, command=lambda: self.show_frame_name('JournalEVTeacher'))            
        button.pack(fill='none', side='left', padx=(0,10))

        button = ttk.Button(frame, text='ANALĪZE “EV”\nSKOLĒNI', bootstyle='primary.outline.TButton', style='my.TButton', width=12, padding=6, command=lambda: self.show_frame_name('JournalEVPupil'))            
        button.pack(fill='none', side='left', padx=(0,10))

        button = ttk.Button(frame, text='ŽURNĀLA\nANALĪZE “SR”', bootstyle='primary.outline.TButton', style='my.TButton', width=12, padding=6, command=lambda: self.show_frame_name('JournalSR'))            
        button.pack(fill='none', side='left', padx=(0,10))

        button = ttk.Button(frame, text='DATU\nLEJUPIELĀDĒŠANA', bootstyle='primary.outline.TButton', style='my.TButton', width=16, padding=6, command=lambda: self.show_frame_name('EKlaseGetData'))            
        button.pack(fill='none', side='left', padx=(0,10))

        button = ttk.Button(frame, text='SĀKUMS', bootstyle='primary.outline.TButton', style='my.TButton', width=10, padding=12, command=lambda: self.show_frame_name('StartPage'))            
        button.pack(fill='none', side='right', padx=(0,10))

        button = ttk.Button(frame, text='PAR ESSA', bootstyle='primary.outline.TButton', style='my.TButton', width=10, padding=12, command=lambda: self.show_frame_name('About'))            
        button.pack(fill='none', side='right', padx=(0,10))

    def top_bar(self):
        top_frame = ttk.Frame(self, width=self.view_width, height=20, bootstyle='dark')
        top_frame.place(x=0, y=0, width=self.view_width)
        
        label1 = ttk.Label(top_frame, text='', font=(self.default_font_name, 9, 'bold'), bootstyle='inverse-dark')
        label1.place(x=5, y=0)

    def bottom_bar(self, message=''):
        bottom_frame = ttk.Frame(self, width=self.view_width, height=25, bootstyle='dark')
        bottom_frame.place(x=0, y=self.view_height-25, width=self.view_width)
        
        try:
            expire_days = days_between(str(date.today()), self.app_expire)
        except:
            expire_days = 100

        if self.platform.is_authenticated:
            auth_info = 'Esi ielogojies elektroniska skolvadības sistēmā'
        else:
            if expire_days < 0:
                auth_info = 'Programmas derīguma termiņš beidzās.'
            elif expire_days == 0:
                auth_info = 'Programmas derīguma termiņš beigsies šodien!'
            elif expire_days == 1:
                auth_info = 'Programmas derīguma termiņš beigsies rīt!'
            elif expire_days > 1 and expire_days <= 10:
                auth_info = 'Programmas derīguma termiņš beigsies pēc '+str(expire_days)+' dienām.'
            else:
                auth_info = '' # 'Neesi ielogojies elektroniska skolvadības sistēmā'

        if message == '':
            message = auth_info

        label1 = ttk.Label(bottom_frame, text=message, font=(self.default_font_name, 9, 'bold'), bootstyle='inverse-dark')
        label1.place(x=5, y=2)

        label2 = ttk.Label(bottom_frame, text='GUI:'+GUI_VERSION+' DRV:'+ESSA_VERSION, font=(self.default_font_name, 9, 'bold'), bootstyle='inverse-dark')
        label2.place(x=self.view_width-120, y=2)

    def db_last_update(self):
        journal_last_download = False
        db_file = self.platform.db_dir + self.platform.db_journal_file_name
        if os.path.exists(db_file):
            timestamp = os.path.getmtime(db_file)
            datestamp_journal = datetime.fromtimestamp(timestamp)
            journal_last_download = True

        timetable_last_download = False
        db_file = self.platform.db_dir + self.platform.db_timetable_file_name
        if os.path.exists(db_file):
            timestamp = os.path.getmtime(db_file)
            datestamp_timetable = datetime.fromtimestamp(timestamp)
            timetable_last_download = True

        text = ''
        if timetable_last_download or journal_last_download:
            text = 'Pēdējais datubāzes atjauninājums:'
            if timetable_last_download:
                text += '\n» stundu saraksts ↓ ' + str(datestamp_timetable)[:16] # "2025-10-01 12:00"
            if journal_last_download:
                text += '\n» žurnāls ↓ ' + str(datestamp_journal)[:16] # "2025-10-01 12:00" 
        
        return str(text)

    def remove_excel_data_dir(self):            
        if not self.user_auth:
            self.show_login_frame = True
            self.show_frame(StartPage)
            return False

        is_files = False
        if os.path.exists(self.excel_dir):
            base_path = pathlib.Path(self.excel_dir)
            files_cnt = len(list(base_path.glob('*.xlsx')))
            # print(files_cnt)
            if files_cnt > 0:
                is_files = True

        if is_files:
            self.message_box(
                title='Uzmanību!', 
                message='Atradu saglabātos datus Excel formatā.\nVai tiešām vēlies izdzēst šos datus?', 
                callback=lambda: self.remove_files(self.excel_dir, '.xlsx'), 
                yesno=True)
        else:
            self.message_box('Informācija','Nav datu, ko dzēst.')

    def remove_db_data_dir(self):
        if not self.user_auth:
            self.show_login_frame = True
            self.show_frame(StartPage)
            return False

        is_files = False
        if os.path.exists(self.platform.db_dir):
            base_path = pathlib.Path(self.platform.db_dir)
            files_cnt = len(list(base_path.glob('*.db')))
            # print(files_cnt)
            if files_cnt > 0:
                is_files = True

        if is_files:
            self.message_box(
                title='Uzmanību!', 
                message='Atradu saglabātos datus DB formatā.\nVai tiešām vēlies izdzēst šos datus?', 
                callback=lambda: self.remove_files(self.platform.db_dir, '.db'), 
                yesno=True)
        else:
            self.message_box('Informācija','Nav datu, ko dzēst.')

    def remove_all_data_dir(self):
        if not self.user_auth:
            self.show_login_frame = True
            self.show_frame(StartPage)
            return False

        def remove():
            try:
                if app_data_dir.endswith(app_data_dir_prefix):
                    shutil.rmtree(app_data_dir)
                    self.destroy()
            except:
                pass

        if getattr(sys, 'frozen', False) and app_data_dir.endswith(app_data_dir_prefix):
            self.message_box(
                title='Uzmanību!', 
                message='Vai vēlies izdzēst visus programmas datus?\nPēc datu dzēšanas programma tiks pabeigta.', 
                callback=remove, 
                yesno=True)
        else:
            print("Developer mode")

    def remove_files(self, path, file_name_ext = '.xlsx'):
        if os.path.isdir(path):
            for file_name in os.listdir(path):
                if file_name.endswith(file_name_ext):
                    # print(path + '/' + file_name)
                    os.remove(path + '/' + file_name)
            self.frame.before()
            self.show_frame(StartPage)

    def open_dir(self, path = ''):
        if not self.user_auth:
            self.show_login_frame = True
            self.show_frame(StartPage)
            return False

        path = os.path.realpath(path)
        os.startfile(path)

    def check_expiration(self):        
        if self.enable_check_expiration:        
            today = date.today()
            if self.app_expire and self.app_expire <= str(today):
                self.message_box('Informācija','Programmas derīguma termiņš beidzās.\n\nJauno versiju vari lejupielādēt no: '+GITHUB, window_height=220)
                return False
        else:
            self.enable_check_expiration = True
        return True     

    def tksleep(self, time:float) -> None:
        '''
        Emulating `time.sleep(seconds)`
        Created by TheLizzard, inspired by Thingamabobs
        '''
        self.after(int(time*1000), self.quit)
        self.mainloop()
    tk.Misc.tksleep = tksleep

if __name__ == '__main__':
    platform = Connect()
    app = App(platform=platform, window_width=1100, window_height=620)
    try:
        app.iconbitmap(app_data_dir + '/gfx/essa.ico')

        from ctypes import windll, byref, sizeof, c_int
        from ctypes.wintypes import HWND
        title_bar_color = 0x00302716
        title_text_color = 0x00FFFFFF
        HWND = windll.user32.GetParent(app.winfo_id())
        windll.dwmapi.DwmSetWindowAttribute(HWND, 35, byref(c_int(title_bar_color)), sizeof(c_int))
        windll.dwmapi.DwmSetWindowAttribute(HWND, 36, byref(c_int(title_text_color)), sizeof(c_int))
    finally:
        if getattr(sys, 'frozen', False):
            pyi_splash.close()
        
        copyright_notice()
        app.mainloop()