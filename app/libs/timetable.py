'''
ESSA :: Electronic Grade Book Assistant
Copyright (C) 2025 Mariusz Duka
This file is part of ESSA and is licensed under the GNU GPLv3 or later.
See the LICENSE file for full text.
'''

import os
import json
import xlsxwriter
from datetime import datetime

class TimeTable:
    def __init__(self, classes={}, rooms={}):

        self.workbook = None
        self.worksheet = None

        self.classes = classes
        self.for_classes = []
        self.rooms = rooms
        self.for_rooms = []
        self.for_days = 6

        self.title_line_1 = ''
        self.title_line_2 = ''
        self.day_name = []
        self.hours = []
        self.teachers = {}
                
        self.optimize_teacher_name = False

        self.optimize_lesson_name = False
        self.optimize_lesson_name_data = []

        self.replace_text = False
        self.replace_text_data = []

        self.fix_weeks_ab = False
        self.fix_weeks_ab_data = []

        self.save_dir = ''
        self.excel_file_dir = ''
        self.excel_file_name = 'TimeTable'
        self.excel_file_name_rooms = 'TimeTableRooms'
        self.excel_file_name_ext = 'xlsx'
        self.excel_file_name_date = False
        self.excel_full_file_name = ''
        self.excel_worksheet_name = ''
        self.font_1_name = 'Arial Narrow'
        self.font_1_size = 11
        self.default_rows_height = 18

        self.translate_data = {}

    def set_for_classes(self, for_classes):
        self.for_classes = for_classes

    def set_for_rooms(self, for_rooms):
        self.for_rooms = for_rooms

    def set_for_days(self, for_days):
        self.for_days = for_days

    def set_title_line1(self, title_line_1):
        self.title_line_1 = title_line_1

    def set_title_line2(self, title_line_2):
        self.title_line_2 = title_line_2

    def set_day_name(self, day_name):
        self.day_name = day_name

    def set_hours(self, hours):
        self.hours = hours

    def set_teachers(self, teachers):
        self.teachers = teachers

    def set_optimize_teacher_name(self, optimize_teacher_name):
        self.optimize_teacher_name = optimize_teacher_name

    def set_optimize_lesson_name(self, optimize_lesson_name):
        self.optimize_lesson_name = optimize_lesson_name

    def set_optimize_lesson_name_data(self, optimize_lesson_name_data):
        self.optimize_lesson_name_data = optimize_lesson_name_data

    def set_replace_text(self, replace_text):
        self.replace_text = replace_text

    def set_replace_text_data(self, replace_text_data):
        self.replace_text_data = replace_text_data

    def set_fix_weeks_ab(self, fix_weeks_ab):
        self.fix_weeks_ab = fix_weeks_ab

    def set_fix_weeks_ab_data(self, fix_weeks_ab_data):
        self.fix_weeks_ab_data = fix_weeks_ab_data

    def set_save_dir(self, save_dir):
        self.save_dir = save_dir

    def set_excel_file_dir(self, excel_file_dir):
        self.excel_file_dir = excel_file_dir

    def set_excel_file_name(self, excel_file_name):
        self.excel_file_name = excel_file_name

    def set_excel_file_name_rooms(self, excel_file_name_rooms):
        self.excel_file_name_rooms = excel_file_name_rooms

    def set_excel_file_name_ext(self, excel_file_name_ext):
        self.excel_file_name_ext = excel_file_name_ext

    def set_excel_file_name_date(self, excel_file_name_date):
        self.excel_file_name_date = excel_file_name_date

    def set_excel_full_file_name(self, excel_full_file_name):
        self.excel_full_file_name = excel_full_file_name

    def get_excel_full_file_name(self):
        return self.excel_full_file_name

    def set_excel_worksheet_name(self, excel_worksheet_name):
        self.excel_worksheet_name = excel_worksheet_name

    def set_font1_name(self, font_1_name):
        self.font_1_name = font_1_name

    def set_font1_size(self, font_1_size):
        self.font_1_size = font_1_size

    def set_rows_height(self, default_rows_height):
        self.default_rows_height = default_rows_height

    def set_translate_data(self, translate_data):
        self.translate_data = translate_data

    def set_config(self, config):
        teachers = {}
        for cl, teacher in config['TimeTable.Teachers'].items():
            teachers[cl] = tuple(teacher.split(','))
        # print(teachers)

        day_name = []
        for _, day in config['TimeTable.Days'].items():
            day_name.append(day)
        # print(day_name)

        hours = []
        for _, hour in config['TimeTable.Hours'].items():
            hours.append(hour)
        # print(hours)

        optimize_lessonname_data = []
        try:
            for _, optimize in config['TimeTable.Optimize.LessonName'].items():
                optimize_lessonname_data.append(json.loads(optimize))
        except:
            optimize_lessonname_data = []
        # print(optimize_lessonname_data)

        replace_text = []
        try:
            for _, text in config['TimeTable.Optimize.ReplaceText'].items():
                replace_text.append(tuple(text.split(',')))
        except:
            replace_text = []
        # print(ReplaceTextData)

        fix_weeks_ab_data = []
        try:
            for _, f in config['TimeTable.Optimize.FixWeeksAB'].items():
                el = f.split('|')
                el1 = el[0].split(',')
                el2 = json.loads(el[1])
                el3 = json.loads(el[2])
                item = (el1, el2, el3)
                fix_weeks_ab_data.append(tuple(item))
        except:
            fix_weeks_ab_data = []
        # print(fix_weeks_ab_data)

        self.set_for_classes(config['TimeTable']['Classes'].split(','))
        self.set_for_days(config['TimeTable'].getint('Days'))
        self.set_title_line1(config['TimeTable']['TitleLine1'])
        self.set_title_line2(config['TimeTable']['TitleLine2'])

        self.set_teachers(teachers)
        self.set_day_name(tuple(day_name))
        self.set_hours(tuple(hours))
        
        self.set_optimize_teacher_name(config['TimeTable.Optimize'].getboolean('TeacherName'))

        self.set_optimize_lesson_name(config['TimeTable.Optimize'].getboolean('LessonName'))
        self.set_optimize_lesson_name_data(optimize_lessonname_data)
        
        self.set_replace_text(config['TimeTable.Optimize'].getboolean('ReplaceText'))
        self.set_replace_text_data(replace_text)
        
        self.set_fix_weeks_ab(config['TimeTable.Optimize'].getboolean('FixWeeksAB'))
        self.set_fix_weeks_ab_data(fix_weeks_ab_data)

        self.set_excel_file_dir(config['TimeTable.Excel']['ExcelFileDir'])
        self.set_excel_file_name(config['TimeTable.Excel']['ExcelFileName'])
        self.set_excel_file_name_rooms(config['TimeTable.Excel']['ExcelFileNameRooms'])
        self.set_excel_file_name_ext(config['TimeTable.Excel']['ExcelFileNameExt'])
        self.set_excel_file_name_date(config['TimeTable.Excel'].getboolean('ExcelFileNameDate'))
        self.set_excel_worksheet_name(config['TimeTable.Excel']['ExcelWorksheetName'])
        self.set_font1_name(config['TimeTable.Excel']['Font1Name'])
        self.set_font1_size(config['TimeTable.Excel'].getint('Font1Size'))
        self.set_rows_height(config['TimeTable.Excel'].getint('RowsHeight'))

        translate_data = {}
        translate_data['teacher'] = config['TimeTable.Translate']['Teacher']
        translate_data['room'] = config['TimeTable.Translate']['Room']
        translate_data['hour'] = config['TimeTable.Translate']['Hour']
        translate_data['class'] = config['TimeTable.Translate']['Class']
        self.set_translate_data(translate_data)

    def getConfig(self):
        timetable_config = {}

        timetable_config['TimeTable'] = {}
        timetable_config['TimeTable']['Classes'] = self.for_classes
        timetable_config['TimeTable']['Days'] = self.for_days
        timetable_config['TimeTable']['TitleLine1'] = self.title_line_1
        timetable_config['TimeTable']['TitleLine2'] = self.title_line_2
        timetable_config['TimeTable']['Teachers'] = self.teachers
        timetable_config['TimeTable']['DayName'] = self.day_name
        timetable_config['TimeTable']['Hours'] = self.hours

        timetable_config['TimeTable']['Optimize'] = {}
        timetable_config['TimeTable']['Optimize']['TeacherName'] = self.optimize_teacher_name
        
        timetable_config['TimeTable']['Optimize']['LessonName'] = self.optimize_lesson_name
        timetable_config['TimeTable']['Optimize']['LessonNameData'] = self.optimize_lesson_name_data

        timetable_config['TimeTable']['Optimize']['ReplaceText'] = self.replace_text
        timetable_config['TimeTable']['Optimize']['ReplaceTextData'] = self.replace_text_data

        timetable_config['TimeTable']['Optimize']['FixWeeksAB'] = self.fix_weeks_ab
        timetable_config['TimeTable']['Optimize']['FixWeeksABData'] = self.fix_weeks_ab_data
        
        timetable_config['TimeTable']['Excel'] = {}
        timetable_config['TimeTable']['Excel']['ExcelFileDir'] = self.excel_file_dir
        timetable_config['TimeTable']['Excel']['ExcelFileName'] = self.excel_file_name
        timetable_config['TimeTable']['Excel']['ExcelFileNameRooms'] = self.excel_file_name_rooms
        timetable_config['TimeTable']['Excel']['ExcelFileNameExt'] = self.excel_file_name_ext
        timetable_config['TimeTable']['Excel']['ExcelFileNameDate'] = self.excel_file_name_date
        timetable_config['TimeTable']['Excel']['ExcelWorksheetName'] = self.excel_worksheet_name
        timetable_config['TimeTable']['Excel']['Font1Name'] = self.font_1_name
        timetable_config['TimeTable']['Excel']['Font1Size'] = self.font_1_size
        timetable_config['TimeTable']['Excel']['RowsHeight'] = self.default_rows_height

        timetable_config['TimeTable']['Traslate'] = self.translate_data

        return timetable_config

    def excel_column(self, n):
        arr = [0] * 10000
        i = 0
        r = ''
 
        # Step 1: Converting to number
        # assuming 0 in number system
        while (n > 0):
            arr[i] = n % 26
            n = int(n // 26)
            i += 1
         
        # Step 2: Getting rid of 0, as 0 is
        # not part of number system
        for j in range(0, i - 1):
            if (arr[j] <= 0):
                arr[j] += 26
                arr[j + 1] = arr[j + 1] - 1
 
        for j in range(i, -1, -1):
            if (arr[j] > 0):
                r += chr(ord('A') + (arr[j] - 1))

        return r

    def optimize_teacher_name_(self, name):
        if name == '':
            return name

        short = ''
        teachers = name.split(',')

        for teacher in teachers:
            n1 = teacher.strip().split(' ')
            if len(n1) == 1:
                return name.strip()
            n2 = n1[1] # name
            n3 = n1[0] # surname
            if n3.find('-') > 0:
                n4 = n3.split('-')
                n3 = n4[0][:1] + '.-' + n4[1]
            short += ' ' + n2[:1] + '. ' + n3 + ','

        return short[:-1].strip()

    def optimize_lesson_name_(self, name):
        optimize = False

        for optimize in self.optimize_lesson_name_data:
            find = list(optimize.keys())[0]
            replace = list(optimize.values())[0]
            replace = replace.replace('#NL#','\n')

            if name.find(find) > 0:
                name = name.replace(find, replace)                
                optimize = True
                # print(name)

        return name, optimize

    def create_workbook(self, filename):
        self.workbook = xlsxwriter.Workbook(filename)
        self.worksheet = self.workbook.add_worksheet(self.excel_worksheet_name)

        self.worksheet.set_column(0, 0, 2)
        self.worksheet.set_column(1, 0, 3)

        self.worksheet.set_default_row(self.default_rows_height)

        # title_1
        self.title_1 = self.workbook.add_format({'bold': True, 'num_format': '#', 'text_wrap': True})
        # title_1.set_color('white')
        # title_1.set_bg_color('#21618c')
        self.title_1.set_font_size(20)
        self.title_1.set_center_across()
        self.title_1.set_align('center')
        self.title_1.set_align('vcenter')

        # title_2
        self.title_2 = self.workbook.add_format({'bold': True, 'num_format': '#'})
        self.title_2.set_font_size(14)
        self.title_2.set_color('white')
        self.title_2.set_bg_color('#21618c')
        self.title_2.set_center_across()
        self.title_2.set_align('center')
        self.title_2.set_align('vcenter')

        # header_1
        self.header_1 = self.workbook.add_format({'bold': True, 'num_format': '#'})
        self.header_1.set_color('white')
        self.header_1.set_bg_color('#21618c')
        self.header_1.set_center_across()
        self.header_1.set_align('center')
        self.header_1.set_align('vcenter')

        # header_2
        self.header_2 = self.workbook.add_format({'bold': True, 'num_format': '#'})
        self.header_2.set_color('white')
        self.header_2.set_bg_color('#154360')
        self.header_2.set_center_across()
        self.header_2.set_align('center')
        self.header_2.set_align('vcenter')

        # header_3
        self.header_3 = self.workbook.add_format({'bold': True, 'num_format': '#'})
        self.header_3.set_center_across()
        self.header_3.set_align('center')
        self.header_3.set_align('vcenter')

        # header_4
        self.header_4 = self.workbook.add_format()
        self.header_4.set_center_across()
        self.header_4.set_align('center')
        self.header_4.set_align('vcenter')

        # header_5
        self.header_5 = self.workbook.add_format({'bold': True, 'text_wrap': True})
        self.header_5.set_center_across()
        self.header_5.set_align('center')
        self.header_5.set_align('vcenter')
        self.header_5.set_font_name(self.font_1_name)
        self.header_5.set_font_size(self.font_1_size)

        # header_6
        self.header_6 = self.workbook.add_format({'bold': True, 'text_wrap': True})
        self.header_6.set_bg_color('#eaecee')
        self.header_6.set_top_color('#ffffff')
        self.header_6.set_top()
        self.header_6.set_center_across()
        self.header_6.set_align('center')
        self.header_6.set_align('vcenter')
        self.header_6.set_font_name(self.font_1_name)
        self.header_6.set_font_size(self.font_1_size)

        # header_6a
        self.header_6a = self.workbook.add_format({'bold': True, 'text_wrap': True})
        self.header_6a.set_bg_color('#eaecee')
        self.header_6a.set_top_color('#21618c')
        self.header_6a.set_top()
        self.header_6a.set_center_across()
        self.header_6a.set_align('center')
        self.header_6a.set_align('vcenter')
        self.header_6a.set_font_name(self.font_1_name)
        self.header_6a.set_font_size(self.font_1_size)

        # header_6_o
        self.header_6_o = self.workbook.add_format({'bold': True, 'text_wrap': True})
        self.header_6_o.set_bg_color('#eaecee')
        self.header_6_o.set_top_color('#ffffff')
        self.header_6_o.set_top()
        self.header_6_o.set_center_across()
        self.header_6_o.set_align('center')
        self.header_6_o.set_align('vcenter')
        self.header_6_o.set_font_name(self.font_1_name)
        self.header_6_o.set_font_size(10)

        # header_6a_o
        self.header_6a_o = self.workbook.add_format({'bold': True, 'text_wrap': True})
        self.header_6a_o.set_bg_color('#eaecee')
        self.header_6a_o.set_top_color('#21618c')
        self.header_6a_o.set_top()
        self.header_6a_o.set_center_across()
        self.header_6a_o.set_align('center')
        self.header_6a_o.set_align('vcenter')
        self.header_6a_o.set_font_name(self.font_1_name)
        self.header_6a_o.set_font_size(10)

        # hours format
        self.format_hour = self.workbook.add_format({'bold': True, 'num_format': '#'})
        self.format_hour.set_color('white')
        self.format_hour.set_bg_color('#21618c')
        self.format_hour.set_center_across()
        self.format_hour.set_align('center')
        self.format_hour.set_align('vcenter')

        # def day in table
        self.format_day = self.workbook.add_format({'bold': True, 'border': 2})
        self.format_day.set_color('white')
        self.format_day.set_bg_color('#2980b9')
        self.format_day.set_align('center')
        self.format_day.set_align('vcenter')
        # self.format_day.set_right_color('red')
        self.format_day.set_rotation(90)
        self.format_day.set_font_size(12)

        # def top of table
        self.worksheet.write('A4', '', self.header_1)
        self.worksheet.write('B4', '', self.header_1)
        self.worksheet.write('C4', '', self.header_1)
        self.worksheet.write('D4', '', self.header_1)
        self.worksheet.write('A5', '', self.header_1)
        self.worksheet.write('B5', '', self.header_1)
        self.worksheet.write('C5', self.translate_data['hour'], self.header_3)
        self.worksheet.write('D5', '', self.header_1)
        self.worksheet.set_row(5, 4)
        self.worksheet.write('A6', '', self.header_1)
        self.worksheet.write('B6', '', self.header_1)
        self.worksheet.write('C6', '', self.header_1)
        self.worksheet.write('D6', '', self.header_1)

        # days = ['MONDAY', 'TUESDAY', 'WEDNESDAY', 'THURSDAY', 'FRIDAY']

        row_prefix = 7

        for d_idx, day in enumerate(self.day_name):

            if d_idx >= self.for_days:
                break

            self.worksheet.merge_range('A'+str(row_prefix)+':A'+str(row_prefix+10), day, self.format_day)

            self.worksheet.write('B'+str(row_prefix), '0', self.format_hour)
            self.worksheet.write('C'+str(row_prefix), self.hours[0], self.header_4)
            self.worksheet.write('D'+str(row_prefix), '', self.header_1)

            self.worksheet.write('B'+str(row_prefix+1), '1', self.format_hour)
            self.worksheet.write('C'+str(row_prefix+1), self.hours[1], self.header_4)
            self.worksheet.write('D'+str(row_prefix+1), '', self.header_1)

            self.worksheet.write('B'+str(row_prefix+2), '2', self.format_hour)
            self.worksheet.write('C'+str(row_prefix+2), self.hours[2], self.header_4)
            self.worksheet.write('D'+str(row_prefix+2), '', self.header_1)

            self.worksheet.write('B'+str(row_prefix+3), '3', self.format_hour)
            self.worksheet.write('C'+str(row_prefix+3), self.hours[3], self.header_4)
            self.worksheet.write('D'+str(row_prefix+3), '', self.header_1)

            self.worksheet.write('B'+str(row_prefix+4), '4', self.format_hour)
            self.worksheet.write('C'+str(row_prefix+4), self.hours[4], self.header_4)
            self.worksheet.write('D'+str(row_prefix+4), '', self.header_1)

            self.worksheet.write('B'+str(row_prefix+5), '5', self.format_hour)
            self.worksheet.write('C'+str(row_prefix+5), self.hours[5], self.header_4)
            self.worksheet.write('D'+str(row_prefix+5), '', self.header_1)

            self.worksheet.write('B'+str(row_prefix+6), '6', self.format_hour)
            self.worksheet.write('C'+str(row_prefix+6), self.hours[6], self.header_4)
            self.worksheet.write('D'+str(row_prefix+6), '', self.header_1)

            self.worksheet.write('B'+str(row_prefix+7), '7', self.format_hour)
            self.worksheet.write('C'+str(row_prefix+7), self.hours[7], self.header_4)
            self.worksheet.write('D'+str(row_prefix+7), '', self.header_1)

            self.worksheet.write('B'+str(row_prefix+8), '8', self.format_hour)
            self.worksheet.write('C'+str(row_prefix+8), self.hours[8], self.header_4)
            self.worksheet.write('D'+str(row_prefix+8), '', self.header_1)

            self.worksheet.write('B'+str(row_prefix+9), '9', self.format_hour)
            self.worksheet.write('C'+str(row_prefix+9), self.hours[9], self.header_4)
            self.worksheet.write('D'+str(row_prefix+9), '', self.header_1)

            self.worksheet.write('B'+str(row_prefix+10), '10', self.format_hour)
            self.worksheet.write('C'+str(row_prefix+10), self.hours[10], self.header_4)
            self.worksheet.write('D'+str(row_prefix+10), '', self.header_1)

            # def footer day of table
            self.worksheet.set_row(row_prefix+10, 4)
            self.worksheet.write('A'+str(row_prefix+11), '', self.header_1)
            self.worksheet.write('B'+str(row_prefix+11), '', self.header_1)
            self.worksheet.write('C'+str(row_prefix+11), '', self.header_1)
            self.worksheet.write('D'+str(row_prefix+11), '', self.header_1)

            row_prefix += 12

    def save_workbook(self):
        while True:
            try:
                self.workbook.close()
                return True

            except xlsxwriter.exceptions.FileCreateError as e:
                return -1

                decision = input(
                    'Exception caught in workbook.close(): %s\n'
                    'Please close the file if it is open in Excel.\n'
                    'Try to write file again? [Y/n]: ' % e
                )
                if decision != 'n':
                    continue

            break

        return False

    def create_timetable_classes(self):

        self.excel_full_file_name = self.save_dir + '/' + self.excel_file_dir + '/' + self.excel_file_name
        if self.excel_file_name_date:
            self.excel_full_file_name += '_' + datetime.today().strftime('%Y%m%d_%H%M%S') + '.' + self.excel_file_name_ext
        else:
            self.excel_full_file_name += '.' + self.excel_file_name_ext

        # print(self.excel_full_file_name)

        # create workbook
        self.create_workbook(self.excel_full_file_name)

        # create timetable
        double_rows = []
        thin_rows = []
        thin_cols = []

        # print(self.for_classes)
        # print(self.classes)

        cnt_for_classes = len(self.for_classes)
        if cnt_for_classes == 0:
            return False

        # print('Creating a lesson plan for classes:')

        for c_idx, c in enumerate(self.for_classes):
        # for c_idx, c in enumerate(self.classes):

            col_1 = 5 + (4*c_idx)
            col_2 = 6 + (4*c_idx)
            col_3 = 7 + (4*c_idx)
            col_4 = 8 + (4*c_idx)

            c_name = c.upper() + ' ' + self.translate_data['class']
            
            # if c_idx < (cnt_for_classes-1):
            #    print(c.upper()+', ', end='')
            # else:
            #    print(c.upper())
            # print(self.classes[c])
            
            self.worksheet.merge_range(self.excel_column(col_1)+'4'+':'+self.excel_column(col_4)+'4', c_name, self.title_2)

            # self.worksheet.write(excel_column(col_1)+'4', c_name, self.header_1)
            # self.worksheet.write(excel_column(col_2)+'4', '', self.header_1)
            # self.worksheet.write(excel_column(col_3)+'4', '', self.header_1)
            # self.worksheet.write(excel_column(col_4)+'4', '', self.header_1)

            if c.lower() in self.teachers.keys():
                t_room = self.teachers[c.lower()]
            else:
                t_room = ('', '')
            # print(t_room)

            try:
                if t_room[1] == '':
                    pass
            except:
                t_room = ('', '')

            if (t_room[0] != ''):
                self.worksheet.write(self.excel_column(col_1)+'5', t_room[0], self.header_5)
            self.worksheet.write(self.excel_column(col_2)+'5', self.translate_data['teacher'], self.header_5)
            if (t_room[1] != ''):
                self.worksheet.write(self.excel_column(col_3)+'5', self.translate_data['room']+' '+t_room[1], self.header_5)
            self.worksheet.write(self.excel_column(col_4)+'5', '', self.header_1)

            self.worksheet.set_row(5, 4)
            self.worksheet.write(self.excel_column(col_1)+'6', '', self.header_1)
            self.worksheet.write(self.excel_column(col_2)+'6', '', self.header_1)
            self.worksheet.write(self.excel_column(col_3)+'6', '', self.header_1)
            self.worksheet.write(self.excel_column(col_4)+'6', '', self.header_1)

            thin_cols.append(col_4-1)

            row_prefix = 7
            
            # print(self.classes)

            for d_idx, day in enumerate(self.day_name, 1):

                if d_idx > self.for_days:
                    break

                # print(day, c, d_idx)
                # print(self.classes[c][d_idx+1])
                # return False

                ln_len = len(self.classes[c][d_idx])
                # print(ln_len)

                if ln_len < len(self.hours):
                    # print(self.classes[c][d_idx])
                    for i in range(ln_len, len(self.hours)):
                        data = [{'name': '--', 'teachers': '', 'room': ''}]
                        self.classes[c][d_idx][i] = data
                    # print(self.classes[c][d_idx])

                for l_idx, lesson in enumerate(self.classes[c][d_idx]):

                    s1, s2, s3 = '', '', ''

                    l_cnt = 0
                    l_len = len(self.classes[c][d_idx][lesson])

                    # fix weeks A <> B
                    if self.fix_weeks_ab:
                        for l in self.classes[c][d_idx][lesson]:
                            breaker = False
                            for cl, search, data in self.fix_weeks_ab_data:
                                if c in cl and l[next(iter(search))] == search[next(iter(search))]:                            
                                    # data = {'name': '#', 'teachers': '#', 'room': '#'}
                                    self.classes[c][d_idx][l_idx].append(data.copy())
                                    breaker = True
                                    break
                            if breaker:
                                break

                    # print(self.classes[c][d_idx])

                    for l in self.classes[c][d_idx][lesson]:
                        # print(l)

                        if self.replace_text:
                            for f, t in self.replace_text_data:
                                l['name'] = l['name'].replace(f, t)
                                l['teachers'] = l['teachers'].replace(f, t)
                                l['room'] = l['room'].replace(f, t)

                        if l['name'] != '--':

                            if self.optimize_lesson_name and l_len == 1:
                                s1_o, optimize = self.optimize_lesson_name_(l['name'])
                                if optimize:
                                    s1 += s1_o + '\n'
                                    l_cnt += 1
                                else:
                                    s1 += l['name'] + '\n'
                            else:
                                s1 += l['name'] + '\n'
                        else:
                            s1 += '\n'                        

                        s2 += self.optimize_teacher_name_(l['teachers']) + '\n' if self.optimize_teacher_name else l['teachers'] + '\n'
                        
                        # print (self.optimize_teacher_name_(l['teachers']))
                            
                        s3 += l['room'] + '\n'

                        room_name_optimize = False
                        if s3.upper().find('(A)') > 0 or s3.upper().find('(B)') > 0:
                            room_name_optimize = True

                        l_cnt += 1

                    s1 = s1[:-1]
                    s2 = s2[:-1]
                    s3 = s3[:-1]

                    if (l_cnt > 1):
                        double_rows.append(row_prefix+l_idx-1)

                    self.worksheet.write(self.excel_column(col_1)+str(row_prefix+l_idx), s1, self.header_5)
                    self.worksheet.write(self.excel_column(col_2)+str(row_prefix+l_idx), s2, self.header_6a if l_idx == 0 else self.header_6)
                    if room_name_optimize:
                        self.worksheet.write(self.excel_column(col_3)+str(row_prefix+l_idx), s3, self.header_6a_o if l_idx == 0 else self.header_6_o)
                    else:
                        self.worksheet.write(self.excel_column(col_3)+str(row_prefix+l_idx), s3, self.header_6a if l_idx == 0 else self.header_6)
                    self.worksheet.write(self.excel_column(col_4)+str(row_prefix+l_idx), '', self.header_1)            

                # def footer day of table
                self.worksheet.set_row(row_prefix+10, 4)
                self.worksheet.write(self.excel_column(col_1)+str(row_prefix+11), '', self.header_1)
                self.worksheet.write(self.excel_column(col_2)+str(row_prefix+11), '', self.header_1)
                self.worksheet.write(self.excel_column(col_3)+str(row_prefix+11), '', self.header_1)
                self.worksheet.write(self.excel_column(col_4)+str(row_prefix+11), '', self.header_1)

                thin_rows.append(row_prefix+10)

                row_prefix += 12
            
        # double rows
        for r in double_rows:
            self.worksheet.set_row(r, self.default_rows_height * 2)

        # title
        title = self.title_line_1+'\n'+self.title_line_2 if self.title_line_2 != '' else self.title_line_1
        self.worksheet.merge_range('A2:'+self.excel_column(col_4)+'2', title, self.title_1)
        self.worksheet.set_row(1, 60)

        # autofit
        self.worksheet.autofit()

        # thin rows
        self.worksheet.set_column(0, 0, 3)
        self.worksheet.set_column(3, 3, 0.1)

        for c in thin_cols:
            self.worksheet.set_column(c, c, 0.1)

        for r in thin_rows:
            self.worksheet.set_row(r, 4)

        # save workbook
        return self.save_workbook()

    def create_timetable_rooms(self):

        self.excel_full_file_name = self.save_dir + '/' + self.excel_file_dir + '/' + self.excel_file_name_rooms
        if self.excel_file_name_date:
            self.excel_full_file_name += '_' + datetime.today().strftime('%Y%m%d_%H%M%S') + '.' + self.excel_file_name_ext
        else:
            self.excel_full_file_name += '.' + self.excel_file_name_ext

        # create workbook
        self.create_workbook(self.excel_full_file_name)

        # create timetable
        double_rows = []
        thin_rows = []
        thin_cols = []

        # print(self.for_classes)
        # print(self.classes)

        cnt_for_rooms = len(self.rooms.keys())
        if cnt_for_rooms == 0:
            return False

        # print('Creating a lesson plan for rooms:')

        for c_idx, room in enumerate(self.rooms.keys()):
            col_1 = 5 + (3*c_idx)
            col_2 = 6 + (3*c_idx)
            col_3 = 7 + (3*c_idx)

            # print(room)

            s_room = self.translate_data['room'] + ' ' + room
            # s_room = room

            self.worksheet.merge_range(self.excel_column(col_1)+'4'+':'+self.excel_column(col_3)+'4', s_room, self.title_2)

            self.worksheet.write(self.excel_column(col_1)+'5', 'Klase', self.header_5)
            self.worksheet.write(self.excel_column(col_2)+'5', 'Priekšmets', self.header_5)
            self.worksheet.write(self.excel_column(col_3)+'5', '', self.header_1)

            self.worksheet.set_row(5, 4)
            self.worksheet.write(self.excel_column(col_1)+'6', '', self.header_1)
            self.worksheet.write(self.excel_column(col_2)+'6', '', self.header_1)
            self.worksheet.write(self.excel_column(col_3)+'6', '', self.header_1)

            thin_cols.append(col_3-1)

            row_prefix = 7

            for d_idx, day in enumerate(self.day_name, 1):

                if d_idx > self.for_days:
                    break
                
                len_hours = len(self.hours)
                # print(len_hours)

                if d_idx in self.rooms[room]:
                    for l_idx, h in enumerate(self.hours, 0):
                        
                        s1, s2 = '', ''

                        if l_idx in self.rooms[room][d_idx]:

                            lessons = self.rooms[room][d_idx][l_idx]
                            len_lessons = len(lessons)
                            for data in lessons:
                                # print(data)

                                s1 += str(data[0]) + '\n'
                                s2 += str(data[1]) + '\n'

                            if len_lessons > 1:
                                dr_add = True
                                for dr in double_rows:
                                    if dr[0] == row_prefix+l_idx-1 and dr[1] > len_lessons:
                                        dr_add = False
                                        break
                                if dr_add:
                                    double_rows.append((row_prefix+l_idx-1, len_lessons))

                            s1 = s1[:-1]
                            s2 = s2[:-1]
                    
                        # print(l_idx, data)

                        self.worksheet.write(self.excel_column(col_1)+str(row_prefix+l_idx), s1, self.header_5)
                        self.worksheet.write(self.excel_column(col_2)+str(row_prefix+l_idx), s2, self.header_5)
                        self.worksheet.write(self.excel_column(col_3)+str(row_prefix+l_idx), '', self.header_1)   
                else:
                    for l_idx, h in enumerate(self.hours, 0):
                        self.worksheet.write(self.excel_column(col_1)+str(row_prefix+l_idx), '', self.header_5)
                        self.worksheet.write(self.excel_column(col_2)+str(row_prefix+l_idx), '', self.header_5)
                        self.worksheet.write(self.excel_column(col_3)+str(row_prefix+l_idx), '', self.header_1)

                # def footer day of table
                self.worksheet.set_row(row_prefix+10, 4)
                self.worksheet.write(self.excel_column(col_1)+str(row_prefix+11), '', self.header_1)
                self.worksheet.write(self.excel_column(col_2)+str(row_prefix+11), '', self.header_1)
                self.worksheet.write(self.excel_column(col_3)+str(row_prefix+11), '', self.header_1)

                thin_rows.append(row_prefix+10)

                row_prefix += 12

        # double rows
        for r in double_rows:
            self.worksheet.set_row(r[0], self.default_rows_height * r[1])

        # title
        title = self.title_line_1+'\n'+self.title_line_2 if self.title_line_2 != '' else self.title_line_1
        self.worksheet.merge_range('A2:'+self.excel_column(col_3)+'2', title, self.title_1)
        self.worksheet.set_row(1, 60)

        # autofit
        self.worksheet.autofit()

        # thin rows
        self.worksheet.set_column(0, 0, 3)
        self.worksheet.set_column(3, 3, 0.1)

        for c in thin_cols:
            self.worksheet.set_column(c, c, 0.1)

        for r in thin_rows:
            self.worksheet.set_row(r, 4)

        # save workbook
        return self.save_workbook()

    def remove_data_dir(self):
        if os.path.isdir(self.save_dir + '/' + self.excel_file_dir):
            for file_name in os.listdir(self.save_dir + '/' + self.excel_file_dir):
                if file_name.endswith('.xlsx'):
                    print(self.save_dir + '/' + self.excel_file_dir + '/' + file_name)
                    # os.remove(self.save_dir + '/' + self.data_dir + '/' + file_name)