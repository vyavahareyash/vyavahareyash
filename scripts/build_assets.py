#!/usr/bin/env python3
"""Build the profile README's SVG tiles into assets/.

Run from anywhere:  python3 scripts/build_assets.py
Needs Pillow (for the portrait). Project banners are drawn as vector art below.
Edit the data below (copy, metrics, projects) and re-run to update the README art.
"""
import base64
import io
from html import escape
from pathlib import Path
from xml.etree import ElementTree

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"

TILE, BORDER, TEXT, MUTED = "#14141A", "#26262E", "#F2F2F5", "#9A9AA6"
SHAPE, EDGE, DIM, CARD = "#1F1F27", "#3A3A46", "#5A5A66", "#1A1A21"  # banner art tones
LIME = "#CAE556"  # matches the portrait's background so the art blends into the badge
INK = "#0B0B0F"
# shortcut: system font stacks, Geist only if installed locally; embed a subset font if the look drifts.
SANS = "Geist, Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif"
MONO = "'Geist Mono', ui-monospace, SFMono-Regular, Menlo, Consolas, monospace"

PROJECTS = [
    {
        "slug": "total-recall",
        "name": "WhatsApp Total Recall",
        "tag": "PyPI",
        "desc": "MCP server that lets Claude and Cursor search your WhatsApp history. Fully local hybrid search.",
        "pill": "pip install whatsapp-total-recall",
    },
    {
        "slug": "outloud",
        "name": "OutLoud",
        "tag": "Chrome Web Store",
        "desc": "Offline neural text-to-speech for any webpage via local Ollama. First audio in under a second.",
        "pill": "Add to Chrome →",
    },
    {
        "slug": "cashflow",
        "name": "Cashflow",
        "tag": "5 platforms",
        "desc": "Offline personal finance app. Speak your spending and an on-device SLM logs it.",
        "pill": "Android · macOS · Windows · Linux · Web",
    },
    {
        "slug": "openrouter-tracker",
        "name": "OpenRouter Tracker",
        "tag": "Homebrew",
        "desc": "Native desktop widget for OpenRouter credits, spend velocity and rate limits.",
        "pill": "brew install vyavahareyash/tap/openrouter-tracker",
    },
    {
        "slug": "timezone",
        "name": "Timezone",
        "tag": "Homebrew",
        "desc": "Menu bar app for meeting times. Each city is a strip coloured like its sky.",
        "pill": "brew install vyavahareyash/tap/timezone",
    },
]

FOCUS = [("Production RAG", "for risk & compliance"), ("Agent systems", "memory & context layers"),
         ("Local-first AI", "MCP & on-device models")]

IMPACT = [
    {
        "slug": "risk-issue",
        "label": "UBS · RISK ISSUE ASSISTANT",
        "headline": "~10× faster reviews",
        "caption": "Checks remediation claims against evidence buried in nested documents.",
        "picture": "bars",
    },
    {
        "slug": "audit-rag",
        "label": "UBS · AUDIT-RESPONSE ASSISTANT",
        "headline": "Live in 4 departments",
        "caption": "Drafts evidence-linked audit answers from past responses and routes cases to experts.",
        "picture": "rollout",
    },
]

