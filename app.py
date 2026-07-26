import streamlit as st
import pandas as pd
from main import BankSystem

# Page Configuration for a professional look
st.set_page_config(page_title="Enterprise Bank Management", layout="centered")

# Initialize Session State
if "bank" not in st.session_state:
    # Initializes the database tables and BankSystem
    st.session_state.bank = BankSystem() 
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "account" not in st.session_state:
    st.session_state.account = None
if "pin" not in st.session_state:
    st.session_state.pin = None

# Custom CSS for a minimal, professional aesthetic
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    h1 { color: #2c3e50; font-family: 'Helvetica Neue', sans-serif; }
    h2, h3 { color: #34495e; font-family: 'Helvetica Neue', sans-serif; }
    .stButton>button { background-color: #2980b9; color: white; border-radius: 4px; }
    .stButton>button:hover { background-color: #3498db; }
    </style>
""", unsafe_allow_html=True)

def login_screen():
    st.title("Bank Management System")
    st.markdown("---")
    
    tab1, tab2 = st.tabs(["Login", "Create Account"])
    
    with tab1:
        st.subheader("Account Login")
        with st.form("login_form"):
            account_no = st.text_input("Account Number")
            pin = st.text_input("4-Digit PIN", type="password")
            submit_login = st.form_submit_button("Secure Login")
            
            if submit_login:
                if not account_no or not pin:
                    st.error("Account Number and PIN are required.")
                else:
                    # Validates credentials using your backend logic
                    account = st.session_state.bank.read_account(account_no, pin)
                    if account:
                        st.session_state.logged_in = True
                        st.session_state.account = account
                        st.session_state.pin = pin
                        st.rerun()
                    else:
                        st.error("Invalid credentials. Please try again.")

    with tab2:
        st.subheader("Register New Account")
        with st.form("register_form"):
            new_name = st.text_input("Full Name")
            new_pin = st.text_input("4-Digit PIN", type="password", max_chars=4)
            confirm_pin = st.text_input("Confirm PIN", type="password", max_chars=4)
            submit_register = st.form_submit_button("Create Account")
            
            if submit_register:
                if not new_name:
                    st.error("Name cannot be empty.")
                elif len(new_pin) != 4 or not new_pin.isdigit():
                    st.error("PIN must be exactly 4 digits.")
                elif new_pin != confirm_pin:
                    st.error("PINs do not match.")
                else:
                    # Saves the new account to the database
                    new_acc = st.session_state.bank.create_account(new_name, new_pin)
                    if new_acc:
                        st.success("Account created successfully.")
                        st.info(f"Your Account Number is: **{new_acc.get_account_number()}**")
                        st.warning("Please save your account number securely.")
                    else:
                        st.error("An error occurred. Please try again later.")

def dashboard():
    account = st.session_state.account
    pin = st.session_state.pin
    bank = st.session_state.bank

    st.sidebar.title("Navigation")
    st.sidebar.markdown(f"**User:** {account.get_name()}")
    st.sidebar.markdown(f"**Account:** {account.get_account_number()}")
    st.sidebar.markdown("---")
    
    menu = st.sidebar.radio("Menu", [
        "Overview", 
        "Deposit Funds", 
        "Withdraw Funds", 
        "Transaction History", 
        "Account Settings",
        "Close Account"
    ])
    
    st.sidebar.markdown("---")
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.account = None
        st.session_state.pin = None
        st.rerun()

    st.title("Account Dashboard")
    st.markdown("---")

    if menu == "Overview":
        st.subheader("Financial Overview")
        # Fetches balance directly from your class method
        balance = bank.get_account_balance(account.get_account_number(), pin)
        if balance is not None:
            col1, col2 = st.columns(2)
            col1.metric(label="Current Balance", value=f"${balance:.2f}")
        else:
            st.error("Error retrieving balance.")

    elif menu == "Deposit Funds":
        st.subheader("Make a Deposit")
        with st.form("deposit_form"):
            amount = st.number_input("Deposit Amount ($)", min_value=0.01, format="%f")
            submit = st.form_submit_button("Deposit")
            if submit:
                # Executes deposit and updates the database
                if bank.deposit(account.get_account_number(), pin, amount):
                    st.success(f"${amount:.2f} successfully deposited.")
                else:
                    st.error("Deposit failed. Please try again.")

    elif menu == "Withdraw Funds":
        st.subheader("Make a Withdrawal")
        with st.form("withdraw_form"):
            amount = st.number_input("Withdrawal Amount ($)", min_value=0.01, format="%f")
            submit = st.form_submit_button("Withdraw")
            if submit:
                # Executes withdrawal and updates the database
                if bank.withdraw(account.get_account_number(), pin, amount):
                    st.success(f"${amount:.2f} successfully withdrawn.")
                else:
                    st.error("Withdrawal failed. Check your balance and try again.")

    elif menu == "Transaction History":
        st.subheader("Audit Logs")
        # Retrieves logs from the audit table via your Audit class
        logs = bank.get_single_audit_logs(account.get_account_number())
        if not logs:
            st.info("No transaction history available.")
        else:
            df = pd.DataFrame(logs)
            # Reorder and format columns for professional display
            df = df[["timestamp", "action", "amount", "holder_name"]]
            df.columns = ["Date & Time", "Action", "Amount ($)", "Initiated By"]
            st.dataframe(df, use_container_width=True, hide_index=True)

    elif menu == "Account Settings":
        st.subheader("Update Account Information")
        
        tab_name, tab_pin = st.tabs(["Update Name", "Change PIN"])
        
        with tab_name:
            with st.form("name_form"):
                new_name = st.text_input("New Full Name")
                if st.form_submit_button("Update Name"):
                    if new_name:
                        account.set_name(new_name)
                        if bank.update_account(account):
                            st.success("Name updated successfully.")
                            st.rerun()
                        else:
                            st.error("Failed to update name.")
                    else:
                        st.warning("Please enter a valid name.")
                        
        with tab_pin:
            with st.form("pin_form"):
                current_pin = st.text_input("Current PIN", type="password", max_chars=4)
                new_pin = st.text_input("New 4-Digit PIN", type="password", max_chars=4)
                confirm_new_pin = st.text_input("Confirm New PIN", type="password", max_chars=4)
                
                if st.form_submit_button("Change PIN"):
                    if current_pin != pin:
                        st.error("Current PIN is incorrect.")
                    elif len(new_pin) != 4 or not new_pin.isdigit():
                        st.error("New PIN must be exactly 4 digits.")
                    elif new_pin != confirm_new_pin:
                        st.error("New PINs do not match.")
                    else:
                        # Re-hashes the PIN and updates the database row
                        account.set_pin_hash(new_pin)
                        if bank.update_account(account):
                            st.success("PIN changed successfully. Please log in again.")
                            st.session_state.logged_in = False
                            st.rerun()
                        else:
                            st.error("Failed to update PIN.")

    elif menu == "Close Account":
        st.subheader("Account Deletion")
        st.error("Warning: This action is permanent and cannot be undone.")
        with st.form("delete_form"):
            confirm = st.text_input('Type "DELETE" to confirm')
            auth_pin = st.text_input("Enter PIN to authorize", type="password", max_chars=4)
            if st.form_submit_button("Permanently Delete Account"):
                if confirm == "DELETE" and auth_pin == pin:
                    # Executes PostgreSQL DELETE statement
                    if bank.delete_account(account.get_account_number(), pin):
                        st.success("Account permanently deleted.")
                        st.session_state.logged_in = False
                        st.session_state.account = None
                        st.session_state.pin = None
                        st.rerun()
                    else:
                        st.error("An error occurred during deletion.")
                else:
                    st.error("Validation failed. Check your input and PIN.")

if __name__ == "__main__":
    if st.session_state.logged_in:
        dashboard()
    else:
        login_screen()