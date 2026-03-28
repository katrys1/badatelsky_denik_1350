import streamlit as st
import time
import os
import base64
from PIL import Image

# --- 1. KONFIGURACE STRÁNKY ---
st.set_page_config(page_title="Badatelský deník 1350", page_icon="🌿", layout="wide", initial_sidebar_state="collapsed")

# --- 2. STYLIZACE (ČISTĚ BÍLÁ A TEXTURINA) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Texturina:wght@400;700&display=swap');

    /* Globální písmo a ČISTĚ BÍLÉ POZADÍ */
    html, body, [data-testid="stAppViewContainer"], [data-testid="stHeader"], .stApp, .stMarkdown, p, span, h1, h2, h3, h4, h5, h6, label, .stMetric, .stSelectbox, .stTextInput, .stTextArea {
        background-color: #ffffff !important;
        font-family: 'Texturina', serif !important;
        color: #000000 !important;
    }

    /* Čitelná vstupní pole */
    input, textarea, [data-baseweb="input"], [data-baseweb="textarea"] {
        background-color: #ffffff !important;
        font-family: 'Texturina', serif !important;
        color: #000000 !important;
        border: 1px solid #0f172a !important;
        -webkit-text-fill-color: #000000 !important;
    }

    * { font-family: 'Texturina', serif !important; }

    /* Dashboard Kontejner */
    .dashboard-container {
        background: #ffffff;
        border: 2px solid #0f172a;
        border-radius: 16px;
        padding: 1.5rem;
        margin-bottom: 2rem;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
    }

    .rank-display {
        background: #0f172a;
        color: #ffffff !important;
        padding: 4px 12px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        font-size: 0.75rem;
        border-radius: 4px;
    }

    .inventory-item {
        display: inline-block;
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        padding: 4px 10px;
        margin: 4px;
        border-radius: 8px;
        font-size: 0.85rem;
    }

    .stButton>button {
        width: 100%;
        border-radius: 8px;
        padding: 0.6rem 1rem;
        background-color: #ffffff !important;
        color: #0f172a !important;
        border: 2px solid #0f172a !important;
        font-weight: 700;
        font-variant: small-caps;
    }
    .stButton>button:hover {
        background-color: #0f172a !important;
        color: #ffffff !important;
    }
    
    .stMetric {
        background: #ffffff;
        padding: 0.75rem;
        border-radius: 12px;
        border: 1px solid #e2e8f0;
    }

    @media (max-width: 768px) {
        .dashboard-container { padding: 1rem; }
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. INICIALIZACE STAVU & POMOCNÉ FUNKCE ---
def play_music():
    if os.path.exists("intro.mp3"):
        with open("intro.mp3", "rb") as f:
            b64 = base64.b64encode(f.read()).decode()
            st.markdown(f"""
                <audio id="bg-audio" src="data:audio/mp3;base64,{b64}" autoplay loop></audio>
                <script>
                    var audio = document.getElementById("bg-audio");
                    audio.volume = 0.4;
                </script>
            """, unsafe_allow_html=True)

def get_rank(xp):
    if xp < 200: return "Učeň"
    if xp < 400: return "Tovaryš"
    return "Mistr"

if 'step' not in st.session_state:
    st.session_state.step = 0
    st.session_state.substep = 0
    st.session_state.xp = 0
    st.session_state.claimed_xp = set()
    st.session_state.max_xp = 500
    st.session_state.diary_entries = []
    st.session_state.l2_found = []
    st.session_state.kresadlo_unlocked = False
    st.session_state.lupa_unlocked = False
    st.session_state.klic_unlocked = False
    st.session_state.pigmenty_unlocked = False
    st.session_state.stetec_unlocked = False
    if 'grid' not in st.session_state:
        st.session_state.grid = [["." for _ in range(7)] for _ in range(7)]

def claim_xp(amount, key):
    if key not in st.session_state.claimed_xp:
        st.session_state.xp += amount
        st.session_state.claimed_xp.add(key)
        st.toast(f"Získal jsi {amount} XP! ✨")
        return True
    return False

def add_diary_entry(text):
    if text not in st.session_state.diary_entries:
        st.session_state.diary_entries.append(text)

# --- 4. KOMPONENTY DASHBOARDU ---
def render_church_blueprint():
    found = st.session_state.l2_found
    gold, base = "#fbbf24", "#0f172a"
    arch_color = gold if "3" in found else base
    ribs_opacity = "1" if "2" in found else "0.1"
    keystone_color = gold if "1" in found else base
    glass_opacity = "0.7" if "4" in found else "0"
    
    svg = f"""
    <div style="display: flex; justify-content: center; margin: 10px 0;">
    <svg width="200" height="240" viewBox="0 0 200 250">
        <defs><linearGradient id="glass" x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" style="stop-color:#3b82f6;stop-opacity:1"/><stop offset="100%" style="stop-color:#ef4444;stop-opacity:1"/></linearGradient></defs>
        <path d="M 20 230 L 20 120 Q 100 -20 180 120 L 180 230 Z" fill="url(#glass)" style="opacity: {glass_opacity}; transition: all 1s;" />
        <path d="M 20 230 L 20 120 Q 100 -20 180 120 L 180 230" fill="none" stroke="{arch_color}" stroke-width="6" style="transition: all 1s;" />
        <g style="opacity: {ribs_opacity}; transition: opacity 1s;"><path d="M 20 120 Q 100 80 180 120" fill="none" stroke="{gold}" stroke-width="2" stroke-dasharray="4" /><path d="M 100 50 L 20 120 M 100 50 L 180 120" stroke="{gold}" stroke-width="3" /></g>
        <circle cx="100" cy="50" r="10" fill="{keystone_color}" />
    </svg></div>"""
    st.markdown(svg, unsafe_allow_html=True)

def render_rozeta(size=100):
    import math
    completed = sum([st.session_state.get(k, False) for k in ["kresadlo_unlocked", "lupa_unlocked", "klic_unlocked", "pigmenty_unlocked", "stetec_unlocked"]]) + (1 if st.session_state.step >= 7 else 0)
    colors = ['#3b82f6', '#8b5cf6', '#ec4899', '#f59e0b', '#10b981', '#ef4444', '#6366f1', '#a855f7']
    svg_paths = ""
    for i in range(8):
        angle = 360 / 8
        s_ang = (i * angle - 90) * math.pi / 180.0
        e_ang = ((i + 1) * angle - 90) * math.pi / 180.0
        p_d = f"M 50 50 L {50 + 40*math.cos(s_ang)} {50 + 40*math.sin(s_ang)} A 40 40 0 0 1 {50 + 40*math.cos(e_ang)} {50 + 40*math.sin(e_ang)} Z"
        op = "0.9" if i < completed else "0.1"
        fill = colors[i] if i < completed else "#e2e8f0"
        svg_paths += f'<path d="{p_d}" fill="{fill}" style="opacity:{op}; transition: all 0.5s;" />'
    st.markdown(f'<div style="text-align:center;"><svg width="{size}" height="{size}" viewBox="0 0 100 100">{svg_paths}<circle cx="50" cy="50" r="8" fill="#1e293b"/></svg></div>', unsafe_allow_html=True)

def render_dashboard():
    # Only 6 possible milestones now (kresadlo, lupa, klic, pigmenty, stetec + end)
    # Wait, the list was 7 before including Olovnice. Now it's 6.
    completed = sum([st.session_state.get(k, False) for k in ["kresadlo_unlocked", "lupa_unlocked", "klic_unlocked", "pigmenty_unlocked", "stetec_unlocked"]]) + (1 if st.session_state.step >= 7 else 0)
    percentage = (completed / 6) * 100
    rank = get_rank(st.session_state.xp)

    with st.container():
        st.markdown('<div class="dashboard-container">', unsafe_allow_html=True)
        col_h1, col_h2, col_h3 = st.columns([2, 1, 1])
        with col_h1:
            st.markdown(f"### 🛡️ {st.session_state.get('jmeno', 'Poutník')}")
            st.markdown(f'<span class="rank-display">{rank}</span>', unsafe_allow_html=True)
            st.caption(f"Narozen léta Páně {st.session_state.get('rok_narozeni', '????')}")
        with col_h2: st.metric("Zkušenosti", f"{st.session_state.xp} XP")
        with col_h3: st.metric("Postup", f"{int(percentage)}%")
        st.divider()
        c1, c2 = st.columns([2.5, 1.5])
        with c1:
            st.markdown("##### 🎒 Brašna")
            items = [("🔥", "Křesadlo", "kresadlo_unlocked"), ("🔍", "Lupa", "lupa_unlocked"), ("🗝️", "Klíč", "klic_unlocked"), ("🎨", "Pigmenty", "pigmenty_unlocked"), ("🖌️", "Štětec", "stetec_unlocked")]
            html = '<div style="margin-bottom:10px;">'
            for icon, name, key in items:
                status = "✅" if st.session_state.get(key) else "🔒"
                op = "1" if st.session_state.get(key) else "0.3"
                html += f'<span class="inventory-item" style="opacity:{op}">{status} {icon} {name}</span>'
            html += '</div>'
            st.markdown(html, unsafe_allow_html=True)
        with c2: render_rozeta(80)
        st.markdown('</div>', unsafe_allow_html=True)

def render_admin():
    with st.expander("👁️‍Změna stavu", expanded=False):
        kod = st.text_input("Kód:", type="password", key="gm_pass")
        if kod == "1350":
            l1, l2 = st.columns(2)
            ns = l1.number_input("Level", 0, 7, int(st.session_state.step))
            nsub = l2.number_input("Substep", 0, 5, int(st.session_state.substep))
            if st.button("🚀 Skočit!"):
                st.session_state.step = ns; st.session_state.substep = nsub; st.rerun()
            if st.button("🔓 Odemknout Vše"):
                for k in ["kresadlo_unlocked", "lupa_unlocked", "klic_unlocked", "pigmenty_unlocked", "stetec_unlocked"]: st.session_state[k] = True
                st.rerun()

# --- 5. LOGIKA PRŮCHODU ---
if st.session_state.step > 0:
    play_music()
    render_dashboard()

# --- LEVEL 0: ÚVOD ---
if st.session_state.step == 0:
    st.title("🌿 Badatelský deník 1350")
    if os.path.exists("poutnik.jpg"): st.image("poutnik.jpg", width=900) # Fixed width for modern streamlit
    st.write("Vítej, poutníku v čase. Než vstoupíš do kroniky roku 1350, zapiš své údaje.")
    c1, c2 = st.columns(2)
    jmeno = c1.text_input("Tvé jméno:")
    rok = c2.number_input("Rok narození:", 1300, 2026, 2010)
    if jmeno and st.button("Vstoupit do kroniky"):
        st.session_state.jmeno = jmeno
        st.session_state.rok_narozeni = rok
        st.session_state.step = 2
        st.rerun()

# --- LEVEL 2: ARCHITEKTURA ---
elif st.session_state.step == 2:
    st.header("🏛️ Úroveň 2: Architektura")
    c_img, c_win = st.columns([1.5, 1])
    with c_img:
        if os.path.exists("b_sipky.jpg"): st.image("b_sipky.jpg", width=900)
    with c_win:
        st.write("Mistr stavitel: „Najdi prvky, které drží nebesa nad námi.“")
        render_church_blueprint()

    targets = {"1": "Svorník", "2": "Žebrová klenba", "3": "Lomený oblouk", "4": "Vitráž"}
    cols = st.columns(4)
    for i, (k, v) in enumerate(targets.items()):
        if k in st.session_state.l2_found: cols[i].success(f"✅ {v}")
        elif cols[i].button(v):
            st.session_state.l2_found.append(k); claim_xp(50, f"l2_{k}"); st.rerun()
    
    if len(st.session_state.l2_found) >= 4:
        st.success("Našel jsi všechny prvky! Mistr je spokojen s tvým okem pro detaily.")
        if st.button("Postoupit k studiu díla"):
            add_diary_entry("Prostudoval jsem prvky architektury.")
            st.session_state.step = 3
            st.rerun()

# --- LEVEL 3: STUDIUM ---
elif st.session_state.step == 3:
    st.header("🔍 Úroveň 3: Studium díla")
    if os.path.exists("image_c6a996.jpg"): st.image("image_c6a996.jpg", width=900)
    detail = st.text_input("Co tě na malbě nejvíce zaujalo?")
    if detail and st.button("Zapsat do deníku"):
        add_diary_entry(f"Studoval jsem detail: {detail}"); claim_xp(40, "l3_study"); st.session_state.lupa_unlocked = True; st.session_state.step = 4; st.rerun()

# --- LEVEL 4: PÍSMO ---
elif st.session_state.step == 4:
    st.header("📜 Úroveň 4: Písmo")
    if os.path.exists("d.jpg"): st.image("d.jpg", width=900)
    st.write("Rozlušti kód z badatelského listu (např. L 1, 26).")
    kod = st.text_input("Kód:").upper().strip()
    if kod == "L 1, 26":
        st.success("Kód přijat! Získal jsi 🗝️ Klíč."); st.session_state.klic_unlocked = True; claim_xp(60, "l4_script")
        if st.button("Otevřít tajnou chodbu"): st.session_state.step = 5; st.rerun()

# --- LEVEL 5: DÍLNY ---
elif st.session_state.step == 5:
    st.header("🎨 Úroveň 5: Dílny")
    if os.path.exists("e.jpg"): st.image("e.jpg", width=900)
    if 'skupina' not in st.session_state:
        st.write("Vyber si svou specializaci:")
        ca, cb, cc = st.columns(3)
        if ca.button("Písař"): st.session_state.skupina = "A"; st.rerun()
        if cb.button("Herbář"): st.session_state.skupina = "B"; st.rerun()
        if cc.button("Figuralista"): st.session_state.skupina = "C"; st.rerun()
    else:
        st.session_state.pigmenty_unlocked = True
        img_key = st.session_state.skupina
        if os.path.exists(f"{img_key}.png"): st.image(f"{img_key}.png", width=900)
        if st.session_state.skupina == "B":
            st.subheader("Herbářská zahrada")
            for r in range(3):
                gcols = st.columns(3)
                for c in range(3):
                    if gcols[c].button(st.session_state.grid[r][c], key=f"g_{r}_{c}"):
                        st.session_state.grid[r][c] = "🌿"; st.toast("Zasazeno! 🌿"); st.rerun()
            if st.button("Dokončit zahradu"): claim_xp(80, "l5_done"); add_diary_entry("Pracoval jsem v herbáři."); st.session_state.step = 6; st.rerun()
        else:
            if st.button("Dokončit práci"): st.session_state.step = 6; st.rerun()

# --- LEVEL 6: REALIZACE ---
elif st.session_state.step == 6:
    st.header("🖌️ Úroveň 6: Realizace")
    if os.path.exists("f.jpg"): st.image("f.jpg", width=900)
    st.session_state.stetec_unlocked = True
    up = st.file_uploader("Nahraj své dílo:", type=["png", "jpg"])
    if up:
        st.image(up, width=900)
        if st.button("Finalizovat dílo"): claim_xp(100, "l6_final"); add_diary_entry("Vytvořil jsem mistrovské dílo."); st.session_state.step = 7; st.rerun()

# --- LEVEL 7: ZÁVĚR ---
elif st.session_state.step == 7:
    st.header("🏆 Konec Pouti")
    if os.path.exists("h.jpg"): st.image("h.jpg", width=900)
    st.success(f"Gratulujeme, mistře {st.session_state.get('jmeno','')}!"); st.write(f"Zkušenosti: {st.session_state.xp}")
    st.markdown("### Tvůj Deník")
    for e in st.session_state.diary_entries: st.write(f"- {e}")
    if st.button("Začít znovu"): st.session_state.clear(); st.rerun()

render_admin()
