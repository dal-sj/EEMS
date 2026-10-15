"""기획서(docs/proposal/README.md)에 들어가는 그림을 생성한다.

모든 그래프는 '개념도/가설'이며 실험 결과가 아니다.
합성 곡선은 이해를 돕기 위한 예시이고, 실제 수치는 실험 단계에서 다시 그린다.

실행: pip install matplotlib koreanize-matplotlib numpy && python make_figures.py
"""
from pathlib import Path

import koreanize_matplotlib  # noqa: F401  (NanumGothic 등록)
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Rectangle

OUT = Path(__file__).resolve().parents[1] / "images"
OUT.mkdir(parents=True, exist_ok=True)

# ---- 공통 스타일 (밝은 배경, 얇은 마크, 연한 그리드) ----
SURFACE = "#fcfcfb"
INK = "#0b0b0b"
INK2 = "#52514e"
MUTED = "#898781"
GRID = "#e1e0d9"
AXIS = "#c3c2b7"
BLUE, ORANGE, AQUA, YELLOW, MAGENTA, GREEN, VIOLET, RED = (
    "#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#6250d6", "#e34948",
)
BLUE_LIGHT = "#cde2fb"
BLUE_MID = "#86b6ef"

plt.rcParams.update({
    "figure.facecolor": SURFACE,
    "axes.facecolor": SURFACE,
    "axes.edgecolor": AXIS,
    "axes.labelcolor": INK2,
    "axes.titlecolor": INK,
    "axes.titleweight": "bold",
    "axes.titlesize": 13,
    "axes.grid": True,
    "grid.color": GRID,
    "grid.linewidth": 0.8,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "xtick.color": MUTED,
    "ytick.color": MUTED,
    "xtick.labelcolor": INK2,
    "ytick.labelcolor": INK2,
    "legend.frameon": False,
    "legend.labelcolor": INK2,
    "font.size": 11,
    "axes.unicode_minus": False,
    "savefig.dpi": 160,
    "savefig.bbox": "tight",
    "savefig.facecolor": SURFACE,
})


def note(fig, text):
    fig.text(0.99, 0.005, text, ha="right", va="bottom", fontsize=9, color=MUTED)


# ------------------------------------------------------------------
# 1. 핵심 동작 루프 (관측 → 예측 → 최적화 → 실행 → 학습)
# ------------------------------------------------------------------
def fig_concept_loop():
    fig, ax = plt.subplots(figsize=(10, 5.6))
    ax.set_xlim(-5, 5)
    ax.set_ylim(-3.05, 3.4)
    ax.axis("off")

    steps = [
        ("① 관측", "기기 전력·온도·\n사용자 조작 수집\n(1초~1분)", BLUE),
        ("② 예측", "앞으로 24시간의\n기저부하·기온·태양광\n(Edge AI 모델)", ORANGE),
        ("③ 최적화", "요금·DR·쾌적성을\n동시에 고려한\n24시간 운전계획 (MPC)", AQUA),
        ("④ 실행", "MCU로 제어 명령\n안전계층이 최종 검사", VIOLET),
        ("⑤ 학습", "예측오차·사용자\n거절(override)로\n모델·선호 갱신", YELLOW),
    ]
    r = 2.35
    angles = np.deg2rad([90, 18, -54, -126, 162])
    pos = [(r * 1.45 * np.cos(a), r * np.sin(a)) for a in angles]
    w, h = 2.55, 1.35
    boxes = []
    for (title, body, color), (x, y) in zip(steps, pos):
        box = FancyBboxPatch((x - w / 2, y - h / 2), w, h,
                             boxstyle="round,pad=0.02,rounding_size=0.18",
                             fc=SURFACE, ec=color, lw=2.2)
        ax.add_patch(box)
        boxes.append(box)
        ax.text(x, y + 0.36, title, ha="center", va="center", fontsize=13, weight="bold", color=INK)
        ax.text(x, y - 0.2, body, ha="center", va="center", fontsize=9, color=INK2, linespacing=1.3)

    for i in range(len(pos)):
        j = (i + 1) % len(pos)
        ax.add_patch(FancyArrowPatch(pos[i], pos[j], patchA=boxes[i], patchB=boxes[j],
                                     shrinkA=6, shrinkB=6, arrowstyle="-|>", mutation_scale=18,
                                     color=MUTED, lw=1.8, connectionstyle="arc3,rad=-0.15"))

    ax.add_patch(FancyBboxPatch((-1.35, -0.62), 2.7, 1.24,
                                boxstyle="round,pad=0.02,rounding_size=0.2",
                                fc=BLUE_LIGHT, ec="none"))
    ax.text(0, 0.18, "Edge Hub", ha="center", va="center", fontsize=14, weight="bold", color=INK)
    ax.text(0, -0.25, "Raspberry Pi · 15분마다 반복\n인터넷이 끊겨도 동작", ha="center",
            va="center", fontsize=9, color=INK2)

    ax.text(-5, 3.25, "외부 입력:  요금표 · 국민DR 발령 · 기상예보 · 사용자 설정(마감시각/쾌적범위)",
            fontsize=9.5, color=INK2, va="top")
    note(fig, "개념도")
    fig.savefig(OUT / "01_concept_loop.png")
    plt.close(fig)


