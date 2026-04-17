import streamlit as st
import pandas as pd

st.set_page_config(page_title="FSM Tool", layout="wide")

st.markdown("""
<div style="background:linear-gradient(90deg,#2c3e50,#4ca1af,#5dade2);
padding:20px;border-radius:15px;color:white;text-align:center;">
<h2>FSM Minimization Tool</h2>
<p>Implication Table Method</p>
</div>
""", unsafe_allow_html=True)

mode = st.selectbox("Mode", ["Moore", "Mealy"])
n = int(st.number_input("States", 2, 8, 4))

states = [chr(65+i) for i in range(n)]

if "df" not in st.session_state:
    st.session_state.df = None

if st.session_state.df is None or len(st.session_state.df) != n:

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

df = st.data_editor(st.session_state.df, use_container_width=True)
st.session_state.temp_df = df
def clean(x):
    return str(x).strip().upper()

def idx(x):
    return ord(x) - 65

def valid(x):
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
        r = find(parent, i)
        groups.setdefault(r, []).append(states[i])

    return list(groups.values())
    def show(trans, out):

    if mode == "Moore":
        df2 = pd.DataFrame({
            "State": states,
            "X=0": [t[0] for t in trans],
            "X=1": [t[1] for t in trans],
            "Output": out
        })
    else:
        df2 = pd.DataFrame({
            "State": states,
            "Next X=0": [t[0] for t in trans],
            "Next X=1": [t[1] for t in trans],
            "Out X=0": [o[0] for o in out],
            "Out X=1": [o[1] for o in out]
        })

    st.dataframe(df2)


if st.button("Run"):

    df = st.session_state.temp_df

    trans = []
    out = []
    invalid = False

    for i in range(n):

        t = [clean(df.iloc[i]["X=0"]), clean(df.iloc[i]["X=1"])]

        for x in t:
            if not valid(x):
                invalid = True

        if mode == "Moore":
            o = clean(df.iloc[i]["Output"])
            if o == "":
                invalid = True
            out.append(o)
        else:
            o = [clean(df.iloc[i]["O/P X=0"]), clean(df.iloc[i]["O/P X=1"])]
            if "" in o:
                invalid = True
            out.append(o)

        trans.append(t)

    if invalid:
        st.error("Fill all fields")
    else:
        mark = minimize(states, trans, out, mode)
        groups = build_groups(states, mark)

        st.success("Done")

        for g in groups:
            st.write(g)


