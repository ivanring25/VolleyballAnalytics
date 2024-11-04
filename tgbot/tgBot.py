import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
import csv
import re
from collections import defaultdict, Counter
import os
import tempfile
import pandas as pd

API_TOKEN = ''
bot = telebot.TeleBot(API_TOKEN)

def is_valid_filename(filename):
        return re.match(r'^[\w,\s-]+\.[A-Za-z]{3}$', filename) is not None

def is_csv_file(filename):
    return filename.lower().endswith('.csv')

BASE_DIR = 'safe_directory/'  # Убедитесь, что эта директория существует

def safe_file_path(filename):
    return os.path.join(BASE_DIR, filename)

class BaseAction:
    def __init__(self, volleyball_action):
        self.volleyball_action = volleyball_action
        self.user_data = {}
    

    def _finish_action(self, chat_id, action):
        
        bot.send_message(chat_id, f"Сгенерированный шифр: {action}")
        self.user_data.pop(chat_id, None)

        markup = ReplyKeyboardMarkup(row_width = 3, resize_keyboard=True)
        buttons = ["1", "2" , "3", "4", "5", "6", "7", "8", "9", "0"]
        markup.add(*[KeyboardButton(text) for text in buttons])
        
        next_menu_message = ("Выберите действие, отправив номер:\n"
                              "1. Подача\n"
                              "2. Прием\n"
                              "3. Передача\n"
                              "4. Атака\n"
                              "5. Защита\n"
                              "6. Блок\n"
                              "7. Ошибка\n"
                              "8. Завершить розыгрыш\n"
                              "9. Сохранить игру\n"
                              "0. Аналитика")
        
        bot.send_message(chat_id, next_menu_message, reply_markup=markup)

class VolleyballAction:
    def __init__(self):
        self.data = []
        self.current_rally = []

    def generate_serve_action(self, player_number, zone, style, result):
        action = f"S{player_number}z{zone}{style}{result if result in ('#', '-') else ''}"
        self.current_rally.append(action)
        return action
    
    def generate_reception_action(self, quality, player_number):
        action = f"R{quality}n{player_number}"
        self.current_rally.append(action)
        return action
    
    def generate_attack_action(self, player_number, block_touch, zone, attack_type, quality):
        action = f"A{player_number}{block_touch}z{zone}{attack_type}{quality}"
        self.current_rally.append(action)
        return action
    
    def generate_block_action(self, player_number):
        action = f"B{player_number}"
        self.current_rally.append(action)
        return action
    
    def end_rally(self):
        if self.current_rally:
            rally = ",".join(self.current_rally)
            self.data.append(rally)
            self.current_rally = []
            return "Розыгрыш завершен и сохранен."
        return "Розыгрыш пустой."

    def save_to_csv(self, filename):
        
        with open(filename, mode='w', encoding='utf-8', newline='') as file:
            writer = csv.writer(file)
            for row in self.data:
                writer.writerow([row])

class ServeAction(BaseAction):
    def start(self, message):
        chat_id = message.chat.id
        self.user_data[chat_id] = {}
        
        bot.send_message(chat_id, "Введите номер игрока, подающего мяч:", reply_markup=ReplyKeyboardRemove())
        bot.register_next_step_handler(message, self.get_player_number)

    def get_player_number(self, message):
        chat_id = message.chat.id
        self.user_data[chat_id]['player_number'] = message.text.strip()

        markup = ReplyKeyboardMarkup(row_width=3, resize_keyboard=True)
        buttons = ["1", "6", "5", "2", "3", "4"]
        markup.add(*[KeyboardButton(text) for text in buttons])

        bot.send_message(chat_id, "Введите зону подачи (1-6):", reply_markup=markup)
        bot.register_next_step_handler(message, self.get_zone)

    def get_zone(self, message):
        chat_id = message.chat.id
        self.user_data[chat_id]['zone'] = message.text.strip()

        markup = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
        buttons = ["F", "P"]
        markup.add(*[KeyboardButton(text) for text in buttons])
        bot.send_message(chat_id, "Введите стиль подачи (F - силовая, P - планер):",reply_markup=markup)

        bot.register_next_step_handler(message, self.get_style)

    def get_style(self, message):
        chat_id = message.chat.id
        self.user_data[chat_id]['style'] = message.text.strip()

        markup = ReplyKeyboardMarkup(row_width=3, resize_keyboard=True)
        buttons = ["#", "-", "$"]
        markup.add(*[KeyboardButton(text) for text in buttons])

        bot.send_message(chat_id, "Введите результат подачи (# - очко, - - ошибка, $ - подача):", reply_markup=markup)
        bot.register_next_step_handler(message, self.get_result)

    def get_result(self, message):
        chat_id = message.chat.id
        self.user_data[chat_id]['result'] = message.text.strip()
        data = self.user_data[chat_id]
        action = self.volleyball_action.generate_serve_action(
            data['player_number'], data['zone'], data['style'], data['result']
        )


        self._finish_action(chat_id, action)
        
