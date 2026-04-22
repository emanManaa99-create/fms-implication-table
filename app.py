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

<div style="
margin-top:15px;
display:inline-block;
padding:10px 20px;
border-radius:12px;
background: rgba(255,255,255,0.15);
">
<b>Eman Fawzi Manaa</b><br>
ID: 10513
</div>

</div>
""", unsafe_allow_html=True)

mode = st.selectbox("Mode", ["Moore", "Mealy"])
n = int(st.number_input("Number of States", 2, 8, 4))
num_inputs = int(st.number_input("Number of Inputs", 1, 3, 1))

states = [chr(65+i) for i in range(n)]

def generate_inputs(k):
    return [format(i, f"0{k}b") for i in range(2**k)]

inputs = generate_inputs(num_inputs)

if "last_mode" not in st.session_state:
    st.session_state.last_mode = mode
if "last_n" not in st.session_state:
    st.session_state.last_n = n
if "last_inp" not in st.session_state:
    st.session_state.last_inp = num_inputs

if ("df" not in st.session_state
    or st.session_state.last_mode != mode
    or st.session_state.last_n != n
    or st.session_state.last_inp != num_inputs):

    st.session_state.last_mode = mode
    st.session_state.last_n = n
    st.session_state.last_inp = num_inputs

    data = {"State": states}

    for inp in inputs:
        data[f"Next (X = {inp})"] = [""] * n

    if mode == "Moore":
        data["Output"] = [""] * n
    else:
        for inp in inputs:
            data[f"Output (X = {inp})"] = [""] * n

    st.session_state.df = pd.DataFrame(data)

df = st.data_editor(st.session_state.df, use_container_width=True, num_rows="fixed")


def clean(x):
    return str(x).strip().upper()

def valid_state(x):
    return x in states


def reachable_states(all_states_names, trans):

    visited = set()
    stack = [0]

    while stack:
        s = stack.pop()

        if s in visited:
            continue

        visited.add(s)

        for nxt in trans[s]:
            stack.append(all_states_names.index(nxt))

    return sorted(list(visited))


def minimize(states, trans, out, mode):

    n = len(states)
    mark = [[0]*n for _ in range(n)]

    for i in range(n):
        for j in range(i):

            if mode == "Moore":
                if out[i] != out[j]:
                    mark[i][j] = 1
            else:
                for k in range(len(out[i])):
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

                for k in range(len(trans[i])):

                    ni = states.index(trans[i][k])
                    nj = states.index(trans[j][k])

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


if st.button("Run Minimization"):

    trans = []
    out = []
    invalid = False

    for i in range(n):

        t = [clean(df.iloc[i][f"Next (X = {inp})"]) for inp in inputs]

        for x in t:
            if not valid_state(x):
                invalid = True

        if mode == "Moore":
            o = clean(df.iloc[i]["Output"])
            if o == "":
                invalid = True
            out.append(o)
        else:
            o = [clean(df.iloc[i][f"Output (X = {inp})"]) for inp in inputs]

            if "" in o or len(o) != len(t):
                invalid = True

            out.append(o)

        trans.append(t)

    if invalid:
        st.error("Fill all fields correctly")

    else:
        reachable = reachable_states(states, trans)

        states = [states[i] for i in reachable]
        trans = [trans[i] for i in reachable]
        out = [out[i] for i in reachable]

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





