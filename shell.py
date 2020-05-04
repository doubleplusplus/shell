from cmd import Cmd
import os

class MyShell(Cmd):
    prompt = '<Shell> '
    intro = "Welcome! Type ? to list commands. Type 'exit' to end Shell"

    def do_prompt(self, line):
        "Change the interactive prompt"
        self.prompt = '<' + line + '> '

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

    do_EOF = do_exit  # press command+D, send EOF and exit
    help_EOF = help_exit

    last_output = ''

    def do_shell(self, line):
        "Run a shell command"
        print("running shell command:", line)
        output = os.popen(line).read()
        print(output)
        self.last_output = output

    def do_echo(self, line):
        "Print the input, replacing '$out' with the output of the last shell command"
        # Obviously not robust
        print(line.replace('$out', self.last_output))


if __name__ == '__main__':
    shell = MyShell()
    shell.cmdloop()

