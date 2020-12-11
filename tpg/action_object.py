from logging import fatal

import numpy as np
import random
from tpg.utils import flip

"""
Action  Object has a program to produce a value for the action, program doesn't
run if just a discrete action code.
"""
class ActionObject:

    '''
    An action object can be initalized by:
        - Copying another action object
        - Passing an index into the action codes in initParams as the action
        - Passing a team as the action
    '''
    def __init__(self, initParams=None, action=None):

        '''
        Defer importing the Team class to avoid circular dependency.
        This may require refactoring to fix properly
        '''
        from tpg.team import Team

        # The action is a team
        '''
        TODO handle team references somehow
        '''
        if isinstance(action, Team):
            self.teamAction = action

        # The action is another action object
        if isinstance(action, ActionObject):
            self.actionCode = action.actionCode
            self.teamAction = action.teamAction

        # An int means the action is an index into the action codes in initParams
        if isinstance(action, int):
            
            if "actionCodes" not in initParams:
                raise Exception('action codes not found in init params', initParams)

            try:
                self.actionCode = initParams["actionCodes"][action]
                self.teamAction = None
            except IndexError as err:
                '''
                TODO log index error
                '''


    # def __init__(self, actionObj=None, actionIndex=None, teamAction=None,
    #         initParams=None):
    #     if actionObj is not None:
    #         # clone the other action object
    #         self.actionCode = actionObj.actionCode
    #         self.teamAction = actionObj.teamAction
    #     else:
    #         # no cloning
    #         '''
    #         TODO What happens when actionIndex is None?
    #         '''
    #         self.actionCode = initParams["actionCodes"][actionIndex]
    #         self.teamAction = teamAction

    #     # increase references to team
    #     if self.teamAction is not None:
    #         self.teamAction.numLearnersReferencing += 1

    '''
    An ActionObject is equal to another object if that object:
        - is an instance of the ActionObject class
        - has the same action code
        - has the same team action
    '''
    def __eq__(self, o:object)->bool:

        # The other object must be an instance of the ActionObject class
        if not isinstance(o, ActionObject):
            return False
        
        # The other object's action code must be equal to ours
        if self.actionCode != o.actionCode:
            return False
        
        # The other object's team action must be equal to ours
        if self.teamAction != o.teamAction:
            return False

        return True

    """
    Returns the action code, and if applicable corresponding real action(s).
    """
    def getAction(self, state, visited, actVars=None):
        if self.teamAction is not None:
            # action from team
            return self.teamAction.act(state, visited, actVars=actVars)
        else:
            # atomic action
            return self.actionCode

    """
    Returns true if the action is atomic, otherwise the action is a team.
    """
    def isAtomic(self):
        return self.teamAction is None

    """
    Change action to team or atomic action.
    """
    def mutate(self, mutateParams, parentTeam, teams, pActAtom):
        # dereference if old action is team
        if self.teamAction is not None:
            self.teamAction.numLearnersReferencing -= 1

        # mutate action
        if flip(pActAtom):
            # atomic
            self.actionCode = random.choice(mutateParams["actionCodes"])
            self.teamAction = None
        else:
            # team action
            self.teamAction = random.choice([t for t in teams
                    if t is not self.teamAction and t is not parentTeam])
            self.teamAction.numLearnersReferencing += 1
