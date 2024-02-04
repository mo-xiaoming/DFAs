# `^`, `$`, `.`, `*`, `+`, `?`, `|`
# `.*?`, `.+?`, `.{m,n}?`
# `{m}`, `{m,}`, `{,n}`, `{m,n}`
# `[]` character set, `[^]` negated character set
# group `(...)` and named group `(?<name>...)`
# backtracing `\n`
# lookahead `(?=...)` and `(?!...)`
# lookbehind `(?<=...)` and `(?<!...)`

# Derivatives of Regular Expressions
# Glushkov's Construction Algorithm

from dataclasses import dataclass
from typing import Set


def insert_concatenation_operators(infix):
    infix = list(infix)
    for i in range(len(infix) - 1, 0, -1):
        if (infix[i].isalnum() or infix[i] in (".", "(")) and (
            infix[i - 1].isalnum() or infix[i - 1] in (")", ".", "*", "+", "?")
        ):
            infix.insert(i, "~")
    return "".join(infix)


def shunting_yard(infix):
    specials = {"*": 60, "+": 60, "?": 60, "~": 40, "|": 20}

    pofix, stack = "", ""

    for c in infix:
        if c == "(":
            stack = stack + c
        elif c == ")":
            while stack[-1] != "(":
                pofix, stack = pofix + stack[-1], stack[:-1]
            stack = stack[:-1]
        elif c in specials:
            while stack and specials.get(c, 0) <= specials.get(stack[-1], 0):
                pofix, stack = pofix + stack[-1], stack[:-1]
            stack = stack + c
        else:
            pofix = pofix + c

    while stack:
        pofix, stack = pofix + stack[-1], stack[:-1]

    return pofix


class State:
    label, edge1, edge2 = None, None, None


@dataclass
class NFA:
    start: State
    accept: State


def thompsons_construction(pofix):
    if len(pofix) == 0:
        # empty pattern
        #
        # start == accept
        s = State()
        return NFA(s, s)

    nfaStack = []

    for c in pofix:
        if c == "|":
            #                                               edge1
            #                 > --> nfa1.start  nfa1.accept -->
            #         edge1  /                                  \
            # start ------->                                     >-----> accept
            #         edge2  \                                  /
            #                 > --> nfa2.start  nfa2.accept -->
            #                                               edge1
            #
            # stack <- (start, accept)

            nfa2, nfa1 = nfaStack.pop(), nfaStack.pop()
            start, accept = State(), State()
            start.edge1, start.edge2 = nfa1.start, nfa2.start
            nfa1.accept.edge1, nfa2.accept.edge1 = accept, accept
            nfaStack.append(NFA(start, accept))
        elif c == "~":
            #
            #                           edge1
            #  nfa2.start  nfa2.accept -------> nfa1.start  nfa1.accept
            #
            # stack <- (nfa1.start, nfa2.accept)
            nfa1, nfa2 = nfaStack.pop(), nfaStack.pop()
            nfa2.accept.edge1 = nfa1.start
            nfaStack.append(NFA(nfa2.start, nfa1.accept))
        elif c == "*":
            #                          edge1
            #                    +----------------+
            #          edge1     v                |      edge2
            # start -+-------> nfa.start      nfa.accept -------+--> accept
            #        |                                          |
            #        +------------------------------------------+
            #          edge2
            #
            # stack <- (start, accept)
            nfa1 = nfaStack.pop()
            start, accept = State(), State()
            start.edge1, start.edge2 = nfa1.start, accept
            nfa1.accept.edge1, nfa1.accept.edge2 = nfa1.start, accept
            nfaStack.append(NFA(start, accept))
        elif c == "+":
            #                          edge1
            #                    +----------------+
            #          edge1     v                |      edge2
            # start ---------> nfa.start      nfa.accept ----------> accept
            #
            # stack <- (start, accept)
            nfa1 = nfaStack.pop()
            start, accept = State(), State()
            start.edge1 = nfa1.start
            nfa1.accept.edge1, nfa1.accept.edge2 = nfa1.start, accept
            nfaStack.append(NFA(start, accept))
        elif c == "?":
            #          edge1                              edge1
            # start -+-------> nfa.start      nfa.accept -------+--> accept
            #        |                                          |
            #        +------------------------------------------+
            #          edge2
            #
            # stack <- (start, accept)
            nfa1 = nfaStack.pop()
            accept, start = State(), State()
            start.edge1, start.edge2 = nfa1.start, accept
            nfa1.accept.edge1 = accept
            nfaStack.append(NFA(start, accept))
        else:  # char or dot
            #                    edge1
            # start[lable:c] -----------> accept
            #
            # stack <- (start, accept)
            start, accept = State(), State()
            start.label, start.edge1 = c, accept
            nfaStack.append(NFA(start, accept))

    assert len(nfaStack) == 1, f"len(nfaStack)={len(nfaStack)}"
    return nfaStack.pop()


def follow_epsilons(state: State) -> Set[State]:
    states: Set[State] = set()
    states.add(state)

    if state.label is None:
        if state.edge1 is not None:
            states |= follow_epsilons(state.edge1)
        if state.edge2 is not None:
            states |= follow_epsilons(state.edge2)

    return states


def match(infix, string):
    infix = insert_concatenation_operators(infix)
    postfix = shunting_yard(infix)
    nfa = thompsons_construction(postfix)

    current = follow_epsilons(nfa.start)
    nexts = set()

    for c in string:
        for state in current:
            if state.label in (c, "."):
                nexts |= follow_epsilons(state.edge1)
        current = nexts
        nexts = set()

    if nfa.accept in current:
        return True

    # empty pattern matches empty string
    if not string and nfa.start == nfa.accept:
        return True

    return False
