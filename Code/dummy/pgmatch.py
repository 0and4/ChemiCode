#"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"
import os
import pandas as pd
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate

# OpenAI API 키 설정 (환경 변수로 설정)
os.environ["OPENAI_API_KEY"] = "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"  # 여기에 본인의 OpenAI API 키를 입력하세요

# 엑셀 파일을 데이터프레임으로 불러오기
file_path = 'd:/workspace/chemicode/data/subject.xlsx'
data = pd.read_excel(file_path, sheet_name='Sheet1')

# ChatGPT 모델 설정
llm = ChatOpenAI(model_name="gpt-4", openai_api_key=os.getenv("OPENAI_API_KEY"))

# 사용자 요청에 따른 데이터 필터링 함수 정의
def filter_programs(user_query):
    # 사용자가 언급한 키워드를 기반으로 데이터 필터링
    keywords = user_query.split()  # 간단한 방법으로 사용자가 입력한 문장을 단어로 분리하여 키워드로 활용
    filtered_data = data[data['Unnamed: 8'].str.contains('|'.join(keywords), case=False, na=False)]
    
    # 키워드와 일치하는 프로그램이 없을 경우 전체 데이터 반환
    if filtered_data.empty:
        filtered_data = data

    return filtered_data

# 프롬프트 템플릿 설정
prompt_template = PromptTemplate(
    input_variables=["programs"],
    template="사용자의 요청에 따라 다음의 비교과 프로그램을 추천합니다:\n{programs}\n각 프로그램의 설명을 참고하여 선택해 보세요."
)

# 프로그램 추천 및 LLM 호출 함수 정의
def recommend_program(user_query):
    # 필터링된 데이터 추출
    filtered_data = filter_programs(user_query)
    
    # 추출된 데이터를 텍스트로 변환
    program_list = ""
    for _, row in filtered_data.iterrows():
        program_list += f"{row['Unnamed: 1']}: {row['Unnamed: 8']}\n"

    # 템플릿에 필터링된 데이터 적용
    input_prompt = prompt_template.format(programs=program_list)
    
    # LLM을 사용하여 응답 생성
    response = llm(input_prompt)  # llm 객체를 호출하는 방식으로 변경
    return response, filtered_data

# 사용자 입력을 받아서 프로그램 추천 수행
if __name__ == "__main__":
    user_input = input("비교과 프로그램에 대해 원하는 내용을 입력하세요: ")
    response, programs = recommend_program(user_input)

    # 결과 출력
    print("\n추천된 프로그램:\n")
    print(response)
    print("\n세부 프로그램 목록:\n")
    print(programs)
