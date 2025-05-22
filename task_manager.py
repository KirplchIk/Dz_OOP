import uuid
from datetime import datetime
import sys

# Константы
STATUS_ACTIVE = "active"
STATUS_DONE = "done"
SEPARATOR = "<>" 
DB_FILE_PATH = "db.txt"

NEW_TASK_ITEM = "1"
COMPLETE_TASK_ITEM = "2"
CHANGE_TASK_ITEM = "3"
SHOW_COMPLETED_TASKS = "4"
ERASE_COMPLETED_TASKS = "5"
EXIT_ITEM = "0"
MENU_ITEMS = {
    NEW_TASK_ITEM: "Создать новую задачу",
    COMPLETE_TASK_ITEM: "Завершить задачу",
    CHANGE_TASK_ITEM: "Изменить параметры задачи",
    SHOW_COMPLETED_TASKS: "Показать завершённые задачи",
    ERASE_COMPLETED_TASKS: "Очистить все завершённые задачи",
    EXIT_ITEM: "Выйти из программы"
}

# Временно перенсли сюда, чтобы можно было вызывать из разных функций
# Вывод списка задач в консоль
def print_all_tasks_to_console(tasks):
    counter = 1
    for task_info in tasks:
        print(str(counter) + ": " + task_info)
        counter += 1

#----------#
# Блок функций для чтения/записи в файл
#----------#
# Читаем ВСЕ содержимое файла
def read_from_db():
    with open(DB_FILE_PATH, "r", encoding="utf8") as file_object: 
        return file_object.read()


# Добавляем новую строку в файл
def append_new_line_to_db(new_line): 
    file_object = open(DB_FILE_PATH, "a", encoding="utf8")
    file_object.write("\n") 
    file_object.write(new_line)
    file_object.close()


# Перезаписываем все задачи/всё содержимое файла
def rewrite_db(raw_content): 
    file_object = open(DB_FILE_PATH, "w", encoding="utf8")
    file_object.write(raw_content)
    file_object.close()


#----------#
# Преобразуем содержимое файла в список задач
def deserialize_tasks_from_db(raw_content):
    # raw_tasks = raw_content.splitlines()
    # tasks = []
    # for task_info in raw_tasks:
    #     splitted_task = task_info.split(SEPARATOR) 
    #     tasks.append(splitted_task)
    # return tasks

    #переделали на списочное включение
    return [task_info.split(SEPARATOR) for task_info in raw_content.splitlines()]
    # будем создавать список объектов Task на основе инфы из базы и возвращать его


# Подготавливаем список задач для вывода в консоль
def prepare_tasks_list_to_output(raw_tasks_list):
    # tasks = []
    # for task_info in raw_tasks_list:
    #     status = "✓" if task_info[4] == STATUS_ACTIVE else "✕"
    #     task = status + " " + task_info[1] + " " + task_info[2] + " " + task_info[3] # склеиваем параметры задачи
    #     tasks.append(task)
    # return tasks

    #переделали на списочное включение
    return [("✓" if task_info[4] == STATUS_ACTIVE else "✕") + " " + task_info[1] + " " + task_info[2] + " " + task_info[3]
            for task_info in raw_tasks_list]
    # возвращаем список задач путем перебора объектов и вызова to_output


# Превращаем информацию о задаче в строку для последующего сохранения в БД
def serialize_task_for_db(task_data):
    return SEPARATOR.join([task_data[0], task_data[1], task_data[2], task_data[3], task_data[4]])
    # всё-таки поменяем (как??)
	

# Подготавливаем новую задачу для сохранения
def prepare_new_task_to_save(task_info): 
    task_id = uuid.uuid4() 
    task_date_created = datetime.now() 
    task_to_save = serialize_task_for_db([str(task_id), task_info[0], "["+task_info[1]+"]", str(task_date_created), STATUS_ACTIVE])
    return task_to_save
    # создаем новый экземпляр


