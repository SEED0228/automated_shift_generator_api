from datetime import datetime as dt
from datetime import timedelta as td
import random
from deap import creator, base, tools, algorithms
from scoop import futures
from modules.variant import Variant
import requests
from itertools import groupby

day_names = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
start_dt = dt.now()
end_dt = dt.now()
all_shifts = []
parameters = {}
ptjs = []
shift_dict = {}

# シフト作成用関数、apiから呼び出される
def create_shifts(part_time_jobs, params: dict)-> dict:
    global all_shifts, parameters, ptjs
    parameters = params
    response = {}
    ptjs = part_time_jobs
    from_date = dt.strptime(parameters['period']['from'], '%Y-%m-%d')
    to_date = dt.strptime(parameters['period']['to'], '%Y-%m-%d')
    parameters['days'] = (to_date - from_date).days + 1
    all_shifts = get_all_shifts(part_time_jobs, parameters['period'])
    response.setdefault('results', exec_ga())
    return response

# イベントとシフトが重なってなければtrue
def is_not_overlap_time(element: dict):
    global start_dt, end_dt
    return not (element['start_time'] <= end_dt and element['end_time'] >= start_dt)

# google calendarのイベントを考慮した上で入りうるシフトのパターンを全て取得
def get_all_shifts(part_time_jobs, period: dict)-> dict:
    global start_dt, end_dt
    from_date = dt.strptime(period['from'], '%Y-%m-%d')
    to_date = dt.strptime(period['to'], '%Y-%m-%d')
    # 予定がない場合にシフトを入れられる全パターンを取得
    components = {}
    for day_name in day_names:
        components[day_name] = []
    for part_time_job in part_time_jobs:
        for day_name in day_names:
            for period in part_time_job["enabled_work_time"][day_name]:
                if period["is_enabled"]:
                    start_time = int(period['start_time'].split(':')[0])
                    end_time = int(period['end_time'].split(':')[0])
                    min_time = 3
                    max_time = 9
                    for i in range(min_time, min(max_time, end_time - start_time) + 1):
                        for j in range(start_time, end_time - i + 1):
                            # 6時間を超えると休憩1時間追加
                            break_time = min(i // 7, 1)
                            work_time = i - break_time
                            components[day_name].append({
                                "start_time": f"T{str(j).zfill(2)}:00:00+09:00",
                                "end_time": f"T{str(j+i).zfill(2)}:00:00+09:00",
                                "name": part_time_job['name'],
                                "salary": part_time_job['hourly_wage'] * work_time,
                                "break_time": break_time,
                                "work_time": work_time,
                                "transportation_expenses": part_time_job['transportation_expenses'] * 2
                            })
    # response.setdefault('components', components)

    # google calendarで取得したeventを考慮せずに、指定された期間で入りうるシフト情報を作成
    shifts = []
    for i in range((to_date - from_date).days + 1):
        date = from_date + td(days=i)
        datestr = date.strftime('%Y-%m-%d')
        for element in components[day_names[date.weekday()]]:
            new_element = element.copy()
            new_element['start_time'] = dt.strptime(datestr + element['start_time'], '%Y-%m-%dT%H:%M:%S%z')
            new_element['end_time'] = dt.strptime(datestr + element['end_time'], '%Y-%m-%dT%H:%M:%S%z')
            shifts.append(new_element)
    events = get_google_calendars_events(period)
    # 上記シフト情報からgoogle calendarで取得したeventを考慮
    for event in events:
        if 'dateTime' in event['start']:
            start_dt = dt.strptime(event['start']['dateTime'], '%Y-%m-%dT%H:%M:%S%z')
            end_dt = dt.strptime(event['end']['dateTime'], '%Y-%m-%dT%H:%M:%S%z')
        elif 'date' in event['start']:
            # 日本時間を考慮
            start_dt = dt.strptime(event['start']['date'] + "+09:00", '%Y-%m-%d%z')
            end_dt = dt.strptime(event['start']['date'] + "+09:00", '%Y-%m-%d%z') + td(days=1, seconds=-1)
        else:
            continue
        shifts = list(filter(is_not_overlap_time, shifts))
    return shifts

# APIを介してgoogle calendarのイベント情報を取得
def get_google_calendars_events(period: dict):
    r = requests.get('http://high-entropy.australiaeast.cloudapp.azure.com:8080/get_calendar', period)
    # # リクエストエラー発生時用
    # r = requests.get('http://high-entropy.australiaeast.cloudapp.azure.com:8080/get_calendar')
    json = r.json()
    return json['items']

# バリアントの評価
def evalVariant(individual):
    global all_shifts, parameters, shift_dict
    variant = Variant(shift_dict, parameters, list=individual)
    variant.create_selected_shifts()
    return variant.eval()

# 遺伝的アルゴリズムの実行
def exec_ga():
    result = {}
    global all_shifts, parameters, shift_dict
    shift_dict = {}
    for key, shifts in groupby(all_shifts, key=lambda x: x['start_time'].strftime('%Y-%m-%d')):
        shift_dict[key] = list(shifts)
    result.setdefault('all_shifts0', all_shifts)
    creator.create("FitnessMax", base.Fitness, weights=(-10.0, -10.0,))
    creator.create("Individual", list, fitness=creator.FitnessMax)
    toolbox = base.Toolbox()
    toolbox.register("map", futures.map)
    # 1/10でシフトが選択される 値が1の時にそのindexのシフトが選択
    print(len(ptjs) * 100)
    toolbox.register("attr_bool", random.randint, 0, len(ptjs) * 80)
    toolbox.register("individual", tools.initRepeat, creator.Individual, toolbox.attr_bool, len(shift_dict))
    toolbox.register("population", tools.initRepeat, list, toolbox.individual)
    toolbox.register("evaluate", evalVariant)
    toolbox.register("mate", tools.cxTwoPoint)
    toolbox.register("mutate", tools.mutFlipBit, indpb=0.05)
    toolbox.register("select", tools.selTournament, tournsize=3)
    population = toolbox.population(n=500)

    NGEN=20
    for gen in range(NGEN):
        offspring = algorithms.varAnd(population, toolbox, cxpb=0.5, mutpb=0.1)
        fits = toolbox.map(toolbox.evaluate, offspring)
        for fit, ind in zip(fits, offspring):
            ind.fitness.values = fit
        population = toolbox.select(offspring, k=len(population))
        print(str(gen)+','+str(sum(tools.selBest(population, k=1)[0])))
    top10 = tools.selBest(population, k=10)
    for i in range(10):
        variant = Variant(shift_dict, parameters, list=top10[i])
        variant.create_selected_shifts()
        ind_result = {}
        ind_result.setdefault('salary', variant.sum_total_salary())
        ind_result.setdefault('shifts', variant.get_selected_shifts())
        ind_result.setdefault('length', len(variant.selected_shifts))
        result.setdefault(str(i), ind_result)
    return result
