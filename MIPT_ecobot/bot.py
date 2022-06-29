import os, re
import telebot
import dbworker
import yandexmap
import auxiliaryfunc as af
from telebot import types
from dotenv import load_dotenv

config = load_dotenv()
bot = telebot.TeleBot(os.getenv("tgapikey"))

user_dict = dict()
day_dict = dict()

#декоратор телебота для обработки команд. возвращает экземпляр message который пойдет в арг функции
@bot.message_handler(commands=['start', 'menu'])
def menu(message):
    try:
        if message.text == '/start':
            user_dict[message.chat.id] = []
            print(user_dict)
            day_dict[message.chat.id] = {'Monday': True, 'Tuesday': True, 'Wednesday': True,
            'Thursday': True, 'Friday': True, 'Saturday': True, 'Sunday': True}
            print(day_dict)
            user_dict[message.chat.id].append('Понедельник')
            user_dict[message.chat.id].append('Вторник')
            user_dict[message.chat.id].append('Среда')
            user_dict[message.chat.id].append('Четверг')
            user_dict[message.chat.id].append('Пятница')
            user_dict[message.chat.id].append('Суббота')
            user_dict[message.chat.id].append('Воскресенье')

        obj = dbworker.init_user(chat_id = message.chat.id)
        print(obj)

        #создание внутренней тг клавиатуры, инлайн кнопки - добавить call-back
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        itembtn1 = types.KeyboardButton('/add_convenient_day')
        itembtn2 = types.KeyboardButton('/set_address')
        itembtn3 = types.KeyboardButton('/enter_trash_weight')
        itembtn4 = types.KeyboardButton('/profile')
        markup.add(itembtn1,itembtn2,itembtn3,itembtn4)

        bot.reply_to(message, "start", reply_markup = markup, parse_mode='MARKDOWN')

    except Exception as e:
        bot.reply_to(message, f'smth go wrong: {e}')
        

@bot.message_handler(commands=['set_address'])
def set_address(message):
    try:
        markup = types.ReplyKeyboardRemove(selective=False)

        msg = bot.send_message(message.chat.id, "Введите ваш адрес", reply_markup=markup, parse_mode='MARKDOWN')
        bot.register_next_step_handler(msg, set_coordinates)

    except Exception as e:
        bot.reply_to(message, f'smth go wrong: {e}')

def set_coordinates(message):
    pos = yandexmap.geo_decoder(address = message.text)
    
    if pos == 'error':

        msg = bot.send_message(message.chat.id, "Упс:( Мы не можем распознать ваш адрес, попробуйте еще раз...", parse_mode='MARKDOWN')
        bot.register_next_step_handler(msg, set_coordinates)

    else: 
        obj = dbworker.set_position(chat_id = message.chat.id, address = message.text, x = pos['x'], y = pos['y'])

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        itembtn1 = types.KeyboardButton('/add_convenient_day')
        itembtn2 = types.KeyboardButton('/set_address')
        itembtn3 = types.KeyboardButton('/enter_trash_weight')
        itembtn4 = types.KeyboardButton('/profile')
        markup.add(itembtn1,itembtn2,itembtn3,itembtn4)
        
        bot.send_message(message.chat.id, f"Ура, вы указали адресс {obj.address}\n\nВаши координаты: {obj.x} {obj.y}", reply_markup=markup, parse_mode='MARKDOWN')

@bot.message_handler(commands=['enter_trash_weight'])
def enter_trash_weight(message):
    try:
        markup = types.ReplyKeyboardRemove(selective=False)

        msg = bot.send_message(message.chat.id, "Введите вес мусора [в (кг)]", reply_markup=markup, parse_mode='MARKDOWN')
        bot.register_next_step_handler(msg, set_trash_weight)

    except Exception as e:
        bot.reply_to(message, f'smth go wrong: {e}')

def set_trash_weight(message):
    trash_weight = message.text.replace(',', '.')
    obj = dbworker.set_trash_weight(chat_id = message.chat.id, trash_weight = float(trash_weight))

    if obj == 'error':
        msg = bot.send_message(message.chat.id, "Упс;( Вы указали вес мусора 0кг или даже меньше!!! Вы очень экологичны;)\n\nВведите вес мусора еще раз!", parse_mode='MARKDOWN')
        bot.register_next_step_handler(msg, set_trash_weight)

    else: 
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        itembtn1 = types.KeyboardButton('/add_convenient_day')
        itembtn2 = types.KeyboardButton('/set_address')
        itembtn3 = types.KeyboardButton('/enter_trash_weight')
        itembtn4 = types.KeyboardButton('/profile')
        markup.add(itembtn1,itembtn2,itembtn3,itembtn4)

        bot.send_message(message.chat.id, f"Вы указали {obj.trash_weight} кг мусора!", reply_markup=markup, parse_mode='MARKDOWN')

@bot.message_handler(commands=['admin'])
def admin(message):
    try:
        markup = types.ReplyKeyboardRemove(selective=False)

        msg = bot.send_message(message.chat.id, "Введите пароль", reply_markup=markup, parse_mode='MARKDOWN')
        bot.register_next_step_handler(msg, admin_panel)

    except Exception as e:
        bot.reply_to(message, f'smth go wrong: {e}')

