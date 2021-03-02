import re
import ast
from typing import Tuple, List

NODE_SIMILARITY_WEIGHT = 0.5
RELATION_SIMILARITY_WEIGHT = 0.5


def _parse_dict_from_js(items: str) -> list:
    """
    Parse dictionary from javascript file.
    js is short for javascript.

    Input
        - items : String of nodes or edges in dictionary format.
    Returns
        - items : List of parsed dictionaries.
    """
    items = re.findall('\[([^]]+)', items)
    items = items[0].split("}, ")

    for idx, item in enumerate(items):
        if idx != len(items) - 1:
            items[idx] = item + "}"
        items[idx] = ast.literal_eval(items[idx][:])

    return items


def parse_js_file(base_path: str, file_name: str) -> Tuple[list, list]:
    """
    Opens javascript file and parses nodes and edges as form of list of dictionaries.
    js is short for javascript.

    Inputs : base_path, file_name
        - base_path : Path where javascript files are saved.
        - file_name : Name of javascript file.

    Returns : nodes, edges
        - nodes : List of parsed node dictionaries.
        - edges : List of parsed edge dictionaries.
    """
    with open(f"{base_path}{file_name}.js", 'r', encoding='utf-8') as f:
        data = f.readlines()

    nodes, edges = data[0], data[2]

    nodes = _parse_dict_from_js(nodes)
    edges = _parse_dict_from_js(edges)

    return nodes, edges


def get_unique_node(nodes: list) -> set:
    node_set = set()

    for node_dict in nodes:
        node_set.add(node_dict['label'])

    return node_set


def convert_id_to_word(nodes: list) -> dict:
    """
    Generates dictionary that converts node 'id' to word.

    Input
        - nodes : list of node dictionaries

    Returns
        - id2word : dictionary with id as key and word as value
    """
    id2word = dict()

    for node_dict in nodes:
        idx = node_dict['id']
        word = node_dict['label']
        id2word[idx] = word

    return id2word


def create_score_list(edges: list, id2word: dict) -> list:
    """
    Creates score list from list of edge dictionaries.

    Input
        - edges : list of edges dictionaries
        - id2word : dictionary with id as key and word as value

    Returns
        - scores : list of similarity scores between node1 and node2
    """
    scores = list()

    for edge_dict in edges:
        node1 = edge_dict['from']
        node2 = edge_dict['to']

        score = edge_dict['label']
        scores.append([id2word[node1], id2word[node2], score])

    return scores


def get_jaccard_similarity(union_node: set,
                           intersection_node: set) -> float:
    return round(len(intersection_node) / len(union_node), 5)


def get_average_score(scores1: list, scores2: list) -> float:
    """
    Calculate average score between common nodes of two score lists.
    """
    score_sum = 0
    count = 0

    for s1 in scores1:
        for s2 in scores2:
            if {s1[0], s1[1]} == {s2[0], s2[1]}:
                score_diff = abs(float(s1[2]) - float(s2[2]))

                count += 1
                score_sum += score_diff

    if not count:
        average_score = 0.0
    else:
        avg_score = score_sum / count
        average_score = 1 - round(avg_score, 3)

    return average_score


def get_ks_similarity(base_path, ks1, ks2) -> float:
    """
    Gets ks similarity score between two knowledge structures.
    ks is short for knowledge structure.
    """
    nodes1, edges1 = parse_js_file(base_path, ks1)
    nodes2, edges2 = parse_js_file(base_path, ks2)

    node_set1 = get_unique_node(nodes1)
    node_set2 = get_unique_node(nodes2)

    union_node = node_set1.union(node_set2)
    intersection_node = node_set1.intersection(node_set2)

    id2word1 = convert_id_to_word(nodes1)
    id2word2 = convert_id_to_word(nodes2)

    scores1 = create_score_list(edges1, id2word1)
    scores2 = create_score_list(edges2, id2word2)

    relation_similarity = get_average_score(scores1, scores2)
    node_similarity = get_jaccard_similarity(union_node, intersection_node)

    ks_similarity = RELATION_SIMILARITY_WEIGHT * relation_similarity + NODE_SIMILARITY_WEIGHT * node_similarity
    return ks_similarity


def get_combinations(indices1, indices2=None) -> List[list]:
    """
    Gets combinations in indices, or between two indices.
    If indices2 is none, get combinations only in indices1.
    """
    combinations = list()

    if indices2 is None:
        for i in range(len(indices1) - 1):
            for j in range(i + 1, len(indices1)):
                if i != j:
                    combinations.append([indices1[i], indices1[j]])
    else:
        for index1 in indices1:
            for index2 in indices2:
                combinations.append([index1, index2])

    return combinations


def get_intra_similarity(base_path, keyword, indices) -> Tuple[float, List[List[float]]]:
    """
    Get intra similarity within a knowledge structure.

    Inputs: base_path, keyword, indices
        - base_path : Path where javascript files are saved.
        - keyword : Search keyword.
        - indices : Indices of selected news articles.

    Returns: intra_similarity, scores
        - intra_similarity : Similarity score within a keyword.
        - scores : Double list of node1, node2 and score
    """
    similarity_sum = 0
    scores = list()

    if not indices:
        intra_similarity = 0.0

    else:
        combinations = get_combinations(indices)

        for combination in combinations:
            ks_similarity = get_ks_similarity(base_path, f"{keyword}_{str(combination[0])}",
                                              f"{keyword}_{str(combination[1])}")
            similarity_score = round(ks_similarity, 3)

            scores.append([combination[0], combination[1], similarity_score])
            similarity_sum += similarity_score

        intra_similarity = round(similarity_sum / len(combinations), 3)

    return intra_similarity, scores


def get_inter_similarity(base_path, keyword1, keyword2, indices1, indices2) -> Tuple[float, List[List[float]]]:
    """
    Get inter similarity between two knowledge structures.

    Inputs: base_path, keyword1, keyword2, indices1, indices2
        - base_path : Path where javascript files are saved.
        - keyword1 : Search keyword1.
        - keyword2 : Search keyword2.
        - indices1 : Indices of selected news articles for keyword1.
        - indices2 : Indices of selected news articles for keyword2.

    Returns: inter_similarity, scores
        - inter_similarity : Similarity score between two keywords.
        - scores : Double list of ks1, ks2 and score
    """
    similarity_sum = 0
    scores = list()

    if not indices1 or not indices2:
        inter_similarity = 0.0

    else:
        combinations = get_combinations(indices1, indices2)

        for combination in combinations:
            ks_similarity = get_ks_similarity(base_path, keyword1 + '_' + str(combination[0]),
                                              keyword2 + '_' + str(combination[1]))
            similarity_score = round(ks_similarity, 3)

            scores.append([combination[0], combination[1], similarity_score])
            similarity_sum += similarity_score

        inter_similarity = round(similarity_sum / len(combinations), 3)

    return inter_similarity, scores


def calc_similarity(base_path, keyword1, indices1, keyword2, indices2):
    intra_average_similarity1, intra_similarities1 = get_intra_similarity(base_path, keyword1, indices1)
    intra_average_similarity2, intra_similarities2 = get_intra_similarity(base_path, keyword2, indices2)
    inter_average_similarity, inter_similarities = get_inter_similarity(base_path, keyword1, keyword2, indices1,
                                                                        indices2)

    return intra_similarities1, intra_similarities2, inter_similarities, \
           intra_average_similarity1, intra_average_similarity2, inter_average_similarity
