import os
import subprocess


# Basically a unique string that will never show up in the output (hopefully)
COMMAND_SEPARATOR = "COMMAND_SEPARATOR===??!<>239'_"

class GfRepl(object):
    def __init__(self, gf_bin = 'gf'):
        self.pipe = os.pipe()   # (read, write)
        self.gfproc = subprocess.Popen((gf_bin, '--run'),
                          stdin = subprocess.PIPE,
                          stderr = self.pipe[1],
                          stdout = self.pipe[1])
        self.commandcounter = 0
        self.infile = os.fdopen(self.pipe[0])

        # catch any initial messages
        sep = self.__writeSeparator()
        self.gfproc.stdin.flush()
        self.initialOutput = self.__getOutput(sep)

    def __writeCmd(self, cmd):
        if not cmd.endswith('\n'):
            cmd += '\n'
        self.gfproc.stdin.write(str.encode(cmd))
        self.commandcounter += 1

    def __writeSeparator(self):
        sep = COMMAND_SEPARATOR + str(self.commandcounter)
        self.gfproc.stdin.write(str.encode(f"ps \"{sep}\"\n"))
        return sep

    def __getOutput(self, sep):
        """ read lines until sep found """
        output = ""
        for line in self.infile:
            if line.rstrip() == sep:
                return output
            output += line


    def handleLine(self, cmd):
        """ forwards a command to the GF Repl and returns the output """
        self.__writeCmd(cmd)
        sep = self.__writeSeparator()
        self.gfproc.stdin.flush()
        return self.__getOutput(sep)


if __name__ == "__main__":
    import sys
    gfrepl = GfRepl()
    print(gfrepl.initialOutput)
    while True:
        line = input("> ")
        print(gfrepl.handleLine(line))
