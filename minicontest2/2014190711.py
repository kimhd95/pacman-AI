from captureAgents import CaptureAgent
import random, time, util
from game import Directions
import game
from util import nearestPoint
from game import Agent
import math

DEPTH_LIMIT = 3

#################
# Team creation #
#################

def createTeam(firstIndex, secondIndex, isRed,
               first = 'OffenderAgent', second = 'DefenderAgent'):

  return [eval(first)(firstIndex), eval(second)(secondIndex)]

##########
# Agents #
##########

class DummyAgent(CaptureAgent):
    def registerInitialState(self, gameState):
      self.start = gameState.getAgentPosition(self.index)
      CaptureAgent.registerInitialState(self, gameState)

    def chooseAction(self, gameState):
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

    def getSuccessor(self, gameState, action):
      successor = gameState.generateSuccessor(self.index, action)
      pos = successor.getAgentState(self.index).getPosition()
      if pos != nearestPoint(pos):
        # Only half a grid position was covered
        return successor.generateSuccessor(self.index, action)
      else:
        return successor

    def evaluate(self, gameState, action):
      features = self.getFeatures(gameState, action)
      weights = self.getWeights(gameState, action)
      return features * weights

    def getFeatures(self, gameState, action):
      features = util.Counter()
      successor = self.getSuccessor(gameState, action)
      features['successorScore'] = self.getScore(successor)
      return features

    def getWeights(self, gameState, action):
      return {'successorScore': 1.0}

    # def getScaredAgents(self, gameState):

    def isOutside(self, gameState):
        pos = gameState.getAgentPosition(self.index)
        return gameState.isRed(pos) ^ gameState.isOnRedTeam(self.index)

    def checkDangerOfAgent(self, gameState, agent):     # agent가 (1) 적, (2) 본 진영, (3) scared 상태가 아님 이면 TRUE
      opponents = self.getOpponents(gameState)
      pos = gameState.getAgentPosition(agent)

      return agent in opponents and not gameState.isRed(pos) ^ gameState.isOnRedTeam(agent) and gameState.getAgentState(agent).scaredTimer < 5


class OffenderAgent(DummyAgent):
    def __init__(self, index, timeForComputing = .1):
        self.index = index
        self.red = None
        self.agentsOnTeam = None
        self.distancer = None
        self.observationHistory = []
        self.timeForComputing = timeForComputing
        self.display = None

        self.mode = "MovingAgent"   # Offender Agent는 4가지 모드를 가짐
                                    # 1. 수비 모드 : food를 다 먹었거나 시간 상 먹으러 갈 수 없을 때     ==> 아군 진영
                                    # 2. 이동 모드 : 상대 진영을 향해 이동                             ==> 아군 진영
                                    # 3. 공격 모드 : 상대를 피해 food를 찾음                           ==> 상대 진영
                                    # 4. 귀환 모드 : 상대를 피해 진영으로 귀환 (food를 먹었고 위험하다는 판단이 들 때) ==> 상대 진영


    def chooseAction(self, gameState):
        # print(self.mode, gameState.data.timeleft)
        myPos = gameState.getAgentPosition(self.index)
        foodList = self.getFood(gameState).asList()
        minFoodDistance = min([self.getMazeDistance(myPos, foodPos) for foodPos in foodList]) if foodList else 1000
        enemies = [gameState.getAgentState(i) for i in self.getOpponents(gameState)]
        invaders = [a for a in enemies if a.isPacman and a.getPosition() != None]

        isOutside = self.isOutside(gameState)

        if not isOutside:   # 아군 진영에 있을 때
                            # invader 있을 때 Defender 전환
            minInvaderDistance = min([self.getMazeDistance(myPos, invader.getPosition()) for invader in invaders]) if invaders else 10
            goToDefend = len(foodList) == 0 or gameState.data.timeleft < 4*minFoodDistance + 10
            goToDefend = goToDefend or (len(invaders) > 0 and minInvaderDistance < 8)
            if goToDefend:
            # if True:
                self.mode = "DefendingAgent"
                self.Agent = DefendingAgent(self.index)
                self.Agent.registerInitialState(gameState)
                # print("Defending")
            else:
                self.mode = "MovingAgent"
                self.Agent = MovingAgent(self.index)
                self.Agent.registerInitialState(gameState)

            action = self.Agent.getAction(gameState)
            return action

        else:       # 상대 진영에 있을 때
            if self.mode == "MovingAgent":
                self.mode = "OffendingAgent"
                self.Agent = OffendingAgent(self.index)
                self.Agent.registerInitialState(gameState)
                action = self.Agent.getAction(gameState)
                return action
            elif self.mode == "OffendingAgent":
                opponents = self.getOpponents(gameState)
                dangerousOpponents = [o for o in opponents if self.checkDangerOfAgent(gameState, o)]    # "위험한" 적
                minEnemyDistance = min([self.getMazeDistance(myPos, gameState.getAgentPosition(do)) for do in dangerousOpponents]) if dangerousOpponents else 10

                goToReturn = gameState.data.timeleft < 4*minFoodDistance + 10 or \
                             len(foodList) == 0 or \
                             (gameState.getAgentState(self.index).numCarrying > 0 and \
                             minEnemyDistance < 4)

                if goToReturn:
                    self.mode = "ReturningAgent"
                    self.Agent = ReturningAgent(self.index)
                    self.Agent.registerInitialState(gameState)
                else:
                    self.Agent = OffendingAgent(self.index)
                    self.Agent.registerInitialState(gameState)
                action = self.Agent.getAction(gameState)
                return action
            elif self.mode == "ReturningAgent":
                self.Agent = ReturningAgent(self.index)
                self.Agent.registerInitialState(gameState)
                action = self.Agent.getAction(gameState)
                return action

