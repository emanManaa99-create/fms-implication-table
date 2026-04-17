import streamlit as st

st.set_page_config(page_title="FSM Minimization Tool", layout="wide")

st.markdown(
    """
    <div style="
        background: linear-gradient(90deg,#0f0f0f,#2b2b2b);
        padding: 25px;
        border-radius: 12px;
        text-align: center;
        color: white;
        margin-bottom: 25px;">
        <h2>Finite State Machine Minimization</h2>
        <p style="color:#bbbbbb;">Implication Table Method - Moore & Mealy</p>
    </div>
    """,
    unsafe_allow_html=True
)

mode = st.selectbox("Select Mode", ["Moore", "Mealy"])
n = st.number_input("Number of States", 2, 10, 4)

states = [chr(65+i) for i in range(int(n))]
inputs = ["00", "01", "10", "11"]

st.markdown("### FSM Transition & Output Table")

trans = {}
out = {}

for s in states:
    with st.expander(f"State {s}", expanded=True):

        cols = st.columns(4)
        trans[s] = []

        for i, inp in enumerate(inputs):
            trans[s].append(
                cols[i].text_input(inp, key=f"{s}{inp}")
            )

        out[s] = st.text_input("Output", key=f"o{s}")


def idx(s):
    return ord(s) - 65


def minimize(states, trans, out):

    n = len(states)
    mark = [[0]*n for _ in range(n)]

    for i in range(n):
        for j in range(i):
            if out[states[i]] != out[states[j]]:
                mark[i][j] = 1

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

                    try:
                        a = idx(trans[si][k])
                        b = idx(trans[sj][k])
                    except:
                        return None

                    x = max(a, b)
                    y = min(a, b)

                    if mark[x][y] == 1:
                        mark[i][j] = 1
                        change = True
                        break

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
    if st.button("Run Minimization ▶")
    if all(all(trans[s]) for s in states) and all(out[s] for s in states):

        result = minimize(states, trans, out)

        if result is None:
            st.error("Please check input format")
        else:
            st.success("Equivalent States Found")

            st.markdown("### Result Groups")

            for g in result:
                st.markdown(
                    f"""
                    <div style="
                        background:#111;
                        padding:12px;
                        margin:8px 0;
                        border-radius:10px;
                        color:#00ffcc;
                        font-size:16px;
                        font-weight:bold;
                        text-align:center;">
                        {' , '.join(g)}
                    </div>
                    """,
                    unsafe_allow_html=True
                )

    else:
        st.warning("Please fill all fields")
