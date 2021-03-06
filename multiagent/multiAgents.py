# multiAgents.py
# --------------
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
#
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).


from util import manhattanDistance
from game import Directions
import random, util

from game import Agent

class ReflexAgent(Agent):
    """
    A reflex agent chooses an action at each choice point by examining
    its alternatives via a state evaluation function.

    The code below is provided as a guide.  You are welcome to change
    it in any way you see fit, so long as you don't touch our method
    headers.
    """


    def getAction(self, gameState):
        """
        You do not need to change this method, but you're welcome to.

        getAction chooses among the best options according to the evaluation function.

        Just like in the previous project, getAction takes a GameState and returns
        some Directions.X for some X in the set {NORTH, SOUTH, WEST, EAST, STOP}
        """
        # Collect legal moves and successor states
        legalMoves = gameState.getLegalActions()

        # Choose one of the best actions
        scores = [self.evaluationFunction(gameState, action) for action in legalMoves]
        bestScore = max(scores)
        bestIndices = [index for index in range(len(scores)) if scores[index] == bestScore]
        chosenIndex = random.choice(bestIndices) # Pick randomly among the best

        "Add more of your code here if you want to"

        return legalMoves[chosenIndex]

    def evaluationFunction(self, currentGameState, action):
        """
        Design a better evaluation function here.

        The evaluation function takes in the current and proposed successor
        GameStates (pacman.py) and returns a number, where higher numbers are better.

        The code below extracts some useful information from the state, like the
        remaining food (newFood) and Pacman position after moving (newPos).
        newScaredTimes holds the number of moves that each ghost will remain
        scared because of Pacman having eaten a power pellet.

        Print out these variables to see what you're getting, then combine them
        to create a masterful evaluation function.
        """
        # Useful information you can extract from a GameState (pacman.py)
        successorGameState = currentGameState.generatePacmanSuccessor(action)
        newPos = successorGameState.getPacmanPosition()
        newFood = successorGameState.getFood()
        newGhostStates = successorGameState.getGhostStates()
        newScaredTimes = [ghostState.scaredTimer for ghostState in newGhostStates]

        "*** YOUR CODE HERE ***"
        curPos = currentGameState.getPacmanPosition()
        #newPos
        curScore = currentGameState.getScore()
        newScore = successorGameState.getScore()
        curGhostStates = currentGameState.getGhostStates()
        #newGhostStates
        curGhostDistances = [manhattanDistance(curPos, gstate.getPosition()) for gstate in curGhostStates]
        newGhostDistances = [manhattanDistance(newPos, gstate.getPosition()) for gstate in newGhostStates]
        curFood = currentGameState.getFood()
        #newFood
        curFoodDistances = [manhattanDistance(curPos, foodPos) for foodPos in curFood.asList()]
        newFoodDistances = [manhattanDistance(newPos, foodPos) for foodPos in newFood.asList()]

        # criteria1 = 3*(newScore - curScore)
        # if min(newGhostDistances) <= 1:
        #     criteria2 = -1000
        # else:
        #     criteria2 = 1/min(curGhostDistances) - 1/min(newGhostDistances) if max(newScaredTimes) == 0 else  0
        # criteria3 = 1/min(newFoodDistances) - 1/min(curFoodDistances) if newFoodDistances else 0

        if min(newGhostDistances) <= 1 and max(newScaredTimes) == 0:    # 유령과 한칸차이이고 scared상태가 아닐때
            return -100
        elif action == Directions.STOP:     # 멈춰있는 경우
            return -1
        elif newScore - curScore >= 0:      # food를 먹는 경우
            return 5
        elif min(curFoodDistances) - min(newFoodDistances) > 0:         # 제일 가까운 food와 근접해질때
            return 3
        else:                               # 그 외: food와의 거리에 따라
            return 1 + 1/min(newFoodDistances) - 1/min(curFoodDistances) if newFoodDistances else 0


def scoreEvaluationFunction(currentGameState):
    """
    This default evaluation function just returns the score of the state.
    The score is the same one displayed in the Pacman GUI.

    This evaluation function is meant for use with adversarial search agents
    (not reflex agents).
    """
    return currentGameState.getScore()

class MultiAgentSearchAgent(Agent):
    """
    This class provides some common elements to all of your
    multi-agent searchers.  Any methods defined here will be available
    to the MinimaxPacmanAgent, AlphaBetaPacmanAgent & ExpectimaxPacmanAgent.

    You *do not* need to make any changes here, but you can if you want to
    add functionality to all your adversarial search agents.  Please do not
    remove anything, however.

    Note: this is an abstract class: one that should not be instantiated.  It's
    only partially specified, and designed to be extended.  Agent (game.py)
    is another abstract class.
    """

    def __init__(self, evalFn = 'scoreEvaluationFunction', depth = '2'):
        self.index = 0 # Pacman is always agent index 0
        self.evaluationFunction = util.lookup(evalFn, globals())
        self.depth = int(depth)