class ReceptionAction(BaseAction):

    def start(self, message):
        chat_id = message.chat.id
        self.user_data[chat_id] = {}
        markup = ReplyKeyboardMarkup(row_width=3, resize_keyboard=True)
        buttons = ["#", "+", "!", "-", "$"]
        markup.add(*[KeyboardButton(text) for text in buttons])
        bot.send_message(chat_id, "Введите качество приема (# - лучший, + - хороший, ! - средний, - - плохой, $ - ошибка):",reply_markup=markup)
        bot.register_next_step_handler(message, self.get_quality)

    def get_quality(self, message):
        chat_id = message.chat.id
        self.user_data[chat_id]['quality'] = message.text.strip()
        bot.send_message(chat_id, "Введите номер игрока, который совершал прием:", reply_markup=ReplyKeyboardRemove())
        bot.register_next_step_handler(message, self.get_player_number)

    def get_player_number(self, message):
        chat_id = message.chat.id
        self.user_data[chat_id]['player_number'] = message.text.strip()
        data = self.user_data[chat_id]
        action = self.volleyball_action.generate_reception_action(data['quality'], data['player_number'])

        
        self._finish_action(chat_id, action)
        
class AttackAction(BaseAction):

    def start(self, message):
        chat_id = message.chat.id
        self.user_data[chat_id] = {}
        bot.send_message(chat_id, "Введите номер атакующего игрока:", reply_markup=ReplyKeyboardRemove())
        bot.register_next_step_handler(message, self.get_player_number)

    def get_player_number(self, message):
        chat_id = message.chat.id
        self.user_data[chat_id]['player_number'] = message.text.strip()

        markup = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
        buttons = ["-", "+", "O", "E"]
        markup.add(*[KeyboardButton(text) for text in buttons])

        bot.send_message(chat_id, "Введите касание блока (- - без блока, + - было касание блока, O - блок аут, E - блок в пол):",reply_markup=markup)
        bot.register_next_step_handler(message, self.get_block_touch)

    def get_block_touch(self, message):
        chat_id = message.chat.id
        block_touch = message.text.strip()
        self.user_data[chat_id]['block_touch'] = block_touch

        # Если блок аута или блок в пол, завершаем сбор данных и создаем шифр
        if block_touch in ["O", "E"]:
            data = self.user_data[chat_id]
            action = self.volleyball_action.generate_attack_action(
                data['player_number'], block_touch, zone="0", attack_type="", quality=""
            )
            self._finish_action(chat_id, action)
        else:

            markup = ReplyKeyboardMarkup(row_width=3, resize_keyboard=True)
            buttons = ["1", "6", "5", "2", "3", "4"]
            markup.add(*[KeyboardButton(text) for text in buttons])

            bot.send_message(chat_id, "Введите зону атаки (1-6):",reply_markup=markup)
            bot.register_next_step_handler(message, self.get_zone)

    def get_zone(self, message):
        chat_id = message.chat.id
        self.user_data[chat_id]['zone'] = message.text.strip()

        markup = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
        buttons = ["F", "D"]
        markup.add(*[KeyboardButton(text) for text in buttons])

        bot.send_message(chat_id, "Введите тип атаки (F - удар, D - атака скидкой):",reply_markup=markup)
        bot.register_next_step_handler(message, self.get_attack_type)

    def get_attack_type(self, message):
        chat_id = message.chat.id
        self.user_data[chat_id]['attack_type'] = message.text.strip()

        markup = ReplyKeyboardMarkup(row_width=3, resize_keyboard=True)
        buttons = ["#", "-", "$"]
        markup.add(*[KeyboardButton(text) for text in buttons])

        bot.send_message(chat_id, "Введите качество атаки (# - идеальная, - - ошибка, $ - атаку подняли):",reply_markup=markup)
        bot.register_next_step_handler(message, self.get_quality)

    def get_quality(self, message):
        chat_id = message.chat.id
        self.user_data[chat_id]['quality'] = message.text.strip() if message.text.strip() in ("#", "-") else ""
        data = self.user_data[chat_id]
        action = self.volleyball_action.generate_attack_action(
            data['player_number'], data['block_touch'], data['zone'], data['attack_type'], data['quality']
        )
        self._finish_action(chat_id, action)

