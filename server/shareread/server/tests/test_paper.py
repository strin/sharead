'''
tests for module shareread.server.paper.
'''
import shareread.server.db as db
from shareread.server.paper import *
from datetime import datetime


def test_inverse_indexing():
    db.flush_db()
    # test indexing process.
    save_paper_entry('swift', {
        'title': 'Swift: Compiled Inference For Probabilistic Programming Languages',
        'abstract': '''A probabilistic program defines a probability mea-sure over its semantic structures. One common goal of probabilistic programming languages (PPLs) is to compute posterior probabilities for arbitrary models and queries, given observed evidence, us-ing a generic inference engine. Most PPL infer-ence engines\\u2014even the compiled ones\\u2014incur sig-nificant runtime interpretation overhead, especially for contingent and open-universe models. This paper describes Swift, a compiler for the BLOG PPL. Swift-generated code incorporates optimiza-tions that eliminate interpretation overhead, main-tain dynamic dependencies efficiently, and handle memory management for possible worlds of vary-ing sizes. Experiments comparing Swift with other PPL engines on a variety of inference problems demonstrate speedups ranging from 12x to 326x.'''
    })
    save_paper_entry('deeprl', {
        'title': 'Curiosity-driven Exploration In Deep Reinforcement Learning Via Bayesian Neural Networks',
        'abstract': '''Scalable and effective exploration remains a key challenge in reinforcement learn-ing (RL). While there are methods with optimality guarantees in the setting of dis-crete state and action spaces, these methods cannot be applied in high-dimensional deep RL scenarios. As such, most contemporary RL relies on simple heuristics such as exploration or adding Gaussian noise to the controls. This paper introduces Variational Information Maximizing Exploration (VIME), an explo-ration strategy based on maximization of information gain about the agent\'s belief of environment dynamics. We propose a practical implementation, using varia-tional inference in Bayesian neural networks which efficiently handles continuous state and action spaces. VIME modifies the MDP reward function, and can be applied with several different underlying RL algorithms. We demonstrate that VIME achieves significantly better performance compared to heuristic exploration methods across a variety of continuous control tasks and algorithms, including tasks with very sparse rewards.'''
    })
    save_paper_entry('bitcoin', {
        'title': 'Bitcoin: A Peer-to-peer Electronic Cash System',
        'abstract': '''A purely peer-to-peer version of electronic cash would allow online payments to be sent directly from one party to another without going through a financial institution. Digital signatures provide part of the solution, but the main benefits are lost if a trusted third party is still required to prevent double-spending. We propose a solution to the double-spending problem using a peer-to-peer network. The network timestamps transactions by hashing them into an ongoing chain of hash-based proof-of-work, forming a record that cannot be changed without redoing the proof-of-work. The longest chain not only serves as proof of the sequence of events witnessed, but proof that it came from the largest pool of CPU power. As long as a majority of CPU power is controlled by nodes that are not cooperating to attack the network, they\'ll generate the longest chain and outpace attackers. The network itself requires minimal structure. Messages are broadcast on a best effort basis, and nodes can leave and rejoin the network at will, accepting the longest proof-of-work chain as proof of what happened while they were gone'''
    })
    save_paper_entry('example', {
        'title': 'Example',
        'authors': [{"first_name": "Satoshi", "last_name": "Nakamoto"}]
    }) # a case where abstract does not exist.
    inverse_indexing_once()
    store = KeyValueStore('paperwords:bitcoin')
    assert(store.get('bitcoin'))
    assert(store.get('peer-to-peer'))
    # test query.
    assert(rank_by_inverted_words('bitcoin: peer-to-peer')[0] == 'bitcoin')
    assert(rank_by_inverted_words('probability semantic')[0] == 'swift')
    assert(rank_by_inverted_words('satoshi')[0] == 'example')
    # print rank_by_inverted_words('')[0]
    # assert(False)
