
"""
Transporting a coconut.
Design issue:
There are 2 types of movement:
  Normal movement. No jet stream. Normal movement can be interrupted at any time.
  Jet stream movement. Jet stream movement can be entered and exited only at certain points.
Journey goes from 0 to last jet stream

Okay, not going to bother with robustness this time.

Algorithmic approach: Use 2 data structures.
  1 is the open air slots, with the path for each. Seed with the 0-length path going nowhere.
  2 is the jet streams, sorted by starting position, ascending.
For each jet stream, cycle through the open air slots, separating them into 2 groups.
  One group is valid to add to them. Find the lowest cost of these, and add to it. Keep the lowest cost and the added.
    I know that any later jet stream under consideration will start at least as late as this one, so higher than the lowest cost is higher for those, too.
  One group is not valid to add to them. Keep these, too.
At the end, take the open air slots, and find the lowest distance of these.

Going to use a functional approach: Do not mutate a data structure once it has finished being built, and build it in a very simple manner.
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

    pathcost() -- How much it would take to go a certain distance past the open point using this path
    invalid() -- Whether the pathcost calculation would make sense for this certain distance

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
            self.cost = predecessor.cost + jetstream.cost + self.weight * (jetstream.start - predecessor.open)
            self.jetstreams = predecessor.jetstreams + [jetstream]
    def pathcost(self,position):
        """pathcost(position)

        It's the responsibility of the caller to check that the position makes sense to calculate.
        """
        return self.cost + self.weight * (position - self.open)
    def isvalid(self,position):
        """invalid(position)

        Validity is defined as being in open air at that position.
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

    Takes an iterable of paths and returns a tuple of the lowest-cost path for the longest distance tuple in that path, and the final cost over that path.
    """
    finaldest = max(paths,key=lambda path: path.open)
    minimum = minimumpath(paths,finaldest.open)
    return minimum,minimum.pathcost(finaldest.open)

def calcpath(paths,streams):
    """calcpath(paths, streams)

    Takes an initial iterable of paths and a sorted iterable of jetstreams to add, and returns whatever finalminimum() returns.
    Which is a tuple of the lowest-cost path and the final cost over that path.

    Function signature and operation inspired by recursive Scheme style, but turned into an iteration because Python is more efficient with iteration than recursion.
    And this problem is small enough that I don't need to make it execute in parallel, or reuse any data structures.

    Normal way to call this:
    calcpath([Path(weight=[n])],jetstreams)

    Function arguments are not modified.
    """
    for jet in streams:
        valids = [] # Paths that are valid to add a jetstream to.
        laters = [] # Paths that are kept for the next streams.
        # The order of paths in these data structures does not matter.
        for path in paths:
            if path.isvalid(jet.start):
                valids.append(path)
            else:
                laters.append(path)
        minimum = minimumpath(valids,jet.start)
        laters.append(minimum)
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
