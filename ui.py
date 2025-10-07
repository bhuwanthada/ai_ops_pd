# # import json
# #
# # import streamlit as st
# # import requests
# # from datetime import datetime
# #
# # # -----------------------------# Sample incident data (20 incidents)# -----------------------------
# # incident_data = [
# #     {"id": 1, "title": "SQL Server High CPU Usage on Production Node",
# #      "description": "CPU utilization reached above 95% on the main SQL Server instance causing query delays.",
# #      "priority": "P1", "comments": ["DBA restarted SQL service temporarily to reduce load.",
# #                                     "Identified multiple expensive queries running simultaneously.",
# #                                     "Users reported slow response on dashboards."]},
# #     {"id": 2, "title": "SQL Server DB Connection Timeout",
# #      "description": "Application unable to establish DB connections due to timeout error on login.", "priority": "P1",
# #      "comments": ["Connection pool maxed out at 1000 sessions.", "Error 10060 observed in SQL error logs.",
# #                   "Developers escalated issue as app downtime."]},
# #     {"id": 3, "title": "SQL Server I/O Bottleneck on TempDB",
# #      "description": "Heavy read/write contention observed on TempDB files leading to high latency.", "priority": "P1",
# #      "comments": ["Added additional TempDB data files to reduce contention.",
# #                   "High checkpoint activity observed in perfmon.", "Business reports taking 10x more time."]},
# #     {"id": 4, "title": "SQL Server High CPU - Long Running Queries",
# #      "description": "Several queries consuming CPU >80% for prolonged time on critical server.", "priority": "P2",
# #      "comments": ["Execution plan shows missing index warnings.", "Query tuning recommended for finance module.",
# #                   "Alerts triggered in monitoring system."]},
# #     {"id": 14, "title": "SQL Server DB Connection Reset",
# #      "description": "Intermittent connection resets observed between app and DB.", "priority": "P2",
# #      "comments": ["Checked network latency between app and DB tier.",
# #                   "Connection string pooling parameters under review.", "SQL Browser service status verified."]},
# #     {"id": 15, "title": "SQL Server I/O Bottleneck during Backup",
# #      "description": "Backup jobs cause high I/O utilization impacting OLTP queries.", "priority": "P3",
# #      "comments": ["Backup schedule moved to off-hours.", "Monitoring reports backup compression disabled.",
# #                   "OLTP workload faced blocking during backup."]},
# #     {"id": 16, "title": "SQL Server High CPU due to Statistics Update",
# #      "description": "Automatic statistics update caused CPU surge for 20 minutes.", "priority": "P4",
# #      "comments": ["Updated stats on large tables triggered CPU spike.", "DBA considering async stats update.",
# #                   "Monitoring reported degraded performance."]},
# #     {"id": 17, "title": "SQL Server DB Connection Drops due to Network Issues",
# #      "description": "Frequent packet drops observed causing DB connection loss.", "priority": "P1",
# #      "comments": ["Network team engaged to check switches.", "Dropped sessions logged in SQL error log.",
# #                   "Users reported sudden disconnects during transactions."]},
# #     {"id": 18, "title": "SQL Server Connection Pool Exhaustion",
# #      "description": "Too many active sessions causing pool exhaustion.", "priority": "P2",
# #      "comments": ["Application team asked to optimize session handling.", "Idle sessions cleaned up by DBA.",
# #                   "Monitoring reports multiple long-idle connections."]},
# #     {"id": 19, "title": "SQL Server I/O Bottleneck on Log Writes",
# #      "description": "Checkpoint operations blocked due to slow log writes.", "priority": "P3",
# #      "comments": ["Heavy insert workload caused write log contention.", "DB log backup delayed.",
# #                   "Perfmon log bytes flushed/sec was very low."]},
# #     {"id": 20, "title": "SQL Server CPU Usage from CLR Functions",
# #      "description": "CLR-based functions consuming CPU more than expected.", "priority": "P4",
# #      "comments": ["CLR assemblies under optimization review.", "CPU usage stable after disabling certain jobs.",
# #                   "Monitoring will continue for next 24 hours."]}
# # ]  # -----------------------------# Session State Initialization# -----------------------------
# # if 'users' not in st.session_state:
# #     st.session_state['users'] = {'admin': {'password': 'admin', 'full_name': 'Administrator'}}
# #
# # if 'view' not in st.session_state:
# #     st.session_state['view'] = 'login'
# #
# # if 'user' not in st.session_state:
# #     st.session_state['user'] = None
# #
# # if 'selected_priority' not in st.session_state:
# #     st.session_state['selected_priority'] = 'P1'
# #
# # if 'selected_incident' not in st.session_state:
# #     st.session_state['selected_incident'] = None
# #
# # st.session_state['incidents'] = incident_data
# #
# # if 'page' not in st.session_state:
# #     st.session_state['page'] = 'login'
# # # NEW: State for AI Chat
# # if 'chat_history' not in st.session_state:
# #     st.session_state['chat_history'] = []
# # if 'ai_initialized' not in st.session_state:
# #     st.session_state['ai_initialized'] = False
# #
# #
# # # -----------------------------# Helper Functions# -----------------------------
# #
# # def login_user(username, password):
# #     users = st.session_state['users']
# #     if username in users and users[username]['password'] == password:
# #         st.session_state['user'] = {'username': username, 'full_name': users[username].get('full_name', username)}
# #         st.session_state['page'] = 'dashboard'
# #         return True
# #     return False
# #
# #
# # def signup_user(username, password, full_name=''):
# #     users = st.session_state['users']
# #     if username in users:
# #         return False, 'User already exists.'
# #     users[username] = {'password': password, 'full_name': full_name}
# #     st.session_state['users'] = users
# #     return True, 'Signup successful. Please login.'
# #
# #
# # def logout_user():
# #     st.session_state['user'] = None
# #     st.session_state['page'] = 'login'
# #
# #
# # def get_counts_by_priority():
# #     counts = {'P1': 0, 'P2': 0, 'P3': 0, 'P4': 0}
# #     for i in st.session_state['incidents']:
# #         counts[i['priority']] += 1
# #     return counts
# #
# #
# # def get_incidents_by_priority(priority):
# #     return [i for i in st.session_state['incidents'] if i['priority'] == priority]
# #
# #
# # def get_incident_by_id(incident_id):
# #     for i in st.session_state['incidents']:
# #         if str(i['id']) == str(incident_id):
# #             return i
# #     return None
# #
# #
# # def call_ai_recommendation(incident):
# #     # This helper function is designed to take an incident object (or a dictionary
# #     # that simulates one, with a 'description' key)
# #     url = 'http://localhost:8000/generate-ai-recommendation'
# #     try:
# #         # Use the description field for the query
# #         query_text = incident.get('description', 'No description provided')
# #         data = json.dumps({"query": query_text, "log_id": f"incident_{incident.get('id', 'chat')}"})
# #
# #         # NOTE: headers are often required for JSON posting
# #         headers = {'Content-Type': 'application/json'}
# #         resp = requests.post(url, data=data, headers=headers)
# #         if resp.status_code == 200:
# #             # We assume the response JSON has a key like 'response' for the AI text
# #             response_data = resp.json()
# #             return {'response': response_data}
# #         else:
# #             return {'error': f'API returned {resp.status_code}: {resp.text}'}
# #     except requests.exceptions.ConnectionError:
# #         return {'error': 'Could not connect to the AI services.'}
# #     except Exception as e:
# #         return {'error': str(e)}
# #
# #
# # # -----------------------------# Pages# -----------------------------
# #
# # if st.session_state['page'] == 'login':
# #     st.title('Login')
# #     with st.form('login_form'):
# #         username = st.text_input('Username')
# #         password = st.text_input('Password', type='password')
# #         login_btn = st.form_submit_button('Login')
# #         signup_btn = st.form_submit_button('Signup')
# #
# #     if signup_btn:
# #         st.session_state['page'] = 'signup'
# #         st.rerun()
# #
# #     if login_btn:
# #         if login_user(username.strip(), password):
# #             st.success('Login successful')
# #             st.rerun()
# #         else:
# #             st.error('Invalid username or password')
# #
# # elif st.session_state['page'] == 'signup':
# #     st.title('Signup')
# #     with st.form('signup_form'):
# #         full_name = st.text_input('Full Name')
# #         username = st.text_input('Username')
# #         password = st.text_input('Password', type='password')
# #         confirm = st.text_input('Confirm Password', type='password')
# #         create_btn = st.form_submit_button('Create Account')
# #         back_btn = st.form_submit_button('Back to Login')
# #
# #     if back_btn:
# #         st.session_state['page'] = 'login'
# #         st.rerun()
# #
# #     if create_btn:
# #         if password != confirm:
# #             st.error('Passwords do not match')
# #         else:
# #             ok, msg = signup_user(username.strip(), password, full_name.strip())
# #             if ok:
# #                 st.success(msg)
# #                 st.session_state['page'] = 'login'
# #                 st.rerun()
# #             else:
# #                 st.error(msg)
# #
# # elif st.session_state['page'] == 'dashboard':
# #     st.title('Incident Dashboard')
# #     if st.session_state['user']:
# #         if st.button('Logout'):
# #             logout_user()
# #             st.rerun()
# #
# #     # 1. Box for Priority Summary (Requested functionality 1: create various boxes)
# #     st.header("Open Incidents counts with priorities")
# #     with st.container(border=True):
# #         counts = get_counts_by_priority()
# #         cols = st.columns(4)
# #         for idx, p in enumerate(['P1', 'P2', 'P3', 'P4']):
# #             with cols[idx]:
# #                 # Use st.metric for a clean display of counts
# #                 # st.metric(label=f"{p}", value=counts[p])
# #                 if st.button(f'{p}: {counts[p]}', use_container_width=True):
# #                     st.session_state['selected_priority'] = p
# #
# #     st.markdown("---")
# #
# #     # 2. Box for Incident List (Requested functionality 1: create various boxes)
# #     st.header(f"Open Tickets - {st.session_state['selected_priority']}")
# #     with st.container(border=True):
# #         incidents_for_display = get_incidents_by_priority(st.session_state['selected_priority'])
# #
# #         if incidents_for_display:
# #             for inc in incidents_for_display:
# #                 col_id, col_title, col_view = st.columns([1, 6, 2])
# #                 col_id.write(f"ID: **{inc['id']}**")
# #                 col_title.write(f"{inc['title']}")
# #
# #                 if col_view.button('View Details', key=f"btn_dash_{inc['id']}", use_container_width=True):
# #                     st.session_state['selected_incident'] = inc['id']
# #                     st.session_state['page'] = 'details'
# #                     st.rerun()
# #                 st.markdown("---")  # Visual separator
# #         else:
# #             st.info(f"No incidents found for Priority {st.session_state['selected_priority']}")
# #
# #
# # elif st.session_state['page'] == 'details':
# #     if st.session_state['user']:
# #         if st.button('Logout'):
# #             logout_user()
# #             st.rerun()
# #
# #     incident = get_incident_by_id(st.session_state['selected_incident'])
# #
# #     # Reset chat state if user navigates back and forth
# #     if 'current_incident_id' not in st.session_state or st.session_state['current_incident_id'] != incident['id']:
# #         st.session_state['chat_history'] = []
# #         st.session_state['ai_initialized'] = False
# #         st.session_state['current_incident_id'] = incident['id']
# #
# #     if not incident:
# #         st.error('Incident not found')
# #     else:
# #         st.title(f"Incident Details - {incident['title']}")
# #         if st.button('Back to Dashboard'):
# #             st.session_state['page'] = 'dashboard'
# #             st.session_state['selected_incident'] = None
# #             st.session_state['chat_history'] = []
# #             st.session_state['ai_initialized'] = False
# #             st.rerun()
# #
# #         # Define columns: Main Details (3 parts) and AI Assistant (1 part)
# #         main_content_col, ai_assistant_col = st.columns([3, 1])
# #
# #         # ------------------- 1. Incident Details (BIG BOX - Requested functionality 2) -------------------
# #         with main_content_col:
# #             st.header("Incident Information")
# #             # Use a single large container to cover all primary incident sections
# #             with st.container(border=True):
# #
# #                 # Title and Priority
# #                 st.subheader(incident['title'])
# #                 st.metric(label='Priority', value=incident['priority'])
# #                 st.markdown("---")
# #
# #                 # Description Section
# #                 with st.expander("Detailed Description", expanded=True):
# #                     st.info(incident['description'])
# #
# #                 # Comments Section
# #                 st.subheader('Comments History')
# #                 # Use a smaller scrollable container for comments within the big box
# #                 comment_container = st.container(height=300, border=True)
# #                 with comment_container:
# #                     if incident['comments']:
# #                         # FIX: The original error (f' - ') is fixed here by including the variable {}
# #                         for i, c in enumerate(reversed(incident['comments'])):
# #                             # Simulating a timestamp and user for better presentation
# #                             st.write(f"**{datetime.now().strftime('%Y-%m-%d %H:%M')} - User {i + 1}: {c}**")
# #                             st.markdown("---")
# #                     else:
# #                         st.markdown("_No comments recorded for this incident._")
# #
# #         # ------------------- 2. AI Recommendation/Chat (Right Panel Box) -------------------
# #         with ai_assistant_col:
# #             st.header('AI Assistant')
# #             with st.container(border=True):  # Separate container for the AI section
# #
# #                 # 1. Initial Recommendation Button
# #                 if not st.session_state['ai_initialized']:
# #                     if st.button('Generate AI Recommendation', key='gen_ai_rec'):
# #                         with st.spinner('Please wait..'):
# #                             res = call_ai_recommendation(incident)
# #
# #                             if 'error' in res:
# #                                 st.error(f"AI API Error: {res['error']}")
# #                             else:
# #                                 response = res.get('response', 'No specific recommendation provided.')
# #
# #                                 st.session_state['chat_history'].append(
# #                                     {"role": "AI", "content": response}
# #                                 )
# #                                 st.session_state['ai_initialized'] = True
# #                                 st.rerun()
# #
# #                 # 2. Display Chat History (if initialized)
# #                 if st.session_state['ai_initialized']:
# #                     st.markdown("---")
# #
# #                     # Display history (Scrollable if too long)
# #                     chat_display_container = st.container(height=400)
# #                     with chat_display_container:
# #                         for message in st.session_state['chat_history']:
# #                             if message["role"] == "AI":
# #                                 with st.chat_message("assistant"):
# #                                     st.write(message["content"])
# #                             else:
# #                                 with st.chat_message("user"):
# #                                     st.write(message["content"])
# #
# #                     # 3. Chat Input Box for follow-up
# #                     user_input = st.chat_input("Ask a follow-up question...")
# #
# #                     if user_input:
# #                         # Add user query to history
# #                         st.session_state['chat_history'].append(
# #                             {"role": "User", "content": user_input}
# #                         )
# #
# #                         # Create a dummy incident object for the API call (passing the query as description)
# #                         simulated_incident = {"description": user_input, "id": incident['id']}
# #
# #                         with st.spinner("AI thinking..."):
# #                             res = call_ai_recommendation(simulated_incident)
# #
# #                             if 'error' in res:
# #                                 ai_response = f"Sorry, the AI encountered an error: {res['error']}"
# #                             else:
# #                                 ai_response = res.get('response', 'AI provided an unstructured response.')
# #
# #                         # Add AI response to history
# #                         st.session_state['chat_history'].append(
# #                             {"role": "AI", "content": ai_response}
# #                         )
# #                         st.rerun()
# ######################################################
# ######################################################
# ######################################################
# ######################################################
#
# # import json
# #
# # import streamlit as st
# # import requests
# # from datetime import datetime
# # # -----------------------------# Sample incident data (20 incidents)# -----------------------------
# # incident_data = [
# #     {"id": 1, "title": "SQL Server High CPU Usage on Production Node",
# #      "description": "CPU utilization reached above 95% on the main SQL Server instance causing query delays.",
# #      "priority": "P1", "comments": ["DBA restarted SQL service temporarily to reduce load.",
# #                                     "Identified multiple expensive queries running simultaneously.",
# #                                     "Users reported slow response on dashboards."]},
# #     {"id": 2, "title": "SQL Server DB Connection Timeout",
# #      "description": "Application unable to establish DB connections due to timeout error on login.", "priority": "P1",
# #      "comments": ["Connection pool maxed out at 1000 sessions.", "Error 10060 observed in SQL error logs.",
# #                   "Developers escalated issue as app downtime."]},
# #     {"id": 3, "title": "SQL Server I/O Bottleneck on TempDB",
# #      "description": "Heavy read/write contention observed on TempDB files leading to high latency.", "priority": "P1",
# #      "comments": ["Added additional TempDB data files to reduce contention.",
# #                   "High checkpoint activity observed in perfmon.", "Business reports taking 10x more time."]},
# #     {"id": 4, "title": "SQL Server High CPU - Long Running Queries",
# #      "description": "Several queries consuming CPU >80% for prolonged time on critical server.", "priority": "P2",
# #      "comments": ["Execution plan shows missing index warnings.", "Query tuning recommended for finance module.",
# #                   "Alerts triggered in monitoring system."]},
# #     {"id": 14, "title": "SQL Server DB Connection Reset",
# #      "description": "Intermittent connection resets observed between app and DB.", "priority": "P2",
# #      "comments": ["Checked network latency between app and DB tier.",
# #                   "Connection string pooling parameters under review.", "SQL Browser service status verified."]},
# #     {"id": 15, "title": "SQL Server I/O Bottleneck during Backup",
# #      "description": "Backup jobs cause high I/O utilization impacting OLTP queries.", "priority": "P3",
# #      "comments": ["Backup schedule moved to off-hours.", "Monitoring reports backup compression disabled.",
# #                   "OLTP workload faced blocking during backup."]},
# #     {"id": 16, "title": "SQL Server High CPU due to Statistics Update",
# #      "description": "Automatic statistics update caused CPU surge for 20 minutes.", "priority": "P4",
# #      "comments": ["Updated stats on large tables triggered CPU spike.", "DBA considering async stats update.",
# #                   "Monitoring reported degraded performance."]},
# #     {"id": 17, "title": "SQL Server DB Connection Drops due to Network Issues",
# #      "description": "Frequent packet drops observed causing DB connection loss.", "priority": "P1",
# #      "comments": ["Network team engaged to check switches.", "Dropped sessions logged in SQL error log.",
# #                   "Users reported sudden disconnects during transactions."]},
# #     {"id": 18, "title": "SQL Server Connection Pool Exhaustion",
# #      "description": "Too many active sessions causing pool exhaustion.", "priority": "P2",
# #      "comments": ["Application team asked to optimize session handling.", "Idle sessions cleaned up by DBA.",
# #                   "Monitoring reports multiple long-idle connections."]},
# #     {"id": 19, "title": "SQL Server I/O Bottleneck on Log Writes",
# #      "description": "Checkpoint operations blocked due to slow log writes.", "priority": "P3",
# #      "comments": ["Heavy insert workload caused write log contention.", "DB log backup delayed.",
# #                   "Perfmon log bytes flushed/sec was very low."]},
# #     {"id": 20, "title": "SQL Server CPU Usage from CLR Functions",
# #      "description": "CLR-based functions consuming CPU more than expected.", "priority": "P4",
# #      "comments": ["CLR assemblies under optimization review.", "CPU usage stable after disabling certain jobs.",
# #                   "Monitoring will continue for next 24 hours."]}
# # ]  # -----------------------------# Session State Initialization# -----------------------------
# # if 'users' not in st.session_state:
# #     st.session_state['users'] = {'admin': {'password': 'admin', 'full_name': 'Administrator'}}
# #
# # if 'view' not in st.session_state:
# #     st.session_state['view'] = 'login'
# #
# # if 'user' not in st.session_state:
# #     st.session_state['user'] = None
# #
# # if 'selected_priority' not in st.session_state:
# #     st.session_state['selected_priority'] = 'P1'
# #
# # if 'selected_incident' not in st.session_state:
# #     st.session_state['selected_incident'] = None
# #
# # st.session_state['incidents'] = incident_data
# #
# # if 'page' not in st.session_state:
# #     st.session_state['page'] = 'login'# NEW: State for AI Chat
# # if 'chat_history' not in st.session_state:
# #     st.session_state['chat_history'] = []
# # if 'ai_initialized' not in st.session_state:
# #     st.session_state['ai_initialized'] = False
# #
# # # -----------------------------# Helper Functions# -----------------------------
# #
# # def login_user(username, password):
# #     users = st.session_state['users']
# #     if username in users and users[username]['password'] == password:
# #         st.session_state['user'] = {'username': username, 'full_name': users[username].get('full_name', username)}
# #         st.session_state['page'] = 'dashboard'
# #         return True
# #     return False
# #
# #
# # def signup_user(username, password, full_name=''):
# #     users = st.session_state['users']
# #     if username in users:
# #         return False, 'User already exists.'
# #     users[username] = {'password': password, 'full_name': full_name}
# #     st.session_state['users'] = users
# #     return True, 'Signup successful. Please login.'
# #
# #
# # def logout_user():
# #     st.session_state['user'] = None
# #     st.session_state['page'] = 'login'
# #
# #
# # def get_counts_by_priority():
# #     counts = {'P1': 0, 'P2': 0, 'P3': 0, 'P4': 0}
# #     for i in st.session_state['incidents']:
# #         counts[i['priority']] += 1
# #     return counts
# #
# #
# # def get_incidents_by_priority(priority):
# #     return [i for i in st.session_state['incidents'] if i['priority'] == priority]
# #
# #
# # def get_incident_by_id(incident_id):
# #     for i in st.session_state['incidents']:
# #         if str(i['id']) == str(incident_id):
# #             return i
# #     return None
# #
# #
# # def call_ai_recommendation(incident):
# #     # This helper function is designed to take an incident object (or a dictionary
# #     # that simulates one, with a 'description' key)
# #     try:
# #         url = 'http://localhost:8000/generate-ai-recommendation'
# #         # Use the description field for the query
# #         query_text = incident.get('description', 'No description provided')
# #         data = json.dumps({"query": query_text, "log_id": f"incident_{incident.get('id', 'chat')}"})
# #
# #         # NOTE: headers are often required for JSON posting
# #         headers = {'Content-Type': 'application/json'}
# #         resp = requests.post(url, data=data, headers=headers)
# #         if resp.status_code == 200:
# #             # We assume the response JSON has a key like 'response' for the AI text
# #             response_data = resp.json()
# #             return {'response': response_data}
# #         else:
# #             return {'error': f'API returned {resp.status_code}: {resp.text}'}
# #     except requests.exceptions.ConnectionError:
# #         return {'error': 'Could not connect to the AI services.'}
# #     except Exception as e:
# #         return {'error': str(e)}
# #
# # # -----------------------------# Pages# -----------------------------
# #
# # if st.session_state['page'] == 'login':
# #     st.title('Login')
# #     with st.form('login_form'):
# #         username = st.text_input('Username')
# #         password = st.text_input('Password', type='password')
# #         login_btn = st.form_submit_button('Login')
# #         signup_btn = st.form_submit_button('Signup')
# #
# #     if signup_btn:
# #         st.session_state['page'] = 'signup'
# #         st.rerun()
# #
# #     if login_btn:
# #         if login_user(username.strip(), password):
# #             st.success('Login successful')
# #             st.rerun()
# #         else:
# #             st.error('Invalid username or password')
# #
# # elif st.session_state['page'] == 'signup':
# #     st.title('Signup')
# #     with st.form('signup_form'):
# #         full_name = st.text_input('Full Name')
# #         username = st.text_input('Username')
# #         password = st.text_input('Password', type='password')
# #         confirm = st.text_input('Confirm Password', type='password')
# #         create_btn = st.form_submit_button('Create Account')
# #         back_btn = st.form_submit_button('Back to Login')
# #
# #     if back_btn:
# #         st.session_state['page'] = 'login'
# #         st.rerun()
# #
# #     if create_btn:
# #         if password != confirm:
# #             st.error('Passwords do not match')
# #         else:
# #             ok, msg = signup_user(username.strip(), password, full_name.strip())
# #             if ok:
# #                 st.success(msg)
# #                 st.session_state['page'] = 'login'
# #                 st.rerun()
# #             else:
# #                 st.error(msg)
# #
# # elif st.session_state['page'] == 'dashboard':
# #     st.title('Incident Dashboard')
# #     if st.session_state['user']:
# #         if st.button('Logout'):
# #             logout_user()
# #             st.rerun()
# #
# #     # 1. Box for Priority Summary (Requested functionality 1: create various boxes)
# #     st.header("Open Incidents counts with priorities")
# #     with st.container(border=True):
# #         counts = get_counts_by_priority()
# #         cols = st.columns(4)
# #         for idx, p in enumerate(['P1', 'P2', 'P3', 'P4']):
# #             with cols[idx]:
# #                 if st.button(f'{p}: {counts[p]}', use_container_width=True):
# #                     st.session_state['selected_priority'] = p
# #
# #     st.markdown("---")
# #
# #     # 2. Box for Incident List (Requested functionality 1: create various boxes)
# #     st.header(f"Open Tickets - {st.session_state['selected_priority']}")
# #     with st.container(border=True):
# #         incidents_for_display = get_incidents_by_priority(st.session_state['selected_priority'])
# #
# #         if incidents_for_display:
# #             for inc in incidents_for_display:
# #                 col_id, col_title, col_view = st.columns([1, 6, 2])
# #                 col_id.write(f"ID: **{inc['id']}**")
# #                 col_title.write(f"{inc['title']}")
# #
# #                 if col_view.button('View Details', key=f"btn_dash_{inc['id']}", use_container_width=True):
# #                     st.session_state['selected_incident'] = inc['id']
# #                     st.session_state['page'] = 'details'
# #                     st.rerun()
# #                 st.markdown("---")  # Visual separator
# #         else:
# #             st.info(f"No incidents found for Priority {st.session_state['selected_priority']}")
# #
# #
# # elif st.session_state['page'] == 'details':
# #     if st.session_state['user']:
# #         if st.button('Logout'):
# #             logout_user()
# #             st.rerun()
# #
# #     incident = get_incident_by_id(st.session_state['selected_incident'])
# #
# #     # Reset chat state if user navigates back and forth
# #     if 'current_incident_id' not in st.session_state or st.session_state['current_incident_id'] != incident['id']:
# #         st.session_state['chat_history'] = []
# #         st.session_state['ai_initialized'] = False
# #         st.session_state['current_incident_id'] = incident['id']
# #
# #     if not incident:
# #         st.error('Incident not found')
# #     else:
# #         st.title(f"Incident Details - {incident['title']}")
# #         if st.button('Back to Dashboard'):
# #             st.session_state['page'] = 'dashboard'
# #             st.session_state['selected_incident'] = None
# #             st.session_state['chat_history'] = []
# #             st.session_state['ai_initialized'] = False
# #             st.rerun()
# #
# #         # Define columns: Main Details (2 parts) and AI Assistant (1 part)
# #         # CHANGED: Ratio adjusted from [3, 1] to [2, 1] to make the AI Assistant column wider.
# #         main_content_col, ai_assistant_col = st.columns([2, 1])
# #
# #         # ------------------- 1. Incident Details (BIG BOX - Requested functionality 2) -------------------
# #         with main_content_col:
# #             st.header("Incident Information")
# #             # Use a single large container to cover all primary incident sections
# #             with st.container(border=True):
# #
# #                 # Title and Priority
# #                 st.subheader(incident['title'])
# #                 st.metric(label='Priority', value=incident['priority'])
# #                 st.markdown("---")
# #
# #                 # Description Section
# #                 with st.expander("Detailed Description", expanded=True):
# #                     st.info(incident['description'])
# #
# #                 # Comments Section
# #                 st.subheader('Comments History')
# #                 # Use a smaller scrollable container for comments within the big box
# #                 comment_container = st.container(height=300, border=True)
# #                 with comment_container:
# #                     if incident['comments']:
# #                         # FIX: The original error (f' - ') is fixed here by including the variable {}
# #                         for i, c in enumerate(reversed(incident['comments'])):
# #                             # Simulating a timestamp and user for better presentation
# #                             st.write(f"**{datetime.now().strftime('%Y-%m-%d %H:%M')} - User {i + 1}: **")
# #                             st.markdown("---")
# #                     else:
# #                         st.markdown("_No comments recorded for this incident._")
# #
# #         # ------------------- 2. AI Recommendation/Chat (Right Panel Box) -------------------
# #         with ai_assistant_col:
# #             st.header('AI Assistant')
# #             with st.container(border=True):  # Separate container for the AI section
# #                 # 1. Initial Recommendation Button
# #                 if not st.session_state['ai_initialized']:
# #                     if st.button('Generate AI Recommendation', key='gen_ai_rec'):
# #                         with st.spinner('Please wait..'):
# #                             res = call_ai_recommendation(incident)
# #
# #                             if 'error' in res:
# #                                 st.error(f"AI API Error: {res['error']}")
# #                             else:
# #                                 response = res.get('response', 'No specific recommendation provided.')
# #
# #                                 st.session_state['chat_history'].append(
# #                                     {"role": "AI", "content": response}
# #                                 )
# #                                 st.session_state['ai_initialized'] = True
# #                                 st.rerun()
# #
# #                 # 2. Display Chat History (if initialized)
# #                 if st.session_state['ai_initialized']:
# #                     st.markdown("---")
# #
# #                     # Display history (Scrollable if too long)
# #                     chat_display_container = st.container(height=400)
# #                     with chat_display_container:
# #                         for message in st.session_state['chat_history']:
# #                             if message["role"] == "AI":
# #                                 with st.chat_message("assistant"):
# #                                     st.write(message["content"])
# #                             else:
# #                                 with st.chat_message("user"):
# #                                     st.write(message["content"])
# #
# #                     # 3. Chat Input Box for follow-up
# #                     user_input = st.chat_input("Ask a follow-up question...")
# #
# #                     if user_input:
# #                         # Add user query to history
# #                         st.session_state['chat_history'].append(
# #                             {"role": "User", "content": user_input}
# #                         )
# #
# #                         # Create a dummy incident object for the API call (passing the query as description)
# #                         simulated_incident = {"description": user_input, "id": incident['id']}
# #
# #                         with st.spinner("AI thinking..."):
# #                             res = call_ai_recommendation(simulated_incident)
# #
# #                             if 'error' in res:
# #                                 ai_response = f"Sorry, the AI encountered an error: {res['error']}"
# #                             else:
# #                                 ai_response = res.get('response', 'AI provided an unstructured response.')
# #
# #                         # Add AI response to history
# #                         st.session_state['chat_history'].append(
# #                             {"role": "AI", "content": ai_response}
# #                         )
# #                         st.rerun()
#
# import streamlit as st
# from datetime import datetime
# from collections import Counter
#
# # ------------------ Mock Data & Functions ------------------
#
# def get_all_incidents():
#     """Return a list of mock incidents"""
#     incident_data = [
#         {"id": 1, "title": "SQL Server High CPU Usage on Production Node",
#          "description": "CPU utilization reached above 95% on the main SQL Server instance causing query delays.",
#          "priority": "P1", "comments": ["DBA restarted SQL service temporarily to reduce load.",
#                                         "Identified multiple expensive queries running simultaneously.",
#                                         "Users reported slow response on dashboards."]},
#         {"id": 2, "title": "SQL Server DB Connection Timeout",
#          "description": "Application unable to establish DB connections due to timeout error on login.", "priority": "P1",
#          "comments": ["Connection pool maxed out at 1000 sessions.", "Error 10060 observed in SQL error logs.",
#                       "Developers escalated issue as app downtime."]},
#         {"id": 3, "title": "SQL Server I/O Bottleneck on TempDB",
#          "description": "Heavy read/write contention observed on TempDB files leading to high latency.", "priority": "P1",
#          "comments": ["Added additional TempDB data files to reduce contention.",
#                       "High checkpoint activity observed in perfmon.", "Business reports taking 10x more time."]},
#         {"id": 4, "title": "SQL Server High CPU - Long Running Queries",
#          "description": "Several queries consuming CPU >80% for prolonged time on critical server.", "priority": "P2",
#          "comments": ["Execution plan shows missing index warnings.", "Query tuning recommended for finance module.",
#                       "Alerts triggered in monitoring system."]},
#         {"id": 14, "title": "SQL Server DB Connection Reset",
#          "description": "Intermittent connection resets observed between app and DB.", "priority": "P2",
#          "comments": ["Checked network latency between app and DB tier.",
#                       "Connection string pooling parameters under review.", "SQL Browser service status verified."]},
#         {"id": 15, "title": "SQL Server I/O Bottleneck during Backup",
#          "description": "Backup jobs cause high I/O utilization impacting OLTP queries.", "priority": "P3",
#          "comments": ["Backup schedule moved to off-hours.", "Monitoring reports backup compression disabled.",
#                       "OLTP workload faced blocking during backup."]},
#         {"id": 16, "title": "SQL Server High CPU due to Statistics Update",
#          "description": "Automatic statistics update caused CPU surge for 20 minutes.", "priority": "P4",
#          "comments": ["Updated stats on large tables triggered CPU spike.", "DBA considering async stats update.",
#                       "Monitoring reported degraded performance."]},
#         {"id": 17, "title": "SQL Server DB Connection Drops due to Network Issues",
#          "description": "Frequent packet drops observed causing DB connection loss.", "priority": "P1",
#          "comments": ["Network team engaged to check switches.", "Dropped sessions logged in SQL error log.",
#                       "Users reported sudden disconnects during transactions."]},
#         {"id": 18, "title": "SQL Server Connection Pool Exhaustion",
#          "description": "Too many active sessions causing pool exhaustion.", "priority": "P2",
#          "comments": ["Application team asked to optimize session handling.", "Idle sessions cleaned up by DBA.",
#                       "Monitoring reports multiple long-idle connections."]},
#         {"id": 19, "title": "SQL Server I/O Bottleneck on Log Writes",
#          "description": "Checkpoint operations blocked due to slow log writes.", "priority": "P3",
#          "comments": ["Heavy insert workload caused write log contention.", "DB log backup delayed.",
#                       "Perfmon log bytes flushed/sec was very low."]},
#         {"id": 20, "title": "SQL Server CPU Usage from CLR Functions",
#          "description": "CLR-based functions consuming CPU more than expected.", "priority": "P4",
#          "comments": ["CLR assemblies under optimization review.", "CPU usage stable after disabling certain jobs.",
#                       "Monitoring will continue for next 24 hours."]}
#     ]
#     return incident_data
#
# def get_incident_by_id(incident_id):
#     for i in get_all_incidents():
#         if i['id'] == incident_id:
#             return i
#     return None
#
# def call_ai_recommendation(incident):
#     import json, requests
#     url = 'http://localhost:8000/generate-ai-recommendation'
#     try:
#         query_text = incident.get('description', 'No description provided')
#         data = json.dumps({"query": query_text, "log_id": f"incident_{incident.get('id', 'chat')}"})
#         headers = {'Content-Type': 'application/json'}
#         resp = requests.post(url, data=data, headers=headers)
#         import pdb;pdb.set_trace()
#         if resp.status_code == 200:
#             return {'response': resp.json()}
#         else:
#             return {'error': f'API returned {resp.status_code}: {resp.text}'}
#     except requests.exceptions.ConnectionError:
#         return {'error': 'Could not connect to the AI services.'}
#     except Exception as e:
#         return {'error': str(e)}
#
# # ------------------ Authentication ------------------
#
# def login_user(username, password):
#     if username == "bhuwan" and password == "password":
#         st.session_state['user'] = username
#         st.session_state['page'] = 'dashboard'
#     else:
#         st.error("Invalid credentials!")
#
# def logout_user():
#     for key in ['user', 'page', 'selected_incident', 'chat_history', 'ai_initialized', 'filter_priority']:
#         if key in st.session_state:
#             del st.session_state[key]
#
# # ------------------ Streamlit App ------------------
#
# st.set_page_config(page_title="Incident Management Dashboard", layout="wide")
#
# if 'page' not in st.session_state:
#     st.session_state['page'] = 'login'
# if 'chat_history' not in st.session_state:
#     st.session_state['chat_history'] = []
# if 'ai_initialized' not in st.session_state:
#     st.session_state['ai_initialized'] = False
# if 'filter_priority' not in st.session_state:
#     st.session_state['filter_priority'] = None  # default view (all incidents)
#
# # ------------------ LOGIN PAGE ------------------
# if st.session_state['page'] == 'login':
#     st.title("Incident Management Portal")
#     st.write("Please login to continue.")
#     username = st.text_input("Username")
#     password = st.text_input("Password", type="password")
#     if st.button("Login"):
#         login_user(username, password)
#
# # ------------------ DASHBOARD PAGE ------------------
# elif st.session_state['page'] == 'dashboard':
#     if st.session_state.get('user'):
#         st.sidebar.success(f"Logged in as {st.session_state['user']}")
#         if st.sidebar.button("Logout"):
#             logout_user()
#             st.rerun()
#
#         st.title("Incident Dashboard")
#
#         # ✅ Priority Summary Section
#         incidents = get_all_incidents()
#         priority_counts = Counter(i['priority'] for i in incidents)
#         priorities = sorted(priority_counts.keys())
#
#         cols = st.columns(len(priorities) + 1)
#         for idx, p in enumerate(priorities):
#             color = {
#                 "P1": "#FF4B4B",
#                 "P2": "#FFA534",
#                 "P3": "#FFD700",
#                 "P4": "#4CAF50"
#             }.get(p, "#CCCCCC")
#
#             # clickable button for filter
#             with cols[idx]:
#                 st.markdown(
#                     f"""
#                     <div style='background-color:{color}; padding:10px; border-radius:10px; text-align:center; cursor:pointer;'>
#                         <h4 style='color:white; margin-bottom:0;'>{p}{":"}{priority_counts[p]}</h4>
#                     </div>
#                     """,
#                     unsafe_allow_html=True
#                 )
#                 if st.button(f"click here", key=f"btn_{p}"
#                              ):
#                     st.session_state['filter_priority'] = p
#                     st.rerun()
#
#         with cols[-1]:
#             if st.button("Show All Tickets"):
#                 st.session_state['filter_priority'] = None
#                 st.rerun()
#
#         st.markdown("---")
#
#         # ✅ Filter incidents based on priority selection
#         filtered_incidents = (
#             [i for i in incidents if i["priority"] == st.session_state["filter_priority"]]
#             if st.session_state["filter_priority"]
#             else incidents
#         )
#
#         # ✅ Incident List
#         for i in filtered_incidents:
#             with st.container(border=True):
#                 st.subheader(i['title'])
#                 st.write(f"**Priority:** {i['priority']}")
#                 st.write(f"**Description:** {i['description']}")
#                 if st.button(f"View Details of {i['title']}", key=f"view_{i['id']}"):
#                     st.session_state['selected_incident'] = i['id']
#                     st.session_state['page'] = 'details'
#                     st.rerun()
#
# # ------------------ DETAILS PAGE ------------------
# elif st.session_state['page'] == 'details':
#     if st.session_state['user']:
#         if st.button('Logout'):
#             logout_user()
#             st.rerun()
#
#     incident = get_incident_by_id(st.session_state['selected_incident'])
#     if 'current_incident_id' not in st.session_state or st.session_state['current_incident_id'] != incident['id']:
#         st.session_state['chat_history'] = []
#         st.session_state['ai_initialized'] = False
#         st.session_state['current_incident_id'] = incident['id']
#
#     if not incident:
#         st.error('Incident not found')
#     else:
#         st.title(f"Incident Details - {incident['title']}")
#         if st.button('Back to Dashboard'):
#             st.session_state['page'] = 'dashboard'
#             st.session_state['selected_incident'] = None
#             st.session_state['chat_history'] = []
#             st.session_state['ai_initialized'] = False
#             st.rerun()
#
#         main_content_col, ai_assistant_col = st.columns([2, 1.5])
#
#         # ------------------- Unified Ticket Details Scroll -------------------
#         with main_content_col:
#             st.header("Incident Information")
#             with st.container(border=True, height=500):
#                 st.subheader(incident['title'])
#                 st.metric(label='Priority', value=incident['priority'])
#                 st.markdown("---")
#
#                 st.markdown("**Description:**")
#                 st.info(incident['description'])
#                 st.markdown("---")
#
#                 st.markdown("**Comments:**")
#                 if incident['comments']:
#                     for i, c in enumerate(reversed(incident['comments'])):
#                         st.write(f"**{datetime.now().strftime('%Y-%m-%d %H:%M')} - User {i + 1}:** {c}")
#                         st.markdown("---")
#                 else:
#                     st.markdown("_No comments recorded for this incident._")
#
#         # ------------------- AI Assistant -------------------
#         with ai_assistant_col:
#             st.header('AI Assistant')
#             with st.container(border=True):
#                 if not st.session_state['ai_initialized']:
#                     if st.button('Generate AI Recommendation', use_container_width=True):
#                         with st.spinner('Generating recommendation...'):
#                             res = call_ai_recommendation(incident)
#                             if 'error' in res:
#                                 st.error(f"AI API Error: {res['error']}")
#                             else:
#                                 response = res.get('response', 'No specific recommendation provided.')
#                                 st.session_state['chat_history'].append({"role": "AI", "content": response})
#                                 st.session_state['ai_initialized'] = True
#                                 st.rerun()
#
#                 if st.session_state['ai_initialized']:
#                     st.markdown("---")
#                     chat_display_container = st.container(height=450)
#                     with chat_display_container:
#                         for msg in st.session_state['chat_history']:
#                             if msg["role"] == "AI":
#                                 with st.chat_message("assistant"):
#                                     st.write(msg["content"])
#                             else:
#                                 with st.chat_message("user"):
#                                     st.write(msg["content"])
#
#                     user_input = st.chat_input("Ask a follow-up question...")
#                     if user_input:
#                         st.session_state['chat_history'].append({"role": "User", "content": user_input})
#                         simulated_incident = {"description": user_input, "id": incident['id']}
#                         with st.spinner("AI thinking..."):
#                             res = call_ai_recommendation(simulated_incident)
#                             ai_response = res.get('response', 'provided suggestions based upon previous '
#                                                               'incidents history. Hence no new comments.')
#                         st.session_state['chat_history'].append({"role": "AI", "content": ai_response})
#                         st.rerun()
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