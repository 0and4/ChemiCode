#"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"
import os
import pandas as pd
from flask import Flask, request, jsonify
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate

# OpenAI API 키 설정 (환경 변수로 설정)
os.environ["OPENAI_API_KEY"] ="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"  # 자신의 OpenAI API 키로 교체

app = Flask(__name__)

# 엑셀 파일을 데이터프레임으로 불러오기
file_path = 'chemicode\data\subject.xlsx'
data = pd.read_excel(file_path, sheet_name='Sheet1')

# ChatGPT 모델 설정
llm = ChatOpenAI(model_name="gpt-4", openai_api_key=os.getenv("OPENAI_API_KEY"))

# 프롬프트 템플릿 설정
prompt_template = PromptTemplate(
    input_variables=["programs"],
    template="사용자의 요청에 따라 다음의 비교과 프로그램을 추천합니다:\n{programs}\n각 프로그램의 설명을 참고하여 선택해 보세요."
)

# 사용자 요청에 따른 데이터 필터링 함수 정의
def filter_programs(user_query):
    keywords = user_query.split()  # 사용자 입력을 단어로 분리하여 키워드로 사용
    filtered_data = data[data['Unnamed: 8'].str.contains('|'.join(keywords), case=False, na=False)]
    
    if filtered_data.empty:
        filtered_data = data  # 일치하는 항목이 없을 경우 전체 데이터를 반환

    return filtered_data

@app.route('/recommend', methods=['POST'])
def recommend_program():
    user_input = request.json['query']
    
    # 데이터 필터링
    filtered_data = filter_programs(user_input)
    
    # 추출된 데이터를 텍스트로 변환
    program_list = "\n".join([f"{row['Unnamed: 1']}: {row['Unnamed: 8']}" for _, row in filtered_data.iterrows()])
    
    # 템플릿에 필터링된 데이터 적용
    input_prompt = prompt_template.format(programs=program_list)
    
    # LLM을 사용하여 응답 생성
    response = llm(input_prompt)
    
    return jsonify({"programs": response})

if __name__ == '__main__':
    app.run(debug=True)
