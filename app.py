from flask import Flask, jsonify, render_template, request
import requests
import json
import os

app = Flask(__name__)

@app.route('/fetch-data', methods=['GET'])
def fetch_data():
    url = "https://narg.edupage.org/timetable/server/regulartt.js?__func=regularttGetData"
    
    headers = {
        "accept": "*/*",
        "accept-language": "ru-RU,ru;q=0.9,hu;q=0.8,en;q=0.7",
        "content-type": "application/json; charset=UTF-8",
        "origin": "https://narg.edupage.org",
        "priority": "u=1, i",
        "referer": "https://narg.edupage.org/",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "user-agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1"
    }
    
    cookies = {
        "PHPSESSID": "b3b8a58a9a64d8fa845342fcd7088784"
    }
    
    data = {
        "__args": [None, "35"],
        "__gsh": "00000000"
    }
    
    response = requests.post(url, headers=headers, cookies=cookies, json=data)
    
    with open('weird.json', 'w', encoding='utf-8') as f:
        json.dump(response.json(), f, ensure_ascii=False, indent=4)
    
    return jsonify({
        "status": "success",
        "message": "Data fetched and saved to weird.json"
    })

def load_timetable_data():
    try:
        with open('weird.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        result = {
            'classes': {},
            'periods': {},
            'days': {},
            'subjects': {},
            'teachers': {},
            'classrooms': {},
            'lessons': {},
            'cards': {}
        }
        
        for table in data['r']['dbiAccessorRes']['tables']:
            table_id = table['id']
            if table_id in result:
                for row in table.get('data_rows', []):
                    result[table_id][row['id']] = row
                    
        return result
    except Exception as e:
        print(f"Error loading data: {e}")
        return None

def get_css_class_for_subject(subject_name):
    """Get a CSS class name based on the subject name"""
    subject_name = subject_name.lower() if subject_name else ''
    
    if 'konsultat' in subject_name:
        return 'konsultatsioonid'
    elif 'kehaline' in subject_name or 'kasvatus' in subject_name:
        return 'kehaline-kasvatus'
    elif 'eesti keel' in subject_name:
        return 'eesti-keel'
    elif 'kunst' in subject_name:
        return 'kunst'
    elif 'matemat' in subject_name:
        return 'matemaatika'
    else:
        return ''

@app.route('/api/classes', methods=['GET'])
def api_classes():
    """API endpoint to get all classes for the dropdown selector"""
    data = load_timetable_data()
    if not data:
        return jsonify([])
    
    classes = []
    for class_id, class_obj in data['classes'].items():
        classes.append({
            'id': class_id,
            'name': class_obj['name']
        })
    
    classes.sort(key=lambda x: x['name'])
    return jsonify(classes)

@app.route('/api/timetable/<class_id>', methods=['GET'])
def api_timetable(class_id):
    refresh = request.args.get('refresh', 'false').lower() == 'true'
    
    if refresh:
        fetch_data()
    
    data = load_timetable_data()
    if not data:
        return jsonify({"error": "Error loading data"})
    
    return jsonify({"status": "success", "message": "Data refreshed"})

