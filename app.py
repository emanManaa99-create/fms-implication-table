import streamlit as st
import pandas as pd

st.set_page_config(page_title="FSM Minimization Tool", layout="wide")

st.markdown(
    """
    <div style="
        background: linear-gradient(90deg,#4facfe,#00f2fe);
        padding: 30px;
        border-radius: 18px;
        text-align: center;
        color: white;
        margin-bottom: 25px;">
        <h2>Finite State Machine Minimization</h2>
        <p>Implication Table Method - Moore & Mealy</p>
    </div>
    """,
    unsafe_allow_html=True
)

mode = st.selectbox("Select Mode", ["Moore", "Mealy"])
n = st.number_input("Number of States", 2, 10, 4)

states = [chr(65+i) for i in range(int(n))]
inputs = ["00", "01", "10", "11"]

st.markdown("## Transition Table (Excel Style)")

if "df" not in st.session_state:
    st.session_state.df = None

if st.session_state.df is None or len(st.session_state.df) != n:
    st.session_state.df = pd.DataFrame({
        "State": states,
        "00": [""]*n,
        "01": [""]*n,
        "10": [""]*n,
        "11": [""]*n,
        "Output": [""]*n
    })
edited = st.data_editor(st.session_state.df, use_container_width=True)
st.session_state.df = edited
def clean(x):
    return str(x).strip().upper() if x is not None else ""


def valid_state(x):
    return x in states


def idx(x):
    return ord(x) - 65


def minimize(states, trans, out, mode):

    n = len(states)
    mark = [[0]*n for _ in range(n)]

    for i in range(n):
        for j in range(i):

            if mode == "Moore":
                if out[i] != out[j]:
                    mark[i][j] = 1
            else:
                for k in range(4):
                    if out[i][k] != out[j][k]:
                        mark[i][j] = 1
                        break

    change = True

    while change:
        change = False

        for i in range(n):
            for j in range(i):

                if mark[i][j] == 1:
                    continue

                for k in range(4):

                    ni = idx(trans[i][k])
                    nj = idx(trans[j][k])

                    x = max(ni, nj)
                    y = min(ni, nj)

                    if mark[x][y] == 1:
                        mark[i][j] = 1
                        change = True
                        break

    return mark


def draw_table(states, mark):

    st.markdown("## Implication Table")

    for i in range(len(states)):
        row = ""

        for j in range(len(states)):

            if j >= i:
                row += "⬜ "
            else:
                row += "❌ " if mark[i][j] else "⭕ "

        st.write(states[i], row)


def build_groups(states, mark):

    n = len(states)
    visited = [0]*n
    groups = []

    for i in range(n):
        if not visited[i]:
            g = [states[i]]
            visited[i] = 1

            for j in range(i+1, n):
                if mark[max(i,j)][min(i,j)] == 0:
                    g.append(states[j])
                    visited[j] = 1

            groups.append(g)

    return groups


if st.button("Run Minimization ▶"):

    df = st.session_state.df.copy()

    trans = []
    out = []

    invalid = False

    for i in range(len(states)):

        t = [
            clean(df.iloc[i]["00"]),
            clean(df.iloc[i]["01"]),
            clean(df.iloc[i]["10"]),
            clean(df.iloc[i]["11"]),
        ]

        o = clean(df.iloc[i]["Output"])

        for x in t:
            if x and not valid_state(x):
                invalid = True

        if mode == "Moore" and not o:
            invalid = True

        if mode == "Mealy" and any(x == "" for x in t):
            invalid = True

        trans.append(t)
        out.append(o if mode == "Moore" else t)

    if invalid:
        st.error("Invalid input: check states and fill all fields")
    else:

        mark = minimize(states, trans, out, mode)

        draw_table(states, mark)

        groups = build_groups(states, mark)

        st.success("Equivalent State Groups Found")

        for g in groups:
            st.markdown(
                f"""
                <div style="
                    background:white;
                    border-left:5px solid #4facfe;
                    padding:12px;
                    margin:10px 0;
                    border-radius:10px;">
                    <b>{', '.join(g)}</b>
                </div>
                """,
                unsafe_allow_html=True
            )
st.session_state.df = edited
