#!/usr/bin/env python3
"""
Draw the 10 placeholder hotel images the dashboard's "View asset" links open.

They are simple flat illustrations written as SVG, so they are original,
license-free and reproducible. Each asset is mapped to one scene by the room
type in its filename (see SCENE_FOR in dashboard/build_dashboard.py).

    python scripts/make_sample_images.py          # writes SVG + PNG

Writes docs/assets/sample-images/<scene>.svg and, when Playwright with
Chromium is installed, a 1200x800 <scene>.png next to each one.
"""
from __future__ import annotations
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "docs" / "assets" / "sample-images"
W, H = 1200, 800


def tag(label: str) -> str:
    return (f'<g font-family="Helvetica,Arial,sans-serif">'
            f'<rect x="32" y="{H-78}" width="{140 + len(label) * 11}" height="46" rx="8" fill="#0F1B24" fill-opacity=".72"/>'
            f'<text x="52" y="{H-48}" font-size="20" font-weight="700" fill="#fff" letter-spacing="1.5">SAMPLE</text>'
            f'<text x="148" y="{H-48}" font-size="20" fill="#DCE6EE">{label}</text></g>')


def svg(body: str, label: str) -> str:
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">'
            f'{body}{tag(label)}</svg>')


def grad(id_, top, bot):
    return (f'<defs><linearGradient id="{id_}" x1="0" y1="0" x2="0" y2="1">'
            f'<stop offset="0" stop-color="{top}"/><stop offset="1" stop-color="{bot}"/></linearGradient></defs>')


SCENES: dict[str, tuple[str, str]] = {}

# 1 lobby -------------------------------------------------------------------
SCENES["lobby"] = ("Lobby", grad("g", "#EDE3D3", "#D8C7AE") + """
<rect width="1200" height="800" fill="url(#g)"/>
<rect y="560" width="1200" height="240" fill="#B99B77"/>
<g fill="#C9B394">""" + "".join(f'<rect x="{x}" y="0" width="70" height="560"/>' for x in (120, 1010)) + """</g>
<rect x="330" y="120" width="540" height="330" rx="165" fill="#F6EFE4" stroke="#C7AE8A" stroke-width="10"/>
<g stroke="#D9C6A8" stroke-width="4">""" + "".join(f'<line x1="{600+int(250*c)}" y1="{285-int(150*s)}" x2="600" y2="450"/>' for c, s in ((-.95,.3),(-.6,.8),(0,1),(.6,.8),(.95,.3))) + """</g>
<circle cx="600" cy="110" r="10" fill="#8A6B45"/><line x1="600" y1="0" x2="600" y2="100" stroke="#8A6B45" stroke-width="4"/>
<ellipse cx="600" cy="130" rx="70" ry="22" fill="#E8B84A"/>
<rect x="420" y="470" width="360" height="110" rx="10" fill="#6E5236"/>
<rect x="410" y="455" width="380" height="24" rx="6" fill="#8C6B48"/>
<rect x="250" y="520" width="60" height="90" rx="6" fill="#4E7A5A"/><circle cx="280" cy="480" r="55" fill="#5E9469"/>
<rect x="890" y="520" width="60" height="90" rx="6" fill="#4E7A5A"/><circle cx="920" cy="480" r="55" fill="#5E9469"/>
<g fill="#A08664" fill-opacity=".45">""" + "".join(f'<rect x="{x}" y="560" width="2" height="240"/>' for x in range(0, 1200, 120)) + "</g>")