class MinimaxAgent(MultiAgentSearchAgent):
    """
    Your minimax agent (question 2)
    """

    def getAction(self, gameState):
        """
        Returns the minimax action from the current gameState using self.depth
        and self.evaluationFunction.

        Here are some method calls that might be useful when implementing minimax.

        gameState.getLegalActions(agentIndex):
        Returns a list of legal actions for an agent
        agentIndex=0 means Pacman, ghosts are >= 1

        gameState.generateSuccessor(agentIndex, action):
        Returns the successor game state after an agent takes an action

        gameState.getNumAgents():
        Returns the total number of agents in the game

        gameState.isWin():
        Returns whether or not the game state is a winning state

        gameState.isLose():
        Returns whether or not the game state is a losing state
        """
        "*** YOUR CODE HERE ***"
        # Pseudo-code
        # def value(state):
        #     if the state is a terminal state: return the state’s utility
        #     if the next agent is MAX: return max-value(state)
        #     if the next agent is MIN: return min-value(state)
        # def max-value(state):
        #     initialize v = -∞
        #     for each successor of state:
        #     v = max(v, value(successor))
        #     return v
        # def min-value(state):
        #     initialize v = +∞
        #     for each successor of state:
        #     v = min(v, value(successor))
        #     return v

        def maxValue(gameState, depth):
            legalActions = gameState.getLegalActions(0)     # 팩맨 액션
            if gameState.isWin() or not legalActions or depth >= self.depth:    #트리 말단 노드일때 evaluationFunction 수행
                return self.evaluationFunction(gameState)
            return max(minValue(gameState.generateSuccessor(0, action), depth+1, 1) for action in legalActions)

        def minValue(gameState, depth, agentIndex):
            legalActions = gameState.getLegalActions(agentIndex)        # 유령 액션
            if gameState.isLose() or not legalActions:      #트리 말단
                return self.evaluationFunction(gameState)

            numAgents = gameState.getNumAgents()
            if agentIndex < numAgents - 1:  # 다음 agent가 Ghost일때 노드 확장
                return min(minValue(gameState.generateSuccessor(agentIndex, action), depth, agentIndex + 1) for action in legalActions)
            else:   # 다음 agent가 PACMAN일때 노드 확장
                return min(maxValue(gameState.generateSuccessor(agentIndex, action), depth) for action in legalActions)

        return max(gameState.getLegalActions(0), key=lambda a: minValue(gameState.generateSuccessor(0, a), 1, 1))


class AlphaBetaAgent(MultiAgentSearchAgent):
    """
    Your minimax agent with alpha-beta pruning (question 3)
    """
    # Pseudo-code
    # def value(state):
    #     if the state is a terminal state: return the state’s utility
    #     if the next agent is MAX: return max-value(state)
    #     if the next agent is MIN: return min-value(state)

    # def max-value(state):
    #     initialize v = -∞
    #     for each successor of state:
    #       v = max(v, min-value(successor, alpha, beta))
    #       if v > beta: return v
    #       alpha = max(alpha, v)
    #     return v
    # def min-value(state):
    #     initialize v = +∞
    #     for each successor of state:
    #       v = min(v, max-value(successor, alpha, beta))
    #       if v < alpha: return v
    #       beta = min(beta, v)
    #     return v

    def getAction(self, gameState):
        """
        Returns the minimax action using self.depth and self.evaluationFunction
        """
        "*** YOUR CODE HERE ***"
        def maxValue(gameState, alpha, beta, depth):
            # print(" >> " + "a=", alpha," b=", beta, " depth=", depth, " agent=pacman")
            v = -999999
            legalActions = gameState.getLegalActions(0)
            if not legalActions or depth == self.depth:     #말단 노드
                return self.evaluationFunction(gameState)

            for action in legalActions:     # for each successor of state
                newStates =  gameState.generateSuccessor(0, action)
                # successor V 계산, 비교
                newV = minValue(newStates, alpha, beta, depth + 1, 1)
                if newV > v and depth == 0:
                    toAct = action
                v = max(v, newV)
                if v > beta:        # best option인 경우 (Tree cut)
                    return v
                alpha = max(alpha, v)

            if depth == 0:
                return toAct if toAct else legalActions[0]
            return v

        def minValue(gameState, alpha, beta, depth, agentIndex):
            # print(" >> " + "a=", alpha," b=", beta, " depth=", depth, " agent=ghost", agentIndex)
            v = 999999
            legalActions = gameState.getLegalActions(agentIndex)
            if not legalActions:        # 말단 노드
                return self.evaluationFunction(gameState)

            numAgents = gameState.getNumAgents()
            for action in legalActions:
                newStates = gameState.generateSuccessor(agentIndex, action)
                v = min(v, maxValue(newStates, alpha, beta, depth)) if agentIndex == numAgents-1 else min(v, minValue(newStates, alpha, beta, depth, agentIndex+1))
                if v < alpha:       # Stop expanding (Tree cut)
                    return v
                beta = min(beta, v)
            return v

        return maxValue(gameState, -999999, 999999, 0)


class ExpectimaxAgent(MultiAgentSearchAgent):
    """
      Your expectimax agent (question 4)
    """

    def getAction(self, gameState):
        """
        Returns the expectimax action using self.depth and self.evaluationFunction

        All ghosts should be modeled as choosing uniformly at random from their
        legal moves.
        """
        "*** YOUR CODE HERE ***"
        util.raiseNotDefined()

def betterEvaluationFunction(currentGameState):
    """
    Your extreme ghost-hunting, pellet-nabbing, food-gobbling, unstoppable
    evaluation function (question 5).

    DESCRIPTION: <write something here so we know what you did>
    """
    "*** YOUR CODE HERE ***"
    util.raiseNotDefined()

# Abbreviation
better = betterEvaluationFunction
