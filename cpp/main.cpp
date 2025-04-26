#include <bits/stdc++.h>
using namespace std;

// -------------------- constants --------------------
constexpr int N = 20;
constexpr int M = 40;
constexpr int MAX_ACTIONS = 1600;
constexpr int INF = 1e9;

const vector<pair<string, pair<int, int>>> DIRS = {
    {"U", {-1, 0}},
    {"D", {1, 0}},
    {"L", {0, -1}},
    {"R", {0, 1}}};
const vector<string> DIR_KEYS = {"U", "D", "L", "R"};

// -------------------- random --------------------
mt19937 rng(42);

// -------------------- time keeper --------------------
struct TimeKeeper {
    chrono::high_resolution_clock::time_point start_time;
    double timeout;
    TimeKeeper(double timeout = 1.5) : start_time(chrono::high_resolution_clock::now()), timeout(timeout) {}
    double elapsed_time() const {
        auto now = chrono::high_resolution_clock::now();
        return chrono::duration<double>(now - start_time).count();
    }
    bool is_timeout() const {
        return elapsed_time() > timeout;
    }
};

// -------------------- State class --------------------
struct State {
    int N;
    vector<vector<bool>> grid;
    pair<int, int> start;
    pair<int, int> pos;
    vector<pair<int, int>> coords;
    vector<pair<string, string>> actions;
    int _visited;

    State(int N_, pair<int, int> start_, const vector<pair<int, int>>& coords_)
        : N(N_), grid(N_, vector<bool>(N_, false)), start(start_), pos(start_), coords(coords_), actions(), _visited(0) {}

    int visited() const { return _visited; }
    optional<pair<int, int>> target() const {
        if (_visited >= (int)coords.size()) return nullopt;
        return coords[_visited];
    }
    bool in_bounds(int i, int j) const {
        return 0 <= i && i < N && 0 <= j && j < N;
    }
    bool can_apply(const string& act, const string& dir) const {
        if ((act != "M" && act != "S" && act != "A")) return false;
        auto it = find(DIR_KEYS.begin(), DIR_KEYS.end(), dir);
        if (it == DIR_KEYS.end()) return false;
        int di = 0, dj = 0;
        for (auto& d : DIRS)
            if (d.first == dir) tie(di, dj) = d.second;
        int ci = pos.first, cj = pos.second;
        if (act == "M") {
            int ni = ci + di, nj = cj + dj;
            return in_bounds(ni, nj) && !grid[ni][nj];
        }
        if (act == "S") {
            return true;
        }
        if (act == "A") {
            int ti = ci + di, tj = cj + dj;
            return in_bounds(ti, tj);
        }
        return false;
    }
    void apply_action(const string& act, const string& dir) {
        if (!can_apply(act, dir)) throw runtime_error("Invalid or impossible action: " + act + " " + dir);
        int di = 0, dj = 0;
        for (auto& d : DIRS)
            if (d.first == dir) tie(di, dj) = d.second;
        if (act == "M") {
            int ni = pos.first + di, nj = pos.second + dj;
            pos = {ni, nj};
            auto tgt = target();
            if (tgt && pos == *tgt) _visited++;
        } else if (act == "S") {
            int i = pos.first, j = pos.second;
            while (true) {
                int ni = i + di, nj = j + dj;
                if (!in_bounds(ni, nj) || grid[ni][nj]) break;
                i = ni;
                j = nj;
            }
            pos = {i, j};
            auto tgt = target();
            if (tgt && pos == *tgt) _visited++;
        } else {  // act == "A"
            int ti = pos.first + di, tj = pos.second + dj;
            grid[ti][tj] = !grid[ti][tj];
        }
        actions.emplace_back(act, dir);
    }
    bool is_done() const {
        return !target().has_value();
    }
    void output_actions() const {
        for (auto& [act, dir] : actions) {
            cout << act << " " << dir << endl;
        }
    }
    int calculate_score() const {
        if (!is_done()) return actions.size() + 1;
        return M + 2 * N * M - (int)actions.size();
    }
};

vector<State> recall_steps(const State& state) {
    State st(state.N, state.start, state.coords);
    vector<State> steps = {st};
    for (auto& [act, dir] : state.actions) {
        st.apply_action(act, dir);
        steps.push_back(st);
    }
    return steps;
}

