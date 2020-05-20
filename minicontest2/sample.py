from captureAgents import CaptureAgent
import random, time, util
from game import Directions
import game
from game import Agent
import math
from util import nearestPoint

MAXDEPTH = 3

#################
# Team creation #
#################

def createTeam(firstIndex, secondIndex, isRed,
               first = 'InvadeAgent', second = 'InvadeAgent'):
  """
  This function should return a list of two agents that will form the
  team, initialized using firstIndex and secondIndex as their agent
  index numbers.  isRed is True if the red team is being created, and
  will be False if the blue team is being created.
  As a potentially helpful development aid, this function can take
  additional string-valued keyword arguments ("first" and "second" are
  such arguments in the case of this function), which will come from
  the --redOpts and --blueOpts command-line arguments to capture.py.
  For the nightly contest, however, your team will be created without
  any extra arguments, so you should make sure that the default
  behavior is what you want for the nightly contest.
  """
  # The following line is an example only; feel free to change it.
  return [eval(first)(firstIndex), eval(second)(secondIndex)]

##########
# Agents #
##########

class DummyAgent(CaptureAgent):
  """
  A Dummy agent to serve as an example of the necessary agent structure.
  You should look at baselineTeam.py for more details about how to
  create an agent as this is the bare minimum.
  """


  def registerInitialState(self, gameState):
    """
    This method handles the initial setup of the
    agent to populate useful fields (such as what team
    we're on).
    A distanceCalculator instance caches the maze distances
    between each pair of positions, so your agents can use:
    self.distancer.getDistance(p1, p2)
    IMPORTANT: This method may run for at most 15 seconds.
    """

    '''
    Make sure you do not delete the following line. If you would like to
    use Manhattan distances instead of maze distances in order to save
    on initialization time, please take a look at
    CaptureAgent.registerInitialState in captureAgents.py.
    '''
    #CaptureAgent.registerInitialState(self, gameState)

    '''
    Your initialization code goes here, if you need any.
    '''
    self.start = gameState.getAgentPosition(self.index)
    CaptureAgent.registerInitialState(self, gameState)


  def chooseAction(self, gameState):
    """
    Picks among actions randomly.
    """
    actions = gameState.getLegalActions(self.index)

    '''
    You should change this in your own agent.
    '''

    # You can profile your evaluation time by uncommenting these lines
    # start = time.time()
    values = [self.evaluate(gameState, a) for a in actions]
    # print 'eval time for agent %d: %.4f' % (self.index, time.time() - start)

    maxValue = max(values)
    bestActions = [a for a, v in zip(actions, values) if v == maxValue]

    foodLeft = len(self.getFood(gameState).asList())

    if foodLeft <= 2:
      bestDist = 9999
      for action in actions:
        successor = self.getSuccessor(gameState, action)
        pos2 = successor.getAgentPosition(self.index)
        dist = self.getMazeDistance(self.start, pos2)
        if dist < bestDist:
          bestAction = action
          bestDist = dist
      return bestAction

    return random.choice(bestActions)

    #return random.choice(actions)



  def getSuccessor(self, gameState, action):
    """
    Finds the next successor which is a grid position (location tuple).
    """
    successor = gameState.generateSuccessor(self.index, action)
    pos = successor.getAgentState(self.index).getPosition()
    if pos != nearestPoint(pos):
      # Only half a grid position was covered
      return successor.generateSuccessor(self.index, action)
    else:
      return successor

  def evaluate(self, gameState, action):
    """
    Computes a linear combination of features and feature weights
    """
    features = self.getFeatures(gameState, action)
    weights = self.getWeights(gameState, action)

    # previousObservation = self.getPreviousObservation()
    # if previousObservation:
    #   if previousObservation.getAgentPosition(self.index) == gameState.getAgentPosition(self.index):
    #     print("I am Agnet:", self.index, "I am at: ", gameState.getAgentPosition(self.index), " score:", features * weights)
    #     print(features)
    #     print('action', action)
    return features * weights

  def getFeatures(self, gameState, action):
    """
    Returns a counter of features for the state
    """


    features = util.Counter()
    successor = self.getSuccessor(gameState, action)
    features['successorScore'] = successor
    return features

  def getWeights(self, gameState, action):
    """
    Normally, weights do not depend on the gamestate.  They can be either
    a counter or a dictionary.
    """
    return {'successorScore': 1.0}

  def amIinEnemyRegion(self, gameState):
    pos = gameState.getAgentPosition(self.index)
    if gameState.isOnRedTeam(self.index) and not gameState.isRed(pos):
      return True
    elif gameState.isOnRedTeam(self.index) and gameState.isRed(pos):
      return False
    elif not gameState.isOnRedTeam(self.index) and gameState.isRed(pos):
      return True
    elif not gameState.isOnRedTeam(self.index) and not gameState.isRed(pos):
      return False

  def isThisGuyAGhost(self, gameState, index):
    ghostList = []
    if gameState.isOnRedTeam(self.index):
      enemyList = gameState.getBlueTeamIndices()
      for enemy in enemyList:
        if not gameState.isRed(gameState.getAgentPosition(enemy)):
          ghostList.append(enemy)
    else:
      enemyList = gameState.getRedTeamIndices()
      for enemy in enemyList:
        if gameState.isRed((gameState.getAgentPosition(enemy))):
          ghostList.append(enemy)

    return index in ghostList


