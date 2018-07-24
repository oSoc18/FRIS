import numpy as np
from frisr3.research_outputs import ResearchOutput
from itertools import chain, product

from scipy.cluster import hierarchy
from scipy.cluster.hierarchy import fcluster
from scipy.spatial import distance
from scipy.spatial.distance import squareform

from typing import Iterable, List

def get_keyword_set(outputs):
    kw_set = set(chain.from_iterable((o.keywords() for o in outputs)))
    kws = np.array(list(kw_set))

    kw_nums = { k: i for i, k in enumerate(kws) }
    return (kws, kw_nums)


def keyword_mapping(keyword_set, outputs) -> dict:
    mapping = {}
    for output in outputs:
        keywords = mapping.setdefault(output.uuid(), set())

        # Add annotated keywords
        for keyword in output.keywords():
            keywords.add(keyword)

        # Search for keywords in abstract
        abstract = output.abstract()
        if abstract:
            for keyword in keyword_set:
                if keyword in abstract:
                    keywords.add(keyword)
        
        # Search for keywords in title
        title = output.title()
        if title:
            for keyword in keyword_set:
                if keyword in title:
                    keywords.add(keyword)
    return mapping


def keyword_matrix(outputs, kw_nums, kw_mapping):
    mat = np.zeros((len(outputs), len(kw_nums)), dtype=np.bool)
    for output_num, output in enumerate(outputs):
        for kw in kw_mapping[output.uuid()]:
            mat[output_num, kw_nums[kw]] = True
    return mat


def keyword_correlations(kw_nums, kw_mapping):
    n = len(kw_nums)
    # count co-occurences of keywords
    mat = np.zeros((n, n), dtype=np.int32)
    for kw_set in kw_mapping.values():
        nums = [kw_nums[k] for k in kw_set]
        for k1 in nums:
            for k2 in nums:
                mat[k1, k2] += 1
    counts = np.diagonal(mat)
    correlation = mat / (counts + counts[:, np.newaxis] - mat)
    return correlation


def conditional_keyword_probs(kw_nums, kw_mapping):
    n = len(kw_nums)

    # count co-occurences of keywords
    mat = np.zeros((n, n), dtype=np.int32)
    for kw_set in kw_mapping.values():
        nums = [kw_nums[k] for k in kw_set]
        for k1 in nums:
            for k2 in nums:
                mat[k1, k2] += 1
    counts = np.diagonal(mat)
    conditionals = mat / counts[:, np.newaxis]
    return conditionals


def output_profiles(kw_matrix, kw_correlations):
    mat = np.dot(kw_matrix, kw_correlations)
    normalized = mat / np.sum(mat, axis=1)[:, np.newaxis]
    return normalized


def output_similarity(outputs, kw_mapping):
    n = len(outputs)
    similarity = np.zeros((n, n), dtype=np.float64)
    for i, output_i in enumerate(outputs):
        for j, output_j in enumerate(outputs):
            kws1 = kw_mapping[output_i.uuid()]
            kws2 = kw_mapping[output_j.uuid()]
            similarity[i, j] = len(kws1 & kws2) / len(kws1 | kws2)
    return similarity

# Matthews Correlation Coefficient
def matthews_correlation(data, reference):
    s, _ = data.shape
    n, _= reference.shape
    
    # True positives
    tp = np.sum(data, axis=0)
    # False negatives
    fn = np.sum(reference, axis=0) - tp
    # False positives
    fp = s - tp
    # True negatives
    tn = n - s - fn
    
    numerator = tp*tn - fp*fn 
    denominator = np.sqrt((tp + fp) * (tp + fn) * (tn + fp) * (tn + fn))
    mcc = np.divide(numerator, denominator, out=np.zeros_like(numerator), where=denominator!=0)
    return mcc


def cluster_outputs(outputs):
    keywords, kw_nums = get_keyword_set(outputs)
    kw_mapping = keyword_mapping(keywords, outputs)
    # discard outputs without keywords
    outputs = [o for o in outputs if kw_mapping[o.uuid()]]
    kw_matrix = keyword_matrix(outputs, kw_nums, kw_mapping)
    kw_correlations = keyword_correlations(kw_nums, kw_mapping)
    n = len(outputs)


    profiles = output_profiles(kw_matrix, kw_correlations)
    # TODO: avoid converting to square form and back
    distances = squareform(distance.pdist(profiles, 'cosine'))

    Z = hierarchy.ward(squareform(distances))

    # compute membership vectors for each node in the cluster tree
    cluster_elems = np.zeros((2 * n - 1, n), dtype=np.bool)
    cluster_elems[:n] = np.diag(np.ones(n, dtype=np.bool))
    for i in range(n-1):
        a, b = Z[i, 0:2].astype(np.int)
        cluster_elems[n+i, :] = np.logical_or(cluster_elems[a], cluster_elems[b])
    
    # compute correlation between subtree membership and keywords
    mccs = np.array([matthews_correlation(profiles[c], profiles) for c in cluster_elems])
    # assign the best ranking keyword to each node
    kws = np.argmax(mccs, axis=1)
    # put the associated correlation in a vector for easy access
    cluster_mcc = mccs[np.arange(2*n-1), kws]


    # Build parents list
    parents = np.zeros(2 * n - 1, dtype=np.int64)
    parents[2*n-2] = 2*n-2

    for i in reversed(range(n-1)):
        children = Z[i, 0:2].astype(np.int)
            
        mcc, parent_mcc = cluster_mcc[[n+i, parents[n+i]]]
        kw, parent_kw = kws[[n+i, parents[n+i]]]

        if mcc > parent_mcc and kw != parent_kw:
            parents[children] = n + i
        else:
            parents[children] = parents[n+i]

        # for now we'll ignore values that don't belong to a leaf node.
    # because I'm not competent, I defined a leaf node as a node that has
    # at least 1/3 of its size as direct children.
    num_leaf_children = np.zeros(n-1, dtype=np.int)
    for i in range(n):
        num_leaf_children[parents[i] - n] += 1
    print(num_leaf_children - Z[:, 3] / 3)
    is_leaf = num_leaf_children > Z[:, 3] / 3
    # the root may never be a leaf node.
    is_leaf[-1] = False

    for i in reversed(range(n-1)):
        p = parents[n+i]
        if is_leaf[p - n]:
            # if parent is a leaf, discard this node
            parents[parents == n + i] = p            

    nodes = {}
    for p in np.unique(parents):
        if is_leaf[p - n]: 
            research_outputs = [outputs[o].title() for o in np.where(cluster_elems[p])[0]]
            nodes[p] = {
                'name': keywords[kws[p]],
                'size': len(research_outputs),
                'research_outputs': research_outputs,
            }
        else:
            nodes[p] = {
                'name': keywords[kws[p]],
                'size': 0,
                'children': []
            }
    for p in np.unique(parents)[:-1]:
        node = nodes.pop(p)
        parent = nodes[parents[p]]
        parent['children'].append(node)
        parent['size'] += node['size']
        
    tree = nodes[2*n-2]
    tree['name'] = 'root'
    return tree