class DefendingAgent(OffenderAgent):
    def getAction(self, gameState):
        actions = gameState.getLegalActions(self.index)
        values = [self.evaluate(gameState, a) for a in actions]
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

        return features

    def getWeights(self, gameState, action):
        return {'numInvaders': -1000, 'onDefense': 100, 'invaderDistance': -10, 'stop': -100, 'reverse': -2}

class MovingAgent(OffenderAgent):
  def getAction(self, gameState):
    actions = gameState.getLegalActions(self.index)
    values = [self.evaluate(gameState, a) for a in actions]
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
    if len(foodList) > 0: # This should always be True,  but better safe than sorry
      myPos = successor.getAgentState(self.index).getPosition()
      minDistance = min([self.getMazeDistance(myPos, food) for food in foodList])
      features['distanceToFood'] = minDistance
    opponents = self.getOpponents(gameState)
    dangerousOpponents = [o for o in opponents if self.checkDangerOfAgent(successor, o)]    # "위험한" 적
    minEnemyDistance = min([self.getMazeDistance(myPos, successor.getAgentPosition(do)) for do in dangerousOpponents]) if dangerousOpponents else 10
    features['distanceToEnemy'] = minEnemyDistance if minEnemyDistance > 1 else -100
    features['stop'] = -10 if action == Directions.STOP else 0  # 멈춤 방지
    return features

  def getWeights(self, gameState, action):
    return {'successorScore': 100, 'distanceToFood': -1, 'distanceToEnemy': 0.1, 'stop': 1}

