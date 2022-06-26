import getpass

from peewee import OperationalError

from durator.common.account.managers import AccountManager
from durator.common.log import LOG
from durator.db.database import DB, db_connection
from durator.db.models import MODELS


class DatabaseClient:
    """Command-line front-end to the database."""

    def __init__(self):
        self.shutdown_flag = False
        self.shell_commands = {
            "help": {"help": "print this help", "func": self._shell_print_commands},
            "quit": {"help": "quit the client", "func": self._shell_quit},
            "install": {"help": "create database and tables", "func": self._install_db},
            "test": {"help": "test database availability", "func": self._test_db},
            "account": {"help": "create a new player account", "func": self._new_account},
        }

    def start(self):
        LOG.info("Database client started. Type help for a list of commands.")
        self._shell()

    def _shell(self):
        while not self.shutdown_flag:
            user_input = input("> ")
            user_words = user_input.split()
            if not user_words:
                continue

            command_name = self._shell_find_command(user_words)
            if command_name is None:
                continue

            command = self.shell_commands[command_name]
            command["func"]()

    def _shell_find_command(self, user_words):
        command_name = user_words[0]
        if command_name not in self.shell_commands:
            possible_alias = [cmd for cmd in self.shell_commands if cmd.startswith(command_name)]
            if len(possible_alias) < 1:
                print("Unknown command.")
                return None
            elif len(possible_alias) > 1:
                print("Ambiguous alias:", ", ".join(possible_alias))
                return None
            else:
                command_name = possible_alias[0]
        return command_name

    def _shell_print_commands(self):
        print("Commands available:")
        for command_name in sorted(self.shell_commands):
            command = self.shell_commands[command_name]
            print("        {:<16}{}".format(command_name, command["help"]))

    def _shell_quit(self):
        self.shutdown_flag = True

    def _install_db(self):
        drop_tables = input("Do you want to drop existing tables? [y/N]") == "y"

        try:
            result = self._install_db_tables(drop_tables=drop_tables)
            if result:
                print("Database installation OK")
        except OperationalError as exc:
            print("An exception occured during tables creation:")
            print(str(exc))

    @db_connection
    def _install_db_tables(self, drop_tables=False):
        if drop_tables:
            DB.drop_tables(MODELS, safe=True)
        DB.create_tables(MODELS, safe=True)
        return True

    def _test_db(self):
        @db_connection
        def get_test_value():
            return 1325  # misc value, the decorator will return None on failure

        test_value = None
        try:
            test_value = get_test_value()
        except OperationalError as exc:
            print("Exception caught: " + str(exc))

        if test_value is not None:
            print("Database access test OK")
        else:
            print("Database access test failed :(")

    def _new_account(self):
        name = input("Name: ")
        password = getpass.getpass("Password: ")
        if not name or not password:
            print("Invalid arguments.")
            return

        account = AccountManager.create_account(name, password)
        if account:
            print("Account created.")
        else:
            print("Account couldn't be created.")
