import streamlit as st
import random
import time
import pandas as pd
import matplotlib.pyplot as plt

from quiz import QuizApp
from questions_data import python_questions, sql_questions, java_questions

# ---------------- CONFIG ----------------
st.set_page_config(page_title="Quiz Application", page_icon="📝")

# ---------------- SESSION STATE ----------------
defaults = {
    "logged_in": False,
    "username": "",
    "q_index": 0,
    "score": 0,
    "start_time": None,
    "shuffled_questions": False
}

for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ---------------- BACKEND ----------------
app = QuizApp()
app.add_subject("Python", python_questions)
app.add_subject("SQL", sql_questions)
app.add_subject("Java", java_questions)

st.title("📝 Online Quiz Application")

# ---------------- LOGOUT ----------------
if st.session_state.logged_in:
    if st.sidebar.button("Logout"):
        st.session_state.clear()
        st.rerun()

# ---------------- LOGIN / REGISTER ----------------
if not st.session_state.logged_in:
    tab1, tab2 = st.tabs(["Login", "Register"])

    with tab1:
        user = st.text_input("Username")
        pwd = st.text_input("Password", type="password")

        if st.button("Login"):
            if app.login(user, pwd):
                st.session_state.logged_in = True
                st.session_state.username = user
                st.rerun()
            else:
                st.error("Invalid credentials")

    with tab2:
        new_user = st.text_input("New Username")
        new_pass = st.text_input("New Password", type="password")

        if st.button("Register"):
            if app.register(new_user, new_pass):
                st.success("Registered successfully! Please login")

# ---------------- QUIZ ----------------
else:
    st.sidebar.success(f"Welcome {st.session_state.username}")
    subject = st.sidebar.selectbox("Select Subject", list(app.subjects.keys()))
    quiz = app.subjects[subject]
    total_q = len(quiz.questions)

    # Shuffle questions ONCE
    if not st.session_state.shuffled_questions:
        random.shuffle(quiz.questions)
        st.session_state.start_time = time.time()
        st.session_state.shuffled_questions = True

    # Progress
    st.progress(st.session_state.q_index / total_q)

    # ---------------- QUESTIONS ----------------
    if st.session_state.q_index < total_q:
        q = quiz.questions[st.session_state.q_index]

        st.subheader(f"Question {st.session_state.q_index + 1} of {total_q}")
        st.write(q.text)

        # ---- FIX: shuffle options ONCE per question ----
        opt_key = f"options_{st.session_state.q_index}"
        radio_key = f"radio_{st.session_state.q_index}"

        if opt_key not in st.session_state:
            opts = q.options.copy()
            random.shuffle(opts)
            st.session_state[opt_key] = opts

        selected = st.radio(
            "Choose an option:",
            st.session_state[opt_key],
            index=None,
            key=radio_key
        )

        submit = st.button("Submit Answer", disabled=selected is None)

        if submit:
            if q.check_answer(selected[0]):
                st.success("Correct 🎉")
                st.session_state.score += 1
            else:
                st.error(f"Wrong ❌ Correct Answer: {q.answer}")

            # cleanup option state
            del st.session_state[opt_key]

            st.session_state.q_index += 1
            st.rerun()

    # ---------------- RESULTS ----------------
    else:
        elapsed = int(time.time() - st.session_state.start_time)
        correct = st.session_state.score
        wrong = total_q - correct
        percentage = (correct / total_q) * 100

        st.subheader("🎯 Quiz Completed")
        st.success(f"Score: {correct}/{total_q}")
        st.write(f"Percentage: **{percentage:.2f}%**")
        st.info(f"⏱ Time Taken: {elapsed} seconds")

        # Pass / Fail
        if percentage >= 60:
            st.success("✅ Status: PASS")
        else:
            st.error("❌ Status: FAIL")

        # Save score
        app.save_score(
            st.session_state.username,
            subject,
            correct,
            total_q
        )

        # ---------------- VISUALIZATION ----------------
        st.subheader("📊 Result Analysis")

        df = pd.DataFrame({
            "Result": ["Correct", "Wrong"],
            "Count": [correct, wrong]
        }).set_index("Result")

        st.bar_chart(df)

        fig, ax = plt.subplots()
        ax.pie(
            [correct, wrong],
            labels=["Correct", "Wrong"],
            autopct="%1.1f%%",
            startangle=90
        )
        ax.set_title("Quiz Result Distribution")
        st.pyplot(fig)

        # Restart
        if st.button("Restart Quiz"):
            for key in list(st.session_state.keys()):
                if key.startswith(("options_", "radio_")):
                    del st.session_state[key]

            st.session_state.q_index = 0
            st.session_state.score = 0
            st.session_state.start_time = None
            st.session_state.shuffled_questions = False
            st.rerun()
