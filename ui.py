import streamlit as st
from datetime import datetime
from collections import Counter

# ------------------ Mock Data & Functions ------------------

def get_all_incidents():
    """Return a list of mock incidents"""
    incident_data = [
        {"id": 1, "title": "SQL Server High CPU Usage on Production Node",
         "description": "CPU utilization reached above 95% on the main SQL Server instance causing query delays.",
         "priority": "P1", "comments": ["DBA restarted SQL service temporarily to reduce load.",
                                        "Identified multiple expensive queries running simultaneously.",
                                        "Users reported slow response on dashboards."]},
        {"id": 2, "title": "SQL Server DB Connection Timeout",
         "description": "Application unable to establish DB connections due to timeout error on login.", "priority": "P1",
         "comments": ["Connection pool maxed out at 1000 sessions.", "Error 10060 observed in SQL error logs.",
                      "Developers escalated issue as app downtime."]},
        {"id": 3, "title": "SQL Server I/O Bottleneck on TempDB",
         "description": "Heavy read/write contention observed on TempDB files leading to high latency.", "priority": "P1",
         "comments": ["Added additional TempDB data files to reduce contention.",
                      "High checkpoint activity observed in perfmon.", "Business reports taking 10x more time."]},
        {"id": 4, "title": "SQL Server High CPU - Long Running Queries",
         "description": "Several queries consuming CPU >80% for prolonged time on critical server.", "priority": "P2",
         "comments": ["Execution plan shows missing index warnings.", "Query tuning recommended for finance module.",
                      "Alerts triggered in monitoring system."]},
        {"id": 14, "title": "SQL Server DB Connection Reset",
         "description": "Intermittent connection resets observed between app and DB.", "priority": "P2",
         "comments": ["Checked network latency between app and DB tier.",
                      "Connection string pooling parameters under review.", "SQL Browser service status verified."]},
        {"id": 15, "title": "SQL Server I/O Bottleneck during Backup",
         "description": "Backup jobs cause high I/O utilization impacting OLTP queries.", "priority": "P3",
         "comments": ["Backup schedule moved to off-hours.", "Monitoring reports backup compression disabled.",
                      "OLTP workload faced blocking during backup."]},
        {"id": 16, "title": "SQL Server High CPU due to Statistics Update",
         "description": "Automatic statistics update caused CPU surge for 20 minutes.", "priority": "P4",
         "comments": ["Updated stats on large tables triggered CPU spike.", "DBA considering async stats update.",
                      "Monitoring reported degraded performance."]},
        {"id": 17, "title": "SQL Server DB Connection Drops due to Network Issues",
         "description": "Frequent packet drops observed causing DB connection loss.", "priority": "P1",
         "comments": ["Network team engaged to check switches.", "Dropped sessions logged in SQL error log.",
                      "Users reported sudden disconnects during transactions."]},
        {"id": 18, "title": "SQL Server Connection Pool Exhaustion",
         "description": "Too many active sessions causing pool exhaustion.", "priority": "P2",
         "comments": ["Application team asked to optimize session handling.", "Idle sessions cleaned up by DBA.",
                      "Monitoring reports multiple long-idle connections."]},
        {"id": 19, "title": "SQL Server I/O Bottleneck on Log Writes",
         "description": "Checkpoint operations blocked due to slow log writes.", "priority": "P3",
         "comments": ["Heavy insert workload caused write log contention.", "DB log backup delayed.",
                      "Perfmon log bytes flushed/sec was very low."]},
        {"id": 20, "title": "SQL Server CPU Usage from CLR Functions",
         "description": "CLR-based functions consuming CPU more than expected.", "priority": "P4",
         "comments": ["CLR assemblies under optimization review.", "CPU usage stable after disabling certain jobs.",
                      "Monitoring will continue for next 24 hours."]}
    ]
    return incident_data

def get_incident_by_id(incident_id):
    for i in get_all_incidents():
        if i['id'] == incident_id:
            return i
    return None

def call_ai_recommendation(incident):
    import json, requests
    url = 'http://localhost:8000/generate-ai-recommendation'
    try:
        query_text = incident.get('description', 'No description provided')
        data = json.dumps({"query": query_text, "log_id": f"incident_{incident.get('id', 'chat')}"})
        headers = {'Content-Type': 'application/json'}
        resp = requests.post(url, data=data, headers=headers)
        if resp.status_code == 200:
            return {'response': resp.json()}
        else:
            return {'error': f'API returned {resp.status_code}: {resp.text}'}
    except requests.exceptions.ConnectionError:
        return {'error': 'Could not connect to the AI services.'}
    except Exception as e:
        return {'error': str(e)}

# ------------------ Authentication ------------------

def login_user(username, password):
    if username == "bhuwan" and password == "password":
        st.session_state['user'] = username
        st.session_state['page'] = 'dashboard'
    else:
        st.error("Invalid credentials!")

def logout_user():
    for key in ['user', 'page', 'selected_incident', 'chat_history', 'ai_initialized', 'filter_priority']:
        if key in st.session_state:
            del st.session_state[key]

# ------------------ Streamlit App ------------------

st.set_page_config(page_title="Incident Management Dashboard", layout="wide")

if 'page' not in st.session_state:
    st.session_state['page'] = 'login'
if 'chat_history' not in st.session_state:
    st.session_state['chat_history'] = []
if 'ai_initialized' not in st.session_state:
    st.session_state['ai_initialized'] = False
if 'filter_priority' not in st.session_state:
    st.session_state['filter_priority'] = None  # default view (all incidents)

