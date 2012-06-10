from collections import deque
from django.utils.datastructures import SortedDict
from .exceptions import CircularDependency


class SortedSet(SortedDict):
    """
    A variant of set() that maintains insert ordering.
    """

    def __init__(self, data=tuple()):
        self.extend(data)

    def __str__(self):
        return "SortedSet(%s)" % list(self)

    def add(self, value):
        self[value] = True

    def remove(self, value):
        del self[value]

    def extend(self, iterable):
        [self.add(k) for k in iterable]


def depends(target, get_children):
    """
    Given a single target migration and a function to get its deps,
    returns the list of migrations to apply, in order.
    """
    result = SortedSet(reversed(list(dfs(target, get_children))))
    return list(result)


def dfs(start, get_children):
    "Nice entry-point to depth-first search"
    return flatten(_dfs(start, get_children, []))


def _dfs(start, get_children, path):
    "Actual depth-first search worker function"
    if start in path:
        raise CircularDependency(path[path.index(start):] + [start])
    path.append(start)
    yield start
    try:
        children = sorted(get_children(start), key=lambda x: str(x))
    except AttributeError:
        # Print this else it'll get masked by flatten()
        import traceback
        traceback.print_exc()
        raise
    if children:
        # We need to apply all the migrations this one depends on
        yield (_dfs(n, get_children, path) for n in children)
    path.pop()


def flatten(*stack):
    "Given a nested set of iterables, flattens it into a single iterable"
    stack = deque(stack)
    while stack:
        try:
            x = stack[0].next()
        except AttributeError:
            stack[0] = iter(stack[0])
            x = stack[0].next()
        except StopIteration:
            stack.popleft()
            continue
        if hasattr(x, '__iter__'):
            stack.appendleft(x)
        else:
            yield x
