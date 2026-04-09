import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime

# ── Try importing plotly (optional) ──────────────────────────────────────────
try:
    import plotly.express as px
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False

# ── PAGE CONFIG ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="DRP Platform",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CUSTOM CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    /* ── General ── */
    .block-container { padding-top: 1.5rem; }

    /* ── KPI cards ── */
    .kpi-card {
        background: #f8f9fa;
        border-left: 5px solid #0d6efd;
        border-radius: 8px;
        padding: 14px 18px;
        margin-bottom: 10px;
    }
    .kpi-card.yellow { border-left-color: #ffc107; }
    .kpi-card.green  { border-left-color: #198754; }
    .kpi-card.blue   { border-left-color: #0dcaf0; }
    .kpi-card.dark   { border-left-color: #6c757d; }
    .kpi-number { font-size: 2rem; font-weight: 700; }
    .kpi-label  { font-size: 0.85rem; color: #6c757d; margin-top: 2px; }

    /* ── Status badges ── */
    .badge {
        display: inline-block;
        padding: 3px 10px;
        border-radius: 12px;
        font-size: 0.78rem;
        font-weight: 600;
        letter-spacing: 0.4px;
    }
    .badge-pending     { background:#fff3cd; color:#856404; }
    .badge-approved    { background:#d1e7dd; color:#0f5132; }
    .badge-rejected    { background:#f8d7da; color:#842029; }
    .badge-implemented { background:#cfe2ff; color:#084298; }
    .badge-closed      { background:#e2e3e5; color:#383d41; }

    /* ── Workflow stepper ── */
    .workflow-step {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 20px;
        margin: 2px;
        font-size: 0.8rem;
        font-weight: 600;
    }
    .step-active   { background:#0d6efd; color:#fff; }
    .step-done     { background:#198754; color:#fff; }
    .step-upcoming { background:#e9ecef; color:#6c757d; }

    /* ── Section headers ── */
    .section-header {
        font-size: 1.05rem;
        font-weight: 700;
        color: #212529;
        border-bottom: 2px solid #0d6efd;
        padding-bottom: 4px;
        margin-bottom: 14px;
    }

    /* ── Login box ── */
    .login-box {
        background: #fff;
        border: 1px solid #dee2e6;
        border-radius: 12px;
        padding: 36px 40px;
        box-shadow: 0 4px 16px rgba(0,0,0,0.08);
    }

    /* ── Sidebar nav button tweaks ── */
    section[data-testid="stSidebar"] .stButton > button {
        text-align: left;
        border-radius: 6px;
        border: none;
        background: transparent;
        padding: 8px 12px;
        width: 100%;
        font-size: 0.9rem;
    }
    section[data-testid="stSidebar"] .stButton > button:hover {
        background: #e9ecef;
    }
    section[data-testid="stSidebar"] .stButton.active-nav > button {
        background: #0d6efd;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# ── FILE PATHS ────────────────────────────────────────────────────────────────
DC_FILE   = "design_changes.csv"
CON_FILE  = "construction.csv"
LOG_FILE  = "logistics.csv"
USR_FILE  = "users.json"

# ── INIT DATA FILES ───────────────────────────────────────────────────────────
def init_files():
    if not os.path.exists(DC_FILE):
        pd.DataFrame(columns=[
            "change_id","project_name","element_id","location_floor",
            "description","raised_by","raised_by_role","file_name",
            "status","pmc_comment","client_comment","created_at","updated_at"
        ]).to_csv(DC_FILE, index=False)

    if not os.path.exists(CON_FILE):
        pd.DataFrame(columns=[
            "zone_floor","activity","status","responsible_stakeholder","last_update"
        ]).to_csv(CON_FILE, index=False)

    if not os.path.exists(LOG_FILE):
        pd.DataFrame(columns=[
            "component_id","dispatch_date","in_transit","delivered","installed"
        ]).to_csv(LOG_FILE, index=False)

    if not os.path.exists(USR_FILE):
        with open(USR_FILE, "w") as f:
            json.dump([], f)

init_files()

# ── SESSION STATE ─────────────────────────────────────────────────────────────
def ss_init():
    defaults = {
        "logged_in": False,
        "user_name": "",
        "user_role": "",
        "current_page": "Dashboard",
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

ss_init()

# ── DATA HELPERS ──────────────────────────────────────────────────────────────
def load_dc():
    return pd.read_csv(DC_FILE)

def save_dc(df):
    df.to_csv(DC_FILE, index=False)

def load_con():
    return pd.read_csv(CON_FILE)

def save_con(df):
    df.to_csv(CON_FILE, index=False)

def load_log():
    return pd.read_csv(LOG_FILE)

def save_log(df):
    df.to_csv(LOG_FILE, index=False)

def gen_change_id():
    df = load_dc()
    return f"CHG-{len(df)+1:04d}"

def now_str():
    return datetime.now().strftime("%Y-%m-%d %H:%M")

# ── BADGE HTML ────────────────────────────────────────────────────────────────
BADGE_CLASS = {
    "Pending":     "badge-pending",
    "Approved":    "badge-approved",
    "Rejected":    "badge-rejected",
    "Implemented": "badge-implemented",
    "Closed":      "badge-closed",
}
BADGE_ICON = {
    "Pending": "🟡", "Approved": "🟢", "Rejected": "🔴",
    "Implemented": "🔵", "Closed": "⚫",
}

def badge(status):
    cls = BADGE_CLASS.get(status, "badge-pending")
    icon = BADGE_ICON.get(status, "⚪")
    return f'<span class="badge {cls}">{icon} {status}</span>'

# ── WORKFLOW STEPPER ──────────────────────────────────────────────────────────
WORKFLOW = ["Pending", "Approved", "Implemented", "Closed"]

def workflow_html(current_status):
    idx = WORKFLOW.index(current_status) if current_status in WORKFLOW else -1
    if current_status == "Rejected":
        return '<span class="workflow-step" style="background:#dc3545;color:#fff;">🔴 Rejected</span>'
    parts = []
    labels = ["1 · Pending", "2 · PMC Approved", "3 · Implemented", "4 · Closed"]
    for i, label in enumerate(labels):
        if i < idx:
            cls = "step-done"
        elif i == idx:
            cls = "step-active"
        else:
            cls = "step-upcoming"
        parts.append(f'<span class="workflow-step {cls}">{label}</span>')
    return " → ".join(parts)

# ═══════════════════════════════════════════════════════════════════════════════
#  PAGE: LOGIN
# ═══════════════════════════════════════════════════════════════════════════════
def page_login():
    _, mid, _ = st.columns([1, 2, 1])
    with mid:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown("""
        <div style='text-align:center; margin-bottom:24px;'>
            <div style='font-size:3rem;'>🏗️</div>
            <h1 style='font-size:2rem; margin:6px 0 4px;'>DRP Platform</h1>
            <p style='color:#6c757d; font-size:1rem;'>Design Review & Project Management</p>
        </div>
        """, unsafe_allow_html=True)

        with st.container():
            st.markdown('<div class="login-box">', unsafe_allow_html=True)

            st.markdown("#### Login to Continue")
            name = st.text_input(
                "Your Name",
                placeholder="e.g. Ravi Shah",
                label_visibility="visible"
            )
            role = st.selectbox(
                "Select Your Role",
                ["Designer", "PMC", "Client", "Contractor", "Factory/Site"]
            )

            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("▶  Enter Platform", type="primary", use_container_width=True):
                if name.strip():
                    st.session_state.logged_in  = True
                    st.session_state.user_name  = name.strip()
                    st.session_state.user_role  = role
                    # log user
                    with open(USR_FILE, "r") as f:
                        users = json.load(f)
                    users.append({"name": name.strip(), "role": role,
                                  "login_time": now_str()})
                    with open(USR_FILE, "w") as f:
                        json.dump(users, f, indent=2)
                    st.rerun()
                else:
                    st.error("Please enter your name to continue.")

            st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("""
        <div style='text-align:center; color:#adb5bd; font-size:0.8rem;'>
            Roles: Designer · PMC · Client · Contractor · Factory/Site
        </div>
        """, unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
#  SIDEBAR
# ═══════════════════════════════════════════════════════════════════════════════
NAV_ITEMS = [
    ("📊", "Dashboard"),
    ("✏️", "Create Design Change"),
    ("✅", "Approvals"),
    ("📍", "Tracking"),
    ("🔒", "Close Change"),
    ("🧊", "BIM Viewer"),
]

def sidebar():
    with st.sidebar:
        # User info
        st.markdown(f"""
        <div style='background:#f8f9fa; border-radius:8px; padding:12px 14px; margin-bottom:14px;'>
            <div style='font-weight:700; font-size:1rem;'>👤 {st.session_state.user_name}</div>
            <div style='color:#6c757d; font-size:0.82rem; margin-top:2px;'>
                Role: <b>{st.session_state.user_role}</b>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("**Navigation**")
        for icon, label in NAV_ITEMS:
            full = f"{icon} {label}"
            is_active = st.session_state.current_page == label
            btn_label = f"▶ {full}" if is_active else f"   {full}"
            if st.button(btn_label, key=f"nav_{label}", use_container_width=True):
                st.session_state.current_page = label
                st.rerun()

        st.markdown("---")

        # Workflow quick reference
        st.markdown("**Workflow**")
        st.markdown("""
        <div style='font-size:0.8rem; color:#495057; line-height:1.9;'>
        🖊️ <b>Designer</b> → creates change<br>
        🔍 <b>PMC</b> → reviews & approves<br>
        ✅ <b>Client</b> → final approval<br>
        🔨 <b>Contractor</b> → implements<br>
        🏭 <b>Factory/Site</b> → closes
        </div>
        """, unsafe_allow_html=True)

        st.markdown("---")
        if st.button("🚪  Logout", use_container_width=True):
            for k in ["logged_in", "user_name", "user_role"]:
                st.session_state[k] = "" if k != "logged_in" else False
            st.session_state.current_page = "Dashboard"
            st.rerun()

# ═══════════════════════════════════════════════════════════════════════════════
#  PAGE: DASHBOARD
# ═══════════════════════════════════════════════════════════════════════════════
def page_dashboard():
    st.markdown("## 📊 Dashboard")
    st.markdown(f"Welcome back, **{st.session_state.user_name}** &nbsp;|&nbsp; Role: `{st.session_state.user_role}`")
    st.markdown("---")

    df = load_dc()

    # KPI row
    pending      = len(df[df.status == "Pending"])     if not df.empty else 0
    approved     = len(df[df.status == "Approved"])    if not df.empty else 0
    implemented  = len(df[df.status == "Implemented"]) if not df.empty else 0
    closed       = len(df[df.status == "Closed"])      if not df.empty else 0
    rejected     = len(df[df.status == "Rejected"])    if not df.empty else 0
    total        = len(df)

    c1, c2, c3, c4, c5, c6 = st.columns(6)
    kpi_data = [
        (c1, total,       "Total Changes",  "#0d6efd"),
        (c2, pending,     "Pending",        "#ffc107"),
        (c3, approved,    "Approved",       "#198754"),
        (c4, implemented, "Implemented",    "#0dcaf0"),
        (c5, closed,      "Closed",         "#6c757d"),
        (c6, rejected,    "Rejected",       "#dc3545"),
    ]
    for col, val, label, color in kpi_data:
        col.markdown(f"""
        <div class="kpi-card" style="border-left-color:{color};">
            <div class="kpi-number" style="color:{color};">{val}</div>
            <div class="kpi-label">{label}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    col_left, col_right = st.columns([3, 2])

    with col_left:
        st.markdown('<div class="section-header">📋 Latest Design Changes</div>', unsafe_allow_html=True)
        if df.empty:
            st.info("No design changes have been submitted yet.")
        else:
            show = df[["change_id","project_name","element_id","raised_by","status","created_at"]].tail(8).copy()
            show.columns = ["Change ID","Project","Element","Raised By","Status","Created"]
            # Add emoji to status
            show["Status"] = show["Status"].apply(lambda s: f"{BADGE_ICON.get(s,'⚪')} {s}")
            st.dataframe(show, use_container_width=True, hide_index=True)

    with col_right:
        st.markdown('<div class="section-header">📈 Status Distribution</div>', unsafe_allow_html=True)
        if df.empty or total == 0:
            st.info("Submit a design change to see statistics.")
        else:
            if PLOTLY_AVAILABLE:
                counts = df.status.value_counts().reset_index()
                counts.columns = ["Status", "Count"]
                color_map = {
                    "Pending":"#ffc107","Approved":"#198754",
                    "Rejected":"#dc3545","Implemented":"#0dcaf0","Closed":"#6c757d"
                }
                fig = px.pie(counts, values="Count", names="Status",
                             color="Status", color_discrete_map=color_map,
                             hole=0.45)
                fig.update_layout(
                    margin=dict(t=10, b=10, l=10, r=10),
                    height=260,
                    showlegend=True,
                    legend=dict(font=dict(size=11))
                )
                fig.update_traces(textposition='inside', textinfo='percent+label')
                st.plotly_chart(fig, use_container_width=True)
            else:
                counts = df.status.value_counts()
                for s, cnt in counts.items():
                    st.markdown(f"**{BADGE_ICON.get(s,'⚪')} {s}:** {cnt}")

    # Construction summary
    con_df = load_con()
    if not con_df.empty:
        st.markdown("---")
        st.markdown('<div class="section-header">🏗️ Construction Progress Snapshot</div>', unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        c1.metric("Not Started", len(con_df[con_df.status == "Not Started"]))
        c2.metric("In Progress",  len(con_df[con_df.status == "In Progress"]))
        c3.metric("Completed",    len(con_df[con_df.status == "Completed"]))

# ═══════════════════════════════════════════════════════════════════════════════
#  PAGE: CREATE DESIGN CHANGE
# ═══════════════════════════════════════════════════════════════════════════════
def page_create():
    st.markdown("## ✏️ Create Design Change")

    role = st.session_state.user_role
    if role != "Designer":
        st.error("🚫 **Access Denied** — Only users with the **Designer** role can create design changes.")
        st.info(f"Your current role is: **{role}**")
        return

    st.markdown("Fill in the details below. Fields marked **\\*** are required.")
    st.markdown("---")

    with st.form("create_change_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            project_name  = st.text_input("Project Name *")
            element_id    = st.text_input("Element ID *", placeholder="e.g. COL-B3, WALL-F2")
        with col2:
            location_floor = st.text_input("Location / Floor *", placeholder="e.g. Level 2, Zone A")
            raised_by      = st.text_input("Raised By", value=st.session_state.user_name, disabled=True)

        description = st.text_area("Description of Change *",
                                   placeholder="Describe the change in detail…",
                                   height=130)

        uploaded_file = st.file_uploader(
            "Attach Supporting File (optional)",
            type=["pdf","png","jpg","jpeg","dwg","xlsx","docx"],
            help="Drawings, images, or documents supporting this change"
        )

        st.markdown("<br>", unsafe_allow_html=True)
        submitted = st.form_submit_button("📤  Submit Design Change", type="primary")

        if submitted:
            errors = []
            if not project_name.strip():  errors.append("Project Name")
            if not element_id.strip():    errors.append("Element ID")
            if not location_floor.strip():errors.append("Location / Floor")
            if not description.strip():   errors.append("Description")

            if errors:
                st.error(f"Please fill in: **{', '.join(errors)}**")
            else:
                change_id = gen_change_id()
                file_name = uploaded_file.name if uploaded_file else ""
                df = load_dc()
                new_row = pd.DataFrame([{
                    "change_id":      change_id,
                    "project_name":   project_name.strip(),
                    "element_id":     element_id.strip(),
                    "location_floor": location_floor.strip(),
                    "description":    description.strip(),
                    "raised_by":      st.session_state.user_name,
                    "raised_by_role": role,
                    "file_name":      file_name,
                    "status":         "Pending",
                    "pmc_comment":    "",
                    "client_comment": "",
                    "created_at":     now_str(),
                    "updated_at":     now_str(),
                }])
                df = pd.concat([df, new_row], ignore_index=True)
                save_dc(df)
                st.success(f"✅ Design Change **{change_id}** submitted successfully!")
                st.balloons()
                st.markdown(f"""
                <div style='background:#d1e7dd; border-radius:8px; padding:14px 18px; margin-top:10px;'>
                    <b>Change ID:</b> {change_id}<br>
                    <b>Status:</b> 🟡 Pending (awaiting PMC review)<br>
                    <b>Submitted by:</b> {st.session_state.user_name} at {now_str()}
                </div>
                """, unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
#  PAGE: APPROVALS
# ═══════════════════════════════════════════════════════════════════════════════
def page_approvals():
    st.markdown("## ✅ Approvals")

    role = st.session_state.user_role
    if role not in ["PMC", "Client"]:
        st.error("🚫 **Access Denied** — Only **PMC** and **Client** roles can access the Approvals page.")
        st.info(f"Your current role is: **{role}**")
        return

    df = load_dc()

    # Tabs: My Queue | All Changes
    tab_queue, tab_all = st.tabs(["📥 My Approval Queue", "📋 All Changes"])

    with tab_queue:
        if role == "PMC":
            queue = df[df.status == "Pending"].copy()
            st.markdown(f"**PMC Review Queue** — Changes waiting for your review &nbsp; `{len(queue)} pending`")
            next_status_approve = "Approved"
            comment_col = "pmc_comment"
        else:  # Client
            queue = df[df.status == "Approved"].copy()
            st.markdown(f"**Client Final Approval Queue** — PMC-approved changes awaiting your sign-off &nbsp; `{len(queue)} pending`")
            next_status_approve = "Implemented"
            comment_col = "client_comment"

        if queue.empty:
            st.success("🎉 Your queue is empty — nothing waiting for review.")
        else:
            for _, row in queue.iterrows():
                with st.expander(
                    f"📄 **{row.change_id}**  ·  {row.project_name}  ·  Element: {row.element_id}  ·  "
                    f"Floor: {row.location_floor}",
                    expanded=False
                ):
                    # Workflow stepper
                    st.markdown(workflow_html(row.status), unsafe_allow_html=True)
                    st.markdown("<br>", unsafe_allow_html=True)

                    c1, c2 = st.columns(2)
                    with c1:
                        st.markdown(f"**Project:** {row.project_name}")
                        st.markdown(f"**Element ID:** `{row.element_id}`")
                        st.markdown(f"**Location / Floor:** {row.location_floor}")
                    with c2:
                        st.markdown(f"**Raised By:** {row.raised_by} ({row.raised_by_role})")
                        st.markdown(f"**Submitted:** {row.created_at}")
                        st.markdown(f"**Status:** {row.status}", unsafe_allow_html=True)

                    st.markdown(f"**Description:**\n> {row.description}")

                    if row.file_name:
                        st.markdown(f"📎 **Attached File:** `{row.file_name}`")

                    if role == "Client" and row.pmc_comment:
                        st.markdown(f"💬 **PMC Comment:** {row.pmc_comment}")

                    comment = st.text_area(
                        "Your Comment (optional)",
                        key=f"comment_{row.change_id}",
                        placeholder="Add review notes…"
                    )

                    ca, cb, _ = st.columns([1.2, 1.2, 3])
                    approve_label = "✅ Approve → Implement" if role == "Client" else "✅ Approve → Send to Client"
                    if ca.button(approve_label, key=f"approve_{row.change_id}", type="primary"):
                        df.loc[df.change_id == row.change_id, "status"]    = next_status_approve
                        df.loc[df.change_id == row.change_id, comment_col] = comment
                        df.loc[df.change_id == row.change_id, "updated_at"]= now_str()
                        save_dc(df)
                        st.success(f"Change **{row.change_id}** approved ✅")
                        st.rerun()

                    if cb.button("❌ Reject", key=f"reject_{row.change_id}"):
                        df.loc[df.change_id == row.change_id, "status"]    = "Rejected"
                        df.loc[df.change_id == row.change_id, comment_col] = comment
                        df.loc[df.change_id == row.change_id, "updated_at"]= now_str()
                        save_dc(df)
                        st.warning(f"Change **{row.change_id}** rejected ❌")
                        st.rerun()

    with tab_all:
        st.markdown("**Full Design Change Register**")
        if df.empty:
            st.info("No design changes in the system yet.")
        else:
            show = df.copy()
            show["status"] = show["status"].apply(lambda s: f"{BADGE_ICON.get(s,'⚪')} {s}")
            st.dataframe(show, use_container_width=True, hide_index=True)

# ═══════════════════════════════════════════════════════════════════════════════
#  PAGE: TRACKING
# ═══════════════════════════════════════════════════════════════════════════════
def page_approvals():
    st.markdown("## Approvals")

    role = st.session_state.user_role
    df = load_dc()
    can_review = role in ["PMC", "Client"]

    tab_queue, tab_all = st.tabs(["My Approval Queue", "All Changes"])

    with tab_queue:
        if not can_review:
            st.info(
                "This section is visible to all stakeholders. "
                "Only PMC and Client can take approval actions."
            )
            st.markdown(f"Your current role is: **{role}**")
        elif role == "PMC":
            queue = df[df.status == "Pending"].copy()
            st.markdown(f"**PMC Review Queue** - Changes waiting for your review `{len(queue)} pending`")
            next_status_approve = "Approved"
            comment_col = "pmc_comment"
        else:
            queue = df[df.status == "Approved"].copy()
            st.markdown(
                f"**Client Final Approval Queue** - PMC-approved changes awaiting your sign-off `{len(queue)} pending`"
            )
            next_status_approve = "Implemented"
            comment_col = "client_comment"

        if can_review:
            if queue.empty:
                st.success("Your queue is empty - nothing is waiting for review.")
            else:
                for _, row in queue.iterrows():
                    with st.expander(
                        f"{row.change_id} | {row.project_name} | Element: {row.element_id} | Floor: {row.location_floor}",
                        expanded=False,
                    ):
                        st.markdown(workflow_html(row.status), unsafe_allow_html=True)
                        st.markdown("<br>", unsafe_allow_html=True)

                        c1, c2 = st.columns(2)
                        with c1:
                            st.markdown(f"**Project:** {row.project_name}")
                            st.markdown(f"**Element ID:** `{row.element_id}`")
                            st.markdown(f"**Location / Floor:** {row.location_floor}")
                        with c2:
                            st.markdown(f"**Raised By:** {row.raised_by} ({row.raised_by_role})")
                            st.markdown(f"**Submitted:** {row.created_at}")
                            st.markdown(f"**Status:** {row.status}")

                        st.markdown(f"**Description:**\n> {row.description}")

                        if row.file_name:
                            st.markdown(f"**Attached File:** `{row.file_name}`")

                        if role == "Client" and row.pmc_comment:
                            st.markdown(f"**PMC Comment:** {row.pmc_comment}")

                        comment = st.text_area(
                            "Your Comment (optional)",
                            key=f"comment_{row.change_id}",
                            placeholder="Add review notes...",
                        )

                        ca, cb, _ = st.columns([1.2, 1.2, 3])
                        approve_label = (
                            "Approve -> Implement" if role == "Client" else "Approve -> Send to Client"
                        )
                        if ca.button(approve_label, key=f"approve_{row.change_id}", type="primary"):
                            df.loc[df.change_id == row.change_id, "status"] = next_status_approve
                            df.loc[df.change_id == row.change_id, comment_col] = comment
                            df.loc[df.change_id == row.change_id, "updated_at"] = now_str()
                            save_dc(df)
                            st.success(f"Change **{row.change_id}** approved.")
                            st.rerun()

                        if cb.button("Reject", key=f"reject_{row.change_id}"):
                            df.loc[df.change_id == row.change_id, "status"] = "Rejected"
                            df.loc[df.change_id == row.change_id, comment_col] = comment
                            df.loc[df.change_id == row.change_id, "updated_at"] = now_str()
                            save_dc(df)
                            st.warning(f"Change **{row.change_id}** rejected.")
                            st.rerun()

    with tab_all:
        st.markdown("**Full Design Change Register**")
        if df.empty:
            st.info("No design changes in the system yet.")
        else:
            show = df.copy()
            show["status"] = show["status"].apply(lambda s: f"{BADGE_ICON.get(s, '')} {s}".strip())
            st.dataframe(show, use_container_width=True, hide_index=True)


def page_tracking():
    st.markdown("## 📍 Tracking Module")

    tab1, tab2, tab3 = st.tabs([
        "🏗️ Live Construction",
        "🚚 Logistics",
        "🔄 Design Changes",
    ])

    role = st.session_state.user_role

    # ── Tab 1: Live Construction ──────────────────────────────────────────────
    with tab1:
        st.markdown('<div class="section-header">Live Construction Tracking</div>', unsafe_allow_html=True)

        if role in ["Contractor", "Factory/Site", "PMC"]:
            with st.expander("➕ Log New Construction Activity"):
                with st.form("con_form"):
                    r1c1, r1c2 = st.columns(2)
                    zone        = r1c1.text_input("Zone / Floor *", placeholder="e.g. Level 3, Zone B")
                    activity    = r1c2.text_input("Activity *", placeholder="e.g. Column casting")
                    r2c1, r2c2 = st.columns(2)
                    con_status  = r2c1.selectbox("Status", ["Not Started", "In Progress", "Completed"])
                    responsible = r2c2.text_input("Responsible Stakeholder")

                    if st.form_submit_button("Add Activity"):
                        if zone.strip() and activity.strip():
                            df_con = load_con()
                            new_row = pd.DataFrame([{
                                "zone_floor":             zone.strip(),
                                "activity":               activity.strip(),
                                "status":                 con_status,
                                "responsible_stakeholder":responsible.strip(),
                                "last_update":            now_str(),
                            }])
                            df_con = pd.concat([df_con, new_row], ignore_index=True)
                            save_con(df_con)
                            st.success("✅ Activity logged!")
                            st.rerun()
                        else:
                            st.error("Zone and Activity are required.")

        df_con = load_con()
        if df_con.empty:
            st.info("No construction activities logged yet.")
        else:
            # Filter
            f_col1, f_col2 = st.columns([2, 2])
            status_filter = f_col1.multiselect(
                "Filter by Status",
                ["Not Started", "In Progress", "Completed"],
                default=["Not Started", "In Progress", "Completed"],
                key="con_filter"
            )
            filtered = df_con[df_con.status.isin(status_filter)]

            # Colour rows
            STATUS_COLOURS = {
                "Not Started": "#fff3cd",
                "In Progress": "#cfe2ff",
                "Completed":   "#d1e7dd",
            }
            def row_colour(row):
                colour = STATUS_COLOURS.get(row.status, "#ffffff")
                return [f"background-color: {colour}"] * len(row)

            if not filtered.empty:
                styled = filtered.style.apply(row_colour, axis=1)
                st.dataframe(styled, use_container_width=True, hide_index=True)
                # Summary
                ns = len(filtered[filtered.status == "Not Started"])
                ip = len(filtered[filtered.status == "In Progress"])
                cm = len(filtered[filtered.status == "Completed"])
                total_rows = len(filtered)
                prog = (cm / total_rows * 100) if total_rows else 0
                st.markdown(f"**Overall Completion:** {cm}/{total_rows} activities &nbsp; ({prog:.1f}%)")
                st.progress(prog / 100)
            else:
                st.info("No activities match your filter.")

    # ── Tab 2: Logistics ─────────────────────────────────────────────────────
    with tab2:
        st.markdown('<div class="section-header">Logistics Tracking — Prefab Material</div>', unsafe_allow_html=True)

        if role in ["Contractor", "Factory/Site", "PMC"]:
            with st.expander("➕ Add Logistics Entry"):
                with st.form("log_form"):
                    lc1, lc2 = st.columns(2)
                    comp_id      = lc1.text_input("Component ID *", placeholder="e.g. BEAM-GF-04")
                    dispatch_dt  = lc2.date_input("Dispatch Date")
                    lc3, lc4, lc5 = st.columns(3)
                    in_transit   = lc3.checkbox("In Transit")
                    delivered    = lc4.checkbox("Delivered")
                    installed    = lc5.checkbox("Installed")

                    if st.form_submit_button("Add Component"):
                        if comp_id.strip():
                            df_log = load_log()
                            new_row = pd.DataFrame([{
                                "component_id":  comp_id.strip(),
                                "dispatch_date": dispatch_dt.strftime("%Y-%m-%d"),
                                "in_transit":    "Yes" if in_transit else "No",
                                "delivered":     "Yes" if delivered  else "No",
                                "installed":     "Yes" if installed  else "No",
                            }])
                            df_log = pd.concat([df_log, new_row], ignore_index=True)
                            save_log(df_log)
                            st.success("✅ Component added!")
                            st.rerun()
                        else:
                            st.error("Component ID is required.")

        df_log = load_log()
        if df_log.empty:
            st.info("No logistics entries yet.")
        else:
            # Status column
            def log_stage(row):
                if row.installed == "Yes":  return "🟢 Installed"
                if row.delivered == "Yes":  return "🔵 Delivered"
                if row.in_transit == "Yes": return "🟡 In Transit"
                return "⚪ Dispatched"

            df_log["Stage"] = df_log.apply(log_stage, axis=1)
            st.dataframe(df_log, use_container_width=True, hide_index=True)

            # Summary counts
            sc1, sc2, sc3, sc4 = st.columns(4)
            sc1.metric("Total",      len(df_log))
            sc2.metric("In Transit", len(df_log[df_log.in_transit == "Yes"]))
            sc3.metric("Delivered",  len(df_log[df_log.delivered  == "Yes"]))
            sc4.metric("Installed",  len(df_log[df_log.installed  == "Yes"]))

    # ── Tab 3: Design Change Tracking ────────────────────────────────────────
    with tab3:
        st.markdown('<div class="section-header">Design Change Register & Status</div>', unsafe_allow_html=True)

        df_dc = load_dc()
        if df_dc.empty:
            st.info("No design changes to track.")
        else:
            # Filters row
            fc1, fc2, fc3 = st.columns([2, 2, 2])
            status_sel = fc1.multiselect(
                "Filter by Status",
                ["Pending","Approved","Rejected","Implemented","Closed"],
                default=["Pending","Approved","Implemented"],
                key="dc_status_filter"
            )
            project_list = ["All"] + df_dc.project_name.dropna().unique().tolist()
            project_sel  = fc2.selectbox("Filter by Project", project_list, key="dc_proj_filter")
            search_term  = fc3.text_input("Search Element / Change ID", key="dc_search")

            filtered = df_dc.copy()
            if status_sel:
                filtered = filtered[filtered.status.isin(status_sel)]
            if project_sel != "All":
                filtered = filtered[filtered.project_name == project_sel]
            if search_term:
                mask = (
                    filtered.element_id.str.contains(search_term, case=False, na=False) |
                    filtered.change_id.str.contains(search_term, case=False, na=False)
                )
                filtered = filtered[mask]

            track_cols = ["change_id","element_id","project_name","location_floor",
                          "raised_by","status","pmc_comment","client_comment",
                          "created_at","updated_at"]
            track_df = filtered[track_cols].copy()
            track_df.columns = [
                "Change ID","Element","Project","Location",
                "Raised By","Status","PMC Comment","Client Comment",
                "Created","Last Updated"
            ]
            track_df["Status"] = track_df["Status"].apply(lambda s: f"{BADGE_ICON.get(s,'⚪')} {s}")
            st.dataframe(track_df, use_container_width=True, hide_index=True)
            st.caption(f"Showing {len(filtered)} of {len(df_dc)} total changes")

# ═══════════════════════════════════════════════════════════════════════════════
#  PAGE: CLOSE CHANGE
# ═══════════════════════════════════════════════════════════════════════════════
def page_close():
    st.markdown("## 🔒 Close / Confirm Implementation")

    role = st.session_state.user_role
    if role not in ["Contractor", "Factory/Site"]:
        st.error("🚫 **Access Denied** — Only **Contractor** and **Factory/Site** roles can close changes.")
        st.info(f"Your current role is: **{role}**")
        return

    df = load_dc()
    impl = df[df.status == "Implemented"].copy()

    if impl.empty:
        st.info("🎉 No implemented changes awaiting closure.")
    else:
        st.markdown(f"**{len(impl)} change(s) awaiting closure confirmation:**")
        for _, row in impl.iterrows():
            with st.expander(f"📄 {row.change_id}  ·  {row.project_name}  ·  Element: {row.element_id}"):
                st.markdown(workflow_html(row.status), unsafe_allow_html=True)
                st.markdown("<br>", unsafe_allow_html=True)

                c1, c2 = st.columns(2)
                with c1:
                    st.markdown(f"**Project:** {row.project_name}")
                    st.markdown(f"**Element:** `{row.element_id}`")
                    st.markdown(f"**Location:** {row.location_floor}")
                with c2:
                    st.markdown(f"**Raised By:** {row.raised_by}")
                    st.markdown(f"**Client Comment:** {row.client_comment or '—'}")
                    st.markdown(f"**Last Updated:** {row.updated_at}")

                st.markdown(f"**Description:** {row.description}")

                if st.button(f"✅  Mark as Closed — {row.change_id}", key=f"close_{row.change_id}", type="primary"):
                    df.loc[df.change_id == row.change_id, "status"]     = "Closed"
                    df.loc[df.change_id == row.change_id, "updated_at"] = now_str()
                    save_dc(df)
                    st.success(f"Change **{row.change_id}** marked as ⚫ Closed.")
                    st.rerun()

    st.markdown("---")
    st.markdown("**All Closed Changes**")
    closed = df[df.status == "Closed"]
    if closed.empty:
        st.info("No closed changes yet.")
    else:
        show = closed[["change_id","project_name","element_id","raised_by","updated_at"]].copy()
        show.columns = ["Change ID","Project","Element","Raised By","Closed At"]
        st.dataframe(show, use_container_width=True, hide_index=True)

# ═══════════════════════════════════════════════════════════════════════════════
#  PAGE: BIM VIEWER
# ═══════════════════════════════════════════════════════════════════════════════
def page_bim():
    st.markdown("## 🧊 BIM Viewer")
    st.info("ℹ️ Lightweight placeholder BIM viewer — upload a floor plan image and select an element to visualise its change record.")

    col_ctrl, col_view = st.columns([1, 2])

    df = load_dc()

    with col_ctrl:
        st.markdown('<div class="section-header">Controls</div>', unsafe_allow_html=True)

        uploaded_image = st.file_uploader(
            "Upload Floor Plan / BIM Screenshot",
            type=["png","jpg","jpeg"],
            help="Upload any floor plan or model screenshot"
        )

        if not df.empty:
            element_opts = ["— Select element —"] + df.element_id.unique().tolist()
            selected_el  = st.selectbox("Select Element ID", element_opts)
        else:
            selected_el = None
            st.info("No design changes in system yet.")

        if selected_el and selected_el != "— Select element —":
            matched = df[df.element_id == selected_el].sort_values("created_at", ascending=False)
            if not matched.empty:
                row = matched.iloc[0]
                st.markdown("---")
                st.markdown(f"""
                <div style='background:#fff8e1; border:1px solid #ffc107;
                            border-radius:8px; padding:14px;'>
                    <b>Change Record</b><br><br>
                    🆔 <b>Change ID:</b> {row.change_id}<br>
                    📁 <b>Project:</b> {row.project_name}<br>
                    📍 <b>Location:</b> {row.location_floor}<br>
                    📝 <b>Description:</b> {row.description}<br>
                    👤 <b>Raised By:</b> {row.raised_by}<br>
                    📅 <b>Submitted:</b> {row.created_at}
                </div>
                """, unsafe_allow_html=True)

                st.markdown("<br>", unsafe_allow_html=True)

                status_colour = {
                    "Pending":"#ffc107","Approved":"#198754",
                    "Rejected":"#dc3545","Implemented":"#0dcaf0","Closed":"#6c757d"
                }.get(row.status, "#ccc")

                st.markdown(f"""
                <div style='background:{status_colour}; color:#fff;
                            padding:10px 16px; border-radius:8px;
                            font-weight:700; font-size:1rem; text-align:center;'>
                    🔴 Element Flagged: {selected_el}<br>
                    <span style='font-size:0.85rem; font-weight:400;'>
                    Status: {row.status}
                    </span>
                </div>
                """, unsafe_allow_html=True)

                if len(matched) > 1:
                    st.markdown(f"*{len(matched)} change record(s) found for this element.*")
                    st.dataframe(
                        matched[["change_id","status","raised_by","created_at"]],
                        use_container_width=True, hide_index=True
                    )

    with col_view:
        st.markdown('<div class="section-header">Visual Preview</div>', unsafe_allow_html=True)

        if uploaded_image:
            st.image(uploaded_image, caption="Uploaded Floor Plan", use_column_width=True)

            if selected_el and selected_el != "— Select element —":
                st.markdown(f"""
                <div style='border:3px solid #dc3545; background:#fff5f5;
                            border-radius:8px; padding:12px 16px; margin-top:10px;'>
                    🔴 <b>Element <code>{selected_el}</code> is highlighted</b> — active design change recorded.<br>
                    <span style='color:#6c757d; font-size:0.85rem;'>
                    In a full BIM integration, this element would be highlighted in red on the 3D model.
                    </span>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style='border:2px dashed #dee2e6; border-radius:10px;
                        height:340px; display:flex; flex-direction:column;
                        align-items:center; justify-content:center;
                        color:#adb5bd; font-size:1rem;'>
                <div style='font-size:2.5rem; margin-bottom:10px;'>📐</div>
                <div>Upload a floor plan image to start</div>
                <div style='font-size:0.82rem; margin-top:6px;'>
                    PNG or JPG — any floor plan or model screenshot
                </div>
            </div>
            """, unsafe_allow_html=True)

        # Legend
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("""
        <div style='display:flex; gap:12px; flex-wrap:wrap; font-size:0.8rem;'>
            <span>🔴 Changed Element</span>
            <span>🟡 Pending Review</span>
            <span>🟢 Approved</span>
            <span>🔵 Implemented</span>
            <span>⚫ Closed</span>
        </div>
        """, unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
#  MAIN ROUTER
# ═══════════════════════════════════════════════════════════════════════════════
def main():
    if not st.session_state.logged_in:
        page_login()
        return

    sidebar()

    page = st.session_state.current_page
    dispatch = {
        "Dashboard":              page_dashboard,
        "Create Design Change":   page_create,
        "Approvals":              page_approvals,
        "Tracking":               page_tracking,
        "Close Change":           page_close,
        "BIM Viewer":             page_bim,
    }
    fn = dispatch.get(page, page_dashboard)
    fn()


if __name__ == "__main__":
    main()
