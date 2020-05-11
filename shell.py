from cmd import Cmd
import os
import sys
import shlex
import signal


class MyShell(Cmd):
    def __init__(self):
        super(MyShell, self).__init__()
        self.prompt = '<' + self.full_to_home_abbr(os.getcwd()) + '> '
        self.intro = "Welcome! Type ? to list commands. Type 'exit' or 'x' to stop Shell"
        self.last_output = ''

    def do_prompt(self, line):
        "Change the interactive prompt"
        self.prompt = '<' + line + '> '

    def do_exit(self, arg):
        '''exit the Shell. Shorthand: x'''
        args = shlex.split(arg)
        if len(args) > 1:
            print('exit: too many arguments', file=sys.stderr)
            return
        print("Shell terminated!")
        return True

    def help_exit(self):
        print('exit the Shell. Shorthand: x, command+D.')

    do_EOF = do_exit  # press command+D, send EOF and exit
    help_EOF = help_exit

    def emptyline(self):
        "when an empty line is entered, do nothing"
        # By default when an empty line is entered, the last command is repeated
        pass

    def default(self, inp):
        if inp == 'x':
            return self.do_exit(inp)
        #print("Default: {}".format(inp))
        command = shlex.split(inp)
        child_pid = os.fork()
        if child_pid == 0:
            try:
                os.execvp(command[0], command)
            except FileNotFoundError:
                print(f'No command: {command[0]}')
                # if error, kill child process
                os.kill(os.getpid(), signal.SIGKILL)
        else:
            os.waitpid(child_pid, 0)

    def do_shell(self, line):  # ! is shortcut for the shell command
        "Run a shell command"
        print("running shell command:", line)
        #os.system(line)
        output = os.popen(line).read()
        print(output)
        self.last_output = output

    def do_echo(self, line):
        "Print the input, replacing '$out' with the output of the last shell command"
        # Obviously not robust
        print(line.replace('$out', self.last_output))

    def do_ls(self, input):
        "show directory"
        if input == '':
            # sort alphabetically without hidden files
            files = sorted([f for f in os.listdir() if not f.startswith('.')], key=str.lower)
            print(*files, sep='\n')  # print list items
        else:
            try:
                files = sorted([f for f in os.listdir(input) if not f.startswith('.')], key=str.lower)
                print(*files, sep='\n')
            except FileNotFoundError:
                print(f'Path not found: {input}')

    def home_abbr_to_full(self, abbr_path: str):
        if abbr_path.startswith('~'):
            abbr_path = abbr_path.replace('~', os.environ['HOME'], 1)
        return abbr_path

    def full_to_home_abbr(self, full_path: str):
        if full_path.startswith(os.environ['HOME']):
            full_path = full_path.replace(os.environ['HOME'], '~', 1)
        return full_path

    def do_cd(self, path):
        """convert to absolute path and change directory"""
        try:
            os.chdir(os.path.abspath(path))
            self.do_prompt(f'{self.full_to_home_abbr(os.getcwd())}')
            #print(os.getcwd())  # cwd = current working directory
        except FileNotFoundError:
            print(f'cd: not a file: {path}')
        except NotADirectoryError:
            print(f'cd: not a directory {path}')


if __name__ == '__main__':
    if len(sys.argv) > 1:
        # accept command line arguments
        MyShell().onecmd(' '.join(sys.argv[1:]))
    else:
        MyShell().cmdloop()