class OffendingAgent(OffenderAgent):
    def buildMinimax(self, gameState, curLevel, limit, prevNode):
      numOfAgents = gameState.getNumAgents()
      agentIndex = curLevel % numOfAgents
      agentPos = gameState.getAgentPosition(self.index)
      depth = curLevel // numOfAgents + 1
      legalActions = gameState.getLegalActions(agentIndex)

      if agentIndex == self.index and gameState.isOver() or depth > limit or agentPos==gameState.getInitialAgentPosition(self.index):
          if curLevel >= numOfAgents:
              return self.getFeatures(gameState) * self.getWeights(gameState)


      if agentIndex == self.index:  # myAgent
        maxV = -math.inf

        for action in legalActions:
          # curNode = {'action': action, 'agentType': 'pacman', 'prev': []}
          curNode = [0, action, 'pacman', []]       # [value, action, agent, prevNode]
          successor = gameState.generateSuccessor(agentIndex, action)

          v = self.buildMinimax(successor, curLevel + 1, limit, curNode)
          maxV = max(v, maxV)
          curNode[0] = v  # v 갱신
          # curNode['value'] = v
          # curNode['prev'].append(curNode)
          prevNode[3].append(curNode)   # 트리 branch에 현재노드 추가
        return maxV

      elif self.checkDangerOfAgent(gameState, agentIndex):  # 위험한 적군인 경우
        myPos = gameState.getAgentPosition(self.index)
        nextStates = []     # {[[pos, action]...]}

        for action in legalActions:
          successor = gameState.generateSuccessor(agentIndex, action)
          nextStates.append([successor.getAgentPosition(agentIndex), action])

        distances = [self.getMazeDistance(myPos, s[0]) for s in nextStates]
        minDistanceToEnemy = min(distances)
        newAction = nextStates[distances.index(minDistanceToEnemy)][1]
        successor = gameState.generateSuccessor(agentIndex, newAction)
        curNode = [0, newAction, 'ghost', []]
        # curNode = {'action': newAction, 'agentType': 'ghost', 'prev': []}
        v = self.buildMinimax(successor, curLevel + 1, limit, curNode)

        curNode[0] = v  # [[action, score], []]
        prevNode[3].append(curNode)
        # curNode['value'] = v
        # curNode['prev'].append(curNode)
        return v

      else:
        return self.buildMinimax(gameState, curLevel + 1, limit, prevNode)

    def getBestAction(self, gameState, rootNode, curLevel, limit):
      depth = curLevel // gameState.getNumAgents()
      if not rootNode[3] or depth > limit:
      # if not rootNode['prev'] or depth > limit:
        return
      if rootNode[2] == 'pacman':
      # if rootNode['agentType'] == 'pacman':
        maxScore = -math.inf
        for i in range(len(rootNode[3])):
        # for i in range(len(rootNode['prev'])):
          # if rootNode[3][i][0] > maxScore:
          prev_i = rootNode[3][i]
          if prev_i[0] > maxScore:
            maxScore = prev_i[0]
            action = prev_i[1]
            childIndex = i
        return action
      elif rootNode['agentType'] == 'ghost':
        childIndex = 0

      self.getBestAction(gameState, rootNode[3][childIndex], curLevel+1, limit)



    def getAction(self, gameState):
      """
      Returns the minimax action using self.depth and self.evaluationFunction
      """
      "*** YOUR CODE HERE ***"
      myPos = gameState.getAgentPosition(self.index)
      limit = DEPTH_LIMIT
      s0 = [None, 'first', 'pacman', []]
      # tree = {'action': 'first', 'agentType': 'pacman', 'prev': []}
      self.buildMinimax(gameState, self.index, limit, s0)
      bestAction = self.getBestAction(gameState, s0, limit, 0)
      # print(bestAction)
      return bestAction

    def getFeatures(self, gameState):
      features = util.Counter()
      foodList = self.getFood(gameState).asList()
      # 캡슐도 food로 취급
      capsulesList = self.getCapsules(gameState)
      for c in capsulesList:
          foodList.append(c)

      features['successorScore'] = -len(foodList)
      if len(foodList) == 0:
          return features

      myPos = gameState.getAgentState(self.index).getPosition()
      minDistance = min([self.getMazeDistance(myPos, food) for food in foodList])
      features['distanceToFood'] = -minDistance

      opponents = self.getOpponents(gameState)
      dangerousOpponents = [o for o in opponents if self.checkDangerOfAgent(gameState, o)]    # "위험한" 적
      minEnemyDistance = min([self.getMazeDistance(myPos, gameState.getAgentPosition(do)) for do in dangerousOpponents]) if dangerousOpponents else 10
      dangerousOpponentsStates = [gameState.getAgentState(do) for do in dangerousOpponents]

      if gameState.getAgentPosition(self.index)==gameState.getInitialAgentPosition(self.index):
          features['distanceToEnemy'] = -1000
      elif minEnemyDistance > 1:
          features['distanceToEnemy'] = -50
      else:
          features['distanceToEnemy'] = -1 / minEnemyDistance

      return features

    def getWeights(self, gameState):
      return {'successorScore': 100, 'distanceToFood': 1, 'distanceToEnemy': 5}