# ------------------------------------------------------------------
# 2. 하루 부하 이동 개념 (제주 계시별 선택요금 시간대 배경)
# ------------------------------------------------------------------
def tou_bands(ax, ymax):
    bands = [(0, 8, "경부하", "#eef4fc"), (8, 16, "중간부하", "#f6f5f1"),
             (16, 22, "최대부하", "#fdeee7"), (22, 24, "경부하", "#eef4fc")]
    for s, e, label, c in bands:
        ax.add_patch(Rectangle((s, 0), e - s, ymax, color=c, zorder=0, lw=0))
        ax.text((s + e) / 2, ymax * 0.97, label, ha="center", va="top", fontsize=9, color=INK2)


def fig_load_shift():
    t = np.arange(0, 24, 0.25)
    rng = np.random.default_rng(3)
    base = (0.35 + 0.25 * np.exp(-((t - 7.5) / 1.2) ** 2) + 0.45 * np.exp(-((t - 19.5) / 2.0) ** 2)
            + 0.03 * rng.standard_normal(t.size))
    ac_before = np.where((t >= 14) & (t < 23), 1.1, 0.0)
    washer_before = np.where((t >= 19) & (t < 20.5), 0.9, 0.0)
    before = base + ac_before + washer_before

    ac_after = np.where((t >= 12) & (t < 16), 1.35, 0.0) + np.where((t >= 16) & (t < 23), 0.75, 0.0)
    washer_after = np.where((t >= 22.5) & (t < 24), 0.9, 0.0)
    after = base + ac_after + washer_after

    fig, ax = plt.subplots(figsize=(10, 4.6))
    ymax = 3.2
    tou_bands(ax, ymax)
    ax.plot(t, before, color=MUTED, lw=2, label="제어 전")
    ax.plot(t, after, color=BLUE, lw=2, label="제어 후 (제안 시스템)")
    ax.set_xlim(0, 24)
    ax.set_ylim(0, ymax)
    ax.set_xticks(range(0, 25, 3))
    ax.set_xlabel("시각 (시)")
    ax.set_ylabel("가구 전력 (kW)")
    ax.set_title("하루 부하 이동 개념: 같은 생활, 다른 시간표", loc="left")
    ax.legend(loc="upper left", bbox_to_anchor=(0, 0.9))

    ax.annotate("사전 냉방(pre-cooling)\n건물에 '냉기'를 저장", xy=(13.5, 2.05), xytext=(9.2, 2.55),
                fontsize=9, color=INK2, arrowprops=dict(arrowstyle="-", color=MUTED, lw=1))
    ax.annotate("세탁기 → 경부하로 이동\n(사용자 마감 07시 준수)", xy=(23.0, 2.0), xytext=(18.3, 0.45),
                fontsize=9, color=INK2, arrowprops=dict(arrowstyle="-", color=MUTED, lw=1))
    ax.annotate("피크 시간대 부하 ↓", xy=(18.6, 1.42), xytext=(16.2, 2.45),
                fontsize=9, color=INK2, arrowprops=dict(arrowstyle="-", color=MUTED, lw=1))
    ax.grid(axis="x", visible=False)
    note(fig, "개념 예시(합성 데이터) · 배경 시간대: 제주 주택용 계시별 선택요금 구분")
    fig.savefig(OUT / "02_load_shift_concept.png")
    plt.close(fig)


