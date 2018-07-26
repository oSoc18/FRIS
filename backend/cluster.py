import numpy as np
from frisr3.research_outputs import ResearchOutput
from itertools import chain, product

from scipy.cluster import hierarchy
from scipy.cluster.hierarchy import fcluster
from scipy.spatial import distance
from scipy.spatial.distance import squareform

def cluster_outputs(outputs):
    """ perform the clustering routine """
    keywords, kw_nums = get_keyword_set(outputs)
    kw_mapping = keyword_mapping(keywords, outputs)

    # discard outputs without keywords
    outputs = np.array([o for o in outputs if kw_mapping[o.uuid()]])
    n = len(outputs)

    conditionals = conditional_keyword_probs(kw_nums, kw_mapping)
    kw_matrix = keyword_matrix(outputs, kw_nums, kw_mapping)

    kw_fsets = keyword_fuzzsets(kw_matrix, conditionals)
    projected = pca(kw_fsets)

    distances = distance.pdist(projected, 'euclidean')
    Z = hierarchy.ward(distances)
    return assemble_tree(keywords, outputs, Z, kw_fsets)

def get_keyword_set(outputs):
    """ gather the set of all keywords occuring in the outputs"""
    kw_set = set(chain.from_iterable((o.keywords() for o in outputs)))
    kws = np.array(list(kw_set))

    kw_nums = { k: i for i, k in enumerate(kws) }
    return (kws, kw_nums)


def keyword_mapping(keyword_set, outputs):
    """
    Create a mapping between outputs and the keywords associated with them.
    In addition to the keywords the research outputs have been labeled with in
    the FRIS database, titles and abstracts are searched for known keywords
    in order to get data on untagged outputs.
    """
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
    """
    Create a boolean matrix that has outputs for rows and keywords for columns,
    that is True if the output was labelled with the keyword.
    """
    mat = np.zeros((len(outputs), len(kw_nums)), dtype=np.bool)
    for output_num, output in enumerate(outputs):
        for kw in kw_mapping[output.uuid()]:
            mat[output_num, kw_nums[kw]] = True
    return mat


def conditional_keyword_probs(kw_nums, kw_mapping):
    """ Compute the conditional probabilities between having keywords """
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


def keyword_fuzzsets(kw_matrix, conditionals):
    """
    The keyword data is very sparse and incomplete. This procedure creates a
    bayesian model of keyword co-occurence, and then uses that to predict the
    chance of an output having a certain keyword. This results in a fuzzy
    keyword set.
    """
    kw_fsets = np.zeros(kw_matrix.shape, dtype=np.float64)
    neg_conditionals = 1 - conditionals

    for i, observation in enumerate(kw_matrix):
        kw_fsets[i, :] = 1 - np.product(neg_conditionals[observation], axis=0)
    return kw_fsets


def pca(kw_fsets, retained_variance=0.99):
    """ Extract principal components from the keyword fuzzsets """
    corr = np.corrcoef(kw_fsets.T)
    eig_vals, eig_vecs = np.linalg.eigh(corr)

    total = np.sum(eig_vals)
    idxs = np.argsort(eig_vals)[::-1]

    cum_energy = np.cumsum(eig_vals[idxs] / total)
    k = np.sum(np.cumsum(eig_vals[idxs]/total) < retained_variance)
    
    proj = eig_vecs[:, idxs[:k]]

    projected = np.dot(kw_fsets, proj)
    return projected


# Matthews Correlation Coefficient
def mcc(data, reference):
    """
    Calculate the Matthews correlation coefficient between being contained in
    the given data set and having a certain keyword.
    """
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


MCC_TRESHOLD = 0.2
MIN_LEAF_SIZE = 5
MAX_LEAF_SIZE = 20

