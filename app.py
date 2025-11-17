import streamlit as st
import pandas as pd
import plotly.express as px

# --- Page Config ---
st.set_page_config(page_title="Expense Tracker", page_icon="💰")

# --- Session State ---
if 'expenses' not in st.session_state:
    st.session_state.expenses = []
if 'budget' not in st.session_state:
    st.session_state.budget = 0.0

# --- Sidebar ---
with st.sidebar:
    st.header("⚙️ Settings")
    budget_input = st.number_input(
        "Set Monthly Budget", 
        min_value=0.0, 
        value=st.session_state.budget, 
        step=100.0
    )
    
    if st.button("Update Budget"):
        st.session_state.budget = budget_input
        st.success("Budget Updated!")

    st.divider()
    if st.button("Clear All Data"):
        st.session_state.expenses = []
        st.rerun()

st.title("💰 Personal Expense Tracker")

# --- Input Form (Always Visible) ---
with st.expander("➕ Add New Expense", expanded=True):
    with st.form("expense_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Description")
        with col2:
            amount = st.number_input("Amount", min_value=0.01, step=1.0)
        category = st.selectbox("Category", ["Food", "Transport", "Utilities", "Entertainment", "Shopping", "Other"])
        
        if st.form_submit_button("Add Expense"):
            if name and amount > 0:
                st.session_state.expenses.append({
                    "Description": name, 
                    "Amount": amount, 
                    "Category": category
                })
                st.success("Added!")
            else:
                st.warning("Please fill in all fields.")

# --- Data Processing ---
if st.session_state.expenses:
    df = pd.DataFrame(st.session_state.expenses)
    total_spent = df["Amount"].sum()
else:
    df = pd.DataFrame(columns=["Description", "Amount", "Category"])
    total_spent = 0.0

remaining = st.session_state.budget - total_spent

# --- TABS ---
tab1, tab2 = st.tabs(["📊 Dashboard", "🥧 Analysis"])

# TAB 1: Overview
with tab1:
    # Metrics
    c1, c2, c3 = st.columns(3)
    c1.metric("Budget", f"${st.session_state.budget:,.2f}")
    c2.metric("Spent", f"${total_spent:,.2f}")
    c3.metric("Remaining", f"${remaining:,.2f}", delta=remaining)

    # Progress Bar
    if st.session_state.budget > 0:
        progress = min(total_spent / st.session_state.budget, 1.0)
        st.progress(progress)
        if total_spent > st.session_state.budget:
            st.error("⚠️ Budget Exceeded!")

    # Recent Transactions
    st.subheader("Recent Transactions")
    if not df.empty:
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No expenses yet.")

# TAB 2: Analysis (Pie Chart)
with tab2:
    st.subheader("Expense Breakdown")
    
    if not df.empty:
        # 1. Create the Pie Chart
        fig = px.pie(
            df, 
            values='Amount', 
            names='Category', 
            title='Spending by Category',
            hole=0.4, # Makes it a donut chart
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        # Display Pie Chart
        st.plotly_chart(fig, use_container_width=True)

        # 2. Category Statistics Text
        st.divider()
        
        # Group by category to find highest spender
        category_group = df.groupby("Category")["Amount"].sum().sort_values(ascending=False)
        top_category = category_group.index[0]
        top_amount = category_group.iloc[0]
        
        col_a, col_b = st.columns(2)
        with col_a:
            st.info(f"**Highest Spending:** {top_category} (${top_amount:,.2f})")
        with col_b:
            count = len(df)
            avg = total_spent / count
            st.info(f"**Average per Transaction:** ${avg:,.2f}")

    else:
        st.info("Add expenses to see the analysis.")
