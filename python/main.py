# author:  Taichicchi
# created: 26.04.2025 15:00:00

import sys
from collections import deque
from typing import List, Optional, Tuple

# -------------------- constants --------------------
N = 20
M = 40
MAX_ACTIONS = 1600
DIRS = {"U": (-1, 0), "D": (1, 0), "L": (0, -1), "R": (0, 1)}
DIR_KEYS = list(DIRS)  # deterministic order
INF = 10**9


# -------------------- State class --------------------
class State:
    """
    Holds the current rink state and action history.

    Attributes
    ----------
    grid[i][j] : bool
        True if a block occupies the cell.
    pos : tuple[int, int]
        Current position.
    coords : list[tuple[int, int]]
        The ordered list of destination cells.
    actions : list[tuple[str,str]]
        History of executed (action, direction) pairs.
    _visited : int
        Number of destinations already visited.
    """

    def __init__(self, N: int, start: Tuple[int, int], coords: List[Tuple[int, int]]):
        self.N = N
        # False: empty, True: has block
        self.grid = [[False] * N for _ in range(N)]
        self.pos = start
        self.coords = coords
        self.actions: List[Tuple[str, str]] = []
        self._visited = 0

    # ---------- convenience properties ----------
    @property
    def visited(self) -> int:
        """Number of destinations already visited."""
        return self._visited

    @property
    def target(self) -> Optional[Tuple[int, int]]:
        """Next destination cell, or None if all done."""
        return None if self._visited >= len(self.coords) else self.coords[self._visited]

    # ---------- helpers ----------
    def in_bounds(self, i: int, j: int) -> bool:
        return 0 <= i < self.N and 0 <= j < self.N

    def can_apply(self, act: str, dir: str) -> bool:
        if act not in ("M", "S", "A") or dir not in DIRS:
            return False
        di, dj = DIRS[dir]
        ci, cj = self.pos
        if act == "M":
            ni, nj = ci + di, cj + dj
            return self.in_bounds(ni, nj) and not self.grid[ni][nj]
        if act == "S":
            return True  # always allowed (0‑length slide OK)
        if act == "A":
            ti, tj = ci + di, cj + dj
            return self.in_bounds(ti, tj)
        return False

    # ---------- core ----------
    def apply_action(self, act: str, dir: str) -> None:
        """Apply an action that has already been verified with can_apply."""
        if not self.can_apply(act, dir):
            raise ValueError(f"Invalid or impossible action: {act} {dir}")
        di, dj = DIRS[dir]
        if act == "M":
            ni, nj = self.pos[0] + di, self.pos[1] + dj
            self.pos = (ni, nj)
            # count visit only for M step
            if self.target is not None and self.pos == self.target:
                self._visited += 1
        elif act == "S":
            i, j = self.pos
            while True:
                ni, nj = i + di, j + dj
                if not self.in_bounds(ni, nj) or self.grid[ni][nj]:
                    break
                i, j = ni, nj
            self.pos = (i, j)
            # count visit only for M step
            if self.target is not None and self.pos == self.target:
                self._visited += 1
        else:  # act == "A"
            ti, tj = self.pos[0] + di, self.pos[1] + dj
            self.grid[ti][tj] = not self.grid[ti][tj]
        self.actions.append((act, dir))

    # ---------- misc ----------
    def is_done(self) -> bool:
        return self.target is None

    def output_actions(self):
        for act, dir in self.actions:
            print(act, dir)

    def calculate_score(self) -> int:
        if not self.is_done():
            return len(self.actions) + 1
        return M + 2 * N * M - len(self.actions)


# -------------------- path‑finder --------------------


def shortest_actions(state: State) -> List[Tuple[str, str]]:
    """Return shortest (act,dir) sequence from current pos to state.target using only M/S."""
    if state.target is None:
        return []

    N = state.N
    gx, gy = state.target
    sx, sy = state.pos

    # slide only
    for d in DIR_KEYS:
        i, j = sx, sy
        while True:
            ni, nj = i + DIRS[d][0], j + DIRS[d][1]
            if not (0 <= ni < N and 0 <= nj < N) or state.grid[ni][nj]:
                break
            i, j = ni, nj
        if (i, j) == (gx, gy):
            return [("S", d)]

    # dist[i][j][k]: min steps to (i,j) with last_is_move==k(0: S, 1: M)
    dist = [[[INF] * 2 for _ in range(N)] for _ in range(N)]
    par = [[[(None, None, None, None)] * 2 for _ in range(N)] for _ in range(N)]
    dq = deque()
    dist[sx][sy][1] = 0
    dq.append((sx, sy, 1))

    while dq:
        x, y, lm = dq.popleft()
        if (x, y) == (gx, gy) and lm == 1:
            break
        # explore four dirs
        for d in DIR_KEYS:
            dx, dy = DIRS[d]
            # Move M
            nx, ny = x + dx, y + dy
            if 0 <= nx < N and 0 <= ny < N and not state.grid[nx][ny] and dist[nx][ny][1] == INF:
                dist[nx][ny][1] = dist[x][y][lm] + 1
                par[nx][ny][1] = (x, y, lm, "M", d)
                dq.append((nx, ny, 1))
            # Slide S
            sx2, sy2 = x, y
            while True:
                tx, ty = sx2 + dx, sy2 + dy
                if not (0 <= tx < N and 0 <= ty < N) or state.grid[tx][ty]:
                    break
                sx2, sy2 = tx, ty
            if dist[sx2][sy2][0] == INF:
                dist[sx2][sy2][0] = dist[x][y][lm] + 1
                par[sx2][sy2][0] = (x, y, lm, "S", d)
                dq.append((sx2, sy2, 0))

    if dist[gx][gy][1] == INF:
        raise RuntimeError("No path found with M/S only (should not happen)")

    # reconstruct
    actions: List[Tuple[str, str]] = []
    x, y, lm = gx, gy, 1
    while (x, y, lm) != (sx, sy, 1):
        px, py, plm, act, dir_ = par[x][y][lm]
        actions.append((act, dir_))
        x, y, lm = px, py, plm
    actions.reverse()
    return actions


# -------------------- main routine (greedy baseline) --------------------


def main():
    N, M = map(int, input().split())
    start = tuple(map(int, input().split()))
    coords = [tuple(map(int, input().split())) for _ in range(M - 1)]

    st = State(N, start, coords)

    while not st.is_done():
        seq = shortest_actions(st)
        for act, dir_ in seq:
            st.apply_action(act, dir_)

    # 出力
    st.output_actions()

    score = st.calculate_score()
    print(f"score {score}", file=sys.stderr)


if __name__ == "__main__":
    main()
