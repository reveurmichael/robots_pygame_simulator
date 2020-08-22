__author__ = "lunde chen"
__email__  = "lundechen@shu.edu.cn"


def points_adjoin(p1, p2):
    return (-1 <= p1[0]-p2[0] <= 1 and p1[1] == p2[1] or
             p1[0] == p2[0] and -1 <= p1[1]- p2[1] <= 1)

def adjoins(pts, p):
    return any(points_adjoin(p, p2) for p2 in pts)

def is_connected(pos):
    regions = []
    for p in pos:
        # find all adjoining regions
        adjregs = [r for r in regions if adjoins(r, p)]
        if adjregs:
            adjregs[0].add(p)
            if len(adjregs) > 1:
                # joining more than one reg, merge
                regions[:] = [r for r in regions if r not in adjregs]
                regions.append(reduce(set.union, adjregs))
        else:
            # not adjoining any, start a new region
            regions.append(set([p]))
    #print "||regions|| = ", len(regions)
    return len(regions) == 1

def test():
    pos = [(1, 2), (2, 3), (3, 4)]
    pos = [(1, 2), (1, 3), (1, 4), (2, 3), (2, 4), (2, 5)]
    print is_connected(pos)