# 2 guestroom ---------------------------------------------------------------
SCENES["guestroom"] = ("Guestroom", """
<rect width="1200" height="800" fill="#E9EEF2"/>
<rect x="760" y="90" width="340" height="380" fill="#BFD9EA"/><rect x="760" y="90" width="340" height="380" fill="none" stroke="#fff" stroke-width="14"/>
<line x1="930" y1="90" x2="930" y2="470" stroke="#fff" stroke-width="10"/>
<path d="M760 90h60v380h-60z" fill="#C3A98A"/><path d="M1040 90h60v380h-60z" fill="#C3A98A"/>
<rect y="600" width="1200" height="200" fill="#9C8570"/>
<rect x="150" y="250" width="520" height="190" rx="14" fill="#5B6E7E"/>
<rect x="120" y="430" width="580" height="190" rx="18" fill="#F7F7F4"/>
<rect x="120" y="500" width="580" height="120" rx="10" fill="#D7E1E8"/>
<rect x="175" y="385" width="200" height="80" rx="30" fill="#FFFFFF"/><rect x="440" y="385" width="200" height="80" rx="30" fill="#FFFFFF"/>
<rect x="120" y="610" width="580" height="30" fill="#6B5846"/>
<rect x="30" y="470" width="80" height="120" rx="6" fill="#8A7159"/><rect x="45" y="400" width="10" height="70" fill="#444"/>
<path d="M20 400h60l-12-60H32z" fill="#F2D79B"/>
<rect x="710" y="470" width="80" height="120" rx="6" fill="#8A7159"/>""")

# 3 suite -------------------------------------------------------------------
SCENES["suite"] = ("Suite living room", """
<rect width="1200" height="800" fill="#F1ECE6"/>
<rect x="80" y="80" width="1040" height="360" fill="#9FC4D8"/>
<path d="M80 330 L260 250 L420 300 L610 210 L800 290 L960 230 L1120 280 V440 H80Z" fill="#7A9BAE"/>
<g stroke="#fff" stroke-width="12">""" + "".join(f'<line x1="{x}" y1="80" x2="{x}" y2="440"/>' for x in (340, 600, 860)) + """</g>
<rect x="80" y="80" width="1040" height="360" fill="none" stroke="#fff" stroke-width="16"/>
<rect y="580" width="1200" height="220" fill="#B7A48E"/>
<rect x="210" y="450" width="560" height="150" rx="24" fill="#3F5566"/>
<rect x="190" y="520" width="600" height="100" rx="20" fill="#4E6A7E"/>
<rect x="250" y="470" width="120" height="70" rx="16" fill="#E0B96A"/><rect x="600" y="470" width="120" height="70" rx="16" fill="#E0B96A"/>
<rect x="820" y="610" width="240" height="24" rx="12" fill="#6F5A45"/><rect x="900" y="634" width="12" height="60" fill="#6F5A45"/><rect x="968" y="634" width="12" height="60" fill="#6F5A45"/>
<rect x="890" y="570" width="30" height="40" rx="4" fill="#F4F1EA"/><circle cx="905" cy="555" r="22" fill="#D56C5C"/>
<rect x="380" y="660" width="440" height="30" rx="15" fill="#8C735A"/>""")

# 4 pool --------------------------------------------------------------------
SCENES["pool"] = ("Pool", grad("g", "#8FD0F0", "#DDF2FB") + """
<rect width="1200" height="800" fill="url(#g)"/>
<circle cx="980" cy="140" r="60" fill="#FFE08A"/>
<rect y="360" width="1200" height="440" fill="#EFE5D2"/>
<path d="M140 440 H1060 L1140 720 H60Z" fill="#2EA6C9"/>
<path d="M170 460 H1030 L1100 700 H100Z" fill="#48C1E0"/>
<g stroke="#A7E7F5" stroke-width="6" fill="none" stroke-linecap="round">""" + "".join(f'<path d="M{x} {y} q30 -16 60 0 t60 0"/>' for x, y in ((250,540),(560,600),(820,520),(420,660),(760,650))) + """</g>
<g fill="#F7F7F2">""" + "".join(f'<rect x="{x}" y="380" width="150" height="30" rx="8"/><rect x="{x+110}" y="350" width="40" height="40" rx="6"/>' for x in (120, 380, 640, 900)) + """</g>
<g>""" + "".join(f'<line x1="{x}" y1="380" x2="{x}" y2="220" stroke="#8C6B48" stroke-width="6"/><path d="M{x-90} 240 Q{x} 170 {x+90} 240Z" fill="#E86F5A"/>' for x in (260, 780)) + """</g>
<path d="M40 360 C60 250 70 180 60 90" stroke="#7B5A3A" stroke-width="16" fill="none"/>
<g fill="#4F9A5E"><path d="M60 90 q-80 -10 -120 50 q70 -20 120 -50z"/><path d="M60 90 q80 -20 130 30 q-70 -10 -130 -30z"/><path d="M60 90 q-20 -70 30 -110 q-10 60 -30 110z"/></g>""")

