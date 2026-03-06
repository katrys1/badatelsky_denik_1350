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
    st.session_state.denik = []
    st.session_state.max_xp = 450
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

# --- 4. SIDEBAR ---
with st.sidebar:
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
            st.write(f"✅ {name}" if st.session_state.get(key, False) else f"🔒 *zamčeno*")
        
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
                st.rerun()

    # --- 5. LOGIKA PRŮCHODU ---

# --- ÚROVEŇ 0: ÚVOD ---
if st.session_state.step == 0:
    if st.session_state.substep == 0:
        if os.path.exists("poutnik.jpg"): st.image("poutnik.jpg", use_container_width=True)
        if st.button("Začít putování"):
            st.session_state.substep = 1
            st.rerun()
    else:
        st.header("Badatelský deník: Malířská dílna (1350)")
        st.session_state.jmeno = st.text_input("Zadej své jméno, badateli:")
        st.number_input("Rok tvého narození (do kroniky):", min_value=1300, max_value=2026, value=2010)
        if st.session_state.jmeno and st.button("Vstoupit do ticha kostela"):
            st.session_state.step = 1
            st.session_state.substep = 0
            st.rerun()

# --- ÚROVEŇ 1: SAKRÁLNÍ PROSTOR ---
elif st.session_state.step == 1:
    if st.session_state.substep == 0:
        if os.path.exists("a.jpg"): st.image("a.jpg", use_container_width=True)
        if st.button("Vstoupit do lodi kostela"):
            st.session_state.substep = 1
            st.rerun()
    else:
        st.subheader("ÚROVEŇ 1: SAKRÁLNÍ PROSTOR")
        st.write(f"Vítej, {st.session_state.jmeno}. Ztiš se a vnímej prostor.")
        if st.button("Zhluboka se nadechnout (+10 XP)"):
            st.session_state.xp += 10
            st.session_state.step = 2
            st.session_state.substep = 0
            st.rerun()

# --- ÚROVEŇ 2: ARCHITEKTURA ---
elif st.session_state.step == 2:
    
    # 1. FÁZE: Pozorování
    if st.session_state.substep == 0:
        st.subheader("🏛️ Síla kamene")
        if os.path.exists("b.jpg"): st.image("b.jpg", use_container_width=True)
        st.info("Mistr stavitel: „Zvedni hlavu. Co drží tuto stavbu nad tebou?“")
        if st.button("Pozorovat a vnímat prostor (+10 XP)"):
            st.session_state.xp += 10
            st.session_state.substep = 1
            st.rerun()
            
    # 2. FÁZE: Hledání prvků
    elif st.session_state.substep == 1:
        st.subheader("🔍 Hledání důkazů (společně s lektorem)")
        if os.path.exists("b_sipky.jpg"): st.image("b_sipky.jpg", use_container_width=True)
        targets = {"1": "Žebrová klenba", "2": "Svorník", "3": "Lomený oblouk", "4": "Vitráž"}
        
        cols = st.columns(4)
        for i, (num, name) in enumerate(targets.items()):
            if num in st.session_state.l2_found:
                cols[i].success(f"✅ {name}")
            else:
                if cols[i].button(f"Najít {num}"):
                    st.session_state.l2_found.append(num)
                    st.session_state.xp += 5
                    st.rerun()
        
        if len(st.session_state.l2_found) >= 4:
            if st.button("Vysvětlit podstatu stavby"):
                st.session_state.substep = 2
                st.rerun()

    # 3. FÁZE: Mistrova zkouška (Zde se odemyká křesadlo)
    elif st.session_state.substep == 2:
        st.subheader("📜 Mistrova zkouška")
        q1 = st.text_input("Jaký sloh definuje tyto lomené tvary?").lower().strip()
        q2 = st.text_input("Kamenná žebra se sbíhají v...").lower().strip()
        q3 = st.text_input("Jak se říká oknu s barevným sklem?").lower().strip()

        if st.button("Odevzdat odpovědi"):
            if q1 in ["gotika", "gotický"] and q2 in ["svorník", "svorníku"] and q3 in ["vitráž", "vitrážové okno"]:
                st.success("Mistr: „Výborně! Získáváš poznání o architektuře.“")
                st.session_state.kresadlo_unlocked = True
                st.session_state.xp += 20
                st.session_state.substep = 3 
                st.rerun()
            else:
                st.error("Mistr: „Tvé znalosti jsou vratké. Přemýšlej znovu.“")

    # 4. FÁZE: PŮDORYS (Rozcestník - oprava prázdné obrazovky)
    elif st.session_state.substep == 3:
        st.subheader("🧭 Postupuj hlouběji do chrámu")
        st.write("Mistr: „Kde právě teď stojíš?")

        # Layout podle tvého schématu
        c1, c2, c3 = st.columns([1, 2, 1])
        with c2:
            if st.button("⚜️ Oltář"):
                st.warning("Mistr: „Nespěchej, nejdříve musíš určit svou polohu v kněžišti.“")

        c1, c2, c3 = st.columns([1, 2, 1])
        with c2:
            if st.button("⛪ Kněžiště", type="primary"):
                st.session_state.substep = 4
                st.rerun()

        c1, c2, c3 = st.columns([1, 2, 1])
        with c2:
            if st.button("👣 Hlavní loď"):
                st.info("Zde jsi jen jedním z mnoha. Běž dál.")

        col_l, col_r = st.columns(2)
        with col_l:
            if st.button("🕯️ Boční loď (vlevo)"): st.toast("Jen prach...")
        with col_r:
            if st.button("🕯️ Boční loď (vpravo)"): st.toast("Tudy ne.")

    # 5. FÁZE: Rituál Olovnice
    elif st.session_state.substep == 4:
        st.subheader("📐 Rituál Olovnice v Kněžišti")
        st.success("Správně! Přistoupil jsi ke stupňům kněžiště.")
        st.session_state.olovnice_unlocked = True

        st.write("Mistr: „Na jakou světovou stranu se díváš?“")
        comp = st.columns(4)
        if comp[0].button("SEVER"): st.error("To není správně")
        if comp[1].button("VÝCHOD", type="primary"):
            st.session_state.smer_urcen = True
            st.rerun()
        if comp[2].button("JIH"): st.error("Zkus to znovu")
        if comp[3].button("ZÁPAD"): st.error("Zkus opačnou světovou stranu.")

        if st.session_state.get('smer_urcen', False):
            st.success("Správně. Východ je směr světla.")
            if st.button("Pokročit k oltáři (+15 XP)"):
                st.session_state.xp += 15
                st.session_state.step = 3
                st.session_state.substep = 0
                st.session_state.smer_urcen = False
                st.rerun()
    

