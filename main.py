import hashlib as hlib
import string
import random
from database import connect_to_database
#Encryption and verification
def hash_pin(pin):
    return hlib.sha256(pin.encode()).hexdigest()
def verify_pin(input_pin,stored_pin):
    return hash_pin(input_pin)==stored_pin

#database initialize
def intialize_tables():
    conn=connect_to_database()
    if not conn:
        return False
    try:
        cur=conn.cursor()

        create_account_table="""CREATE TABLE IF NOT EXISTS accounts(
        account_no VARCHAR(100) PRIMARY KEY,
        name VARCHAR(100) NOT NULL,
        pin VARCHAR(100) NOT NULL,
        balance DECIMAL(20,2) DEFAULT 0.00,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP 
        )"""

        create_audit_table="""CREATE TABLE IF NOT EXISTS audit(
        id SERIAL PRIMARY KEY,
        account_no VARCHAR(100) NOT NULL,
        holder_name VARCHAR(100) NOT NULL,
        action VARCHAR(100) NOT NULL,
        amount DECIMAL(20,2) DEFAULT 0.00,
        time_stamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP ,
        CONSTRAINT fk_audit_account
        FOREIGN KEY (account_no) REFERENCES accounts(account_no)
        )"""
        cur.execute(create_account_table)
        cur.execute(create_audit_table)
        
        conn.commit()
        cur.close()
        return True
    except Exception as err:
        print(f"Error occured: {err}")
        return False
    

#ACCOUNT CLASS
class Account:

    def __init__(self,name="",pin="",account_number=""):
        self.__account_number=(account_number if account_number else self.__generate_account_number())

        self.__name=name
        self.__pin=hash_pin(pin)
        self.__balance=0.0
        
    @staticmethod
    def __generate_account_number():
        return "".join(random.choices(string.ascii_uppercase+string.digits,k=10))
    
    #Getters
    def get_account_number(self):
        return self.__account_number
    def get_name(self):
        return self.__name
    def get_pin_hash(self):
        return self.__pin
    def get_balance(self):
        return self.__balance
    

    #Setter 
    def set_name(self,name):
        self.__name=name

    def set_pin_hash(self,pin):
        self.__pin=hash_pin(pin)

    def set_balance(self,balance):
        self.__balance=balance


    #Utilities

    def deposit(self,amount):
        if amount<=0:
            return False
        self.__balance+=amount
        return True
    def withdraw(self,amount):
        if amount<=0 or amount>self.__balance:
            return False
        self.__balance-=amount
        return True
    
    #Database CRUD

    @classmethod
    def load_from_db(cls,account,pin):
        connection=connect_to_database()

        if not connection:
            return False
        try:
            cursor=connection.cursor()
            cursor.execute("""SELECT account_no,name,pin,balance FROM accounts WHERE account_no=%s""",(account,),)
            result=cursor.fetchone()
            connection.commit()
            cursor.close()
            if result:
                stored_pin_hash=result[2]
                if verify_pin(pin,stored_pin_hash):
                    account=cls(result[1],pin,result[0])
                    account.set_balance(float(result[3]))
                    return account
                    

        except Exception as err:
            print(f"Error Loading account : {err}")   
            return None
        
    def save_to_db(self):
        connection=connect_to_database()

        if not connection:
            return False
        try:
            cursor=connection.cursor()
            cursor.execute("""INSERT INTO accounts(account_no,name,pin,balance) VALUES(%s,%s,%s,%s) 
                           ON CONFLICT(account_no)
                           DO UPDATE SET name=%s,pin=%s,balance=%s""",
                           (self.__account_number,
                            self.__name,
                            self.__pin,
                            self.__balance,
                            self.__name,
                            self.__pin,
                            self.__balance,))
            connection.commit()
            cursor.close()
            return True
                    

        except Exception as err:
            print(f"Error Saving account : {err}")   
            return None
        
    def delete_from_db(self):
        connection=connect_to_database()

        if not connection:
            return False
        try:
            cursor=connection.cursor()
            cursor.execute("DELETE FROM audit WHERE account_no=%s",(self.__account_number,))
            cursor.execute("""DELETE FROM accounts WHERE account_no=%s """,(self.__account_number,))
            connection.commit()
            cursor.close()
            return True
                    

        except Exception as err:
            print(f"Error Deleting account : {err}")   
            return None


