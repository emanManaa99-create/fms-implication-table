import streamlit as st
import pandas as pd

st.set_page_config(page_title="FSM Minimization Tool", layout="wide")

st.markdown("""
<div style="
background: linear-gradient(90deg,#0f2027,#203a43,#2c5364);
padding:25px;
border-radius:15px;
color:white;
text-align:center;
box-shadow:0px 4px 20px rgba(0,0,0,0.4);">
<h2>FSM Minimization Tool</h2>
<p>Implication Table Method (Moore / Mealy)</p>
</div>
""", unsafe_allow_html=True)

mode = st.selectbox("Mode", ["Moore", "Mealy"])
n = st.number_input("Number of States", 2, 8, 4)

states = [chr(65+i) for i in range(int(n))]
inputs = ["X=0", "X=1"]

if "df" not in st.session_state or len(st.session_state.df) != n:

    st.session_state.df = pd.DataFrame({
        "State": states,
        "X=0": [""]*n,
        "X=1": [""]*n,
        "Output X=0": [""]*n,
        "Output X=1": [""]*n,
    })

st.markdown("## Input Table")

df = st.data_editor(
    st.session_state.df,
    use_container_width=True,
    key="editor",
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

                    x = max(ni, nj)
                    y = min(ni, nj)

                    if mark[x][y]:
                        mark[i][j] = 1
                        changed = True
                        break

    return mark


def build_groups(states, mark):

    visited = [0]*len(states)
    groups = []

    for i in range(len(states)):
        if not visited[i]:
            g = [states[i]]
            visited[i] = 1

            for j in range(i+1, len(states)):
                if mark[max(i,j)][min(i,j)] == 0:
                    g.append(states[j])
                    visited[j] = 1

            groups.append(g)

    return groups


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

        if mode == "Moore":

            o = clean(df.iloc[i]["Output X=0"])

            if o == "":
                invalid = True

            out.append(o)
        else:

            o = [
                clean(df.iloc[i]["Output X=0"]),
                clean(df.iloc[i]["Output X=1"])
            ]

            if "" in o:
                invalid = True

            out.append(o)

        for x in t:
            if not valid_state(x):
                invalid = True

        trans.append(t)

    if invalid:
        st.error("Please fill all fields correctly")
    else:

        mark = minimize(states, trans, out, mode)

        draw_table(states, mark)

        groups = build_groups(states, mark)

        st.success("Equivalent State Groups")

        for g in groups:
            st.markdown(
                f"""
                <div style="
                    background: linear-gradient(90deg,#0f2027,#2c5364);
                    color:white;
                    padding:12px;
                    margin:10px;
                    border-radius:10px;
                    border-left:5px solid #4facfe;">
                    <b>{', '.join(g)}</b>
                </div>
                """,
                unsafe_allow_html=True
            )





