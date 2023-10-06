'''   Создание таблиц  '''

'''Данный модуль создает четыре таблицы : photo, people, vk_user, favorites.
Для создания таблиц необходимо :
- создать базу данных с именем vk_tinder
- установить psycopg2
- в переменную your_password записать свой пароль от postgres
- вызвать функцию create_tables() '''

import psycopg2

your_password: str = '...'

def create_tables()-> None :
    '''функция создает три таблицы. Перед этим удаляет ранее созданные'''
    conn = psycopg2.connect(host='localhost', database='vk_tinder', user='postgres', password= your_password)

    with conn.cursor() as cur :

        cur.execute('''
        DROP TABLE IF EXISTS photo, favorites, people, vk_user; 
        
        CREATE TABLE vk_user (
                    id_user VARCHAR(30) PRIMARY KEY, 
                    first_name VARCHAR(30) NOT NULL, 
                    last_name VARCHAR(30));
                     
        CREATE TABLE people (
                    id_favorite VARCHAR(30) PRIMARY KEY,
                    first_name VARCHAR(30) NOT NULL,
                    last_name VARCHAR(30));

        CREATE TABLE favorites (
            id_user VARCHAR(30) NOT NULL REFERENCES vk_user(id_user),
            id_favorite VARCHAR(30) NOT NULL REFERENCES people(id_favorite),
            CONSTRAINT pk PRIMARY KEY (id_user, id_favorite)
            );

        CREATE TABLE IF NOT EXISTS photo (
                    id_photo SERIAL PRIMARY KEY,
                    id_favorite VARCHAR(30) NOT NULL REFERENCES people(id_favorite),
                    id_vk_photo VARCHAR(70) NOT NULL);''')
    
        conn.commit()
    print('Созданы таблицы photo, favorites, vk_user, people')
    conn.close()

create_tables()