# --- ÚROVEŇ 3: STUDIUM DÍLA ---
elif st.session_state.step == 3:
    if st.session_state.substep == 0:
        col_main, col_side = st.columns([3, 1])
        with col_main:
            if os.path.exists("c.jpg"): st.image("c.jpg", use_container_width=True)
            if st.button("Prozkoumat oltářní desku"):
                st.session_state.substep = 1
                st.rerun()
        with col_side:
            if os.path.exists("predikonograficky_popis.png"):
                st.image("predikonograficky_popis.png", use_container_width=True)
    elif st.session_state.substep == 1:
        col_main, col_side = st.columns([3, 1])
        with col_main:
            if os.path.exists("image_c6a996.jpg"): st.image("image_c6a996.jpg", use_container_width=True)
            if st.button("Studovat detaily"):
                st.session_state.substep = 2
                st.rerun()

    else:
        col_main, col_side = st.columns([3, 1])
        with col_main:
            st.subheader("ÚROVEŇ 3: STUDIUM DÍLA")
            vjem = st.text_input("Zapiš detail, který tě zaujal:", key="ans3")
            if vjem and st.button("Uložit do deníku (+20 XP)"):
                st.session_state.denik.append(vjem)
                st.session_state.xp += 20
                st.session_state.lupa_unlocked = True
                st.session_state.step = 4
                st.session_state.substep = 0
                st.rerun()


# --- ÚROVEŇ 4: PÍSMO ---
elif st.session_state.step == 4:
    if st.session_state.substep == 0:
        col_main, col_side = st.columns([3, 1])
        with col_main:
            if os.path.exists("d.jpg"): st.image("d.jpg", use_container_width=True)
            if st.button("Prozkoumat listiny"):
                st.session_state.substep = 1
                st.rerun()
        with col_side:
            if os.path.exists("ikonograficky_popis.png"):
                st.image("ikonograficky_popis.png", use_container_width=True)
    elif st.session_state.substep == 1:
        if os.path.exists("image.png"): st.image("image.png", use_container_width=True)
        if st.button("Rozluštit kód textu"):
            st.session_state.substep = 2
            st.rerun()
    else:
        st.subheader("ÚROVEŇ 4: ZNALOST PÍSMA")
        kod = st.text_input("Zadej kód:", key="ans4").upper().strip()
        if kod == "L 1, 26":
            st.success("Získal jsi 🗝️ Zlatý klíč.")
            st.session_state.klic_unlocked = True
            if st.button("Vstoupit do chodby (+60 XP)"):
                st.session_state.xp += 60
                st.session_state.step = 4.5
                st.session_state.substep = 0
                st.rerun()
   # --- TAJNÁ MÍSTNOST (Vložit za Úroveň 4) ---
