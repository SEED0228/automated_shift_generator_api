from datetime import datetime as dt
import random
from itertools import groupby

class Variant(object):
    # 初期化
    def __init__(self, all_shifts, parameters, list=None):
        self.all_shifts = all_shifts
        self.length = len(all_shifts)
        self.parameters = parameters
        if list == None:
            self.make_sample()
        else:
            self.list = list
        self.selected_shifts = []
        for id, x in enumerate(self.list):
            if x == 1:
                self.selected_shifts.append(self.all_shifts[id])
    pass

    # ランダムなデータを生成
    def make_sample(self):
        sample_list = []
        for num in range(self.length):
            sample_list.append(random.randint(0, 60))
        self.list = tuple(sample_list)
    
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
    
    # 同じ日に複数のシフトが入っていないかのチェック
    def count_duplicated_shifts(self):
        cnt = 0
        selected_shifts = self.selected_shifts.copy()
        for _, shifts in groupby(selected_shifts, key=lambda x: x['start_time'].strftime('%Y-%m-%d')):
            l = len(list(shifts))
            if l > 1:
                cnt += l
        return cnt
    
    # 出勤する日数の出力
    def count_days(self):
        selected_shifts = self.selected_shifts.copy()
        return len(list(groupby(selected_shifts, key=lambda x: x['start_time'].strftime('%Y-%m-%d'))))

    # 遺伝的アルゴリズムにおける評価を行う
    def eval(self):
        # 希望した給料との差異
        salary_diff = abs(self.sum_total_salary() - self.parameters['expected_salary']) / max(self.sum_total_salary(), self.parameters['expected_salary'])
        # 日付が重複したシフトの割合
        duplicated_shift_count = self.count_duplicated_shifts() / self.length
        # 週に何日で出たいかからこの期間で大体何日入りたいかを算出
        from_date = dt.strptime(self.parameters['period']['from'], '%Y-%m-%d')
        to_date = dt.strptime(self.parameters['period']['to'], '%Y-%m-%d')
        days = (to_date - from_date).days + 1
        count_days = self.count_days()
        expected_days = round(self.parameters['expected_day_per_week'] / 7 * days)
        print(f"{expected_days}, {count_days}")
        # 希望勤務日数との差異
        days_diff = abs(expected_days - count_days) / max(expected_days, count_days)
        return salary_diff, duplicated_shift_count, days_diff,
        

