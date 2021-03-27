# -*- coding: utf-8 -*-

import copy
from queue import LifoQueue, Queue

import numpy as np
from notetool.tool.log import logger


class Recorder(object):
    point = None  # 进行猜测的点
    point_index = 0  # 猜测候选列表使用的值的索引
    value = None  # 回溯记录的值


class Sudoku(object):
    def __init__(self, data):
        # 数据初始化(二维的object数组)
        self.value = np.array([[0] * 9] * 9, dtype=object)  # 数独的值，包括未解决和已解决的
        self.new_points = Queue()  # 先进先出，新解（已解决值）的坐标
        self.recorder = LifoQueue()  # 先进后出，回溯器
        self.guess_times = 0  # 猜测次数

        # 九宫格的基准列表
        self.base_points = [[0, 0], [0, 3], [0, 6], [
            3, 0], [3, 3], [3, 6], [6, 0], [6, 3], [6, 6]]

        # 整理数据
        _data = np.array(data).reshape(9, -1)
        for r in range(0, 9):
            for c in range(0, 9):
                if _data[r, c]:  # if not Zero
                    # numpy default is int32, convert to int
                    self.value[r, c] = int(_data[r, c])
                    # 新的确认的值添加到列表中，以便遍历
                    self.new_points.put((r, c))
                    # logger.debug(f'init: answer={self.value[r, c]} at {(r, c)}')
                else:  # if Zero, guess no. is 1-9
                    self.value[r, c] = [1, 2, 3, 4, 5, 6, 7, 8, 9]

    # 剔除数字
    def _cut_num(self, point):
        r, c = point
        val = self.value[r, c]

        # 行
        for i, item in enumerate(self.value[r]):
            if isinstance(item, list):
                if item.count(val):
                    item.remove(val)

                    # 判断移除后，是否剩下一个元素
                    if len(item) == 1:
                        self.new_points.put((r, i))  # 添加坐标到“已解决”列表
                        logger.debug('only one in row: answer={} at {}'.format(
                            self.value[r, i], (r, i)))
                        self.value[r, i] = item[0]

        # 列
        for i, item in enumerate(self.value[:, c]):
            if isinstance(item, list):
                if item.count(val):
                    item.remove(val)

                    # 判断移除后，是否剩下一个元素
                    if len(item) == 1:
                        self.new_points.put((i, c))
                        logger.debug('only one in col: answer={} at {}'.format(
                            self.value[i, c], (i, c)))
                        self.value[i, c] = item[0]

        # 所在九宫格(3x3的数组)
        b_r, b_c = map(lambda x: x // 3 * 3, point)  # 九宫格基准点
        for m_r, row in enumerate(self.value[b_r:b_r + 3, b_c:b_c + 3]):
            for m_c, item in enumerate(row):
                if isinstance(item, list):
                    if item.count(val):
                        item.remove(val)

                        # 判断移除后，是否剩下一个元素
                        if len(item) == 1:
                            r = b_r + m_r
                            c = b_c + m_c
                            self.new_points.put((r, c))
                            # logger.debug(f'only one in block: answer={self.value[r, c]} at {(r, c)}')
                            self.value[r, c] = item[0]

    # 同一行、列或九宫格中, List里，可能性只有一个的情况
    def _check_one_possible(self):
        # 同一行只有一个数字的情况
        for r in range(0, 9):
            # 只取出是这一行是List的格子
            values = list(filter(lambda x: isinstance(x, list), self.value[r]))

            for c, item in enumerate(self.value[r]):
                if isinstance(item, list):
                    for value in item:
                        if sum(map(lambda x: x.count(value), values)) == 1:
                            self.value[r, c] = value
                            self.new_points.put((r, c))
                            logger.debug(
                                'list val is only one in row: answer={} at {}'.format(self.value[r, c], (r, c)))
                            return True

        # 同一列只有一个数字的情况
        for c in range(0, 9):
            values = list(
                filter(lambda x: isinstance(x, list), self.value[:, c]))

            for r, item in enumerate(self.value[:, c]):
                if isinstance(item, list):
                    for value in item:
                        if sum(map(lambda x: x.count(value), values)) == 1:
                            self.value[r, c] = value
                            self.new_points.put((r, c))
                            logger.debug(
                                'list val is only one in col: answer={} at {}'.format(self.value[r, c], (r, c)))
                            return True

        # 九宫格内的单元格只有一个数字的情况
        for r, c in self.base_points:
            # reshape: 3x3 改为1维数组
            values = list(filter(lambda x: isinstance(x, list),
                                 self.value[r:r + 3, c:c + 3].reshape(1, -1)[0]))

            for m_r, row in enumerate(self.value[r:r + 3, c:c + 3]):
                for m_c, item in enumerate(row):
                    if isinstance(item, list):
                        for value in item:
                            if sum(map(lambda x: x.count(value), values)) == 1:
                                self.value[r + m_r, c + m_c] = value
                                self.new_points.put((r + m_r, c + m_c))
                                logger.debug('list val is only one in block: answer={} at {}'.format(
                                    self.value[r + m_r, c + m_c], (r + m_r, c + m_c)))
                                return True

    # 同一个九宫格内数字在同一行或同一列处理(同行列隐性排除)
    def _check_same_num(self):
        for b_r, b_c in self.base_points:
            block = self.value[b_r:b_r + 3, b_c:b_c + 3]

            # 判断数字1~9在该九宫格的分布情况
            _data = block.reshape(1, -1)[0]
            for i in range(1, 10):
                result = map(lambda x: 0 if not isinstance(x[1], list) else x[0] + 1 if x[1].count(i) else 0,
                             enumerate(_data))
                result = list(filter(lambda x: x > 0, result))
                r_count = len(result)

                if r_count in [2, 3]:
                    # 2或3个元素才有可能同一行或同一列
                    rows = list(map(lambda x: (x - 1) // 3, result))
                    cols = list(map(lambda x: (x - 1) % 3, result))

                    if len(set(rows)) == 1:
                        # 同一行，去掉其他行的数字
                        result = list(map(lambda x: b_c + (x - 1) % 3, result))
                        row = b_r + rows[0]

                        for col in range(0, 9):
                            if col not in result:
                                item = self.value[row, col]
                                if isinstance(item, list):
                                    if item.count(i):
                                        item.remove(i)

                                        # 判断移除后，是否剩下一个元素
                                        if len(item) == 1:
                                            self.new_points.put((row, col))
                                            logger.debug(
                                                'block compare row: answer={} at {}'.format(self.value[row, col],
                                                                                            (row, col)))
                                            self.value[row, col] = item[0]
                                            return True

                    elif len(set(cols)) == 1:
                        # 同一列
                        result = list(
                            map(lambda x: b_r + (x - 1) // 3, result))
                        col = b_c + cols[0]

                        for row in range(0, 9):
                            if row not in result:
                                item = self.value[row, col]
                                if isinstance(item, list):
                                    if item.count(i):
                                        item.remove(i)

                                        # 判断移除后，是否剩下一个元素
                                        if len(item) == 1:
                                            self.new_points.put((row, col))
                                            logger.debug(
                                                'block compare col: answer={} at {}'.format(self.value[row, col],
                                                                                            (row, col)))
                                            self.value[row, col] = item[0]
                                            return True

    # 排除法解题
    def sudo_exclude(self):
        is_run_same = True
        is_run_one = True

        while is_run_same:
            while is_run_one:
                # 剔除数字
                while not self.new_points.empty():
                    point = self.new_points.get()  # 先进先出
                    self._cut_num(point)

                # 检查List里值为单个数字的情况，如有新answer则加入new_points Queue，立即_cut_num
                is_run_one = self._check_one_possible()

            # 检查同行或列的情况
            is_run_same = self._check_same_num()
            is_run_one = True

    # 得到有多少个确定的数字
    def get_num_count(self):
        return sum(map(lambda x: 1 if isinstance(x, int) else 0, self.value.reshape(1, -1)[0]))

    # 评分，找到最佳的猜测坐标
    def get_best_point(self):
        best_score = 0
        best_point = (0, 0)

        for r, row in enumerate(self.value):
            for c, item in enumerate(row):
                point_score = self._get_point_score((r, c))
                if best_score < point_score:
                    best_score = point_score
                    best_point = (r, c)
        return best_point

    # 计算某坐标的评分
    def _get_point_score(self, point):
        # 评分标准 (10-候选个数) + 同行确定数字个数 + 同列确定数字个数
        r, c = point
        item = self.value[r, c]

        if isinstance(item, list):
            score = 10 - len(item)
            score += sum(map(lambda x: 1 if isinstance(x, int)
                             else 0, self.value[r]))
            score += sum(map(lambda x: 1 if isinstance(x, int)
                             else 0, self.value[:, c]))
            return score
        else:
            return 0

    # 验证有没错误
    def check_value(self):
        # 行
        r = 0
        for row in self.value:
            nums = []
            lists = []
            for item in row:
                (lists if isinstance(item, list) else nums).append(item)
            if len(set(nums)) != len(nums):
                # logger.error(f'verify failed. dup in row {r}')
                logger.debug('verify failed. dup in row {}'.format(r))
                return False  # 数字要不重复
            if len(list(filter(lambda x: len(x) == 0, lists))):
                return False  # 候选列表不能为空集
            r += 1

        # 列
        for c in range(0, 9):
            nums = []
            lists = []
            col = self.value[:, c]

            for item in col:
                (lists if isinstance(item, list) else nums).append(item)
            if len(set(nums)) != len(nums):
                logger.debug('verify failed. dup in col {}'.format(c))
                return False  # 数字要不重复
            if len(list(filter(lambda x: len(x) == 0, lists))):
                return False  # 候选列表不能为空集

        # 九宫格
        for b_r, b_c in self.base_points:
            nums = []
            lists = []
            block = self.value[b_r:b_r + 3, b_c:b_c + 3].reshape(1, -1)[0]

            for item in block:
                (lists if isinstance(item, list) else nums).append(item)
            if len(set(nums)) != len(nums):
                logger.debug(
                    'verify failed. dup in block {}'.format((b_r, b_c)))
                return False  # 数字要不重复
            if len(list(filter(lambda x: len(x) == 0, lists))):
                return False  # 候选列表不能为空集
        return True

    # 猜测记录
    def record_guess(self, point, index=0):
        # 记录
        recorder = Recorder()
        recorder.point = point
        recorder.point_index = index
        # recorder.value = self.value.copy() #numpy的copy不行
        recorder.value = copy.deepcopy(self.value)
        self.recorder.put(recorder)
        logger.debug('added to LIFO queue: {}'.format(
            [x.point for x in self.recorder.queue]))
        self.guess_times += 1  # 记录猜测次数

        # 新一轮的排除处理
        item = self.value[point]
        # assume only 1 in this point
        self.value[point] = item[index]
        self.new_points.put(point)
        logger.debug(
            'guessing: answer={}/{} @{}'.format(self.value[point], item, point))
        self.sudo_exclude()

    # 回溯，需要先进后出
    def recall(self):
        while True:
            if self.recorder.empty():
                raise Exception('Sudo is wrong, no answer!')
            else:
                recorder = self.recorder.get()
                point = recorder.point
                index = recorder.point_index + 1
                item = recorder.value[point]

                # 判断索引是否超出范围
                # if not exceed，则再回溯一次
                if index < len(item):
                    break
                # if exceed, pop next recorder
                logger.debug(f'Recall! Try previous point.')

        logger.debug(
            'Recall! Try next possible in same point, {} @{}'.format(item[index], point))
        self.value = recorder.value
        self.record_guess(point, index)

    # Main function 解题
    def sudo_solve(self):
        # 第一次解题，排除法
        logger.debug('excluding knowning answers')
        self.sudo_exclude()
        logger.debug('excluded, current result:\n{}'.format(self.value))

        # 检查有没错误的，有错误的则回溯；没错误却未解开题目，则再猜测
        while True:
            if self.check_value():
                fixed_answer = self.get_num_count()
                logger.debug(
                    'current no. of fixed answers: {}'.format(fixed_answer))
                if fixed_answer == 81:
                    break
                else:
                    # 获取最佳猜测点
                    point = self.get_best_point()
                    logger.debug(
                        'Adding new guessing in LIFO, {}'.format(point))

                    # 记录并处理
                    self.record_guess(point)
                    logger.debug(
                        'guessed, current result:\n{}'.format(self.value))
            else:
                # 出错，则回溯，尝试下一个猜测
                self.recall()


def sudoku_generate(mask_rate=0.5):
    while True:
        n = 9
        m = np.zeros((n, n), np.int)
        rg = np.arange(1, n + 1)
        m[0, :] = np.random.choice(rg, n, replace=False)
        try:
            for r in range(1, n):
                for c in range(n):
                    col_rest = np.setdiff1d(rg, m[:r, c])
                    row_rest = np.setdiff1d(rg, m[r, :c])
                    avb1 = np.intersect1d(col_rest, row_rest)
                    sub_r, sub_c = r // 3, c // 3
                    avb2 = np.setdiff1d(np.arange(0, n + 1),
                                        m[sub_r * 3:(sub_r + 1) * 3, sub_c * 3:(sub_c + 1) * 3].ravel())
                    avb = np.intersect1d(avb1, avb2)
                    m[r, c] = np.random.choice(avb, size=1)
            break
        except ValueError:
            pass

    mm = m.copy()
    mm[np.random.choice([True, False], size=m.shape, p=[
                        mask_rate, 1 - mask_rate])] = 0

    return mm


def sudoku_check_solution(m):
    if isinstance(m, list):
        m = np.array(m)
    elif isinstance(m, str):
        m = np.loadtxt(m, dtype=np.int, delimiter=",")
    set_rg = set(np.arange(1, m.shape[0] + 1))
    no_good = False
    for i in range(m.shape[0]):
        for j in range(m.shape[1]):
            r1 = set(m[3 * (i // 3):3 * (i // 3 + 1), 3 * (j // 3)                       :3 * (j // 3 + 1)].ravel()) == set_rg
            r2 = set(m[i, :]) == set_rg
            r3 = set(m[:, j]) == set_rg
            if not (r1 and r2 and r3):
                no_good = True
                break
        if no_good:
            break
    if no_good:
        logger.info("Checked: not good")
    else:
        logger.info("Checked: OK")

    return not no_good


def sudoku_solve_solution1(array):
    sudo = Sudoku(array)
    sudo.sudo_solve()
    return sudo.value


def sudoku_solve_solution2(array):
    if isinstance(array, list):
        array = np.array(array)
    elif isinstance(array, str):
        array = np.loadtxt(array, dtype=np.int, delimiter=",")
    rg = np.arange(array.shape[0] + 1)
    while True:
        mt = array.copy()
        while True:
            d = []
            d_len = []
            for i in range(array.shape[0]):
                for j in range(array.shape[1]):
                    if mt[i, j] == 0:
                        possibles = np.setdiff1d(rg, np.union1d(np.union1d(mt[i, :], mt[:, j]),
                                                                mt[3 * (i // 3):3 * (i // 3 + 1),
                                                                   3 * (j // 3):3 * (j // 3 + 1)]))
                        d.append([i, j, possibles])
                        d_len.append(len(possibles))
            if len(d) == 0:
                break
            idx = np.argmin(d_len)
            i, j, p = d[idx]
            if len(p) > 0:
                num = np.random.choice(p)
            else:
                break
            mt[i, j] = num
            if len(d) == 0:
                break
        if np.all(mt != 0):
            break

    return mt


def sudoku_solve_solution(array, method=1):
    if method == 1:
        return sudoku_solve_solution1(array)
    else:
        return sudoku_solve_solution2(array)
