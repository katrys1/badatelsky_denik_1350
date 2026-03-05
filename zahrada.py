import streamlit as st

# Konfigurace stránky
st.set_page_config(page_title="Hortus Conclusus", layout="centered")

# Symbolika přímo z podkladů
LIBRARY = {
    "1": {"id": "S", "name": "Studna", "char": "🔵", "symbol": "Fons Signatus (Pramen zapečetěný)."},
    "2": {"id": "C", "name": "Cesta", "char": "▒", "symbol": "Symbol kříže a čtyř rajských řek."},
    "3": {"id": "Z", "name": "Zeď", "char": "🧱", "symbol": "Hortus Conclusus. Ochrana zahrady."},
    "4": {"id": "L", "name": "Lilie", "char": "⚜️", "symbol": "Čistota (atribut Panny Marie)."},
    "5": {"id": "R", "name": "Růže", "char": "🌹", "symbol": "Krev mučedníků (červená) nebo nebeská láska."},
    "6": {"id": "B", "name": "Bylinky", "char": "🌿", "symbol": "Salvia (Šalvěj) – symbol spásy a zdraví."},
}

# Inicializace stavu aplikace (Session State)
if 'grid' not in st.session_state:
    size = 7
    st.session_state.grid = [["." for _ in range(size)] for _ in range(size)]
    st.session_state.current_tool = "1"
    st.session_state.last_info = "Vyberte nástroj a klikněte do zahrady!"

st.title("🌿 Hortus Conclusus")

# --- UI: VÝBĚR NÁSTROJE ---
st.subheader("Výběr nástroje")
cols_tools = st.columns(len(LIBRARY))
for i, (k, v) in enumerate(LIBRARY.items()):
    label = f"{v['char']} {v['name']}"
    # Zvýraznění aktivního nástroje barvou tlačítka (v rámci možností Streamlitu)
    type_btn = "primary" if st.session_state.current_tool == k else "secondary"
    if cols_tools[i].button(label, key=f"tool_{k}", type=type_btn):
        st.session_state.current_tool = k
        st.session_state.last_info = f"Vybráno: {v['name']}"
        st.rerun()

st.divider()

# --- UI: ZAHRADA (MŘÍŽKA) ---
st.subheader("Zahrada")

# Styl pro mřížku
grid_container = st.container()

for r in range(7):
    cols = st.columns(7)
    for c in range(7):
        cell_content = st.session_state.grid[r][c]
        # Každé políčko je tlačítko
        if cols[c].button(cell_content, key=f"cell_{r}_{c}"):
            tool = LIBRARY[st.session_state.current_tool]
            st.session_state.grid[r][c] = tool["char"]
            st.session_state.last_info = f"Položeno: {tool['name']} - {tool['symbol']}"
            st.rerun()

st.divider()

# --- UI: KNIHA MOUDROSTI ---
st.info(f"**Kniha moudrosti:** {st.session_state.last_info}")

# Reset tlačítko
if st.button("Vysadit novou zahradu (Reset)"):
    st.session_state.grid = [["." for _ in range(7)] for _ in range(7)]
    st.session_state.last_info = "Zahrada byla vyčištěna."
    st.rerun()