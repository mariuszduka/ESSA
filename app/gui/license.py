'''
ESSA :: Electronic Grade Book Assistant
Copyright (C) 2025 Mariusz Duka
This file is part of ESSA and is licensed under the GNU GPLv3 or later.
See the LICENSE file for full text.
'''

import os
import tkinter as tk
import ttkbootstrap as ttk

class License(ttk.Frame):
    def __init__(self, parent, controller, platform): 
        ttk.Frame.__init__(self, parent, width=controller.view_width, height=controller.view_height)

        self.lock = False

        self.platform = platform
        self.controller = controller

        self.app_data_dir = self.controller.app_data_dir
        self.essa_config = self.controller.essa_config

        self.license_file = self.app_data_dir + '/license.txt'

        # TOP FRAME
        self.main_frame = ttk.Frame(self)
        self.controller.top_menu_buttons(self.main_frame)

        # LEFT FRAME
        self.left_frame = ttk.Frame(self)
        self.left_frame.pack(fill='none', padx=10, pady=(0,95), expand=True)

        tree_scroll_y = ttk.Scrollbar(self.left_frame, orient=tk.VERTICAL)

        label = ttk.Label(self.left_frame, text='PROGRAMMATŪRAS ESSA LIETOŠANAS LICENCES LĪGUMS', justify='center', font=(controller.default_font_name, 11, 'bold'))
        label.pack(pady=(20,0), expand=False)

        self.text_box_config = ttk.Text(self.left_frame, height=21, width=120, wrap='word', font=("Consolas", 11), yscrollcommand=tree_scroll_y.set)

        tree_scroll_y.config(command=self.text_box_config.yview)
        tree_scroll_y.pack(side=tk.RIGHT, fill='y', pady=20)

        self.text_box_config.pack(side='left', pady=(20,20), expand=False)

        try:
            with open(os.path.join(self.app_data_dir, 'LICENSE.txt'), encoding='utf8') as f:
                self.license_text = f.read()
        except Exception:
            self.license_text = 'ESSA is licensed under the GNU General Public License v3.0 or later — see https://www.gnu.org/licenses/gpl-3.0.html.'

    def before(self):
        # self.open_license_file(self.license_file)
        self.text_box_config.delete('1.0', ttk.END)
        self.text_box_config.insert(ttk.END, self.license_text)
    
    def after(self):
        pass

    def is_locked(self):
        return self.lock

    def open_license_file(self, file_name = ''):
        if file_name != '':
            if os.path.isfile(file_name):
                text_file = open(file_name, encoding='utf8')
                content = text_file.read()
                text_file.close()
                self.text_box_config.delete('1.0', ttk.END)
                self.text_box_config.insert(ttk.END, content)
            else:
                self.controller.message_box('Kļūda','Nevaru atvērt failu ar programmas lietošanas licenci.')
