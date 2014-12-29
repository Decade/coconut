import sys
"""
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
    I know that any later jet stream under consideration will start later than this one, so higher than the lowest cost is higher for those, too.
  One group is not valid to add to them. Keep these, too.
At the end, take the open air slots, and find the lowest distance of these.
"""

class Jetstream:
    def __init__(self, start, end, cost):
        self.start = start
        self.end = end
        self.cost = cost
    def __unicode__(self):
        return '(' + str(self.start) + ',' + str(self.end) + ')'

class Path:
    def __init__(self,*,weight=1,predecessor=None,jetstream=None):
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
        return self.cost + self.weight * (position - self.open)
    def isvalid(self,position):
        return position >= self.open
    def __unicode__(self):
        return '[' + ', '.join(i.__unicode__() for i in self.jetstreams) + ']'

def minimumpath(paths, position):
    return min(paths,key=lambda x: x.pathcost(position))

def finalminimum(paths):
    finaldest = max(paths,key=lambda x: x.open)
    minimum = minimumpath(paths,finaldest.open)
    return minimum,minimum.pathcost(finaldest.open)

def calcpath(paths,streams):
    for jet in streams:
        valids = []
        laters = []
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
        sys.exit(1)
    file = open(sys.argv[1])
    weight = int(file.readline())
    jets = sorted((Jetstream(int(i[0]),int(i[1]),int(i[2])) for i in (i.split() for i in file.readlines())),key = lambda x: x.start)
    file.close()
    seed = Path(weight=weight)
    path, cost = calcpath([seed],jets)
    print(cost)
    print(path.__unicode__())

if __name__ == '__main__':
    main()
