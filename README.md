# Bank Management System

A robust, object-oriented Python application designed to simulate a professional banking environment. This system combines a secure PostgreSQL database with a clean, interactive web interface, delivering a seamless user experience for managing financial records.

---

## 🚀 Key Features

*   **Secure Authentication:** Utilizes `hashlib` for cryptographic PIN hashing, ensuring user credentials are fundamentally protected.
*   **Core Financial Operations:** Seamlessly process deposits, withdrawals, and balance inquiries with strict validation and real-time database persistence.
*   **Comprehensive Audit Logging:** Automatically tracks and records all account activities to generate detailed, timestamped transaction histories.
*   **Account Management:** Users can register new accounts, dynamically update profile information (like legal names and PINs), and securely delete their accounts.
*   **Modern Web Interface:** A highly interactive web GUI built entirely in Python using **Streamlit**, prioritizing high-utility, clean design over cluttered interfaces.

---

## 🛠️ Technology Stack

*   **Frontend:** Streamlit 
*   **Backend Logic:** Python 3 (Object-Oriented Programming)
*   **Database:** PostgreSQL (`psycopg2`)
*   **Security:** Python `hashlib` 

---

## 📂 System Architecture

The backend code is modularly separated to ensure clean state management and scalable logic:

*   **`BankSystem`**: The core orchestrator handling database connections, execution of CRUD operations, and financial validations.
*   **`Account`**: The object-oriented representation of the end-user, handling localized state variables (like Name, Account Number, and PIN hashes).
*   **`Audit`**: The tracking mechanism responsible for recording timestamps, action types, and monetary amounts for every transaction.

---

## ⚙️ Installation and Setup

### 1. Prerequisites
*   Python 3.8+ installed on your local machine.
*   PostgreSQL installed and actively running.

### 2. Database Configuration
Ensure you have a local PostgreSQL server running. The system is configured to connect to a database named `bank`. By default, the `database.py` file expects the following connection parameters:
*   **Host:** `localhost`
*   **Port:** `5432`
*   **User:** `postgres`
*   **Password:** *(Your specific PostgreSQL Password)*

### 3. Install Dependencies
Navigate to the root directory of the project in your terminal and install the required Python libraries:
```bash
pip install streamlit psycopg2 pandas
