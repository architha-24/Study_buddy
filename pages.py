import streamlit as st
from datetime import datetime
from database import *
from utils import *

def show_learn_summarize_page():
    st.header("📖 Learn & Summarize")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        user_text = st.text_area("Paste your study material:", height=200, 
                               placeholder="Enter your notes, textbook content, or any study material here...")
        
        num_points = st.slider("Summarize into how many key points?", min_value=3, max_value=10, value=5)
        
        if st.button("🎯 Generate Smart Summary", type="primary"):
            if user_text.strip() == "":
                st.warning("Please enter some text first!")
            else:
                with st.spinner("Analyzing and creating simple summary..."):
                    points = generate_smart_summary(user_text, num_points)
                    
                    st.subheader("✨ Simple & Clear Summary")
                    st.success("Here are the main points in simple language:")
                    
                    for i, point in enumerate(points, 1):
                        st.write(f"**{i}.** {point}")
                    
                    if points:
                        summary_topic = f"Summary - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
                        summary_content = "**Key Points:**\n\n" + "\n".join([f"• {point}" for point in points])
                        st.session_state.current_note_topic = summary_topic
                        st.session_state.current_note_content = summary_content
                        
                        st.info("💡 **Summary ready!** Go to 'My Notes' to save these points and add your own thoughts.")
    
    with col2:
        st.subheader("💡 Study Guide")
        st.info("""
        **How to use this effectively:**
        
        1. **Paste** your study material
        2. **Generate** key points summary
        3. **Write notes** in your own words
        4. **Review** regularly
        
        **Pro Tip:** Use the summary as a starting point for your personal notes!
        """)

def show_notes_page():
    st.header("📝 My Personal Notes")
    
    notes = load_personal_notes(st.session_state.user_id)
    
    st.subheader("✍️ Write New Note")
    
    with st.form("note_form"):
        topic = st.text_input("Note Topic/Title:", 
                            value=st.session_state.current_note_topic,
                            placeholder="e.g., Python Functions Summary")
        content = st.text_area("Your Notes:", 
                             height=300,
                             value=st.session_state.current_note_content,
                             placeholder="Write your understanding, key insights, or reflections here...")
        
        col1, col2 = st.columns(2)
        with col1:
            save_btn = st.form_submit_button("💾 Save Note")
        with col2:
            if st.session_state.current_note_id:
                delete_btn = st.form_submit_button("🗑️ Delete Note")
            else:
                delete_btn = False
        
        if save_btn:
            if topic.strip() and content.strip():
                if st.session_state.current_note_id:
                    if update_personal_note(st.session_state.current_note_id, topic, content, st.session_state.user_id):
                        st.success("✅ Note updated successfully!")
                        st.session_state.current_note_id = None
                        st.session_state.current_note_topic = ""
                        st.session_state.current_note_content = ""
                        st.rerun()
                    else:
                        st.error("Failed to update note")
                else:
                    if save_personal_note(topic, content, st.session_state.user_id):
                        st.success("✅ Note saved successfully!")
                        st.session_state.current_note_topic = ""
                        st.session_state.current_note_content = ""
                        st.rerun()
                    else:
                        st.error("Failed to save note")
            else:
                st.warning("Please enter both topic and content")
        
        if delete_btn and st.session_state.current_note_id:
            if delete_personal_note(st.session_state.current_note_id, st.session_state.user_id):
                st.success("✅ Note deleted successfully!")
                st.session_state.current_note_id = None
                st.session_state.current_note_topic = ""
                st.session_state.current_note_content = ""
                st.rerun()
            else:
                st.error("Failed to delete note")
    
    if notes:
        st.subheader("📚 Your Saved Notes")
        for note in notes:
            with st.expander(f"📄 {note['topic']} (Last modified: {note['last_modified']})"):
                st.write(note['content'])
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.caption(f"Created: {note['created_date']}")
                with col2:
                    if st.button("Edit", key=f"edit_{note['id']}"):
                        st.session_state.current_note_id = note['id']
                        st.session_state.current_note_topic = note['topic']
                        st.session_state.current_note_content = note['content']
                        st.rerun()
    else:
        st.info("📝 You haven't created any notes yet. Start by writing your first note above!")