# ------------------------------------------------------------------
# 3. 요금 시나리오 3종 (작은 다중 그래프)
# ------------------------------------------------------------------
def fig_tariffs():
    fig, axes = plt.subplots(1, 3, figsize=(13, 3.9))

    ax = axes[0]
    edges = [0, 200, 400, 600]
    levels = [1.0, 1.8, 2.6]
    for i, lv in enumerate(levels):
        ax.add_patch(Rectangle((edges[i] + 2, 0), edges[i + 1] - edges[i] - 4, lv,
                               color=[BLUE_MID, "#3987e5", "#1c5cab"][i], lw=0))
        ax.text((edges[i] + edges[i + 1]) / 2, lv + 0.08, f"{i + 1}구간", ha="center", fontsize=9, color=INK2)
    ax.set_xlim(0, 600)
    ax.set_ylim(0, 3.1)
    ax.set_xticks([0, 200, 400, 600])
    ax.set_xlabel("월 사용량 (kWh)")
    ax.set_ylabel("상대 단가 (개념)")
    ax.set_title("S1 누진제 (현행 주택용)", loc="left")
    ax.text(5, 2.95, "하계(7~8월) 구간: 300 / 450 kWh", fontsize=8.5, color=MUTED, va="top")
    ax.grid(axis="x", visible=False)

    ax = axes[1]
    hours = np.arange(24)
    price = np.where((hours >= 16) & (hours < 22), 2.6, np.where((hours >= 8) & (hours < 16), 1.5, 1.0))
    colors = np.where(price > 2, "#1c5cab", np.where(price > 1.2, "#3987e5", BLUE_MID))
    ax.bar(hours + 0.5, price, width=0.88, color=colors, lw=0)
    ax.set_xlim(0, 24)
    ax.set_ylim(0, 3.1)
    ax.set_xticks(range(0, 25, 4))
    ax.set_xlabel("시각 (시)")
    ax.set_title("S2 계시별 (TOU)", loc="left")
    ax.text(19, 2.7, "최대부하", ha="center", fontsize=9, color=INK2)
    ax.text(12, 1.6, "중간", ha="center", fontsize=9, color=INK2)
    ax.text(4, 1.1, "경부하", ha="center", fontsize=9, color=INK2)
    ax.grid(axis="x", visible=False)

    ax = axes[2]
    t = np.arange(0, 24, 1)
    smp = 1.6 + 0.35 * np.cos((t - 3) / 24 * 2 * np.pi) - 0.75 * np.exp(-((t - 12.5) / 2.3) ** 2) \
        + 0.6 * np.exp(-((t - 19) / 1.6) ** 2)
    ax.step(np.append(t, 24), np.append(smp, smp[-1]), where="post", color=BLUE, lw=2)
    ax.set_xlim(0, 24)
    ax.set_ylim(0, 3.1)
    ax.set_xticks(range(0, 25, 4))
    ax.set_xlabel("시각 (시)")
    ax.set_title("S3 실시간 (SMP 연동, 가상)", loc="left")
    ax.annotate("태양광 많은 낮:\n가격 하락", xy=(12.5, 0.95), xytext=(5.0, 0.35), fontsize=9, color=INK2,
                arrowprops=dict(arrowstyle="-", color=MUTED, lw=1))
    ax.annotate("저녁 피크", xy=(19, 2.15), xytext=(19.5, 2.75), fontsize=9, color=INK2,
                arrowprops=dict(arrowstyle="-", color=MUTED, lw=1))

    fig.suptitle("요금 구조가 바뀌면 '최적의 행동'도 바뀐다", x=0.01, ha="left", fontsize=14,
                 weight="bold", color=INK)
    fig.tight_layout(rect=(0, 0.03, 1, 0.97))
    note(fig, "개념도 · 단가는 상대값(실험에서는 한전 요금표·KPX SMP 실측값 사용)")
    fig.savefig(OUT / "03_tariff_scenarios.png")
    plt.close(fig)


