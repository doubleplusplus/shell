from cmd import Cmd


class MyShell(Cmd):
    prompt = '<Shell> '
    intro = "Welcome! Type ? to list commands. Type 'exit' to end Shell"

    def do_exit(self, inp):
        '''exit the Shell. Shorthand: x q.'''
        print("Shell terminated!")
        return True

    def help_exit(self):
        print('exit the Shell. Shorthand: x q command+D.')

    def default(self, inp):
        if inp == 'x' or inp == 'q':
            return self.do_exit(inp)

        print("Default: {}".format(inp))

    def do_add(self, inp):
        print("Adding '{}'".format(inp))

    def help_add(self):
        print("Add a new entry to the system.")

    do_EOF = do_exit  # press command+D, send EOF and exit
    help_EOF = help_exit


if __name__ == '__main__':
    shell = MyShell()
    shell.cmdloop()

