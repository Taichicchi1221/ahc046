# author:  Taichicchi
# created: 26.04.2025 15:00:00

import copy
import random
import sys
import time
from collections import deque
from typing import List, Optional, Tuple

# -------------------- constants --------------------
N = 20
M = 40
MAX_ACTIONS = 1600
DIRS = {"U": (-1, 0), "D": (1, 0), "L": (0, -1), "R": (0, 1)}
DIR_KEYS = list(DIRS)  # deterministic order
INF = 10**9


random.seed(42)

# -------------------- time keeper --------------------


class TimeKeeper:
    def __init__(self, timeout: float = 1.5):
        self.start_time = time.perf_counter()
        self.timeout = timeout

    def elapsed_time(self):
        return time.perf_counter() - self.start_time

    def is_timeout(self):
        return self.elapsed_time() > self.timeout


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


# -------------------- BFS helper --------------------
def bfs_shortest(
    grid: List[List[bool]],
    N: int,
    start: Tuple[int, int],
    target: Tuple[int, int],
) -> Optional[List[Tuple[str, str]]]:
    """Find shortest sequence of (act, dir) using only M and S from start to target."""
    if start == target:
        return []
    visited = [[False] * N for _ in range(N)]
    prev = {}  # (i,j) -> ((pi,pj), act, dir)
    dq = deque()
    visited[start[0]][start[1]] = True
    dq.append(start)

    while dq:
        ci, cj = dq.popleft()
        # try both actions
        for act in ("M", "S"):
            for dir in DIR_KEYS:
                di, dj = DIRS[dir]
                if act == "M":
                    ni, nj = ci + di, cj + dj
                    if not (0 <= ni < N and 0 <= nj < N):
                        continue
                    if grid[ni][nj]:
                        continue
                else:  # act == "S"
                    # slide until boundary or block
                    ni, nj = ci, cj
                    while True:
                        ti, tj = ni + di, nj + dj
                        if not (0 <= ti < N and 0 <= tj < N):
                            break
                        if grid[ti][tj]:
                            break
                        ni, nj = ti, tj
                if (ni, nj) == (ci, cj):
                    continue  # zero-length slide
                if not visited[ni][nj]:
                    visited[ni][nj] = True
                    prev[(ni, nj)] = ((ci, cj), act, dir)
                    if (ni, nj) == target:
                        # reconstruct path
                        path = []
                        cur = (ni, nj)
                        while cur != start:
                            p, a, d = prev[cur]
                            path.append((a, d))
                            cur = p
                        return list(reversed(path))
                    dq.append((ni, nj))
    return None


# -------------------- main routine (greedy baseline) --------------------


def main():
    time_keeper = TimeKeeper(timeout=1.8)

    input()  # skip
    start = tuple(map(int, input().split()))
    coords = [tuple(map(int, input().split())) for _ in range(M - 1)]

    state = State(N, start, coords)

    steps = []
    while not state.is_done():
        tgt = state.target
        # handle already at target
        if state.pos == tgt:
            state._visited += 1
            continue

        path = bfs_shortest(state.grid, state.N, state.pos, tgt)
        if path is None:
            break  # unreachable
        for act, dir in path:
            state.apply_action(act, dir)
            steps.append(copy.deepcopy(state))
            if len(state.actions) >= MAX_ACTIONS:
                break
        if len(state.actions) >= MAX_ACTIONS:
            break

    states = [state]
    while not time_keeper.is_timeout():
        dir = random.choice(DIR_KEYS)
        step = random.randint(0, len(steps) - 1)
        state = copy.deepcopy(steps[step])

        if state.can_apply("A", dir):
            state.apply_action("A", dir)
            while not state.is_done():
                tgt = state.target
                # handle already at target
                if state.pos == tgt:
                    state._visited += 1
                    continue

                path = bfs_shortest(state.grid, state.N, state.pos, tgt)
                if path is None:
                    break  # unreachable
                for act, dir in path:
                    state.apply_action(act, dir)
                    if len(state.actions) >= MAX_ACTIONS:
                        break
                if len(state.actions) >= MAX_ACTIONS:
                    break
            states.append(state)

    # Choose the best state among state1, state2, state3, state4, state5
    best_state = max(states, key=lambda s: s.calculate_score())
    score = best_state.calculate_score()

    print(f"score {score}", file=sys.stderr)
    best_state.output_actions()


if __name__ == "__main__":
    main()
