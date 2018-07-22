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


def cluster_outputs(outputs, root_name):
    keywords, kw_nums = get_keyword_set(outputs)
    kw_mapping = keyword_mapping(keywords, outputs)
    # discard outputs without keywords
    outputs = [o for o in outputs if kw_mapping[o.uuid()]]
    kw_matrix = keyword_matrix(outputs, kw_nums, kw_mapping)
    kw_correlations = keyword_correlations(kw_nums, kw_mapping)

    profiles = output_profiles(kw_matrix, kw_correlations)
    # TODO: avoid converting to square form and back
    distances = squareform(distance.pdist(profiles, 'cosine'))

    Z = hierarchy.ward(squareform(distances))
    labels = fcluster(Z, criterion='distance', t=0.3*np.max(Z[:, 2]))

    cs = {}
    for (i, label) in enumerate(labels):
        cs.setdefault(label, []).append(i)
    clusters = [np.array(c) for c in cs.values()]

    def group_keyword(idxs):
        profile = np.mean(profiles[idxs], axis=0)
        avg_profile = np.mean(profiles, axis=0)
        # kw_vec = np.mean(kw_vecs[pubs], axis=0)
        scores = profile - avg_profile
        best = np.argmax(scores)
        return best
    
    children = []
    for c in clusters:
        children.append({
            'name': keywords[group_keyword(c)],
            'size': len(c),
            'research_outputs': [outputs[i].attributes() for i in c],
        })
    children.sort(key=lambda c: c['size'], reverse=True)

    return {
        'name': root_name,
        'size': len(outputs),
        'children': children,
    }