# 5 exterior dusk -----------------------------------------------------------
SCENES["exterior"] = ("Exterior at dusk", grad("g", "#2B2F5C", "#E58B6B") + """
<rect width="1200" height="800" fill="url(#g)"/>
<g fill="#FFFFFF" fill-opacity=".7">""" + "".join(f'<circle cx="{x}" cy="{y}" r="2.5"/>' for x, y in ((100,60),(260,120),(420,50),(700,90),(880,40),(1050,110),(1150,60),(560,140))) + """</g>
<rect x="330" y="150" width="540" height="560" fill="#1F2438"/>
<g fill="#F7C873">""" + "".join(f'<rect x="{360+c*72}" y="{190+r*62}" width="46" height="36" rx="3" fill-opacity="{0.35 if (r*7+c*3)%5==0 else 0.95}"/>' for r in range(7) for c in range(7)) + """</g>
<rect x="520" y="620" width="160" height="90" fill="#F7C873"/><rect x="470" y="600" width="260" height="22" fill="#11151F"/>
<rect x="130" y="380" width="200" height="330" fill="#2A3150"/><rect x="870" y="330" width="220" height="380" fill="#2A3150"/>
<g fill="#F7C873" fill-opacity=".8">""" + "".join(f'<rect x="{x}" y="{y}" width="30" height="24"/>' for x in (160,220,280) for y in (420,480,540,600)) + "".join(f'<rect x="{x}" y="{y}" width="30" height="24"/>' for x in (900,960,1020) for y in (370,430,490,550,610)) + """</g>
<rect y="700" width="1200" height="100" fill="#141826"/>
<g fill="#FFE3A3">""" + "".join(f'<circle cx="{x}" cy="690" r="7"/>' for x in range(60, 1200, 140)) + "</g>")

# 6 restaurant --------------------------------------------------------------
SCENES["restaurant"] = ("Restaurant", """
<rect width="1200" height="800" fill="#3B2A24"/>
<rect y="520" width="1200" height="280" fill="#5A3E32"/>
<g fill="#6A4A3C">""" + "".join(f'<rect x="{x}" y="60" width="160" height="300" rx="80"/>' for x in (80, 380, 680, 980)) + """</g>
<g fill="#E9B872" fill-opacity=".25">""" + "".join(f'<rect x="{x+20}" y="80" width="120" height="260" rx="60"/>' for x in (80, 380, 680, 980)) + """</g>
""" + "".join(f'<line x1="{x}" y1="0" x2="{x}" y2="170" stroke="#1E1512" stroke-width="3"/><path d="M{x-40} 210 L{x-20} 170 H{x+20} L{x+40} 210Z" fill="#F2C572"/><ellipse cx="{x}" cy="230" rx="80" ry="22" fill="#F2C572" fill-opacity=".25"/>' for x in (300, 600, 900)) + """
""" + "".join(f'<ellipse cx="{x}" cy="560" rx="150" ry="32" fill="#F4EEE4"/><rect x="{x-8}" y="580" width="16" height="140" fill="#2A1D19"/><rect x="{x-60}" y="714" width="120" height="12" rx="6" fill="#2A1D19"/><circle cx="{x-60}" cy="552" r="20" fill="#fff"/><circle cx="{x+60}" cy="552" r="20" fill="#fff"/><rect x="{x-4}" y="505" width="8" height="40" fill="#C9A96E"/><circle cx="{x}" cy="500" r="8" fill="#FFD27F"/>' for x in (250, 600, 950)) + """
""" + "".join(f'<rect x="{x}" y="500" width="70" height="160" rx="12" fill="#8E3B3B"/>' for x in (60, 1070)))

