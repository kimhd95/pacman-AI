def minimaxTree_node(self, gameState, curLevel, maxDepth, parentNode):
    n = gameState.getNumAgents()
    depth = curLevel // n + 1
    agentIndex = curLevel % n

    if agentIndex == self.index and curLevel >= n \
            and (gameState.getAgentPosition(self.index)==gameState.getInitialAgentPosition(self.index) \
            or gameState.isOver() \
            or depth > maxDepth):
      return self.evaluate_invade(gameState)


    legalActions = gameState.getLegalActions(agentIndex)

    if agentIndex == self.index:  # pacman
      maxV = -math.inf
      for action in legalActions:
        successor = gameState.generateSuccessor(agentIndex, action)
        curNode = [0, action, 'pacman', []]       # [value, action, agent, parentNode]
        v = self.minimaxTree_node(successor, curLevel + 1, maxDepth, curNode)
        maxV = max(v, maxV)
        curNode[0] = v  # [[action, v], []]
        parentNode[3] = curNode
      return maxV

    elif self.checkDangerOfAgent(gameState, agentIndex):  # ghost
      myPos = gameState.getAgentPosition(self.index)
      ghostPositions = []
      ghostActions = []

      for action in legalActions:
        successor = gameState.generateSuccessor(agentIndex, action)
        ghostPositions.append(successor.getAgentPosition(agentIndex))  # [Position, Action]
        ghostActions.append(action)
      # print(ghostPositions)
      distList = [self.getMazeDistance(myPos, ghost) for ghost in ghostPositions]

      ## Pacman die

      minDistance = min(distList)
      greedyIndex = distList.index(minDistance)
      greedyAction = ghostActions[greedyIndex]
      successor = gameState.generateSuccessor(agentIndex, greedyAction)
      curNode = [0, greedyAction, 'ghost', []]
      v = self.minimaxTree_node(successor, curLevel + 1, maxDepth, curNode)

      curNode[0] = v  # [[action, score], []]
      parentNode[3] = curNode
      return v

    else:
      return self.minimaxTree_node(gameState, level + 1, maxDepth, parentNode)
