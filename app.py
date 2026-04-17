import streamlit as st
import pandas as pd

st.set_page_config(page_title="FSM Tool", layout="wide")

st.markdown("""
<div style="background:linear-gradient(90deg,#4facfe,#00f2fe);
padding:25px;border-radius:15px;color:white;text-align:center">
<h2>FSM Minimization Tool</h2>
<p>Stable Version</p>
</div>
""", unsafe_allow_html=True)

mode = st.selectbox("Mode", ["Moore", "Mealy"])
n = st.number_input("States", 2, 8, 4)

states = [chr(65+i) for i in range(int(n))]

if "df" not in st.session_state:
    st.session_state.df = pd.DataFrame({
        "State": states,
        "00": ["" for _ in range(n)],
        "01": ["" for _ in range(n)],
        "10": ["" for _ in range(n)],
        "11": ["" for _ in range(n)],
        "Output": ["" for _ in range(n)]
    })

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
                for k in range(4):
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

                for k in range(4):

                    if trans[i][k] == "" or trans[j][k] == "":
                        continue

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
            clean(df.iloc[i]["00"]),
            clean(df.iloc[i]["01"]),
            clean(df.iloc[i]["10"]),
            clean(df.iloc[i]["11"]),
        ]

        o = clean(df.iloc[i]["Output"])

        if mode == "Moore" and o == "":
            invalid = True

        if mode == "Mealy" and any(x == "" for x in t):
            invalid = True

        for x in t:
            if x and not valid_state(x):
                invalid = True

        trans.append(t)
        out.append(o if mode == "Moore" else t)

    if invalid:
        st.error("Please complete all fields correctly")
    else:

        mark = minimize(states, trans, out, mode)

        draw_table(states, mark)

        groups = build_groups(states, mark)

        st.success("Equivalent Groups Found")

        for g in groups:
            st.markdown(
                f"""
                <div style="
                    background:white;
                    border-left:5px solid #4facfe;
                    padding:12px;
                    margin:10px 0;
                    border-radius:10px;">
                    <b>{', '.join(g)}</b>
                </div>
                """,
                unsafe_allow_html=True
            )

st.session_state.temp_df = df