@bot.message_handler(commands=['profile'])
def profile(message):
    try:

        address = dbworker.get_user_address(chat_id = message.chat.id)
        if address == 'none':
            address = 'Вы не указали адрес'
        trash_weight = dbworker.get_trash_weight(chat_id = message.chat.id)
        if trash_weight == 'none':
            trash_weight = 'Вы не указали вес мусора'

        if len(user_dict[message.chat.id]) == 0:
            days = 'Вы не указали удобные дни'
            
        else:
            days = ''
            for i in range(len(user_dict[message.chat.id])):
                days += user_dict[message.chat.id][i]+', '

        msg = f'*Профиль*\n\nАдрес: {address}\nВес мусора: {trash_weight}\nУдобные дни: {days}'

        bot.send_message(message.chat.id, msg, parse_mode='MARKDOWN')
        

    except Exception as e:
        bot.reply_to(message, f'smth go wrong: {e}')

#создание кнопок админа
def admin_panel(message):
    try:
        
        if message.text == '1234':
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
            itembtn1 = types.KeyboardButton('/send_best_position')
            markup.add(itembtn1)

            bot.send_message(message.chat.id, "у нашего админа самые лучшие анекдоты!", reply_markup=markup, parse_mode='MARKDOWN')

        else:
            msg = bot.send_message(message.chat.id, "Указан неверный пароль", parse_mode='MARKDOWN')
            
    except Exception as e:
        bot.reply_to(message, f'smth go wrong: {e}')

@bot.message_handler(commands=['send_best_position'])
def send_best_position(message):
    try:
        print(user_dict)
        best_day = af.best_day(user_dict)
        print(best_day)
        chat_ids = af.chatids_with_best_day_match(user_dict = user_dict, best_day = best_day)
        print(chat_ids)
        x, y = af.determine_the_best_position(applied_chatids = chat_ids)

        if x == 'no x': 
            bot.reply_to(message, f'Никто не указал вес мусора или удобный день')
        else:
                best_address = yandexmap.get_address_by_coordinates(x = x, y = y)
                nearest_address = af.nearest_address(applied_chatids = chat_ids, x = x, y = y)

                all_users_chatids = dbworker.get_users_chatids()

                msg=f'Наш супер пупер бот все посчитал демократическими алгоритмами!\n\nДень:{best_day}\nЛучший адрес(по нашему независимому мнению): {best_address} ({x}, {y})\nБлижайший адрес к лучшей точке из наших пользователей: {nearest_address}'

                for i in range(len(all_users_chatids)):
                    bot.send_message(all_users_chatids[i], msg, parse_mode='MARKDOWN')
                    bot.send_message(all_users_chatids[i], 'Лучший адрес', parse_mode='MARKDOWN')
                    bot.send_location(all_users_chatids[i], x, y)


    except Exception as e:
        bot.reply_to(message, f'smth go wrong: {e}')
        print(e)

@bot.message_handler(commands=['cleardb'])
def cleardb(message):
    output = dbworker.clearDB()
    bot.send_message(message.chat.id, output, parse_mode='MARKDOWN')

@bot.message_handler(commands=['add_convenient_day'])
def add_convenient_day(message):
    try:
        markup_inline = types.InlineKeyboardMarkup(row_width=1)

        monday = types.InlineKeyboardButton(text = 'Понедельник', callback_data = 'Monday')
        tuesday = types.InlineKeyboardButton(text = 'Вторник', callback_data = 'Tuesday')
        wednesday = types.InlineKeyboardButton(text = 'Среда', callback_data = 'Wednesday')
        thursday = types.InlineKeyboardButton(text = 'Четверг', callback_data = 'Thursday')
        friday = types.InlineKeyboardButton(text = 'Пятница', callback_data = 'Friday')
        saturday = types.InlineKeyboardButton(text = 'Суббота', callback_data = 'Saturday')
        sunday = types.InlineKeyboardButton(text = 'Воскресенье', callback_data = 'Sunday')
        update = types.InlineKeyboardButton(text = 'Обновить 🔄', callback_data = 'update')
        
        markup_inline.add(monday, tuesday, wednesday, thursday, friday, saturday, sunday,update)

        bot.send_message(message.chat.id, "Выберите удобные дни!", reply_markup=markup_inline, parse_mode='MARKDOWN')

    except Exception as e:
         bot.reply_to(message, f'smth go wrong: {e}')

