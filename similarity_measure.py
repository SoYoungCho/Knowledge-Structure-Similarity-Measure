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
from typing import Tuple

ALPHA = 0.5
BETA = 0.5


# base_path = "C:/Users/kirc/Desktop/Soyoung/KIRC/지식구조 프로그램/knowledge_structure_kirc-master/results/result_webgraph/data/"
# path는 변수로 받로고 해야함


def _parse_dict_from_js(items):
    # js는 풀어쓰거나, 아래 doc string으로 주석 추가 필요
    items = re.findall('\[([^]]+)', items)
    items = items[0].split("}, ")

    for idx, item in enumerate(items):
        if idx != len(items) - 1:
            items[
                idx] = item + "}"  # item + "}"와 같이 더해서 결합하는 것은 권장하지 않음. f"{item}}". 여기서는 중괄호라 그런지 안 먹힘. f"{변수명}합칠 문자열" : 문자열 합치기 f-string
        items[idx] = ast.literal_eval(items[idx][:])
    return items


def parse_js_file(base_path, file_name: str) -> Tuple[list, list]:
    """
    자바스크립트에서 온 딕셔너리 형태의 문자열을 딕셔너리로 변환해준다.
    input : js 파일명 (코로나_0)
    output : node_list, edge_list
    """
    with open(base_path + file_name + ".js", 'r', encoding='utf-8') as f:
        data = f.readlines()

    nodes, edges = data[0], data[2]

    nodes = _parse_dict_from_js(nodes) # 원래는 nodes_list였는데, 변수명은 비슷한 건 통일해주는 것이 좋다고 함.
    edges = _parse_dict_from_js(edges)

    return nodes, edges


def get_unique_node(nodes: list):  # 유니크 값들 추출. 함수명은 변수명같이 지으면 안됨. 그리고 변수는 일반적으로 리스트나 튜플이기에 뒤에 자료형을 생략해서 변수명을 지을 수 있음.
    # 딕셔너리 형태만 자주 사용하지 않기에 예외. .set도 마찬가지.
    node_set = set()

    for node_dict in nodes: # 딕셔너리도 dic말고 dict로 .
        node_set.add(node_dict['label'])

    return node_set


def convert_id_to_word(nodes: list):  # ID를 키워드로 바꿔주는 딕셔너리 생성 . 주석은 웬만하면 안쓰기. 주석을 쓰지 않아도 이해가 갈정도로 짜기. 주석을 단다면 독스트링으로
    # 독스트링으로 하면 나중에 문서를 만들 때도 자동으로 만들어짐. 설명이 필요하면 독스트링 내에서 끝내기. 설명은 주석으로 하지 않는 것이 파이썬의 암묵적인 룰
    # 독스트링 안에는 함수 기능이랑 인풋 아웃풋. 귀찮으면 간단한 설명만 쓰는게 좋음. 이름에서 너무 명확히 나오면 (본 함수같이) 패스 가능.
    id2word = dict()

    for node_dict in nodes:
        idx = node_dict['id']
        word = node_dict['label']
        id2word[idx] = word  # 한줄만 똑 떨어져 있으면 그냥 합치는 게 낫다. 만일 기능적으로 분리되면 두줄 세줄 두줄 이런식으로 띄는데, 한줄이면 그냥 붙이자.

    return id2word


def create_score_list(edges: list, id2word: dict) -> list:  # Score List 생성
    scores = list()
    # 여기처럼 변수 선언하고 for 문 전에 한칸 띄기. 함수 선언하며 변수를 다 선언하고 시작. 선언부, 로직부 나누어져 있으면 보기 편함
    for edge_dict in edges:
        node1 = edge_dict['from'] #n1, n2였던걸 node1 node2로 바꿈. node_1처럼 숫자에 언더바 붙이는 것은 보기 흉함
        node2 = edge_dict['to']
        # 여기 띄어쓰기함!
        score = edge_dict['label']
        scores.append([id2word[node1], id2word[node2], score])

    return scores


