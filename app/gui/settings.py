'''
ESSA :: Electronic Grade Book Assistant
Copyright (C) 2025 Mariusz Duka
This file is part of ESSA and is licensed under the GNU GPLv3 or later.
See the LICENSE file for full text.
'''

import os
import tkinter as tk
import ttkbootstrap as ttk
import configparser

class Settings(ttk.Frame):
    def __init__(self, parent, controller, platform): 
        ttk.Frame.__init__(self, parent, width=controller.view_width, height=controller.view_height)

        self.lock = False

        self.platform = platform
        self.controller = controller

        self.app_data_dir = self.controller.app_data_dir
        self.essa_config = self.controller.essa_config

        self.custom_conf_file = self.app_data_dir + '/conf/custom.conf'
        self.default_conf_file = self.app_data_dir + '/conf/default.conf'

        # TOP FRAME
        self.main_frame = ttk.Frame(self)
        self.controller.top_menu_buttons(self.main_frame)

        # LEFT FRAME
        self.left_frame = ttk.Frame(self)
        self.left_frame.pack(fill='none', padx=10, pady=(0,20), expand=True)

        tree_scroll_y = ttk.Scrollbar(self.left_frame, orient=tk.VERTICAL)

        label = ttk.Label(self.left_frame, text='PROGRAMMAS UZSTĀDĪJUMI', justify='center', font=(controller.default_font_name, 11, 'bold'))
        label.pack(pady=(20,0), expand=False)

        label = ttk.Label(self.left_frame, text='Visas konfigurācijas izmaiņas jāveic ļoti uzmanīgi.', justify='center', font=(controller.default_font_name, 9, 'italic'))
        label.pack(pady=(0,0), expand=False)

        self.text_box_config = ttk.Text(self.left_frame, height=17, width=120, wrap='none', font=("Consolas", 11), yscrollcommand=tree_scroll_y.set)

        tree_scroll_y.config(command=self.text_box_config.yview)
        tree_scroll_y.pack(side=tk.RIGHT, fill='y', pady=20)

        self.text_box_config.pack(side='left', pady=(20,20), expand=False)

        btn1 = ttk.Button(self, text="Saglabāt", command=self.save_config_file)
        btn1.pack(side='left', padx=(200,0), pady=(0,100))

        btn2 = ttk.Button(self, text="Ielādē standarta uzstādījumi", style='light.TButton', command=self.default_config)
        btn2.pack(side='right', padx=(0,200), pady=(0,100))

    def before(self):
        self.open_config_file(self.custom_conf_file)
    
    def after(self):
        pass

    def is_locked(self):
        return self.lock

    def open_config_file(self, file_name = ''):
        if file_name != '':
            if os.path.isfile(file_name):
                text_file = open(file_name, encoding='utf8')
                content = text_file.read()
                text_file.close()
                self.text_box_config.delete('1.0', ttk.END)
                self.text_box_config.insert(ttk.END, content)
            else:
                self.controller.message_box('Kļūda','Nevaru atvērt programmas konfigurācijas failu.')

    def save_config_file(self):
        text = self.text_box_config.get(1.0, ttk.END)
        config = configparser.ConfigParser()
        try:
            config.read_string(text)
            
            text_file = open(self.custom_conf_file, 'w', encoding='utf8')
            text_file.write(text)
            text_file.close()

            self.essa_config.read(self.custom_conf_file, encoding='utf8')

            self.controller.message_box('Informācija','Konfigurācija ir saglabāta.')
        except:
            self.controller.message_box('Kļūda','Konfigurācija ir nepareiza!')

    def default_config(self):
        self.controller.message_box(
            title='Uzmanība!', 
            message='Vai vēlaties ielādēt standarta iestatījumus?\nVisi iepriekšējie uzstādījumi tiks dzēsti!', 
            callback=lambda: self.open_config_file(self.default_conf_file), 
            yesno=True)