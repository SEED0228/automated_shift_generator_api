from datetime import datetime as dt
import random
from itertools import groupby

class Variant(object):
    # 初期化
    def __init__(self, shift_dict, parameters, list=None):
        self.shift_dict = shift_dict
        self.length = len(shift_dict)
        self.parameters = parameters
        if list == None:
            self.make_sample()
        else:
            self.list = list
        self.selected_shifts = []

    # ランダムなデータを生成
    def make_sample(self):
        sample_list = []
        for num in range(self.length):
            sample_list.append(random.randint(0, 60))
        self.list = tuple(sample_list)
    
    # 選択されたシフトを作成
    def create_selected_shifts(self):
        self.selected_shifts = []
        copy_dict_values = list(self.shift_dict.values())
        for id, x in enumerate(self.list):
            shifts = copy_dict_values[id]
            if x < len(shifts):
                self.selected_shifts.append(shifts[x])
    # 選択されたシフトを取得
    def get_selected_shifts(self):
        selected_shifts = self.selected_shifts.copy()
        for selected_shift in selected_shifts:
            selected_shift['period'] = {}
            selected_shift['period']['from'] = selected_shift['start_time'].strftime('%Y-%m-%dT%H:%M:%S%z')
            selected_shift['period']['to'] = selected_shift['end_time'].strftime('%Y-%m-%dT%H:%M:%S%z')
        return selected_shifts

    # 合計の給料を取得
    def sum_total_salary(self):
        return sum(x['salary'] for x in self.selected_shifts)

    # 遺伝的アルゴリズムにおける評価を行う
    def eval(self):
        # 希望した給料との差異
        salary_diff = abs(self.sum_total_salary() - self.parameters['expected_salary']) / max(self.sum_total_salary(), self.parameters['expected_salary'])
        # 週に何日で出たいかからこの期間で大体何日入りたいかを算出
        count_days = len(self.selected_shifts)
        expected_days = round(self.parameters['expected_day_per_week'] / 7 * self.parameters['days'])
        print(f"{expected_days}, {count_days}, {salary_diff}")
        # 希望勤務日数との差異
        days_diff = abs(expected_days - count_days) / max(expected_days, count_days)
        return salary_diff, days_diff,
        

