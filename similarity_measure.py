'''
Example

input:

- index_A = [0,1,2,3,4,5,6,7,8,9]
- keyword_A = "코로나"
- index_B = [0,1,2,3,4,5,6,7,8,9]
- keyword_B = "바이오"

output:

A_list, B_list, AB_list, A_avg, B_avg, AB_avg

'''

import re
import ast

ALPHA = 0.5
BETA = 0.5
JS_DIR_PATH = "C:/Users/kirc/Desktop/Soyoung/KIRC/지식구조 프로그램/knowledge_structure_kirc-master/results/result_webgraph/data/"

def _parse_dict_in_js(_items):
    items = re.findall('\[([^]]+)', _items)
    items = items[0].split("}, ")

    for idx, item in enumerate(items):
        if idx != len(items)-1:
            items[idx] = item+"}"
        items[idx] = ast.literal_eval(items[idx][:])
    return items


def parse_js_file(file_name: str):
    """
    input : js 파일명 (코로나_0)
    output : node_list, edge_list
    """
    with open(JS_DIR_PATH + file_name + ".js", 'r', encoding='utf-8') as f:
        data = f.readlines()

    nodes, edges = data[0], data[2]

    node_list = _parse_dict_in_js(nodes)
    edge_list = _parse_dict_in_js(edges)

    return node_list, edge_list


def unique_node(node_list: list):  # 유니크 값들 추출
    node_set = set()

    for node_dic in node_list:
        node_set.add(node_dic['label'])

    return node_set


def convert_id_to_word(node_list: list):  # ID를 키워드로 바꿔주는 딕셔너리 생성
    id2word = dict()

    for node_dic in node_list:
        idx = node_dic['id']
        word = node_dic['label']

        id2word[idx] = word

    return id2word


def create_score_list(edge_list: list, id2word: dict):  # Score List 생성
    score_list = list()
    for edge_dic in edge_list:
        n1 = edge_dic['from']
        n2 = edge_dic['to']
        score = edge_dic['label']
        score_list.append([id2word[n1], id2word[n2], score])

    return score_list


def jaccard_similarity_score(union_node, intersection_node):
    return round(len(intersection_node) / len(union_node), 5)


def get_avg_score(score_list_A, score_list_B: list):
    score_sum = 0
    count = 0

    for score_A in score_list_A:  # A에 쌍이 있는지 확인
        for score_B in score_list_B:  # 해당 A의 쌍이 B에도 있는지 확인
            if (score_A[0] == score_B[0] and score_A[1] == score_B[1]) \
                    or (score_A[0] == score_B[1] and score_A[1] == score_B[0]):

                # print("겹치는 쌍 : ", score_A, score_B)
                score_diff = abs(float(score_A[2]) - float(score_B[2]))

                count += 1
                score_sum += score_diff

    if count == 0:
        return 0
    else:
        avg_score = score_sum / count
        return 1 - round(avg_score, 3)


def get_ks_similarity(ks_A, ks_B):  # main 함수
    node_list_A, edge_list_A = parse_js_file(ks_A)
    node_list_B, edge_list_B = parse_js_file(ks_B)

    node_set_A = unique_node(node_list_A)
    node_set_B = unique_node(node_list_B)

    union_node = node_set_B.union(node_set_A)

    id2word_A = convert_id_to_word(node_list_A)
    id2word_B = convert_id_to_word(node_list_B)

    score_list_A = create_score_list(edge_list_A, id2word_A)
    score_list_B = create_score_list(edge_list_B, id2word_B)

    intersection_node = node_set_A.intersection(node_set_B)  # 공통 노드 키워드 구하기

    relation_sim = get_avg_score(score_list_A, score_list_B)
    # print("relation_sim : ", relation_sim)
    node_sim = jaccard_similarity_score(union_node, intersection_node)
    # print("node_sim : ", node_sim)

    arithmetic_score = ALPHA * relation_sim + BETA * node_sim
    return arithmetic_score


def get_file_pair_list(index_list: list):  # nC2 구하는 함수
    file_pair_list = list()

    for i in range(len(index_list) - 1):
        for j in range(i + 1, len(index_list)):
            if i == j:
                continue
            else:
                file_pair_list.append([index_list[i], index_list[j]])

    return file_pair_list


def get_nxn_file_list(index_A, index_B):  # n*n 구하는 함수
    nxn_file_list = list()

    for num_A in index_A:
        for num_B in index_B:
            nxn_file_list.append([num_A, num_B])

    return nxn_file_list


def intra_sim(keyword, index_list):
    similarity_sum = 0
    score_list = list()

    if not index_list:  # index list 비어있는 경우. 즉 선택한 기사가 없는 경우

        return score_list, 0.0

    else:
        file_pair_list = get_file_pair_list(index_list)

        for pair in file_pair_list:
            ks_similarity = get_ks_similarity(keyword + '_' + str(pair[0]), keyword + '_' + str(pair[1]))
            similarity_score = round(ks_similarity, 3)

            score_list.append([pair[0], pair[1], similarity_score])
            similarity_sum += similarity_score

        if len(file_pair_list) == 0:
            intra_avg_score = 0
        else:
            intra_avg_score = round(similarity_sum / len(file_pair_list), 3)

        return score_list, intra_avg_score


def inter_sim(keyword_A, keyword_B, index_A, index_B):
    similarity_sum = 0
    score_list = list()

    if not index_A or not index_B:  # index list 비어있는 경우. 즉 선택한 기사가 없는 경우

        return score_list, 0.0

    else:
        file_nxn_pair_list = get_nxn_file_list(index_A, index_B)

        for pair in file_nxn_pair_list:
            ks_similarity = get_ks_similarity(keyword_A + '_' + str(pair[0]), keyword_B + '_' + str(pair[1]))
            similarity_score = round(ks_similarity, 3)

            score_list.append([pair[0], pair[1], similarity_score])
            similarity_sum += similarity_score

        if len(file_nxn_pair_list) == 0:
            inter_avg_score = 0
        else:
            inter_avg_score = round(similarity_sum / len(file_nxn_pair_list), 3)

        return score_list, inter_avg_score


'''
Use Example

input:

- keyword_A = "코로나"
- index_A = [0,1,2,3,4,5,6,7,8,9]
- keyword_B = "바이오"
- index_B = [0,1,2,3,4,5,6,7,8,9]

output:

- A_list, A_avg = intra_sim(keyword_A, index_A)
- B_list, B_avg = intra_sim(keyword_B, index_B)
- AB_list, AB_avg = inter_sim(keyword_A, keyword_B, index_A, index_B)

'''


def similarity_measure(keyword_A, index_A, keyword_B, index_B):
    A_list, A_avg = intra_sim(keyword_A, index_A)
    B_list, B_avg = intra_sim(keyword_B, index_B)
    AB_list, AB_avg = inter_sim(keyword_A, keyword_B, index_A, index_B)

    return A_list, B_list, AB_list, A_avg, B_avg, AB_avg