#AUDIT CLASS
class Audit:
    @staticmethod
    def log_actions(account_number,holer_name,action,amount=0.0):
        connection=connect_to_database()

        if not connection:
            return False
        try:
            cursor=connection.cursor()
            cursor.execute("""INSERT INTO audit(account_no,holder_name,action,amount) VALUES(%s,%s,%s,%s) """,(account_number,holer_name,action,amount,))
            connection.commit()
            cursor.close()
            return True
                    

        except Exception as err:
            print(f"Error inserting logs : {err}")   
            return None
    
    @staticmethod
    def get_single_audit_logs(account_number):
        connection=connect_to_database()

        if not connection:
            return []
        try:
            cursor=connection.cursor()
            cursor.execute(""" SELECT id,holder_name,action,amount,time_stamp FROM audit 
                           WHERE account_no=%s
                           ORDER BY time_stamp DESC""",(account_number,))
            result=cursor.fetchall()

            logs=[]

            for row in result:
                logs.append({
                    "id":row[0],
                    "holder_name":row[1],
                    "action":row[2],
                    "amount":row[3],
                    "timestamp":row[4]

                })
            connection.commit()
            cursor.close()
            return logs
                    

        except Exception as err:
            print(f"Error logging {account_number} actions : {err}")   
            return None

    @staticmethod
    def clear_single_audit_logs(account_number):
        connection=connect_to_database()

        if not connection:
            return False
        try:
            cursor=connection.cursor()
            cursor.execute(""" DELETE FROM audit WHERE account_no =%s""",(account_number,),)
            connection.commit()
            cursor.close()
            return True
                    

        except Exception as err:
            print(f"Error clearing audit actions : {err}")   
            return False


    @staticmethod
    def get_all_audit_logs():
        connection=connect_to_database()

        if not connection:
            return []
        try:
            cursor=connection.cursor()
            cursor.execute(""" SELECT id,holder_name,action,amount,time_stamp FROM audit 
                           ORDER BY timestamp DESC""")
            result=cursor.fetchall()

            logs=[]

            for row in result:
                logs.append({
                    "id":row[0],
                    "holder_name":row[1],
                    "action":row[2],
                    "amount":row[3],
                    "timestamp":row[4]

                })
            connection.commit()
            cursor.close()
            return logs
                    

        except Exception as err:
            print(f"Error logging actions : {err}")   
            return None
        

    @staticmethod
    def clear_all_audit_logs():
        connection=connect_to_database()

        if not connection:
            return False
        try:
            cursor=connection.cursor()
            cursor.execute("DELETE FROM audit")
            connection.commit()
            cursor.close()
            return True
                    

        except Exception as err:
            print(f"Error clearing audit actions : {err}")   
            return False

class BankSystem:
    def __init__(self):
        if intialize_tables():
            print("Tables initialized")

    def create_account(self,name,pin):
        account=Account(name,pin)
        if account.save_to_db():
            Audit.log_actions(account.get_account_number(),account.get_name(),"Account Created",0.0)
            return account
        return None
    
    def read_account(self,account_no,pin):
        account=Account.load_from_db(account_no,pin)
        if account:
            Audit.log_actions(account_no,account.get_name(),"Details Checked",0.0)
            return account
        return None
    
    def update_account(self,account):
        return account.save_to_db()
    
    def delete_account(self,account_no,pin):
        account=Account.load_from_db(account_no,pin)
        if account:
            success=account.delete_from_db()
            if success:
                Audit.log_actions(account_no,account.get_name(),"Account Deleted",0.0)
                return True
        return False
    
    def deposit(self,account_no,pin,amount):
        account=Account.load_from_db(account_no,pin)
        if account and account.deposit(amount):
            if account.save_to_db():
                Audit.log_actions(account_no,account.get_name(),"Amount Deposit",amount)
                return True
        return False
    
    def withdraw (self,account_no,pin,amount):
        account=Account.load_from_db(account_no,pin)
        if account and account.withdraw(amount):
            if account.save_to_db():
                Audit.log_actions(account_no,account.get_name(),"Amount Deposit",amount)
                return True
        return False
    
    def get_account_balance(self,account_no,pin):
        account=Account.load_from_db(account_no,pin)
        if account:
            Audit.log_actions(account_no,account.get_name(),"Balance checked",0.0)
            return account.get_balance()
        return None
    
    def get_single_audit_logs(self,account_no):
        return Audit.get_single_audit_logs(account_no)
    
    def get_all_audit_logs(self):
        return Audit.get_all_audit_logs()
    
    def clear_single_audit_logs(self,account_no):
        return Audit.clear_single_audit_logs(account_no)
    
    def clear_all_audit_logs(self):
        return Audit.clear_all_audit_logs()


