import random
from environment import Agent, Environment
from planner import RoutePlanner
from simulator import Simulator

class LearningAgent(Agent):
    """An agent that learns to drive in the smartcab world."""

    def __init__(self, env):
        super(LearningAgent, self).__init__(env)  # sets self.env = env, state = None, next_waypoint = None, and a default color
        self.color = 'red'  # override color
        self.planner = RoutePlanner(self.env, self)  # simple route planner to get next_waypoint
        # TODO: Initialize any additional variables here
        # All possible actions
        actions = self.env.valid_actions 
        # Traffic light state choices
        traffic_light = ['red', 'green']
        # All other states have the same choices
        waypoint, oncoming, left = actions, actions, actions
        # Initialize a dictionary to store the Q-values, intialized with all zeros        
        self.q_table = {}
        for li in traffic_light:
            for pt in waypoint:
                for on in oncoming:
                    for lf in left:
                        self.q_table[(li, pt, on, lf)] = {None: 0, 'forward': 4, 'left': 4, 'right': 4}
                        
    def reset(self, destination=None):
        self.planner.route_to(destination)
        # TODO: Prepare for a new trip; reset any variables here, if required

    def update(self, t):
        # Gather inputs
        self.next_waypoint = self.planner.next_waypoint()  # from route planner, also displayed by simulator
        inputs = self.env.sense(self)
        deadline = self.env.get_deadline(self)

        # TODO: Update state
        self.state = (inputs['light'],
                      self.next_waypoint,
                      inputs['oncoming'],
                      inputs['left'])
        print "The current state is: {}".format(self.state)
        print "t:{}".format(t)
        
        # TODO: Select action according to your policy
        action = max(self.q_table[self.state],
                     key=self.q_table[self.state].get)

        # Execute action and get reward
        reward = self.env.act(self, action)

        # TODO: Learn policy based on state, action, reward
        # Set parameters
        alpha = 0.5  # learning rate
        gamma = 0.75 # discount factor
        
        
        # New state after the above action
        inputs_new = self.env.sense(self)
        state_new = (inputs_new['light'],
                     self.planner.next_waypoint(),
                     inputs_new['oncoming'],
                     inputs_new['left'])
        
        # Q_value Calculation
        q_value = (1 - alpha) * self.q_table[self.state][action] + \
                  alpha * (reward + gamma * max(self.q_table[state_new].values()))
        # Q_table Update
        self.q_table[self.state][action] = q_value
        # Set current state and action as previous state and action
        self.state_prev = self.state
        self.action_prev = action
        
        
        print "LearningAgent.update(): deadline = {}, inputs = {}, action = {}, reward = {}".format(deadline, inputs, action, reward)  # [debug]


def run():
    """Run the agent for a finite number of trials."""

    # Set up environment and agent
    e = Environment()  # create environment (also adds some dummy traffic)
    a = e.create_agent(LearningAgent)  # create agent
    e.set_primary_agent(a, enforce_deadline=True)  # specify agent to track
    # NOTE: You can set enforce_deadline=False while debugging to allow longer trials

    # Now simulate it
    sim = Simulator(e, update_delay=0.1, display=False)  # create simulator (uses pygame when display=True, if available)
    # NOTE: To speed up simulation, reduce update_delay and/or set display=False

    sim.run(n_trials=100)  # run for a specified number of trials
    # NOTE: To quit midway, press Esc or close pygame window, or hit Ctrl+C on the command-line


if __name__ == '__main__':
    run()