@app.route('/timetable/<class_id>', methods=['GET'])
def show_timetable(class_id):
    data = load_timetable_data()
    if not data:
        return "Error loading data"
    
    class_data = None
    for class_id_key, class_obj in data['classes'].items():
        if class_id_key == class_id:
            class_data = class_obj
            break
    
    if not class_data:
        return f"Class with ID {class_id} not found"
    
    periods = sorted(data['periods'].values(), key=lambda x: int(x.get('period', 0)))
    period_ids = [p['id'] for p in periods]
    
    if data['days'] and len(data['days']) > 0:
        first_day = next(iter(data['days'].values()))
        print("First day keys:", list(first_day.keys()))
    
    day_order = ['Es', 'Te', 'Ko', 'Ne', 'Re']
    
    days_dict = {day['short']: day for day in data['days'].values()}
    days = [days_dict.get(day_short) for day_short in day_order if day_short in days_dict]
    
    for card_id, card in data['cards'].items():
        if 'periods_count' in card and int(card['periods_count']) > 1:
            lesson = data['lessons'].get(card['lessonid'])
            if lesson and class_id in lesson.get('classids', []):
                subject = data['subjects'].get(lesson.get('subjectid', ''), {}).get('name', '')
                print(f"Found multi-period lesson: {subject}, periods: {card['periods_count']}, start: {card['period']}")
    
    multi_period_lessons = {}
    for day_short in day_order:
        multi_period_lessons[day_short] = []
    
    for card_id, card in data['cards'].items():
        if 'periods_count' not in card or int(card['periods_count']) <= 1:
            continue
            
        lesson = data['lessons'].get(card['lessonid'])
        if not lesson or class_id not in lesson.get('classids', []):
            continue
            
        start_period_id = card['period']
        periods_count = int(card['periods_count'])
        
        for day_index, day_short in enumerate(day_order):
            if day_index >= len(card.get('days', '')) or card['days'][day_index] != '1':
                continue
                
            subject = data['subjects'].get(lesson.get('subjectid', ''), {})
            subject_name = subject.get('name', '')
            
            teacher_name = ''
            if lesson.get('teacherids') and len(lesson['teacherids']) > 0:
                teacher = data['teachers'].get(lesson['teacherids'][0], {})
                teacher_name = teacher.get('short', '')
            
            classroom_name = ''
            if card.get('classroomids') and len(card['classroomids']) > 0:
                classroom = data['classrooms'].get(card['classroomids'][0], {})
                classroom_name = classroom.get('short', '')
                
            start_period_index = period_ids.index(start_period_id) if start_period_id in period_ids else -1
            if start_period_index < 0:
                continue
                
            end_period_index = min(start_period_index + periods_count - 1, len(period_ids) - 1)
            
            multi_period_lessons[day_short].append({
                'start_period_index': start_period_index,
                'end_period_index': end_period_index,
                'periods_count': periods_count,
                'subject': subject_name,
                'subject_short': subject.get('short', ''),
                'color': subject.get('color', '#FFFFFF'),
                'teacher': teacher_name,
                'classroom': classroom_name,
                'css_class': get_css_class_for_subject(subject_name)
            })
            
            print(f"Added multi-period lesson for {day_short}: {subject_name}, spans: {periods_count}, from {start_period_index} to {end_period_index}")
    
    timetable = []
    for day_short in day_order:
        day_data = days_dict.get(day_short)
        if not day_data:
            continue
            
        day_row = {'day': day_short, 'periods': []}
        multi_lessons = multi_period_lessons[day_short]
        
        multi_lessons.sort(key=lambda x: x['start_period_index'])
        
        covered_periods = [False] * len(periods)
        
        for lesson in multi_lessons:
            start_idx = lesson['start_period_index']
            end_idx = lesson['end_period_index']
            
            for i in range(start_idx, end_idx + 1):
                covered_periods[i] = True
                
            if start_idx < len(periods):
                day_row['periods'].append({
                    'has_lessons': True,
                    'is_multi_period': True,
                    'period_span': end_idx - start_idx + 1,
                    'lessons': [lesson],
                    'count': 1
                })
                
                for i in range(start_idx + 1, end_idx + 1):
                    day_row['periods'].append({
                        'has_lessons': False,
                        'is_placeholder': True,
                        'lessons': [],
                        'count': 0
                    })
        
        period_idx = 0
        for i, period in enumerate(periods):
            if covered_periods[i]:
                continue
                
            period_lessons = []
            for card_id, card in data['cards'].items():
                if card['period'] != period['id']:
                    continue
                    
                if 'periods_count' in card and int(card['periods_count']) > 1:
                    continue
                    
                day_index = day_order.index(day_short) if day_short in day_order else -1
                if day_index < 0 or day_index >= len(card.get('days', '')) or card['days'][day_index] != '1':
                    continue
                    
                lesson = data['lessons'].get(card['lessonid'])
                if not lesson or class_id not in lesson.get('classids', []):
                    continue
                    
                subject = data['subjects'].get(lesson.get('subjectid', ''), {})
                subject_name = subject.get('name', '')
                
                teacher_name = ''
                if lesson.get('teacherids') and len(lesson['teacherids']) > 0:
                    teacher = data['teachers'].get(lesson['teacherids'][0], {})
                    teacher_name = teacher.get('short', '')
                
                classroom_name = ''
                if card.get('classroomids') and len(card['classroomids']) > 0:
                    classroom = data['classrooms'].get(card['classroomids'][0], {})
                    classroom_name = classroom.get('short', '')
                
                period_lesson = {
                    'subject': subject_name,
                    'subject_short': subject.get('short', ''),
                    'color': subject.get('color', '#FFFFFF'),
                    'teacher': teacher_name,
                    'classroom': classroom_name,
                    'css_class': get_css_class_for_subject(subject_name)
                }
                period_lessons.append(period_lesson)
            
            if period_lessons:
                day_row['periods'].append({
                    'has_lessons': True,
                    'is_multi_period': False,
                    'period_span': 1,
                    'lessons': period_lessons,
                    'count': len(period_lessons)
                })
            else:
                day_row['periods'].append({
                    'has_lessons': False,
                    'is_multi_period': False,
                    'period_span': 1,
                    'lessons': [],
                    'count': 0
                })
                
        while len(day_row['periods']) < len(periods):
            day_row['periods'].append({
                'has_lessons': False,
                'is_multi_period': False,
                'period_span': 1,
                'lessons': [],
                'count': 0
            })
            
        if len(day_row['periods']) > len(periods):
            day_row['periods'] = day_row['periods'][:len(periods)]
            
        timetable.append(day_row)
    
    timetable.sort(key=lambda day: day_order.index(day['day']) if day['day'] in day_order else 999)
    
    return render_template(
        'timetable.html', 
        timetable=timetable, 
        periods=periods, 
        class_name=class_data['name'], 
        class_id=class_id
    )

@app.route('/classes', methods=['GET'])
def list_classes():
    data = load_timetable_data()
    if not data:
        return "Error loading data"
    
    classes = []
    for class_id, class_obj in data['classes'].items():
        classes.append({
            'id': class_id,
            'name': class_obj['name']
        })
    
    classes.sort(key=lambda x: x['name'])
    return render_template('classes.html', classes=classes)

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True) 