'''
ESSA :: Electronic Grade Book Assistant
Copyright (C) 2026 Mariusz Duka
This file is part of ESSA and is licensed under the GNU GPLv3 or later.
See the LICENSE file for full text.
'''

import re
import ttkbootstrap as ttk

class EKlaseAuth(ttk.Frame):
    def __init__(self, parent, controller, platform): 
        ttk.Frame.__init__(self, parent, width=controller.view_width, height=controller.view_height)

        self.lock = False

        self.platform = platform
        self.controller = controller

        self.login = ttk.StringVar()
        self.password = ttk.StringVar()

        # TOP FRAME
        self.main_frame = ttk.Frame(self)
        self.controller.top_menu_buttons(self.main_frame)

        # LEFT FRAME LOGIN
        self.left_frame = ttk.Frame(self)
        self.left_frame.pack(side='left', fill='none', padx=10, pady=(0,110), expand=True)

        label = ttk.Label(self.left_frame, text='AUTORIZĒTIES AR E-KLASE', justify='center', font=(controller.default_font_name, 11, 'bold'))
        label.pack(pady=(40,20), expand=True)

        # user name
        login_label = ttk.Label(self.left_frame, text='Lietotājvārds:')
        login_label.pack(fill='x', expand=True)

        login_entry = ttk.Entry(self.left_frame, textvariable=self.login, font=(controller.default_font_name, 11, 'normal'))
        login_entry.pack(fill='x', expand=True, pady=(0,10))
        login_entry.bind('<Return>', self.auth_login)
        login_entry.focus()

        # password
        password_label = ttk.Label(self.left_frame, text='Parole:')
        password_label.pack(fill='x', expand=True)

        password_entry = ttk.Entry(self.left_frame, textvariable=self.password, show='*', font=(controller.default_font_name, 11, 'normal'))
        password_entry.pack(fill='x', expand=True, pady=(0,10))
        password_entry.bind('<Return>', self.auth_login)

        # auth button
        self.login_button = ttk.Button(self.left_frame, text='Autorizācija', command=self.auth_login)
        self.login_button.pack(fill='x', expand=True, pady=(10,20))

        # LEFT FRAME LOGOUT
        self.left_frame_logout = ttk.Frame(self)
        self.left_frame_logout.pack(side='left', fill='none', padx=10, pady=(0,110), expand=True)

        label = ttk.Label(self.left_frame_logout, text='AUTORIZĒTIES AR E-KLASE', justify='center', font=(controller.default_font_name, 11, 'bold'))
        label.pack(pady=(0,20), expand=True)

        # auth button
        self.logout_button = ttk.Button(self.left_frame_logout, text='Izlogoties', command=self.auth_logout)
        self.logout_button.pack(fill='x', expand=True, pady=(20,75))

        # RIGHT FRAME
        right_frame = ttk.Frame(self)
        right_frame.pack(side='right', fill='none', padx=(10,140), pady=(10,90), expand=False)

        text_info = '''Lai izgūtu datus no elektroniskās skolvadības sistēmas ir jābūt autorizētai darbinieka piekļuvei. '''
        text_info += '''Datu analīzes apjoms ir atkarīgs no piešķirtajām tiesībām E-klasē.\n'''
        text_info += '''Drošības dēļ, tavi piekļuves dati (lietotājvārds un parole) nekur netiek saglabāti. '''
        text_info += '''Visi izgūtie dati ir šifrēti, kas neļauj tos nolasīt neautorizētām personām. '''
        text_info += '''Datu izgūšanas mehānisms ir veidots tā, lai netraucētu normālu E-klase sistēmas darbību. '''
        text_info += '''\nAtceries! Nedalies ar E-klase sistēmas piekļuves datiem. '''
        text_info += '''Ja nevari ielogoties, pārbaudi, vai tavi dati ir pareizi un vai izmanto jaunāko programmas versiju. '''

        text_box = ttk.Text(right_frame, width=48, height=10, wrap='word', spacing1=10)
        text_box.pack()
        text_box.insert(ttk.END, 'INFORMĀCIJA\n', ('important'))
        text_box.tag_configure('important', foreground='#eb6234', justify='center', font=(controller.default_font_name, 11, 'bold'))
        text_box.insert(ttk.END, text_info)

        text_box.config(state='disabled', cursor='arrow', highlightthickness=0, borderwidth=0, takefocus=0)  # Make the Text widget read-only, disable text selection, set background, and remove border
        text_box.bind("<1>", lambda e: "break")  # Disable text selection by blocking mouse clicks

        self.before()
    
    def before(self):
        self.left_frame.pack_forget()
        self.left_frame_logout.pack_forget()

        if self.platform.is_authenticated:
            self.left_frame_logout.pack(side='left', fill='none', padx=10, pady=(10,90), expand=True)
        else:
            self.left_frame.pack(side='left', fill='none', padx=10, pady=(10,130), expand=True)
        
    def after(self):
        pass

    def is_locked(self):
        return self.lock

    def lock_frame(self):
        self.lock = True        
        self.login_button.config(state='disabled')
        self.controller.update_menu_states(ttk.DISABLED)

    def unlock_frame(self):
        self.lock = False        
        self.login_button.config(state='normal')
        self.controller.update_menu_states(ttk.NORMAL)

    def auth_login(self, event=None):
        login = self.login.get().strip()
        password = self.password.get().strip()

        auth_error_msg = 'Nepareizi ievadīts lietotājvārds un/vai parole.'

        personal_code_pattern = r'\d{6}-\d{5}' # Latvian personal code pattern
        username_pattern = r'[A-Za-z0-9_.@-]{3,}' # General username pattern

        is_personal_code = re.fullmatch(personal_code_pattern, login) is not None
        is_username = re.fullmatch(username_pattern, login) is not None

        if login and password and (is_personal_code or is_username):
            self.platform.set_login(login)
            self.platform.set_password(password)

            self.lock_frame()

            if self.platform.auth_login(False): # Auth?
                if self.platform.req_school_id(False): # School ID?
                    if self.platform.get_user_admin():

                        if not self.platform.req_classes_idx(json_save=False):
                            auth_error_msg = 'Nav pieejas klases datiem.'
                            # print('class_data error')
                        else:
                            # print(self.platform.get_classes_available())

                            self.login.set('')
                            self.password.set('')
                            self.unlock_frame()

                            self.controller.show_frame_name('EKlaseGetData')
                            # self.controller.show_frame_name('StartPage')
                                
                            return True

                    else:
                        auth_error_msg = 'Tev nav piešķirtas tiesības lejupielādēt datus.'
                        # print('user_type error')
                else:
                    auth_error_msg = 'Nav iespējams lejupielādēt skolas identifikatoru.'
                    # print('reqSchoolID error')
            else:
                # print('Auth error')
                pass

            self.unlock_frame()
        
        # Auth error
        self.platform.set_login('')
        self.platform.set_password('')
        self.platform.set_user_name('')

        self.controller.message_box(
            title = 'Autorizācijas kļūda', 
            message = auth_error_msg
        )
        return False

    def auth_logout(self):
        self.platform.auth_logout()
        self.left_frame_logout.pack_forget()        
        self.left_frame.pack(side='left', fill='none', padx=10, pady=(10,130), expand=True)
        self.controller.bottom_bar()