def show_goals_page():
    st.header("🎯 Study Goals")

    goals = load_study_goals(st.session_state.user_id)
    
    with st.form("add_goal", clear_on_submit=True):
        goal = st.text_input("Enter your study goal:")
        submitted = st.form_submit_button("Add Goal")
        if submitted:
            if goal.strip():
                if add_study_goal(goal, st.session_state.user_id):
                    st.success("🎯 Goal added successfully!")
                    st.rerun()
                else:
                    st.error("Failed to add goal. Please try again.")
            else:
                st.warning("Please enter a valid goal.")

    if not goals:
        st.info("📝 No goals set yet. Add your first study goal above!")
    else:
        st.subheader("Your Study Goals")
        for goal in goals:
            status = "✅" if goal['completed'] else "⏳"
            cols = st.columns([4, 1, 1])
            
            with cols[0]:
                st.write(f"{status} **{goal['goal']}**")
                st.caption(f"Created: {goal['created_date']}")
            
            with cols[1]:
                if not goal['completed']:
                    if st.button("Mark Done", key=f"done_{goal['id']}"):
                        if mark_goal_complete(goal['id'], st.session_state.user_id):
                            st.success("✅ Goal completed!")
                            st.rerun()
                        else:
                            st.error("Failed to update goal.")
            
            with cols[2]:
                if st.button("Delete", key=f"del_{goal['id']}"):
                    if delete_goal(goal['id'], st.session_state.user_id):
                        st.success("🗑️ Goal deleted!")
                        st.rerun()
                    else:
                        st.error("Failed to delete goal.")
            
            st.markdown("---")

def show_progress_page():
    st.header("📈 Progress Dashboard")
    
    goals = load_study_goals(st.session_state.user_id)
    sessions = load_study_sessions(st.session_state.user_id)
    notes = load_personal_notes(st.session_state.user_id)
    
    st.subheader(f"📊 {st.session_state.username}'s Progress")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_goals = len(goals)
        completed_goals = sum(1 for g in goals if g['completed'])
        st.metric("Study Goals", f"{completed_goals}/{total_goals}")
    
    with col2:
        total_notes = len(notes)
        st.metric("Personal Notes", total_notes)
    
    with col3:
        total_sessions = len(sessions)
        st.metric("Study Sessions", total_sessions)
    
    with col4:
        if goals:
            completion_rate = (completed_goals / total_goals) * 100 if total_goals > 0 else 0
            st.metric("Goal Completion", f"{completion_rate:.1f}%")
        else:
            st.metric("Goal Completion", "0%")
    
    if goals:
        st.subheader("🎯 Goal Progress")
        completion_rate = (completed_goals / total_goals) * 100
        st.progress(int(completion_rate))
        st.write(f"**{completed_goals} out of {total_goals} goals completed** ({completion_rate:.1f}%)")
        
        if completed_goals > 0:
            st.write("### ✅ Completed Goals")
            for goal in goals:
                if goal['completed']:
                    st.write(f"• {goal['goal']}")
        
        pending_goals = [g for g in goals if not g['completed']]
        if pending_goals:
            st.write("### ⏳ Pending Goals")
            for goal in pending_goals:
                st.write(f"• {goal['goal']}")
    
    if notes:
        st.subheader("📝 Recent Notes")
        for note in notes[:5]:
            st.write(f"**{note['topic']}** - {note['last_modified']}")
    
    if not goals and not notes:
        st.info("📊 Start setting goals and taking notes to see your progress here!")

def show_tips_page():
    st.header("💡 Smart Study Tips")
    tips = get_study_tips()
    
    st.write("### Effective Learning Strategies")
    for i, tip in enumerate(tips, 1):
        st.write(f"**{i}.** {tip}")
    
    st.info("💪 **Remember**: Consistent practice and smart strategies lead to better learning outcomes!")