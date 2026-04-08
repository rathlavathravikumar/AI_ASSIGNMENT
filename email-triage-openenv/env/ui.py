"""
Email Triage UI - A beautiful, animated interface for the Email Triage environment.
"""

import streamlit as st
import time
from typing import Dict, Any
from env.environment import EmailTriageEnv
from env.models import Action, ActionType, Category, Priority, FlagType


# Custom CSS for stunning visuals and animations
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    * {
        font-family: 'Inter', sans-serif;
    }

    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        text-align: center;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        animation: fadeInUp 0.8s ease-out;
    }

    .email-card {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        border-left: 4px solid #667eea;
        transition: all 0.3s ease;
        animation: slideInRight 0.6s ease-out;
    }

    .email-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.15);
    }

    .priority-urgent {
        border-left-color: #e74c3c;
        background: linear-gradient(135deg, #ffeaa7 0%, #fab1a0 100%);
    }

    .priority-normal {
        border-left-color: #f39c12;
        background: linear-gradient(135deg, #fff3cd 0%, #ffeaa7 100%);
    }

    .priority-low {
        border-left-color: #27ae60;
        background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%);
    }

    .action-button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.8rem 1.5rem;
        border-radius: 8px;
        font-weight: 500;
        transition: all 0.3s ease;
        margin: 0.5rem;
        cursor: pointer;
    }

    .action-button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
    }

    .action-button:disabled {
        background: #bdc3c7;
        cursor: not-allowed;
        transform: none;
    }

    .score-display {
        background: linear-gradient(135deg, #2ecc71 0%, #27ae60 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        font-size: 1.2rem;
        font-weight: 600;
        margin: 1rem 0;
        animation: bounceIn 0.8s ease-out;
    }

    .sidebar-content {
        background: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        margin-bottom: 1rem;
    }

    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }

    @keyframes slideInRight {
        from {
            opacity: 0;
            transform: translateX(30px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }

    @keyframes bounceIn {
        0% {
            opacity: 0;
            transform: scale(0.3);
        }
        50% {
            opacity: 1;
            transform: scale(1.05);
        }
        70% {
            transform: scale(0.9);
        }
        100% {
            opacity: 1;
            transform: scale(1);
        }
    }

    .stButton>button {
        width: 100%;
    }

    .email-subject {
        font-size: 1.1rem;
        font-weight: 600;
        color: #2c3e50;
        margin-bottom: 0.5rem;
    }

    .email-sender {
        color: #7f8c8d;
        font-size: 0.9rem;
        margin-bottom: 0.5rem;
    }

    .email-body {
        color: #34495e;
        line-height: 1.5;
        margin-bottom: 1rem;
    }

    .action-panel {
        background: #ecf0f1;
        padding: 1.5rem;
        border-radius: 10px;
        margin-top: 1rem;
    }

    .stats-card {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        margin: 0.5rem 0;
        text-align: center;
    }

    .stats-number {
        font-size: 2rem;
        font-weight: bold;
        color: #667eea;
    }

    .stats-label {
        color: #7f8c8d;
        font-size: 0.9rem;
    }
</style>
""", unsafe_allow_html=True)


class EmailTriageUI:
    def __init__(self):
        self.env = EmailTriageEnv()
        self.current_task = None
        self.score = 0.0
        self.actions_taken = 0

    def initialize_session_state(self):
        """Initialize session state variables"""
        if 'env_state' not in st.session_state:
            st.session_state.env_state = None
        if 'current_task' not in st.session_state:
            st.session_state.current_task = None
        if 'score' not in st.session_state:
            st.session_state.score = 0.0
        if 'actions_taken' not in st.session_state:
            st.session_state.actions_taken = 0
        if 'game_started' not in st.session_state:
            st.session_state.game_started = False

    def start_new_task(self, task_id: str):
        """Start a new task"""
        try:
            observation = self.env.reset(task_id)
            st.session_state.env_state = self.env.state()
            st.session_state.current_task = task_id
            st.session_state.score = 0.0
            st.session_state.actions_taken = 0
            st.session_state.game_started = True
            return observation
        except Exception as e:
            st.error(f"Error starting task: {str(e)}")
            return None

    def take_action(self, action: Action):
        """Take an action in the environment"""
        try:
            observation, reward, done, info = self.env.step(action)
            st.session_state.env_state = self.env.state()
            st.session_state.score += reward.value
            st.session_state.actions_taken += 1
            return observation, reward, done, info
        except Exception as e:
            st.error(f"Error taking action: {str(e)}")
            return None, None, None, None

    def render_email_card(self, email, index):
        """Render an email card with animations"""
        priority_class = f"priority-{email.priority.lower()}" if hasattr(email, 'priority') else ""

        st.markdown(f"""
        <div class="email-card {priority_class}" style="animation-delay: {index * 0.1}s">
            <div class="email-subject">{email.subject}</div>
            <div class="email-sender">From: {email.sender} &lt;{email.sender_email}&gt;</div>
            <div class="email-body">{email.body[:200]}{'...' if len(email.body) > 200 else ''}</div>
        </div>
        """, unsafe_allow_html=True)

    def render_action_panel(self):
        """Render the action selection panel"""
        st.markdown('<div class="action-panel">', unsafe_allow_html=True)
        st.subheader("📋 Take Action")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown("**Priority**")
            priority = st.selectbox(
                "Set Priority",
                [p.value for p in Priority],
                key="priority_select"
            )

            st.markdown("**Category**")
            category = st.selectbox(
                "Set Category",
                [c.value for c in Category],
                key="category_select"
            )

        with col2:
            st.markdown("**Flag Type**")
            flag_type = st.selectbox(
                "Set Flag",
                ["None"] + [f.value for f in FlagType],
                key="flag_select"
            )

            action_type = st.selectbox(
                "Action Type",
                [a.value for a in ActionType],
                key="action_select"
            )

        with col3:
            if st.button("🚀 Execute Action", key="execute_btn", help="Execute the selected action"):
                # Build action based on selections
                action_data = {"action_type": action_type}

                if action_type == "classify":
                    action_data.update({
                        "priority": priority,
                        "category": category
                    })
                elif action_type == "flag":
                    if flag_type != "None":
                        action_data["flag_type"] = flag_type
                    else:
                        st.error("Please select a flag type")
                        return

                action = Action(**action_data)
                observation, reward, done, info = self.take_action(action)

                if observation:
                    if reward.value != 0:
                        st.success(f"Action completed! Reward: {reward.value:.3f}")
                        st.info(reward.reason)

                    if done:
                        st.balloons()
                        st.success("🎉 Task completed!")
                        time.sleep(2)
                        st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)

    def render_stats(self):
        """Render statistics panel"""
        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown("""
            <div class="stats-card">
                <div class="stats-number">{:.3f}</div>
                <div class="stats-label">Current Score</div>
            </div>
            """.format(st.session_state.score), unsafe_allow_html=True)

        with col2:
            st.markdown("""
            <div class="stats-card">
                <div class="stats-number">{}</div>
                <div class="stats-label">Actions Taken</div>
            </div>
            """.format(st.session_state.actions_taken), unsafe_allow_html=True)

        with col3:
            emails_processed = len(st.session_state.env_state.get('processed_emails', [])) if st.session_state.env_state else 0
            total_emails = len(st.session_state.env_state.get('inbox', [])) + emails_processed if st.session_state.env_state else 0

            st.markdown("""
            <div class="stats-card">
                <div class="stats-number">{}/</div>
                <div class="stats-label">Emails Processed</div>
            </div>
            """.format(emails_processed, total_emails), unsafe_allow_html=True)

    def render_main_interface(self):
        """Render the main UI interface"""
        st.markdown("""
        <div class="main-header">
            <h1>📧 Email Triage Assistant</h1>
            <p>AI-powered email management with beautiful animations</p>
        </div>
        """, unsafe_allow_html=True)

        # Task selection
        if not st.session_state.game_started:
            st.markdown('<div class="sidebar-content">', unsafe_allow_html=True)
            st.subheader("🎯 Select Task")

            task_options = ["task_1", "task_2", "task_3"]
            task_descriptions = [
                "Easy: Priority & Category Classification",
                "Medium: Full Email Management",
                "Hard: Complex Multi-step Triage"
            ]

            selected_task = st.selectbox(
                "Choose your challenge:",
                task_options,
                format_func=lambda x: f"{x.upper()}: {task_descriptions[int(x.split('_')[1])-1]}"
            )

            if st.button("🚀 Start Task", key="start_task"):
                observation = self.start_new_task(selected_task)
                if observation:
                    st.success(f"Task {selected_task.upper()} started!")
                    time.sleep(1)
                    st.rerun()

            st.markdown('</div>', unsafe_allow_html=True)
        else:
            # Game interface
            col1, col2 = st.columns([3, 1])

            with col1:
                st.subheader("📬 Inbox")

                if st.session_state.env_state and 'inbox' in st.session_state.env_state:
                    inbox = st.session_state.env_state['inbox']
                    if inbox:
                        for i, email in enumerate(inbox):
                            self.render_email_card(email, i)
                    else:
                        st.info("🎉 All emails processed!")

                # Action panel
                if st.session_state.env_state and 'inbox' in st.session_state.env_state and st.session_state.env_state['inbox']:
                    self.render_action_panel()

            with col2:
                st.subheader("📊 Statistics")
                self.render_stats()

                st.markdown('<div class="sidebar-content">', unsafe_allow_html=True)
                if st.button("🔄 New Task", key="new_task"):
                    st.session_state.game_started = False
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

    def run(self):
        """Main application runner"""
        self.initialize_session_state()
        self.render_main_interface()


def main():
    st.set_page_config(
        page_title="Email Triage Assistant",
        page_icon="📧",
        layout="wide",
        initial_sidebar_state="collapsed"
    )

    ui = EmailTriageUI()
    ui.run()


if __name__ == "__main__":
    main()</content>
<parameter name="filePath">/home/rgukt-basar/email-triage-openenv/env/ui.py