import utils

from getpass import getpass

from customer import Customer
from editor import Editor
from session import Session
from utils import cursor


class Shell:

    def handle(self):
        cmdList = {
            "login": self.login,
            "signup": self.signup,
            "help": self.help,
        }

        print("Type \"help\" for usage\n")
        while True:
            try:
                line = input("$ ").strip()
                print()

                if not line:
                    continue

                if line in cmdList:
                    func = cmdList[line]
                    func()
                elif line == "exit" or line == "quit":
                    return
                else:
                    print(f"{line}: command not found\n")
            except (KeyboardInterrupt, EOFError):
                break

    def help(self):
        print("usage: login: provide an Id and password to login as a(an) customer \ editor\n"
              "signup: register as a customer and login as a customer\n"
              "quit: exit the program\n")

    def login(self):
        print("Ctrl-C / Ctrl-Z to aboard login process\n")

        try:
            id = input("id: ").strip()
            pwd = getpass("password: ").strip()

            print()

            assert id and pwd, "Id and password cannot be empty\n"

            prefix = id[0]
            idInt = id[1:]

            assert (prefix == "c" or prefix == "e") and utils.isValidInt(idInt), "Invalid Id. Prefix is required before digit: \"c\" - customers, \"e\" - editors\n"

            if prefix == "c":
                if self.hasCustomer(id):
                    if self.checkCustomerPwd(id, pwd):
                        print("Welcome\n")
                        pass  # initialize a customer instance and then call handle()
                else:
                    print(f"Customer {id} doesn't exist\n")
                    ans = input("Sign up as a new customer(y/n)?")
                    if ans.lower() == "y":
                        if self.signup():
                            print("Welcome\n")
                    # initialize a customer instance and then call handle()
            elif prefix == "e":
                if self.hasEditor(id):
                    if self.checkEditorPwd(id, pwd):
                        editor = Editor(id)
                        editor.handle()
                else:
                    print(f"Editor {id} doesn't exist\n")
        except (KeyboardInterrupt, EOFError):
            print("Aboard task\n")
        except AssertionError as ae:
            print(ae)

    def signup(self):
        print("Ctrl-C / Ctrl-Z to aboard signup process\n")

        try:
            cid = input("id: ").strip()

            assert utils.isValidInt(cid), "Invalid Id\n"

            cid = f"c{int(cid)}"
            if not self.hasCustomer(f"c{cid}"):
                name = input("name: ").strip()
                pwd = getpass("password: ").strip()

                print()

                assert utils.isValidText(name), "Invalid name\n"
                assert utils.isValidText(pwd) and " " not in pwd, "Invalid password\n"

                self.addCustomer(cid, name, pwd)

                return True
            else:
                print(f"customer {cid} already exists\n")
        except (KeyboardInterrupt, EOFError):
            print("Aboard task\n")
        except AssertionError as ae:
            print(ae)

        return False

    def addCustomer(self, cid, name, pwd):
        cursor.execute("insert into customers values "
                       "(?, ?, ?)", (cid, name, pwd,))
        utils.commit()

        print(f"Customer {cid} is added into database")

    def checkCustomerPwd(self, cid, pwd):
        rpwd = cursor.execute(
            "select pwd from customers where cid = ?", (cid,)
        ).fetchone()[0]

        if pwd == rpwd:
            return True

        print("Incorrect password\n")

        return False

    def checkEditorPwd(self, eid, pwd):
        rpwd = cursor.execute(
            "select pwd from editors where eid = ?", (eid,)
        ).fetchone()[0]

        if pwd == rpwd:
            return True

        print("Incorrect password\n")

        return False

    def hasCustomer(self, cid):
        result = cursor.execute(
            "select * from customers where cid = ?", (cid,)
        ).fetchone()

        if result:
            return True

        return False

    def hasEditor(self, eid):
        result = cursor.execute(
            "select * from editors where eid = ?", (eid,)
        ).fetchone()

        if result:
            return True

        return False
