import numpy as np
from frisr3.research_outputs import ResearchOutput
from itertools import chain, product

from scipy.cluster import hierarchy
from scipy.cluster.hierarchy import fcluster
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

def output_similarity(outputs, kw_mapping):
    n = len(outputs)
    similarity = np.zeros((n, n), dtype=np.float64)
    for i, output_i in enumerate(outputs):
        for j, output_j in enumerate(outputs):
            kws1 = kw_mapping[output_i.uuid()]
            kws2 = kw_mapping[output_j.uuid()]
            similarity[i, j] = len(kws1 & kws2) / len(kws1 | kws2)
    return similarity


MAX_CLUSTER_SIZE = 15
def cluster_outputs(outputs, root_name):
    keywords, kw_nums = get_keyword_set(outputs)
    kw_mapping = keyword_mapping(keywords, outputs)
    # discard outputs without keywords
    outputs = [o for o in outputs if kw_mapping[o.uuid()]]
    kw_matrix = keyword_matrix(outputs, kw_nums, kw_mapping)
    similarity = output_similarity(outputs, kw_mapping)
    distances = 1 - similarity

    def cluster_idxs(idxs):
        """ cluster a subset of the outputs """
        dists = distances[np.ix_(idxs, idxs)]
        Z = hierarchy.ward(squareform(dists))

        labels = fcluster(Z, criterion='distance', t=(0.7*np.max(Z[:,2])))

        clusters = {}
        for (i, label) in enumerate(labels):
            clusters.setdefault(label, []).append(idxs[i])
        return [np.array(c) for c in clusters.values()]

    def cluster_tree(idxs):
        """ recursively cluster a subset of the outputs """
        children = []
        for cluster in cluster_idxs(idxs):
            node = {}
            node['name'] = "No name yet"
            node['size'] = len(cluster)
            if len(cluster) > MAX_CLUSTER_SIZE:
                node['children'] = cluster_tree(cluster)
            else:
                node_outputs = []
                for idx in cluster:
                    output = outputs[idx]
                    attrs = outputs[idx].attributes()
                    attrs['keywords'] = list(kw_mapping[output.uuid()])
                    node_outputs.append(attrs)
                node['research_outputs'] = node_outputs
            children.append(node)
        children.sort(key=lambda c: c['size'], reverse=True)
        return children
    
    return {
        'name': root_name,
        'size': len(outputs),
        'children': cluster_tree(np.arange(len(outputs))),
    }


