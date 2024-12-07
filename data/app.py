from flask import Flask, request, jsonify
from flask_cors import CORS  # CORS 추가
import pandas as pd

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}})

data = pd.read_csv('virtual_data.csv')
sports_no_disability = ['검도', '골프', '농구', '롤러인라인', '댄스(줌바 등)', '배구', '배드민턴', '볼링', '야구', '합기도', '복싱', '무용(발레 등)', '요가', '필라테스', '줄넘기', '크로스핏', '빙상(스케이트)', '주짓수', '클라이밍(암벽등반)', '당구', '수영', '스쿼시', '에어로빅', '유도', '축구(풋살)', '탁구', '태권도', '테니스', '헬스', '종합체육시설', '승마', '펜싱']
sports_with_disability = ['수영', '농구', '배구', '필라테스', '배드민턴']

male_preferences = [
    '축구(풋살)', '야구', '농구', '태권도', '합기도', '주짓수', '유도', '복싱', '검도', '당구',
    '클라이밍(암벽등반)', '헬스', '크로스핏', '골프', '볼링', '배구', '배드민턴', '탁구', '테니스',
    '펜싱', '승마', '수영', '롤러인라인', '빙상(스케이트)', '스쿼시', '종합체육시설', '에어로빅',
    '요가', '필라테스', '댄스(줌바 등)', '무용(발레 등)', '줄넘기'
]

female_preferences = [
    '요가', '필라테스', '댄스(줌바 등)', '무용(발레 등)', '에어로빅', '줄넘기', '헬스', '수영',
    '배드민턴', '배구', '테니스', '크로스핏', '빙상(스케이트)', '롤러인라인', '스쿼시',
    '클라이밍(암벽등반)', '탁구', '골프', '승마', '종합체육시설', '펜싱', '검도', '태권도',
    '합기도', '주짓수', '유도', '볼링', '농구', '축구(풋살)', '야구', '복싱', '당구'
]

sex_weights = {
    '남자': {sport: 32 - rank for rank, sport in enumerate(male_preferences)},
    '여자': {sport: 32 - rank for rank, sport in enumerate(female_preferences)}
}

mbti_weights = {
    'ISTJ': ['골프', '볼링', '탁구', '당구', '배드민턴'],
    'ISFJ': ['요가', '필라테스', '수영', '배구', '배드민턴'],
    'INFJ': ['요가', '수영', '무용(발레 등)', '댄스(줌바 등)', '필라테스'],
    'INTJ': ['클라이밍(암벽등반)', '검도', '크로스핏', '헬스', '주짓수'],
    'ISTP': ['당구', '골프', '탁구', '검도', '합기도'],
    'ISFP': ['요가', '댄스(줌바 등)', '필라테스', '에어로빅', '배드민턴'],
    'INFP': ['무용(발레 등)', '요가', '수영', '줄넘기', '댄스(줌바 등)'],
    'INTP': ['클라이밍(암벽등반)', '골프', '크로스핏', '검도', '볼링'],
    'ESTP': ['축구(풋살)', '농구', '야구', '태권도', '헬스'],
    'ESFP': ['댄스(줌바 등)', '에어로빅', '배드민턴', '필라테스', '수영'],
    'ENFP': ['무용(발레 등)', '요가', '수영', '댄스(줌바 등)', '줄넘기'],
    'ENTP': ['클라이밍(암벽등반)', '크로스핏', '골프', '검도', '합기도'],
    'ESTJ': ['축구(풋살)', '야구', '농구', '태권도', '헬스'],
    'ESFJ': ['배구', '배드민턴', '수영', '필라테스', '댄스(줌바 등)'],
    'ENFJ': ['요가', '수영', '무용(발레 등)', '댄스(줌바 등)', '에어로빅'],
    'ENTJ': ['클라이밍(암벽등반)', '크로스핏', '헬스', '검도', '주짓수']
}

def set_age_weights(age):
    if age < 20:
        return ['축구(풋살)', '농구', '야구', '배드민턴', '롤러인라인']
    elif 20 <= age < 30:
        return ['헬스', '크로스핏', '수영', '요가', '필라테스']
    elif 30 <= age < 40:
        return ['골프', '테니스', '배구', '탁구', '클라이밍(암벽등반)']
    elif 40 <= age < 50:
        return ['골프', '당구', '승마', '검도', '에어로빅']
    else:
        return ['요가', '필라테스', '걷기', '수영', '탁구']

def recommend_sport(user):
    disability = user.get('disability', '무')
    sex = user['sex']
    if sex == '여':
        sex = '여자'
    elif sex == '남':
        sex = '남자'
    mbti = user['mbti'].upper()
    age = user['age']

    if disability == '유':
        available_sports = sports_with_disability
    else:
        available_sports = sports_no_disability

    sex_pref = sorted(available_sports, key=lambda x: sex_weights[sex].get(x, 0), reverse=True)
    mbti_pref = mbti_weights.get(mbti, [])
    age_pref = set_age_weights(age)

    recommendations = list(dict.fromkeys(
        [sport for sport in sex_pref if sport in available_sports] +
        [sport for sport in mbti_pref if sport in available_sports] +
        [sport for sport in age_pref if sport in available_sports]
    ))

    return recommendations[:5]

@app.route('/recommend', methods=['POST'])
def recommend():
    user = request.get_json()
    recommended_sports = recommend_sport(user)
    return jsonify({'recommended_sports': recommended_sports})

if __name__ == '__main__':
    app.run(debug=True)