def get_jaccard_similarity(union_node, intersection_node): # jaccard_similarity_score가 기존 함수명이였음. 이것도 변수명같으니 고쳐주고, score 가 없어도 직관적이니 뺌.
    return round(len(intersection_node) / len(union_node), 5)


def get_average_score(scores1, scores2: list): # get_avg_score 였는데, 그냥 풀어서 씀. 이건 사람 스타일 문제. 구글은 줄여서 쓰고 애플은 풀어서 씀. 정답이 없음.
    score_sum = 0
    count = 0

    for s1 in scores1:  # A에 쌍이 있는지 확인
        for s2 in scores2:  # 해당 A의 쌍이 B에도 있는지 확인
            # if (s1[0] == s2[0] and s1[1] == s2[1]) \
            #         or (s1[0] == s2[1] and s1[1] == s2[0]):
            if set(s1) == set(s2):
                print("겹치는 쌍 : ", s1, s2)
                score_diff = abs(float(s1[2]) - float(s2[2]))

                count += 1
                score_sum += score_diff

    if count == 0:
        return 0
    else:
        avg_score = score_sum / count
        return 1 - round(avg_score, 3)


def get_ks_similarity(base_path, ks1, ks2):  # main 함수
    nodes1, edges1 = parse_js_file(base_path, ks1)
    nodes2, edges2 = parse_js_file(base_path, ks2)

    node1_set = get_unique_node(nodes1)
    node2_set = get_unique_node(nodes2)

    union_node = node1_set.union(node2_set)

    id2word1 = convert_id_to_word(nodes1)
    id2word2 = convert_id_to_word(nodes2)

    scores1 = create_score_list(edges1, id2word1)
    scores2 = create_score_list(edges2, id2word2)

    intersection_node = node1_set.intersection(node2_set)  # 공통 노드 키워드 구하기

    relation_sim = get_average_score(scores1, scores2)
    # print("relation_sim : ", relation_sim)
    node_sim = get_jaccard_similarity(union_node, intersection_node)
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


def intra_sim(base_path, keyword, index_list):
    similarity_sum = 0
    score_list = list()

    if not index_list:  # index list 비어있는 경우. 즉 선택한 기사가 없는 경우

        return score_list, 0.0

    else:
        file_pair_list = get_file_pair_list(index_list)

        for pair in file_pair_list:
            ks_similarity = get_ks_similarity(base_path, keyword + '_' + str(pair[0]), keyword + '_' + str(pair[1]))
            similarity_score = round(ks_similarity, 3)

            score_list.append([pair[0], pair[1], similarity_score])
            similarity_sum += similarity_score

        if len(file_pair_list) == 0:
            intra_avg_score = 0
        else:
            intra_avg_score = round(similarity_sum / len(file_pair_list), 3)

        return score_list, intra_avg_score


def inter_sim(base_path, keyword_A, keyword_B, index_A, index_B):
    similarity_sum = 0
    score_list = list()

    if not index_A or not index_B:  # index list 비어있는 경우. 즉 선택한 기사가 없는 경우

        return score_list, 0.0

    else:
        file_nxn_pair_list = get_nxn_file_list(index_A, index_B)

        for pair in file_nxn_pair_list:
            ks_similarity = get_ks_similarity(base_path, keyword_A + '_' + str(pair[0]), keyword_B + '_' + str(pair[1]))
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


def similarity_measure(base_path, keyword_A, index_A, keyword_B, index_B):
    A_list, A_avg = intra_sim(base_path, keyword_A, index_A)
    B_list, B_avg = intra_sim(base_path, keyword_B, index_B)
    AB_list, AB_avg = inter_sim(base_path, keyword_A, keyword_B, index_A, index_B)

    return A_list, B_list, AB_list, A_avg, B_avg, AB_avg