# ------------------ LOGIN PAGE ------------------
if st.session_state['page'] == 'login':
    st.title("🔐 Incident Management Portal")
    st.write("Please login to continue.")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        login_user(username, password)

# ------------------ DASHBOARD PAGE ------------------
elif st.session_state['page'] == 'dashboard':
    if st.session_state.get('user'):
        st.sidebar.success(f"Logged in as {st.session_state['user']}")
        if st.sidebar.button("Logout"):
            logout_user()
            st.rerun()

        st.title("Incident Dashboard")

        # ✅ Priority Summary Section
        incidents = get_all_incidents()
        from collections import Counter
        priority_counts = Counter(i['priority'] for i in incidents)
        priorities = sorted(priority_counts.keys())

        cols = st.columns(len(priorities) + 1)
        for idx, p in enumerate(priorities):
            color = {
                "P1": "#FF4B4B",
                "P2": "#FFA534",
                "P3": "#FFD700",
                "P4": "#4CAF50"
            }.get(p, "#CCCCCC")

            with cols[idx]:
                st.markdown(
                    f"""
                    <div style='background-color:{color}; padding:10px; border-radius:10px; text-align:center; cursor:pointer;'>
                        <h4 style='color:white; margin-bottom:0;'>{p}</h4>
                        <p style='color:white; font-size:24px; margin-top:0;'>{priority_counts[p]}</p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                if st.button(f"Show {p} Tickets", key=f"btn_{p}"):
                    st.session_state['filter_priority'] = p
                    st.rerun()

        with cols[-1]:
            if st.button("Show All Tickets"):
                st.session_state['filter_priority'] = None
                st.rerun()

        st.markdown("---")

        # ✅ Filter incidents based on priority selection
        filtered_incidents = (
            [i for i in incidents if i["priority"] == st.session_state["filter_priority"]]
            if st.session_state["filter_priority"]
            else incidents
        )

        # ✅ Incident List
        for i in filtered_incidents:
            with st.container(border=True):
                st.subheader(i['title'])
                st.write(f"**Priority:** {i['priority']}")
                st.write(f"**Description:** {i['description']}")
                if st.button(f"View Details of {i['title']}", key=f"view_{i['id']}"):
                    st.session_state['selected_incident'] = i['id']
                    st.session_state['page'] = 'details'
                    st.rerun()

# ------------------ DETAILS PAGE ------------------
elif st.session_state['page'] == 'details':
    if st.session_state['user']:
        if st.button('Logout'):
            logout_user()
            st.rerun()

    incident = get_incident_by_id(st.session_state['selected_incident'])
    if 'current_incident_id' not in st.session_state or st.session_state['current_incident_id'] != incident['id']:
        st.session_state['chat_history'] = []
        st.session_state['ai_initialized'] = False
        st.session_state['current_incident_id'] = incident['id']

    if not incident:
        st.error('Incident not found')
    else:
        st.title(f"Incident Details - {incident['title']}")
        if st.button('Back to Dashboard'):
            st.session_state['page'] = 'dashboard'
            st.session_state['selected_incident'] = None
            st.session_state['chat_history'] = []
            st.session_state['ai_initialized'] = False
            st.rerun()

        main_content_col, ai_assistant_col = st.columns([2, 1.5])

        # ------------------- Unified Ticket Details Scroll -------------------
        with main_content_col:
            st.header("Incident Information")
            with st.container(border=True, height=500):
                st.subheader(incident['title'])
                st.metric(label='Priority', value=incident['priority'])
                st.markdown("---")

                st.markdown("**Description:**")
                st.info(incident['description'])
                st.markdown("---")

                st.markdown("**Comments:**")
                if incident['comments']:
                    for i, c in enumerate(reversed(incident['comments'])):
                        st.write(f"**{datetime.now().strftime('%Y-%m-%d %H:%M')} - User {i + 1}:** {c}")
                        st.markdown("---")
                else:
                    st.markdown("_No comments recorded for this incident._")

        # ------------------- AI Assistant -------------------
        with ai_assistant_col:
            st.header('AI Assistant')
            with st.container(border=True):
                if not st.session_state['ai_initialized']:
                    if st.button('Generate AI Recommendation', use_container_width=True):
                        with st.spinner('Generating recommendation...'):
                            res = call_ai_recommendation(incident)
                            if 'error' in res:
                                st.error(f"AI API Error: {res['error']}")
                            else:
                                response = res.get('response', 'No specific recommendation provided.')
                                st.session_state['chat_history'].append({"role": "assistant", "content": response})
                                st.session_state['ai_initialized'] = True
                                st.rerun()

                if st.session_state['ai_initialized']:
                    st.markdown("---")
                    chat_display_container = st.container(height=450)
                    with chat_display_container:
                        for msg in st.session_state['chat_history']:
                            if msg["role"] == "assistant":
                                with st.chat_message("assistant"):
                                    st.write(msg["content"])
                            else:
                                with st.chat_message("user"):
                                    st.write(msg["content"])

                    # ✅ Fixed chat input display issue
                    user_input = st.chat_input("Ask a follow-up question...")
                    if user_input:
                        # show user query immediately
                        st.session_state['chat_history'].append({"role": "user", "content": user_input})

                        simulated_incident = {"description": user_input, "id": incident['id']}
                        with st.spinner("AI thinking..."):
                            res = call_ai_recommendation(simulated_incident)
                            ai_response = res.get('response', 'AI returned no response.')

                        # show AI response
                        st.session_state['chat_history'].append({"role": "assistant", "content": ai_response})
                        st.rerun()