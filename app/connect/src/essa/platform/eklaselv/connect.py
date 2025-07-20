'''
ESSA Connect :: Electronic Grade Book Assistant Connector
Copyright (C) 2025 Mariusz Duka
This file is part of ESSA and is licensed under the GNU GPLv3 or later.
See the LICENSE file for full text.
'''

import os
import sys
import shutil
import json
import re
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from time import sleep

# encrypt SQLite3
try:
    from sqlcipher3 import dbapi2 as sqlite3
except ModuleNotFoundError as err:
    import sqlite3

# import request module
try:
    import requests
except ModuleNotFoundError as err:
    print(err)
    sys.exit(0)

# import tqdm module
try:
    from tqdm import tqdm
except ModuleNotFoundError as err:
    print(err)
    sys.exit(0)

class Connect:
    def __init__(self, login='', password='', date=''):
        self.driver_name = 'eklaselv'
        self.driver_description = 'E-klase.lv :: Latvian electronic school management platform'

        self.login = login
        self.password = password

        self.tenant_id = ''
        self.study_year_id = ''
        self.study_year_start_date = ''
        self.study_year_end_date = ''
        self.current_semester_from = ''
        self.current_semester_to = ''

        self.user_name = ''
        self.user_admin = False
        self.user_permissions = {}
        self.user_context = {}

        self.date = date if date != '' else self.get_next_monday()

        self.url_login = ''
        self.url_api_user = ''
        self.url_api_classes = ''
        self.url_api_get_week = ''
        self.url_api_disciplines = ''
        self.url_api_journal = ''

        self.classes = {}
        self.classes_diary_planner = {}
        self.classes_available = []

        self.save_dir = ''        
        self.data_dir = self.save_dir + '/' + self.driver_name
        self.config_file = self.data_dir + '/' + self.driver_name + '.conf'

        self.timetable_data_dir = self.data_dir  + '/timetable/'
        self.journal_data_dir = self.data_dir  + '/journal/'
        
        self.db_dir = self.data_dir + '/db/'
        self.db_timetable_file_name = 'timetable.db'
        self.db_journal_file_name = 'journal.db'
        self.db_default_timetable_file = 'timetable.db.default'
        self.db_default_journal_file = 'journal.db.default'

        self.db_encrypt = False
        self.db_decrypted = None
        self.db_cipher_compatibility = None
        self.db_password = None

        self.sleep_time = 1
        self.data_cache = False

        self.req = requests.Session()
        self.req_user_agent = 'ESSA'
        self.req.headers.update({'User-Agent': self.req_user_agent})
        self.is_authenticated = False
        self.req_in_progress = False

    def get_driver_name(self):
        return self.driver_name

    def get_driver_description(self):
        return self.driver_description

    def get_next_monday(self, date_format='%Y-%m-%d', fix_today=True):
        today = datetime.today()
        if fix_today and today.weekday() == 0:
            return today.strftime(date_format)
        else:
            nextmonday = today + timedelta(7-today.weekday())
            return nextmonday.strftime(date_format)

    def set_login(self, login):
        self.login = login

    def set_password(self, password):
        self.password = password

    def set_user_name(self, user_name):
        self.user_name = user_name

    def get_user_name(self):
        return self.user_name

    def set_user_admin(self, user_admin):
        self.user_admin = user_admin

    def get_user_admin(self):
        return self.user_admin

    def set_user_permissions(self, user_permissions):
        self.user_permissions = user_permissions

    def get_user_permissions(self):
        return self.user_permissions

    def set_save_dir(self, save_dir):
        self.save_dir = save_dir
        self.data_dir = self.save_dir + '/' + self.driver_name
        self.db_dir = self.data_dir + '/db/'
        self.config_file = self.data_dir + '/' + self.driver_name + '.conf'
        self.timetable_data_dir = self.data_dir + '/timetable/'
        self.journal_data_dir = self.data_dir + '/journal/'
        self.db_timetable_file_name = 'timetable.db'
        self.db_journal_file_name = 'journal.db'
        self.db_default_timetable_file = 'timetable.dbc.default' if self.db_encrypt else 'timetable.db.default'
        self.db_default_journal_file = 'journal.dbc.default' if self.db_encrypt else 'journal.db.default'

    def check_save_dir(self):
        folders = (self.data_dir, self.db_dir, self.journal_data_dir, self.timetable_data_dir)
        for folder in folders:
            if not os.path.exists(folder):
                os.makedirs(folder)

    def set_url_login(self, url_login):
        self.url_login = url_login

    def set_url_api_user(self, url_api_user):
        self.url_api_user = url_api_user

    def set_url_api_classes(self, url_api_classes):
        self.url_api_classes = url_api_classes

    def set_url_api_get_week(self, url_api_get_week):
        self.url_api_get_week = url_api_get_week

    def set_url_api_disciplines(self, url_api_disciplines):
        self.url_api_disciplines = url_api_disciplines

    def set_url_api_journal(self, url_api_journal):
        self.url_api_journal = url_api_journal

    def set_date(self, date):
        self.date = date

    def set_tenant_id(self, tenant_id):
        self.tenant_id = tenant_id

    def get_tenant_id(self):
        return self.tenant_id

    def set_study_year_id(self, study_year_id):
        self.study_year_id = study_year_id

    def set_study_year_start_date(self, study_year_start_date):
        self.study_year_start_date = study_year_start_date

    def set_study_year_end_date(self, study_year_end_date):
        self.study_year_end_date = study_year_end_date

    def set_current_semester_from(self, current_semester_from):
        self.current_semester_from = current_semester_from

    def set_current_semester_to(self, current_semester_to):
        self.current_semester_to = current_semester_to

    def set_default_urls(self):
        self.set_url_login('https://my.e-klase.lv/?v=15')
        self.set_url_api_user('https://my.e-klase.lv/api/user-context')
        self.set_url_api_classes('https://my.e-klase.lv/api/classes/items/of-user?tenantId={}&studyYearId={}')
        self.set_url_api_get_week('https://my.e-klase.lv/DiaryPlanner/GetWeek/OfClass/{}/{}')
        self.set_url_api_disciplines('https://my.e-klase.lv/api/class-journals/of-class/items/{}')
        self.set_url_api_journal('https://my.e-klase.lv/api/journal-lesson/items/all?classId={}&disciplineId={}&groupIndex={}&joinedGroupId=0&tenantId={}&studyYearId={}&dateFrom={}&dateTo={}&sortByClass=false&activeStudentsInJournal=true&onlyMyRecords=false&loadLessonsWithEvaluationsWeight=false&loadLessonsWithEvaluations=false&loadLessonsWithNonAttendances=false&loadDrafts=true&deleted=false&loadAllRecords=true')

    def set_sleep_time(self, sleep_time):
        if not isinstance(sleep_time, (int, float)):
            sleep_time = 1
        if sleep_time < 0.5:
            sleep_time = 0.5
        # print('Sleep time set to:', sleep_time, 'seconds')
        self.sleep_time = sleep_time

    def get_sleep_time(self):
        return self.sleep_time

    def get_data_cache(self):
        return self.data_cache

    def set_is_authenticated(self, is_authenticated):
        self.is_authenticated = is_authenticated

    def get_is_authenticated(self):
        return self.is_authenticated

    def set_req_in_progress(self, req_in_progress):
        self.req_in_progress = req_in_progress

    def get_req_in_progress(self):
        return self.req_in_progress

    def set_req_user_agent(self, req_user_agent):
        self.req.headers.update({'User-Agent': req_user_agent})

    def set_classes_available(self, classes_available):
        self.classes_available = classes_available

    def get_classes_available(self):
        return self.classes_available

    def set_db_timetable_file_name(self, db_timetable_file_name):
        self.db_timetable_file_name = db_timetable_file_name

    def get_timetable_file_name(self):
        return self.db_timetable_file_name

    def set_db_journal_file_name(self, db_journal_file_name):
        self.db_journal_file_name = db_journal_file_name

    def db_journal_file_name(self):
        return self.db_journal_file_name

    def set_db_encrypt(self, db_encrypt):
        self.db_encrypt = db_encrypt

    def get_db_encrypt(self):
        return self.db_encrypt

    def set_db_decrypted(self, db_decrypted):
        self.db_encrypted = db_decrypted

    def get_db_decrypted(self):
        return self.db_decrypted

    def set_db_cipher_compatibility(self, db_cipher_compatibility):
        self.db_cipher_compatibility = db_cipher_compatibility

    def get_db_cipher_compatibility(self):
        return self.db_cipher_compatibility

    def set_db_password(self, db_password):
        self.db_password = db_password

    def get_db_password(self):
        return self.db_password

    '''
    Authorization to the platform    
    '''
    def auth_complex(self, show_info=True):
        if not self.is_authenticated: # is logged?
            if self.auth_login(show_info): # is logged as admin's permissions?
                # print(self.get_user_permissions())
                return True
            else:
                # print('auth_login error')
                return False
        else:
            return True

    '''
    Login to the platform
    '''
    def auth_login(self, show_info=True):

        if self.url_login == '':
            # print('settings error (loginToPlatform)')
            return False

        if self.login == '' or self.password == '':
            print('Login to e-klase.lv:')
            self.login = input('Username: ')
            self.password = input('Password: ')

            if self.login == '' or self.password == '':
                print('The username and password are incomplete, please re-enter them.')
                return False

            login_format = r'^\d{6}-\d{5}$'
            if not re.match(login_format, self.login):
                print('The username is invalid. The correct format is XXXXXX-XXXXX.')
                return False

        payload = {
            'UserName': self.login,
            'Password': self.password
        }

        if show_info:
            print('Date:', self.date)

        self.set_is_authenticated(False)
        
        try:
            response = self.req.post(self.url_login, data=payload)
        
            # print(response.headers)
            # print(response.text)
            # sys.exit()

            if response.status_code == 200:

                soup = BeautifulSoup(response.text, 'html.parser')

                # check if login correct
                if soup.find_all(class_='validation-summary-errors'):
                    print('[!] E-Klase => Incorrect login or password.')
                    return False

                # check if two factor auth
                if soup.find_all(id='two-factor-auth-app'):
                    print('[!] E-Klase => You must have a Latvian IP number.')
                    return False

                # check data school and user's permissions
                if self.req_school_id(show_info):
                    if self.get_user_admin():
                        self.set_is_authenticated(True)
                        return True
                    else:
                        # print('get_user_admin error')
                        return False
                else:
                    # print('req_school_id error')
                    return False
            else:
                return False
        except:
            return False        

    '''
    Logout from the platform
    '''
    def auth_logout(self):
        self.req.close()
        self.set_is_authenticated(False)
        return True

    '''
    Check data school and user's permissions
    '''
    def req_school_id(self, show_info=True):
        if self.url_api_user == '':
            # print('settings error (reqSchoolID)')
            return False

        try:
            response = self.req.get(self.url_api_user)

            if response.status_code == 200:
                r_json = response.json()
                self.user_context = r_json['userContext']

                tenant_id = self.user_context['school']['tenantId']
                study_year_id = self.user_context['studyYear']['id']
                study_year_start_date = self.user_context['studyYear']['startDate']
                study_year_end_date = self.user_context['studyYear']['endDate']
                current_semester_from = self.user_context['studyYear']['currentSemester']['from']
                current_semester_to = self.user_context['studyYear']['currentSemester']['to']
                user_name = self.user_context['user']['firstName'] + ' ' + self.user_context['user']['lastName']
                user_permissions = self.user_context['user']['permissions']
                
                user_admin = False
                if user_permissions['hasPermissionsToAllIndividualJournals']:
                    user_admin = True
                    # print('Admin')

                self.set_tenant_id(tenant_id)
                self.set_study_year_id(study_year_id)            
                self.set_study_year_start_date(study_year_start_date)
                self.set_study_year_end_date(study_year_end_date)            
                self.set_current_semester_from(current_semester_from)
                self.set_current_semester_to(current_semester_to)         
                self.set_user_name(user_name)
                self.set_user_admin(user_admin)
                self.set_user_permissions(user_permissions)

                if show_info:
                    print('SCHOOL ID:', tenant_id, '[', study_year_id, ']')

                return True
            else:
                return False
        except:
            return False

    '''
    Check the possibility to download data
    '''
    def req_classes_idx(self, json_save=False):
        if not self.is_authenticated:
            print('No user authorization in the system.')
            return False

        if self.url_api_classes == '' or self.tenant_id == '' or self.study_year_id == '' or self.url_api_get_week == '' or self.url_api_disciplines == '':
            # print('settings error (req_classes_idx)')
            return False

        try:
            url = self.url_api_classes.format(self.tenant_id, self.study_year_id)
            response = self.req.get(url)      

            if response.status_code == 200:

                if json_save:
                    f = open(self.data_dir + '/classes.json', 'w', encoding='utf-8')
                    f.write(response.text)
                    f.close()         

                classes_available = []

                r_json = response.json()
                for c in r_json['allActive']:

                    class_id = str(c['id'])
                    class_name = str(c['name'])

                    classes_available.append(class_name)

                    self.classes[class_name] = {}
                    self.classes[class_name]['id'] = class_id
                    self.classes[class_name]['name'] = class_name
                    self.classes[class_name]['url'] = {}
                    self.classes[class_name]['url']['lessons'] = ''
                    self.classes[class_name]['url']['disciplines'] = self.url_api_disciplines.format(class_id)
                    self.classes[class_name]['json'] = {}
                    self.classes[class_name]['json']['lessons'] = ''
                    self.classes[class_name]['json']['disciplines'] = ''
                    self.classes[class_name]['json']['journals'] = {}

                self.set_classes_available(classes_available)
                return classes_available

            else:
                return False
        except:
            return False

    '''
    Download JSON classes's data
    '''
    def req_classes_data(self, req_classes=[], progress_bar=None, json_save=False, show_info=True):
        if not self.is_authenticated:
            print('No user authorization in the system.')
            return False

        cnt_classes = len(self.classes)
        cnt_req_classes = len(req_classes)

        if cnt_classes == 0 or cnt_req_classes == 0:
            return False

        # create directory if needed
        if json_save and not os.path.isdir(self.timetable_data_dir):
            os.makedirs(self.timetable_data_dir, exist_ok=True)       
        
        # req data
        self.set_req_in_progress(True)
            
        if progress_bar is not None:
            pbar = req_classes
        else:
            pbar = tqdm(req_classes)

        try:
            for idx, i in enumerate(pbar):

                class_name = str(i)

                # req only selected classes or all
                if class_name not in self.classes:
                    # print(class_name)
                    continue

                url = self.url_api_get_week.format(self.classes[class_name]['id'], self.date)
                if url == '':
                    continue

                response = self.req.get(url)
                
                if response.status_code == 200:

                    self.classes[class_name]['json']['lessons'] = response.text

                    if json_save:
                        f = open(self.timetable_data_dir + '/' + class_name.lower() + '_class.json', 'w', encoding='utf-8')
                        f.write(response.text)
                        f.close()

                if show_info:
                    pbar.set_description('Download (classes) [%s]' % class_name)
                    pbar.set_postfix()

                if progress_bar is not None:
                    progress_bar.set(int((idx/cnt_req_classes)*100))

                sleep(self.sleep_time)
        except:
            self.set_req_in_progress(False)
            return False

        if progress_bar is not None:
            progress_bar.set(100)

        self.set_req_in_progress(False)
        return True

    '''
    Save JSON classes data to SQLite database
    '''
    def sqlite_classes_data(self, req_classes=[], db_update=True, db_file_archive=False, show_info=True):
        
        if len(req_classes) == 0 or len(self.classes) == 0:
            return False
        
        try:
            db_file_name = self.db_dir + self.db_timetable_file_name
            db_file_name_date = self.db_dir + 'timetable_' + datetime.today().strftime('%Y%m%d_%H%M%S') + '.db'
            db_default_name = self.db_dir + self.db_default_timetable_file

            # create directory if needed
            if not os.path.exists(db_file_name):
                # print(db_default_name, db_file_name)
                shutil.copyfile(db_default_name, db_file_name)

            if db_file_archive:
                shutil.copyfile(db_file_name, db_file_name_date)

            with sqlite3.connect(db_file_name) as conn:                
                cur = conn.cursor()

                if self.db_encrypt:
                    if not self.set_db_pragma(conn):
                        return False

                # clear db
                if not db_update:
                    cur.execute('DELETE FROM class;')
                    cur.execute('DELETE FROM lesson;')
                    conn.commit()

                if show_info:
                    print('Adding data to the SQLite database...')
                    print('=>', db_file_name)

                for req_class in req_classes:

                    if self.classes[req_class]['json']['lessons'] == '':
                        continue

                    try:
                        data = json.loads(self.classes[req_class]['json']['lessons'])
                    except:
                        return False

                    # class
                    if db_update:
                        cur.execute('SELECT COUNT() FROM class WHERE id=?', [data['ClassId']])
                        numberOfRows = int(cur.fetchone()[0])
                        if numberOfRows > 0:
                            cur.execute('DELETE FROM class WHERE id=?', [data['ClassId']])
                            cur.execute('DELETE FROM lesson WHERE class_id=?', [data['ClassId']])
                            conn.commit()

                    cur.execute('INSERT OR IGNORE INTO class (id, name, period, study_year_start_date, study_year_end_date, week_start_date, week_end_date) VALUES (?,?,?,?,?,?,?);', 
                    [data['ClassId'], str(req_class), data['Period'], data['StudyYearStartDate'], data['StudyYearEndDate'], data['WeekStartDate'], data['WeekEndDate']])

                    # lesson
                    for day in data['Days']:

                        date = day['Date']

                        for lesson in day['Lessons']:
                            for discipline in lesson['LessonDisciplines']:

                                d_name = discipline['Name'].lower()
                                l_type = 1 # 'S'
                                if '(f)' in d_name:
                                    l_type = 2 # 'F'
                                elif '(i)' in d_name:
                                    l_type = 3 # 'I'
                                elif '(p)' in d_name:
                                    l_type = 4 # 'P'

                                # lesson
                                cur.execute('INSERT OR IGNORE INTO lesson (date, number, type, group_index, class_id, discipline_id, diary_id, day_index, only_this_week, is_active, name, room, teachers, author) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?);', 
                                            [day['Date'], discipline['LessonNumber'], l_type, discipline['GroupIndex'], data['ClassId'], discipline['Id'], discipline['DiaryId'], discipline['DayIndex'], discipline['OnlyThisWeek'], discipline['IsActive'], discipline['Name'], discipline['Room'], discipline['Teachers'], discipline['Author']])

                    conn.commit()

                cur.execute('VACUUM;')
                cur.close()

            conn.close()
            return True

        except sqlite3.Error as e:
            print(e)

        return False

    '''
    Download JSON journal's data
    '''
    def req_journals_data(self, req_journals=[], progress_bar=None, json_save=False, show_info=True):

        if not self.is_authenticated:
            print('No user authorization in the system.')
            return False

        if self.url_api_classes == '' or self.tenant_id == '' or self.study_year_id == '' or self.url_api_disciplines == '' or self.url_api_journal == '':
            # print('settings error (req_journals_data)')
            return False

        cnt_classes = len(self.classes)
        cnt_req_journals = len(req_journals)

        if cnt_classes == 0 or cnt_req_journals == 0:
            return False

        # create directory if needed
        if json_save and not os.path.isdir(self.journal_data_dir):
            os.makedirs(self.journal_data_dir, exist_ok=True)

        # req data
        self.set_req_in_progress(True)
            
        if progress_bar is not None:
            pbar = req_journals
        else:
            pbar = tqdm(req_journals)

        # print(pbar)

        for idx, c in enumerate(pbar):
                
            class_name = str(c)
            class_id = self.classes[class_name]['id']

            # req only selected classes or all
            if class_name not in self.classes:
                # print(class_name)
                continue

            url = self.classes[class_name]['url']['disciplines']
            if url == '':
                continue

            response = self.req.get(url)
                
            if response.status_code == 200:                    

                self.classes[class_name]['json']['disciplines'] = response.text

                if json_save:
                    f = open(self.journal_data_dir + '/' + class_name.lower() + '_disciplines.json', 'w', encoding='utf-8')
                    f.write(response.text)
                    f.close()

                if show_info:
                    pbar.set_description('Download (journal) [%s]' % class_name)
                    pbar.set_postfix()
                    
                r2_json = response.json()
                cnt_disciplines = len(r2_json)

                sleep(self.sleep_time)
                    
                for idx2, d in enumerate(r2_json):
                    discipline_id = d['journalId']['disciplineId']
                    group_index = d['journalId']['groupIndex']

                    url = self.url_api_journal.format(class_id, discipline_id, group_index, self.tenant_id, self.study_year_id, self.current_semester_from, self.current_semester_to)
                    response = self.req.get(url)

                    if response.status_code == 200:

                        if discipline_id not in self.classes[class_name]['json']['journals']:
                            self.classes[class_name]['json']['journals'][discipline_id] = {}
                        self.classes[class_name]['json']['journals'][discipline_id][group_index] = response.text

                        if json_save:
                            f = open(self.journal_data_dir + '/' + class_name.lower() + '_journal_' + str(discipline_id) + '_' + str(group_index) + '.json', 'w', encoding='utf-8')
                            f.write(response.text)
                            f.close()

                        if progress_bar is not None:
                            perc_classes = idx/cnt_req_journals
                            perc_disciplines = idx2/cnt_disciplines/cnt_req_journals
                            perc_update = int((perc_classes+perc_disciplines)*100)
                            
                            progress_bar.set(perc_update)
                        else:
                            perc_classes = idx
                            perc_disciplines = idx2/cnt_disciplines
                            perc_update = round((perc_classes+perc_disciplines),2)
                            
                            pbar.n = perc_update
                            pbar.refresh()
                        
                        # print(idx, idx2, cnt_req_journals, cnt_disciplines, perc_update)

                        sleep(self.sleep_time)

                    else:
                        self.set_req_in_progress(False)
                        return False

            else:
                self.set_req_in_progress(False)
                return False

        # save self.classes to JSON file
        if json_save:
            f = open(self.journal_data_dir + '/' + 'classes.json', 'w', encoding='utf-8')
            f.write(json.dumps(self.classes, ensure_ascii=False, indent=4))
            f.close()

        if progress_bar is not None:
            progress_bar.set(100)

        self.set_req_in_progress(False)
        
        return True

    '''
    Save JSON journal's data to SQLite database
    '''
    def sqlite_journal_data(self, req_journals=[], db_update=True, db_file_archive=False, show_info=True, load_classes_from_json=False):

        if load_classes_from_json:
            if os.path.exists(self.journal_data_dir + '/classes.json'):
                with open(self.journal_data_dir + '/classes.json', 'r', encoding='utf-8') as f:
                    self.classes = json.load(f)

        if len(req_journals) == 0 or len(self.classes) == 0:
            return False

        try:
            db_file_name = self.db_dir + self.db_journal_file_name
            db_file_name_date = self.db_dir + 'journal_' + datetime.today().strftime('%Y%m%d_%H%M%S') + '.db'
            db_default_name = self.db_dir + self.db_default_journal_file

            # create directory if needed
            if not os.path.exists(db_file_name):
                # print(db_default_name, db_file_name)
                shutil.copyfile(db_default_name, db_file_name)

            if db_file_archive:
                shutil.copyfile(db_file_name, db_file_name_date)

            with sqlite3.connect(db_file_name) as conn:                
                cur = conn.cursor()

                if self.db_encrypt:
                    if not self.set_db_pragma(conn):
                        return False

                # clear db
                if not db_update:
                    cur.execute('DELETE FROM class;')
                    cur.execute('DELETE FROM discipline;')
                    cur.execute('DELETE FROM discipline_teacher;')
                    cur.execute('DELETE FROM evaluation;')
                    cur.execute('DELETE FROM lesson;')
                    cur.execute('DELETE FROM lesson_teacher;')
                    cur.execute('DELETE FROM pupil;')
                    cur.execute('DELETE FROM school;')
                    cur.execute('DELETE FROM teacher;')
                    conn.commit()

                if show_info:
                    print('Adding data to the SQLite database...')
                    print('=>', db_file_name)

                for req_journal in req_journals:

                    class_name = str(req_journal)
                    class_id = self.classes[class_name]['id']

                    # check if disciplines id downloaded
                    if self.classes[class_name]['json']['disciplines'] == '':
                        continue

                    # insert class id and name to DB
                    cur.execute('INSERT OR IGNORE INTO class (id, name) VALUES (?,?);', [class_id, class_name])
                        
                    # disciplines
                    disciplines = json.loads(self.classes[class_name]['json']['disciplines'])

                    # print('disciplines', len(disciplines))

                    for dp in disciplines:
                        
                        # print(dp)
                        
                        cur.execute('SELECT COUNT() FROM discipline WHERE id=? AND class_id=? AND group_index=?', [dp['journalId']['disciplineId'], dp['journalId']['classId'], dp['journalId']['groupIndex']])
                        numberOfRows = int(cur.fetchone()[0])
                        if numberOfRows == 0:

                            discipline_type = 'S'
                            if '(I)' in dp['disciplineName']:
                                discipline_type = 'I'
                            if '(F)' in dp['disciplineName']:
                                discipline_type = 'F'

                            cur.execute('INSERT INTO discipline (id, name, type, class_id, class_name, group_index) VALUES (?,?,?,?,?,?);', 
                                        [dp['journalId']['disciplineId'], dp['disciplineName'], discipline_type, dp['journalId']['classId'], dp['className'], dp['journalId']['groupIndex']])
                                
                        for t in dp['teachers']:
                            cur.execute('INSERT OR IGNORE INTO teacher (id, first_name, last_name) VALUES (?,?,?);', [t['id'], t['firstName'], t['lastName']])

                            cur.execute('SELECT COUNT() FROM discipline_teacher WHERE discipline_id=? AND group_index=? AND teacher_id=?', [dp['journalId']['disciplineId'], dp['journalId']['groupIndex'], t['id']])
                            numberOfRows = int(cur.fetchone()[0])
                            if numberOfRows == 0:
                                cur.execute('INSERT INTO discipline_teacher (discipline_id, group_index, teacher_id) VALUES (?,?,?);', [dp['journalId']['disciplineId'], dp['journalId']['groupIndex'], t['id']])

                        # journals
                        journals = self.classes[class_name]['json']['journals'][str(dp['journalId']['disciplineId']) if load_classes_from_json else dp['journalId']['disciplineId']]
                        # print('journals:', len(journals))

                        for journal in journals:
                            
                            journal = json.loads(journals[journal])
                            # print(journal)
                                                       
                            for lesson in journal['lessons']:
                                # print(lesson)
                                if (lesson['subject']['textValue'] == None):
                                    lesson['subject']['textValue'] = ''
                                if (lesson['homeTask'] == None):
                                    lesson['homeTask'] = {}
                                    lesson['homeTask']['date'] = ''
                                    lesson['homeTask']['textWithAttachments'] = {}
                                    lesson['homeTask']['textWithAttachments']['textValue'] = ''
                                if lesson['evaluationWeight'] == None:
                                    lesson['evaluationWeight'] = 0
                                            
                                cur.execute('SELECT COUNT() FROM lesson WHERE id=?', [lesson['id']])
                                numberOfRows = int(cur.fetchone()[0])
                                if numberOfRows == 0:
                                    cur.execute('INSERT OR IGNORE INTO lesson (id, group_index, date, type_id, type_name, metholodogy, evaluation_system_type, evaluation_weight, subject, home_task_date, home_task_subject, discipline_id, class_id) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?);', 
                                                [lesson['id'], lesson['journalId']['groupIndex'], lesson['date'], lesson['lessonType']['id'], lesson['lessonType']['name'], lesson['metholodogy'], lesson['evaluationSystemType'], lesson['evaluationWeight'], lesson['subject']['textValue'], lesson['homeTask']['date'], lesson['homeTask']['textWithAttachments']['textValue'], dp['journalId']['disciplineId'], class_id])
                                else:
                                    cur.execute('UPDATE lesson SET group_index=?, date=?, type_id=?, type_name=?, metholodogy=?, evaluation_system_type=?, evaluation_weight=?, subject=?, home_task_date=?, home_task_subject=?, discipline_id=?, class_id=? WHERE id=?;', 
                                                [lesson['journalId']['groupIndex'], lesson['date'], lesson['lessonType']['id'], lesson['lessonType']['name'], lesson['metholodogy'], lesson['evaluationSystemType'], lesson['evaluationWeight'], lesson['subject']['textValue'], lesson['homeTask']['date'], lesson['homeTask']['textWithAttachments']['textValue'], dp['journalId']['disciplineId'], class_id, lesson['id']])

                                for t in lesson['teachers']:
                                    cur.execute('INSERT OR IGNORE INTO teacher (id, first_name, last_name) VALUES (?,?,?);', [t['id'], t['firstName'], t['lastName']])
                                                
                                    cur.execute('SELECT COUNT() FROM lesson_teacher WHERE lesson_id=? AND teacher_id=?', [lesson['id'], t['id']])
                                    numberOfRows = int(cur.fetchone()[0])
                                    if numberOfRows == 0:
                                        cur.execute('INSERT INTO lesson_teacher (lesson_id, teacher_id) VALUES (?,?);', [lesson['id'], t['id']])

                            for pupil in journal['pupils']:
                                # print(pupil)
                                cur.execute('INSERT OR IGNORE INTO pupil (id, first_name, last_name, class_id, class_name) VALUES (?,?,?,?,?);', 
                                            [pupil['personalFileId'], pupil['firstName'], pupil['lastName'], pupil['classId'], pupil['className']])

                                # insert or update evaluation
                                for pupil_lesson in pupil['lessons']:
                                    if pupil_lesson['evaluation'] is None:
                                        pupil_lesson['evaluation'] = {}
                                        pupil_lesson['evaluation']['value'] = ''
                                    cur.execute('SELECT COUNT() FROM evaluation WHERE lesson_id=? AND pupil_id=?', [pupil_lesson['lessonId'], pupil['personalFileId']])
                                    numberOfRows = int(cur.fetchone()[0])
                                    if numberOfRows == 0:
                                        cur.execute('INSERT INTO evaluation (lesson_id, pupil_id, value) VALUES (?,?,?);', 
                                                    [pupil_lesson['lessonId'], pupil['personalFileId'], pupil_lesson['evaluation']['value']])
                                    else:
                                        cur.execute('UPDATE evaluation SET value=? WHERE lesson_id=? AND pupil_id=?;', 
                                                    [pupil_lesson['evaluation']['value'], pupil_lesson['lessonId'], pupil['personalFileId']])
                            
                            conn.commit()
                
                conn.commit()
                cur.execute('VACUUM;')
                cur.close()

            conn.close()
        except sqlite3.Error as e:
            print(e)

    '''
    SQL get struct data
    '''
    def get_db_classes_names(self):
        records = []

        db_file_name = self.db_dir + self.db_timetable_file_name
        if db_file_name == '' or not os.path.exists(db_file_name):
            return records
    
        try:
            with sqlite3.connect(db_file_name) as conn:                
                cur = conn.cursor()

                if self.db_encrypt:
                    if not self.set_db_pragma(conn):
                        return False

                sql_query = """SELECT DISTINCT name FROM "main"."class" LIMIT 49999 OFFSET 0;"""
                cur.execute(sql_query)
                rows = cur.fetchall()
                cur.close()

                for row in rows:
                    records.append(row[0])

        except sqlite3.Error as e:
            print(e)
            return False

        return records

    def get_db_classes_lessons(self, classes_custom=[], lesson_type=['S'], days = 5):

        db_file_name = self.db_dir + self.db_timetable_file_name
        if db_file_name == '' or not os.path.exists(db_file_name):
            return False

        lessons = {}
        records = []

        try:
            with sqlite3.connect(db_file_name) as conn:                
                cur = conn.cursor()

                if self.db_encrypt:
                    if not self.set_db_pragma(conn):
                        return False

                sql_query = """SELECT DISTINCT lesson_date, class_name, lesson_day_index, lesson_number, lesson_type, lesson_name, lesson_room, lesson_teachers FROM "main"."v_timetable_classes" LIMIT 49999 OFFSET 0;"""
                cur.execute(sql_query)
                records = cur.fetchall()
                cur.close()

        except sqlite3.Error as e:
            print(e)  
            return False

        for record in records:

            # 1 level - class
            if not record[1] in lessons.keys():
                lessons[record[1]] = {}

            # 2 level - day
            if not record[2] in lessons[record[1]].keys():
                lessons[record[1]][record[2]] = {}

            # 3 level - lesson
            if not record[3] in lessons[record[1]][record[2]].keys():
                lessons[record[1]][record[2]][record[3]] = []

            l_type = 'S'            
            if record[4] == 2:
                l_type = 'F'
            elif record[4] == 3:
                l_type = 'I'
            elif record[4] == 4:
                l_type = 'P'

            if l_type in lesson_type:
                lessons[record[1]][record[2]][record[3]].append({'name': record[5], 'room': record[6], 'teachers': record[7]})
            else:
                if len(lessons[record[1]][record[2]][record[3]]) == 0:
                    lessons[record[1]][record[2]][record[3]].append({'name': '--', 'room': '', 'teachers': ''})

        # print(lessons)
        return lessons

    def get_db_classes_rooms(self, classes_custom=[], lesson_type=['S'], days = 5):

        db_file_name = self.db_dir + self.db_timetable_file_name
        if db_file_name == '' or not os.path.exists(db_file_name):
            return False

        rooms = {}
        records = []

        try:
            with sqlite3.connect(db_file_name) as conn:                
                cur = conn.cursor()

                if self.db_encrypt:
                    if not self.set_db_pragma(conn):
                        return False

                sql_query = """SELECT DISTINCT lesson_room, lesson_day_index, lesson_number, lesson_type, class_name, lesson_name  FROM "main"."v_timetable_rooms" LIMIT 49999 OFFSET 0;"""
                cur.execute(sql_query)
                records = cur.fetchall()
                cur.close()

        except sqlite3.Error as e:
            print(e)  
            return False

        for record in records:

            l_type = 'S'            
            if record[3] == 2:
                l_type = 'F'
            elif record[3] == 3:
                l_type = 'I'
            elif record[3] == 4:
                l_type = 'P'

            if l_type in lesson_type and record[4] in classes_custom and record[1] <= days:

                # room
                if record[0] not in rooms:
                    rooms[record[0]] = {}

                # day
                if record[1] not in rooms[record[0]]:
                    rooms[record[0]][record[1]] = {}

                # lesson
                if record[2] not in rooms[record[0]][record[1]]:
                    rooms[record[0]][record[1]][record[2]] = []

                rooms[record[0]][record[1]][record[2]].append((record[4], record[5]))

        # print(rooms)
        return rooms

    def set_db_pragma(self, conn):
        pragma_key = "PRAGMA key='{}'".format(self.db_password)
        pragma_cipher = "PRAGMA cipher_compatibility = {}".format(self.db_cipher_compatibility)

        '''
        print(pragma_key)
        print(pragma_cipher)
        '''
        
        conn.execute(pragma_key)
        conn.execute(pragma_cipher)
        try:
            conn.execute("SELECT count(*) FROM sqlite_master;")
            # print("Database decrypted successfully!")
            self.db_decrypted = True
            return True
        except sqlite3.DatabaseError as e:
            print(f"Failed to decrypt database: {e}")
            conn.close()
            self.db_decrypted = False
            return False

    '''
    Remove all JSON downloaded files
    '''
    def remove_json_files(self):
        # timetable
        if os.path.isdir(self.timetable_data_dir):
            for file_name in os.listdir(self.timetable_data_dir):
                if file_name.endswith('_class.json'):
                    # print(self.data_dir + '/' + file_name)
                    os.remove(self.timetable_data_dir + '/' + file_name)
            if os.path.exists(self.config_file):
                # print(self.config_file)
                os.remove(self.config_file)

        # journal
        if os.path.isdir(self.journal_data_dir):
            for file_name in os.listdir(self.journal_data_dir):
                if file_name.endswith('.json'):
                    os.remove(self.journal_data_dir + '/' + file_name)