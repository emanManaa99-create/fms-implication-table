import streamlit as st
import pandas as pd

st.set_page_config(page_title="FSM Tool", layout="wide")

st.markdown("""
<div style="background:linear-gradient(90deg,#0f2027,#203a43,#2c5364);
padding:25px;border-radius:15px;color:white;text-align:center">
<h2>FSM Minimization Tool</h2>
<p>Implication Table Method</p>
</div>
""", unsafe_allow_html=True)

mode = st.selectbox("Mode", ["Moore", "Mealy"])
n = st.number_input("Number of States", 2, 8, 4)

states = [chr(65+i) for i in range(int(n))]

if "ns_df" not in st.session_state or len(st.session_state.ns_df) != n:
    st.session_state.ns_df = pd.DataFrame({
        "State": states,
        "X=0": [""]*n,
        "X=1": [""]*n
    })

if "op_df" not in st.session_state or len(st.session_state.op_df) != n:
    st.session_state.op_df = pd.DataFrame({
        "State": states,
        "X=0": [""]*n,
        "X=1": [""]*n
    })

if "moore_df" not in st.session_state or len(st.session_state.moore_df) != n:
    st.session_state.moore_df = pd.DataFrame({
        "State": states,
        "Output": [""]*n
    })

st.markdown("## Input Tables")

if mode == "Mealy":

    st.markdown("### Next State")
    ns_df = st.data_editor(st.session_state.ns_df, use_container_width=True, key="ns")

    st.markdown("### Output")
    op_df = st.data_editor(st.session_state.op_df, use_container_width=True, key="op")

    st.session_state.temp_ns = ns_df
    st.session_state.temp_op = op_df

else:

    st.markdown("### Moore Table")
    moore_df = st.data_editor(st.session_state.moore_df, use_container_width=True, key="mo")

    st.session_state.temp_moore = moore_df
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

    invalid = False
    trans = []
    out = []

    if mode == "Mealy":

        ns_df = st.session_state.temp_ns
        op_df = st.session_state.temp_op

        for i in range(n):

            t0 = clean(ns_df.iloc[i]["X=0"])
            t1 = clean(ns_df.iloc[i]["X=1"])

            o0 = clean(op_df.iloc[i]["X=0"])
            o1 = clean(op_df.iloc[i]["X=1"])

            if not valid_state(t0) or not valid_state(t1):
                invalid = True

            if o0 == "" or o1 == "":
                invalid = True

            trans.append([t0, t1])
            out.append([o0, o1])

    else:

        moore_df = st.session_state.temp_moore

        for i in range(n):

            o = clean(moore_df.iloc[i]["Output"])

            if o == "":
                invalid = True

            trans.append([states[i], states[i]])
            out.append(o)

    if invalid:
        st.error("Please fill all fields correctly")
    else:

        mark = minimize(states, trans, out, mode)

        draw_table(states, mark)

        groups = build_groups(states, mark)

        st.success("Equivalent Groups")

        for g in groups:
            st.markdown(
                f"""
                <div style="background:white;
                border-left:5px solid #203a43;
                padding:12px;margin:10px;border-radius:10px;">
                <b>{', '.join(g)}</b>
                </div>
                """,
                unsafe_allow_html=True
            )