# Получаем список всех задач из БД и подготавливаем к выводу в консоль
def get_all_tasks(to_show):
    all_tasks = read_from_db()
    # raw_tasks = deserialize_tasks_from_db(all_tasks)
    # print(raw_tasks)
    # final_tasks = []
    # for raw_task in raw_tasks:
    #     if raw_task[4] == to_show: final_tasks.append(raw_task)

    #переделали на списочное включение
    final_tasks = [raw_task for raw_task in deserialize_tasks_from_db(all_tasks) if raw_task[4] == to_show]

    tasks_list_to_print = prepare_tasks_list_to_output(final_tasks)
    return tasks_list_to_print
    # меняем на перебор объектов и используем параметр status


# Парсим введённые пользователем параметры задачи: описание и дату исполнения
def parse_new_task_input(raw_data):
    splitted_params = raw_data.split("[") 
    task_description = splitted_params[0].strip()
    task_due_date = ""
    
    if len(splitted_params) == 2:
        task_due_date = splitted_params[1].replace("]","")
    
    return [task_description, task_due_date]
    # не меняем


#----------#

# Действие меню "Новая задача"
def action_new_task():
    print("#------------------#")
    print("Введите параметры новой задачи или 0, чтобы вернуться в основное меню:")
    new_task_info = input()
    
    if new_task_info == "0": return

    task_data = parse_new_task_input(new_task_info)
    task_to_save = prepare_new_task_to_save(task_data)
    append_new_line_to_db(task_to_save)
    # не меняем


# Действие меню "Завершить задачу"
def action_complete_task():
    print("#------------------#")
    print("Введите номер задачи для завершения или 0, чтобы вернуться в основное меню")
    
    # Запрашиваем у пользователя порядковый номер задачи (который он видит на экране)
    task_number = int(input())
    
    if task_number == 0: return
    
    # Как-то находим эту задачу в БД
    all_tasks = read_from_db()
    raw_tasks = deserialize_tasks_from_db(all_tasks)
    
    tasks_output = []
    active_tasks_count = 1
    for task in raw_tasks:
        if task[4] == STATUS_ACTIVE:
            if active_tasks_count == task_number:
                task[4] = STATUS_DONE
            active_tasks_count += 1
        task_to_save = serialize_task_for_db(task)
        tasks_output.append(task_to_save)
    
    final_string_to_save = "\n".join(tasks_output)
    rewrite_db(final_string_to_save)
    # меняем на перебор объектов и обращаемся к параметру status

# Действие меню "Изменить параметры задачи"
def action_change_task_params():
    print("#------------------#")
    print("Введите номер задачи для изменения её параметров или 0, чтобы вернуться в предыдущее меню")    
    #ТУДУ: Реализовать логику изменения параметров задачи, т.е. изменения описания и/или времени исполнения

# Действие меню "Показать завершённые задачи"
def show_completed_tasks():
    print("#------------------#")
    print("Завершённые задачи:")
    tasks_list = get_all_tasks(STATUS_DONE)
    print_all_tasks_to_console(tasks_list) 
    # не меняем   
    

# Действие меню "Очистить все завершённые задачи"
def erase_completed_tasks():
    print("#------------------#")
    print("Очищаем базу от завершённых задач...")
    #ТУДУ: реализовать логику
  

#----------#
# Вывод в консоль
#----------#
# Вывод основного меню
def show_main_menu():
    print("#------------------#")
    print("Выберите действие:")
    menu_text = ""
    for key, value in MENU_ITEMS.items():
        menu_text = menu_text + key + " – " + value + "\n"
    
    print(menu_text)
    print("Номер действия: ")
    choice = input()
    
    if choice == NEW_TASK_ITEM:
        action_new_task()
    elif choice == COMPLETE_TASK_ITEM:
        action_complete_task()
    elif choice == CHANGE_TASK_ITEM:
        action_change_task_params()
    elif choice == SHOW_COMPLETED_TASKS:
        show_completed_tasks()
    elif choice == ERASE_COMPLETED_TASKS:
        erase_completed_tasks()
    elif choice == EXIT_ITEM:
        sys.exit()
    else:
        print("Неизвестная команда")


# Основная функция с постоянным выводом списка задач и меню
def main():
    while True:
        tasks_list = get_all_tasks(STATUS_ACTIVE)
        print("Актуальные задачи:")
        print_all_tasks_to_console(tasks_list)
        show_main_menu()

# Вызов основной функции при запуске
main()