# ------------------------------------------------------------------
# 4. 커뮤니티 리바운드 피크
# ------------------------------------------------------------------
def fig_rebound():
    t = np.arange(0, 24, 0.25)
    base = 60 + 25 * np.exp(-((t - 8) / 1.5) ** 2) + 70 * np.exp(-((t - 20) / 2.2) ** 2)
    flex = 55 * np.exp(-((t - 20) / 1.6) ** 2)
    none = base + flex
    tt = np.where(t < 12, t + 24, t)
    indep = base + 110 * np.exp(-((tt - 22.6) / 0.55) ** 2) * (tt >= 22)
    coord = base + 22 * ((tt >= 22) & (tt < 30)) * (1 - 0.2 * np.abs((tt - 26) / 4))

    fig, ax = plt.subplots(figsize=(10, 4.6))
    ax.plot(t, none, color=MUTED, lw=2, label="무제어")
    ax.plot(t, indep, color=ORANGE, lw=2, label="집집마다 따로 최적화")
    ax.plot(t, coord, color=BLUE, lw=2, label="Aggregator 협조 최적화 (제안)")
    ax.axvspan(22, 24, color="#eef4fc", lw=0, zorder=0)
    ax.axvspan(0, 8, color="#eef4fc", lw=0, zorder=0)
    ax.text(23, 6, "경부하", ha="center", fontsize=9, color=INK2)
    ax.text(4, 6, "경부하", ha="center", fontsize=9, color=INK2)
    i = np.argmax(indep)
    ax.annotate("리바운드 피크:\n모두가 22시 '싼 시간'에 동시 시작", xy=(t[i], indep[i]),
                xytext=(11.0, 195), fontsize=9.5, color=INK2,
                arrowprops=dict(arrowstyle="-", color=MUTED, lw=1))
    ax.set_xlim(0, 24)
    ax.set_ylim(0, 230)
    ax.set_xticks(range(0, 25, 3))
    ax.set_xlabel("시각 (시)")
    ax.set_ylabel("단지 전체 전력 (kW, 100가구)")
    ax.set_title("왜 '단지 단위 협조'가 필요한가: 리바운드 피크", loc="left")
    ax.legend(loc="upper left")
    ax.grid(axis="x", visible=False)
    note(fig, "개념 예시(합성 데이터) · 실험 E5에서 실데이터로 검증")
    fig.savefig(OUT / "04_rebound_peak.png")
    plt.close(fig)


# ------------------------------------------------------------------
# 5. 예측 정확도의 가치 (가설)
# ------------------------------------------------------------------
def fig_value_of_forecast():
    e = np.linspace(0, 40, 200)
    mean = 100 * np.exp(-e / 28)
    lo, hi = mean - 4 - e * 0.25, np.minimum(100, mean + 4 + e * 0.25)
    fig, ax = plt.subplots(figsize=(8.5, 4.5))
    ax.fill_between(e, lo, hi, color=BLUE_LIGHT, lw=0, label="가설 범위")
    ax.plot(e, mean, color=BLUE, lw=2, label="가설 곡선")
    pts = [(0, "오라클(완벽 예측)\n= 이론 상한"), (8, "제안: Edge AI 예측"), (30, "단순 예측\n(어제 같은 시각)")]
    for x, lab in pts:
        y = 100 * np.exp(-x / 28)
        ax.plot([x], [y], "o", ms=9, mfc=BLUE, mec=SURFACE, mew=2, zorder=5)
        ax.annotate(lab, xy=(x, y), xytext=(x + 1.8, y + 6), fontsize=9.5, color=INK2)
    ax.axhline(70, color=AXIS, lw=1)
    ax.text(40, 71.5, "성공 기준: 오라클 대비 70%", ha="right", fontsize=9, color=MUTED)
    ax.set_xlim(0, 40)
    ax.set_ylim(0, 115)
    ax.set_xlabel("기저부하 예측 오차 (nMAE, %)")
    ax.set_ylabel("오라클 대비 절감 달성률 (%)")
    ax.set_title("AI가 '얼마나 정확해야' 돈이 되는가? (RQ4)", loc="left")
    ax.legend(loc="lower left")
    note(fig, "가설 그래프 — 실험 E3에서 실제 곡선으로 교체")
    fig.savefig(OUT / "05_value_of_forecast.png")
    plt.close(fig)


