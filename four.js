def uniformCostSearch(tree, curIndex):
    pq = util.PriorityQueue()
    actions = []
    state = tree[curIndex]
    visitedPos = []

    cost = 0
    pq.push(state, cost)

    while not pq.isEmpty():
        curPos, actions = pq.pop()
        if problem.isGoalState(curPos):
            return cost
        if curPos not in visitedPos:
            for s in problem.getSuccessors(curPos):
                if s[0] not in visitedPos:
                    newActions = actions + [s[1]]
                    cost = problem.getCostOfActions(newActions)
                    pq.push((s[0], newActions), cost)
        visitedPos.append(curPos)

    return actions
