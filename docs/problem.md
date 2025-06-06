### **問題文**

\( N \times N \) のマス目からなるスケートリンクがある。左上のマスの座標を \( (0, 0) \) とし、下方向に \( i \) マス、右方向に \( j \) マス進んだ位置のマスの座標を \( (i, j) \) とする。  
\( N \times N \) マスの外部はすべてブロックで覆われており、通過できない。初期状態では、\( N \times N \) マスの内部にブロックは存在しない。

あなたは初期位置 \( (i*0, j_0) \) におり、指定された目的地 \( (i_1, j_1), \dots, (i*{M-1}, j\_{M-1}) \) をこの順番で訪れたい。

各ターンでは、上下左右のいずれかの方向を指定し、以下のいずれかの行動を 1 つ選んで実行できる。

- **移動**：指定した方向に隣接するマスへ 1 マス移動する。移動先がブロックであってはならない。
- **滑走**：指定した方向へ、ブロックにぶつかるまで直線的に滑走する。
- **変更**：指定した方向に隣接するマスに対し、ブロックが置かれていなければ設置し、すでに置かれていれば除去する。  
  　\( N \times N \) マスの外部は指定できない。なお、現在の目的地や将来の目的地にブロックを設置することも可能であるが、その場合、そのマスを訪れるにはブロックを除去する必要がある。

「滑走」によって目的地の上を通過した場合、そのマスを訪れたとはみなされない。目的地を訪れたと判定されるには、「移動」でそのマスに到達する必要がある。

目的地は指定された順番通りに訪れる必要がある。順番よりも後の目的地を先に通過しても、その時点では訪れたとはみなされない。順番が来たときに、あらためてそのマスを訪れる必要がある。

行動は最大 \( 2NM \) ターンまで行える。出来る限り少ないターン数ですべての目的地を指定された順に訪れよ。

---

### **得点**

出力した行動列の長さを \( T \)、訪れることが出来た目的地の数を \( m \) としたとき、以下のスコアが得られる。

- \( m < M - 1 \) の場合、\( m + 1 \)
- \( m = M - 1 \) の場合、\( M + 2NM - T \)

合計で 150 個のテストケースがあり、各テストケースの得点の合計が提出の得点となる。一つ以上のテストケースで不正な出力や制限時間超過をした場合、提出全体の判定が `WA` や `TLE` となる。  
コンテスト時間中に得た最高得点で最終順位が決定され、コンテスト終了後のシステムテストは行われない。同じ得点を複数の参加者が得た場合、提出時刻に関わらず同じ順位となる。

---

### **入力**

入力は以下の形式で標準入力から与えられる。

```
N M
i₀ j₀
…
i_{M−1} j_{M−1}
```

- 全てのテストケースにおいて、\( N = 20, M = 40 \) に固定されている。
- 初期位置および目的地の座標 \( (i_k, j_k) \) は、\( 0 \leq i_k, j_k < N \) を満たす整数であり、すべて相異なる。

---

### **出力**

各ターンに選択した行動と方向を、以下のようにアルファベット 1 文字ずつで表す。

#### 行動

- 移動：`M`
- 滑走：`S`
- 変更：`A`

#### 方向

- 上：`U`
- 下：`D`
- 左：`L`
- 右：`R`

\( t \) ターン目 (\( t = 0, 1, ..., T-1 \)) の行動と方向をそれぞれ \( a_t, d_t \) としたとき、以下の形式で標準出力に出力せよ。

```
a₀ d₀
…
a_{T−1} d_{T−1}
```
