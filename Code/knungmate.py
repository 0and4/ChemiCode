from flask import Flask, render_template, request, redirect, session
from random import choice
import pandas as pd
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
import os

app = Flask(__name__)
app.secret_key = "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"
# OpenAI API 키 설정 (환경 변수로 설정)
os.environ["OPENAI_API_KEY"] = "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"  # 여기에 본인의 OpenAI API 키를 입력하세요

# 사용자 계정 정보 (단순 예시)
users = {
    "202400001": "password1",
    "202400009": "password2",
    "admin": "adminpassword"
}

# 전역 변수로 사용자 선호 정보를 저장
user_data = {}  # 각 사용자의 룸메이트 선호 정보 저장
matches = {}    # 룸메이트 매칭 결과 저장

# 비교과 프로그램 데이터 불러오기
file_path = 'chemicode/ChemiCode/Code/data/subject.xlsx'
data = pd.read_excel(file_path, sheet_name='Sheet1')

# ChatGPT 모델 설정
llm = ChatOpenAI(model_name="gpt-4", openai_api_key=os.getenv("OPENAI_API_KEY"))

# 메인 페이지 처리
@app.route('/')
def home():
    return redirect('/login')

# 로그인 처리
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # 사용자 인증
        if username in users and users[username] == password:
            session['username'] = username
            return redirect('/menu')  # 로그인 후 메인 메뉴로 이동
        else:
            return '로그인 실패. 다시 시도하세요.'
    return render_template('login.html')

# 메인 메뉴 (서비스 선택 화면)
@app.route('/menu')
def menu():
    if 'username' not in session:
        return redirect('/login')
    return render_template('menu.html')

# 로그아웃 처리
@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect('/login')

### 룸메이트 매칭 서비스 ###
# 룸메이트 선호 선택 페이지
@app.route('/preferences', methods=['GET', 'POST'])
def preferences():
    if 'username' not in session:
        return redirect('/login')

    if request.method == 'POST':
        username = session['username']

        # 사용자가 선택한 선호 데이터를 저장
        user_data[username] = {
            'gender': request.form['gender'],
            'smoking': request.form['smoking'],
            'bedtime': request.form['bedtime'],
            'lifestyle': request.form['lifestyle'],
            'noise_sensitivity': request.form['noise_sensitivity'],
            'relationship': request.form['relationship'],
            'cleanliness': request.form['cleanliness'],
            'late_snack': request.form['late_snack']
        }

        print(f"저장된 사용자 데이터: {user_data}")
        return redirect('/wait_for_match')

    return render_template('preferences.html')
# 매칭 로직 함수 정의 (사용자를 임의로 매칭)
def auto_match(username):
    global matches

    # 이미 매칭된 사용자가 있다면 패스
    if username in matches:
        return

    # 모든 사용자의 목록에서 현재 사용자를 제외한 사람을 무작위로 선택
    available_users = [user for user in user_data.keys() if user != username and user not in matches]
    
    if available_users:
        # 무작위로 룸메이트 선택
        roommate = choice(available_users)
        matches[username] = {'id': roommate, 'preferences': user_data[roommate]}
        matches[roommate] = {'id': username, 'preferences': user_data[username]}
        print(f"매칭 완료: {username} ↔ {roommate}")
    else:
        matches[username] = {'id': username, 'preferences': None}  # 매칭되지 않음

# wait_for_match 페이지에서 매칭 실행
@app.route('/wait_for_match')
def wait_for_match():
    if 'username' not in session:
        return redirect('/login')

    username = session['username']
    
    # 자동 매칭 실행
    auto_match(username)
    
    return render_template('wait_for_match.html')

# 매칭 결과 페이지
@app.route('/match_result')
def match_result():
    if 'username' not in session:
        return redirect('/login')

    username = session['username']

    # 임의로 202400002 사용자와 매칭된 것처럼 표시
    roommate = "202400002"
    roommate_preferences = {
        'gender': '남성',
        'smoking': '비흡연',
        'bedtime': '밤 11시 이전',
        'lifestyle': '아침형 인간',
        'noise_sensitivity': '중간',
        'relationship': '친한 친구',
        'cleanliness': '깔끔함',
        'late_snack': '드물게'
    }

    return render_template('match_result.html', roommate=roommate, preferences=roommate_preferences)

    """
@app.route('/match_result')
def match_result():
    if 'username' not in session:
        return redirect('/login')

    username = session['username']
    global matches

    # 사용자가 매칭된 룸메이트 정보를 확인
    if username in matches:
        match_info = matches[username]
        if match_info and match_info['id'] != username:
            roommate = match_info['id']
            roommate_preferences = match_info['preferences']
            
            # 매칭된 사용자의 선호도 정보를 템플릿에 전달
            return render_template('match_result.html', roommate=roommate, preferences=roommate_preferences)
        else:
            return "매칭된 룸메이트가 없습니다."
    else:
        return "매칭된 룸메이트가 없습니다."
    """
### 비교과 프로그램 매칭 서비스 ###
# 프로그램 추천 페이지
@app.route('/programs', methods=['GET', 'POST'])
def programs():
    if 'username' not in session:
        return redirect('/login')

    response = ""
    filtered_data = None  # 초기화

    if request.method == 'POST':
        user_query = request.form['query']
        response, filtered_data = recommend_program(user_query)

    return render_template('pgmatch.html', response=response, programs=filtered_data)

# 프로그램 추천 및 LLM 호출 함수 정의
def recommend_program(user_query):
    # 사용자 요청에 따른 데이터 필터링
    filtered_data = filter_programs(user_query)

    # 필터링된 데이터가 없는 경우 예외 처리
    if filtered_data.empty:
        return "추천된 프로그램이 없습니다.", filtered_data  # 빈 데이터프레임을 반환

    # 필터링된 데이터 추출
    program_list = ""
    for _, row in filtered_data.iterrows():
        program_list += f"{row['Unnamed: 1']}: {row['Unnamed: 8']}\n"

    # 프롬프트 템플릿 설정 및 응답 생성
    prompt_template = PromptTemplate(
        input_variables=["programs"],
        template="사용자의 요청에 따라 다음의 비교과 프로그램을 추천합니다:\n{programs}\n각 프로그램의 설명을 참고하여 선택해 보세요."
    )
    input_prompt = prompt_template.format(programs=program_list)
    response = llm(input_prompt)
    return response, filtered_data


# 데이터 필터링 함수
def filter_programs(user_query):
    keywords = user_query.split()
    # 사용자 쿼리에 따라 데이터 필터링
    filtered_data = data[data['Unnamed: 8'].str.contains('|'.join(keywords), case=False, na=False)]

    # 필터링된 데이터가 비어있을 경우 None 반환
    if filtered_data.empty:
        return None

    return filtered_data

# Flask 애플리케이션 실행
if __name__ == '__main__':
    app.run(debug=True)
