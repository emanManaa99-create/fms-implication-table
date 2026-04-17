import streamlit as st

st.set_page_config(page_title="FSM Tool", layout="wide")

st.markdown(
    """
    <div style="
        background: linear-gradient(90deg,#4b6cb7,#182848);
        padding: 28px;
        border-radius: 16px;
        text-align: center;
        color: white;
        margin-bottom: 25px;">
        <h2>Finite State Machine Minimization</h2>
        <p style="color:#d0d0d0;">Implication Table Method - Moore & Mealy</p>
    </div>
    """,
    unsafe_allow_html=True
)

mode = st.selectbox("Mode", ["Moore", "Mealy"])
n = st.number_input("Number of States", 2, 10, 4)

states = [chr(65+i) for i in range(int(n))]
inputs = ["00", "01", "10", "11"]

trans = {}
out = {}

st.markdown("### Transition Table")

for s in states:
    with st.expander(f"State {s}", expanded=True):

        cols = st.columns(4)
        trans[s] = []
        out[s] = []

        for i, inp in enumerate(inputs):
            trans[s].append(cols[i].text_input(f"Next({inp})", key=f"n{s}{inp}"))

        if mode == "Moore":
            out[s] = st.text_input("Output", key=f"o{s}")
        else:
            st.markdown("**Outputs (Mealy)**")
            out[s] = []
            c2 = st.columns(4)

            for i, inp in enumerate(inputs):
                out[s].append(c2[i].text_input(f"Out({inp})", key=f"m{s}{inp}"))


def idx(s):
    return ord(s) - 65


def minimize(states, trans, out, mode):

    n = len(states)
    mark = [[0]*n for _ in range(n)]

    for i in range(n):
        for j in range(i):
            if mode == "Moore":
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
                        ni = idx(trans[si][k])
                        nj = idx(trans[sj][k])
                    except:
                        return None

                    x = max(ni, nj)
                    y = min(ni, nj)

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


if st.button("Run Minimization ▶"):

    valid = True

    if mode == "Moore":
        valid = all(all(trans[s]) for s in states) and all(out[s] for s in states)
    else:
        for s in states:
            if not all(trans[s]):
                valid = False
            if not all(out[s]):
                valid = False

    result = minimize(states, trans, out, mode) if valid else None

    if result is None:
        st.error("Check input format")
    else:
        st.success("Equivalent States Found")

        st.markdown("### Result Groups")

        for g in result:
            st.markdown(
                f"""
                <div style="
                    background: linear-gradient(135deg,#ffffff,#f3f6ff);
                    border: 1px solid #dbe4ff;
                    border-left: 6px solid #4b6cb7;
                    padding: 16px;
                    margin: 12px 0;
                    border-radius: 14px;
                    box-shadow: 0 4px 12px rgba(0,0,0,0.08);">

                    <div style="font-size:14px;color:#666;margin-bottom:6px;">
                        Equivalent State Group
                    </div>

                    <div style="font-size:18px;font-weight:600;color:#1f2a44;">
                        {' , '.join(g)}
                    </div>

                </div>
                """,
                unsafe_allow_html=True
            )