# 7 spa ---------------------------------------------------------------------
SCENES["spa"] = ("Spa", """
<rect width="1200" height="800" fill="#E6EFEA"/>
<rect y="540" width="1200" height="260" fill="#CBDCD2"/>
<g fill="#D8E5DE">""" + "".join(f'<rect x="{x}" y="0" width="14" height="540"/>' for x in range(40, 1200, 60)) + """</g>
<rect x="260" y="400" width="680" height="70" rx="30" fill="#FFFFFF"/>
<rect x="300" y="470" width="20" height="150" fill="#9E8466"/><rect x="880" y="470" width="20" height="150" fill="#9E8466"/>
<rect x="300" y="380" width="200" height="40" rx="20" fill="#F2F0EA"/>
<g fill="#8BA99A">""" + "".join(f'<ellipse cx="{x}" cy="{y}" rx="{rx}" ry="{ry}"/>' for x, y, rx, ry in ((1010,610,70,34),(1000,560,56,28),(1015,515,42,22),(1005,478,30,16))) + """</g>
<g fill="#F4E8C8">""" + "".join(f'<rect x="{x}" y="620" width="40" height="70" rx="6"/><ellipse cx="{x+20}" cy="610" rx="8" ry="14" fill="#FFB84D"/>' for x in (130, 190)) + """</g>
<path d="M600 250 q-60 -80 0 -160 q60 80 0 160z" fill="#9CC3AE"/>
<path d="M600 250 q-110 -40 -130 -130 q90 20 130 130z" fill="#B5D5C3"/>
<path d="M600 250 q110 -40 130 -130 q-90 20 -130 130z" fill="#B5D5C3"/>
<rect x="520" y="670" width="160" height="16" rx="8" fill="#FFFFFF"/><rect x="540" y="650" width="120" height="20" rx="8" fill="#FFFFFF"/>""")

# 8 rooftop -----------------------------------------------------------------
SCENES["rooftop"] = ("Rooftop terrace", grad("g", "#F6B26B", "#F9E2B6") + """
<rect width="1200" height="800" fill="url(#g)"/>
<circle cx="600" cy="400" r="120" fill="#FFD98A"/>
<g fill="#8F7389">""" + "".join(f'<rect x="{x}" y="{y}" width="{w}" height="{500-y}"/>' for x, y, w in ((0,280,90),(100,210,70),(180,300,120),(310,240,80),(400,330,90),(700,260,90),(800,180,70),(880,300,110),(1000,230,80),(1090,310,110))) + """</g>
<rect y="500" width="1200" height="300" fill="#5E4A3F"/>
<rect y="480" width="1200" height="24" fill="#3E302A"/>
<g stroke="#3E302A" stroke-width="6">""" + "".join(f'<line x1="{x}" y1="420" x2="{x}" y2="480"/>' for x in range(20, 1200, 60)) + """</g>
<line x1="0" y1="420" x2="1200" y2="420" stroke="#3E302A" stroke-width="8"/>
<path d="M0 80 Q300 160 600 90 T1200 110" stroke="#3E302A" stroke-width="3" fill="none"/>
<g fill="#FFF1C2">""" + "".join(f'<circle cx="{x}" cy="{100 + int(30*abs(((x%600)-300)/300))}" r="9"/>' for x in range(40, 1200, 80)) + """</g>
""" + "".join(f'<ellipse cx="{x}" cy="600" rx="90" ry="20" fill="#F2E6D6"/><rect x="{x-6}" y="610" width="12" height="100" fill="#2A211C"/><rect x="{x-110}" y="560" width="50" height="120" rx="10" fill="#C96B4B"/><rect x="{x+60}" y="560" width="50" height="120" rx="10" fill="#C96B4B"/><rect x="{x-20}" y="560" width="14" height="36" rx="4" fill="#F9E2B6"/><rect x="{x+10}" y="566" width="14" height="30" rx="4" fill="#F9E2B6"/>' for x in (330, 870)))

