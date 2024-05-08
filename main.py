import psycopg2
import configparser
import time
from contextlib import closing

def connect_db():
    config = configparser.ConfigParser()
    config.read('db_config.ini')
    db_params = config['postgresql']
    conn = psycopg2.connect(**db_params)
    return conn

def timed(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        print(f"{func.__name__} выполнена за {end_time - start_time:.6f} секунд")
        return result
    return wrapper

@timed
def create_user(conn, name, email):
    with closing(conn.cursor()) as cursor:
        cursor.execute("INSERT INTO users (name, email) VALUES (%s, %s) RETURNING id;", (name, email))
        user_id = cursor.fetchone()[0]
        conn.commit()
        return user_id

@timed
def read_user(conn, user_id):
    with closing(conn.cursor()) as cursor:
        cursor.execute("SELECT * FROM users WHERE id = %s;", (user_id,))
        user = cursor.fetchone()
        return user

@timed
def update_user(conn, user_id, name, email):
    with closing(conn.cursor()) as cursor:
        cursor.execute("UPDATE users SET name = %s, email = %s WHERE id = %s;", (name, email, user_id))
        conn.commit()

@timed
def delete_user(conn, user_id):
    with closing(conn.cursor()) as cursor:
        cursor.execute("DELETE FROM users WHERE id = %s;", (user_id,))
        conn.commit()

def main():
    try:
        conn = connect_db()
        print("Подключение к базе данных успешно выполнено.")
    except Exception as e:
        print(f"Не удалось подключиться к базе данных: {e}")
        return
    
    while True:
        print("\nВыберите действие:")
        print("1. Создать пользователя")
        print("2. Прочитать пользователя")
        print("3. Обновить пользователя")
        print("4. Удалить пользователя")
        print("5. Выйти")
        choice = input("Введите номер действия: ")

        if choice == '1':
            name = input("Введите имя: ")
            email = input("Введите email: ")
            user_id = create_user(conn, name, email)
            print(f"Пользователь создан с ID: {user_id}")
        elif choice == '2':
            user_id = int(input("Введите ID пользователя: "))
            user = read_user(conn, user_id)
            print(f"Пользователь: {user}")
        elif choice == '3':
            user_id = int(input("Введите ID пользователя: "))
            name = input("Введите новое имя: ")
            email = input("Введите новый email: ")
            update_user(conn, user_id, name, email)
            print("Пользователь обновлен.")
        elif choice == '4':
            user_id = int(input("Введите ID пользователя: "))
            delete_user(conn, user_id)
            print("Пользователь удален.")
        elif choice == '5':
            print("Выход из программы.")
            break
        else:
            print("Неверный ввод, попробуйте снова.")

    conn.close()

if __name__ == "__main__":
    main()
