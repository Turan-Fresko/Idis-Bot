import requests,json,datetime
from bs4 import BeautifulSoup
import BypassPhp

headers = {}
session = requests.session()

with open('data.json', 'r', encoding='utf-8') as file:
    data = json.load(file)

headers = {
    "user-agent": data["config"]["user-agent"],
    "cookie": data["config"]["cookie"]
}

session.headers = headers

def update_cookie():
    try:
        response = BypassPhp.get_cookie()
        if response[0]:
            print("[*] Successful authorization https://idis.ieml.ru/Education/protected/...")
            with open('data.json', 'r', encoding='utf-8') as file:
                data = json.load(file)
            session.headers.update(data["config"])
            return [True, "Succes"]
        return [False,"Failed Auth"]

    except Exception as err:
        return [False,err]

def get_teachers():
    try:
        r = session.get("https://idis.ieml.ru/Education/protected/student-cabinet/SessionDisciplines")
        soup = BeautifulSoup(r.text, 'html.parser')
        try:
            text = soup.body.get_text(strip=True)
            if text == "Check your browser. Please, wait!": return [False,"Failed Auth"]
        except: pass
        lessons = soup.find_all('div', class_='discipline-block')
        new_teachers = []
        for lesson in lessons:
            lesson_div_name = lesson.find('div', class_='creature-heading')
            lesson_name = lesson_div_name.find('h1')

            lesson_div_teachers = lesson.find('div', class_='property-block')
            lessons_mass = []
            for heading in lesson_div_teachers.find_all('h4'):
                title = heading.text.strip()
                next_p = heading.find_next('p')
                link = next_p.find('a')
                name = link.text.strip()
                href = "https://idis.ieml.ru" + link['href']
                lessons_mass.append({"title": title, "teacher": name, "href": href})
            new_teachers.append({"name": lesson_name.text.strip(), "lessons":lessons_mass})
        
        with open('data.json', 'r+', encoding='utf-8') as file:
            data = json.load(file)
            data["Teachers"]["teachers"] = new_teachers
            data["Teachers"]["last"] = datetime.datetime.now().strftime("%d/%m/%Y, %H:%M:%S")
            file.seek(0)
            json.dump(data, file, ensure_ascii=False, indent=4)
            file.truncate()
    except Exception as err:
        return [False, err]
    return [True,"Succes"]

def get_last_teachers() -> dict:
    with open('data.json', 'r', encoding='utf-8') as file:
        data = json.load(file)
    teachers_array = data["Teachers"]
    return teachers_array

def get_schedule(start:datetime.datetime,end:datetime.datetime):
    try:
        today = datetime.datetime.now()
        date1 = start.strftime("%d.%m.%Y")
        date2 = end.strftime("%d.%m.%Y")
        r = session.get(f"https://idis.ieml.ru/Education/protected/student-cabinet/GenerateScheduleLessons?par_begindate={date1}&par_enddate={date2}")
        soup = BeautifulSoup(r.text, 'html.parser')
        try:
            text = soup.body.get_text(strip=True)
            if text == "Check your browser. Please, wait!": return [False,"Failed Auth"]
        except: pass
        lessons = soup.find_all('div', class_='daily-box-wrapper')
        new_schedule = [] 
        for lesson in lessons:
            lesson_time = lesson.find('span', class_='sub-time')
            lesson_date = lesson.find_all('p', class_='box-content-header')
            total_date = {"date": lesson_date[0].text.strip(),"week": lesson_date[1].text.strip()}
            lesson_place = lesson.find_all('p', class_='box-content-subheader')
            total_place = {"address": lesson_place[0].text.strip(),"audience": lesson_place[1].text.strip()}
            lesson_name = lesson.find('p', class_='disc-inf-header')
            teacher = lesson.find('p', class_='disc-inf-bottom')
            div_comment = lesson.find('div', class_='comment-popup')
            if div_comment is None: comment = "<b>Не указано.</b>"
            else: comment = div_comment.text.strip()
            new_schedule.append({"name": lesson_name.text.strip(), "time": lesson_time.text.strip(), "date": total_date, "place": total_place, "comment":comment , "teacher": teacher.text.strip()})
        existing_dates = {lesson['date']['date'] for lesson in new_schedule}

        for n in range((end - start).days + 1):
            current_date = start + datetime.timedelta(days=n)
            if current_date.strftime("%d.%m.%Y") not in existing_dates:
                new_schedule.append({
                    "name": "Нету пар",
                    "date": {"date": current_date.strftime("%d.%m.%Y")}
                })
        
        with open('data.json', 'r+', encoding='utf-8') as file:
            data = json.load(file)
            data["Schedule"]["lessons"] = new_schedule
            data["Schedule"]["last"] = datetime.datetime.now().strftime("%d/%m/%Y, %H:%M:%S")
            file.seek(0)
            json.dump(data, file, ensure_ascii=False, indent=4)
            file.truncate()
    except Exception as err:
        return [False, err]
    return [True,"Succes"]

def get_last_schedule(date1:str,date2:str):
    with open('data.json', 'r', encoding='utf-8') as file:
        data = json.load(file)
    schedule_list = data["Schedule"]['lessons']
    schedule = []
    start_date = datetime.datetime.strptime(date1, "%d.%m.%Y")
    end_date = datetime.datetime.strptime(date2, "%d.%m.%Y")
    dates = []
    for n in range((end_date - start_date).days + 1):
        dates.append((start_date + datetime.timedelta(days=n)).strftime("%d.%m.%Y"))

    for lesson in schedule_list:
        if lesson["date"]["date"] in dates:
            schedule.append(lesson)
    if schedule == []:
        return [False, "Not Info"]
    return [True, schedule, data["Schedule"]["last"]]

def update_all() -> list:
    try:
        status = []
        today = datetime.datetime.now()
        first_date_of_week = today - datetime.timedelta(days=today.weekday())
        last_date_of_next_week = first_date_of_week + datetime.timedelta(weeks=2) - datetime.timedelta(days=1)
        response = get_teachers()
        status.append({"name": "get_teachers №1", "status": response})
        if response[1] == "Failed Auth":
            response1 = update_cookie()
            status.append({"name": "update_cookie №1", "status": response1})
            if not response1[0]:
                return [False,response1]
            response2 = get_teachers()
            status.append({"name": "get_teachers №2", "status": response2})
        response1 = get_schedule(first_date_of_week,last_date_of_next_week)
        status.append({"name": "get_schedule №1", "status": response1})
        return [True,status]
    except Exception as err:
        return [False,err]