def assemble_tree(keywords, outputs, Z, kw_fsets):
    """
    Assemble a hierarchy for given keywords and outputs, based on the given
    cluster tree. This is done by removing bad internal nodes from the cluster
    tree, until a half-decent result is obtained.
    """
    n = len(outputs)

    # compute membership vectors for each node in the cluster tree
    cluster_elems = np.zeros((2 * n - 1, n), dtype=np.bool)
    cluster_elems[:n] = np.diag(np.ones(n, dtype=np.bool))
    for i in range(n-1):
        a, b = Z[i, 0:2].astype(np.int)
        cluster_elems[n+i, :] = np.logical_or(cluster_elems[a], cluster_elems[b])

    # compute correlation between subtree membership and keywords
    mccs = np.array([mcc(kw_fsets[c], kw_fsets) for c in cluster_elems])
    # assign the best ranking keyword to each node
    kws = np.argmax(mccs, axis=1)
    # put the associated correlation in a vector for easy access
    cluster_mcc = mccs[np.arange(2*n-1), kws]

    # This list keeps a reference to the parent of each node
    parents = np.zeros(2 * n - 1, dtype=np.int64)
    # make the root its own parent
    parents[2*n-2] = 2*n-2

    # intialize parent references
    for i in reversed(range(n-1)):
        children = Z[i, 0:2].astype(np.int)
        parents[children] = n + i

    
    # Keeps track of which nodes were deleted.
    # This is used for fixing the parent references after deletion.
    deleted = np.zeros(n-1, dtype=np.bool)

    # A node is a leaf node when it has at least one leaf child
    is_leaf_node = np.zeros(n-1, dtype=np.bool)
    is_leaf_node[parents[:n] - n] = True

    # merge small leaf nodes together to avoid overfitting and uncomfortableness
    for i in reversed(range(n-1)):
        if Z[i, 3] < MIN_LEAF_SIZE and Z[parents[n+i]-n, 3] < MAX_LEAF_SIZE:
            deleted[i] = True
            is_leaf_node[parents[n+i] - n] = True

    # flatten leaf nodes (so that there are no nodes that have both output
    # children and node children)
    for i in reversed(range(n - 1)):
        if deleted[parents[n+i] - n]:
            # n+i's parent was deleted, find a new one
            parents[n+i] = parents[parents[n+i]]
            deleted[i] = True

        if is_leaf_node[parents[n+i] - n]:
            # n+i's parent is a leaf node; flatten them!
            deleted[i] = True

    fix_references(parents, deleted)

    # finally, prune nodes that form bad categories.
    # We don't prune leaf nodes because that would mess with the tree structure.
    for i in range(n-1):
        if (not is_leaf_node[i]) and cluster_mcc[n+i] < MCC_TRESHOLD:
            deleted[i] = True

    fix_references(parents, deleted)

    nodes = {
        2*n-2: {
            'name': 'root',
            'size': 0,
            'children': [],
        }
    }  

    for i in range(n-2):
        if deleted[i]:
            continue

        if is_leaf_node[i]:
            nodes[n+i] = {
                'name': keywords[kws[n+i]],
                'size': 0,
                'mcc': cluster_mcc[n+i],
                'research_outputs': [],
            }
        else:
            nodes[n+i] = {
                'name': keywords[kws[n+i]],
                'mcc': cluster_mcc[n+i],
                'size': 0,
                'children': [],
            }

    for i in range(n):
        node = nodes[parents[i]]
        node['research_outputs'].append(outputs[i].attributes())
        node['size'] += 1
    
    for i in range(n-2):
        if not deleted[i]:
            node = nodes.pop(n+i)
            parent = nodes[parents[n+i]]
            parent['children'].append(node)
            parent['size'] += node['size']
    
    tree = nodes[2*n-2]
    tree['name'] = 'root'
    return tree

def fix_references(parents, deleted):
    """
    Assign children of deleted parent to their lowest non-deleted ancestor.
    """
    n = len(deleted) + 1
    for i in reversed(range(2*n-1)):
        if deleted[parents[i] - n]:
            parents[i] = parents[parents[i]]