class ReturningAgent(OffendingAgent):
    def getOurBorderPos(self, gameState):
        wallMatrix = gameState.getWalls()
        height = gameState.data.layout.height
        width = gameState.data.layout.width

        border_red = []
        border_blue = []
        border_red_x = width // 2 - 1
        border_blue_x = border_red_x + 1

        for h in range(height):
            if not wallMatrix[border_red_x][h]:
                border_red.append((border_red_x, h))
            if not wallMatrix[border_blue_x][h]:
                border_blue.append((border_blue_x, h))

        return border_red if gameState.isOnRedTeam(self.index) else border_blue

    def getFeatures(self, gameState):
      features = util.Counter()
      borderList = self.getOurBorderPos(gameState)

      myPos = gameState.getAgentState(self.index).getPosition()
      minBorderDistance = min([self.getMazeDistance(myPos, bPos) for bPos in borderList])
      features['distanceToBorder'] = -minBorderDistance if minBorderDistance > 0 else 1000

      # print(minBorderDistance)
      opponents = self.getOpponents(gameState)
      dangerousOpponents = [o for o in opponents if self.checkDangerOfAgent(gameState, o)]    # "위험한" 적
      minEnemyDistance = min([self.getMazeDistance(myPos, gameState.getAgentPosition(do)) for do in dangerousOpponents]) if dangerousOpponents else 10
      dangerousOpponentsStates = [gameState.getAgentState(do) for do in dangerousOpponents]

      if gameState.getAgentPosition(self.index)==gameState.getInitialAgentPosition(self.index):
          features['distanceToEnemy'] = -1000
      elif minEnemyDistance > 1:
          features['distanceToEnemy'] = -50
      else:
          features['distanceToEnemy'] = -1 / minEnemyDistance

      return features

    def getWeights(self, gameState):
      return {'distanceToBorder': 2, 'distanceToEnemy': 1}







