import csv

class VolleyballAction:
    def __init__(self):
        self.data = []
        self.current_rally = []  # Текущий розыгрыш

    def get_serve(self):
        player_number = input("Введите номер игрока, подающего мяч: ")
        zone = input("Введите зону подачи (1-6): ")
        style = input("Введите стиль подачи (F - силовая, P - планер): ")
        result = input("Введите результат подачи (# - очко, - - ошибка): ")
        action = f"S{player_number}z{zone}{style}{result}"
        self.current_rally.append(action)
        return action

    def get_reception(self):
        quality = input("Введите качество приема (# - лучший, + - хороший, ! - средний, - - плохой, f - фрибол, $ - ошибка): ")
        player_number = input("Введите номер игрока, который совершал прием: ")
        action = f"R{quality}n{player_number}"
        self.current_rally.append(action)
        return action
    
    def get_set(self):
        zone = input("Введите зону передачи (1-6): ")
        zone_point = input("Введите уточнение зоны (1 - левый, 2 - середина, 3 - правый): ")
        non_setter = input("Пас не от связующего (оставьте пустым, если пас от связующего): ")
        quality = input("Введите качество передачи (! - средний, + - хороший, # - идеальный): ")
        action = f"P{zone}.{zone_point}{non_setter}{quality}"
        self.current_rally.append(action)
        return action

    def get_attack(self):
        player_number = input("Введите номер атакующего игрока: ")
        block_touch = input("Введите касание блока (- - без блока, + - было касание блока, O - блок аут, E - блок в пол): ")

        if block_touch in ["O", "E"]:
            action = f"A{player_number}{block_touch}z0"
            self.current_rally.append(action)
            return action
        
        zone = input("Введите зону атаки (1-6): ")
        attack_type = input("Введите тип атаки (F - удар, D - атака скидкой):")
        quality = input("Введите качество атаки (# - идеальная, - - ошибка): ")

        action = f"A{player_number}{block_touch}z{zone}{attack_type}{f'{quality}' if quality else ''}"
        self.current_rally.append(action)
        return action

    def get_defense(self):
        player_number = input("Введите номер игрока, выполняющего защиту: ")
        reception_type = input("Введите тип приема (T - верхний, B - нижний): ")
        quality = input("Введите качество защиты (# - идеальная, + - хорошая, - - ошибка): ")
        action = f"D{player_number}{reception_type}{quality if quality else ''}"
        self.current_rally.append(action)
        return action
    
    def get_block(self):
        player_number = input("Номер игрока: ")
        action = f"B{player_number}"
        self.current_rally.append(action)
        return action

    def get_error(self):
        player_number = input("Номер игрока: ")
        type_error = input("n - касание сетки, p - ошибка 2 передачи, l - заступ: ")
        action = f"E{player_number}{type_error}"
        
        self.current_rally.append(action)
        return action

    def end_rally(self):
        """Завершение текущего розыгрыша и добавление в общие данные"""
        if self.current_rally:
            self.data.append(",".join(self.current_rally))  # Запись розыгрыша как одной строки
            self.current_rally = []  # Очистка текущего розыгрыша для нового

    def save_to_csv(self, filename):
        with open(filename, mode='w' , encoding = 'utf-8', newline='') as file:
            writer = csv.writer(file)
            for row in self.data:
                writer.writerow([row])

class VolleyballGame:
    def __init__(self):
        self.actions = VolleyballAction()

    def main_menu(self):
        actions = {
            '1': self.actions.get_serve,
            '2': self.actions.get_reception,
            '3': self.actions.get_set,
            '4': self.actions.get_attack,
            '5': self.actions.get_defense,
            '6': self.actions.get_block,
            '7': self.actions.get_error,
            '8': self.actions.end_rally
        }

        while True:
            print("\nВыберите действие:")
            print("1. Подача")
            print("2. Прием")
            print("3. Передача")
            print("4. Атака")
            print("5. Защита")
            print("6. Блок")
            print("7. Ошибка")
            print("8. Завершить розыгрыш")
            print("0. Выход")

            choice = input("Ваш выбор: ")
            if choice == '0':
                break
            elif choice in actions:
                action_result = actions[choice]()
                if choice != '8':  # Не выводить результат для завершения розыгрыша
                    print(f"Сгенерированный шифр: {action_result}")
            else:
                print("Неверный выбор. Пожалуйста, попробуйте снова.")

    def save_game(self):
        filename = input("Введите имя файла для сохранения данных (например, game.csv): ")
        self.actions.save_to_csv(filename)
        print(f"Данные сохранены в файл {filename}")

if __name__ == "__main__":
    game = VolleyballGame()
    game.main_menu()
    game.save_game()
