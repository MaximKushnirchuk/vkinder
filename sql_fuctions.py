''' Данный модуль содержит функции :

add_favorites_sql - данная функция вызывается в методе __add_favorites. Она вносит данные в базу данных

search_favorites - данная функция возвращает список избранных пользователей.

Для работы необходимо :
- установить psycopg2
- в переменную your_password записать свой пароль от postgres
'''

import psycopg2
from pprint import pprint

your_password: str = '...'


def add_favorites_sql(id_user: str, user_name: str, user_surname: str, id_favorite: str, favorite_name: str, favorite_surname: str, photo_list: list)-> None :
    '''Функция добаляет пользователя в таблицу vk_user, вносит человека в таблицу people, заполняет таблицу photo, заполняет таблицу favorites'''
    print()
    print('Работает функция  add_favorites_sql')
    conn = psycopg2.connect(host = 'localhost', database = 'vk_tinder', user = 'postgres', password = your_password)
    with conn.cursor() as cur :
        # прорверяем и вносим пользователя в vk_user 
        try :
            cur.execute('''INSERT INTO vk_user(id_user, first_name, last_name)
                            VALUES (%s, %s, %s);''', (id_user, user_name, user_surname))
            print('В таблицу vk_user добавлен юзер: ', user_name, user_surname)
        except : 
            print('Такой юзер уже есть : ', user_name, user_surname)
            pass
        conn.commit()    
            
        # прорверяем и вносим пользователя в people и photo
        try :
            cur.execute('''INSERT INTO people(id_favorite, first_name, last_name)
                            VALUES (%s, %s, %s);''', (id_favorite, favorite_name, favorite_surname))

            print('В таблицу people добавлен человек: ', favorite_name, favorite_surname)

            for dict_photo in photo_list :
                    cur.execute('''INSERT INTO photo(id_favorite, id_vk_photo)
                                        VALUES (%s, %s);''', (id_favorite, dict_photo['id']))

                    print('В таблицу photo добавлен фотграфии: ', dict_photo['id'])
        except : 
            print('Такой человек и фотографии уже есть : ', favorite_name, favorite_surname)
            pass
        conn.commit()    
        
        # добавляем в таблицу favorites
        try :
            cur.execute('''INSERT INTO favorites (id_user, id_favorite)
                            VALUES (%s, %s);''', (id_user, id_favorite))

            print('В таблицу favorites (Избранное) для  Юзера : ', user_name, user_surname, '  добавлен человек: ', favorite_name, favorite_surname)
        except : 
            print('У Юзера : ', user_name, user_surname,' В избранном уже есть человек  : ', favorite_name, favorite_surname)
            pass
        conn.commit()  

        conn.commit()    
    conn.close()


def search_favorites(id_user: str)-> None :
    '''Функция принимает на вход один аргумент : id_user
    И возвращает список избранных этого пользователя в формате :
    [
        {
            'id_favorite': '997676423',
            'first_name': 'Elena',
            'last_name': 'Poleno',
            'photo': ['457239020', '457239108', '457239122']
        },
        ...
    ]
    '''
    res_dic = dict()
    conn = psycopg2.connect(host='localhost', database='vk_tinder', user='postgres', password= your_password)
    with conn.cursor() as cur :
        cur.execute('''SELECT p.id_favorite, first_name, last_name, id_vk_photo
                        FROM  people p 
                        JOIN favorites f  
                          ON p.id_favorite  = f.id_favorite
                        JOIN photo ph
                          ON p.id_favorite = ph.id_favorite 
                       WHERE f.id_user = %s;''', (id_user,))

        data = cur.fetchall()        
        for man in  data:
            if man[0] not in res_dic :
                res_dic[man[0]] = {
                    'id_favorite' : man[0],
                    'first_name' : man[1],
                    'last_name' : man[2],
                    'photo' : [man[3]]
                }
            else : res_dic[man[0]]['photo'].append(man[3])
        res = [i for i in res_dic.values()]

    cur.close()
    return res




# favorites_list = search_favorites(...)
# pprint(favorites_list)