from flask import Flask, render_template, request, redirect, session
from random import choice

app = Flask(__name__)
app.secret_key = "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"

# 사용자 계정 정보 (단순 예시)
users = {
    "202400001": "password1",
    "202400009": "password2",
    "admin": "adminpassword"
}
# 영어 값을 한글로 변환할 딕셔너리
preference_translation = {
    'sleep_pattern': {
        'early_bird': '아침형',
        'night_owl': '저녁형'
    },
    'cleanliness': {
        'clean': '청결',
        'messy': '정리 정돈이 부족'
    },
    'noise_tolerance': {
        'quiet': '조용함을 선호',
        'loud': '소음을 잘 참음'
    },
    'social_life': {
        'introvert': '내향적',
        'extrovert': '외향적'
    }
}

# 전역 변수로 사용자 선호 정보를 저장
user_data = {}  # 각 사용자의 선호 정보 저장
matches = {}    # 매칭 결과 저장

# 루트 경로 처리
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
            if username == 'admin':
                return redirect('/admin')  # 관리자는 관리 페이지로 이동
            else:
                return redirect('/preferences')  # 일반 사용자는 선호 선택 페이지로 이동
        else:
            return '로그인 실패. 다시 시도하세요.'
    return render_template('login.html')

# 로그아웃 처리
@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect('/login')

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

# 매칭 대기 페이지
@app.route('/wait_for_match')
def wait_for_match():
    return render_template('wait_for_match.html')

# 관리자가 매칭을 진행하는 페이지
@app.route('/admin', methods=['GET'])
def admin():
    if 'username' not in session or session['username'] != 'admin':
        return redirect('/login')

    # 관리자가 매칭된 결과를 확인할 수 있도록 매칭 데이터를 전달
    return render_template('admin.html', matches=matches)

# 매칭 실행
@app.route('/perform_matching', methods=['POST'])
def perform_matching():
    if 'username' not in session or session['username'] != 'admin':
        return redirect('/login')

    # 관리자를 제외한 사용자 목록 생성
    user_ids = [user for user in user_data.keys() if user != 'admin']
    
    global matches
    matches = {}

    # 성별 그룹으로 나누기
    males = [user for user in user_ids if user_data[user]['gender'] == '남']
    females = [user for user in user_ids if user_data[user]['gender'] == '여']

    # 매칭할 사용자가 2명 이상일 때만 매칭 진행
    def perform_gender_matching(user_list):
        while len(user_list) > 1:
            user1 = user_list.pop(0)
            user2 = user_list.pop(0)
            matches[user1] = {
                'id': user2,
                'preferences': user_data[user2]
            }
            matches[user2] = {
                'id': user1,
                'preferences': user_data[user1]
            }

    # 성별 별로 매칭
    perform_gender_matching(males)
    perform_gender_matching(females)

    # 매칭되지 않은 사용자 처리 (홀수일 경우)
    unmatched_users = males + females
    if len(unmatched_users) == 1:
        unmatched_user = unmatched_users.pop(0)
        matches[unmatched_user] = None

    return redirect('/admin')  # 매칭 후 관리자 페이지로 리디렉션


@app.route('/check_match_status')
def check_match_status():
    if 'username' not in session:
        return {'matching_complete': False}
    
    username = session['username']
    
    # matches 딕셔너리에서 매칭 결과를 확인
    if username in matches and matches[username]:
        return {'matching_complete': True}
    else:
        return {'matching_complete': False}


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
# Flask 애플리케이션 실행
if __name__ == '__main__':
    app.run(debug=True)
