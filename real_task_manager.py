import uuid
from datetime import datetime
import sys
from task import Task


# Константы
STATUS_ACTIVE = "active" # Глобальная константа, используется в разных частях, оставим пока
STATUS_DONE = "done"     # Глобальная константа
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
    for task_info in tasks: # task_info здесь - это уже отформатированная строка
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
    tasks_objects = []
    if not raw_content.strip(): 
        return tasks_objects
    for task_line in raw_content.splitlines():
        if task_line.strip(): 
            parts = task_line.split(SEPARATOR)
            if len(parts) == 5: 
                task_obj = Task(id=parts[0], descr=parts[1], date=parts[2], date_created=parts[3], status=parts[4])
                tasks_objects.append(task_obj)
            else:
                print(f"Предупреждение: некорректная строка в базе данных пропущена: {task_line}")
    return tasks_objects



def prepare_tasks_list_to_output(tasks_objects_list):
    return [task.to_output() for task in tasks_objects_list]


def serialize_task_for_db(task_object):
    return SEPARATOR.join([
        str(task_object.id), 
        task_object.descr,
        task_object.date,
        task_object.date_created, 
        task_object.status
    ])



def prepare_new_task_to_save(task_info):
    description = task_info[0]
    due_date = task_info[1] 

    formatted_due_date = f"[{due_date}]" if due_date else ""

    new_task_object = Task.new_from_user(description, formatted_due_date)
    return serialize_task_for_db(new_task_object)


def get_all_tasks(to_show_status): #
    raw_db_content = read_from_db()
    all_task_objects = deserialize_tasks_from_db(raw_db_content)
    filtered_task_objects = [task_obj for task_obj in all_task_objects if task_obj.status == to_show_status]

    tasks_list_to_print = prepare_tasks_list_to_output(filtered_task_objects)
    return tasks_list_to_print


# Парсим введённые пользователем параметры задачи: описание и дату исполнения
def parse_new_task_input(raw_data):
    splitted_params = raw_data.split("[")
    task_description = splitted_params[0].strip()
    task_due_date = ""

    if len(splitted_params) == 2:
        task_due_date = splitted_params[1].replace("]","").strip() 

    return [task_description, task_due_date]
    # не меняем


#----------#

# Действие меню "Новая задача"
def action_new_task():
    print("#------------------#")
    print("Введите параметры новой задачи (описание [дата]) или 0, чтобы вернуться в основное меню:")
    new_task_info_raw = input() 

    if new_task_info_raw == "0": return

    task_data_parsed = parse_new_task_input(new_task_info_raw) 
    task_string_to_save = prepare_new_task_to_save(task_data_parsed)
    append_new_line_to_db(task_string_to_save)
    print("Задача добавлена!")
 

# Действие меню "Завершить задачу"
def action_complete_task():
    print("#------------------#")
    active_tasks_for_completion = get_all_tasks(STATUS_ACTIVE) 
    if not active_tasks_for_completion:
        print("Нет активных задач для завершения.")
        return

    print("Актуальные задачи для завершения:")
    print_all_tasks_to_console(active_tasks_for_completion)
    print("Введите номер задачи для завершения или 0, чтобы вернуться в основное меню")

    try:
        task_number_input = int(input())
    except ValueError:
        print("Некорректный ввод. Введите число.")
        return

    if task_number_input == 0: return
    if task_number_input < 1 or task_number_input > len(active_tasks_for_completion):
        print("Нет задачи с таким номером.")
        return


    raw_db_content = read_from_db()
    all_task_objects = deserialize_tasks_from_db(raw_db_content) 

    target_task_id = None
    current_active_task_index = 0

    for task_obj in all_task_objects:
        if task_obj.status == Task.STATUS_ACTIVE: 
            current_active_task_index += 1
            if current_active_task_index == task_number_input:
                target_task_id = task_obj.id
                break

    if target_task_id is None:
        print("Не удалось найти задачу для завершения. Возможно, список изменился.")
        return

    modified_tasks_for_db = []
    task_completed = False
    for task_obj in all_task_objects:
        if str(task_obj.id) == str(target_task_id):
            task_obj.status = Task.STATUS_DONE 
            task_completed = True
        modified_tasks_for_db.append(serialize_task_for_db(task_obj))

    if task_completed:
        final_string_to_save = "\n".join(modified_tasks_for_db)
        rewrite_db(final_string_to_save)
        print(f"Задача номер {task_number_input} завершена.")
    else:
        # Опять же, не должно произойти
        print("Ошибка при завершении задачи.")


# Действие меню "Изменить параметры задачи"
def action_change_task_params():
    print("#------------------#")
    print("Введите номер задачи для изменения её параметров или 0, чтобы вернуться в предыдущее меню")
    #ТУДУ: Реализовать логику изменения параметров задачи, т.е. изменения описания и/или времени исполнения
    print("Функционал изменения задачи пока не реализован.")

# Действие меню "Показать завершённые задачи"
def show_completed_tasks():
    print("#------------------#")
    print("Завершённые задачи:")
    tasks_list = get_all_tasks(STATUS_DONE) 
    if tasks_list:
        print_all_tasks_to_console(tasks_list)
    else:
        print("Нет завершённых задач.")
    # не меняем

# Действие меню "Очистить все завершённые задачи"
def erase_completed_tasks():
    print("#------------------#")
    #ТУДУ: реализовать логику
    raw_db_content = read_from_db()
    all_task_objects = deserialize_tasks_from_db(raw_db_content)

    active_tasks_only = [task_obj for task_obj in all_task_objects if task_obj.status == Task.STATUS_ACTIVE]

    if len(active_tasks_only) == len(all_task_objects):
        print("Нет завершённых задач для удаления.")
        return

    tasks_to_save_strings = [serialize_task_for_db(task_obj) for task_obj in active_tasks_only]
    final_string_to_save = "\n".join(tasks_to_save_strings)
    rewrite_db(final_string_to_save)
    print("Все завершённые задачи были удалены.")


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

    print(menu_text.strip()) 
    choice = input("Номер действия: ")
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
        print("Выход из программы.")
        sys.exit()
    else:
        print("Неизвестная команда")


# Основная функция с постоянным выводом списка задач и меню
def main():
    while True:
        tasks_list = get_all_tasks(STATUS_ACTIVE) 
        print("\n#----- Актуальные задачи -----#") 
        if tasks_list:
            print_all_tasks_to_console(tasks_list)
        else:
            print("Список активных задач пуст.")
        show_main_menu()


if __name__ == "__main__": 
    main()