elif st.session_state.step == 4.5:
    st.subheader("Skrytá chodba za oltářem")
    
    # ZOBRAZENÍ OBRÁZKU TAJNÉ MÍSTNOSTI
    if os.path.exists("tajna_mistnost.jpg"): 
        st.image("tajna_mistnost.jpg", use_container_width=True, caption="Vstoupil jsi do zapomenutého archivu.")
    
    st.write("Klíč v tvé dlani začal hřát. Odsunul jsi těžký svícen a uviděl úzké schodiště.")
    st.info("Vidíš starý svitek s dalšími instrukcemi, které si přečti ve svých badatelských listech.")
    
    # --- TADY JE TA OPRAVA: Definujeme sloupce ---
    col1, col2 = st.columns(2) 
    
    with col1:
        if st.button("Prozkoumat okolí"):
            st.toast("Všude je prach a pavučiny...")

    with col2:
        if st.button("Pokračovat rovnou do dílen"):
            st.session_state.step = 5
            st.session_state.substep = 0
            st.rerun()

# --- ÚROVEŇ 5: DÍLNY ---
elif st.session_state.step == 5:
    if st.session_state.substep == 0:
        col_main, col_side = st.columns([3, 1])
        with col_main:
            if os.path.exists("e.jpg"): st.image("e.jpg", use_container_width=True)
            if st.button("Vybrat si mistrovskou specializaci"):
                st.session_state.substep = 1
                st.rerun()
        with col_side:
            if os.path.exists("ikonograficka_interpretace.png"):
                st.image("ikonograficka_interpretace.png", use_container_width=True)
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
                    st.image("A.png", use_container_width=True)
                elif st.session_state.skupina == "B" and os.path.exists("B.png"):
                    st.image("B.png", use_container_width=True)
                elif st.session_state.skupina == "C" and os.path.exists("C.png"):
                    st.image("C.png", use_container_width=True)
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
                    if st.session_state.paska == spravne and st.button("Odevzdat hotové dílo (+50 XP)"):
                        st.session_state.xp += 50
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
                    if st.button("Zahrada je vysázena (+50 XP)"):
                        st.session_state.xp += 50
                        st.session_state.step = 6
                        st.session_state.substep = 0
                        st.rerun()
    
                elif st.session_state.skupina == "C":
                    odev = st.text_area("Proč je andělův oděv tak zdobný?")
                    if odev and st.button("Odeslat mistrovi (+50 XP)"):
                        st.session_state.xp += 50
                        st.session_state.step = 6
                        st.session_state.substep = 0
                        st.rerun()

# --- ÚROVEŇ 6: REALIZACE ---
elif st.session_state.step == 6:
    st.session_state.stetec_unlocked = True
    if st.session_state.substep == 0:
        if os.path.exists("f.jpg"): st.image("f.jpg", use_container_width=True)
        if st.button("Vstoupit k malbě"):
            st.session_state.substep = 1
            st.rerun()
    else:
        st.subheader("ÚROVEŇ 6: REALIZACE")
        up = st.file_uploader("Nahraj fotografii:", type=["jpg", "png"])
        if up:
            st.session_state.vlastni_kresba = up
            st.image(up, use_container_width=True)
            if st.button("DOKONČIT CELOU CESTU"):
                st.session_state.xp += 100
                st.session_state.step = 7
                st.rerun()

# --- ÚROVEŇ 7: ZÁVĚR ---
elif st.session_state.step == 7:
    if os.path.exists("h.jpg"): st.image("h.jpg", use_container_width=True)
    st.header("Gratulujeme, mistře badateli!")
    st.write(f"Získal jsi celkem {st.session_state.xp} XP.")
    st.divider()
    col_a, col_b = st.columns(2)
    with col_a:
        st.caption("Předloha")
        if os.path.exists("image_c6a996.jpg"): st.image("image_c6a996.jpg", use_container_width=True)
    with col_b:
        st.caption("Tvé dílo")
        if 'vlastni_kresba' in st.session_state: st.image(st.session_state.vlastni_kresba, use_container_width=True)

# --- GLOBÁLNÍ NAVIGACE HRÁČE ---
if st.session_state.step > 0:
    st.divider()
    
    # Seznam všech úrovní v aplikaci v postupném pořadí
    levels = [0, 1, 2, 3, 4, 4.5, 5, 6, 7]
    
    # Zjištění, na jaké pozici v seznamu se aktuální hráč nachází
    current_index = levels.index(st.session_state.step) if st.session_state.step in levels else 0

    col_nav_prev, col_nav_space, col_nav_next = st.columns([1, 2, 1])
    
    with col_nav_prev:
        if current_index > 0:
            if st.button("⬅️ Předchozí úroveň"):
                st.session_state.step = levels[current_index - 1]
                st.session_state.substep = 0
                st.rerun()
                
    with col_nav_next:
        if current_index < len(levels) - 1:
            if st.button("Další úroveň ➡️"):
                st.session_state.step = levels[current_index + 1]
                st.session_state.substep = 0
                st.rerun()