# 9 beach -------------------------------------------------------------------
SCENES["beach"] = ("Beach", grad("g", "#7CC6EA", "#CDEBF7") + """
<rect width="1200" height="800" fill="url(#g)"/>
<circle cx="220" cy="150" r="70" fill="#FFE59A"/>
<rect y="360" width="1200" height="160" fill="#2B94C4"/>
<rect y="360" width="1200" height="40" fill="#1F7FAE"/>
<path d="M0 500 Q300 470 600 500 T1200 495 V800 H0Z" fill="#F2DEB0"/>
<path d="M0 505 Q300 480 600 508 T1200 500" stroke="#FFFFFF" stroke-width="10" fill="none" stroke-opacity=".8"/>
""" + "".join(f'<line x1="{x}" y1="700" x2="{x+20}" y2="470" stroke="#6B5236" stroke-width="7"/><path d="M{x-120} 500 Q{x+20} 390 {x+160} 500Z" fill="{c}"/>' for x, c in ((420, "#F4F1EA"), (820, "#2E7D8C"))) + """
<g fill="#FFFFFF">""" + "".join(f'<rect x="{x}" y="660" width="170" height="30" rx="8"/><rect x="{x+130}" y="626" width="40" height="44" rx="6"/>' for x in (330, 730)) + """</g>
<path d="M1080 700 C1070 560 1060 470 1100 360" stroke="#7B5A3A" stroke-width="18" fill="none"/>
<g fill="#3F8A52"><path d="M1100 360 q-110 -10 -160 60 q90 -30 160 -60z"/><path d="M1100 360 q110 -30 170 40 q-90 -20 -170 -40z"/><path d="M1100 360 q-30 -90 30 -140 q-10 80 -30 140z"/><path d="M1100 360 q60 -80 140 -70 q-80 30 -140 70z"/></g>
<path d="M700 300 l20 -10 l20 10" stroke="#3A4B5C" stroke-width="4" fill="none"/><path d="M780 270 l16 -8 l16 8" stroke="#3A4B5C" stroke-width="4" fill="none"/>""")

# 10 ballroom / meetings ----------------------------------------------------
SCENES["ballroom"] = ("Ballroom and events", """
<rect width="1200" height="800" fill="#2E2440"/>
<rect y="540" width="1200" height="260" fill="#4A3A5E"/>
<g fill="#3B2F52">""" + "".join(f'<rect x="{x}" y="60" width="120" height="440"/>' for x in (60, 1020)) + """</g>
<path d="M60 60 q60 220 0 440" stroke="#7C4F8C" stroke-width="40" fill="none"/><path d="M1140 60 q-60 220 0 440" stroke="#7C4F8C" stroke-width="40" fill="none"/>
""" + "".join(f'<line x1="{x}" y1="0" x2="{x}" y2="90" stroke="#C9A96E" stroke-width="3"/><path d="M{x-70} 100 h140 l-30 70 h-80z" fill="#E7C98C"/><g fill="#FFF3D2">' + "".join(f'<circle cx="{x+dx}" cy="{190+abs(dx)//6}" r="6"/>' for dx in range(-60, 61, 20)) + "</g>" for x in (380, 820)) + """
<ellipse cx="600" cy="260" rx="380" ry="120" fill="#F2D38B" fill-opacity=".08"/>
""" + "".join(f'<ellipse cx="{x}" cy="{y}" rx="120" ry="30" fill="#F7F3EA"/><rect x="{x-120}" y="{y}" width="240" height="60" fill="#EDE6D8"/>' + "".join(f'<rect x="{x+dx-14}" y="{y-60}" width="28" height="60" rx="8" fill="#B78DC4"/>' for dx in (-110, -40, 40, 110)) + f'<path d="M{x-16} {y-10} q16 -70 32 0z" fill="#E86F8C"/>' for x, y in ((280, 600), (600, 640), (920, 600))) + """
<rect x="430" y="330" width="340" height="150" rx="6" fill="#1D1729"/><rect x="450" y="350" width="300" height="110" fill="#6E5A9A"/>
<text x="600" y="418" font-family="Helvetica,Arial,sans-serif" font-size="30" font-weight="700" fill="#F3ECFF" text-anchor="middle">WELCOME</text>""")


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for key, (label, body) in SCENES.items():
        (OUT / f"{key}.svg").write_text(svg(body, label))
    print(f"wrote {len(SCENES)} SVGs to {OUT}")
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("playwright not installed - PNGs skipped (the SVGs work as-is)")
        return
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": W, "height": H})
        for key in SCENES:
            pg.goto((OUT / f"{key}.svg").as_uri())
            pg.screenshot(path=str(OUT / f"{key}.png"))
        b.close()
    print(f"wrote {len(SCENES)} PNGs")


if __name__ == "__main__":
    main()