class BlockAction(BaseAction):
    def start(self, message):
        chat_id = message.chat.id
        self.user_data[chat_id] = {}
        bot.send_message(chat_id, "Номер игрока который совершил блок:",reply_markup=ReplyKeyboardRemove())
        bot.register_next_step_handler(message, self.get_player_number)
    
    def get_player_number(self, message):
        chat_id = message.chat.id
        self.user_data[chat_id]['player_number'] = message.text.strip()
        data = self.user_data[chat_id]
        action = self.volleyball_action.generate_block_action(data['player_number'])
        self._finish_action(chat_id, action)
        
class ErrorAction(BaseAction):

    def start(self, message):
        chat_id = message.chat.id
        self.user_data[chat_id] = {}
        bot.send_message(chat_id, "Номер игрока который совершил ошибку:")
        bot.register_next_step_handler(message, self.get_player_number)

    def get_player_number(self, message):
        chat_id = message.chat.id
        self.user_data[chat_id]['player_number'] = message.text.strip()
        bot.send_message(chat_id, "n - касание сетки, p - ошибка 2 передачи, l - заступ: ")
        bot.register_next_step_handler(message, self.get_type_error)
    
    def get_type_error(self, message):
        chat_id = message.chat.id
        self.user_data[chat_id]['type_error'] = message.text.strip()
        data = self.user_data[chat_id]
        action = self.volleyball_action.generate_block_action(data['player_number'], data['type_error'])
        self._finish_action(chat_id, action)