# ------------------------------------------------------------------
# 6. 데이터셋 역할 지도
# ------------------------------------------------------------------
def fig_dataset_map():
    rows = ["ENERTALK (한국 22가구)", "REFIT (영국 20가구)", "Low Carbon London (5,567가구)",
            "CityLearn v2 / NREL EULP", "KPX SMP · 시간별 전력수요", "기상청 ASOS (기온·일사)",
            "KPX 국민DR 규칙 · 발령내역"]
    cols = ["가전 단위", "한국\n생활패턴", "1년 이상", "100가구 이상", "냉난방·PV·\nESS", "가격·DR\n신호", "기상"]
    # 2 = 핵심 제공, 1 = 부분 제공, 0 = 없음
    m = np.array([
        [2, 2, 0, 0, 0, 0, 0],
        [2, 0, 2, 0, 0, 0, 0],
        [0, 0, 2, 2, 0, 1, 0],
        [1, 0, 2, 2, 2, 1, 2],
        [0, 2, 2, 0, 0, 2, 0],
        [0, 2, 2, 0, 1, 0, 2],
        [0, 2, 1, 0, 0, 2, 0],
    ])
    fig, ax = plt.subplots(figsize=(10.5, 4.9))
    ax.grid(False)
    for s in ax.spines.values():
        s.set_visible(False)
    cmap = {0: SURFACE, 1: BLUE_LIGHT, 2: BLUE}
    sym = {0: "", 1: "◐", 2: "●"}
    for i in range(m.shape[0]):
        for j in range(m.shape[1]):
            v = m[i, j]
            ax.add_patch(Rectangle((j + 0.04, i + 0.06), 0.92, 0.88, color=cmap[v], lw=0))
            if v == 0:
                ax.add_patch(Rectangle((j + 0.04, i + 0.06), 0.92, 0.88, fill=False, ec=GRID, lw=0.8))
            ax.text(j + 0.5, i + 0.5, sym[v], ha="center", va="center", fontsize=12,
                    color=SURFACE if v == 2 else INK2)
    ax.set_xlim(0, m.shape[1])
    ax.set_ylim(m.shape[0], 0)
    ax.set_xticks(np.arange(m.shape[1]) + 0.5)
    ax.set_xticklabels(cols, fontsize=10)
    ax.xaxis.tick_top()
    ax.set_yticks(np.arange(m.shape[0]) + 0.5)
    ax.set_yticklabels(rows, fontsize=10)
    ax.tick_params(length=0)
    ax.set_title("어떤 데이터가 어떤 빈칸을 채우는가", loc="left", pad=46)
    fig.text(0.99, 0.01, "● 핵심 제공   ◐ 부분 제공   (빈칸) 없음", ha="right", fontsize=9, color=INK2)
    fig.savefig(OUT / "06_dataset_map.png")
    plt.close(fig)


# ------------------------------------------------------------------
# 7. 로드맵 (주 단위)
# ------------------------------------------------------------------
def fig_roadmap():
    phases = [
        ("P0 기획 확정", 1, 2, "연구·실험"),
        ("P1 데이터 파이프라인·디지털 트윈", 3, 7, "연구·실험"),
        ("P2 예측 모델 (E1)", 6, 10, "연구·실험"),
        ("P3 최적화 제어기·시뮬레이션 실험 (E2·E3)", 9, 15, "연구·실험"),
        ("P4 Edge Hub 소프트웨어·HIL (E4)", 14, 19, "엣지"),
        ("P5 Spring 플랫폼·웹 UI", 16, 24, "플랫폼"),
        ("P6 커뮤니티 Aggregator (E5)", 21, 25, "플랫폼"),
        ("P7 실물 테스트베드·통합 평가 (E6)", 24, 29, "통합"),
        ("P8 결과 정리·문서화·발표", 29, 31, "통합"),
    ]
    color = {"연구·실험": BLUE, "엣지": ORANGE, "플랫폼": AQUA, "통합": VIOLET}
    fig, ax = plt.subplots(figsize=(11, 4.8))
    ax.set_axisbelow(True)
    for i, (name, s, e, cat) in enumerate(phases):
        ax.add_patch(FancyBboxPatch((s - 1 + 0.08, i - 0.32), e - s + 1 - 0.16, 0.64,
                                    boxstyle="round,pad=0,rounding_size=0.18", color=color[cat], lw=0))
    ax.set_yticks(range(len(phases)))
    ax.set_yticklabels([p[0] for p in phases], fontsize=10)
    ax.set_ylim(len(phases) - 0.4, -0.6)
    ax.set_xlim(0, 31)
    ax.set_xticks(range(0, 32, 2))
    ax.set_xticklabels([f"{w}" for w in range(0, 32, 2)])
    ax.set_xlabel("주차 (week)")
    ax.grid(axis="y", visible=False)
    ax.tick_params(axis="y", length=0)
    for ms, label in [(10, "M1 예측 모델 확정"), (15, "M2 시뮬레이션 결론"), (24, "M3 전체 시스템 연결"),
                      (29, "M4 최종 평가")]:
        ax.axvline(ms, color=AXIS, lw=1, zorder=0)
        ax.text(ms, -0.75, label, ha="center", fontsize=8.5, color=INK2)
    handles = [Rectangle((0, 0), 1, 1, color=c) for c in color.values()]
    ax.legend(handles, color.keys(), loc="lower left", ncol=4, bbox_to_anchor=(0, -0.32))
    ax.set_title("로드맵 (약 31주, 1인 기준 예시)", loc="left", pad=22)
    fig.savefig(OUT / "07_roadmap.png")
    plt.close(fig)


if __name__ == "__main__":
    fig_concept_loop()
    fig_load_shift()
    fig_tariffs()
    fig_rebound()
    fig_value_of_forecast()
    fig_dataset_map()
    fig_roadmap()
    print("saved to", OUT)
