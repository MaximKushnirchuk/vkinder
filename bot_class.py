import json
from pprint import pprint
import re
import datetime
import random

import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from sql_fuctions import add_favorites_sql


class Bot:
    def __init__(self):
        # вставить токен сообщества
        token_group = 'vk1.a.prD5LF1FSiTOrG9P9265qr5vm3IP0eeLPXlWmjXVxRvvefVarea5CakA1J-Jp6gKtlXlLoEuj5RhxBgmtqMnPdUm-BiwyZQFRU_Sx3Say9iVNcRw-vBd0ZTfAMDaMsImGK_WFl3bIY9mIbF29N12ab6WXK0DvGmII6VBywwpIhg9oYZSWUk44MAuxglktbREu5FZaCfEQVf1lrZzjjLN_w'  
        # вставить токен пользователя
        token_user = 'vk1.a.0cMQCyYtTDNB3mVGCWkt-aTBmh-qO1XRPXfPz2owx8as0T5qZHVYLX7hazp4pto5GbYhUby2A1L_LS6qiy9uBIsmxn0pffCkoVHFL9vPbSY02iSB-bUxAZ0uHjeaRaf1h3zsnXpj86DKV2wrK1HEHgd2stJabIWNOT4tQT7hvV3rDXAgC5O_obzcthm34l0HYH5qqt3fwAOpYYipPyDhVA'  
        self.vk = vk_api.VkApi(token=token_group)
        self.vku = vk_api.VkApi(token=token_user)
        self.longpoll = VkLongPoll(self.vk)
        self.vk_id = False
        self.first_name = ''
        self.last_name = ''
        self.sex = ''
        self.bdate = False
        self.age = False
        self.city = ''
        self.city_id = ''
        self.min_age = ''
        self.max_age = ''



    def listen(self):
        for event in self.longpoll.listen():
            if  event.type == VkEventType.USER_TYPING or event.type == VkEventType.USER_TYPING_IN_CHAT:
                self.vk_id = event.user_id
                print(event.raw)
                self.__about_user_vk()
                self.__determine_age()
                if self.age < 18:
                    self.__send_mess('Извините, Ваш возраст не походит для использования приложения, будем рады видеть Вас позже :)', False, False)
                    self.listen()
                keyboard = VkKeyboard(inline=True)
                keyboard.add_button(label='ДА', color=VkKeyboardColor.POSITIVE, payload={'Value': 1})
                keyboard.add_button(label='НЕТ', color=VkKeyboardColor.NEGATIVE, payload={'Value': 2})
                keyboard.add_button(label='МОЕ ИЗБРАННОЕ', color=VkKeyboardColor.POSITIVE, payload={'Value': 3})
                self.__send_mess(f'Привет {self.first_name}! Начнем поиск половинки?', False, keyboard)
                break
        flag = self.__keyboard_message(keyboard)         
        if flag == 1:
            self.__set_ages()
            self.search_users()
        elif flag == 2:
            self.__send_mess('До свидания, будем рады видеть Вас снова', False, False)
            return
        elif flag == 3:
            self.__send_mess('Избранное', False, False)
            self.__favorites()
            return

    def __keyboard_message(self, keyboard):
        for event in self.longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me: 
                flag = False
                try:
                    flag = json.loads(event.raw[6]['payload'])['Value']
                    break
                except:
                    self.__send_mess('Что-то пошло не так, попробуйте снова :)', False, keyboard)
                    pass
        return flag

    def __set_ages(self):
        keyboard = VkKeyboard(inline=True)
        keyboard.add_button(label='Моего возраста (+/- 1 год)', color=VkKeyboardColor.PRIMARY, payload={'Value': 1})
        keyboard.add_button(label='Задать вручную', color=VkKeyboardColor.PRIMARY, payload={'Value': 2})
        self.__send_mess('Определитесь с искомым возрастом :)', False, keyboard)  
        flag = self.__keyboard_message(keyboard)       
        if flag == 1:
            self.min_age = self.age - 1
            self.max_age = self.age + 1
            # self.__send_mess(f'{self.min_age} - {self.age} - {self.max_age}')  
        elif flag == 2:   
            self.__send_mess('Введите минимальный возраст второй половинки (min 18, max 100):', False, False)
            for event in self.longpoll.listen():
                if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                    try:
                        min_age = int(event.text)
                        assert 17 < min_age < 101
                        break
                    except:
                        self.__send_mess('Вы ввели некорретное значение минимального возраста, повторите ввод: ', False, False)
                        continue

            self.__send_mess('Введите максимальный возраст второй половинки (min 18, max 100):', False, False)
            for event in self.longpoll.listen():
                if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                    try:
                        max_age = int(event.text)
                        assert (17 < max_age < 101) and (min_age <= max_age)
                        break
                    except:
                        self.__send_mess('Вы ввели некорретное значение максимального возраста, повторите ввод: ', False, False)
                        continue
            
            self.min_age = min_age
            self.max_age = max_age

    def __send_mess(self, message, attachment = False, keyboard = False):
        params = {
            'user_id': self.vk_id,
            'random_id' : random.randrange(10**6),
            'message': message,
            'v':'5.150'
        }
        if keyboard:
            params['keyboard'] = keyboard.get_keyboard()
        else:
            keyboard = VkKeyboard()
            params['keyboard'] = keyboard.get_empty_keyboard()
        if attachment:
            params['attachment'] = attachment
        self.vk.method('messages.send', params)

    def __about_user_vk(self):
        params = {
            'user_ids': self.vk_id,
            'fields' : 'city,sex,bdate',
            'v':'5.150'
        }
        res = self.vk.method('users.get', params)
        if len(res) > 0:
            self.vk_id = res[0]['id']
            self.first_name = res[0]['first_name']
            self.last_name = res[0]['last_name']
            self.bdate = res[0]['bdate']   
            self.sex = res[0]['sex']
            self.city = res[0]['city']['title']
            self.city_id = res[0]['city']['id']     
            return True
        return False
    
    def __determine_age(self):
        pattern = re.compile(r'\.')
        list = pattern.split(self.bdate)
        m = int(list[1])
        d = int(list[0])
        if len(list) == 3:
            y = int(list[2])
        else:
            self.__send_mess('Введите год Вашего рождения (гггг):', False, False)
            for event in self.longpoll.listen():
                if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                    try:
                        y = int(event.text)
                        self.bdate += f'.{y}'
                        break
                    except:
                        self.__send_mess('Вы ввели некорретное значение своего возраста, повторите ввод: ', False, False)
                        continue
        birthday = datetime.date(y, m, d)
        today = datetime.date.today()
        years = (today.year-birthday.year)
        if birthday.month > today.month or (birthday.month == today.month and birthday.day > today.day):
            years -= 1
        self.age = years
    
    def auth_user(self):
        keyboard = VkKeyboard(inline=True)
        keyboard.add_openlink_button(label='Авторизовать', link='https://oauth.vk.com/authorize?client_id=51760260&display=page&redirect_uri=https://oauth.vk.com/blank.html&scope=friends,photos,status,offline&response_type=token&v=5.150&state=123456', payload=None)
        self.__send_mess('Авторизуйте приложение:', False, keyboard)  


    def search_users(self):
        params = {
            'count' : 500, # кол-во результатов в выдаче
            'fields' : '',
            'city' : self.city_id,
            'city_id' : self.city_id,
            'sex' : 1 if self.sex == 2 else 2,
            'status' : {6}, # 1 - не женат/замужем, 6 - в активном поиске
            'age_from' : self.min_age,
            'age_to' : self.max_age,
            'has_photo' : 1,
            'fields' : 'city,sex,bdate',
            # 'offset' : 100, # смещение по выборке
            'v':'5.150'
        }
        res = self.vku.method('users.search', params)
        # print('count ', res['count'])
        # print(len(res['items']))
        i = len(res['items']) - 1
        while i >= 0:
            if res['items'][i]["is_closed"] == True:
                del res['items'][i]
            i -= 1
        # print(len(res['items']))
        # y = json.dumps(res).encode( 'ascii' ).decode( 'unicode-escape' )
        # with open("1.txt", encoding='utf-8', mode="w") as file:
        #     file.write(y)
        self.__show_users(res['items'])

    def __show_users(self, user_list):
        index = 0        
        while True:
            attach = ''
            params = {
                'owner_id': user_list[index]["id"],
                'album_id' : 'profile',
                'extended' : 1,
                # 'count' : 5,
                'v':'5.150'
            }
            res = self.vku.method('photos.get', params)
            photos = self.__find_photos(res)
            # pprint(photos)
            keyboard = VkKeyboard(inline=True)
            if index != 0:
                keyboard.add_button(label='НАЗАД', color=VkKeyboardColor.PRIMARY, payload={'Value': 0})
            if index < len(user_list) - 1:    
                keyboard.add_button(label='ВПЕРЕД', color=VkKeyboardColor.PRIMARY, payload={'Value': 1})
            keyboard.add_button(label='В ИЗБРАННОЕ', color=VkKeyboardColor.POSITIVE , payload={'Value': 2})
            keyboard.add_button(label='ВЫХОД', color=VkKeyboardColor.NEGATIVE, payload={'Value': 3})
            user = f'{user_list[index]["first_name"]} {user_list[index]["last_name"]}\nhttps://vk.com/id{user_list[index]["id"]}'
            for photo in photos:
                attach += f'photo{user_list[index]["id"]}_{photo["id"]},'
            attach = attach.rstrip(',')
            self.__send_mess(user, attach, keyboard)
            flag = self.__keyboard_message(keyboard)
            if flag == 0:
                index -= 1
            elif flag == 1:
                index += 1
            elif flag == 2:
                self.__add_favorites(user_list[index], photos)
            elif flag == 3:
                self.__send_mess('До свидания, будем рады видеть Вас снова', False, False)
                return

    def __find_photos(self, photos):
        likes = []
        url_photos = []
        for like in photos['items']:
            likes.append(int(like['likes']['count']))
        likes.sort(reverse=True)
        likes = likes[:3]

        for photo in photos['items']:
            if int(photo['likes']['count']) in likes:
                 url_photos.append({
                    'id' : photo['id'],
                    'likes' : int(photo['likes']['count']),
                     })               
        return url_photos
    
 
    def __add_favorites(self, user, photos):
        add_favorites_sql(
            id_user= self.vk_id,
            user_name= self.first_name,
            user_surname= self.last_name,
            id_favorite= user['id'],
            favorite_name= user['first_name'],
            favorite_surname= user['last_name'],
            photo_list= photos
        )

    def __favorites():
        pass


        