#valid amount
def get_valid_amount(prompt):
    while True:

        try:
            amount=float(input(prompt))
            if amount<=0:
                print("Amount must be greater than zero")
                continue
            return amount
        except Exception as err:
            print(f"Please enter a valid amount in numbers {err}")


#CLI menu functions

#Create account cli
def create_account_cli(bank):
    print("="*50)
    print("Create New Account")
    print("="*50)

    name =input("Enter your name: ").strip()
    if not name:
            print("Name cannot be Empty/Ignored")
            input("Press enter to continue")
            return
        
    pin =input("Enter your 4-DIGIT Pin: ").strip()
    if len(pin)!=4 or not pin.isdigit():
            print("Pin must be 4 digit and only in numbers")
            input("Press enter to continue")
            return
        
    confirm_pin =input("Confirm your 4-DIGIT Pin: ").strip()
    if confirm_pin!=pin:
            print("Pin is not matching")
            input("Press enter to continue")
            return
        
    account=bank.create_account(name,pin)

    if account:
                print("Account created successfully")
                print(f"Account Number: {account.get_account_number()}")
                print("Save your account no. and pin securely")
    else:
            print("An error occured pls try again later..")

        
    input("Press enter to continue")
        


# logged in account cli

def check_balance_cli(bank,account,pin):
    print("="*50)
    print("Check account balance")
    print("="*50)

    balance=bank.get_account_balance(account.get_account_number(),pin)
    if balance is not None:
        print(f"Account balance : ${ balance:.2f}")
    else:
        print("An error in checking balance pls try again later..")

    input("Press enter to continue")

def deposit_money_cli(bank,account,pin):
    print("="*50)
    print("Deposit money")
    print("="*50)

    amount=get_valid_amount("Enter deposit amount: ")
    if bank.deposit(account.get_account_number(),pin,amount):
        print(f"${amount:.2f} is successfully deposited")

        balance=bank.get_account_balance(account.get_account_number(),pin)
        if balance is not None:
            print(f"Account balance : ${ balance:.2f}")
    else:
        print("An error deposit balance pls try again later..")

    input("Press enter to continue")

def withdraw_money_cli(bank,account,pin):
    print("="*50)
    print("Deposit money")
    print("="*50)

    amount=get_valid_amount("Enter withdraw amount: ")
    if bank.withdraw(account.get_account_number(),pin,amount):
        print(f"${amount:.2f} is successfully withdraw")

        balance=bank.get_account_balance(account.get_account_number(),pin)
        if balance is not None:
            print(f"Account balance : ${ balance:.2f}")
    else:
        print("An error withdraw balance pls try again later..")

    input("Press enter to continue")

def transaction_history_cli(bank,account,pin):
    print("="*50)
    print("Transaction history")
    print("="*50)

    logs=bank.get_single_audit_logs(account.get_account_number())

    if not logs:
        print("No logs available")
    else:
        for log in logs:
            print(f"{log['timestamp']} {log['action']} - {log['amount']:.2f} By: {log['holder_name']}")
    input("Press enter to continue")


