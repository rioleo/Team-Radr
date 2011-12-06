# config.py
# ---------
# Licensing Information: Please do not distribute or publish solutions to this
# project. You are free to use and extend these projects for educational
# purposes. The Pacman AI projects were developed at UC Berkeley, primarily by
# John DeNero (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# For more info, see http://inst.eecs.berkeley.edu/~cs188/sp09/pacman.html

"""
-----------------------
  Agent Configuration
-----------------------

Settings:

 - TeamName (string)
    The official name of your team. Names
    must be alpha-numeric only. Agents with
    invalid team names will not execute.

 - AgentFactory (string)
    The fully qualified name of the agent
    factory to execute.

 - AgentArgs (dict of string:string)
    Arguments to pass to the agent factory

 - NotifyList (list of strings)
    A list of email addresses to notify
    to when this agent competes.
 - Partners (list of strings)
    Group members who have contributed to
    this agent code and design.

"""

# Alpha-Numeric only
TeamName = 'RADD  --Rio, Aki, Dan, Dan'

# Filename.FactoryClassName (CASE-sensitive)
AgentFactory = 'qAgents.qLearnAgents'

Partners = ['Rio Akasaka, Akihiro Maeda, Daniel Strazzulla, Daniel Wiesenthal']

AgentArgs = {'alpha':0.05, 'epsilon':0.0}

NotifyList = ['rakasaka@stanford.edu','amaeda10@stanford.edu', 'strazz@stanford.edu', 'jepense@stanford.edu']
