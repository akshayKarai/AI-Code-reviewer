"""
AI Code Reviewer — Streamlit Frontend
A sleek, dark-themed IDE-style interface for code review.
"""

import streamlit as st
import requests
import os

API_BASE = os.getenv("API_BASE_URL", "http://localhost:8000")

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="CodeSage · AI Code Reviewer",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600&family=Syne:wght@400;600;700;800&display=swap');

html, body, [class*="css"] { font-family: 'Syne', sans-serif; }
code, pre, .stCodeBlock { font-family: 'JetBrains Mono', monospace !important; }

/* Hero */
.hero {
    background: linear-gradient(135deg, #0d0d0d 0%, #111827 50%, #0f1e3d 100%);
    border: 1px solid #1f2937;
    border-radius: 16px;
    padding: 2rem 2.5rem;
    margin-bottom: 1.5rem;
    position: relative;
    overflow: hidden;
}
.hero::after {
    content: '</>';
    position: absolute;
    right: 2rem; top: 50%;
    transform: translateY(-50%);
    font-family: 'JetBrains Mono', monospace;
    font-size: 4rem;
    color: rgba(99,102,241,0.12);
    font-weight: 600;
}
.hero h1 { color: #f1f5f9; font-size: 2rem; margin: 0 0 0.3rem; font-weight: 800; }
.hero p  { color: #64748b; margin: 0; font-size: 0.95rem; }

/* Score ring */
.score-container { text-align: center; padding: 1rem 0; }
.score-number {
    font-size: 3.5rem;
    font-weight: 800;
    font-family: 'JetBrains Mono', monospace;
    line-height: 1;
}
.score-label { font-size: 0.8rem; color: #64748b; text-transform: uppercase; letter-spacing: 0.1em; margin-top: 4px; }

/* Issue cards */
.issue-card {
    border-radius: 10px;
    padding: 1rem 1.2rem;
    margin-bottom: 0.8rem;
    border-left: 4px solid;
}
.issue-critical { background: #1c0a0a; border-color: #ef4444; }
.issue-major    { background: #1c1208; border-color: #f97316; }
.issue-minor    { background: #1a1a08; border-color: #eab308; }
.issue-suggestion { background: #08111c; border-color: #3b82f6; }

.issue-header {
    display: flex; align-items: center; gap: 10px;
    margin-bottom: 0.5rem;
}
.issue-title { font-weight: 700; color: #f1f5f9; font-size: 0.95rem; }
.issue-meta  { font-size: 0.75rem; color: #64748b; }
.issue-desc  { color: #94a3b8; font-size: 0.88rem; line-height: 1.6; margin-bottom: 0.4rem; }
.issue-fix   { color: #4ade80; font-size: 0.85rem; line-height: 1.5; }
.fix-label   { font-size: 0.7rem; text-transform: uppercase; letter-spacing: 0.08em; color: #22c55e; font-weight: 700; margin-bottom: 2px; }

/* Severity badge */
.badge {
    display: inline-block; font-size: 0.68rem; font-weight: 700;
    padding: 2px 8px; border-radius: 20px; text-transform: uppercase; letter-spacing: 0.06em;
}
.badge-critical  { background: #450a0a; color: #fca5a5; }
.badge-major     { background: #431407; color: #fdba74; }
.badge-minor     { background: #422006; color: #fde047; }
.badge-suggestion { background: #0c1a2e; color: #93c5fd; }

/* Stat cards */
.stats-row { display: flex; gap: 10px; flex-wrap: wrap; margin: 1rem 0; }
.stat-card {
    background: #111827; border: 1px solid #1f2937;
    border-radius: 10px; padding: 0.8rem 1.2rem;
    min-width: 90px; text-align: center;
}
.stat-num  { font-size: 1.6rem; font-weight: 800; font-family: 'JetBrains Mono', monospace; color: #f1f5f9; }
.stat-lbl  { font-size: 0.7rem; color: #64748b; text-transform: uppercase; letter-spacing: 0.06em; }

/* Positive aspects */
.positive-item {
    background: #071a10; border: 1px solid #14532d;
    border-radius: 8px; padding: 0.6rem 1rem;
    color: #4ade80; font-size: 0.88rem; margin-bottom: 6px;
}

/* Language pill */
.lang-pill {
    display: inline-block; background: #1e1b4b;
    color: #a5b4fc; font-size: 0.75rem; font-weight: 600;
    padding: 3px 12px; border-radius: 20px;
    font-family: 'JetBrains Mono', monospace;
    text-transform: uppercase; letter-spacing: 0.05em;
}

/* Summary box */
.summary-box {
    background: #111827; border: 1px solid #1f2937;
    border-radius: 10px; padding: 1rem 1.2rem;
    color: #cbd5e1; font-size: 0.93rem; line-height: 1.7;
    margin: 0.8rem 0;
}
</style>
""", unsafe_allow_html=True)

SEVERITY_CSS = {
    "critical": ("issue-critical", "badge-critical", "🔴"),
    "major": ("issue-major", "badge-major", "🟠"),
    "minor": ("issue-minor", "badge-minor", "🟡"),
    "suggestion": ("issue-suggestion", "badge-suggestion", "🔵"),
}

SCORE_COLOR = lambda s: "#4ade80" if s >= 80 else "#eab308" if s >= 55 else "#ef4444"


# ── API helpers ────────────────────────────────────────────────────────────────
def api_get(path):
    try:
        r = requests.get(f"{API_BASE}{path}", timeout=10)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        st.error(f"API error: {e}")
        return None


def api_post(path, payload):
    try:
        r = requests.post(f"{API_BASE}{path}", json=payload, timeout=60)
        r.raise_for_status()
        return r.json()
    except requests.HTTPError as e:
        st.error(f"Error: {e.response.json().get('detail', str(e))}")
        return None
    except Exception as e:
        st.error(f"API error: {e}")
        return None


# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🔍 CodeSage")
    st.markdown("*AI-Powered Code Reviewer*")
    st.divider()

    health = api_get("/health")
    if health:
        st.success("Backend connected ✅")
        st.caption(f"Model: `{health.get('model', 'claude')}`")
    else:
        st.error("Backend offline ❌")

    st.divider()
    st.markdown("### ⚙️ Review Settings")

    languages = api_get("/languages")
    lang_list = languages["languages"] if languages else ["auto", "python", "javascript"]
    selected_lang = st.selectbox("Language", lang_list, index=0)

    st.markdown("**Focus Areas**")
    focus_bugs     = st.checkbox("🐛 Bugs",            value=True)
    focus_security = st.checkbox("🔐 Security",        value=True)
    focus_perf     = st.checkbox("⚡ Performance",     value=True)
    focus_style    = st.checkbox("🎨 Style",           value=True)
    focus_bp       = st.checkbox("📘 Best Practices",  value=True)

    focus_map = {
        "bugs": focus_bugs, "security": focus_security,
        "performance": focus_perf, "style": focus_style,
        "best_practices": focus_bp,
    }
    selected_focus = [k for k, v in focus_map.items() if v] or ["bugs"]

    severity_filter = st.selectbox(
        "Show Issues",
        ["all", "critical", "major"],
        format_func=lambda x: {"all": "All severities", "critical": "Critical only", "major": "Critical + Major"}[x]
    )

    st.divider()
    st.markdown("""
**How it works**
1. Paste your code in the editor
2. Choose language & focus areas
3. Click **Review Code**
4. Get scored feedback + fixes
""")


# ── Main ───────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <h1>🔍 CodeSage</h1>
    <p>Paste your code and get instant AI-powered review — bugs, security, performance & style</p>
</div>
""", unsafe_allow_html=True)

tab_review, tab_explain, tab_examples = st.tabs(["📋 Code Review", "💡 Explain Code", "📂 Examples"])


# ── Tab 1: Review ──────────────────────────────────────────────────────────────
with tab_review:
    code_input = st.text_area(
        "Paste your code here",
        height=300,
        placeholder="# Paste any code here...\ndef my_function():\n    pass",
        label_visibility="collapsed",
    )

    col1, col2 = st.columns([1, 4])
    with col1:
        review_btn = st.button("🔍 Review Code", type="primary", use_container_width=True)

    if review_btn:
        if not code_input.strip():
            st.warning("Please paste some code first.")
        else:
            with st.spinner("Analysing your code with Claude AI…"):
                result = api_post("/review", {
                    "code": code_input,
                    "language": selected_lang,
                    "focus": selected_focus,
                    "severity_filter": severity_filter,
                })

            if result:
                st.session_state["last_review"] = result

    if "last_review" in st.session_state:
        r = st.session_state["last_review"]
        score = r["overall_score"]
        color = SCORE_COLOR(score)

        st.markdown("---")

        # Header row
        col_score, col_info = st.columns([1, 3])
        with col_score:
            st.markdown(f"""
            <div class="score-container">
                <div class="score-number" style="color:{color}">{score}</div>
                <div class="score-label">Quality Score</div>
            </div>
            """, unsafe_allow_html=True)

        with col_info:
            st.markdown(f'<span class="lang-pill">{r["language"]}</span>', unsafe_allow_html=True)
            st.markdown(f'<div class="summary-box">{r["summary"]}</div>', unsafe_allow_html=True)

        # Stats row
        s = r["stats"]
        st.markdown(f"""
        <div class="stats-row">
            <div class="stat-card"><div class="stat-num">{s["total_issues"]}</div><div class="stat-lbl">Total Issues</div></div>
            <div class="stat-card"><div class="stat-num" style="color:#ef4444">{s["critical"]}</div><div class="stat-lbl">Critical</div></div>
            <div class="stat-card"><div class="stat-num" style="color:#f97316">{s["major"]}</div><div class="stat-lbl">Major</div></div>
            <div class="stat-card"><div class="stat-num" style="color:#eab308">{s["minor"]}</div><div class="stat-lbl">Minor</div></div>
            <div class="stat-card"><div class="stat-num" style="color:#3b82f6">{s["suggestions"]}</div><div class="stat-lbl">Tips</div></div>
            <div class="stat-card"><div class="stat-num">{s["lines_of_code"]}</div><div class="stat-lbl">Lines</div></div>
        </div>
        """, unsafe_allow_html=True)

        # Issues
        if r["issues"]:
            st.markdown("### 🚨 Issues Found")
            for issue in r["issues"]:
                sev = issue["severity"]
                card_cls, badge_cls, emoji = SEVERITY_CSS.get(sev, SEVERITY_CSS["suggestion"])
                line_info = f" · Line {issue['line']}" if issue.get("line") else ""
                cat = issue.get("category", "general").replace("_", " ").title()
                st.markdown(f"""
                <div class="issue-card {card_cls}">
                    <div class="issue-header">
                        <span>{emoji}</span>
                        <span class="issue-title">{issue['title']}</span>
                        <span class="badge {badge_cls}">{sev}</span>
                    </div>
                    <div class="issue-meta">{cat}{line_info}</div>
                    <div class="issue-desc">{issue['description']}</div>
                    <div class="fix-label">💡 Fix</div>
                    <div class="issue-fix">{issue['suggestion']}</div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.success("🎉 No issues found matching your filter!")

        # Positive aspects
        if r.get("positive_aspects"):
            st.markdown("### ✅ What's Done Well")
            for p in r["positive_aspects"]:
                st.markdown(f'<div class="positive-item">✓ {p}</div>', unsafe_allow_html=True)

        # Refactored snippet
        if r.get("refactored_snippet"):
            with st.expander("✨ Suggested Refactor"):
                st.code(r["refactored_snippet"], language=r["language"])


# ── Tab 2: Explain ─────────────────────────────────────────────────────────────
with tab_explain:
    explain_input = st.text_area(
        "Paste code to explain",
        height=280,
        placeholder="# Paste any code you want explained in plain English...",
        label_visibility="collapsed",
    )
    if st.button("💡 Explain This Code", type="primary"):
        if not explain_input.strip():
            st.warning("Please paste some code first.")
        else:
            with st.spinner("Generating explanation…"):
                result = api_post("/explain", {"code": explain_input, "language": selected_lang})
            if result:
                st.markdown(f'<span class="lang-pill">{result["language"]}</span>', unsafe_allow_html=True)
                st.markdown(f'<div class="summary-box" style="margin-top:0.8rem">{result["explanation"]}</div>', unsafe_allow_html=True)


# ── Tab 3: Examples ────────────────────────────────────────────────────────────
with tab_explain:
    pass

with tab_examples:
    st.markdown("### 📂 Sample Code Snippets")
    st.markdown("Click any example to load it into the reviewer.")

    examples = {
        "🐛 Python — SQL Injection Bug": {
            "lang": "python",
            "code": '''import sqlite3

def get_user(username):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    # Vulnerable to SQL injection!
    query = "SELECT * FROM users WHERE username = '" + username + "'"
    cursor.execute(query)
    return cursor.fetchone()

def login(username, password):
    user = get_user(username)
    if user and user[2] == password:  # password stored as plaintext
        return True
    return False
'''
        },
        "⚡ JavaScript — Performance Issue": {
            "lang": "javascript",
            "code": '''function findDuplicates(arr) {
    var duplicates = [];
    for (var i = 0; i < arr.length; i++) {
        for (var j = 0; j < arr.length; j++) {
            if (i !== j && arr[i] === arr[j]) {
                if (duplicates.indexOf(arr[i]) === -1) {
                    duplicates.push(arr[i]);
                }
            }
        }
    }
    return duplicates;
}

var numbers = [1,2,3,2,4,3,5];
console.log(findDuplicates(numbers));
'''
        },
        "🔐 Python — Password Manager": {
            "lang": "python",
            "code": '''passwords = {}

def save_password(site, password):
    passwords[site] = password  # stored in plain text in memory
    with open("passwords.txt", "a") as f:
        f.write(f"{site}:{password}\\n")  # written to disk unencrypted

def get_password(site):
    return passwords.get(site, "Not found")

save_password("gmail.com", "mysecretpassword123")
print(get_password("gmail.com"))
'''
        },
        "✅ Clean Python — Good Example": {
            "lang": "python",
            "code": '''from dataclasses import dataclass
from typing import Optional
import logging

logger = logging.getLogger(__name__)

@dataclass
class Product:
    name: str
    price: float
    quantity: int = 0

    def is_in_stock(self) -> bool:
        return self.quantity > 0

    def apply_discount(self, percent: float) -> float:
        if not 0 <= percent <= 100:
            raise ValueError(f"Discount must be 0-100, got {percent}")
        return self.price * (1 - percent / 100)


def process_order(product: Product, qty: int) -> Optional[float]:
    if not product.is_in_stock():
        logger.warning("Product %s is out of stock", product.name)
        return None
    if qty > product.quantity:
        logger.error("Requested qty %d exceeds stock %d", qty, product.quantity)
        return None
    total = product.price * qty
    product.quantity -= qty
    logger.info("Order processed: %s x%d = $%.2f", product.name, qty, total)
    return total
'''
        },
    }

    for label, data in examples.items():
        if st.button(label, use_container_width=True):
            st.session_state["load_example"] = data
            st.success(f"Example loaded! Switch to **📋 Code Review** tab and click **Review Code**.")

    if "load_example" in st.session_state:
        ex = st.session_state["load_example"]
        st.code(ex["code"], language=ex["lang"])
        st.caption("Copy the code above, paste it in the **Code Review** tab, and hit Review!")