class DefenderAgent(DummyAgent):
    def __init__(self, index, timeForComputing = .1):
        self.index = index
        self.red = None
        self.agentsOnTeam = None
        self.distancer = None
        self.observationHistory = []
        self.timeForComputing = timeForComputing
        self.display = None

        self.mode = "PatrolAgent"   # Defender Agent는 2가지 모드를 가짐
                                    # 1. 순찰 모드 : 침투한 상대가 없을 때 border 부근에서 상대의 침투에 대비
                                    # 2. 추격 모드 : 상대가 침투했을 때 해당 에이전트를 추격

    def getOurBorderPos(self, gameState):
        wallMatrix = gameState.getWalls()
        height = gameState.data.layout.height
        width = gameState.data.layout.width

        border_red = []
        border_blue = []
        border_red_x = width // 2 - 1
        border_blue_x = border_red_x + 1

        for h in range(height):
            if not wallMatrix[border_red_x][h]:
                border_red.append((border_red_x, h))
            if not wallMatrix[border_blue_x][h]:
                border_blue.append((border_blue_x, h))

        return border_red if gameState.isOnRedTeam(self.index) else border_blue

    def chooseAction(self, gameState):
        # print(self.timeForComputing)
        myPos = gameState.getAgentPosition(self.index)
        enemies = [gameState.getAgentState(i) for i in self.getOpponents(gameState)]
        invaders = [a for a in enemies if a.isPacman and a.getPosition() != None]
        minInvaderDistance = min([self.getMazeDistance(myPos, invader.getPosition()) for invader in invaders]) if invaders else 30
        minOpponentDistance = min([self.getMazeDistance(myPos, e.getPosition()) for e in enemies]) if enemies else 30
        foodList = self.getFood(gameState).asList()
        minFoodDistance = min([self.getMazeDistance(myPos, foodPos) for foodPos in foodList]) if foodList else 1000

        team = self.getTeam(gameState)
        team.remove(self.index)
        teammate = gameState.getAgentState(team[0])
        minInvaderDistance_team = min([self.getMazeDistance(teammate.getPosition(), invader.getPosition()) for invader in invaders]) if invaders else 99

        isOutside = self.isOutside(gameState)
        # print(self.mode, gameState.data.timeleft)
        if not isOutside:
            if len(invaders) == 0:      # 순찰 모드
                if not teammate.isPacman or minOpponentDistance > 8:
                    self.mode = "MovingAgent"
                    self.Agent = MovingAgent(self.index)
                    self.Agent.registerInitialState(gameState)
                else:
                    self.mode = "PatrolAgent"
                    self.Agent = PatrolAgent(self.index)
                    self.Agent.registerInitialState(gameState)

            else:

                if len(invaders) == 1 and not teammate.isPacman and minInvaderDistance > 10 and minInvaderDistance_team < 8:
                    self.mode = "MovingAgent"
                    self.Agent = MovingAgent(self.index)
                    self.Agent.registerInitialState(gameState)
                else:
                    self.mode = "ChasingAgent"
                    self.Agent = ChasingAgent(self.index)
                    self.Agent.registerInitialState(gameState)

        else:
            if len(invaders) > 0 and (teammate.isPacman or minInvaderDistance_team >= 8):
                self.mode = "ReturningAgent"
                self.Agent = ReturningAgent(self.index)
                self.Agent.registerInitialState(gameState)
                action = self.Agent.getAction(gameState)
                return action

            if self.mode == "MovingAgent":
                self.mode = "OffendingAgent"
                self.Agent = OffendingAgent(self.index)
                self.Agent.registerInitialState(gameState)
            elif self.mode == "OffendingAgent":
                opponents = self.getOpponents(gameState)
                dangerousOpponents = [o for o in opponents if self.checkDangerOfAgent(gameState, o)]    # "위험한" 적
                minEnemyDistance = min([self.getMazeDistance(myPos, gameState.getAgentPosition(do)) for do in dangerousOpponents]) if dangerousOpponents else 10

                goToReturn = gameState.data.timeleft < 4*minFoodDistance + 10 or \
                             len(foodList) == 0 or \
                             (gameState.getAgentState(self.index).numCarrying > 0 and \
                             minEnemyDistance < 8)
                if goToReturn:
                    self.mode = "ReturningAgent"
                    self.Agent = ReturningAgent(self.index)
                    self.Agent.registerInitialState(gameState)
                else:
                    self.Agent = OffendingAgent(self.index)
                    self.Agent.registerInitialState(gameState)
            elif self.mode == "ReturningAgent":
                self.Agent = ReturningAgent(self.index)
                self.Agent.registerInitialState(gameState)


        action = self.Agent.getAction(gameState)
        return action


class PatrolAgent(DefenderAgent):
    def getAction(self, gameState):
        actions = gameState.getLegalActions(self.index)
        values = [self.evaluate(gameState, a) for a in actions]
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
        myState = successor.getAgentState(self.index)
        myPos = myState.getPosition()

        # Computes whether we're on defense (1) or offense (0)
        features['onDefense'] = 1
        if myState.isPacman: features['onDefense'] = 0


        borderList = self.getOurBorderPos(gameState)
        minBorderDistance = min([self.getMazeDistance(myPos, bPos) for bPos in borderList])
        features['minBorderDistance'] = minBorderDistance

        # Computes distance to invaders we can see
        opponents = self.getOpponents(gameState)
        enemies = [o for o in opponents if self.checkDangerOfAgent(gameState, o)]    # "위험한" 적
        minEnemyDistance = min([self.getMazeDistance(myPos, gameState.getAgentPosition(e)) for e in enemies]) if enemies else 10
        features['minEnemyDistance'] = minEnemyDistance if minEnemyDistance > 0 else 10000

        if action == Directions.STOP: features['stop'] = 1

        return features

    def getWeights(self, gameState, action):
        return {'onDefense': 100, 'minEnemyDistance': -10, 'minBorderDistance': -3, 'stop': -100}


class ChasingAgent(DefenderAgent):
    def getAction(self, gameState):
        actions = gameState.getLegalActions(self.index)
        values = [self.evaluate(gameState, a) for a in actions]
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

        return features

    def getWeights(self, gameState, action):
        return {'numInvaders': -1000, 'onDefense': 100, 'invaderDistance': -10, 'stop': -100, 'reverse': -2}


