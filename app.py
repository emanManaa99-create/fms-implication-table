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

n = int(st.number_input("Number of States", 2, 8, 4))

states = [chr(65+i) for i in range(n)]

def make_binary(n):

    bits = max(2, (n-1).bit_length())

    return [format(i, f"0{bits}b") for i in range(n)]

binary = make_binary(n)

st.markdown("## State Mapping (Binary)")

st.dataframe(pd.DataFrame({"State": states, "Binary": binary}), use_container_width=True)

if "df" not in st.session_state or len(st.session_state.df) != n:

    if mode == "Moore":

        st.session_state.df = pd.DataFrame({

            "State": states,

            "X0": [""]*n,

            "X1": [""]*n,

            "Output": [""]*n

        })

    else:

        st.session_state.df = pd.DataFrame({

            "State": states,

            "X0": [""]*n,

            "X1": [""]*n,

            "O0": [""]*n,

            "O1": [""]*n

        })

df = st.data_editor(st.session_state.df, use_container_width=True)

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

            "X0": [t[0] for t in trans],

            "X1": [t[1] for t in trans],

            "Output": out

        })

    else:

        df2 = pd.DataFrame({

            "State": states,

            "X0": [t[0] for t in trans],

            "X1": [t[1] for t in trans],

            "O0": [o[0] for o in out],

            "O1": [o[1] for o in out]

        })

    st.dataframe(df2, use_container_width=True)

if st.button("Run Minimization"):

    trans = []

    out = []

    invalid = False

    for i in range(n):

        t = [clean(df.iloc[i]["X0"]), clean(df.iloc[i]["X1"])]

        for x in t:

            if not valid(x):

                invalid = True

        if mode == "Moore":

            o = clean(df.iloc[i]["Output"])

            if o == "":

                invalid = True

            out.append(o)

        else:

            o = [clean(df.iloc[i]["O0"]), clean(df.iloc[i]["O1"])]

            if "" in o:

                invalid = True

            out.append(o)

        trans.append(t)

    if invalid:

        st.error("Fill all fields correctly")

    else:

        mark = minimize(states, trans, out, mode)

        groups = build_groups(states, mark)

        st.success("Done")

        show(trans, out)

        for g in groups:

            st.write(g)

                invalid = True

        })

    st.dataframe(df2, use_container_width=True)

            if mark[i][j] == 0:
                    

        st
