import streamlit as st
import pandas as pd

# --- Page Config ---
st.set_page_config(page_title="Expense Tracker", page_icon="💰")

# --- Session State Initialization ---
# This keeps the data alive as long as the browser tab is open
if 'expenses' not in st.session_state:
    st.session_state.expenses = []
if 'budget' not in st.session_state:
    st.session_state.budget = 0.0

# --- Sidebar: Budget Settings ---
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
        st.success(f"Budget set to ${budget_input:,.2f}")

    st.divider()
    
    # Option to clear data
    if st.button("Clear All Data"):
        st.session_state.expenses = []
        st.rerun()

# --- Main Page ---
st.title("💰 Personal Expense Tracker")

# 1. Input Form
with st.expander("➕ Add New Expense", expanded=True):
    with st.form("expense_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("Description (e.g., Groceries)")
        with col2:
            amount = st.number_input("Amount", min_value=0.01, step=1.0)
            
        category = st.selectbox(
            "Category", 
            ["Food", "Transport", "Utilities", "Entertainment", "Shopping", "Other"]
        )
        
        submitted = st.form_submit_button("Add Expense")
        
        if submitted:
            if name and amount > 0:
                new_expense = {
                    "Description": name,
                    "Amount": amount,
                    "Category": category
                }
                st.session_state.expenses.append(new_expense)
                st.success("Expense added!")
            else:
                st.warning("Please enter a description and a valid amount.")

# --- Calculations ---
if st.session_state.expenses:
    df = pd.DataFrame(st.session_state.expenses)
    total_spent = df["Amount"].sum()
else:
    df = pd.DataFrame(columns=["Description", "Amount", "Category"])
    total_spent = 0.0

remaining = st.session_state.budget - total_spent

# --- Dashboard Metrics ---
st.divider()
m1, m2, m3 = st.columns(3)

m1.metric("Total Budget", f"${st.session_state.budget:,.2f}")
m2.metric("Total Spent", f"${total_spent:,.2f}")
m3.metric(
    "Remaining", 
    f"${remaining:,.2f}", 
    delta=f"{remaining:,.2f}", 
    delta_color="normal"
)

# --- Progress Bar ---
if st.session_state.budget > 0:
    progress = total_spent / st.session_state.budget
    # Cap progress at 1.0 (100%) to prevent errors if over budget
    bar_value = min(progress, 1.0)
    
    st.write("### Budget Usage")
    st.progress(bar_value)
    
    if total_spent > st.session_state.budget:
        st.error(f"⚠️ You are over budget by ${total_spent - st.session_state.budget:,.2f}!")
    elif bar_value > 0.8:
        st.warning("⚠️ You are nearing your budget limit.")

# --- Visualizations & Data ---
if not df.empty:
    col_chart, col_data = st.columns([2, 1])
    
    with col_chart:
        st.subheader("Expenses by Category")
        # Group data by category for the chart
        chart_data = df.groupby("Category")["Amount"].sum()
        st.bar_chart(chart_data)
        
    with col_data:
        st.subheader("History")
        st.dataframe(df, hide_index=True, use_container_width=True)

else:
    st.info("Start by adding an expense above!")