class MovingAgent(DefenderAgent):
  def getAction(self, gameState):
    actions = gameState.getLegalActions(self.index)
    values = [self.evaluate(gameState, a) for a in actions]
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
    if len(foodList) > 0: # This should always be True,  but better safe than sorry
      myPos = successor.getAgentState(self.index).getPosition()
      minDistance = min([self.getMazeDistance(myPos, food) for food in foodList])
      features['distanceToFood'] = minDistance
    opponents = self.getOpponents(gameState)
    dangerousOpponents = [o for o in opponents if self.checkDangerOfAgent(successor, o)]    # "위험한" 적
    minEnemyDistance = min([self.getMazeDistance(myPos, successor.getAgentPosition(do)) for do in dangerousOpponents]) if dangerousOpponents else 10
    features['distanceToEnemy'] = minEnemyDistance if minEnemyDistance > 1 else -100
    features['stop'] = -10 if action == Directions.STOP else 0  # 멈춤 방지
    return features

  def getWeights(self, gameState, action):
    return {'successorScore': 100, 'distanceToFood': -1, 'distanceToEnemy': 0.1, 'stop': 1}

class OffendingAgent(DefenderAgent):
    def buildMinimax(self, gameState, curLevel, limit, prevNode):
      numOfAgents = gameState.getNumAgents()
      agentIndex = curLevel % numOfAgents
      agentPos = gameState.getAgentPosition(self.index)
      depth = curLevel // numOfAgents + 1
      legalActions = gameState.getLegalActions(agentIndex)

      if agentIndex == self.index and gameState.isOver() or depth > limit or agentPos==gameState.getInitialAgentPosition(self.index):
          if curLevel >= numOfAgents:
              return self.getFeatures(gameState, 0) * self.getWeights(gameState, 0)


      if agentIndex == self.index:  # myAgent
        maxV = -math.inf

        for action in legalActions:
          # curNode = {'action': action, 'agentType': 'pacman', 'prev': []}
          curNode = [0, action, 'pacman', []]       # [value, action, agent, prevNode]
          successor = gameState.generateSuccessor(agentIndex, action)

          v = self.buildMinimax(successor, curLevel + 1, limit, curNode)
          maxV = max(v, maxV)
          curNode[0] = v  # v 갱신
          # curNode['value'] = v
          # curNode['prev'].append(curNode)
          prevNode[3].append(curNode)   # 트리 branch에 현재노드 추가
        return maxV

      elif self.checkDangerOfAgent(gameState, agentIndex):  # 위험한 적군인 경우
        myPos = gameState.getAgentPosition(self.index)
        nextStates = []     # {[[pos, action]...]}

        for action in legalActions:
          successor = gameState.generateSuccessor(agentIndex, action)
          nextStates.append([successor.getAgentPosition(agentIndex), action])

        distances = [self.getMazeDistance(myPos, s[0]) for s in nextStates]
        minDistanceToEnemy = min(distances)
        newAction = nextStates[distances.index(minDistanceToEnemy)][1]
        successor = gameState.generateSuccessor(agentIndex, newAction)
        curNode = [0, newAction, 'ghost', []]
        # curNode = {'action': newAction, 'agentType': 'ghost', 'prev': []}
        v = self.buildMinimax(successor, curLevel + 1, limit, curNode)

        curNode[0] = v  # [[action, score], []]
        prevNode[3].append(curNode)
        # curNode['value'] = v
        # curNode['prev'].append(curNode)
        return v

      else:
        return self.buildMinimax(gameState, curLevel + 1, limit, prevNode)

    def getBestAction(self, gameState, rootNode, curLevel, limit):
      depth = curLevel // gameState.getNumAgents()
      if not rootNode[3] or depth > limit:
      # if not rootNode['prev'] or depth > limit:
        return
      if rootNode[2] == 'pacman':
      # if rootNode['agentType'] == 'pacman':
        maxScore = -math.inf
        for i in range(len(rootNode[3])):
        # for i in range(len(rootNode['prev'])):
          # if rootNode[3][i][0] > maxScore:
          prev_i = rootNode[3][i]
          if prev_i[0] > maxScore:
            maxScore = prev_i[0]
            action = prev_i[1]
            childIndex = i
        return action
      elif rootNode['agentType'] == 'ghost':
        childIndex = 0

      self.getBestAction(gameState, rootNode[3][childIndex], curLevel+1, limit)



    def getAction(self, gameState):
      """
      Returns the minimax action using self.depth and self.evaluationFunction
      """
      "*** YOUR CODE HERE ***"
      myPos = gameState.getAgentPosition(self.index)
      limit = DEPTH_LIMIT
      s0 = [None, 'first', 'pacman', []]
      # tree = {'action': 'first', 'agentType': 'pacman', 'prev': []}
      self.buildMinimax(gameState, self.index, limit, s0)
      bestAction = self.getBestAction(gameState, s0, limit, 0)
      # print(bestAction)
      return bestAction

    def getFeatures(self, gameState, action):
      features = util.Counter()
      foodList = self.getFood(gameState).asList()
      # 캡슐도 food로 취급
      capsulesList = self.getCapsules(gameState)
      for c in capsulesList:
          foodList.append(c)

      features['successorScore'] = -len(foodList)
      if len(foodList) == 0:
          return features

      myPos = gameState.getAgentState(self.index).getPosition()
      minDistance = min([self.getMazeDistance(myPos, food) for food in foodList])
      features['distanceToFood'] = -minDistance

      opponents = self.getOpponents(gameState)
      dangerousOpponents = [o for o in opponents if self.checkDangerOfAgent(gameState, o)]    # "위험한" 적
      minEnemyDistance = min([self.getMazeDistance(myPos, gameState.getAgentPosition(do)) for do in dangerousOpponents]) if dangerousOpponents else 10
      dangerousOpponentsStates = [gameState.getAgentState(do) for do in dangerousOpponents]

      if gameState.getAgentPosition(self.index)==gameState.getInitialAgentPosition(self.index):
          features['distanceToEnemy'] = -1000
      elif minEnemyDistance > 1:
          features['distanceToEnemy'] = -50
      else:
          features['distanceToEnemy'] = -1 / minEnemyDistance

      return features

    def getWeights(self, gameState, action):
      return {'successorScore': 100, 'distanceToFood': 1, 'distanceToEnemy': 5}


