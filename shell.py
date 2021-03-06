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
        self.jobs = []

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

    def do_shell(self, line):  # ! is shortcut for the shell command
        "Run a shell command"
        print("running shell command:", line)
        #os.system(line)
        output = os.popen(line).read()
        print(output)
        self.last_output = output

    def do_print(self, line):
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

    def default(self, inp):
        # print("Default: {}".format(inp))
        if inp == 'x':
            return self.do_exit(inp)
        command = shlex.split(inp)
        redirect_symbols = ['<', '>', '>>']
        intersection = [i for i in redirect_symbols if i in command]
        if intersection:  # if redirection symbol in input
            self.redirection(command)
        elif '|' in inp:
            self.pipeline(inp)
        else:
            # command = shlex.split(inp)
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

    def redirection(self, input):
        print(f'Redirected to: {input[-1]}')
        if '<' in input:
            idx = input.index('<')
            command = input[:idx]
            file = input[idx+1]
            child_pid = os.fork()
            if child_pid == 0 and file:
                fd = os.open(file, os.O_RDONLY, 0o644)
                os.dup2(fd, sys.stdin.fileno())
                os.execvp(command[0], command)
            else:
                os.waitpid(child_pid, 0)
        elif '>' in input:
            idx = input.index('>')
            command = input[:idx]
            file = input[idx + 1]
            child_pid = os.fork()
            if child_pid == 0 and file:
                # file write only, create if not exist
                fd = os.open(file, os.O_WRONLY | os.O_CREAT, 0o644)
                # redirection stdout
                os.dup2(fd, sys.stdout.fileno())
                # os.dup2(fd, sys.stderr.fileno()) # error msg
                os.execvp(command[0], command)
            else:
                os.waitpid(child_pid, 0)
        elif '>>' in input:  # append to file
            idx = input.index('>>')
            command = input[:idx]
            file = input[idx + 1]
            child_pid = os.fork()
            if child_pid == 0 and file:
                fd = os.open(file, os.O_APPEND | os.O_WRONLY | os.O_CREAT, 0o644)
                os.dup2(fd, sys.stdout.fileno())
                os.execvp(command[0], command)
            else:
                os.waitpid(child_pid, 0)

    def pipeline(self, input):
        cmd = input.split('|')
        args_list = [i.strip().split() for i in cmd]
        # print(args_list)
        children_pids = []
        new_fds, old_fds = [], []

        def _clean_up(error: OSError) -> None:
            map(lambda _pid: os.kill(_pid, signal.SIGKILL), children_pids)
            print(f'{args_list[i][0]}: {error}', file=sys.stderr)

        pid = -1
        try:
            for i in range(len(args_list)):
                if i < len(args_list) - 1:  # if next cmd exists
                    new_fds = os.pipe()     # continue to build pipe

                pid = os.fork()
                if pid == 0:
                    if i < len(args_list) - 1:  # if next cmd exists
                        os.close(new_fds[0])
                        os.dup2(new_fds[1], sys.stdout.fileno())
                        os.close(new_fds[1])
                    if i > 0:  # if there is a previous cmd
                        os.dup2(old_fds[0], sys.stdin.fileno())
                        os.close(old_fds[0])
                        os.close(old_fds[1])
                    os.execvp(args_list[i][0], args_list[i])

                else:
                    children_pids.append(pid)
                    if i > 0:
                        os.close(old_fds[0])
                        os.close(old_fds[1])
                    if i < len(args_list) - 1:
                        old_fds = new_fds

            self.jobs.append(('fg', children_pids))
            try:
                for i in children_pids:
                    os.waitpid(i, 0)
                self.jobs.pop()
            except ChildProcessError:
                pass

        except OSError as e:
            _clean_up(e)
            if pid == 0:
                exit(1)
            else:
                return


if __name__ == '__main__':
    if len(sys.argv) > 1:
        # accept command line arguments
        MyShell().onecmd(' '.join(sys.argv[1:]))
    else:
        MyShell().cmdloop()


