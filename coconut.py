
"""
Transporting a coconut.
Design issue:
There are 2 types of movement:
  Normal movement. Forwards or backwards. No jet stream. Normal movement can be interrupted at any time.
  Jet stream movement. Jet stream movement can be entered and exited only at certain points.
Journey goes from 0 to end of last jet stream

Okay, not going to bother with robustness this time.

Algorithmic approach: Use 2 data structures.
  1 is the paths, with the jetstreams for each and their last open points. Seed with the 0-length path going nowhere.
  2 is the jet streams, sorted by starting position, ascending.
For each jet stream, consider a (non-empty) collection of paths.
  One path is the optimal path to add a stream to it.
    Optimal is defined as being the path with the lowest cost for the bird to reach the stream's starting position.
    An optimal path is potentially the optimal path for the next jetstream, too.
  Now we need to think about what to do with the non-optimal paths.
    If the non-optimal path requires going backwards, then it might be optimal for later jetstreams.
      Keep for later.
    If the non-optimal path doesn't require going backwards, then it will be non-optimal for later jetstreams.
      Do not consider further.
  We can do this by testing a path for whether it's optimal, and separately for whether it's forwards.
    I'm going to (conceptually) iterate over these things twice.
Note the asymptotic efficiency. Where the jetstreams do not overlap, the time efficiency of the program is O(n) with a very small constant.
Where they do overlap, the time efficiency is O(n*j) where j is the number of streams that overlap.
Just iterating over the paths twice in this loop does not affect the asymptotic efficiency, but does affect the overall efficiency.

At the end, take the paths, and find the lowest distance of these.

Going to use a functional approach: Do not mutate a data structure once it has finished being built, and build it in a very simple manner. Unless benchmarks tell me otherwise.
"""

import sys


class Jetstream:
    """Jetstream class to hold data and representation of a jetstream.

    Note: Start and end as in normal Unix convention. The end of one Jetstream may be the start of the next.

    Static objects:
    
    start -- Starting point
    end -- Where the bird ends up
    cost -- Cost of riding this jetstream
    """
    def __init__(self, start, end, cost):
        self.start = start
        self.end = end
        self.cost = cost
    def __str__(self):
        return '(' + str(self.start) + ',' + str(self.end) + ')'

class Path:
    """Path class. To hold a path.

    Static objects:

    weight -- Open-air cost of flying
    open -- Where the open air starts again
    cost -- How much energy it takes to get to this open point
    jetstreams -- A list of jetstreams in this path.

    Functions:

    pathcost() -- How much it would take to go to a certain point via open air after going on this path
    forward() -- Whether the bird would be moving forward to go to this point
    """
    def __init__(self,*,weight=1,predecessor=None,jetstream=None):
        """__init__()
        
        Two ways to construct: New path, and adding a jetstream to a path.
        Path(weight = [n]) -- A 0-jetstream path with a certain open-air weight
        Path(predecessor = [pathlike object], jetstream = [new stream]) -- A new path with the previous path's jetstreams, adding a new jetstream

        It's the responsibility of the caller to check that the new jetstream makes sense to add.
        """
        if predecessor == None or jetstream == None:
            self.weight = weight
            self.open = 0
            self.cost = 0
            self.jetstreams = []
        else:
            self.weight = predecessor.weight
            self.open = jetstream.end
            self.cost = predecessor.cost + jetstream.cost + self.weight * abs(jetstream.start - predecessor.open)
            self.jetstreams = predecessor.jetstreams + [jetstream]
    def pathcost(self,position):
        """pathcost(position)

        It's the responsibility of the caller to check that the position makes sense to calculate.
        """
        return self.cost + self.weight * abs(position - self.open)
    def forward(self, position):
        """forward(position)

        True if the bird would be moving forward from this path to this position
        """
        return position >= self.open
    def __str__(self):
        return '[' + ', '.join(str(i) for i in self.jetstreams) + ']'

def minimumpath(paths, position):
    """minimumpath(paths, position)

    Takes an iterable of paths and returns the path with the lowest cost for the position.
    Prerequisite: All of the paths are actually valid for that position, otherwise the calculation is wrong.
    """
    return min(paths,key=lambda path: path.pathcost(position))

def finalminimum(paths):
    """fininalminimum(paths)

    Takes an iterable of paths and returns a tuple of the lowest-cost path for the longest distance jetstream in the paths, and the final cost over that path.
    """
    finaldest = max(paths,key=lambda path: path.open).open
    minimum = minimumpath(paths,finaldest)
    return minimum,minimum.pathcost(finaldest)

def calcpath(paths,streams):
    """calcpath(paths, streams)

    Takes an initial iterable of paths and an in-order iterable of jetstreams to add, and returns whatever finalminimum() returns.
    Which is a tuple of the lowest-cost path and the final cost over that path.

    Function signature and operation inspired by recursive Scheme style, but turned into an iteration because Python is more efficient with iteration than recursion.
    And this problem is small enough that I don't need to make it execute in parallel, or reuse any data structures.

    Normal way to call this:
    calcpath([Path(weight=[n])],jetstreams)

    Function arguments are not modified.
    """
    for jet in streams:
        laters = [path for path in paths if not path.forward(jet.start)] # Paths that are kept for the next streams.
        # The order of paths in these data structures does not matter. Just using lists because convenient.
        minimum = minimumpath(paths,jet.start)
        if minimum.forward(jet.start): laters.append(minimum) # If the optimal is backwards, it was already kept.
        laters.append(Path(predecessor=minimum,jetstream=jet))
        paths = laters
    return finalminimum(paths)

def main():
    if len(sys.argv) != 2:
        print("Usage: " + sys.argv[0] + " [paths.txt]")
        sys.exit(1)
    # Just going to act like this file is here and non-malicious, etc.
    file = open(sys.argv[1])
    weight = int(file.readline())
    # Neato unreadable functional programming. Create a sorted list of jetstreams by
    # reading lines, splitting the lines into words, and parsing the words as ints for the Jetstream constructor.
    jets = sorted((Jetstream(int(i[0]),int(i[1]),int(i[2])) for i in (line.split() for line in file.readlines())),key = lambda stream: stream.start)
    file.close()
    seed = Path(weight=weight)
    path, cost = calcpath([seed],jets)
    print(cost)
    print(path)

if __name__ == '__main__':
    main()
