import streamlit as st
import pandas as pd

st.set_page_config(page_title="FSM Tool", layout="wide")

st.markdown("""
<div style="
background: linear-gradient(90deg,#1e3c72,#2a5298,#4facfe);
padding:25px;
border-radius:15px;
color:white;
text-align:center;
box-shadow:0px 4px 15px rgba(0,0,0,0.3);
">
<h2>FSM Minimization Tool</h2>
<p>Implication Table Method</p>
</div>
""", unsafe_allow_html=True)

mode = st.selectbox("Mode", ["Moore", "Mealy"])
n = int(st.number_input("Number of States", 2, 8, 4))

states = [chr(65+i) for i in range(n)]


if "last_mode" not in st.session_state:
    st.session_state.last_mode = mode

if "last_n" not in st.session_state:
    st.session_state.last_n = n

if ("df" not in st.session_state
    or st.session_state.last_mode != mode
    or st.session_state.last_n != n):

    st.session_state.last_mode = mode
    st.session_state.last_n = n

    if mode == "Moore":
        st.session_state.df = pd.DataFrame({
            "State": states,
            "Next (X = 0)": [""]*n,
            "Next (X = 1)": [""]*n,
            "Output": [""]*n
        })
    else:
        st.session_state.df = pd.DataFrame({
            "State": states,
            "Next (X = 0)": [""]*n,
            "Next (X = 1)": [""]*n,
            "Output (X = 0)": [""]*n,
            "Output (X = 1)": [""]*n
        })

df = st.data_editor(st.session_state.df, use_container_width=True, num_rows="fixed")



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
                if out[i][0] != out[j][0] or out[i][1] != out[j][1]:
                    mark[i][j] = 1

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


if st.button("Run Minimization"):

    trans = []
    out = []
    invalid = False

    for i in range(n):

        t = [
            clean(df.iloc[i]["Next (X = 0)"]),
            clean(df.iloc[i]["Next (X = 1)"])
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
                clean(df.iloc[i]["Output (X = 0)"]),
                clean(df.iloc[i]["Output (X = 1)"])
            ]
            if "" in o:
                invalid = True
            out.append(o)

        trans.append(t)

    if invalid:
        st.error("Fill all fields correctly")

    else:
        mark = minimize(states, trans, out, mode)
        groups = build_groups(states, mark)

        st.success("Equivalent Groups")

        for g in groups:
            st.markdown(
                f"""
                <div style="
                background:#fff;
                border-left:5px solid #4facfe;
                padding:10px;
                margin:10px;
                border-radius:10px;">
                <b>{', '.join(g)}</b>
                </div>
                """,
                unsafe_allow_html=True
            )




