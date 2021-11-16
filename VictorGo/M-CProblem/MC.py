# -*- coding: utf-8 -*-
# @Description:
# @author: victor
# @create time: 2021-10-16-2:37 下午
from queue import PriorityQueue
from queue import Queue
import time

"""
M-C Problem description:
There were N missionaries and N savages coming to the river to go across the river.
There was a boat on the river bank, which could be used by at least k people at a time.
Ask the missionaries how to plan a ferry program for safety, so that at any time,
when missionaries and savages coexist, the number of savages on both sides of the river
and on board will always not exceed the number of missionaries.
IN other words, the following inequality equation should be satisfied:
1) M >= C              in the case of coexistence
2) M + C <= k          in the ferrying process
"""


def heuristic_function(next_state):
    """
    The function is defined the heuristic function used in the a-star search algorithm.
    Here it is defined as:
                                h = m + c - 2 * b

    :param next_state: the next state, which is a tuple (m, c, b)
    :return: the calculation result
    """
    m, c, b = next_state
    return m + c - 2 * b


class M_C_Problem:
    def __init__(self, N=3, k=2):
        """
        This class is used to solve the Missionaries and Savage (MC) problem
        :param N: the initial number of Missionaries and Savages
        :param k: the limited load of the vessel (boat)
        """
        self.N = N
        self.k = k
        self.start_state = (N, N, 1)
        self.goal_state = (0, 0, 0)

    def a_star_search(self):
        """
        This function implements the a star searching algorithm using the defined heuristic function

        :return: the dictionary of all trajectories and the estimation of all states stored before the final state
        """
        # construct the data structures that are needed to use to store the information
        Branches = PriorityQueue()
        Branches.put((heuristic_function(self.start_state), self.start_state))
        parent_states = dict()
        estimations = dict()
        deep = dict()

        # initialize the values of the initial state
        parent_states[self.start_state] = None
        estimations[self.start_state] = heuristic_function(self.start_state)
        deep[self.start_state] = 0

        while not Branches.empty():
            estimation, current_state = Branches.get()

            # is the current state is the goal state, the search finishes
            if current_state == self.goal_state:
                break

            # find the next legal states based on the current state and increase the depth by one
            legal_states = self.next_legal_states(current_state)

            for i in range(len(legal_states)):
                next_state = legal_states[i]
                if next_state not in deep:
                    deep[next_state] = deep[current_state] + 1
                new_estimation = deep[next_state] + heuristic_function(next_state)
                if next_state not in estimations:
                    estimations[next_state] = new_estimation
                    Branches.put((new_estimation, next_state))
                    parent_states[next_state] = current_state

                # print("*******", next_state, estimations[next_state], "******")
        return parent_states, estimations

    def BFS(self):
        Branches = Queue()
        Branches.put(self.start_state)
        parent_states = dict()
        parent_states[self.start_state] = None

        while not Branches.empty():
            current_state = Branches.get()

            # is the current state is the goal state, the search finishes
            if current_state == self.goal_state:
                break
            # find the next legal states based on the current state
            legal_states = self.next_legal_states(current_state)

            for i in range(len(legal_states)):
                next_state = legal_states[i]
                if next_state not in parent_states:
                    Branches.put(next_state)
                    parent_states[next_state] = current_state

        return parent_states

    def is_legal(self, state):
        """
        This function is used to find whether the input state is legal or not.

        :param state: the current state, which is a tuple (m , c, b)
        :return: a boolean value
        """
        m, c, b = state

        # the state is illegal if the value of m or c is smaller than 0
        if m < 0 or c < 0:
            return False

        # Situation 1: m equals to c
        # [1] m = c = N, the state is legal only b = 1
        if m == self.N and m == c:
            if b == 1:
                return True
            elif b == 0:
                return False
        # [2] m = c < N, and m is not equal to 0, the states in this condition is always legal,
        # note that the states (0, 0, 1) and (0, 0, 0) does not include.
        if m < self.N and m == c and m != 0:
            return True

        # Situation 2: m is not equal to c
        # [1] m = N
        if m == self.N:
            # the states are legal in any state when b = 0
            if b == 0 and m != c:
                return True
            # as b = 1, the states are legal only when the following equation can be satisfied: N - m' = c1 - n'
            elif b == 1:
                if self._exist1(c):
                    return True
        # [2] m = 0
        if m == 0:
            # the states are legal in any state when b = 1
            if b == 1 and m != c:
                return True
            # as b = 0, the states are legal only when the following equation can be satisfied: m' = c1 + b
            elif b == 0:
                if self._exist2(c):
                    return True
        # if all the above condition can be satisfied, then return false
        return False

    def _exist1(self, c):
        """
        This function is used to find whether there are values of m' and c' making (N - a) == (c - b) possible.

        :param c: the value of c in the current state
        :return: a boolean value
        """
        flag = False
        for a in range(self.k + 1):
            for b in range(self.k - a + 1):
                if a == 0 and c != 0:
                    flag = True
                else:
                    if (self.N - a) == (c - b) and a >= b and a + b <= self.k:
                        flag = True
        return flag

    def _exist2(self, c):
        """
        The function is used to find whether there are values of m' and c' making m' = c + c' possible.

        :param c: the value of c in the current state
        :return: a boolean value
        """
        flag = False
        for a in range(self.k + 1):
            for b in range(self.k - a + 1):
                if a == 0 and c != self.N:
                    flag = True
                else:
                    if a == (c + b) and a >= b and a + b <= self.k:
                        flag = True

        return flag

    def next_legal_states(self, current_state):
        """
        This function is used to find the next legal states based on the current state.
        :param current_state: the current state
        :return: the list of all the legal next states
        """
        m, c, b = current_state
        legal_states = []
        if b == 1:
            for i in range(self.k + 1):
                for j in range(self.k - i + 1):
                    new_state = (m - i, c - j, 0)
                    if m - i >= 0 and c - j >= 0:
                        if self.is_legal(new_state) and new_state != (m, c, 0):
                            legal_states.append(new_state)

        elif b == 0:
            for i in range(self.k + 1):
                for j in range(self.k - i + 1):
                    new_state = (m + i, c + j, 1)
                    if m + i <= self.N and c + j <= self.N:
                        if self.is_legal(new_state) and new_state != (m, c, 1):
                            legal_states.append(new_state)

        return legal_states

    def find_all_illegal_states(self):
        """
        This function is used to find all the legal states of a MC problem
        :return: the list of a ll the legal states
        """
        count = 0
        all_illegal_states = []
        for i in range(self.N + 1):
            for j in range(self.N + 1):
                for n in range(2):
                    if self.is_legal((i, j, n)):
                        all_illegal_states.append((i, j, n))
                        count += 1

        return count, all_illegal_states

    def print_optimal_trajectory(self, trajectories):
        """
        This function is used to print the optimal trajectory and its length
        :param trajectories: all the trajectories
        :return: None
        """
        trajectory = []
        count = 0
        current_state = self.goal_state

        # if self.goal_state not in trajectories:
        #     print("*********************The problem does not have a solution**********************")
        #     return

        while current_state != self.start_state:
            trajectory.append(current_state)
            count += 1
            current_state = trajectories[current_state]

        trajectory.append(self.start_state)
        trajectory.reverse()
        print("The optimal trajectory is:")
        for i in range(len(trajectory)):
            print(trajectory[i], end='')
            if i + 1 < len(trajectory):
                print("==>", end='')
        print()

        print("The total length is: ", count)


