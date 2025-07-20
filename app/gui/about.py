'''
ESSA :: Electronic Grade Book Assistant
Copyright (C) 2025 Mariusz Duka
This file is part of ESSA and is licensed under the GNU GPLv3 or later.
See the LICENSE file for full text.
'''

import webbrowser
import ttkbootstrap as ttk
from essa import GITHUB, HOMEPAGE

class About(ttk.Frame):
    def __init__(self, parent, controller, platform): 
        ttk.Frame.__init__(self, parent, width=controller.view_width, height=controller.view_height)

        # local webpage
        HOMEPAGE = controller.homepage

        self.lock = False

        self.platform = platform
        self.controller = controller

        background = ttk.Label(self, image=controller.background_image)
        background.place(x=735, y=510, anchor='w')

        # TOP FRAME
        self.main_frame = ttk.Frame(self)
        self.controller.top_menu_buttons(self.main_frame)

        logo = ttk.Label(self, image=controller.logo_image)
        logo.pack(side='right', anchor='ne', padx=(0,60), pady=(80,0))

        about_text = ttk.Text(self, font=self.controller.default_font, wrap='word', height=19, width=50, highlightthickness=0, borderwidth=0)
        about_text.tag_configure('bold1', font=(self.controller.default_font_name, self.controller.default_font_size-1, 'bold'))
        about_text.tag_configure('bold2', font=(self.controller.default_font_name, self.controller.default_font_size, 'bold'))


        about_text.insert('end', 'Programmas funkcionalitāte\n\n', 'bold2') 

        about_text.insert('end', 'Stundu saraksta izgūšana\n', 'bold1')
        about_text.insert('end', 'Izmantojot ESSA, tu vari ātri un ērti izgūt stundu sarakstu\n')
        about_text.insert('end', 'izvēlētajām klasēm no skolvadības sistēmas. Programma\n')
        about_text.insert('end', 'piedāvā arī iespēju pievienot stundu laikus, skolotājus\n')
        about_text.insert('end', 'un fakultatīvās un interešu izglītības nodarbības.\n\n')

        about_text.insert('end', 'Detalizēta vērtējumu analīze\n', 'bold1')

        about_text.insert('end', 'Izmantojot ESSA, tu vari ātri un ērti izgūt pārskatāmus\n')
        about_text.insert('end', 'kopsavilkumus par skolotāju izliktajiem vērtējumiem, kā arī\n')
        about_text.insert('end', 'izgūt datus par skolēnu mācību sasniegumu vērtējumiem.\n\n')

        about_text.insert('end', 'Mācību stundu tēmu analīze\n', 'bold1')

        about_text.insert('end', 'Programma palīdz pārbaudīt, vai mācību stundu ieraksti\n')
        about_text.insert('end', 'elektroniskajā žurnālā atbilst noteiktajiem standartiem.\n')
        about_text.insert('end', 'ESSA analizē tēmu saturu un izceļ tās, kurās trūkst\n')
        about_text.insert('end', 'nepieciešamo frāžu, piemēram, "Sasniedzamie rezultāti".\n')

        about_text.config(state='disabled', cursor='arrow', background='#f2f2f2', highlightthickness=0, borderwidth=0, takefocus=0)  # Make the Text widget read-only, disable text selection, set background, and remove border
        about_text.bind("<1>", lambda e: "break")  # Disable text selection by blocking mouse clicks
        about_text.pack(anchor='w', padx=(60, 0), pady=(50, 0))
       
        btn_frame = ttk.Frame(self)
        btn_frame.pack(anchor='w', padx=(65,0))

        btn1 = ttk.Button(btn_frame, text='Instrukcija', command=lambda: webbrowser.open(HOMEPAGE), style='Outline.TButton')
        btn1.pack(side='left', anchor='nw', padx=(0, 15))

        btn2 = ttk.Button(btn_frame, text='Kontakti', command=lambda: self.controller.show_frame_name('Contact'), style='Outline.TButton')
        btn2.pack(side='left', padx=(0, 15))

        btn3 = ttk.Button(btn_frame, text='GitHub', command=lambda: webbrowser.open(GITHUB), style='Outline.TButton')
        btn3.pack(side='left')        


    def before(self):
        pass
    
    def after(self):
        pass

    def is_locked(self):
        return self.lock