def update_account_name_cli(bank,account,pin):
    print("="*50)
    print("Update Account Name")
    print("="*50)

    new_name =input("Enter your name: ").strip()
    if new_name:
            account.set_name(new_name)
            if bank.update_account(account):
                Audit.log_actions(account.get_account_number(),account.get_name(),"Account Updated",0.0)
                print("name updated successfully")
            else:
                print("Error in updating name")
    else:
        print("No changes made")
    input("Press enter to continue")

def update_account_pin_cli(bank,account,pin):
    print("="*50)
    print("Update Account Pin")
    print("="*50)

    old_pin=input("enter old pin : ").strip()
    if old_pin!=pin:
        print("iccorect current pin ")
        input("Enter to continue..")
        return False

    new_pin =input("Enter new 4-DIGIT Pin: ").strip()
    if len(pin)!=4 or not pin.isdigit():
            print("Pin must be 4 digit and only in numbers")
            input("Press enter to continue")
            return
        
    confirm_pin =input("Confirm your 4-DIGIT Pin: ").strip()
    if confirm_pin!=new_pin:
            print("Pin is not matching")
            input("Press enter to continue")
            return
        
    account.set_pin_hash(new_pin)
    if bank.update_account(account):
        Audit.log_actions(account.get_account_number(),account.get_name(),"Pin changed (Auto Logout)",0.0)
        print("pin updated successfully, you are logged.. ")
        return True
    
    print("Error in updating pin")
    input("Press enter to continue")
    return False


def close_account_cli(bank,account,pin):
    print("="*50)
    print("Delete Account")
    print("="*50)
    choice=input("Are you sure, you want to delete your account(yes/no)").strip().lower()

    if choice!="yes":
        print("Account deletion canccelled")
        input("Enter to continue..")

        return False
    re_pin=input("enter pin to confirm deletion: ").strip()
    if re_pin!=pin:
        print("iccorect pin ")
        input("Enter to continue..")
        return False

    if bank.delete_account(account.get_account_number(),pin):
        print("account deleted successfully")
        return True
    
        
    
    
    print("Error in deleting account")
    input("Press enter to continue")
    return False


#login account cli
def login_account_cli(bank):
    print("="*50)
    print("Login Account")
    print("="*50)

    account_no =input("Enter your account number: ").strip()
    if not account_no:
            print("account number cannot be Empty/Ignored")
            input("Press enter to continue")
            return
        
    pin =input("Enter your 4-DIGIT Pin: ").strip()
    account=bank.read_account(account_no,pin)
    if not account :
            print("wrong credientials")
            input("Press enter to continue")
            return
        

    while True:

        print("="*50)
        print(f"Welcome {account.get_name()}")
        print(f"Account no:  {account_no}")
        print("="*50)

        print("1. check balance")
        print("2. deposit money")
        print("3. withdraw money")
        print("4. transaction history")
        print("5. update account name")
        print("6. update account pin")
        print("7. close account")
        print("8. logout")
        print("="*50)


        choice = int(input("Enter your choice: "))

        match choice:
            case 1:
                check_balance_cli(bank,account,pin)
            case 2:
                deposit_money_cli(bank,account,pin)
            case 3:
                withdraw_money_cli(bank,account,pin)
            case 4:
                transaction_history_cli(bank,account,pin)
            case 5:
                update_account_name_cli(bank,account,pin)
            case 6:
                if update_account_pin_cli(bank,account,pin):
                    break
            case 7:
                if close_account_cli(bank,account,pin):
                    break
            case 8:
                break
            case _:
                print("Wrong choice")
                input("Press enter to continue")
                
    

    

#main menu
def main_menu():
    bank =BankSystem()

    while True:

        print("="*50)
        print("Bank Management System")
        print("="*50)

        print("1. New account")
        print("2. Login account")

        print("0. Exit")

        choice = int(input("Enter your choice: "))

        match choice:
            case 1:
                create_account_cli(bank)
            case 2:
                login_account_cli(bank)
            case 0:
                print("Thanks for using our services , Do visti again")
                break
            case _:
                print("Wrong choice")
                input("Press enter to continue")



if __name__=="__main__":
    main_menu()