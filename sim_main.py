"""
similarity_measure 함수 Use Example

input:

- keyword_A = "코로나"
- index_A = [0,1,2,3,4,5,6,7,8,9]
- keyword_B = "바이오"
- index_B = [0,1,2,3,4,5,6,7,8,9]

output:

A_list, B_list, AB_list, A_avg, B_avg, AB_avg

"""

from similarity_measure import calc_similarity
base_path = "C:/Users/kirc/Desktop/Soyoung/KIRC/지식구조 프로그램/knowledge_structure_kirc-master/results/result_webgraph/data/"

keyword1 = "코로나"
index1 = [0,1,2,3]  # 유저가 선택한 코로나 기사들 index
keyword2 = "한파"
index2 = [0,1,2,3]  # 유저가 선택한 바이오 기사들 index

intra_list1, intra_list2, inter_list, intra_average1, intra_average2, inter_average = calc_similarity(base_path, keyword1, index1, keyword2, index2)
print("A_avg : ", intra_average1)
print("B_avg : ", intra_average2)
print("AB_avg : ", inter_average)

# print("A_list : ", intra_list1)
# print("B_list : ", intra_list2)
# print("AB_list : ", inter_list)
