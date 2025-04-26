# author:  Taichicchi
# created: 26.04.2025 15:00:00

import sys

N = 20
M = 40


class State:
    """
    スケートリンクの状態とこれまでの行動履歴を保持するクラス
    - grid[i][j] が True の場合、そのマスにブロックが存在する
    - pos は現在位置 (i, j)
    - coords は目的地の座標リスト
    - actions は実行した (action, direction) のタプルのリスト
    """

    def __init__(self, N: int, start: tuple[int, int], coords: list[tuple[int, int]]):
        self.N = N
        # False: 空きマス, True: ブロック
        self.grid = [[False] * N for _ in range(N)]
        # 現在位置
        self.pos = start
        # 目的地
        self.coords = coords
        # 行動履歴
        self.actions: list[tuple[str, str]] = []
        # すでに訪れた目的地の数
        self.visited = 0

    def in_bounds(self, i: int, j: int) -> bool:
        return 0 <= i < self.N and 0 <= j < self.N

    def can_apply(self, act: str, dir: str) -> bool:
        """
        指定の行動を現在の状態で実行可能かチェックする
        """
        deltas = {"U": (-1, 0), "D": (1, 0), "L": (0, -1), "R": (0, 1)}
        if act not in ("M", "S", "A") or dir not in deltas:
            return False

        di, dj = deltas[dir]
        ci, cj = self.pos

        if act == "M":
            ni, nj = ci + di, cj + dj
            return self.in_bounds(ni, nj) and not self.grid[ni][nj]

        elif act == "S":
            # 滑走は常に実行可能（何も動かなくても許容）
            return True

        elif act == "A":
            ti, tj = ci + di, cj + dj
            return self.in_bounds(ti, tj)

        return False

    def apply_action(self, act: str, dir: str):
        if not self.can_apply(act, dir):
            raise ValueError(f"Invalid action or cannot apply: {act} {dir}")

        deltas = {"U": (-1, 0), "D": (1, 0), "L": (0, -1), "R": (0, 1)}
        di, dj = deltas[dir]

        # 移動
        if act == "M":
            ni, nj = self.pos[0] + di, self.pos[1] + dj
            self.pos = (ni, nj)
            # 移動後に「次の」目的地と一致すれば visited をインクリメント
            if self.visited < len(self.coords) and self.pos == self.coords[self.visited]:
                self.visited += 1

        # 滑走
        elif act == "S":
            i, j = self.pos
            while True:
                ni, nj = i + di, j + dj
                if not self.in_bounds(ni, nj) or self.grid[ni][nj]:
                    break
                i, j = ni, nj
            self.pos = (i, j)

        # 変更
        elif act == "A":
            ti, tj = self.pos[0] + di, self.pos[1] + dj
            self.grid[ti][tj] = not self.grid[ti][tj]

        self.actions.append((act, dir))

    def output_actions(self):
        """
        行動履歴を出力する
        """
        for act, dir in self.actions:
            print(act, dir)

    def calculate_score(self) -> int:
        """
        スコアを計算する
        """
        T = len(self.actions)
        # すでに self.visited に目的地達成数が入っているので直接使う
        if self.visited < M - 1:
            return self.visited + 1
        else:
            return M + 2 * N * M - T


def main():
    input()  # 読み飛ばし

    start = tuple(map(int, input().split()))
    coords = [tuple(map(int, input().split())) for _ in range(M - 1)]

    state = State(N, start, coords)

    # M（移動）のみで目的地を順番に回る
    for ti, tj in coords:
        # 現在地が目的地と一致するまで1マスずつ移動
        while state.pos != (ti, tj):
            ci, cj = state.pos
            if ci < ti:
                dir = "D"
            elif ci > ti:
                dir = "U"
            elif cj < tj:
                dir = "R"
            else:
                dir = "L"

            # State クラスで状態更新＆行動履歴に記録
            state.apply_action("M", dir)

    state.output_actions()
    score = state.calculate_score()
    print(f"score {score}", file=sys.stderr)


if __name__ == "__main__":
    main()
