#!/usr/bin/env python3
"""
Change a git branch using arrow keys.
"""

from __future__ import annotations
import curses
import subprocess
import locale
from dataclasses import dataclass
from typing import Optional

LOG_ENABLE = False


class Debugger:
    """
    Show debug messages on curses window.
    """

    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.counter = 0
        self.max_rows, self.max_cols = stdscr.getmaxyx()
        self.col_width = 20

    def log(self, *message):
        if not LOG_ENABLE:
            return
        xpos = self.max_cols - self.col_width
        try:
            self.stdscr.addstr(self.counter, xpos, ' '.join(map(str, message)))
            self.counter += 1
        except curses.error:
            self.counter = 0
            self.stdscr.addstr(self.counter, xpos, ' '.join(map(str, message)))


@dataclass
class GitBranch:
    refname: str
    authordata: str
    subject: str


class GitLib:

    def get_branches(self) -> list[GitBranch]:
        stdout = subprocess.check_output(
            ['git', 'branch', '-a',
             '--format=%(refname:short)\t%(authordate:relative)\t%(subject)'])

        def parse_row(row: str):
            row = row.split('\t')
            return GitBranch(refname=row[0], authordata=row[1], subject=row[2])

        return list(map(
            parse_row, filter(None, stdout.decode('utf-8').split('\n'))))

    def checkout(self, branch_name: str):
        # FIXME: Sloppy code.
        branch_name = branch_name.replace('origin/', '')
        subprocess.check_call(['git', 'checkout', branch_name])


class GitChangeBranchUI:
    COLOR_ACTIVE = 1
    # COLOR_HEADER = 2
    REFNAME_WIDTH = 24
    AUTHORDATA_WIDTH = 16

    def __init__(self, stdscr):
        self.stdscr = stdscr
        locale.setlocale(locale.LC_ALL, '')
        self.initialize_colors()
        stdscr.refresh()
        self.max_rows, self.max_cols = stdscr.getmaxyx()
        self.debugger = Debugger(stdscr)
        self.gitlib = GitLib()
        self.git_branches = self.gitlib.get_branches()
        self.position = 0

    def initialize_colors(self):
        curses.use_default_colors()
        curses.init_pair(self.COLOR_ACTIVE, curses.COLOR_BLACK,
                         curses.COLOR_YELLOW)
        # curses.init_pair(self.COLOR_HEADER, curses.COLOR_BLACK,
        #                  curses.COLOR_CYAN)

    def format_git_branch(self, git_branch: GitBranch) -> str:
        subject_width = self.max_cols - sum([2, self.REFNAME_WIDTH, 1, 16, 1])
        template = '{:<%s} {:<%s} {}' % (
            self.REFNAME_WIDTH, self.AUTHORDATA_WIDTH)
        return template.format(
            git_branch.refname[:self.REFNAME_WIDTH],
            git_branch.authordata[:self.AUTHORDATA_WIDTH],
            git_branch.subject[:subject_width])

    def render(self):
        for i, git_branch in enumerate(self.git_branches):
            if i == self.position:
                self.stdscr.addstr(
                    i, 0, f'> {self.format_git_branch(git_branch)}',
                    curses.color_pair(self.COLOR_ACTIVE))
            else:
                self.stdscr.addstr(
                    i, 0, f'  {self.format_git_branch(git_branch)}')
        self.stdscr.addstr(self.position, 0, '')

    def up(self):
        self.debugger.log('up')
        if self.position > 0:
            self.position -= 1

    def down(self):
        self.debugger.log('down')
        if self.position < len(self.git_branches) - 1:
            self.position += 1

    def enter(self) -> GitBranch:
        branch = self.git_branches[self.position]
        branch_name = branch.refname
        self.debugger.log(f'enter: {branch_name}')
        self.gitlib.checkout(branch_name)
        return branch

    def serve(self) -> Optional[GitBranch]:
        while True:
            self.render()
            self.stdscr.refresh()
            # wait for keypress
            c = self.stdscr.getch()
            if c in (14, 106, 258):  # ↓
                self.down()

            elif c in (16, 107, 259):  # ↑
                self.up()
            elif c == 10:
                # Enter
                return self.enter()
            elif c == ord('q'):
                return  # Exit the while


def start_ui(stdscr):
    ui = GitChangeBranchUI(stdscr)
    return ui.serve()


def main():
    try:
        git_branch = curses.wrapper(start_ui)
        if git_branch:
            print(git_branch.refname)
    except subprocess.CalledProcessError:
        print('Not a git repository?')


if __name__ == '__main__':
    main()
