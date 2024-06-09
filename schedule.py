import math
from pulp import *

def solve_scheduling_problem():

    days= int(input("Въведете колко дни е проекта: "))
    if days > 30:
        print("Грешка: Няма проект с толкова дни!")
        return

    num_employees= int(input("Въведете броя на служителите (максимум 10): "))
    if num_employees > 10:
        print("Грешка: Не може да има повече от 10 служители.")
        return

    model = LpProblem("Association NIE Scheduling Problem", LpMinimize)

    names = []
    unavailable_shifts = {}

    for i in range(num_employees):
        name = input(f"Въведете името на служител {i + 1}: ")
        names.append(name)
        unavailable_shifts[name] = []
        
        # Въвеждане на недостъпните смени за всеки служител
        while True:
            unavailable_input = input(f"Въведете ден и смяна, когато {name} не може да работи (формат: ден_смяна, например 1_0 за първи ден, закуска, въведете 'край' за завършване): ")
            if unavailable_input.lower() == 'край':
                break
            day_shift = unavailable_input.split('_')
            if len(day_shift) == 2 and day_shift[0].isdigit() and day_shift[1].isdigit():
                day = int(day_shift[0]) - 1 
                shift = int(day_shift[1])
                if 0 <= day < days and 0 <= shift < 3:
                    unavailable_shifts[name].append((day, shift))
                else:
                    print("Невалиден ден или смяна. Опитайте отново.")
            else:
                print("Невалиден формат. Опитайте отново.")

    # Дефиниране на променливите
    # i - служители, j - дни, k - смени
    x = [[[LpVariable(f"{names[i]}_{j}_{k}", cat="Binary") for k in range(3)] for j in range(days)] for i in range(num_employees)]

    # Дефиниране на променливите за минимизиране на последователни дни на една и съща смяна
    y = [[[LpVariable(f"y_{names[i]}_{j}_{k}", cat="Binary") for k in range(3)] for j in range(days)] for i in range(num_employees)]

    # Дефиниране на целевата функция
    # Целевата функция ще минимизира броя на последователни дни на една и съща смяна
    model += lpSum([y[i][j][k] for i in range(num_employees) for j in range(days - 3) for k in range(3)])

    # Дефиниране на ограниченията
    # Добавяне на ограниченията за недостъпните смени
    for i in range(num_employees):
        for day, shift in unavailable_shifts[names[i]]:
            model += x[i][day][shift] == 0


    # 2 човека на закуска, по трима за другите смени
    max_shift_breakfast = 2
    max_shift = 3 
    for j in range(days):
        model += lpSum([x[i][j][0] for i in range(num_employees)]) == max_shift_breakfast
        model += lpSum([x[i][j][1] for i in range(num_employees)]) == max_shift
        model += lpSum([x[i][j][2] for i in range(num_employees)]) == max_shift

   
    # Един човек трябва да работи по 2 смени на ден
    for i in range(num_employees):
        for j in range(days):
            model += lpSum([x[i][j][k] for k in range(3)]) <= 2

    # Да не се повтарят едни и същи смени твърде много
    for i in range(num_employees):
        for j in range(days - 3):
            for k in range(3):
                model += lpSum([x[i][j + l][k] for l in range(4)]) <= 3 + y[i][j][k]


    # Решаване на модела
    model.solve()
    # Проверка на статуса на решението
    if LpStatus[model.status] != "Optimal":
        print("Решението не е намерено или не е оптимално.")
        return
      
    # Принтиране на график
    for j in range(days):
        print(f"Ден {j + 1}:")
        for i in range(num_employees):
            print(f"\t{names[i]}:", end=" ")
            if x[i][j][0].value() != 0:
                print("Закуска", end=", ")
            if x[i][j][1].value() != 0:
                print("Обяд", end=", ")
            if x[i][j][2].value() != 0:
                print("Вечеря", end=", ")
            print() 

    print()


solve_scheduling_problem() 