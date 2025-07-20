'''
ESSA :: Electronic Grade Book Assistant
Copyright (C) 2025 Mariusz Duka
This file is part of ESSA and is licensed under the GNU GPLv3 or later.
See the LICENSE file for full text.
'''

import re
import importlib.util
from datetime import datetime
from defines import NAME_DAY, SCHOOL_YEAR_SCHEDULE

def remove_html_tags(text):
    """Remove html tags from a string"""        
    if text == '':
        return ''    
    clean = re.compile('<[^>]*>')
    text = re.sub(clean, '', text)
    text = text.replace('&nbsp;', ' ').strip()
    return text

def sort_human(seq, key=None):
    def convert(text):
        return int(text) if text.isdigit() else text       
    def alphanum(obj):
        if key is not None:
            return [convert(c) for c in re.split(r'(\d+)', key(obj))]
        return [convert(c) for c in re.split(r'(\d+)', obj)]
    try:
        return sorted(seq, key=alphanum)
    except Exception:
        return []

def days_between(d1, d2):
    d1 = datetime.strptime(d1, "%Y-%m-%d")
    d2 = datetime.strptime(d2, "%Y-%m-%d")
    return (d2 - d1).days

def day_name():
    names = [
        'pirmdiena',
        'otrdiena',
        'trešdiena',
        'ceturtdiena',
        'piektdiena',
        'sestdiena',
        'svētdiena'
    ]
    today = datetime.today()
    return names[today.weekday()]

def get_names_by_date(date=None):
    """Get names based on the day in the month"""
    if date is None:
        today = datetime.today()
        date = today.strftime("%m-%d")
    if not isinstance(date, str):
        raise ValueError("Date must be a string in the format 'MM-DD'")
    if date in NAME_DAY:
        return NAME_DAY[date]
    return []

def get_current_school_year():
    """Determine the current school year based on today's date."""
    today = datetime.today()
    year = today.year
    if today.month >= 8: # August or later, the information will already reflect the next school year
        return f"{year}/{year + 1}"
    return f"{year - 1}/{year}"

def get_semester_and_holiday_info():
    """Get semester end dates and holiday periods for the current school year."""
    school_year = get_current_school_year()
    if school_year not in SCHOOL_YEAR_SCHEDULE:
        return ""

    schedule = SCHOOL_YEAR_SCHEDULE[school_year]
    
    text = f"#MĀCĪBU GADS {school_year}#\n\n"
    text += "*Pirmais semestris*"
    text += f"\n{schedule['semesters']['first']['start']} līdz {schedule['semesters']['first']['end']}\n"
    text += "\n*Otrais semestris*\n"
    for second in schedule['semesters']['second']:
        grade_mapping = {
            "1-8_and_10-11_grades": "1.–8. un 10.–11. klasēm",
            "9th_grade": "9. klasēm",
            "12th_grade": "12. klasēm"
        }
        grade_range = grade_mapping.get(second, second)
        text += f"{grade_range}: {schedule['semesters']['second'][second]['start']} līdz {schedule['semesters']['second'][second]['end']}\n"
        
    text += "\n*Brīvdienas*\n"
    for holiday in schedule['holidays']:
        holiday_mapping = {
            'spring': 'Pavasara brīvlaiks',
            'summer': 'Vasaras brīvlaiks',
            'autumn': 'Rudens brīvlaiks',
            'winter': 'Ziemas brīvlaiks'
        }
        holiday_mapping = holiday_mapping.get(holiday, holiday)
        text += f"{holiday_mapping}: {schedule['holidays'][holiday]['start']} līdz {schedule['holidays'][holiday]['end']}\n"    
    
    return text

def copyright_notice():
    RESET = '\033[0m'
    GRAY = '\033[90m'
    ORANGE = '\033[38;5;208m'
    BOLD = '\033[1m'

    logo = f"""{ORANGE}{BOLD}
  _____ ____ ____    _    
 | ____/ ___/ ___|  / \\   
 |  _| \\___ \\___ \\ / _ \\  
 | |___ ___) |__) / ___ \\ 
 |_____|____/____/_/   \\_\\                          
    {RESET}
    """

    info_lines = [
        f"{ORANGE}{BOLD}ESSA :: Electronic Grade Book Assistant{RESET}",
        f"{GRAY}Copyright (C) 2025 Mariusz Duka{RESET}",
        f"{GRAY}This file is part of ESSA and is licensed under the GNU GPLv3 or later.{RESET}",
        f"{GRAY}See the LICENSE file for full text.{RESET}"
    ]

    print(logo)
    for line in info_lines:
        print(line)
        
def is_module_available(module_name):
    return importlib.util.find_spec(module_name) is not None