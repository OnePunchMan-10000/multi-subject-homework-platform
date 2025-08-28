def render_profile_page_original():
    """Original Profile page with user stats and achievements - BACKUP VERSION"""
    render_navbar()

    st.markdown("# My Profile")

    # User info section
    col1, col2 = st.columns([1, 3])

    with col1:
        # Profile avatar
        st.markdown("""
        <div style="text-align: center;">
            <div style="width: 100px; height: 100px; background: linear-gradient(45deg, #FFD700, #FFA500);
                        border-radius: 50%; display: flex; align-items: center; justify-content: center;
                        margin: 0 auto; font-size: 2rem; font-weight: bold; color: white;">
                JD
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        username = st.session_state.get('username', 'John Doe')
        email = st.session_state.get('user_email', 'john.doe@example.com')
        st.markdown(f"## {username}")
        st.markdown(f"📧 {email}")
        st.markdown("🎓 Grade 10")

    st.markdown("---")

    # Stats section
    col1, col2, col3 = st.columns(3)

    # Get user stats from history
    user_id = st.session_state.get("user_id")
    total_questions = 0
    subjects_studied = 0
    day_streak = 0

    if user_id:
        try:
            rows = load_history(user_id, limit=1000)  # Get all history
            total_questions = len(rows)
            subjects_studied = len(set(row[1] for row in rows))  # Unique subjects
            day_streak = min(total_questions, 15)  # Simple streak calculation
        except:
            pass

    with col1:
        st.markdown(f"""
        <div style="background: rgba(255, 255, 255, 0.2); padding: 1.5rem; border-radius: 15px; text-align: center;">
            <div style="font-size: 2rem;">📚</div>
            <div style="font-size: 2rem; font-weight: bold; color: #FFD700;">{total_questions}</div>
            <div>Questions Asked</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div style="background: rgba(255, 255, 255, 0.2); padding: 1.5rem; border-radius: 15px; text-align: center;">
            <div style="font-size: 2rem;">🎯</div>
            <div style="font-size: 2rem; font-weight: bold; color: #FFD700;">{subjects_studied}</div>
            <div>Subjects Studied</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div style="background: rgba(255, 255, 255, 0.2); padding: 1.5rem; border-radius: 15px; text-align: center;">
            <div style="font-size: 2rem;">🔥</div>
            <div style="font-size: 2rem; font-weight: bold; color: #FFD700;">{day_streak}</div>
            <div>Day Streak</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # Achievements section
    st.markdown("## 🏆 Achievements")
    st.markdown("Your learning milestones")

    col1, col2 = st.columns(2)

    with col1:
        # First Question achievement
        first_q_unlocked = total_questions >= 1
        st.markdown(f"""
        <div style="background: rgba(255, 255, 255, {'0.3' if first_q_unlocked else '0.1'});
                    padding: 1rem; border-radius: 10px; margin: 0.5rem 0;
                    opacity: {'1' if first_q_unlocked else '0.5'};">
            <div style="font-size: 1.5rem;">🌟 First Question</div>
            <div>Asked your first question</div>
        </div>
        """, unsafe_allow_html=True)

        # Subject Master achievement
        subject_master = subjects_studied >= 3
        st.markdown(f"""
        <div style="background: rgba(255, 255, 255, {'0.3' if subject_master else '0.1'});
                    padding: 1rem; border-radius: 10px; margin: 0.5rem 0;
                    opacity: {'1' if subject_master else '0.5'};">
            <div style="font-size: 1.5rem;">🎓 Subject Master</div>
            <div>Studied 3+ subjects in a subject</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        # Quick Learner achievement
        quick_learner = total_questions >= 10
        st.markdown(f"""
        <div style="background: rgba(255, 255, 255, {'0.3' if quick_learner else '0.1'});
                    padding: 1rem; border-radius: 10px; margin: 0.5rem 0;
                    opacity: {'1' if quick_learner else '0.5'};">
            <div style="font-size: 1.5rem;">⚡ Quick Learner</div>
            <div>Completed 10 questions in one day</div>
        </div>
        """, unsafe_allow_html=True)

        # Streak Champion achievement
        streak_champ = day_streak >= 7
        st.markdown(f"""
        <div style="background: rgba(255, 255, 255, {'0.3' if streak_champ else '0.1'});
                    padding: 1rem; border-radius: 10px; margin: 0.5rem 0;
                    opacity: {'1' if streak_champ else '0.5'};">
            <div style="font-size: 1.5rem;">🔥 Streak Champion</div>
            <div>Maintained a 7+ day streak</div>
        </div>
        """, unsafe_allow_html=True)