class ReturningAgent(OffendingAgent):
    def getOurBorderPos(self, gameState):
        wallMatrix = gameState.getWalls()
        height = gameState.data.layout.height
        width = gameState.data.layout.width

        border_red = []
        border_blue = []
        border_red_x = width // 2 - 1
        border_blue_x = border_red_x + 1

        for h in range(height):
            if not wallMatrix[border_red_x][h]:
                border_red.append((border_red_x, h))
            if not wallMatrix[border_blue_x][h]:
                border_blue.append((border_blue_x, h))

        return border_red if gameState.isOnRedTeam(self.index) else border_blue

    def getFeatures(self, gameState, action):
      features = util.Counter()
      borderList = self.getOurBorderPos(gameState)

      myPos = gameState.getAgentState(self.index).getPosition()
      minBorderDistance = min([self.getMazeDistance(myPos, bPos) for bPos in borderList])
      features['distanceToBorder'] = -minBorderDistance if minBorderDistance > 0 else 1000

      # print(minBorderDistance)
      opponents = self.getOpponents(gameState)
      dangerousOpponents = [o for o in opponents if self.checkDangerOfAgent(gameState, o)]    # "위험한" 적
      minEnemyDistance = min([self.getMazeDistance(myPos, gameState.getAgentPosition(do)) for do in dangerousOpponents]) if dangerousOpponents else 10
      dangerousOpponentsStates = [gameState.getAgentState(do) for do in dangerousOpponents]

      if gameState.getAgentPosition(self.index)==gameState.getInitialAgentPosition(self.index):
          features['distanceToEnemy'] = -1000
      elif minEnemyDistance > 1:
          features['distanceToEnemy'] = -50
      else:
          features['distanceToEnemy'] = -1 / minEnemyDistance

      return features

    def getWeights(self, gameState, action):
      return {'distanceToBorder': 2, 'distanceToEnemy': 1}
