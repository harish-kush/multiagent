"""ResearchAI - Streamlit frontend for the multi-agent research pipeline."""
import html
import json
import re
from datetime import datetime

import streamlit as st

from pipeline import run_research_pipeline

st.set_page_config(page_title="ResearchAI", page_icon="🔎", layout="wide")

STAGES = [
    ("search", "Search Agent", "Finds sources with Tavily"),
    ("reader", "Reader Agent", "Scrapes the most relevant pages"),
    ("writer", "Writer Agent", "Drafts the research report"),
    ("critic", "Critic Agent", "Fact-checks and scores the report"),
]
ICONS = {"pending": "○", "running": "◐", "completed": "✓", "failed": "✕"}
LABELS = {"pending": "Pending", "running": "Running", "completed": "Completed", "failed": "Failed"}

CSS = """
<style>
:root{--bg:#0b1020;--card:#121a30;--line:#222c4a;--text:#e6e9f5;--mute:#8b94b3;--acc:#7c6cff;--acc2:#4f8bff;}
.stApp{background:var(--bg);color:var(--text);}
[data-testid="stSidebar"]{background:#0e1428;border-right:1px solid var(--line);}
#MainMenu,footer{visibility:hidden;}
.block-container{padding-top:2.2rem;max-width:1100px;}
h1.hero{font-size:2.4rem;font-weight:700;letter-spacing:-.02em;margin:0;}
p.sub{color:var(--mute);font-size:1.05rem;margin:.3rem 0 1.5rem;}
.brand{font-size:1.4rem;font-weight:700;}
.brand span{background:linear-gradient(90deg,var(--acc),var(--acc2));-webkit-background-clip:text;color:transparent;}
.stTextArea textarea{background:var(--card)!important;border:1px solid var(--line)!important;border-radius:12px!important;color:var(--text)!important;font-size:1.05rem!important;}
.stTextArea textarea:focus{border-color:var(--acc)!important;box-shadow:0 0 0 1px var(--acc)!important;}
.stButton>button[kind="primary"]{background:linear-gradient(90deg,var(--acc),var(--acc2));border:0;border-radius:10px;font-weight:600;padding:.6rem 1.4rem;color:#fff;}
.stButton>button[kind="primary"]:hover{filter:brightness(1.1);}
.stage{display:flex;align-items:center;gap:.8rem;background:var(--card);border:1px solid var(--line);border-radius:12px;padding:.8rem 1rem;margin-bottom:.5rem;}
.stage .ic{width:1.9rem;height:1.9rem;border-radius:50%;display:flex;align-items:center;justify-content:center;background:#1a2240;color:var(--mute);font-weight:700;}
.stage .t{font-weight:600;} .stage .d{color:var(--mute);font-size:.85rem;} .stage .s{margin-left:auto;font-size:.85rem;color:var(--mute);}
.stage.running{border-color:var(--acc);} .stage.running .ic{background:var(--acc);color:#fff;}
.stage.completed .ic{background:#1d8f6a;color:#fff;} .stage.completed .s{color:#3ccf9b;}
.stage.failed{border-color:#a5384f;} .stage.failed .ic{background:#a5384f;color:#fff;} .stage.failed .s{color:#ff7b93;}
.score{background:var(--card);border:1px solid var(--line);border-radius:16px;padding:1.4rem;text-align:center;}
.score .n{font-size:3.4rem;font-weight:700;line-height:1;}
.score .l{color:var(--mute);margin-top:.4rem;}
.empty{border:1px dashed var(--line);border-radius:16px;padding:2.5rem;text-align:center;color:var(--mute);}
.empty b{color:var(--text);font-size:1.15rem;}
[data-testid="stVerticalBlockBorderWrapper"]{border-radius:12px;}
.pill{display:inline-block;background:#1a2240;border:1px solid var(--line);border-radius:999px;padding:.15rem .7rem;margin:.15rem .2rem .15rem 0;font-size:.82rem;}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

# ---------- session state ----------
st.session_state.setdefault("history", [])   # list of {topic, time, result}
st.session_state.setdefault("current", None)  # {topic, time, result}


# ---------- parsing helpers ----------
def parse_search_results(text):
    items = []
    for block in re.split(r"\n---\n", text or ""):
        title = re.search(r"Title:\s*(.*)", block)
        url = re.search(r"URL:\s*(\S+)", block)
        snip = re.search(r"Snippet:\s*(.*)", block, re.S)
        if url:
            items.append({
                "title": title.group(1).strip() if title else url.group(1),
                "url": url.group(1),
                "snippet": snip.group(1).strip() if snip else "",
            })
    return items


def _clean(s):
    return re.sub(r"\*\*|__", "", s or "").strip()


def parse_critic(text):
    text = text or ""
    score = re.search(r"Score:?\**\s*(\d+(?:\.\d+)?)\s*/\s*10", text, re.I)
    sections = {}
    pattern = r"(Strengths|Areas\s+to\s+Improve|One[\s-]*line\s+verdict)\W*:?\**"
    parts = re.split(pattern, text, flags=re.I)
    for i in range(1, len(parts) - 1, 2):
        key = re.sub(r"\s+", " ", parts[i].lower())
        sections[key] = parts[i + 1].strip(" *\n:")
    verdict = next((v for k, v in sections.items() if "verdict" in k), "")
    return {
        "score": float(score.group(1)) if score else None,
        "strengths": sections.get("strengths", ""),
        "improve": next((v for k, v in sections.items() if k.startswith("areas")), ""),
        "verdict": _clean(verdict),
    }


# ---------- progress UI ----------
def render_stages(container, statuses):
    rows = ""
    for key, name, desc in STAGES:
        s = statuses[key]
        rows += (
            f'<div class="stage {s}"><div class="ic">{ICONS[s]}</div>'
            f'<div><div class="t">{name}</div><div class="d">{desc}</div></div>'
            f'<div class="s">{LABELS[s]}</div></div>'
        )
    container.markdown(rows, unsafe_allow_html=True)


def run_with_progress(topic):
    statuses = {k: "pending" for k, _, _ in STAGES}
    box = st.empty()
    render_stages(box, statuses)

    def on_progress(stage, status):
        statuses[stage] = status
        render_stages(box, statuses)

    try:
        with st.spinner("Agents are researching. This can take a minute or two…"):
            result = run_research_pipeline(topic, on_progress=on_progress)
    except Exception as e:  # stage already marked failed by the pipeline
        for k, v in statuses.items():
            if v == "running":
                statuses[k] = "failed"
        render_stages(box, statuses)
        return {"error": f"{type(e).__name__}: {e}"}
    return result


# ---------- sidebar ----------
with st.sidebar:
    st.markdown('<div class="brand">🔎 <span>ResearchAI</span></div>', unsafe_allow_html=True)
    st.caption("Multi-Agent Research Assistant")
    st.markdown("**About**")
    st.write(
        "Four specialised agents work in sequence: one searches the web, one reads "
        "the best sources, one writes a cited report, and one fact-checks it."
    )
    st.markdown("**Tech stack**")
    st.markdown(
        "".join(f'<span class="pill">{t}</span>' for t in [
            "Gemini 2.5 Flash", "LangChain", "LangGraph / ReAct Agents",
            "Tavily Search", "BeautifulSoup", "LCEL"]),
        unsafe_allow_html=True,
    )
    st.divider()
    st.markdown("**Session history**")
    if not st.session_state.history:
        st.caption("Your research this session will appear here.")
    for i, h in enumerate(reversed(st.session_state.history)):
        idx = len(st.session_state.history) - 1 - i
        label = h["topic"][:34] + ("…" if len(h["topic"]) > 34 else "")
        if st.button(f"{label}", key=f"hist{idx}", help=h["time"], use_container_width=True):
            st.session_state.current = h
            st.rerun()

# ---------- main ----------
st.markdown('<h1 class="hero">AI Research Assistant</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub">Research smarter with autonomous AI agents.</p>', unsafe_allow_html=True)

topic = st.text_area(
    "Research topic",
    placeholder="Enter a topic, e.g. Latest developments in Artificial Intelligence...",
    height=100, label_visibility="collapsed", key="topic_input",
)
go = st.button("Start Research", type="primary")

if go:
    if not topic.strip():
        st.warning("Enter a research topic to get started.")
    else:
        st.markdown("#### Research progress")
        result = run_with_progress(topic.strip())
        entry = {"topic": topic.strip(), "time": datetime.now().strftime("%H:%M:%S"), "result": result}
        st.session_state.current = entry
        if "error" not in result:
            st.session_state.history.append(entry)
        st.rerun() if "error" not in result else None

cur = st.session_state.current

if cur is None:
    st.markdown(
        '<div class="empty"><b>No research yet</b><br>Enter a topic above and select '
        'Start Research. Results, the report and the critic review will appear here.</div>',
        unsafe_allow_html=True,
    )
else:
    res = cur["result"]
    st.markdown(f"#### Results for: {html.escape(cur['topic'])}")

    if "error" in res:
        st.error(f"Research failed: {res['error']}")
        st.caption("Check that your TAVILY_API_KEY and GEMINI_API_KEY are set in .env, then try again or rephrase the topic.")

    tabs = st.tabs(["Search Results", "Scraped Content", "Research Report", "Critic Evaluation"])

    with tabs[0]:
        items = parse_search_results(res.get("search_results", ""))
        if not items:
            st.info("No search results available.")
        for it in items:
            with st.container(border=True):
                st.markdown(f"**[{it['title']}]({it['url']})**")
                st.caption(it["url"])
                st.write(it["snippet"])

    with tabs[1]:
        sources = res.get("scraped_sources") or []
        if sources:
            for n, s in enumerate(sources, 1):
                failed = s["content"].startswith("Could not scrape URL")
                title = s["url"] or f"Source {n}"
                with st.expander(("⚠️ " if failed else "") + title, expanded=(n == 1 and not failed)):
                    if s["url"]:
                        st.markdown(f"[Open source]({s['url']})")
                    if failed:
                        st.warning(s["content"])
                    else:
                        st.write(s["content"])
        elif res.get("scraped_content"):
            with st.expander("Scraped content", expanded=True):
                st.write(res["scraped_content"])
        else:
            st.info("No scraped content available.")

    with tabs[2]:
        report = res.get("report")
        if report:
            st.markdown(report)
            st.download_button("Download Report (.md)", report, file_name="research_report.md",
                               mime="text/markdown", key="dl_md")
        else:
            st.info("The report was not generated.")

    with tabs[3]:
        fb = res.get("feedback")
        if fb:
            c = parse_critic(fb)
            left, right = st.columns([1, 2])
            with left:
                if c["score"] is not None:
                    color = "#3ccf9b" if c["score"] >= 8 else "#f5b84b" if c["score"] >= 5 else "#ff7b93"
                    st.markdown(
                        f'<div class="score"><div class="n" style="color:{color}">{c["score"]:g}'
                        f'<span style="font-size:1.4rem;color:#8b94b3">/10</span></div>'
                        f'<div class="l">Critic score</div></div>', unsafe_allow_html=True)
                else:
                    st.info("Score could not be parsed.")
            with right:
                if c["verdict"]:
                    st.markdown("**Verdict**")
                    st.info(c["verdict"])
            if c["strengths"] or c["improve"]:
                a, b = st.columns(2)
                with a:
                    st.markdown("**Strengths**")
                    st.markdown(c["strengths"] or "_None listed._")
                with b:
                    st.markdown("**Areas to improve**")
                    st.markdown(c["improve"] or "_None listed._")
            else:
                st.markdown(fb)
            with st.expander("Raw critic response"):
                st.text(fb)
        else:
            st.info("No critic evaluation available.")

    st.download_button(
        "Download complete research data (.json)",
        json.dumps({"topic": cur["topic"], "generated_at": cur["time"], **res}, indent=2, ensure_ascii=False),
        file_name="research_data.json", mime="application/json", key="dl_json",
    )