@bot.callback_query_handler(func = lambda call:True)
def callback_handler(call):
    markup_inline = types.InlineKeyboardMarkup(row_width=1)

    monday = types.InlineKeyboardButton(text = 'Понедельник', callback_data = 'Monday')
    tuesday = types.InlineKeyboardButton(text = 'Вторник', callback_data = 'Tuesday')
    wednesday = types.InlineKeyboardButton(text = 'Среда', callback_data = 'Wednesday')
    thursday = types.InlineKeyboardButton(text = 'Четверг', callback_data = 'Thursday')
    friday = types.InlineKeyboardButton(text = 'Пятница', callback_data = 'Friday')
    saturday = types.InlineKeyboardButton(text = 'Суббота', callback_data = 'Saturday')
    sunday = types.InlineKeyboardButton(text = 'Воскресенье', callback_data = 'Sunday')
    update = types.InlineKeyboardButton(text = 'Обновить 🔄', callback_data = 'update')
    
    markup_inline.add(monday, tuesday, wednesday, thursday, friday, saturday, sunday,update)

    if call.data == 'update':
        if len(user_dict[call.from_user.id]) == 0:
            msg = 'Дни, в которые вы можете сдать мусор, лишние уберите:'
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=msg)
            bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=markup_inline)
            bot.answer_callback_query(call.id, text="updated!")
        else:
            msg = 'Дни, в которые вы можете сдать мусор, лишние уберите:\n\n'
            for i in range(len(user_dict[call.from_user.id])):
                msg += user_dict[call.from_user.id][i]+' ✅\n'

            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=msg)
            bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=markup_inline)
            bot.answer_callback_query(call.id, text="updated!")

    if call.data == 'Monday':

        day_dict[call.from_user.id]['Monday'] = not day_dict[call.from_user.id]['Monday']

        if day_dict[call.from_user.id]['Monday'] == True:
            user_dict[call.from_user.id].append('Понедельник')
            bot.answer_callback_query(call.id, text="Вы добавили: Понедельник")
        
        if day_dict[call.from_user.id]['Monday'] == False:
            user_dict[call.from_user.id].remove('Понедельник')
            bot.answer_callback_query(call.id, text="Вы убрали: Понедельник") 
    
    if call.data == 'Tuesday':

        day_dict[call.from_user.id]['Tuesday'] = not day_dict[call.from_user.id]['Tuesday']

        if day_dict[call.from_user.id]['Tuesday'] == True:
            user_dict[call.from_user.id].append('Вторник')
            bot.answer_callback_query(call.id, text="Вы добавили: Вторник")
        
        if day_dict[call.from_user.id]['Tuesday'] == False:
            user_dict[call.from_user.id].remove('Вторник')
            bot.answer_callback_query(call.id, text="Вы убрали: Вторник") 

    if call.data == 'Wednesday':

        day_dict[call.from_user.id]['Wednesday'] = not day_dict[call.from_user.id]['Wednesday']

        if day_dict[call.from_user.id]['Wednesday'] == True:
            user_dict[call.from_user.id].append('Среда')
            bot.answer_callback_query(call.id, text="Вы добавили: Среда")
        
        if day_dict[call.from_user.id]['Wednesday'] == False:
            user_dict[call.from_user.id].remove('Среда')
            bot.answer_callback_query(call.id, text="Вы убрали: Среда") 

    if call.data == 'Thursday':

        day_dict[call.from_user.id]['Thursday'] = not day_dict[call.from_user.id]['Thursday']

        if day_dict[call.from_user.id]['Thursday'] == True:
            user_dict[call.from_user.id].append('Четверг')
            bot.answer_callback_query(call.id, text="Вы добавили: Четверг")
        
        if day_dict[call.from_user.id]['Thursday'] == False:
            user_dict[call.from_user.id].remove('Четверг')
            bot.answer_callback_query(call.id, text="Вы убрали: Четверг") 

    if call.data == 'Friday':

        day_dict[call.from_user.id]['Friday'] = not day_dict[call.from_user.id]['Friday']

        if day_dict[call.from_user.id]['Friday'] == True:
            user_dict[call.from_user.id].append('Пятница')
            bot.answer_callback_query(call.id, text="Вы добавили: Пятница")
        
        if day_dict[call.from_user.id]['Friday'] == False:
            user_dict[call.from_user.id].remove('Пятница')
            bot.answer_callback_query(call.id, text="Вы убрали: Пятница") 

    if call.data == 'Saturday':

        day_dict[call.from_user.id]['Saturday'] = not day_dict[call.from_user.id]['Saturday']

        if day_dict[call.from_user.id]['Saturday'] == True:
            user_dict[call.from_user.id].append('Суббота')
            bot.answer_callback_query(call.id, text="Вы добавили: Суббота")
        
        if day_dict[call.from_user.id]['Saturday'] == False:
            user_dict[call.from_user.id].remove('Суббота')
            bot.answer_callback_query(call.id, text="Вы убрали: Суббота") 

    if call.data == 'Sunday':

        day_dict[call.from_user.id]['Sunday'] = not day_dict[call.from_user.id]['Sunday']

        if day_dict[call.from_user.id]['Sunday'] == True:
            user_dict[call.from_user.id].append('Воскресенье')
            bot.answer_callback_query(call.id, text="Вы добавили: Воскресенье")
        
        if day_dict[call.from_user.id]['Sunday'] == False:
            user_dict[call.from_user.id].remove('Воскресенье')
            bot.answer_callback_query(call.id, text="Вы убрали: Воскресенье")
    
if __name__ == "__main__":
    bot.polling(none_stop=True)