REPO = "https://github.com/vyavahareyash/vyavahareyash/blob/main"
CASE_STUDIES = [
    {
        "slug": "risk-issue-assistant",
        "label": "case study · ubs · strategic risk management",
        "title": "Risk Issue Assistant",
        "subtitle": "An AI assistant that checks remediation claims against the evidence, "
                    "so risk reviews take days instead of weeks.",
        "headline": "~10× faster reviews",
        "picture": "bars",
        "pill": "UBS Outstanding Performer · 2026",
        "glance": [("where", "UBS, Strategic Risk Management"),
                   ("my role", "AI Engineer: requirements, architecture, build, delivery"),
                   ("stack", "Python, Azure OpenAI, advanced RAG, LangChain"),
                   ("recognition", "UBS Outstanding Performer, Aug 2026")],
        "problem": "When a risk issue is raised, the team that owns it fixes it and submits a claim that it is "
                   "resolved. Before the issue can be closed, a reviewer has to confirm the claim is backed by "
                   "evidence. That evidence usually sits in nested documents: files embedded inside other files, "
                   "in mixed formats. Finding and checking it by hand took 3–4 weeks per issue.",
        "built": [("Parses nested and embedded files", "with multi-modal parsing, so evidence is found whatever format it is in."),
                  ("Validates each remediation claim", "against the evidence it finds, and shows the evidence it relied on."),
                  ("Automates the closure check", "that tells reviewers whether an issue looks ready to close.")],
        "flow": ["Risk issue + remediation claim", "Parse nested and embedded documents", "Retrieve the relevant evidence",
                 "LLM checks the claim against the evidence", "Reviewer sees a verdict with cited evidence"],
        "results": [("3–4 wk → 2–3 d", "review time per issue"), ("Outstanding Performer", "UBS recognition, Aug 2026")],
        "note": "Used by the non-technical risk reviewers it was built for.",
        "worked": [("Discovery and design:", "partnered with risk and compliance experts to map the review process, gather "
                                             "requirements and design the architecture; proposed improvements beyond scope."),
                   ("Stakeholders:", "ran live demos for senior management and for the risk users."),
                   ("Production delivery:", "shipped through code review, automated testing and CI/CD.")],
        "links": [("← Profile", "", "https://github.com/vyavahareyash"),
                  ("Award post", "↗", "https://lnkd.in/p/dvxQUTkz"),
                  ("Next case", "→", f"{REPO}/work/audit-response-assistant.md")],
    },
    {
        "slug": "audit-response-assistant",
        "label": "case study · ubs · risk and compliance",
        "title": "Audit-Response Assistant",
        "subtitle": "A RAG assistant that drafts evidence-linked answers to audit requests, "
                    "taken from proof of concept to production.",
        "headline": "Live in 4 departments",
        "picture": "rollout",
        "pill": None,
        "glance": [("where", "UBS, risk and compliance"),
                   ("my role", "AI Engineer: proof of concept to production"),
                   ("stack", "Python, Azure OpenAI, advanced RAG, LangChain")],
        "problem": "Audit requests have to be answered with evidence. Many have been answered before in some form, "
                   "but past answers and their supporting documents are spread across files, often embedded inside "
                   "other files. Each new request meant searching that history by hand and working out which "
                   "subject-matter expert should own it.",
        "built": [("Parses embedded documents,", "so supporting material inside attachments is not missed."),
                  ("Ranks similar past responses", "to find the most relevant answers already given."),
                  ("Drafts a new answer linked to its evidence,", "so reviewers can check every claim at the source."),
                  ("Routes each case", "to the right subject-matter expert.")],
        "flow": ["Audit request", "Parse embedded documents", "Rank similar past responses",
                 "Draft an answer linked to evidence", "Route to the right expert"],
        "results": [("PoC → production", "now a live production system"), ("1 → 4 departments", "teams using it today")],
        "note": None,
        "worked": [("Requirements and architecture:", "worked with risk and compliance experts on both."),
                   ("Production delivery:", "shipped through code review, automated testing and CI/CD.")],
        "links": [("← Profile", "", "https://github.com/vyavahareyash"),
                  ("Next case", "→", f"{REPO}/work/risk-issue-assistant.md")],
    },
]
CASE_NOTE = ("Details are generalised for a public page: no internal data, system names beyond the project name, "
             "or architecture specifics.")

AWARDS = [
    ("2026", "UBS Outstanding Performer", "Risk Issue Assistant"),
    ("2025", "UBS Tech Unleashed, Leader's Choice", "AI-Architect"),
    ("2025", "UBS Data Science Guild Hackathon, Winner", "AI-Architect"),
    ("2024", "NES Innovation Awards, 2nd", "drone pollution mapping"),
    ("2023", "NASA Space Apps Challenge, Winner", "deforestation detection"),
]

STACK = ["Python", "TypeScript", "Dart", "Swift", "SQL", "RAG", "MCP", "LangChain",
         "Azure OpenAI", "Ollama", "PyTorch", "Docker"]


# ---------- primitives ----------

def svg(w, h, body, label):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
            f'role="img" aria-label="{escape(label)}"><title>{escape(label)}</title>{body}</svg>')


def text(x, y, s, size, fill=TEXT, font=SANS, weight=400, anchor="start", spacing=0):
    ls = f' letter-spacing="{spacing}"' if spacing else ""
    return (f'<text x="{x}" y="{y}" font-family="{font}" font-size="{size}" font-weight="{weight}" '
            f'fill="{fill}" text-anchor="{anchor}"{ls}>{escape(s)}</text>')


def tile(x, y, w, h, fill=TILE):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="18" fill="{fill}" stroke="{BORDER}"/>'


def wrap(s, max_chars):
    lines, line = [], ""
    for word in s.split():
        if line and len(line) + 1 + len(word) > max_chars:
            lines.append(line)
            line = word
        else:
            line = f"{line} {word}".strip()
    return lines + [line]


