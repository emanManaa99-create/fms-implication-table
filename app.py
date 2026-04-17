import streamlit as st

st.set_page_config(page_title="FSM Tool", layout="centered")

st.markdown(
    """
    <div style="
        text-align:center;
        padding:10px;
        background-color:#1f1f1f;
        border-radius:10px;
        margin-bottom:20px;">
        <h2 style="color:white;">FSM Minimization Tool</h2>
        <p style="color:#bbb;">Moore / Mealy - Implication based grouping</p>
    </div>
    """,
    unsafe_allow_html=True
)

mode = st.selectbox("Select Mode", ["Moore", "Mealy"])
n = st.number_input("Number of States", 2, 10, 4)

states = [chr(65+i) for i in range(int(n))]

st.markdown("### Input Table")

t = []
o = []

for i in range(int(n)):
    st.markdown(f"**State {states[i]}**")
    t.append(st.text_input(f"Next states {states[i]}", key=f"t{i}"))
    o.append(st.text_input(f"Output {states[i]}", key=f"o{i}"))

st.markdown("---")


def minimize(states, t, o):

    n = len(states)
    mark = [[0]*n for _ in range(n)]

    for i in range(n):
        for j in range(i):
            if o[i] != o[j]:
                mark[i][j] = 1

    change = True
    while change:
        change = False

        for i in range(n):
            for j in range(i):

                if mark[i][j] == 1:
                    continue

                try:
                    ti = list(map(int, t[i].split()))
                    tj = list(map(int, t[j].split()))
                except:
                    return None

                for k in range(len(ti)):
                    a = max(ti[k], tj[k])
                    b = min(ti[k], tj[k])

                    if mark[a][b] == 1:
                        mark[i][j] = 1
                        change = True
                        break

    vis = [0]*n
    groups = []

    for i in range(n):
        if not vis[i]:
            g = [states[i]]
            vis[i] = 1

            for j in range(i+1, n):
                if mark[max(i,j)][min(i,j)] == 0:
                    g.append(states[j])
                    vis[j] = 1

            groups.append(g)

    return groups


if st.button("Minimize FSM 🚀"):

    if all(t) and all(o):

        result = minimize(states, t, o)

        if result is None:
            st.error("Check input format")
        else:
            st.success("Equivalent States Found:")

            for g in result:
                st.markdown(
                    f"""
                    <div style="
                        padding:10px;
                        margin:5px;
                        background-color:#262730;
                        border-radius:8px;
                        color:white;">
                        {' , '.join(g)}
                    </div>
                    """,
                    unsafe_allow_html=True
                )

    else:
        st.warning("Please fill all fields")
