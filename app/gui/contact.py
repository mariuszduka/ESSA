'''
ESSA :: Electronic Grade Book Assistant
Copyright (C) 2025 Mariusz Duka
This file is part of ESSA and is licensed under the GNU GPLv3 or later.
See the LICENSE file for full text.
'''

import webbrowser
import ttkbootstrap as ttk
from essa import GITHUB, HOMEPAGE

class Contact(ttk.Frame):
    def __init__(self, parent, controller, platform): 
        ttk.Frame.__init__(self, parent, width=controller.view_width, height=controller.view_height)

        self.lock = False

        self.platform = platform
        self.controller = controller

        background = ttk.Label(self, image=controller.background_image)
        background.place(x=760, y=520, anchor='w')

        # TOP FRAME
        self.main_frame = ttk.Frame(self)
        self.controller.top_menu_buttons(self.main_frame)

        text_1 = '''
ESSA :: Elektroniskās Skolvadības Sistēmas Asistents

Programmas autors:
© Mariusz Duka


Droši raksti man, ja Tev ir kādi jautājumi par programmas lietošanu.
'''
        text_2 = '''
'''

        logo = ttk.Label(self, image=controller.logo_image)
        logo.pack(side='right', anchor='ne', padx=(0,60), pady=(80,0))

        label = ttk.Label(self, text=text_1, font=self.controller.default_font)
        label.pack(anchor='w', padx=(60,0), pady=(60,0))

        btn_frame = ttk.Frame(self)
        btn_frame.pack(anchor='w', padx=(60,0), pady=(20,0))

        btn_email = ttk.Button(btn_frame, text='E-pasts', command=lambda: webbrowser.open('mailto:mariusz@duka.lv'), style='Outline.TButton')
        btn_email.pack(side='left', padx=(0, 15))

        btn_www = ttk.Button(btn_frame, text='WWW', command=lambda: webbrowser.open('https://duka.lv'), style='Outline.TButton')
        btn_www.pack(side='left', padx=(0, 15))
        
        """
        btn1 = ttk.Button(btn_frame, text='WWW', command=lambda: webbrowser.open(HOMEPAGE), style='Outline.TButton')
        btn1.pack(side='left', padx=(0, 15))

        btn2 = ttk.Button(btn_frame, text='GitHub', command=lambda: webbrowser.open(GITHUB), style='Outline.TButton')
        btn2.pack(side='left')
        """
        
        label = ttk.Label(self, text=text_2, font=self.controller.default_font)
        label.pack(anchor='w', padx=(60,0), pady=(20,0))

        '''
        btn3 = ttk.Button(self, text='Licence', command=lambda: self.controller.show_frame_name('License'), style='Outline.TButton')
        btn3.pack(anchor='w', padx=(60,0), pady=(20,0))
        '''

    def before(self):
        pass
    
    def after(self):
        pass

    def is_locked(self):
        return self.lock