class VolleyballBot:
    def __init__(self):
        
        self.actions = VolleyballAction()

        self.serve_action = ServeAction(self.actions)
        self.reception_action = ReceptionAction(self.actions)
        self.attack_action = AttackAction(self.actions)
        self.block_action = BlockAction(self.actions)
        self.error_action = ErrorAction(self.actions)


    def handle_choice(self, message):
        choice = message.text.strip()

        if choice == '1':
            self.serve_action.start(message)
        elif choice == '2':
            self.reception_action.start(message)
        elif choice == '4':
            self.attack_action.start(message)
        elif choice == '6':
            self.block_action.start(message)
        elif choice == '7':
            self.error_action.start(message)
        elif choice == '8':
            result = self.actions.end_rally()
            bot.send_message(message.chat.id, result)
        elif choice == '9':
            bot.send_message(message.chat.id, "Введите имя файла для сохранения данных (например, game.csv):")
            bot.register_next_step_handler(message, self.process_filename)
        elif choice == '0':
            bot.send_message(message.chat.id, "Пришлите файл .csv")
            self.start_listening()
        else:
            bot.send_message(message.chat.id, "Неверный выбор. Пожалуйста, попробуйте снова.")

    
    def process_filename(self, message):
        filename = message.text.strip()

        # Проверка имени файла
        if not is_valid_filename(filename) or not is_csv_file(filename):
            bot.send_message(message.chat.id, "Неверное имя файла. Пожалуйста, используйте имя с расширением .csv.")
            return

        # Генерация безопасного пути к файлу
        safe_path = safe_file_path(filename)

        self.actions.save_to_csv(safe_path)
        bot.send_message(message.chat.id, f"Данные сохранены в файл {safe_path}")

        # Отправка файла пользователю
        try:
            with open(safe_path, 'rb') as file:
                bot.send_document(message.chat.id, file)
        except Exception as e:
            bot.send_message(message.chat.id, "Произошла ошибка при отправке файла.")

        # Удаление файла после отправки
        #os.remove(safe_path)

    def handle_csv_file(self, message):
        file_info = bot.get_file(message.document.file_id)
        downloaded_file = bot.download_file(file_info.file_path)

        # Временное имя загруженного файла
        input_filename = f'temp_{message.document.file_name}'
        with open(input_filename, 'wb') as new_file:
            new_file.write(downloaded_file)

        # Анализируем и получаем путь к выходному CSV
        analyzed_file = self.analyze_game_stats_from_csv(input_filename)

        # Отправляем проанализированный файл пользователю
        with open(analyzed_file, 'rb') as output_file:
            bot.send_document(message.chat.id, output_file)

        # Удаляем временные файлы
        os.remove(input_filename)
        os.remove(analyzed_file)

    def analyze_game_stats_from_csv(self, csv_file):
        # Загружаем CSV как текст
        with open(csv_file, 'r') as file:
            lines = file.readlines()

        # Инициализация структуры для хранения статистики
        player_stats = defaultdict(lambda: {
            "total_serves": 0,
            "won_serves": 0,
            "lost_serves": 0,
            "zone_count": Counter(),
            "serve_style": {"P": 0, "F": 0},
            "reception_quality": {"R#": 0, "R+": 0, "R!": 0, "R-": 0, "R$": 0},
            "total_receptions": 0,
            "reception_errors": 0,
            "good_reception_rate": 0.0,
            "best_reception_rate": 0.0,
            "total_attacks": 0,
            "won_attacks": 0,
            "attack_errors": 0,
            "attack_type_F": {"total": 0, "success": 0},
            "attack_success_rate_F": 0.0,
            "total_blocks": 0,
            "total_errors": 0,
            "total_points": 0,
            "total_points": 0,
            "total_errors": 0,
            "result": 0
        })

        # Регулярные выражения для парсинга шифров
        serve_pattern = r"S(\d{1,2})z(\d)([FP])([#-]?)"
        reception_pattern = r"R([#+!--$])n(\d{1,2})"
        attack_pattern = r"A(\d{1,2})([-+OTE]?)z(\d)([FD]?)([#-]?)"
        block_pattern = r"B(\d{1,2})"
        error_pattern = r"E(\d{1,2})([a-zA-Z]*)"

        for line in lines:
            events = line.strip('"').split(',')  # Удаляем пробелы и разделяем по запятой

            for entry in events:
                # Проверка, является ли шифр подачей
                serve_match = re.match(serve_pattern, entry)
                if serve_match:
                    player_num = int(serve_match.group(1))
                    zone = int(serve_match.group(2))
                    style = serve_match.group(3)
                    result = serve_match.group(4)

                    # Обновление статистики подачи
                    player_stats[player_num]["total_serves"] += 1
                    player_stats[player_num]["zone_count"][zone] += 1
                    player_stats[player_num]["serve_style"][style] += 1

                    if result == '#':
                        player_stats[player_num]["won_serves"] += 1
                    elif result == '-':
                        player_stats[player_num]["lost_serves"] += 1
                    continue
                
                # Проверка, является ли шифр приемом
                reception_match = re.match(reception_pattern, entry)
                if reception_match:
                    quality = reception_match.group(1)
                    player_num = int(reception_match.group(2))

                    # Обновление статистики приема
                    player_stats[player_num]["total_receptions"] += 1
                    if quality == "$":
                        player_stats[player_num]["reception_errors"] += 1

                    if f"R{quality}" in player_stats[player_num]["reception_quality"]:
                        player_stats[player_num]["reception_quality"][f"R{quality}"] += 1
                    continue

                # Проверка, является ли шифр атакой
                attack_match = re.match(attack_pattern, entry)
                if attack_match:
                    player_num = int(attack_match.group(1))
                    block_touch = attack_match.group(2)
                    zone = int(attack_match.group(3))
                    attack_type = attack_match.group(4)
                    quality = attack_match.group(5)

                    # Обновление статистики атаки
                    player_stats[player_num]["total_attacks"] += 1
                    if block_touch == 'O':
                        player_stats[player_num]["won_attacks"] += 1
                        player_stats[player_num]["attack_type_F"]["total"] += 1
                        player_stats[player_num]["attack_type_F"]["success"] += 1

                    if block_touch == 'E':
                        player_stats[player_num]["attack_errors"] += 1

                    if quality == '#':
                        player_stats[player_num]["won_attacks"] += 1
                    elif quality == '-':
                        player_stats[player_num]["attack_errors"] += 1

                    if attack_type == 'F':
                        player_stats[player_num]["attack_type_F"]["total"] += 1
                        if quality == '#':
                            player_stats[player_num]["attack_type_F"]["success"] += 1
                    continue

                # Проверка, является ли шифр блоком
                block_match = re.match(block_pattern, entry)
                if block_match:
                    player_num = int(block_match.group(1))
                    player_stats[player_num]["total_blocks"] += 1
                    continue
                
                # Проверка, является ли шифр ошибкой
                error_match = re.match(error_pattern, entry)
                if error_match:
                    player_num = int(error_match.group(1))
                    player_stats[player_num]["total_errors"] += 1
                    continue

                print(f"Некорректный формат шифра: {entry}")

        # Вычисление дополнительных метрик для приема и атаки
        for player, stats in player_stats.items():
            total_receptions = stats["total_receptions"]
            if total_receptions > 0:
                good_receptions = stats["reception_quality"]["R#"] + stats["reception_quality"]["R+"]
                stats["good_reception_rate"] = good_receptions / total_receptions
                stats["best_reception_rate"] = stats["reception_quality"]["R#"] / total_receptions

            total_F_attacks = stats["attack_type_F"]["total"]
            
            if total_F_attacks > 0:
                stats["attack_success_rate_F"] = stats["attack_type_F"]["success"] / total_F_attacks
            
            stats["total_points"]= stats["won_attacks"] + stats["won_serves"] + stats["total_blocks"]
            stats["total_errors"] = stats["attack_errors"] + stats["lost_serves"] + stats["total_errors"] + stats["reception_errors"]
            
            stats["result_player"] = stats["total_points"] - stats["total_errors"]


        # Преобразуем статистику в DataFrame
        data_records = []
        for player, stats in player_stats.items():
            most_common_zone = stats["zone_count"].most_common(1)
            most_common_zone = most_common_zone[0][0] if most_common_zone else None
            data_records.append({
                "Player": player,
                "Total Serves": stats["total_serves"],
                "Won Serves": stats["won_serves"],
                "Lost Serves": stats["lost_serves"],
                "Most Common Zone": most_common_zone,
                "Serve Style P": stats["serve_style"]["P"],
                "Serve Style F": stats["serve_style"]["F"],
                "Total Receptions": stats["total_receptions"],
                "Reception Errors (R--)": stats["reception_errors"],
                "Good Reception Rate (R#+R+)": round(stats["good_reception_rate"], 2),
                "Best Reception Rate (R#)": round(stats["best_reception_rate"], 2),
                "Total Attacks": stats["total_attacks"],
                "Won Attacks": stats["won_attacks"],
                "Attack Errors": stats["attack_errors"],
                "Attack Success Rate F": round(stats["attack_success_rate_F"], 2),
                "Total Blocks": stats["total_blocks"],
                "Total Errors": stats["total_errors"],
                "Total Points": stats["total_points"],
                "Player Result": stats["result_player"] 

            })
        
        # Создаём DataFrame
        df = pd.DataFrame(data_records)
        return df

    def start_listening(self):    
        @bot.message_handler(content_types=['document'])
        def handle_document(message):
            # Проверяем, что это CSV-файл
            if message.document.mime_type == 'text/csv':
                # Загружаем файл
                file_info = bot.get_file(message.document.file_id)
                downloaded_file = bot.download_file(file_info.file_path)

                # Создаем временный файл для хранения CSV
                with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as temp_file:
                    temp_filename = temp_file.name
                    temp_file.write(downloaded_file)

                # Путь для выходного файла анализа
                output_filename = "analysis_result.csv"

                # Обрабатываем файл
                bot.send_message(message.chat.id, "Файл получен! Начинаю анализ...")
                try:
                    analysis_result = self.analyze_game_stats_from_csv(temp_filename)
                    bot.send_message(message.chat.id, "Анализ завершен! Отправляю результаты.")
                    
                    # Сохраняем результат анализа в CSV
                    analysis_result.to_csv(output_filename, index=False, encoding="utf-8")

                    # Отправляем CSV результат пользователю
                    with open(output_filename, "rb") as result_file:
                        bot.send_document(message.chat.id, result_file)
                except Exception as e:
                    bot.send_message(message.chat.id, f"Ошибка при анализе файла: {e}")
                finally:
                    # Удаляем временные файлы
                    os.remove(temp_filename)
                    if output_filename and os.path.exists(output_filename):
                        os.remove(output_filename)
            else:
                bot.send_message(message.chat.id, "Пожалуйста, загрузите файл в формате .csv.")

volleyball_bot = VolleyballBot()

@bot.message_handler(commands=['start'])
def start_game(message):
    bot.send_message(
        message.chat.id,
        "Добро пожаловать в волейбольный трекер! Выберите действие, отправив номер:\n"
        "1. Подача\n"
        "2. Прием\n"
        "4. Атака\n"
        "6. Блок\n"
        "7. Ошибка\n"
        "8. Завершить розыгрыш\n"
        "9. Сохранить игру\n"
        "0. Аналитика"
    )

@bot.message_handler(func=lambda message: message.text.isdigit())
def choice_handler(message):
    volleyball_bot.handle_choice(message)

# Запуск бота с polling
bot.remove_webhook()  # Убираем webhook, если активен
bot.polling()