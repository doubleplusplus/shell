from cmd import Cmd
import os

class MyShell(Cmd):
    prompt = '<' + os.getcwd() + '> '
    intro = "Welcome! Type ? to list commands. Type 'exit' or 'x' to stop Shell"

    def do_prompt(self, line):
        "Change the interactive prompt"
        self.prompt = '<' + line + '> '

    def do_exit(self, inp):
        '''exit the Shell. Shorthand: x q.'''
        print("Shell terminated!")
        return True

    def help_exit(self):
        print('exit the Shell. Shorthand: x q command+D.')

    def emptyline(self):
        "when an empty line is entered, do nothing"
        # By default when an empty line is entered, the last command is repeated
        pass

    def default(self, inp):
        if inp == 'x':
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

    def do_ls(self, input):
        "show directory"
        try:
            if input == '':
                # sort alphabetically without hidden files
                files = sorted([f for f in os.listdir() if not f.startswith('.')], key=str.lower)
                print(*files, sep='\n')  # print list items
            else:
                files = sorted([f for f in os.listdir(input) if not f.startswith('.')], key=str.lower)
                print(*files, sep='\n')
        except:
            print('Path not found: {}'.format(input))

    def do_cd(self, path):
        """convert to absolute path and change directory"""
        try:
            os.chdir(os.path.abspath(path))
            self.do_prompt(os.getcwd())
            #print(os.getcwd())  # cwd = current working directory
        except Exception:
            print("cd: no such file or directory: {}".format(path))


if __name__ == '__main__':
    MyShell().cmdloop()
    #print(os.getcwd())

