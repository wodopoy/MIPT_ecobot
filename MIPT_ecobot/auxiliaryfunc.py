import dbworker
from math import sqrt, pow

#функция для поиска наилучшего адреса (по формуле средневзвешенного)
def determine_the_best_position(applied_chatids):
    x_dividend = 0
    y_dividend = 0
    weight_divider = 0
    if len(applied_chatids) == 0:
        x = 'no x'
        y = 'no y'
        return x, y
    for i in range(len(applied_chatids)):
        output = dbworker.get_user_pos_and_trash_weight(chat_id = applied_chatids[i])
        if output == 'none':
            pass
        else:
            x_dividend += output['x'] * output['trash_weight']
            y_dividend += output['y'] * output['trash_weight']
            weight_divider += output['trash_weight']

    if weight_divider == 0:
        x = 'no x'
        y = 'no y'
        return x, y

    x = x_dividend / weight_divider
    y = y_dividend / weight_divider
    return x, y
    
#функция для поиска наилучшего дня     
def best_day(user_dict):
    days = dict()
    best_days = {
        'Понедельник': 0,
        'Вторник': 0,
        'Среда': 0,
        'Четверг': 0,
        'Пятница': 0,
        'Суббота': 0,
        'Воскресенье': 0,
    }


    #проходимся по кортежу в первый раз и создаем в словарике нулевые значения веса мусора в соотвествии chat id из user_dict
    for key in user_dict:
        days[key] = {}
        for i in range(len(user_dict[key])):
            days[key][user_dict[key][i]] = 0

    #проходимся во второй раз и суммируем для каждого дня вес мусора
    for key in user_dict:
        for i in range(len(user_dict[key])):
            out = dbworker.get_trash_weight(chat_id = key)
            if out == 'none':
                pass
            else: 
                days[key][user_dict[key][i]] += out
    
    #суммируем все веса для каждого отдельного дня 
    for key in user_dict:
        for i in range(len(user_dict[key])):
            best_days[user_dict[key][i]] += days[key][user_dict[key][i]]

    #находим ключ(название дня недели) с максимальным весом мусора
    final_dict = dict([max(best_days.items(), key=lambda k_v: k_v[1])])
        
    for key in final_dict:
        best_day = key
    
    return best_day

#Это вспомогательная функция, где мы из кортежа соотвествий юзер чат айди/дни, которые он добавил возвращаем массив с чат айдишниками в вхождении лучшего дня
#user_dict такого вида: {406149871: ['Понедельник', 'Среда', 'Пятница'], 1943316717: ['Понедельник', 'Среда', 'Суббота']}

def chatids_with_best_day_match(user_dict, best_day: str):
    applied_chatids = []
    for key in user_dict:
        if best_day in user_dict[key]:
            applied_chatids.append(key)
    return applied_chatids

#Функция поиска ближайшего адреса из юзеров, у которых есть вхождение в лучший день, к лучшей координате
#получаем наименьшее расстояние и его чайт айди. делаем запрос к бд по чат айди и она возвращает его адрес
def nearest_address(applied_chatids, x: float, y: float):
    best_distance = 100000000
    chat_id = 0
    for i in range(len(applied_chatids)):
        output = dbworker.get_user_pos_and_trash_weight(chat_id = applied_chatids[i])
        distance = sqrt( pow(x - output['x'],2) + pow(y - output['y'],2))

        if distance < best_distance:
            chat_id = applied_chatids[i]
            best_distance = distance

    nearest_address = dbworker.get_user_address(chat_id = chat_id)

    return nearest_address
        

# print(nearest_address(applied_chatids = [406149871, 1943316717], x = 55.73957181818182, y = 37.50369554545455))
# [406149871, 1943316717]
# print(chatids_with_best_day_match(user_dict = {406149871: ['Понедельник', 'Среда', 'Пятница'], 1943316717: ['Понедельник', 'Среда', 'Суббота']}, best_day = 'Понедельник'))
# print(kek(user_dict = {406149871: ['Понедельник', 'Среда', 'Пятница'], 1943316717: ['Понедельник', 'Среда', 'Суббота'], 123123123: ['Среда', 'Суббота']}))
# print(determine_the_best_position(applied_chatids = [406149871, 1943316717]))