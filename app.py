import streamlit as st

st.set_page_config(page_title="FSM Minimization Tool", layout="wide")

st.markdown(

    """

    <div style="

        background: linear-gradient(90deg,#4facfe,#00f2fe);

        padding: 30px;

        border-radius: 18px;

        text-align: center;

        color: white;

        margin-bottom: 25px;

        box-shadow: 0 6px 18px rgba(0,0,0,0.15);">

        <h2>Finite State Machine Minimization</h2>

        <p style="margin-top:8px;color:#eafcff;">

            Implication Table Method - Moore & Mealy

        </p>

    </div>

    """,

    unsafe_allow_html=True

)

mode = st.selectbox("Select Mode", ["Moore", "Mealy"])

n = st.number_input("Number of States", 2, 10, 4)

states = [chr(65+i) for i in range(int(n))]

inputs = ["00", "01", "10", "11"]

trans = {}

out = {}

st.markdown("## Transition Table")

for s in states:

    st.markdown(f"### State {s}")

    cols = st.columns(4)

    trans[s] = []

    out[s] = []

    for i, inp in enumerate(inputs):

        trans[s].append(cols[i].text_input(f"Next {inp}", key=f"n{s}{inp}"))

    if mode == "Moore":

        out[s] = st.text_input("Output", key=f"o{s}")

    else:

        st.caption("Mealy: Output per input")

        c2 = st.columns(4)

        for i, inp in enumerate(inputs):

            out[s].append(c2[i].text_input(f"Out {inp}", key=f"m{s}{inp}"))

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

                if out[states[i]] != out[states[j]]:

                    mark[i][j] = 1

            else:

                for k in range(4):

                    if out[states[i]][k] != out[states[j]][k]:

                        mark[i][j] = 1

                        break

    change = True

    while change:

        change = False

        for i in range(n):

            for j in range(i):

                if mark[i][j] == 1:

                    continue

                si = states[i]

                sj = states[j]

                for k in range(4):

                    ni = idx(trans[si][k])

                    nj = idx(trans[sj][k])

                    x = max(ni, nj)

                    y = min(ni, nj)

                    if mark[x][y] == 1:

                        mark[i][j] = 1

                        change = True

                        break

    return mark

def draw_table(states, mark):

    st.markdown("## Implication Table")

    n = len(states)

    for i in range(n):

        row = ""

        for j in range(n):

            if j >= i:

                row += "⬜ "

            else:

                row += "❌ " if mark[i][j] == 1 else "⭕ "

        st.write(f"{states[i]} : {row}")

def build_groups(states, mark):

    n = len(states)

    visited = [0] * n

    groups = []

    for i in range(n):

        if not visited[i]:

            g = [states[i]]

            visited[i] = 1

            for j in range(i + 1, n):
                if mark[max(i, j)][min(i, j)] == 0:

                    g.append(states[j])

                    visited[j] = 1

            groups.append(g)

    return groups

if st.button("Run Minimization ▶"):

    invalid = False

    for s in states:

        for i in range(4):

            if not valid_state(trans[s][i]):

                invalid = True

        if mode == "Moore":

            if not out[s]:

                invalid = True

        else:

            for i in range(4):

                if not out[s][i]:

                    invalid = True

    if invalid:

        st.error("Invalid input: ensure states are A, B, C... and all fields are filled")

    else:

        mark = minimize(states, trans, out, mode)

        draw_table(states, mark)

        groups = build_groups(states, mark)

        st.success("Equivalent State Groups Found")
        for g in groups:

            st.markdown(

                f"""

                <div style="

                    background: #ffffff;

                    border-left: 6px solid #4facfe;

                    padding: 16px;

                    margin: 12px 0;

                    border-radius: 14px;

                    box-shadow: 0 3px 10px rgba(0,0,0,0.08);">

                    

                    <div style="font-size:13px;color:#666;">

                        Equivalent State Group

                    </div>

                    <div style="font-size:18px;font-weight:600;color:#1f3b57;">

                        {', '.join(g)}

                    </div>

                </div>

                """,

                unsafe_allow_html=True

            )
            

    mark = [[0]*n for _ in range(n)]
