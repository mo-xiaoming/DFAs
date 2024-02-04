# `^`, `$`, `.`, `*`, `+`, `?`, `|`
# `{m}`, `{m,}`, `{,n}`, `{m,n}`
# `[]` character set
# group `(...)` and named group `(?<name>...)`
# backtracing `\n`
# lookahead `(?=...)` and `(?!...)`
# lookbehind `(?<=...)` and `(?<!...)`


from dataclasses import dataclass


def shunting_yard(infix):
    specials = {"*": 60, "+": 55, "?": 50, "|": 20}

    pofix, stack = "", ""

    for c in infix:
        if c == "(":
            stack = stack + c
        elif c == ")":
            while stack[-1] != "(":
                pofix, stack = pofix + stack[-1], stack[:-1]
                if len(stack) == 0:
                    raise Exception("Missing opening bracket")
            stack = stack[:-1]
        elif c in specials:
            while stack and specials.get(c, 0) <= specials.get(stack[-1], 0):
                pofix, stack = pofix + stack[-1], stack[:-1]
            stack = stack + c
        else:
            pofix = pofix + c

    while stack:
        if stack[-1] == "(":
            raise Exception("Missing closing bracket")
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
        s = State()
        return NFA(s, s)

    nfaStack = []

    for c in pofix:
        if c == "|":
            #                                                edge1
            #                 + --> nfa1.start  nfa1.accept -->
            #         edge1  /                                  \
            #               /                                    \
            # start ------->                                      +-----> accept
            #               \                                    /
            #         edge2  \                                  /
            #                 + --> nfa2.start  nfa2.accept -->
            #                                                 edge1
            #
            # stack <- (start, accept)

            nfa2, nfa1 = nfaStack.pop(), nfaStack.pop()
            start, accept = State(), State()
            start.edge1, start.edge2 = nfa1.start, nfa2.start
            nfa1.accept.edge1, nfa2.accept.edge1 = accept, accept
            nfaStack.append(NFA(start, accept))
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

    # final concatenation
    #                                    edge1
    # nfaPopped.start  nfaPopped.accept -------> nfa.start  nfa.accept
    #
    # new nfa = (nfaPopped.start, nfa.accept)
    result = nfaStack.pop()
    while len(nfaStack) > 0:
        f = nfaStack.pop()
        f.accept.edge1 = result.start
        result = NFA(f.start, result.accept)
    return result


def follow_epsilons_or_dot(state):
    states = set()
    states.add(state)

    # if state has a label of None (epsilon) or wildcard (dot)
    if state.label is None:
        if state.edge1 is not None:
            states |= follow_epsilons_or_dot(state.edge1)
        if state.edge2 is not None:
            states |= follow_epsilons_or_dot(state.edge2)

    return states


# Matches a string to an infix regular expression
def match(infix, string):
    # Shunt and compile the regular expression
    postfix = shunting_yard(infix)
    nfa = thompsons_construction(postfix)

    # The current set of states and the next set of states
    current = set()
    nexts = set()

    # Add the start state to the current set
    current |= follow_epsilons_or_dot(nfa.start)

    # loop through each character in the string
    for s in string:
        # loop through the current set of states
        for c in current:
            # Check to see if state is labelled 's'
            if c.label in (s, "."):  # char or dot
                nexts |= follow_epsilons_or_dot(c.edge1)
        # set current to next and clears out next
        current = nexts
        # next is back to an empty set
        nexts = set()

    # Checks if the accept state is in the set for current state
    if nfa.accept in current:
        return True

    if not string and nfa.start == nfa.accept:
        return True

    return False


## Testcases for the matchString function
# infixes = ["a.b.c*", "a.(b|d).c*", "(a.(b|d))*", "a.(b.b)*.c"]
# strings = ["", "abc", "abbc", "abcc", "abad", "abbbc"]
#
# for i in infixes:
#    for s in strings:
#        print(match(i, s), i, s)
#