// -------------------- BFS helper --------------------
optional<vector<pair<string, string>>> bfs_shortest(
    const vector<vector<bool>>& grid,
    int N,
    pair<int, int> start,
    pair<int, int> target) {
    if (start == target) return vector<pair<string, string>>();
    vector<vector<bool>> visited(N, vector<bool>(N, false));
    map<pair<int, int>, tuple<pair<int, int>, string, string>> prev;
    deque<pair<int, int>> dq;
    visited[start.first][start.second] = true;
    dq.push_back(start);

    while (!dq.empty()) {
        auto [ci, cj] = dq.front();
        dq.pop_front();
        for (const string& act : {"M", "S"}) {
            for (const auto& d : DIRS) {
                string dir = d.first;
                int di = d.second.first, dj = d.second.second;
                int ni = ci, nj = cj;
                if (act == "M") {
                    ni = ci + di;
                    nj = cj + dj;
                    if (!(0 <= ni && ni < N && 0 <= nj && nj < N)) continue;
                    if (grid[ni][nj]) continue;
                } else {  // "S"
                    ni = ci;
                    nj = cj;
                    while (true) {
                        int ti = ni + di, tj = nj + dj;
                        if (!(0 <= ti && ti < N && 0 <= tj && tj < N)) break;
                        if (grid[ti][tj]) break;
                        ni = ti;
                        nj = tj;
                    }
                }
                if (ni == ci && nj == cj) continue;
                if (!visited[ni][nj]) {
                    visited[ni][nj] = true;
                    prev[{ni, nj}] = make_tuple(make_pair(ci, cj), act, dir);
                    if (make_pair(ni, nj) == target) {
                        vector<pair<string, string>> path;
                        pair<int, int> cur = {ni, nj};
                        while (cur != start) {
                            auto [p, a, d] = prev[cur];
                            path.emplace_back(a, d);
                            cur = p;
                        }
                        reverse(path.begin(), path.end());
                        return path;
                    }
                    dq.emplace_back(ni, nj);
                }
            }
        }
    }
    return nullopt;
}

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    TimeKeeper time_keeper1(0.6);
    TimeKeeper time_keeper2(1.2);
    TimeKeeper time_keeper3(1.8);

    string dummy;
    getline(cin, dummy);  // skip
    int si, sj;
    cin >> si >> sj;
    vector<pair<int, int>> coords;
    for (int i = 0; i < M - 1; ++i) {
        int x, y;
        cin >> x >> y;
        coords.emplace_back(x, y);
    }

    State state(N, {si, sj}, coords);
    while (!state.is_done()) {
        auto tgt = state.target();
        if (state.pos == *tgt) {
            state._visited++;
            continue;
        }
        auto path = bfs_shortest(state.grid, state.N, state.pos, *tgt);
        if (!path) break;
        for (auto& [act, d] : *path) {
            state.apply_action(act, d);
            if ((int)state.actions.size() >= MAX_ACTIONS) break;
        }
        if ((int)state.actions.size() >= MAX_ACTIONS) break;
    }

    auto steps = recall_steps(state);

    // d = 1
    vector<State> states = {state};
    while (!time_keeper1.is_timeout()) {
        string dir = DIR_KEYS[rng() % DIR_KEYS.size()];
        int step = uniform_int_distribution<int>(0, (int)steps.size() - 1)(rng);
        State st = steps[step];
        if (st.can_apply("A", dir)) {
            st.apply_action("A", dir);
            while (!st.is_done()) {
                auto tgt = st.target();
                if (st.pos == *tgt) {
                    st._visited++;
                    continue;
                }
                auto path = bfs_shortest(st.grid, st.N, st.pos, *tgt);
                if (!path) break;
                for (auto& [act, d] : *path) {
                    st.apply_action(act, d);
                    if ((int)st.actions.size() >= MAX_ACTIONS) break;
                }
                if ((int)st.actions.size() >= MAX_ACTIONS) break;
            }
            states.push_back(st);
        }
    }

    auto best_state = *max_element(states.begin(), states.end(), [](const State& a, const State& b) {
        return a.calculate_score() < b.calculate_score();
    });
    steps = recall_steps(best_state);

    // d = 2
    states = {best_state};
    while (!time_keeper2.is_timeout()) {
        string dir = DIR_KEYS[rng() % DIR_KEYS.size()];
        int step = uniform_int_distribution<int>(0, (int)steps.size() - 1)(rng);
        State st = steps[step];
        if (st.can_apply("A", dir)) {
            st.apply_action("A", dir);
            while (!st.is_done()) {
                auto tgt = st.target();
                if (st.pos == *tgt) {
                    st._visited++;
                    continue;
                }
                auto path = bfs_shortest(st.grid, st.N, st.pos, *tgt);
                if (!path) break;
                for (auto& [act, d] : *path) {
                    st.apply_action(act, d);
                    if ((int)st.actions.size() >= MAX_ACTIONS) break;
                }
                if ((int)st.actions.size() >= MAX_ACTIONS) break;
            }
            states.push_back(st);
        }
    }

    best_state = *max_element(states.begin(), states.end(), [](const State& a, const State& b) {
        return a.calculate_score() < b.calculate_score();
    });
    steps = recall_steps(best_state);

    // d = 3
    states = {best_state};
    while (!time_keeper3.is_timeout()) {
        string dir = DIR_KEYS[rng() % DIR_KEYS.size()];
        int step = uniform_int_distribution<int>(0, (int)steps.size() - 1)(rng);
        State st = steps[step];
        if (st.can_apply("A", dir)) {
            st.apply_action("A", dir);
            while (!st.is_done()) {
                auto tgt = st.target();
                if (st.pos == *tgt) {
                    st._visited++;
                    continue;
                }
                auto path = bfs_shortest(st.grid, st.N, st.pos, *tgt);
                if (!path) break;
                for (auto& [act, d] : *path) {
                    st.apply_action(act, d);
                    if ((int)st.actions.size() >= MAX_ACTIONS) break;
                }
                if ((int)st.actions.size() >= MAX_ACTIONS) break;
            }
            states.push_back(st);
        }
    }

    best_state = *max_element(states.begin(), states.end(), [](const State& a, const State& b) {
        return a.calculate_score() < b.calculate_score();
    });

    int score = best_state.calculate_score();

    // 出力
    cerr << "score " << score << endl;
    best_state.output_actions();

    return 0;
}