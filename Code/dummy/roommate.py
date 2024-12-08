from langchain.prompts import PromptTemplate
from langchain.chat_models import ChatOpenAI
from sklearn.neighbors import KNeighborsClassifier
import pickle
import numpy as np
import os

# OpenAI API 키를 환경 변수에서 가져오기
openai_api_key = "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"

# OpenAI 모델 초기화 (API 키를 직접 전달)
llm = ChatOpenAI(temperature=0.7, openai_api_key=openai_api_key)

# 룸메이트 매칭 질문을 위한 템플릿
template = """
당신은 룸메이트 매칭 시스템입니다. 학생이 다음 설문에 응답하면,
이를 바탕으로 최적의 룸메이트를 추천하세요.

질문:
1. 수면 패턴은 어떤가요? (아침형/저녁형)
2. 정리정돈을 얼마나 잘하나요? (깔끔/자유로움)
3. 소음에 얼마나 민감한가요? (매우 민감/거의 무관)
4. 생활 패턴은 어떤가요? (혼자 있음 선호/사교적인 시간 선호)

설문 결과:
수면 패턴: {sleep_pattern}
정리정돈 습관: {cleanliness}
소음 민감도: {noise_tolerance}
생활 패턴: {social_life}

위 설문을 기반으로 학생에게 어울리는 룸메이트를 추천해 주세요.
"""

# 템플릿과 LLM을 연결
prompt = PromptTemplate(
    input_variables=["sleep_pattern", "cleanliness", "noise_tolerance", "social_life"],
    template=template
)

# 머신러닝 모델 경로
model_path = 'knn_model.pkl'

# 기존 사용자 데이터 (임시 데이터)
existing_users = np.array([
    [0, 80, 90, 60],  # 사용자 1: 아침형, 깔끔, 매우 민감, 혼자 있음 선호
    [1, 20, 10, 40],  # 사용자 2: 저녁형, 자유로움, 거의 무관, 사교적인 시간 선호
    [0, 70, 80, 50],  # 사용자 3: 아침형, 깔끔, 보통, 혼자 있음 선호
    [1, 30, 20, 40],  # 사용자 4: 저녁형, 자유로움, 보통, 사교적인 시간 선호
])

# 레이블 (사용자 ID 또는 추천값)
user_labels = np.array([1, 2, 3, 4])  # 각각 사용자 ID

# KNN 모델 초기화
knn_model = KNeighborsClassifier(n_neighbors=2)
knn_model.fit(existing_users, user_labels)

# KNN 모델 저장
with open(model_path, 'wb') as f:
    pickle.dump(knn_model, f)

# KNN 모델을 통해 매칭 점수 계산 함수
def calculate_match_score(user_data):
    user_input = np.array([[user_data['sleep_pattern'], user_data['cleanliness'], user_data['noise_tolerance'], user_data['social_life']]])
    return knn_model.predict(user_input)[0]  # 가장 가까운 사용자 ID 반환

# 매칭된 사용자의 답변과 점수를 가져오는 함수
def get_matched_user_details(user_id):
    user_answers = {
        1: {'sleep_pattern': '아침형', 'cleanliness': '깔끔', 'noise_tolerance': '매우 민감', 'social_life': '혼자 있음 선호'},
        2: {'sleep_pattern': '저녁형', 'cleanliness': '자유로움', 'noise_tolerance': '거의 무관', 'social_life': '사교적인 시간 선호'},
        3: {'sleep_pattern': '아침형', 'cleanliness': '깔끔', 'noise_tolerance': '보통', 'social_life': '혼자 있음 선호'},
        4: {'sleep_pattern': '저녁형', 'cleanliness': '자유로움', 'noise_tolerance': '보통', 'social_life': '사교적인 시간 선호'},
    }
    return user_answers[user_id]

# LangChain과 KNN 모델을 통합하여 매칭 결과를 계산하는 대화형 흐름
def run_conversation():
    # 대화형 질문 구성
    conversation = {}

    conversation["sleep_pattern"] = input("수면 패턴은 어떤가요? (아침형/저녁형): ")
    conversation["cleanliness"] = input("정리정돈을 얼마나 잘하나요? (깔끔/자유로움): ")
    conversation["noise_tolerance"] = input("소음에 얼마나 민감한가요? (매우 민감/거의 무관): ")
    conversation["social_life"] = input("생활 패턴은 어떤가요? (혼자 있음 선호/사교적인 시간 선호): ")

    # 문자열을 수치로 변환 (KNN 모델에 맞는 형태로 처리)
    conversion_map = {
        "아침형": 0, "저녁형": 1,
        "깔끔": 80, "자유로움": 20,
        "매우 민감": 90, "거의 무관": 10,
        "혼자 있음 선호": 60, "사교적인 시간 선호": 40
    }

    user_data = {
        "sleep_pattern": conversion_map[conversation["sleep_pattern"]],
        "cleanliness": conversion_map[conversation["cleanliness"]],
        "noise_tolerance": conversion_map[conversation["noise_tolerance"]],
        "social_life": conversion_map[conversation["social_life"]]
    }

    # KNN 모델을 통한 매칭 점수 계산
    matched_user_id = calculate_match_score(user_data)
    
    # 매칭된 사용자의 세부 정보를 가져오기
    matched_user_details = get_matched_user_details(matched_user_id)
    
    # 매칭된 사용자와의 결과 출력
    print(f"당신과 매칭된 룸메이트는 이렇게 답변했습니다!")
    print(f"수면 패턴: {matched_user_details['sleep_pattern']}")
    print(f"정리정돈 습관: {matched_user_details['cleanliness']}")
    print(f"소음 민감도: {matched_user_details['noise_tolerance']}")
    print(f"생활 패턴: {matched_user_details['social_life']}")

    # LangChain을 통한 룸메이트 추천 결과 출력
    formatted_prompt = prompt.format(**conversation)

    # 형식 확인 및 출력
    print("Formatted Prompt:", formatted_prompt)  # 추가된 디버깅 정보

    # 오류 방지를 위한 조건문 추가
    #if isinstance(formatted_prompt, str) and #formatted_prompt.strip():
        #try:
        #    response = llm.generate([formatted_prompt])
        #    print("룸메이트 추천 결과:", response.generations[0][0].text)
        #except Exception as e:
        #    print(f"Error during LLM generation: {e}")
    #else:
        #print("Error: The generated prompt is not a valid string.")

# 대화 시작
run_conversation()