if __name__ == "__main__":
    print()
    print("*************************Welcome to MC-problem solver***********************")
    print("----------------------------------------------------------------------------")
    flag = True
    while(flag):
        # input N
        print("Please enter the number of missionaries or cannibals:")
        N = input(">")
        while not N.isdigit():
            print("Please enter a valid integer:")
            N = input(">")

        if N.isdigit():
            N = int(N)

        # input k
        print("Please enter the maximum load of th boat (greater than or equal to 2):")
        k = input(">")
        flag1 = False
        # flag2 = False
        # while(not flag1 or not flag2):
        #     while not k.isdigit():
        #         print("Please enter a valid integer:")
        #         k = input(">")
        #         flag1 = True
        #
        #     k = int(k)
        #     while k < 2:
        #         print("The maximum load of th boat should be greater than or equal to 2:")
        #         k = input(">")
        #         if k.isdigit():
        #             k = int(k)
        #             if k < 2:
        #
        #
        #         else:
        #             break

        # input iteration time
        print("Please enter the maximum number of iteration time:")
        Maxtime = input(">")
        while not Maxtime.isdigit():
            print("Please enter a valid integer:")
            Maxtime = input(">")
        Maxtime = int(Maxtime)

        # run the solver
        test1 = M_C_Problem(N, k)

        print("********************************Running Time*********************************")
        print("-----------------------------------------------------------------------------")
        start1 = time.time()
        for i in range(Maxtime):
            trajectories1, estimations = test1.a_star_search()
        end1 = time.time()
        print("The search time cost by A* algorithm after ", Maxtime, " iterations: ", (end1 - start1))

        start2 = time.time()
        for i in range(Maxtime):
            trajectories2 = test1.BFS()
        end2 = time.time()
        print("The search time cost by BFS algorithm after ", Maxtime, " iterations: ", (end2 - start2))
        print()

        print("*******************************Running Results*******************************")
        print("-----------------------------------------------------------------------------")
        if (0, 0, 0) not in trajectories2:
            print("The problem does not have a solution")
        else:
            print("The trajectory obtained by BFS algorithm:")
            test1.print_optimal_trajectory(trajectories2)
            print()
            print("The trajectory obtained by A* algorithm:")
            test1.print_optimal_trajectory(trajectories1)
        print()

        print("-----------------------------------------------------------------------------")
        print("Please enter 'l' if you want to look through all the legal states of the problem,")
        print("or type any letter to keep on")
        legal = input(">")
        if legal == 'l':
            count, legal_states = test1.find_all_illegal_states()
            print("The total number of the legal states is:", count)
            print(legal_states)

        print("-----------------------------------------------------------------------------")
        print("Please enter 'q' to quit the program, or type any letter to keep on.")
        quit = input(">")
        if quit == 'q':
            flag = False
            print("----------------------------------Bye Bye------------------------------------")
        print()
        print("-----------------------------------------------------------------------------")