class InvadeAgent(DummyAgent):

  def __init__(self, index, timeForComputing = .1):
    # Agent index for querying state
    self.index = index

    # Whether or not you're on the red team
    self.red = None

    # Agent objects controlling you and your teammates
    self.agentsOnTeam = None

    # Maze distance calculator
    self.distancer = None

    # A history of observations
    self.observationHistory = []

    # Time to spend each turn on computing maze distances
    self.timeForComputing = timeForComputing

    # Access to the graphics
    self.display = None
    self.pastIsinEnemyRegion = True       # for initialization
    self.currentIsinEnemyRegion = False
    self.mode = "initial position"
    self.abinitial = True



  def chooseAction(self, gameState):
    # print(self.mode)
    self.currentIsinEnemyRegion = self.amIinEnemyRegion(gameState)


    if gameState.getAgentPosition(self.index) == gameState.getInitialAgentPosition(self.index):
      self.mode = "initial position"

    if self.mode == "initial position":
      if self.currentIsinEnemyRegion:
        self.mode = "AlphaBeta Agent"
        return self.chooseAction(gameState)
      if self.pastIsinEnemyRegion == True and self.currentIsinEnemyRegion == False:
        self.Agent = ChooseInvadePositionAgent(self.index)
        self.Agent.registerInitialState(gameState)
      action = self.Agent.getAction(gameState)
      self.pastIsinEnemyRegion = self.currentIsinEnemyRegion

      return action

    ghostList = self.getOpponents(gameState)
    for ghost in ghostList:
      if self.isThisGuyAGhost(gameState, ghost) == False:
        ghostList.remove(ghost)
      if not ghostList: minGhostDistance = 10
      else:
        minGhostDistance = min(
      [self.getMazeDistance(gameState.getAgentPosition(self.index), gameState.getAgentPosition(ghost)) for ghost in
       ghostList])


    enemies = [gameState.getAgentState(i) for i in self.getOpponents(gameState)]
    invaders = [a for a in enemies if a.isPacman and a.getPosition() != None]

    if self.mode == "goHome Agent" and not self.amIinEnemyRegion(gameState):
      if len(invaders) > 0:
        self.mode = "defensive Agent"
        self.dfinit = True
      else:
        self.mode = "gotoAnother Agent"
        self.gtAinit = True


    if self.mode == "gotoAnother Agent":
      if self.gtAinit == True:
        self.Agent = gotoAnotherPlaceAgent(self.index)
        self.Agent.registerInitialState(gameState)
        self.gtAinit = False
      action = self.Agent.getAction(gameState)
      width = gameState.data.layout.width
      enemies = [gameState.getAgentState(i) for i in self.getOpponents(gameState)]
      invaders = [a for a in enemies if a.isPacman and a.getPosition() != None]
      self.pastIsinEnemyRegion = self.currentIsinEnemyRegion
      if minGhostDistance > 5 and not invaders:
        self.mode = "AlphaBeta Agent"
        self.abinitial = True
      return action


    if self.mode == "defensive Agent":
      if self.dfinit == True:
        self.Agent = DefensiveReflexAgent(self.index)
        self.Agent.registerInitialState(gameState)
        self.dfinit = False
      action = self.Agent.getAction(gameState)
      if len(invaders) == 0:
        self.mode = "gotoAnother Agent"
        self.gtAinit = True
        return self.chooseAction(gameState)
      return action


    if self.getFood(gameState).count() == 0 or \
            gameState.getAgentState(self.index).numCarrying > minGhostDistance - 4 or\
            gameState.data.timeleft < 200 and gameState.getAgentState(self.index).numCarrying != 0:
            # or minGhostDistance < 2

      self.mode = "goHome Agent"
      self.Agent = goHomeAgent(self.index)
      self.Agent.registerInitialState(gameState)
      action = self.Agent.getAction(gameState)
      if self.getFood(gameState).count() > 0 and not self.amIinEnemyRegion(gameState):
        if len(invaders) > 0:
          self.mode = "defensive Agent"
          self.dfinit = True
          return self.chooseAction(gameState)
        else:
          self.mode = "gotoAnother Agent"
          self.gtAinit = True
          return self.chooseAction(gameState)
      return action


    if self.mode == "AlphaBeta Agent":
      if self.pastIsinEnemyRegion == True and self.currentIsinEnemyRegion == False:
        self.mode = "gotoAnother Agent"
        self.gtAinit = True
        return self.chooseAction(gameState)
      if self.pastIsinEnemyRegion == False and self.currentIsinEnemyRegion == True or self.abinitial == True:
        self.Agent = AlphaBetaAgent(self.index)
        self.Agent.registerInitialState(gameState)
        self.abinitial = False
      action = self.Agent.getAction(gameState)
      # if self.pastIsinEnemyRegion == True and self.currentIsinEnemyRegion == False:
      #   self.mode = "initial position"
      # else:
      self.pastIsinEnemyRegion = self.currentIsinEnemyRegion
      return action

    if self.mode == "defensive Agent":
      if self.pastIsinEnemyRegion == True and self.currentIsinEnemyRegion == False:
        self.Agent = DefensiveReflexAgent(self.index)
        self.Agent.registerInitialState(gameState)
        action = self.Agent.getAction(gameState)
        return action

