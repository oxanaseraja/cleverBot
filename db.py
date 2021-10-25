import sqlite3

class BotDB:

    def __init__(self, db_file):
        self.conn = sqlite3.connect(db_file, check_same_thread=False)
        self.cursor = self.conn.cursor()

    def user_exists(self, user_id):
        """Проверяем, есть ли юзер в базе"""
        result = self.cursor.execute("SELECT `id` FROM `users` WHERE `user_id` = ?", (user_id,))
        return bool(len(result.fetchall()))

    def get_user_id(self, user_id):
        """Достаем id юзера в базе по его user_id"""
        result = self.cursor.execute("SELECT `id` FROM `users` WHERE `user_id` = ?", (user_id,))
        return result.fetchone()[0]

    def add_user(self, user_id):
        """Добавляем юзера в базу"""
        self.cursor.execute("INSERT INTO `users` (`user_id`) VALUES (?)", (user_id,))
        return self.conn.commit()

    def add_record(self, user_id, request, result):
        """Создаем запись о поиске"""
        self.cursor.execute("INSERT INTO `results` (`user_id`, `request`, `result`) VALUES (?, ?, ?)",
            (self.get_user_id(user_id), request, result))
        return self.conn.commit()

    def get_records(self, user_id):
        """Получаем историю о поисках"""
        result = self.cursor.execute("SELECT * FROM `results` WHERE `user_id` = ? ORDER BY `date`",
            (self.get_user_id(user_id),))
        return result.fetchall()

    def close(self):
        """Закрываем соединение с БД"""
        self.connection.close()