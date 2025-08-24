import streamlit as st
from app.db import init_db, save_history, load_history
from app.ui import render_navigation, render_footer, render_profile_page, render_about_page
from app.ui import auth_ui, render_subject_grid, render_global_css, render_landing_page
from app.llm import get_api_response
from app.formatting import format_response
from app.visualization import should_show_diagram, create_smart_visualization
from app.backend import backend_save_history, backend_get_history


def main():
    init_db()
    # Inject global CSS
    try:
        render_global_css()
    except Exception:
        pass
    
    # If the user requested to see the login page (from landing), show it first
    if st.session_state.get("show_login"):
        if not auth_ui():
            return

    # If not logged in, show the rich landing page (with fallback to simple header)
    if not st.session_state.get("user_id"):
        try:
            render_landing_page()
        except Exception:
            # Fallback to simple landing if render_landing_page fails
            st.header('Edullm')
            st.write('Your virtual study companion — clear, step-by-step homework solutions.')
            if st.button('Start Learning'):
                st.session_state['show_login'] = True
                st.rerun()
        return

    # User is logged in - show navigation
    render_navigation()
    
    # Check current page (only after login)
    current_page = st.session_state.get('current_page', 'home')
    
    # Handle different pages
    if current_page == 'profile':
        render_profile_page()
        render_footer()
        return
    elif current_page == 'about':
        render_about_page()
        render_footer()
        return
    elif current_page == 'admin':
        from app.ui import admin_ui
        admin_ui()
        render_footer()
        return
    elif current_page == 'subjects':
        # Set selected_subject to None to show subject grid
        st.session_state["selected_subject"] = None

    # Stage 1: Subject-only page (full width) with gold/silver theme override
    if not st.session_state.get("selected_subject"):
        st.markdown(
            """
            <style>
            .stApp { 
                --g1: #d4af37; /* gold */
                --g2: #c0c0c0; /* silver */
                --g3: #e7cf7a; /* light gold */
                --g4: #f5f5f5; /* near white */
                background:
                    radial-gradient(circle at 80% 20%, rgba(255,255,255,0.16) 0, rgba(255,255,255,0) 40%),
                    radial-gradient(circle at 20% 70%, rgba(255,255,255,0.12) 0, rgba(255,255,255,0) 45%),
                    linear-gradient(135deg, var(--g1), var(--g2), var(--g3), var(--g4));
            }
            .subject-card { background: rgba(255,255,255,0.15); border-color: rgba(255,255,255,0.35); }
            .subject-selected { border-color: rgba(255,255,255,0.85); box-shadow: 0 0 0 2px rgba(255,255,255,0.55) inset; }
            .stButton>button { background: linear-gradient(135deg, #d4af37, #c0c0c0); }
            </style>
            """,
            unsafe_allow_html=True,
        )
        # Header for subjects page
        st.markdown("""
        <div class="main-header">
            <h1 class="brand-title" style="margin:0.25rem 0;">Edullm</h1>
            <p class="brand-sub" style="margin:0.1rem 0 0.25rem 0;">Clear, step-by-step homework solutions</p>
        </div>
        """, unsafe_allow_html=True)
        
        _ = render_subject_grid(columns=4)
        return

    # Stage 2: Question UI after subject selection
    # Header for question page
    st.markdown("""
    <div class="main-header">
        <h1 class="brand-title" style="margin:0.25rem 0;">Edullm</h1>
        <p class="brand-sub" style="margin:0.1rem 0 0.25rem 0;">Clear, step-by-step homework solutions</p>
    </div>
    """, unsafe_allow_html=True)
    
    selected_subject = st.session_state.get("selected_subject")
    top_left, top_right = st.columns([3, 1])
    with top_left:
        st.markdown(f"### ❓ Your Question — {selected_subject}")
    with top_right:
        if st.button("Change subject"):
            st.session_state["selected_subject"] = None
            st.rerun()

    question = st.text_area(
        "Enter your homework question:",
        height=120,
        placeholder=f"Ask your {selected_subject} question here...",
        help="Be specific and include all relevant details"
    )
    
    if st.button("🎯 Get Solution", type="primary"):
        if question.strip():
            with st.spinner("Getting solution..."):
                response = get_api_response(question, selected_subject)
                
                if response:
                    st.markdown("---")
                    st.markdown(f"## 📚 {selected_subject} Solution")
                    
                    # Improved formatting in a clean container
                    formatted_response = format_response(response)
                    st.markdown(f"""
                    <div class="solution-content">
                        {formatted_response}
                    </div>
                    """, unsafe_allow_html=True)
                    # Save to history (backend)
                    if backend_save_history(selected_subject, question.strip(), formatted_response):
                        pass  # Successfully saved
                    else:
                        # Fallback to local save if backend fails
                        save_history(
                            st.session_state["user_id"],
                            selected_subject,
                            question.strip(),
                            formatted_response,
                        )
                    
                    # Show diagram if needed
                    if should_show_diagram(question, selected_subject):
                        st.markdown("### 📊 Visualization")
                        viz = create_smart_visualization(question, selected_subject)
                        if viz:
                            # Display visualization at a controlled width so it doesn't stretch full container
                            st.image(viz, width=700)
                    
                    # Simple feedback
                    st.markdown("### Rate this solution")
                    col_a, col_b, col_c = st.columns(3)
                    with col_a:
                        if st.button("👍 Helpful"):
                            st.success("Thanks!")
                    with col_b:
                        if st.button("👎 Needs work"):
                            st.info("We'll improve!")
                    with col_c:
                        if st.button("🔄 Try again"):
                            st.rerun()
        else:
            st.warning("Please enter a question.")
    
    # History + footer
    with st.expander("🕘 View your recent history"):
        # Try to load from backend first, fallback to local
        rows = backend_get_history(limit=25)
        if not rows:
            rows = load_history(st.session_state["user_id"], limit=25)
        if not rows:
            st.info("No history yet.")
        else:
            for row in rows:
                # Handle both backend format (dict) and local format (tuple)
                if isinstance(row, dict):
                    subj, q, created_at = row['subject'], row['question'], row['created_at']
                else:
                    _id, subj, q, a, created_at = row
                    
                st.markdown(f"**[{created_at}] {subj}**")
                st.markdown(f"- Question: {q}")
                # Intentionally do not render the answer to reduce visual bloat and storage usage in UI
                st.markdown("---")

    # Render footer
    render_footer()