class gotoAnotherPlaceAgent(DummyAgent):


  def getFeatures(self, gameState, action):

    features = util.Counter()
    successor = self.getSuccessor(gameState, action)
    myState = successor.getAgentState(self.index)
    myPos = myState.getPosition()
    height = gameState.data.layout.height
    width = gameState.data.layout.width
    actionList = gameState.getLegalActions(self.index)
    #
    # if myPos >= height // 2:
    #   features['yaxis'] = height-

    enemyIndex = self.getOpponents(successor)
    newGhostStates = []
    for index in enemyIndex:
      ghost = successor.getAgentState(index)
      if self.isThisGuyAGhost(successor, index):
        if ghost.scaredTimer < 5:
          newGhostStates.append(successor.getAgentState(index))

    if len(newGhostStates) > 0:
      minGhostDistance = min([self.getMazeDistance(myPos, ghost.getPosition()) for ghost in newGhostStates])
    else:
      minGhostDistance = 1

    features["minGhostDist"] = minGhostDistance

    # Computes distance to invaders we can see
    enemies = [successor.getAgentState(i) for i in self.getOpponents(successor)]
    invaders = [a for a in enemies if a.isPacman and a.getPosition() != None]
    features['numInvaders'] = len(invaders)
    if len(invaders) > 0:
      dists = [self.getMazeDistance(myPos, a.getPosition()) for a in invaders]
      features['invaderDistance'] = min(dists)

    if action == Directions.STOP: features['stop'] = 1
    rev = Directions.REVERSE[gameState.getAgentState(self.index).configuration.direction]
    if action == rev: features['reverse'] = 1

    width = gameState.getWalls().width
    height = gameState.getWalls().height
    wallMatrix = gameState.getWalls()
    borderList = []
    for i in range(height):
      if not wallMatrix[width // 2][i] == True:
        borderList.append((width // 2, i))
    myPos = successor.getAgentState(self.index).getPosition()
    if abs(myPos[0]-width//2) > 2:
      minDistance = min([self.getMazeDistance(myPos, border) for border in borderList])
      features['borderDist'] = -minDistance
    else:
      features['borderDist'] = 0

    return features


  def getWeights(self, gameState, action):
    return {'numInvaders': -1000, 'onDefense': 100, 'invaderDistance': -60, 'stop': -100, 'reverse': -2, 'borderDist': 50, 'minGhostDist': 50}

class myDefensiveAgent(InvadeAgent):

  def chooseAction(self, gameState):
    self.currentIsinEnemyRegion = self.amIinEnemyRegion(gameState)
    if self.mode == "initial position":
      if self.pastIsinEnemyRegion == True and self.currentIsinEnemyRegion == False:
        self.Agent = AlphaBetaAgent(self.index)
        self.Agent.registerInitialState(gameState)
      action = self.Agent.getAction(gameState)
      self.pastIsinEnemyRegion = self.currentIsinEnemyRegion

      if not self.currentIsinEnemyRegion:
        self.mode = "AlphaBeta Agent"
      return action


    if self.getFood(gameState).count() == 0:
      self.Agent = goHomeAgent(self.index)
      self.Agent.registerInitialState(gameState)
      action = self.getAction(gameState)
      return action

    if self.mode == "AlphaBeta Agent":
      if self.pastIsinEnemyRegion == False and self.currentIsinEnemyRegion == True:
        self.Agent = AlphaBetaAgent(self.index)
        self.Agent.registerInitialState(gameState)
      action = self.Agent.getAction(gameState)
      if self.pastIsinEnemyRegion == True and self.currentIsinEnemyRegion == False:
        team = self.getTeam(gameState)
        team.remove(self.index)
        gameState.getAgentState()
        self.mode = "defensive Agent"
      else:
        self.pastIsinEnemyRegion = self.currentIsinEnemyRegion
      return action

    if self.mode == "defensive Agent":
      if self.pastIsinEnemyRegion == True and self.currentIsinEnemyRegion == False:
        self.Agent = DefensiveReflexAgent(self.index)
        self.Agent.registerInitialState(gameState)
        action = self.Agent.getAction(gameState)
        return action



class goHomeAgent(InvadeAgent):
  def minimaxTree_node(self, gameState, k, maxDepth, parrentNode, alpha, beta):
    n = gameState.getNumAgents()
    depth = k // n + 1

    if not depth == 1 and gameState.getAgentPosition(self.index)==gameState.getInitialAgentPosition(self.index) \
            or gameState.isOver() \
            or depth > maxDepth and k % n == self.index:
      return self.evaluate_invade(gameState, k)

    agentIndex = k % n
    actionList = gameState.getLegalActions(agentIndex)

    if agentIndex == self.index:  # pacman
      maxscore = -math.inf
      for action in actionList:
        nextState = gameState.generateSuccessor(agentIndex, action)
        # print("pacman action: ", action, "pacman position: ", gameState.getPacmanPosition())

        thisActionTreeNode = [[action], [], ['pacman']]
        score = self.minimaxTree_node(nextState, k + 1, maxDepth, thisActionTreeNode, alpha, beta)
        maxscore = max(score, maxscore)
        thisActionTreeNode[0].append(score)  # [[action, score], []]
        parrentNode[1].append(thisActionTreeNode)
      return maxscore
    elif self.isThisGuyAGhost(gameState, agentIndex):  # ghost
      pacman_Position = gameState.getAgentPosition(self.index)
      ghostPositions = []
      ghostActions = []
      for action in actionList:
        nextState = gameState.generateSuccessor(agentIndex, action)
        ghostPositions.append(nextState.getAgentPosition(agentIndex))  # [Position, Action]
        ghostActions.append(action)
        # if ghostPositions == gameState.getInitialAgentPosition(agentIndex):
        #

      distList = [manhattanDistance(pacman_Position, ghost) for ghost in ghostPositions]

      ## Pacman die

      minDistance = min(distList)
      greedyIndex = distList.index(minDistance)
      greedyAction = ghostActions[greedyIndex]
      nextState = gameState.generateSuccessor(agentIndex, ghostActions[greedyIndex])
      thisActionTreeNode = [[greedyAction], [], ['ghost']]
      score = self.minimaxTree_node(nextState, k + 1, maxDepth, thisActionTreeNode, alpha, beta)

      thisActionTreeNode[0].append(score)  # [[action, score], []]
      parrentNode[1].append(thisActionTreeNode)
      return score
    else:
      return self.minimaxTree_node(gameState, k + 1, maxDepth, parrentNode, alpha, beta)

  def findPacmanPath(self, gameState, treeNode, maxDepth, k, actions):
    n = gameState.getNumAgents()
    goDeep = k // n
    if goDeep > maxDepth:
      return
    if not treeNode[1]: return
    if treeNode[2][0]=='pacman':
      maxScore = - math.inf
      for i in range(len(treeNode[1])):
        if treeNode[1][i][0][1] > maxScore:
          maxScore = treeNode[1][i][0][
            1]  # [1]: child node list, [i]: ith child node, [0]: child node action and score, [1]: child node score
          action = treeNode[1][i][0][0]
          index = i
      actions.append(action)
    elif treeNode[2][0]=='ghost':

      index = 0
      #
      # minScore = math.inf
      # for i in range(len(treeNode[1])):
      #   if treeNode[1][i][0][1] < minScore:
      #     minScore = treeNode[1][i][0][1]
      #     index = i
    self.findPacmanPath(gameState, treeNode[1][index], maxDepth, k + 1, actions)

  def getAction(self, gameState):
    """
    Returns the minimax action using self.depth and self.evaluationFunction
    """
    "*** YOUR CODE HERE ***"
    myPos = gameState.getAgentPosition(self.index)
    ghostList = self.getOpponents(gameState)
    for ghost in ghostList:
      if self.isThisGuyAGhost(gameState, ghost) == False:
        ghostList.remove(ghost)
    minGhostDistance = min([self.getMazeDistance(myPos, gameState.getAgentPosition(ghost)) for ghost in ghostList])
    if minGhostDistance > 5:
      maxDepth = 1
    else:
      maxDepth = 1

    tree = [["first"], [], ['pacman']]
    finalscore = self.minimaxTree_node(gameState, self.index, maxDepth, tree, -math.inf, math.inf)

    actions = []
    self.findPacmanPath(gameState, tree, maxDepth, 0, actions)

    return actions[0]

  def getWeights(self, gameState):
    return {'distanceToHome': 100, 'rDistanceToGhost': 50, 'getEaten': 10000, 'IamHome!!': 10000, 'goHomeTime': 100 }
    gameState.data.layout.height

  def getFeatures(self, gameState, k):

    features = util.Counter()
    borderList = []
    wallMatrix = gameState.getWalls()
    height = gameState.data.layout.height
    width = gameState.data.layout.width

    if not self.amIinEnemyRegion(gameState):
      features['IamHome!!'] = 1
    else:
      features['IamHome!!'] = 0

    features['goHomeTime'] = -k

    if self.red: width -= 1
    for i in range(height):
      if not wallMatrix[width // 2][i] == True:
        borderList.append((width // 2, i))
    myPos = gameState.getAgentState(self.index).getPosition()
    minDistance = min([self.getMazeDistance(myPos, border) for border in borderList])
    features['distanceToHome'] = -minDistance

    enemyIndex = self.getOpponents(gameState)
    newGhostStates = []
    for index in enemyIndex:
      ghost = gameState.getAgentState(index)
      if self.isThisGuyAGhost(gameState, index):
        if ghost.scaredTimer < 5:
          newGhostStates.append(gameState.getAgentState(index))

    if len(newGhostStates) > 0:
      minGhostDistance = min([self.getMazeDistance(myPos, ghost.getPosition()) for ghost in newGhostStates])
    else:
      minGhostDistance = 1

    if gameState.getAgentPosition(self.index)==gameState.getInitialAgentPosition(self.index):
      features['getEaten'] = -1
    else:
      features['getEaten'] = 0
    features['rDistanceToGhost'] = - 1 / minGhostDistance

    # if len(gameState.getLegalActions(self.index)) == 2:
    #   features['inPit'] = 1
      # features['successorScore'] = self.getScore(successor)

    return features

  def evaluate_invade(self, gameState, k):
    """
    Computes a linear combination of features and feature weights
    """

    ############################
    #cache the score           #
    ############################
    features = self.getFeatures(gameState, k)
    weights = self.getWeights(gameState)

    # previousObservation = self.getPreviousObservation()
    # if previousObservation:
    #   if previousObservation.getAgentPosition(self.index) == gameState.getAgentPosition(self.index):
    #     print("I am Agnet:", self.index, "I am at: ", gameState.getAgentPosition(self.index), " score:", features * weights)
    #     print(features)
    #     print('action', action)
    # if gameState.isRed(gameState.getAgentPosition(self.index)) and not gameState.isOnRedTeam(self.index):
    #   print("I am Agnet:", self.index, "I am at: ", gameState.getAgentPosition(self.index), " score:", features * weights)
    #   print(features)
    return features * weights


class ChooseInvadePositionAgent(InvadeAgent):
  def getAction(self, gameState):
    """
    Picks among the actions with the highest Q(s,a).
    """
    actions = gameState.getLegalActions(self.index)
    # You can profile your evaluation time by uncommenting these lines
    # start = time.time()
    values = [self.evaluate(gameState, a) for a in actions]
    # print 'eval time for agent %d: %.4f' % (self.index, time.time() - start)

    maxValue = max(values)
    bestActions = [a for a, v in zip(actions, values) if v == maxValue]

    foodLeft = len(self.getFood(gameState).asList())

    if foodLeft <= 2:
      bestDist = 9999
      for action in actions:
        successor = self.getSuccessor(gameState, action)
        pos2 = successor.getAgentPosition(self.index)
        dist = self.getMazeDistance(self.start,pos2)
        if dist < bestDist:
          bestAction = action
          bestDist = dist
      return bestAction

    return random.choice(bestActions)



  def getFeatures(self, gameState, action):
    features = util.Counter()
    successor = self.getSuccessor(gameState, action)
    foodList = self.getFood(successor).asList()
    features['successorScore'] = -len(foodList)#self.getScore(successor)

    # Compute distance to the nearest food

    if len(foodList) > 0: # This should always be True,  but better safe than sorry
      myPos = successor.getAgentState(self.index).getPosition()
      minDistance = min([self.getMazeDistance(myPos, food) for food in foodList])
      features['distanceToFood'] = minDistance
    return features

  def getWeights(self, gameState, action):
    return {'successorScore': 100, 'distanceToFood': -1}


class AlphaBetaAgent(DummyAgent):
  """
  Your minimax agent with alpha-beta pruning (question 3)
  """
  def minimaxTree_node(self, gameState, k, maxDepth, parrentNode, alpha, beta):
    # print(parrentNode, k)
    n = gameState.getNumAgents()
    depth = k // n + 1

    if not depth == 1 and gameState.getAgentPosition(self.index)==gameState.getInitialAgentPosition(self.index) \
            or gameState.isOver() \
            or depth > maxDepth and k % n == self.index:
      return self.evaluate_invade(gameState)

    agentIndex = k % n
    actionList = gameState.getLegalActions(agentIndex)

    if agentIndex == self.index:  # pacman
      maxscore = -math.inf
      for action in actionList:
        nextState = gameState.generateSuccessor(agentIndex, action)
        # print("pacman action: ", action, "pacman position: ", gameState.getPacmanPosition())
        thisActionTreeNode = [[action], [], ['pacman']]
        score = self.minimaxTree_node(nextState, k + 1, maxDepth, thisActionTreeNode, alpha, beta)
        maxscore = max(score, maxscore)
        thisActionTreeNode[0].append(score)  # [[action, score], []]
        parrentNode[1].append(thisActionTreeNode)
        print(parrentNode, k)
      return maxscore
    elif self.isThisGuyAGhost(gameState, agentIndex):  # ghost
      pacman_Position = gameState.getAgentPosition(self.index)
      ghostPositions = []
      ghostActions = []
      for action in actionList:
        nextState = gameState.generateSuccessor(agentIndex, action)
        ghostPositions.append(nextState.getAgentPosition(agentIndex))  # [Position, Action]
        ghostActions.append(action)
        # if ghostPositions == gameState.getInitialAgentPosition(agentIndex):
        #

      distList = [manhattanDistance(pacman_Position, ghost) for ghost in ghostPositions]

      ## Pacman die

      minDistance = min(distList)
      greedyIndex = distList.index(minDistance)
      greedyAction = ghostActions[greedyIndex]
      nextState = gameState.generateSuccessor(agentIndex, ghostActions[greedyIndex])
      thisActionTreeNode = [[greedyAction], [], ['ghost']]
      score = self.minimaxTree_node(nextState, k + 1, maxDepth, thisActionTreeNode, alpha, beta)

      thisActionTreeNode[0].append(score)  # [[action, score], []]
      parrentNode[1].append(thisActionTreeNode)
      print(parrentNode, k)
      return score
    else:
      print(parrentNode, k)
      return self.minimaxTree_node(gameState, k + 1, maxDepth, parrentNode, alpha, beta)

  def findPacmanPath(self, gameState, treeNode, maxDepth, k, actions):
    n = gameState.getNumAgents()
    goDeep = k // n
    if goDeep > maxDepth:
      return
    if not treeNode[1]: return
    if treeNode[2][0]=='pacman':
      maxScore = - math.inf
      for i in range(len(treeNode[1])):
        if treeNode[1][i][0][1] > maxScore:
          maxScore = treeNode[1][i][0][
            1]  # [1]: child node list, [i]: ith child node, [0]: child node action and score, [1]: child node score
          action = treeNode[1][i][0][0]
          index = i
      actions.append(action)
    elif treeNode[2][0]=='ghost':

      index = 0
      #
      # minScore = math.inf
      # for i in range(len(treeNode[1])):
      #   if treeNode[1][i][0][1] < minScore:
      #     minScore = treeNode[1][i][0][1]
      #     index = i
    self.findPacmanPath(gameState, treeNode[1][index], maxDepth, k + 1, actions)

  def getAction(self, gameState):
    """
    Returns the minimax action using self.depth and self.evaluationFunction
    """
    "*** YOUR CODE HERE ***"
    myPos = gameState.getAgentPosition(self.index)
    ghostList = self.getOpponents(gameState)
    for ghost in ghostList:
      if self.isThisGuyAGhost(gameState, ghost) == False:
        ghostList.remove(ghost)

    ghostDistList = [self.getMazeDistance(myPos, gameState.getAgentPosition(ghost)) for ghost in ghostList]
    minGhostDistance = min(ghostDistList)
    minDistGhostIndex = ghostDistList.index(minGhostDistance)
    minDistGhost = ghostList[minDistGhostIndex]
    if minGhostDistance > 5:
      maxDepth = 1
    else:
      if gameState.getAgentState(minDistGhost).scaredTimer > 5:
        maxDepth = 1
      else:
        maxDepth = MAXDEPTH


    tree = [["first"], [], ['pacman']]
    finalscore = self.minimaxTree_node(gameState, self.index, maxDepth, tree, -math.inf, math.inf)

    actions = []
    self.findPacmanPath(gameState, tree, maxDepth, 0, actions)

    return actions[0]

  def getWeights(self, gameState):
    return {'successorScore': 500, 'distanceToFood': 10, 'rDistanceToGhost': 50, 'getEaten': 10000, 'goToEatCapsule': 5000 }

  def getFeatures(self, gameState):
    features = util.Counter()
    foodList = self.getFood(gameState).asList()
    features['successorScore'] = -len(foodList)  # self.getScore(successor)
    if len(foodList) > 0:  # This should always be True,  but better safe than sorry
      myPos = gameState.getAgentState(self.index).getPosition()
      minDistance = min([self.getMazeDistance(myPos, food) for food in foodList])
      features['distanceToFood'] = -minDistance
    else:
      return features

    # features["eatGhost"] = -100
    # features["getYou"] = 0
    enemyIndex = self.getOpponents(gameState)
    newGhostStates = []
    for index in enemyIndex:
      ghost = gameState.getAgentState(index)
      if self.isThisGuyAGhost(gameState, index):

        if ghost.scaredTimer < 5:
          newGhostStates.append(gameState.getAgentState(index))

    if len(newGhostStates) > 0:
      minGhostDistance = min([self.getMazeDistance(myPos, ghost.getPosition()) for ghost in newGhostStates])
    else:
      minGhostDistance = 1

    if gameState.getAgentPosition(self.index)==gameState.getInitialAgentPosition(self.index):
      features['getEaten'] = -1
    else:
      features['getEaten'] = 0

    features['rDistanceToGhost'] = - 1 / minGhostDistance

    capsulesList = self.getCapsules(gameState)

    features['goToEatCapsule'] = - len(capsulesList)

    return features

  def evaluate_invade(self, gameState):
    """
    Computes a linear combination of features and feature weights
    """

    ############################
    #cache the score           #
    ############################
    features = self.getFeatures(gameState)
    weights = self.getWeights(gameState)
    return features * weights


class DefensiveReflexAgent(DummyAgent):
  """
  A reflex agent that keeps its side Pacman-free. Again,
  this is to give you an idea of what a defensive agent
  could be like.  It is not the best or only way to make
  such an agent.
  """

  def getFeatures(self, gameState, action):
    features = util.Counter()
    successor = self.getSuccessor(gameState, action)

    myState = successor.getAgentState(self.index)
    myPos = myState.getPosition()

    # Computes whether we're on defense (1) or offense (0)
    features['onDefense'] = 1
    if myState.isPacman: features['onDefense'] = 0

    # Computes distance to invaders we can see
    enemies = [successor.getAgentState(i) for i in self.getOpponents(successor)]
    invaders = [a for a in enemies if a.isPacman and a.getPosition() != None]
    features['numInvaders'] = len(invaders)
    if len(invaders) > 0:
      dists = [self.getMazeDistance(myPos, a.getPosition()) for a in invaders]
      features['invaderDistance'] = min(dists)

    if action == Directions.STOP: features['stop'] = 1
    rev = Directions.REVERSE[gameState.getAgentState(self.index).configuration.direction]
    if action == rev: features['reverse'] = 1


    # 경계선에서 방어
    width = gameState.getWalls().width
    height = gameState.getWalls().height
    wallMatrix = gameState.getWalls()
    borderList = []
    for i in range(height):
      if not wallMatrix[width // 2][i] == True:
        borderList.append((width // 2, i))
    myPos = successor.getAgentState(self.index).getPosition()
    if abs(myPos[0]-width//2) > 2:
      minDistance = min([self.getMazeDistance(myPos, border) for border in borderList])
      features['borderDist'] = -minDistance
    else:
      features['borderDist'] = 0
    # features["borderDist"] = -abs(successor.getAgentPosition(self.index)[0] - width//2)


    return features



  def getWeights(self, gameState, action):
    return {'numInvaders': -1000, 'onDefense': 100, 'invaderDistance': -10, 'stop': -100, 'reverse': -2, 'borderDist': 3}


def manhattanDistance(xy1, xy2):
  "The Manhattan distance heuristic for a PositionSearchProblem"
  return abs(xy1[0] - xy2[0]) + abs(xy1[1] - xy2[1])