def data_uri(path, w, h, quality=80):
    """Cover-crop to w:h, render at 2x for retina, return a JPEG data URI."""
    from PIL import Image  # lazy: build_contributions.py imports this module in CI without Pillow

    img = Image.open(path).convert("RGB")
    iw, ih = img.size
    if iw / ih > w / h:
        nw = round(ih * w / h)
        img = img.crop(((iw - nw) // 2, 0, (iw - nw) // 2 + nw, ih))
    else:
        nh = round(iw * h / w)
        img = img.crop((0, (ih - nh) // 2, iw, (ih - nh) // 2 + nh))
    img = img.resize((w * 2, h * 2), Image.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, "JPEG", quality=quality, optimize=True, progressive=True)
    return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()


def barcode(x, y, h):
    widths = [2, 1, 3, 1, 2, 1, 4, 1, 2, 1, 3, 2, 1, 4, 1, 2, 3, 1, 2, 1, 4, 1, 2, 1, 2]
    out, cx = [], x
    for i, wd in enumerate(widths):
        out.append(f'<rect x="{cx}" y="{y}" width="{wd}" height="{h}"/>')
        cx += wd + (1 if i % 3 else 2)
    return f'<g fill="{LIME}">{"".join(out)}</g>'


# ---------- tiles ----------

def header():
    # 3-column grid inside an 840-wide canvas with 6px transparent gutters
    col = 268
    hero_w, bx, by, bh = 2 * col + 12, 6 + 2 * col + 24, 6, 432
    body = [tile(6, 6, hero_w, bh)]  # hero matches the badge height; impact tiles are separate linked images
    body.append(text(38, 46, "yash vyavahare — ai engineer", 12, MUTED, MONO))
    for i, (line, color) in enumerate([("I ship AI that runs", TEXT), ("in production", TEXT),
                                       ("and on your laptop.", LIME)]):
        body.append(text(38, 136 + i * 44, line, 40, color, weight=600, spacing=-1.2))
    body.append(text(38, 264, "RAG and agent systems for risk & compliance at UBS.", 14, MUTED))
    body.append(text(38, 286, "Local-first tools on PyPI, Homebrew and the Chrome Web Store.", 14, MUTED))
    body.append(f'<rect x="38" y="334" width="{hero_w - 64}" height="1" fill="{BORDER}"/>')
    for i, (title, desc) in enumerate(FOCUS):  # "what I do" strip
        x = 38 + i * 164
        body.append(text(x, 370, title, 14, TEXT, weight=600))
        body.append(text(x, 391, desc, 12, MUTED))

    # ID badge: lanyard slot is a real hole (mask) so the page shows through in light and dark mode
    portrait = data_uri(ASSETS / "src" / "portrait.jpg", 232, 236, quality=82)
    body.append(
        f'<mask id="hole"><rect x="{bx}" y="{by}" width="{col}" height="{bh}" fill="#fff"/>'
        f'<rect x="{bx + col / 2 - 28}" y="{by + 16}" width="56" height="10" rx="5" fill="#000"/></mask>'
        f'<rect x="{bx}" y="{by}" width="{col}" height="{bh}" rx="18" fill="{LIME}" mask="url(#hole)"/>'
        f'<clipPath id="art"><rect x="{bx + 18}" y="{by + 60}" width="232" height="236" rx="12"/></clipPath>'
        f'<image href="{portrait}" x="{bx + 18}" y="{by + 60}" width="232" height="236" clip-path="url(#art)"/>'
        f'<rect x="{bx + 18}" y="{by + 372}" width="232" height="40" rx="8" fill="{INK}"/>'
    )
    body.append(text(bx + 18, by + 48, "AI ENGINEER", 11, INK, MONO, 600))
    body.append(text(bx + col - 18, by + 48, "№ 001", 11, INK, MONO, 600, "end"))
    body.append(text(bx + 18, by + 330, "Yash Vyavahare", 24, INK, weight=700, spacing=-0.5))
    body.append(text(bx + 18, by + 352, "UBS · Pune · since Aug 2024", 13, INK))
    body.append(text(bx + 30, by + 396, "prev. ISRO SAC", 10, LIME, MONO))
    body.append(barcode(bx + 140, by + 381, 22))

    return svg(840, 444, "".join(body),
               "Yash Vyavahare, AI Engineer at UBS. I ship AI that runs in production and on your laptop.")


def label(s):
    return svg(840, 44, text(10, 30, s, 12, MUTED, MONO), s)


def impact(item):
    """Half-width tile: what it is, one headline number, a tiny picture of the change, a link cue."""
    lines = wrap(item["caption"], 52)
    assert len(lines) <= 2, f"{item['slug']}: caption wraps to {len(lines)} lines"
    body = [tile(6, 6, 408, 220), text(26, 40, item["label"], 11, MUTED, MONO),
            text(26, 80, item["headline"], 28, weight=600, spacing=-0.6), item["picture"]]
    body += [text(26, 158 + i * 19, line, 13, MUTED) for i, line in enumerate(lines)]
    body.append(text(26, 206, "Read the case study ↗", 11, LIME, MONO))
    return svg(420, 232, "".join(body), f"{item['label']}: {item['headline']}. {item['caption']} Read the case study.")


def bars_picture(full=250):
    """Before/after bars, lengths proportional to the midpoints (3.5 weeks vs 2.5 days)."""
    after = round(full * 2.5 / 24.5)
    return (text(26, 110, "before", 10, MUTED, MONO)
            + f'<rect x="80" y="102" width="{full}" height="8" rx="4" fill="#33333D"/>'
            + text(80 + full + 10, 110, "3–4 weeks", 10, MUTED, MONO)
            + text(26, 130, "after", 10, MUTED, MONO)
            + f'<rect x="80" y="122" width="{after}" height="8" rx="4" fill="{LIME}"/>'
            + text(80 + after + 10, 130, "2–3 days", 10, TEXT, MONO))


def rollout_picture():
    """One pilot block, then four lit blocks: pilot to production in 4 departments."""
    blocks = (f'<rect x="26" y="100" width="22" height="22" rx="5" fill="none" stroke="{LIME}" stroke-width="1.5"/>'
              + text(60, 116, "→", 14, MUTED)
              + "".join(f'<rect x="{82 + i * 30}" y="100" width="22" height="22" rx="5" fill="{LIME}"/>' for i in range(4)))
    return blocks + text(212, 116, "pilot → production", 10, MUTED, MONO)


# ---------- project banner art (408x166, local coords; flat shapes, one lime accent) ----------

ART_CSS = f"""<style>
.flow{{stroke-dasharray:3 4;animation:flow 1.2s linear infinite}}
@keyframes flow{{to{{stroke-dashoffset:-14}}}}
.hit{{animation:hit 5s ease-in-out infinite}}
@keyframes hit{{0%,30%,100%{{stroke:#33333D}}10%,20%{{stroke:{LIME}}}}}
.wave{{animation:wave 1.8s ease-in-out infinite}}
@keyframes wave{{0%,100%{{opacity:.25}}50%{{opacity:1}}}}
.bar{{transform-box:fill-box;transform-origin:center;animation:bar 1.1s ease-in-out infinite}}
@keyframes bar{{0%,100%{{transform:scaleY(.4)}}50%{{transform:scaleY(1)}}}}
.ring{{transform-box:fill-box;transform-origin:center;animation:ring 2s ease-out infinite}}
@keyframes ring{{from{{transform:scale(1);opacity:.8}}to{{transform:scale(1.8);opacity:0}}}}
.spin{{transform-box:fill-box;transform-origin:center;animation:spin 14s linear infinite}}
@keyframes spin{{to{{transform:rotate(360deg)}}}}
.gauge{{animation:gauge 1.6s ease-out both}}
@keyframes gauge{{from{{stroke-dashoffset:213.6}}}}
.slide{{animation:slide 4s ease-in-out infinite alternate}}
@keyframes slide{{to{{transform:translateX(70px)}}}}
@media (prefers-reduced-motion:reduce){{*{{animation:none!important}}}}
</style>"""


def msg_card(x, y, hit_delay=None):
    cls = f' class="hit" style="animation-delay:{hit_delay}s"' if hit_delay is not None else ""
    return (f'<rect x="{x}" y="{y}" width="52" height="22" rx="6" fill="{CARD}" stroke="#33333D" stroke-width="1.5"{cls}/>'
            f'<rect x="{x + 8}" y="{y + 7}" width="30" height="3" rx="1.5" fill="{MUTED}"/>'
            f'<rect x="{x + 8}" y="{y + 13}" width="20" height="3" rx="1.5" fill="{DIM}"/>')


def art_total_recall():
    links = [((104, 41), (144, 60)), ((92, 107), (144, 95)), ((306, 35), (264, 58)),
             ((318, 95), (264, 92)), ((292, 139), (250, 119))]
    out = [f'<line x1="{a[0]}" y1="{a[1]}" x2="{b[0]}" y2="{b[1]}" stroke="{EDGE}" stroke-width="1.5" class="flow"/>'
           f'<circle cx="{a[0]}" cy="{a[1]}" r="2.5" fill="{DIM}"/>' for a, b in links]
    for (x, y), delay in zip([(52, 30), (40, 96), (306, 24), (318, 84), (292, 128)], [0, 1, 2, 3, 4]):
        out.append(msg_card(x, y, delay))
    out.append(  # chat bubble with tail, magnifier, padlock
        f'<path d="M162 43H246Q264 43 264 61V101Q264 119 246 119H184L162 136L166 119H162Q144 119 144 101V61Q144 43 162 43Z" '
        f'fill="{SHAPE}" stroke="{EDGE}" stroke-width="2" stroke-linejoin="round"/>'
        f'<circle cx="198" cy="78" r="17" fill="none" stroke="{LIME}" stroke-width="4"/>'
        f'<line x1="210" y1="90" x2="222" y2="102" stroke="{LIME}" stroke-width="5" stroke-linecap="round"/>'
        f'<path d="M254 44V39a6 6 0 0 1 12 0V44" fill="none" stroke="{TEXT}" stroke-width="2.5"/>'
        f'<rect x="250" y="44" width="20" height="16" rx="3" fill="{TEXT}"/>'
        f'<circle cx="260" cy="51" r="2" fill="{INK}"/>')
    return "".join(out)


def art_outloud():
    bars = [(64, 110), (76, 96), (88, 104), (100, 88), (112, 70)]  # (y, width); y=88 is the line being read
    out = [f'<rect x="70" y="34" width="150" height="100" rx="10" fill="{SHAPE}" stroke="{EDGE}" stroke-width="2"/>'
           f'<line x1="70" y1="52" x2="220" y2="52" stroke="{EDGE}" stroke-width="1.5"/>'
           + "".join(f'<circle cx="{cx}" cy="43" r="2.5" fill="{DIM}"/>' for cx in (82, 91, 100))
           + f'<rect x="80" y="84" width="122" height="13" rx="3" fill="{LIME}" opacity=".15"/>']
    for y, w in bars:
        out.append(f'<rect x="86" y="{y}" width="{w}" height="5" rx="2.5" '
                   f'fill="{LIME if y == 88 else EDGE}"/>')
    for i, d in enumerate(["M232 78Q240 90 232 102", "M242 70Q254 90 242 110", "M252 62Q268 90 252 118"]):
        out.append(f'<path d="{d}" fill="none" stroke="{LIME}" stroke-width="3" stroke-linecap="round" '
                   f'class="wave" style="animation-delay:{i * 0.25}s"/>')
    out.append(  # llama with headphones: band behind ears, cups on top
        f'<path d="M286 70A29 29 0 0 1 344 70" fill="none" stroke="{EDGE}" stroke-width="6" stroke-linecap="round"/>'
        f'<rect x="296" y="80" width="38" height="100" rx="16" fill="{TEXT}"/>'
        f'<ellipse cx="301" cy="44" rx="6" ry="14" transform="rotate(-15 301 44)" fill="{TEXT}"/>'
        f'<ellipse cx="329" cy="44" rx="6" ry="14" transform="rotate(15 329 44)" fill="{TEXT}"/>'
        f'<ellipse cx="301" cy="46" rx="2.5" ry="8" transform="rotate(-15 301 46)" fill="{MUTED}"/>'
        f'<ellipse cx="329" cy="46" rx="2.5" ry="8" transform="rotate(15 329 46)" fill="{MUTED}"/>'
        f'<ellipse cx="315" cy="72" rx="26" ry="24" fill="{TEXT}"/>'
        + "".join(f'<circle cx="{cx}" cy="{cy}" r="6" fill="{TEXT}"/>' for cx, cy in ((309, 50), (315, 47), (321, 50)))
        + f'<circle cx="306" cy="70" r="3" fill="{INK}"/><circle cx="324" cy="70" r="3" fill="{INK}"/>'
        f'<ellipse cx="315" cy="85" rx="11" ry="8" fill="#DADAE2"/>'
        f'<path d="M312 82H318L315 85Z" fill="{INK}"/>'
        f'<rect x="280" y="60" width="12" height="26" rx="5" fill="{LIME}" stroke="{INK}" stroke-width="1.5"/>'
        f'<rect x="338" y="60" width="12" height="26" rx="5" fill="{LIME}" stroke="{INK}" stroke-width="1.5"/>')
    return "".join(out)


def art_cashflow():
    out = [  # coin with orbiting dashed ring
        f'<circle cx="72" cy="104" r="30" fill="none" stroke="{EDGE}" stroke-width="1.5" stroke-dasharray="6 6" class="spin"/>'
        f'<circle cx="72" cy="104" r="22" fill="{SHAPE}" stroke="{MUTED}" stroke-width="2"/>'
        + text(72, 112, "₹", 22, TEXT, weight=600, anchor="middle")
        # phone with mic button
        + f'<rect x="110" y="22" width="70" height="130" rx="12" fill="{SHAPE}" stroke="{EDGE}" stroke-width="2"/>'
        f'<rect x="135" y="28" width="20" height="4" rx="2" fill="{EDGE}"/>'
        f'<rect x="122" y="46" width="40" height="4" rx="2" fill="{MUTED}"/>'
        f'<rect x="122" y="56" width="28" height="4" rx="2" fill="{DIM}"/>'
        f'<circle cx="145" cy="100" r="18" fill="none" stroke="{LIME}" stroke-width="2" class="ring"/>'
        f'<circle cx="145" cy="100" r="18" fill="{LIME}"/>'
        f'<rect x="140" y="89" width="10" height="15" rx="5" fill="{INK}"/>'
        f'<path d="M136 99a9 9 0 0 0 18 0" fill="none" stroke="{INK}" stroke-width="2"/>'
        f'<line x1="145" y1="108" x2="145" y2="112" stroke="{INK}" stroke-width="2"/>']
    for i, h in enumerate([8, 16, 26, 14, 30, 18, 10, 22, 12]):  # voice waveform
        out.append(f'<rect x="{192 + i * 7}" y="{90 - h / 2}" width="4" height="{h}" rx="2" fill="{LIME}" '
                   f'class="bar" style="animation-delay:{i * 0.12:.2f}s"/>')
    for y in (56, 84, 112):  # transactions it turns into
        out.append(f'<rect x="262" y="{y}" width="96" height="22" rx="6" fill="{CARD}" stroke="#33333D" stroke-width="1.5"/>'
                   f'<circle cx="274" cy="{y + 11}" r="5" fill="{EDGE}"/>'
                   f'<rect x="286" y="{y + 9}" width="40" height="4" rx="2" fill="{MUTED}"/>'
                   f'<rect x="334" y="{y + 8}" width="16" height="6" rx="3" fill="{TEXT}"/>')
    return "".join(out)


def art_openrouter_tracker():
    return (  # menu bar, then the widget: gauge left, stats right
        f'<rect x="0" y="0" width="408" height="12" fill="{CARD}"/>'
        + "".join(f'<rect x="{x}" y="4" width="{w}" height="4" rx="2" fill="{DIM}"/>'
                  for x, w in ((14, 10), (32, 22), (60, 18), (340, 14), (360, 34)))
        + f'<rect x="104" y="26" width="200" height="122" rx="22" fill="{SHAPE}" stroke="{EDGE}" stroke-width="2"/>'
        f'<circle cx="160" cy="87" r="34" fill="none" stroke="#2E2E38" stroke-width="8"/>'
        f'<circle cx="160" cy="87" r="34" fill="none" stroke="{LIME}" stroke-width="8" stroke-linecap="round" '
        f'stroke-dasharray="213.6" stroke-dashoffset="57.7" transform="rotate(-90 160 87)" class="gauge"/>'
        f'<rect x="146" y="80" width="28" height="7" rx="3.5" fill="{TEXT}"/>'
        f'<rect x="150" y="92" width="20" height="4" rx="2" fill="{MUTED}"/>'
        f'<rect x="214" y="52" width="40" height="4" rx="2" fill="{MUTED}"/>'
        f'<rect x="214" y="61" width="64" height="9" rx="4.5" fill="{TEXT}"/>'
        f'<rect x="214" y="88" width="34" height="4" rx="2" fill="{MUTED}"/>'
        f'<rect x="214" y="97" width="50" height="9" rx="4.5" fill="{LIME}"/>'
        f'<rect x="214" y="120" width="72" height="5" rx="2.5" fill="#2E2E38"/>'
        f'<rect x="214" y="120" width="26" height="5" rx="2.5" fill="{LIME}"/>'
        f'<circle cx="284" cy="44" r="8" fill="none" stroke="{MUTED}" stroke-width="2" stroke-dasharray="38 12"/>')


def art_timezone():
    """Menu bar, then the panel: three cities as day strips (night grey, lime dawn and dusk, lighter day), offset by
    their time zones, and one white bead (the same moment) sliding across all three."""
    keys = [(0, "#2A2A33"), (5, "#2A2A33"), (7, LIME), (9.5, "#6A6A78"), (16.5, "#6A6A78"), (19, LIME),
            (21, "#2A2A33"), (24, "#2A2A33")]

    def sky(hour):
        for (h0, c0), (h1, c1) in zip(keys, keys[1:]):
            if h0 <= hour <= h1:
                t = (hour - h0) / (h1 - h0)
                return "#" + "".join(f"{round(int(c0[i:i + 2], 16) * (1 - t) + int(c1[i:i + 2], 16) * t):02X}"
                                     for i in (1, 3, 5))

    x0, width, now = 120, 168, 0.42
    out = [f'<rect x="0" y="0" width="408" height="12" fill="{CARD}"/>'
           + "".join(f'<rect x="{x}" y="4" width="{w}" height="4" rx="2" fill="{DIM}"/>'
                     for x, w in ((14, 10), (32, 22), (60, 18), (348, 14), (368, 26)))
           + f'<rect x="318" y="1" width="20" height="10" rx="3" fill="{EDGE}"/>'
           f'<circle cx="328" cy="6" r="3.2" fill="none" stroke="{TEXT}" stroke-width="1.2"/>'
           f'<rect x="104" y="24" width="200" height="126" rx="18" fill="{SHAPE}" stroke="{EDGE}" stroke-width="2"/>']
    beads = []
    for i, (offset, label_w) in enumerate(((0, 40), (-4.5, 30), (7.5, 48))):
        top = 42 + i * 36
        stops = "".join(f'<stop offset="{q / 24:.3f}" stop-color="{sky((q + offset) % 24)}"/>' for q in range(25))
        out.append(f'<defs><linearGradient id="tz{i}">{stops}</linearGradient></defs>'
                   f'<rect x="{x0}" y="{top}" width="{label_w}" height="4" rx="2" fill="{MUTED}"/>'
                   f'<rect x="{x0 + width - 30}" y="{top - 2}" width="30" height="7" rx="3.5" fill="{TEXT}"/>'
                   f'<rect x="{x0}" y="{top + 10}" width="{width}" height="10" rx="5" fill="url(#tz{i})"/>')
        beads.append(f'<rect x="{x0 + width * now - 3:.1f}" y="{top + 10}" width="6" height="10" rx="3" fill="{TEXT}"/>'
                     f'<rect x="{x0 + width * now - 0.75:.1f}" y="{top + 12}" width="1.5" height="6" rx=".75" fill="{INK}"/>')
    return "".join(out) + f'<g class="slide">{"".join(beads)}</g>'


ART = {"total-recall": art_total_recall, "outloud": art_outloud,
       "cashflow": art_cashflow, "openrouter-tracker": art_openrouter_tracker, "timezone": art_timezone}


def project(p):
    lines = wrap(p["desc"], 50)
    assert len(lines) <= 2, f"{p['slug']}: description wraps to {len(lines)} lines"
    pill_w = round(len(p["pill"]) * 6.7 + 28)
    assert pill_w <= 368, f"{p['slug']}: install pill too wide ({pill_w})"

    body = (
        ART_CSS
        + f'<pattern id="dots" width="16" height="16" patternUnits="userSpaceOnUse">'
        f'<circle cx="8" cy="8" r="1" fill="{SHAPE}"/></pattern>'
        f'<clipPath id="card"><rect x="6" y="6" width="408" height="332" rx="18"/></clipPath>'
        f'<g clip-path="url(#card)"><rect x="6" y="6" width="408" height="332" fill="{TILE}"/>'
        f'<rect x="6" y="6" width="408" height="166" fill="url(#dots)"/>'
        f'<svg x="6" y="6" width="408" height="166" overflow="hidden" aria-hidden="true">{ART[p["slug"]]()}</svg>'
        f'<rect x="6" y="172" width="408" height="1" fill="{BORDER}"/></g>'
        f'<rect x="6" y="6" width="408" height="332" rx="18" fill="none" stroke="{BORDER}"/>'
        + text(26, 212, p["name"], 20, weight=600, spacing=-0.3)
        + text(394, 212, p["tag"], 11, LIME, MONO, anchor="end")
        + "".join(text(26, 238 + i * 20, line, 14, MUTED) for i, line in enumerate(lines))
        + f'<rect x="26" y="278" width="{pill_w}" height="34" rx="17" fill="{INK}" stroke="{BORDER}"/>'
        + text(40, 299, p["pill"], 11, TEXT, MONO)
    )
    return svg(420, 344, body, f"{p['name']} ({p['tag']}): {p['desc']} {p['pill']}")


def recognition_and_stack():
    body = [tile(6, 6, 548, 230), text(30, 44, "recognition", 12, MUTED, MONO)]
    for i, (year, award, why) in enumerate(AWARDS):
        y = 82 + i * 32
        body.append(text(30, y, year, 13, LIME, MONO))
        body.append(f'<text x="84" y="{y}" font-family="{SANS}" font-size="14" fill="{TEXT}">'
                    f'{escape(award)}<tspan fill="{MUTED}"> · {escape(why)}</tspan></text>')

    x0, x_max = 566 + 24, 566 + 268 - 24
    body += [tile(566, 6, 268, 230), text(x0, 44, "stack", 12, MUTED, MONO)]
    x, y = x0, 62
    for chip in STACK:
        w = round(len(chip) * 6.7 + 20)
        if x + w > x_max:
            x, y = x0, y + 32
        body.append(f'<rect x="{x}" y="{y}" width="{w}" height="24" rx="12" fill="none" stroke="#33333D"/>')
        body.append(text(x + 10, y + 16, chip, 11, TEXT, MONO))
        x += w + 6
    assert y + 24 <= 6 + 230 - 12, "stack chips overflow the tile"

    alt = "Recognition: " + "; ".join(f"{y} {a} ({w})" for y, a, w in AWARDS) + ". Stack: " + ", ".join(STACK) + "."
    return svg(840, 242, "".join(body), alt)


def contact(name, arrow="↗", w=420):
    body = tile(6, 6, w - 12, 68) + text(30, 47, name, 18, weight=500) + text(w - 30, 47, arrow, 18, LIME, anchor="end")
    return svg(w, 80, body, name)


# ---------- case-study pages (full-width tiles, 780px of text width inside an 828 card) ----------

def bold_lead_line(x, y, line, lead, size=14):
    """A text line whose leading phrase is bold white and the rest muted."""
    rest = line[len(lead):] if line.startswith(lead) else line
    head = f'<tspan font-weight="600" fill="{TEXT}">{escape(lead)}</tspan>' if line.startswith(lead) else ""
    return f'<text x="{x}" y="{y}" font-family="{SANS}" font-size="{size}" fill="{MUTED}">{head}{escape(rest)}</text>'


def card(h, body, label_text):
    return svg(840, h + 12, tile(6, 6, 828, h) + text(30, 44, label_text, 12, MUTED, MONO) + body, label_text)


def cs_hero(cs, picture):
    lines = wrap(cs["subtitle"], 92)
    assert len(lines) <= 2, f"{cs['slug']}: subtitle wraps to {len(lines)} lines"
    body = [tile(6, 6, 828, 300), text(30, 44, cs["label"], 12, MUTED, MONO),
            text(30, 100, cs["title"], 40, weight=600, spacing=-1.2)]
    body += [text(30, 136 + i * 22, line, 15, MUTED) for i, line in enumerate(lines)]
    body.append(f'<rect x="30" y="192" width="780" height="1" fill="{BORDER}"/>')
    body.append(text(30, 236, cs["headline"], 28, weight=600, spacing=-0.6))
    body.append(f'<g transform="translate(4 152)">{picture}</g>')
    if cs["pill"]:
        w = round(len(cs["pill"]) * 6.7 + 28)
        body.append(f'<rect x="{810 - w}" y="212" width="{w}" height="30" rx="15" fill="none" stroke="{LIME}"/>'
                    + text(810 - w + 14, 231, cs["pill"], 11, LIME, MONO))
    return svg(840, 312, "".join(body), f"{cs['title']}: {cs['subtitle']} {cs['headline']}.")


def cs_glance(items):
    colw = 780 / len(items)
    body, deepest = [], 1
    for i, (key, value) in enumerate(items):
        x = 30 + i * colw
        lines = wrap(value, int(colw / 6.8) - 1)
        deepest = max(deepest, len(lines))
        body.append(text(x, 44, key, 11, MUTED, MONO))
        body += [text(x, 70 + j * 20, line, 13, TEXT) for j, line in enumerate(lines)]
    h = 70 + (deepest - 1) * 20 + 22
    alt = "At a glance: " + "; ".join(f"{k}: {v}" for k, v in items) + "."
    return svg(840, h + 12, tile(6, 6, 828, h) + "".join(body), alt)


def cs_text(label_text, paragraph=None, bullets=None):
    body, y = [], 74
    if paragraph:
        for line in wrap(paragraph, 100):
            body.append(text(30, y, line, 14, TEXT))
            y += 22
    for lead, rest in bullets or []:
        body.append(f'<rect x="30" y="{y - 9}" width="6" height="6" rx="1.5" fill="{LIME}"/>')
        for j, line in enumerate(wrap(f"{lead} {rest}", 94)):
            body.append(bold_lead_line(46, y, line, lead) if j == 0 else text(46, y, line, 14, MUTED))
            y += 22
        y += 8
    h = y - 22 + 26 - (8 if bullets else 0)
    words = paragraph or " ".join(f"{lead} {rest}" for lead, rest in bullets)
    return svg(840, h + 12, tile(6, 6, 828, h) + text(30, 44, label_text, 12, MUTED, MONO) + "".join(body),
               f"{label_text.capitalize().replace(' i ', ' I ')}: {words}")


def cs_flow(steps):
    n, gap, top, bh = len(steps), 30, 66, 78
    bw = (780 - (n - 1) * gap) / n
    body = [ART_CSS]
    for i, step in enumerate(steps):
        x, last = 30 + i * (bw + gap), i == n - 1
        lines = wrap(step, int(bw / 6.6))
        assert len(lines) <= 3, f"flow step too long: {step}"
        body.append(f'<rect x="{x}" y="{top}" width="{bw}" height="{bh}" rx="12" fill="{CARD}" '
                    f'stroke="{LIME if last else EDGE}" stroke-width="{1.5 if last else 1}"/>')
        y0 = top + bh / 2 - (len(lines) - 1) * 9 + 4
        body += [text(x + bw / 2, y0 + j * 18, line, 12, TEXT, anchor="middle") for j, line in enumerate(lines)]
        if not last:
            ay = top + bh / 2
            body.append(f'<line x1="{x + bw + 4}" y1="{ay}" x2="{x + bw + gap - 8}" y2="{ay}" stroke="{MUTED}" '
                        f'stroke-width="1.5" class="flow"/>'
                        f'<path d="M{x + bw + gap - 9} {ay - 4}L{x + bw + gap - 4} {ay}L{x + bw + gap - 9} {ay + 4}Z" fill="{MUTED}"/>')
    h = top + bh + 22
    return svg(840, h + 12, tile(6, 6, 828, h) + text(30, 44, "how it works", 12, MUTED, MONO) + "".join(body),
               "How it works: " + " → ".join(steps) + ".")


def cs_results(items, note):
    colw = 780 / len(items)
    body = []
    for i, (value, caption) in enumerate(items):
        x = 30 + i * colw
        body.append(text(x, 90, value, 28, weight=600, spacing=-0.6))
        body.append(text(x, 114, caption, 13, MUTED))
    h = 140
    if note:
        body.append(f'<rect x="30" y="138" width="780" height="1" fill="{BORDER}"/>' + text(30, 168, note, 14, TEXT))
        h = 192
    alt = "Results: " + "; ".join(f"{v}, {c}" for v, c in items) + (f". {note}" if note else ".")
    return svg(840, h + 12, tile(6, 6, 828, h) + text(30, 44, "results", 12, MUTED, MONO) + "".join(body), alt)


def case_study(cs):
    """Returns ({asset path: svg}, markdown page) for one case study."""
    pictures = {"bars": bars_picture, "rollout": rollout_picture}
    s = cs["slug"]
    tiles = {
        f"work/{s}-hero.svg": cs_hero(cs, pictures[cs["picture"]]()),
        f"work/{s}-glance.svg": cs_glance(cs["glance"]),
        f"work/{s}-problem.svg": cs_text("the problem", paragraph=cs["problem"]),
        f"work/{s}-built.svg": cs_text("what i built", bullets=cs["built"]),
        f"work/{s}-flow.svg": cs_flow(cs["flow"]),
        f"work/{s}-results.svg": cs_results(cs["results"], cs["note"]),
        f"work/{s}-worked.svg": cs_text("how i worked", bullets=cs["worked"]),
    }
    w = 840 // len(cs["links"])
    for i, (name, arrow, _) in enumerate(cs["links"]):
        tiles[f"work/{s}-link-{i}.svg"] = contact(name, arrow, w)

    def alt(path):
        return escape(ElementTree.fromstring(tiles[path]).get("aria-label"))

    images = "\n\n".join(f'<img src="../assets/{p}" width="100%" alt="{alt(p)}" />'
                         for p in tiles if "-link-" not in p)
    links = "".join(f'<a href="{url}"><img src="../assets/work/{s}-link-{i}.svg" width="{100 / len(cs["links"]):.2f}%" '
                    f'alt="{escape(name)}" /></a>' for i, (name, _, url) in enumerate(cs["links"]))
    page = (f"<!-- Generated by scripts/build_assets.py: edit CASE_STUDIES there, then re-run. -->\n"
            f'<div align="center">\n\n{images}\n\n{links}\n\n<sub>{escape(CASE_NOTE)}</sub>\n\n</div>\n')
    return tiles, page


# ---------- build ----------

def main():
    outputs = {
        "header.svg": header(),
        "label-impact.svg": label("impact at ubs / read the case studies"),
        "label-shipped.svg": label("shipped / install it today"),
        "recognition.svg": recognition_and_stack(),
        "contact-email.svg": contact("Email"),
        "contact-linkedin.svg": contact("LinkedIn"),
    }
    pictures = {"bars": bars_picture, "rollout": rollout_picture}
    for item in IMPACT:
        outputs[f"impact-{item['slug']}.svg"] = impact({**item, "picture": pictures[item["picture"]]()})
    for p in PROJECTS:
        outputs[f"project-{p['slug']}.svg"] = project(p)

    for cs in CASE_STUDIES:
        tiles, page = case_study(cs)
        outputs.update(tiles)
        (ROOT / "work").mkdir(exist_ok=True)
        (ROOT / "work" / f"{cs['slug']}.md").write_text(page, encoding="utf-8")

    (ASSETS / "work").mkdir(exist_ok=True)
    for name, content in outputs.items():
        ElementTree.fromstring(content)  # self-check: every tile must be well-formed XML
        (ASSETS / name).write_text(content, encoding="utf-8")
        print(f"{name:44} {len(content) / 1024:6.1f} KB")


if __name__ == "__main__":
    main()
