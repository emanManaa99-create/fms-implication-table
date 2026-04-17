import streamlit as st
import pandas as pd

st.set_page_config(page_title="FSM Minimization Tool", layout="wide")

st.markdown("""
<div style="
background: linear-gradient(90deg,#2c3e50,#4ca1af,#5dade2);
padding:25px;
border-radius:15px;
color:white;
text-align:center;
box-shadow:0px 4px 18px rgba(0,0,0,0.3);">
<h2>FSM Minimization Tool</h2>
<p>Implication Table Method (Moore / Mealy)</p>
</div>
""", unsafe_allow_html=True)

mode = st.selectbox("Mode", ["Moore", "Mealy"])
n = st.number_input("Number of States", 2, 8, 4)

states = [chr(65+i) for i in range(int(n))]

state_bits = {
    "A": "00", "B": "01", "C": "10", "D": "11",
    "E": "100", "F": "101"
}

if "df" not in st.session_state or len(st.session_state.df) != n:

    if mode == "Moore":
        st.session_state.df = pd.DataFrame({
            "State": states,
            "X=0": [""]*n,
            "X=1": [""]*n,
            "Output": [""]*n
        })

    else:
        st.session_state.df = pd.DataFrame({
            "State": states,
            "X=0": [""]*n,
            "X=1": [""]*n,
            "O/P X=0": [""]*n,
            "O/P X=1": [""]*n
        })

st.markdown("## Input Table")

df = st.data_editor(
    st.session_state.df,
    use_container_width=True,
    num_rows="fixed"
)

st.session_state.temp_df = df
def clean(x):
    return str(x).strip().upper()

def idx(x):
    return ord(x) - 65

def valid_state(x):
    return x in states


def minimize(states, trans, out, mode):

    n = len(states)
    mark = [[0]*n for _ in range(n)]

    for i in range(n):
        for j in range(i):

            if mode == "Moore":
                if out[i] != out[j]:
                    mark[i][j] = 1

            else:
                for k in range(2):
                    if out[i][k] != out[j][k]:
                        mark[i][j] = 1
                        break

    changed = True

    while changed:
        changed = False

        for i in range(n):
            for j in range(i):

                if mark[i][j]:
                    continue

                for k in range(2):

                    ni = idx(trans[i][k])
                    nj = idx(trans[j][k])

                    if ni == nj:
                        continue

                    x = max(ni, nj)
                    y = min(ni, nj)

                    if mark[x][y]:
                        mark[i][j] = 1
                        changed = True
                        break

    return mark
    def find(parent, x):
    if parent[x] != x:
        parent[x] = find(parent, parent[x])
    return parent[x]


def union(parent, a, b):
    ra = find(parent, a)
    rb = find(parent, b)
    if ra != rb:
        parent[rb] = ra


def build_groups(states, mark):

    n = len(states)
    parent = list(range(n))

    for i in range(n):
        for j in range(i):
            if mark[i][j] == 0:
                union(parent, i, j)

    groups = {}

    for i in range(n):
        root = find(parent, i)
        groups.setdefault(root, []).append(states[i])

    return list(groups.values())


def show_moore(trans, out):

    st.markdown("## Moore Table")

    df = pd.DataFrame({
        "State": [f"{s} ({state_bits.get(s,'')})" for s in states],
        "X=0 Next State": [trans[i][0] for i in range(len(states))],
        "X=1 Next State": [trans[i][1] for i in range(len(states))],
        "Output": out
    })

    st.dataframe(df, use_container_width=True)


def show_mealy(trans, out):

    st.markdown("## Mealy Table")

    df = pd.DataFrame({
        "State": [f"{s} ({state_bits.get(s,'')})" for s in states],

        "Next State (X=0)": [trans[i][0] for i in range(len(states))],
        "Next State (X=1)": [trans[i][1] for i in range(len(states))],

        "Output (X=0)": [out[i][0] for i in range(len(states))],
        "Output (X=1)": [out[i][1] for i in range(len(states))]
    })

    st.dataframe(df, use_container_width=True)


if st.button("Run Minimization ▶"):

    df = st.session_state.temp_df.copy()

    trans = []
    out = []

    invalid = False

    for i in range(n):

        t = [
            clean(df.iloc[i]["X=0"]),
            clean(df.iloc[i]["X=1"])
        ]

        for x in t:
            if not valid_state(x):
                invalid = True

        if mode == "Moore":

            o = clean(df.iloc[i]["Output"])
            if o == "":
                invalid = True
            out.append(o)

        else:

            o = [
                clean(df.iloc[i]["O/P X=0"]),
                clean(df.iloc[i]["O/P X=1"])
            ]

            if "" in o:
                invalid = True
            out.append(o)

        trans.append(t)

    if invalid:
        st.error("Please fill all fields correctly")

    else:

        mark = minimize(states, trans, out, mode)

        groups = build_groups(states, mark)

        if mode == "Moore":
            show_moore(trans, out)
        else:
            show_mealy(trans, out)

        st.success("Equivalent Groups Found")

        for g in groups:
            st.markdown(
                f"""
                <div style="
                    background: linear-gradient(90deg,#2c3e50,#4ca1af);
                    color:white;
                    padding:12px;
                    margin:10px;
                    border-radius:10px;
                    border-left:5px solid #5dade2;">
                    <b>{', '.join(g)}</b>
                </div>
                """,
                unsafe_allow_html=True
            )


