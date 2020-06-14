# -*- coding:utf-8 -*-
__author__ = 'yangjian'
"""

"""
from .mcts_core import *
from ..core.searcher import Searcher, OptimizeDirection
from ..core.meta_learner import MetaLearner
from ..core.trial import get_default_trail_store


class MCTSSearcher(Searcher):
    def __init__(self, space_fn, policy=None, max_node_space=10, use_meta_learner=True, candidates_size=10,
                 optimize_direction=OptimizeDirection.Minimize, dataset_id=None, trail_store=None):
        if policy is None:
            policy = UCT()
        self.tree = MCTree(space_fn, policy, max_node_space=max_node_space)
        Searcher.__init__(self, space_fn, optimize_direction, dataset_id=dataset_id, trail_store=trail_store)
        self.best_nodes = {}
        self.use_meta_learner = use_meta_learner
        self.histroy = None
        self.meta_learner = None
        self.candidate_size = candidates_size

    def sample(self, history):
        print('Sample')
        if self.use_meta_learner and history is not None and self.histroy is None:
            self.histroy = history
            self.meta_learner = MetaLearner(history, self.dataset_id, self.trail_store)
        space_sample, best_node = self.tree.selection_and_expansion()
        print(f'Sample: {best_node.info()}')

        # count = 0
        # while best_node.is_terminal and best_node.visits > 0:
        #     if count > 1000:
        #         raise RuntimeError('Unable to obtain a valid sample.')
        #     space_sample, best_node = self.tree.selection_and_expansion()
        #     count += 1
        if self.use_meta_learner and self.meta_learner is not None:
            space_sample = self._select_best_candidate(best_node)
        else:
            space_sample = self.tree.roll_out(space_sample, best_node)
        self.best_nodes[space_sample.space_id] = best_node
        return space_sample

    def _select_best_candidate(self, node):
        candidates = []
        scores = []
        for i in range(self.candidate_size):
            space_sample = self.tree.node_to_space(node)
            candidate = self.tree.roll_out(space_sample, node)
            candidates.append(candidate)
            scores.append(self.meta_learner.predict(candidate))
        index = np.argmax(scores)
        print(f'selected candidates scores:{scores}, argmax:{index}')
        return candidates[index]

    def get_best(self):
        raise NotImplementedError

    def update_result(self, space_sample, result):
        best_node = self.best_nodes[space_sample.space_id]
        print(f'Update result: space:{space_sample.space_id}, result:{result}, node:{best_node.info()}')
        self.tree.back_propagation(best_node, result)
        print(f'After back propagation: {best_node.info()}')
        print('\n\n')
        if self.use_meta_learner and self.meta_learner is not None:
            assert self.meta_learner is not None
            self.meta_learner.new_sample(space_sample)

    def summary(self):
        return str(self.tree.root)

    def reset(self):
        raise NotImplementedError

    def export(self):
        raise NotImplementedError