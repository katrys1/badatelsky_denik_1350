import streamlit as st
import time
import os
import base64
from PIL import Image

# --- 1. KONFIGURACE STRÁNKY ---
st.set_page_config(page_title="Badatelský deník 1350", page_icon="🌿", layout="wide")

# --- 2. STYLIZACE (OPRAVENÁ PRO SIDEBAR) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Texturina:wght@400;700&display=swap');

    /* Globální nastavení písma */
    html, body, [data-testid="stAppViewContainer"], .stMarkdown, p, span, label, li, div {
        font-family: 'Texturina', serif !important;
        color: #000000 !important;
    }

    /* Specifické nastavení pro Sidebar, aby nezmizel text a ikony */
    [data-testid="stSidebar"] {
        background-color: #ffffff !important;
        border-right: 2px solid #000000 !important;
    }
    
    [data-testid="stSidebar"] * {
        color: #000000 !important;
        font-family: 'Texturina', serif !important;
    }

    /* Oprava ikon v postranním panelu (zamezí zobrazení textu keyboard_double místo ikony) */
    i.material-icons,
    i.material-icons-outlined,
    i.material-icons-round,
    i.material-icons-sharp,
    i.material-icons-two-tone,
    .stIconMaterial,
    [data-testid="stSidebarCollapseButton"] *,
    [data-testid="collapsedControl"] *,
    [data-testid="stExpanderToggleIcon"] *,
    span[class*="stIconMaterial"],
    span[class*="material-symbols"] {
        font-family: "Material Symbols Rounded", "Material Icons", sans-serif !important;
        font-variant: normal !important;
        text-transform: none !important;
    }

    /* Oprava viditelnosti postranních prvků */
    [data-testid="stSidebarNav"] {
        background-color: transparent !important;
    }

    input, textarea, select, div[data-baseweb="select"], .stTextArea textarea {
        color: #000000 !important;
        background-color: #f0f2f6 !important;
        -webkit-text-fill-color: #000000 !important;
        border: 1px solid #000000 !important;
    }

    .stApp {
        background-color: #ffffff !important;
    }

    .stButton>button {
        width: 100%;
        border-radius: 0px;
        background-color: #ffffff !important;
        color: #000000 !important;
        border: 2px solid #000000 !important;
        font-family: 'Texturina', serif !important;
        font-variant: small-caps;
        font-weight: bold;
    }
    
    .stButton>button:hover {
        background-color: #000000 !important;
        color: #ffffff !important;
    }

    .stProgress > div > div > div > div {
        background-color: #000000 !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. INICIALIZACE STAVU ---
if 'step' not in st.session_state:
    st.session_state.step = 0
    st.session_state.substep = 0
    st.session_state.xp = 0
    st.session_state.claimed_xp = set()
    st.session_state.max_xp = 500
    st.session_state.denik = []
    st.session_state.diary_entries = []
    st.session_state.paska = []  
    st.session_state.current_tool = "1"
    
    # Pomocné stavy pro Level 2
    st.session_state.l2_found = []
    st.session_state.smer_urcen = False
    
    # Brašna
    st.session_state.kresadlo_unlocked = False
    st.session_state.olovnice_unlocked = False
    st.session_state.lupa_unlocked = False
    st.session_state.klic_unlocked = False
    st.session_state.pigmenty_unlocked = False
    st.session_state.stetec_unlocked = False
    
    st.session_state.kresadlo_lost = False
    st.session_state.olovnice_lost = False
    st.session_state.lupa_lost = False
    st.session_state.klic_lost = False
    st.session_state.pigmenty_lost = False
    st.session_state.stetec_lost = False
    st.session_state.l2_exam_step = 0
    st.session_state.l2_exam_health = 3

    if 'grid' not in st.session_state:
        size = 7
        st.session_state.grid = [["." for _ in range(size)] for _ in range(size)]

LIBRARY = {
    "1": {"id": "S", "name": "Studna", "char": "🔵"},
    "2": {"id": "C", "name": "Cesta", "char": "▒"},
    "3": {"id": "Z", "name": "Zeď", "char": "🧱"},
    "4": {"id": "L", "name": "Lilie", "char": "⚜️"},
    "5": {"id": "R", "name": "Růže", "char": "🌹"},
    "6": {"id": "B", "name": "Bylinky", "char": "🌿"},
}


def claim_xp(amount, key):
    if key not in st.session_state.claimed_xp:
        st.session_state.xp += amount
        st.session_state.claimed_xp.add(key)
        return True
    return False

def render_church_blueprint():
    found = st.session_state.l2_found
    
    # Barvy
    base_color = "#1e293b" # tmavě břidlicová
    active_color = "#fbbf24" # zlatá
    glass_colors = ["#3b82f6", "#ef4444", "#10b981", "#f59e0b"] # modrá, červená, zelená, oranžová
    
    # Logika prvků
    arch_color = active_color if "3" in found else base_color
    ribs_opacity = "1" if "2" in found else "0.1"
    keystone_color = active_color if "1" in found else base_color
    glass_opacity = "0.6" if "4" in found else "0"
    
    svg = f'<div style="display: flex; justify-content: center; margin: 1rem 0;">' \
          f'<svg width="180" height="220" viewBox="0 0 200 250" style="filter: drop-shadow(0 0 10px rgba(0,0,0,0.5)); transition: all 1s;">' \
          f'<!-- Vitráž (4) -->' \
          f'<path d="M 20 230 L 20 120 Q 100 -20 180 120 L 180 230 Z" fill="url(#glassGradient)" style="opacity: {glass_opacity}; transition: opacity 1.5s ease-in-out;" />' \
          f'<!-- Lomený oblouk (3) -->' \
          f'<path d="M 20 230 L 20 120 Q 100 -20 180 120 L 180 230" fill="none" stroke="{arch_color}" stroke-width="6" stroke-linecap="round" style="transition: stroke 1s;" />' \
          f'<!-- Žebrová klenba (2) -->' \
          f'<g style="opacity: {ribs_opacity}; transition: opacity 1s;">' \
          f'<path d="M 20 120 Q 100 80 180 120" fill="none" stroke="{active_color}" stroke-width="2" stroke-dasharray="4" />' \
          f'<path d="M 20 120 L 180 120" fill="none" stroke="{active_color}" stroke-width="1" style="opacity: 0.3;" />' \
          f'<path d="M 100 50 L 20 120" fill="none" stroke="{active_color}" stroke-width="3" />' \
          f'<path d="M 100 50 L 180 120" fill="none" stroke="{active_color}" stroke-width="3" />' \
          f'</g>' \
          f'<!-- Svorník (1) -->' \
          f'<circle cx="100" cy="50" r="8" fill="{keystone_color}" stroke="{active_color if "1" in found else "none"}" stroke-width="2" style="transition: all 1s; filter: {"drop-shadow(0 0 5px gold)" if "1" in found else "none"};" />' \
          f'<defs>' \
          f'<linearGradient id="glassGradient" x1="0%" y1="0%" x2="100%" y2="100%">' \
          f'<stop offset="0%" style="stop-color:{glass_colors[0]};stop-opacity:1" />' \
          f'<stop offset="33%" style="stop-color:{glass_colors[1]};stop-opacity:1" />' \
          f'<stop offset="66%" style="stop-color:{glass_colors[2]};stop-opacity:1" />' \
          f'<stop offset="100%" style="stop-color:{glass_colors[3]};stop-opacity:1" />' \
          f'</linearGradient>' \
          f'</defs>' \
          f'</svg>' \
          f'</div>'
    st.sidebar.markdown(svg, unsafe_allow_html=True)

def add_diary_entry(text):
    if text not in st.session_state.diary_entries:
        st.session_state.diary_entries.append(text)

# --- 4. SIDEBAR ---
with st.sidebar:
    st.header("📖 Badatelský deník")
    with st.expander("Zobrazit mé poznámky"):
        # --- INTERAKTIVNÍ SCHÉMA ---
        render_church_blueprint()
        
        if st.session_state.diary_entries:
            for entry in st.session_state.diary_entries:
                st.write(f"- {entry}")
        else:
            st.write("*Deník je zatím prázdný.*")

    st.header("🎵 Hudba")
    if os.path.exists("intro.mp3"):
        import streamlit.components.v1 as components
        with open("intro.mp3", "rb") as f:
            data = f.read()
            b64 = base64.b64encode(data).decode()
            st.markdown(f'<audio id="bg-music" src="data:audio/mp3;base64,{b64}" autoplay loop controls></audio>', unsafe_allow_html=True)
            
        components.html(
            """
            <script>
                const audio = window.parent.document.getElementById('bg-music');
                if (audio) {
                    audio.volume = 0.5;
                    const playOnInteraction = () => {
                        audio.play().catch(e => console.log(e));
                        window.parent.document.removeEventListener('click', playOnInteraction);
                    };
                    window.parent.document.addEventListener('click', playOnInteraction);
                }
            </script>
            """,
            height=0,
            width=0
        )
    
    if st.session_state.step > 0:
        st.divider()
        st.header("🎒 Brašna poutníka")
        items = [
            ("🔥 Křesadlo", "kresadlo_unlocked"),
            ("📐 Olovnice", "olovnice_unlocked"),
            ("🔍 Křišťálová lupa", "lupa_unlocked"),
            ("🗝️ Zlatý klíč", "klic_unlocked"),
            ("🎨 Pigmenty", "pigmenty_unlocked"),
            ("🖌️ Mistrův štětec", "stetec_unlocked")
        ]
        for name, key in items:
            if st.session_state.get(f"{key.split('_')[0]}_lost", False):
                st.write(f"❌ {name} (*ztraceno*)")
            elif st.session_state.get(key, False):
                st.write(f"✅ {name}")
            else:
                st.write(f"🔒 {name} (*zamčeno*)")
        
        st.warning("⚠️ **Pozor, badateli!** O získané předměty můžeš špatným rozhodnutím i přijít.")
        
        
    st.divider()
    
    # --- VÝPOČET ROZETY DLE PŘEDMĚTŮ V BRAŠNĚ ---
    completed_segments = 0
    if st.session_state.get("kresadlo_unlocked", False): completed_segments += 1
    if st.session_state.get("olovnice_unlocked", False): completed_segments += 1
    if st.session_state.get("lupa_unlocked", False): completed_segments += 1
    if st.session_state.get("klic_unlocked", False): completed_segments += 1
    if st.session_state.get("pigmenty_unlocked", False): completed_segments += 1
    if st.session_state.get("stetec_unlocked", False): completed_segments += 2
    if st.session_state.get("step", 0) >= 7: completed_segments += 1  # Úspěšné dokončení
    
    total_segments = 8
    completed_segments = min(completed_segments, total_segments)
    procenta = completed_segments / total_segments
    percentage = procenta * 100
    is_maxed = completed_segments == total_segments
    
    # --- SVG ROZETA (z rozeta.py) ---
    import math
    colors = ['#3b82f6', '#8b5cf6', '#ec4899', '#f59e0b', '#10b981', '#ef4444', '#6366f1', '#a855f7']
    
    svg_paths = ""
    for i in range(total_segments):
        angle = 360 / total_segments
        start_angle = i * angle
        end_angle = (i + 1) * angle
        
        def polar_to_cartesian(cx, cy, r, angle_deg):
            angle_rad = (angle_deg - 90) * math.pi / 180.0
            return cx + r * math.cos(angle_rad), cy + r * math.sin(angle_rad)
            
        start_x, start_y = polar_to_cartesian(100, 100, 80, end_angle)
        end_x, end_y = polar_to_cartesian(100, 100, 80, start_angle)
        large_arc_flag = "0" if end_angle - start_angle <= 180 else "1"
        
        path_d = f"M 100 100 L {start_x} {start_y} A 80 80 0 {large_arc_flag} 0 {end_x} {end_y} Z"
        fill_color = colors[i] if i < completed_segments else '#1e293b'
        opacity = "0.9" if i < completed_segments else "0.3"
        
        svg_paths += f'<path d="{path_d}" fill="{fill_color}" stroke="#0f172a" stroke-width="2" style="opacity: {opacity}; transition: all 0.7s ease-in-out;" />'

    glow_filter = """
<defs>
  <filter id="glow">
    <feGaussianBlur stdDeviation="3.5" result="coloredBlur"/>
    <feMerge>
      <feMergeNode in="coloredBlur"/>
      <feMergeNode in="SourceGraphic"/>
    </feMerge>
  </filter>
</defs>
""" if is_maxed else ""
    
    filter_attr = 'filter="url(#glow)"' if is_maxed else ""
    center_color = "#fff" if is_maxed else "#334155"
    
    if is_maxed:
        status_text = "Rozeta je plná barev společně s tvojí malbou"
        status_color = "#facc15" # text-yellow-400
        status_class = "animate-pulse"
        scale = "scale(1.1)"
    else:
        status_text = f"Pokrok: {round(percentage)}%"
        status_color = "#94a3b8" # text-slate-400
        status_class = ""
        scale = "scale(1.0)"

    svg_html = f"""
<style>
@keyframes pulse {{
  0%, 100% {{ opacity: 1; }}
  50% {{ opacity: .5; }}
}}
.animate-pulse {{
  animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}}
</style>
<div style="display: flex; flex-direction: column; align-items: center; justify-content: center; margin-top: 1rem; margin-bottom: 1rem; transition: all 1s; transform: {scale};">
<svg width="200" height="200" viewBox="0 0 200 200" style="filter: drop-shadow(0 25px 25px rgb(0 0 0 / 0.15));">
{glow_filter}
<g {filter_attr}>
{svg_paths}
<circle cx="100" cy="100" r="15" fill="{center_color}" style="transition: fill 1s;" />
</g>
</svg>
<!-- Textové info ve stylu rozeta.py -->
<div style="margin-top: 1.5rem; text-align: center;">
<h2 class="{status_class}" style="font-size: 1.25rem; font-family: serif; font-weight: bold; text-transform: uppercase; letter-spacing: 0.1em; color: {status_color}; margin: 0;">
{status_text}
</h2>
<p style="color: #64748b; margin-top: 0.5rem; font-family: monospace; font-size: 1rem; margin-bottom: 0;">
{st.session_state.xp} / {st.session_state.max_xp} XP
</p>
</div>
</div>
"""
    st.markdown(svg_html, unsafe_allow_html=True)
    # --- KONEC SVG ROZETY ---
    if 'jmeno' in st.session_state:
        st.caption(f"Poutník: {st.session_state.jmeno}")

    # --- ADMINISTRÁTORSKÝ GOD MODE ---
    with st.expander("👁️‍🗨️", expanded=False):
        admin_kod = st.text_input("Tajný kód", type="password", label_visibility="collapsed")
        if admin_kod == "1350":
            st.warning("⚙️ God Mode Aktivován")
            col_s1, col_s2 = st.columns(2)
            new_s = col_s1.number_input("Step", 0, 7, int(st.session_state.step))
            new_sub = col_s2.number_input("Substep", 0, 5, int(st.session_state.substep))
            
            if st.button("🚀 Přesunout se"):
                st.session_state.step = new_s
                st.session_state.substep = new_sub
                st.rerun()
                
            if st.button("🔑 Odemknout vše"):
                st.session_state.kresadlo_unlocked = True
                st.session_state.olovnice_unlocked = True
                st.session_state.lupa_unlocked = True
                st.session_state.klic_unlocked = True
                st.session_state.pigmenty_unlocked = True
                st.session_state.stetec_unlocked = True
                st.session_state.xp = st.session_state.max_xp
                # Fill claimed_xp for god mode
                st.session_state.claimed_xp.update(["l2_exam", "l2_cardinal", "l3_study", "l3_lupa", "l4_script", "l5_workshop", "l5_olovnice", "l6_realization"])
                for i in range(1, 5): st.session_state.claimed_xp.add(f"l2_item_{i}")
                st.rerun()

            st.divider()
            # --- PŘESUNUTÁ NAVIGACE ---
            levels = [0, 2, 3, 4, 4.5, 5, 6, 7]
            current_index = levels.index(st.session_state.step) if st.session_state.step in levels else 0
            
            c_prev, c_next = st.columns(2)
            if current_index > 0:
                if c_prev.button("⬅️ Předchozí", key="god_prev"):
                    st.session_state.step = levels[current_index - 1]
                    st.session_state.substep = 0
                    st.rerun()
            if current_index < len(levels) - 1:
                if c_next.button("Další ➡️", key="god_next"):
                    st.session_state.step = levels[current_index + 1]
                    st.session_state.substep = 0
                    st.rerun()

    # --- 5. LOGIKA PRŮCHODU ---

# --- ÚROVEŇ 0: ÚVOD ---
if st.session_state.step == 0:
    if os.path.exists("poutnik.jpg"): st.image("poutnik.jpg", width="stretch")
    st.header("Badatelský deník: Malířská dílna (1350)")
    st.session_state.jmeno = st.text_input("Zadej své jméno, badateli:")
    rok = st.number_input("Rok tvého narození (do deníku):", min_value=1300, max_value=2026, value=2010)
    if st.session_state.jmeno and st.button("Vstoupit"):
        st.session_state.rok_narozeni = rok
        st.session_state.step = 2
        st.session_state.substep = 0
        st.rerun()

# --- ÚROVEŇ 1 & 2: SAKRÁLNÍ PROSTOR A ARCHITEKTURA ---
elif st.session_state.step == 2:
    
    # 1. FÁZE: Hledání prvků
    if st.session_state.substep == 0:
        st.subheader("🏛️ ÚROVEŇ 2: SAKRÁLNÍ PROSTOR A ARCHITEKTURA")
        st.write(f"Vítej, {st.session_state.jmeno}. Ztiš se a vnímej prostor.")
        st.info("Mistr stavitel: „Zvedni hlavu. Co drží tuto stavbu nad tebou?“")
        
        if os.path.exists("b_sipky.jpg"): st.image("b_sipky.jpg", width="stretch")
        targets = {"1": "Svorník", "2": "Žebrová klenba", "3": "Lomený oblouk", "4": "Vitráž"}
        
        cols = st.columns(4)
        for i, (num, name) in enumerate(targets.items()):
            if num in st.session_state.l2_found:
                cols[i].success(f"✅ {name}")
            else:
                if cols[i].button(f"Najít {num}"):
                    st.session_state.l2_found.append(num)
                    claim_xp(20, f"l2_item_{num}")
                    st.rerun()
        
        if len(st.session_state.l2_found) >= 4:
            st.success("Našel jsi všechny stavební prvky! Za své úsilí získáváš 🔥 Křesadlo.")
            st.session_state.kresadlo_unlocked = True
            add_diary_entry("Do poutníkovy brašny se přidaly první předměty, které jsem na své pouti využíval.")
            
            st.divider()
            st.write("Mistr stavitel: „Pohleď na tuto stavbu ještě jednou Jak bys popsal podstatu této stavby?“")
            col_p1, col_p2 = st.columns(2)
            if col_p1.button("🌑 Pevnost a tma"):
                st.error("Mistr: „Zvolil jsi špatně a přišel jsi o křesadlo.“")
                st.session_state.kresadlo_unlocked = False
                st.session_state.kresadlo_lost = True
                st.session_state.substep = 1
                st.rerun()
            if col_p2.button("✨ Lehkost a světlo"):
                st.success("Mistr: „Správně vnímáš ducha gotiky.“")
                st.session_state.substep = 1
                st.rerun()

    # 2. FÁZE: Mistrova zkouška stability
    elif st.session_state.substep == 1:
        st.subheader("📜 Mistrova zkouška stability")
        
        # Ukazatel stability (Health)
        health_icons = "❤️" * st.session_state.l2_exam_health + "🖤" * (3 - st.session_state.l2_exam_health)
        st.write(f"**Stabilita tvých vědomostí:** {health_icons}")
        
        # Definice otázek a správných odpovědí
        questions = [
            ("Jaký sloh definuje tyto lomené tvary?", ["gotika", "gotický"]),
            ("Kamenná žebra se sbíhají v...", ["svorník", "svorníku"]),
            ("Jak se říká oknu s barevným sklem?", ["vitráž", "vitrážové okno"])
        ]
        
        curr_q = st.session_state.l2_exam_step
        if curr_q < 3:
            q_text, answers = questions[curr_q]
            # Použijeme jedinečný klíč pro text_input, aby se při každé otázce choval správně
            user_ans = st.text_input(f"Otázka č. {curr_q + 1}: {q_text}", key=f"q_input_{curr_q}").lower().strip()
            
            if st.button("Potvrdit odpověď"):
                if user_ans in answers:
                    st.success("Mistr: „Správně. Stavba stojí pevně.“")
                    st.session_state.l2_exam_step += 1
                    if st.session_state.l2_exam_step == 3:
                        st.success("Mistr: „Prošel jsi zkouškou bez zhroucení klenby. Získáváš 📐 Olovnici, nástroj přesnosti.“")
                        st.session_state.olovnice_unlocked = True
                        claim_xp(50, "l2_exam")
                        st.session_state.substep = 2
                    st.rerun()
                else:
                    st.session_state.l2_exam_health -= 1
                    if st.session_state.l2_exam_health <= 0:
                        st.error("!!! KLENBA PRASKLA !!!")
                        st.error("Mistr: „Tvá neznalost ohrožuje samotnou stavbu! Jdi zpět a dívej se pozorněji.“")
                        # Reset celého postupu úrovně 2
                        st.session_state.substep = 0
                        st.session_state.l2_found = []
                        st.session_state.l2_exam_health = 3
                        st.session_state.l2_exam_step = 0
                    else:
                        st.warning(f"Mistr: „Pozor! V klenbě se objevila prasklina. Tvá stabilita klesá.“")
                    st.rerun()
        else:
            # Pojistka pro případ, že by se hráč vrátil
            st.session_state.substep = 2
            st.rerun()

    # 3. FÁZE: PŮDORYS
    elif st.session_state.substep == 2:
        st.subheader("🧭 Postupuj hlouběji do chrámu")
        st.write("Mistr: „Kde právě teď stojíš?")

        c1, c2, c3 = st.columns([1, 2, 1])
        with c2:
            if st.button("⚜️ Oltář"):
                st.warning("Mistr: „Nespěchej, nejdříve musíš určit svou polohu v kněžišti.“")
                if st.session_state.olovnice_unlocked:
                    st.error("Zatoulal jsi se a tvá 📐 Olovnice se ztratila v prachu.")
                    st.session_state.olovnice_unlocked = False
                    st.session_state.olovnice_lost = True

        c1, c2, c3 = st.columns([1, 2, 1])
        with c2:
            if st.button("⛪ Kněžiště", type="primary"):
                st.session_state.substep = 3
                st.rerun()

        c1, c2, c3 = st.columns([1, 2, 1])
        with c2:
            if st.button("👣 Hlavní loď"):
                st.info("Zde jsi jen jedním z mnoha. Běž dál.")
                if st.session_state.olovnice_unlocked:
                    st.error("Ztratil jsi pozornost i 📐 Olovnici.")
                    st.session_state.olovnice_unlocked = False
                    st.session_state.olovnice_lost = True

        col_l, col_r = st.columns(2)
        with col_l:
            if st.button("🕯️ Boční loď (vlevo)"): 
                st.toast("Jen prach...")
                if st.session_state.olovnice_unlocked:
                    st.session_state.olovnice_unlocked = False
                    st.session_state.olovnice_lost = True
        with col_r:
            if st.button("🕯️ Boční loď (vpravo)"): 
                st.toast("Tudy ne.")
                if st.session_state.olovnice_unlocked:
                    st.session_state.olovnice_unlocked = False
                    st.session_state.olovnice_lost = True

    # 4. FÁZE: Rituál Olovnice
    elif st.session_state.substep == 3:
        st.subheader("📐 Rituál Olovnice v Kněžišti")
        st.success("Správně! Přistoupil jsi ke stupňům kněžiště.")
        st.session_state.olovnice_unlocked = True

        st.write("Mistr: „Na jakou světovou stranu se díváš?“")
        comp = st.columns(4)
        if comp[0].button("SEVER"): 
            st.error("To není správně. Tvá nejistota tě stála 📐 Olovnici.")
            st.session_state.olovnice_unlocked = False
            st.session_state.olovnice_lost = True
        if comp[1].button("VÝCHOD", type="primary"):
            st.session_state.smer_urcen = True
            st.rerun()
        if comp[2].button("JIH"): 
            st.error("Zkus to znovu. Ale dávej pozor!")
            if st.session_state.olovnice_unlocked:
                st.session_state.olovnice_unlocked = False
                st.session_state.olovnice_lost = True
        if comp[3].button("ZÁPAD"): 
            st.error("Zkus opačnou světovou stranu.")
            if st.session_state.olovnice_unlocked:
                st.session_state.olovnice_unlocked = False
                st.session_state.olovnice_lost = True

        if st.session_state.get('smer_urcen', False):
            st.success("Správně. Východ je směr světla.")
            if st.button("Pokročit k oltáři (+40 XP)"):
                claim_xp(40, "l2_cardinal")
                add_diary_entry("Prozkoumal jsem architekturu chrámu a poodhalil tajemství jeho stavby.")
                st.session_state.step = 3
                st.session_state.substep = 0
                st.session_state.smer_urcen = False
                st.rerun()
    

# --- ÚROVEŇ 3: STUDIUM DÍLA ---
elif st.session_state.step == 3:
    add_diary_entry("Přistoupil jsem k oltářní desce se Zvěstováním a začal s jejím studiem.")
    if st.session_state.substep == 0:
        col_main, col_side = st.columns([3, 1])
        with col_main:
            if os.path.exists("c.jpg"): st.image("c.jpg", width="stretch")
            if st.button("Prozkoumat oltářní desku"):
                st.session_state.substep = 1
                st.rerun()
        with col_side:
            if os.path.exists("predikonograficky_popis.png"):
                st.image("predikonograficky_popis.png", width="stretch")
    elif st.session_state.substep == 1:
        col_main, col_side = st.columns([3, 1])
        with col_main:
            if os.path.exists("image_c6a996.jpg"): st.image("image_c6a996.jpg", width="stretch")
            if st.button("Studovat detaily"):
                st.session_state.substep = 2
                st.rerun()
            if st.session_state.get("lupa_unlocked", False):
                if st.button("🔍 Použít křišťálovou lupu (+10 XP)"):
                    st.success("Lupa odhalila jemné detaily!")
                    claim_xp(10, "l3_lupa")
                    st.session_state.substep = 2
                    st.rerun()

    else:
        col_main, col_side = st.columns([3, 1])
        with col_main:
            st.subheader("ÚROVEŇ 3: STUDIUM DÍLA")
            vjem = st.text_input("Zapiš detail, který tě zaujal:", key="ans3")
            if vjem and st.button("Uložit do deníku (+50 XP)"):
                st.session_state.denik.append(vjem)
                claim_xp(50, "l3_study")
                add_diary_entry("Postupně jsem prošel předikonografickým popisem, ikonografickým popisem a interpretací obrazu.")
                st.session_state.lupa_unlocked = True
                st.session_state.step = 4
                st.session_state.substep = 0
                st.rerun()


# --- ÚROVEŇ 4: PÍSMO ---
elif st.session_state.step == 4:
    if st.session_state.substep == 0:
        col_main, col_side = st.columns([3, 1])
        with col_main:
            if os.path.exists("d.jpg"): st.image("d.jpg", width="stretch")
            if st.button("Prozkoumat listiny"):
                st.session_state.substep = 1
                st.rerun()
        with col_side:
            if os.path.exists("ikonograficky_popis.png"):
                st.image("ikonograficky_popis.png", width="stretch")
    elif st.session_state.substep == 1:
        if os.path.exists("image.png"): st.image("image.png", width="stretch")
        if st.button("Rozluštit kód textu"):
            st.session_state.substep = 2
            st.rerun()
    else:
        st.subheader("ÚROVEŇ 4: ZNALOST PÍSMA")
        kod = st.text_input("Zadej kód:", key="ans4").upper().strip()
        if kod == "L 1, 26":
            st.success("Získal jsi 🗝️ Zlatý klíč.")
            st.session_state.klic_unlocked = True
            if st.button("Vstoupit do chodby (+90 XP)"):
                claim_xp(90, "l4_script")
                st.session_state.step = 4.5
                st.session_state.substep = 0
                st.rerun()

# --- ÚROVEŇ 4.5: TAJNÁ MÍSTNOST ---
elif st.session_state.step == 4.5:
    st.subheader("Skrytá chodba za oltářem")
    
    if os.path.exists("tajna_mistnost.jpg"): 
        st.image("tajna_mistnost.jpg", width="stretch", caption="Vstoupil jsi do zapomenutého archivu.")
    
    st.write("Klíč v tvé dlani začal hřát. Odsunul jsi těžký svícen a uviděl úzké schodiště.")
    st.info("Vidíš starý svitek s dalšími instrukcemi, které si přečti ve svých badatelských listech.")
    
    if st.button("Pokračovat do dílen"):
        st.session_state.step = 5
        st.session_state.substep = 0
        st.rerun()

# --- ÚROVEŇ 5: DÍLNY ---
elif st.session_state.step == 5:
    if st.session_state.substep == 0:
        col_main, col_side = st.columns([3, 1])
        with col_main:
            if os.path.exists("e.jpg"): st.image("e.jpg", width="stretch")
            if st.button("Vybrat si mistrovskou specializaci"):
                st.session_state.substep = 1
                st.rerun()
        with col_side:
            if os.path.exists("ikonograficka_interpretace.png"):
                st.image("ikonograficka_interpretace.png", width="stretch")
    else:
        st.subheader("ÚROVEŇ 5: DÍLENSKÁ SPECIALIZACE - Práce s badatelskými listy")
        if 'skupina' not in st.session_state:
            cA, cB, cC = st.columns(3)
            if cA.button("A: Písaři"): st.session_state.skupina = "A"; st.rerun()
            if cB.button("B: Herbáři"): st.session_state.skupina = "B"; st.rerun()
            if cC.button("C: Figuralisté"): st.session_state.skupina = "C"; st.rerun()
        else:
            st.session_state.pigmenty_unlocked = True
            # Úprava poměru sloupců, aby byl pravý sloupec mnohem širší a obrázky byly přímo čitelné
            col_main, col_side = st.columns([1, 1.5])
            with col_side:
                if st.session_state.skupina == "A" and os.path.exists("A.png"):
                    st.image("A.png", width="stretch")
                elif st.session_state.skupina == "B" and os.path.exists("B.png"):
                    st.image("B.png", width="stretch")
                elif st.session_state.skupina == "C" and os.path.exists("C.png"):
                    st.image("C.png", width="stretch")
            with col_main:
                if st.session_state.skupina == "A":
                    st.write("Napiš správně text a odpověz na badatelskou otázku z listu")
                    spravne = ["Ave", "gratia", "plena", "Dominus", "tecum"]
                    slova = ["plena", "Ave", "tecum", "gratia", "Dominus"]
                    cols = st.columns(5)
                    for i, s in enumerate(slova):
                        if cols[i].button(s, key=f"p_{i}"): st.session_state.paska.append(s); st.rerun()
                    st.info(f"Nápis: {' '.join(st.session_state.paska)}")
                    if st.button("Smazat"): st.session_state.paska = []; st.rerun()
                    if st.session_state.paska == spravne and st.button("Odevzdat hotové dílo (+90 XP)"):
                        claim_xp(90, "l5_workshop")
                        add_diary_entry("Postupně jsem prošel předikonografickým popisem, ikonografickým popisem a interpretací obrazu.")
                        st.session_state.step = 6
                        st.session_state.substep = 0
                        st.rerun()
    
                elif st.session_state.skupina == "B":
                    tcols = st.columns(6)
                    for i, (k, v) in enumerate(LIBRARY.items()):
                        if tcols[i].button(v['char'], key=f"t_{k}"): st.session_state.current_tool = k
                    for r in range(7):
                        gcols = st.columns(7)
                        for c in range(7):
                            if gcols[c].button(st.session_state.grid[r][c], key=f"g_{r}_{c}"):
                                 st.session_state.grid[r][c] = LIBRARY[st.session_state.current_tool]["char"]
                                 st.rerun()
                    
                    if st.session_state.get("olovnice_unlocked", False):
                        if st.button("📐 Použít olovnici pro vyrovnání tvojí zahrady (+10 XP)"):
                            st.success("Zahrada je nyní dokonale zarovnaná!")
                            claim_xp(10, "l5_olovnice")
                            
                    if st.button("Zahrada je vysázena (+90 XP)"):
                        claim_xp(90, "l5_workshop")
                        add_diary_entry("Postupně jsem prošel předikonografickým popisem, ikonografickým popisem a interpretací obrazu.")
                        st.session_state.step = 6
                        st.session_state.substep = 0
                        st.rerun()
    
                elif st.session_state.skupina == "C":
                    odev = st.text_area("Proč je andělův oděv tak zdobný?")
                    if odev and st.button("Odeslat mistrovi (+90 XP)"):
                        claim_xp(90, "l5_workshop")
                        add_diary_entry("Postupně jsem prošel předikonografickým popisem, ikonografickým popisem a interpretací obrazu.")
                        st.session_state.step = 6
                        st.session_state.substep = 0
                        st.rerun()

# --- ÚROVEŇ 6: REALIZACE ---
elif st.session_state.step == 6:
    st.session_state.stetec_unlocked = True
    if st.session_state.substep == 0:
        if os.path.exists("f.jpg"): st.image("f.jpg", width="stretch")
        if st.button("Vstoupit k malbě"):
            st.session_state.substep = 1
            st.rerun()
    else:
        st.subheader("ÚROVEŇ 6: REALIZACE")
        up = st.file_uploader("Nahraj fotografii:", type=["jpg", "png"])
        if up:
             st.session_state.vlastni_kresba = up
             st.image(up, width="stretch")
             
             has_tools = st.session_state.get("pigmenty_unlocked", False) and st.session_state.get("stetec_unlocked", False)
             btn_label = "🎨 DOKONČIT MISTROVSKÉ DÍLO" if has_tools else "✏️ DOKONČIT PROSTOU SKICU"
             
             if st.button(btn_label):
                 if has_tools:
                     st.balloons()
                     st.session_state.masterpiece = True
                 else:
                     st.session_state.masterpiece = False
                 claim_xp(80, "l6_realization")
                 add_diary_entry("Namaloval jsem malbu inspirovanou tímto vzácným obrazem.")
                 st.session_state.step = 7
                 st.rerun()

# --- ÚROVEŇ 7: ZÁVĚR ---
elif st.session_state.step == 7:
    if os.path.exists("h.jpg"): st.image("h.jpg", width="stretch")
    st.header("Gratulujeme, mistře badateli!")
    
    # --- FINÁLNÍ DENÍK ---
    st.markdown("### 🖋️ Tvůj badatelský deník")
    rok_nar = st.session_state.get('rok_narozeni', 2010)
    
    diary_text = f"Badatelský deník mistra **{st.session_state.jmeno}**.\n"
    diary_text += f"Narozen léta Páně {rok_nar}.\n\n"
    for entry in st.session_state.diary_entries:
        diary_text += f"- {entry}\n"

    st.divider()
    if st.session_state.get("masterpiece", False):
        evaluation = "✨ **Zhodnocení cesty:** Tvá pouť byla vedena trpělivostí a moudrostí. Jako skutečný mistr jsi shromáždil všechnu výbavu a tvé dílo bylo toho důkazem. Zanechal jsi po sobě stopu, která v dějinách umění nevybledne."
    else:
        evaluation = "📉 **Zhodnocení cesty:** Tvá pouť byla plná objevů, ale v klíčové chvíli ti chyběly nástroje mistra. Tvé dílo zůstalo skicou, ale zkušenosti, které jsi nabral, byly neocenitelné. Příště hledej s větší pečlivostí."

    st.info(diary_text)
    st.success(evaluation)

    st.write(f"Získal jsi celkem {st.session_state.xp} XP.")
    st.divider()
    col_a, col_b = st.columns(2)
    with col_a:
        st.caption("Předloha")
        if os.path.exists("image_c6a996.jpg"): st.image("image_c6a996.jpg", width="stretch")
    with col_b:
        if 'vlastni_kresba' in st.session_state: st.image(st.session_state.vlastni_kresba, width="stretch")

