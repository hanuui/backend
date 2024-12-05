from flask import Flask, jsonify, request
from flask_cors import CORS
import pandas as pd
import math


app = Flask(__name__)
CORS(app)  # CORS 설정

# CSV 파일 경로
CSV_FILE_PATH = "./data/program_sports.csv"
CSV_FILE_PATH_FACILITY = "./data/facility.csv"

# NaN 값을 처리하는 함수
def remove_nan_values(facility):
    """ 데이터 내 NaN 값이 있으면 None으로 변환하는 함수 """
    for key, value in facility.items():
        if isinstance(value, float) and math.isnan(value):  # NaN 값을 확인
            facility[key] = None  # NaN을 None으로 변환
    return facility

# 데이터를 로드하는 함수
def load_filtered_program_data(region=None, time=None, days=None, target=None, sport=None, page=1, limit=20,search=None, facility=None):
    try:
        # CSV 데이터를 pandas로 읽기
        df = pd.read_csv(CSV_FILE_PATH)
        
        # 필터링 시작
        if region:
            df = df[df["CTPRVN_NM"] == region]
        
        if time:
            df = df[df[time] == True]
        
        if days:
            for day in days:
                df = df[df[day] == True]
        
        if target:
            # target 값이 해당하는 열에서 True인 데이터만 선택
            if target in ["child", "teen", "adult", "senior", "disorder"]:
                df = df[df[target] == True]
        
        if sport:
            # SPORT 열에서 선택한 스포츠만 필터링
            df = df[df["SPORT"] == sport]

        if search:
            # FCLTY_NM 및 SPORT에서 키워드 검색
            df = df[df["FCLTY_NM"].str.contains(search, na=False, case=False) |
                    df["SPORT"].str.contains(search, na=False, case=False)]
        if facility:
            # 시설명으로 필터링
            df = df[df["FCLTY_NM"] == facility]  # 정확하게 해당 시설명만 필터링
        

        # 페이지네이션 처리
        start = (page - 1) * limit
        end = start + limit
        total_count = len(df)
        paged_data = df.iloc[start:end].to_dict(orient="records")

        return paged_data, total_count
    except Exception as e:
        print(f"Error loading or filtering data: {e}")
        return [], 0

@app.route('/api/programs', methods=['GET'])
def get_programs():
    """프로그램 데이터를 반환하는 엔드포인트"""
    # 요청 파라미터 가져오기
    region = request.args.get('region', None)
    time = request.args.get('time', None)
    days = request.args.getlist('days')  # 요일은 리스트 형태로 받음
    target = request.args.get('target', None)  # 단일 값으로 받음
    sport = request.args.get('sport', None)  # SPORT 필터 추가
    page = int(request.args.get('page', 1))
    limit = int(request.args.get('limit', 20))
    search = request.args.get('search', None)  # 검색 키워드 추가
    facility= request.args.get('facility', None)  # 시설명 필터 추가


    
    # 데이터를 로드하고 필터링
    data, total_count = load_filtered_program_data(region, time, days, target, sport, page, limit, search, facility)
    
    # 응답 데이터 형식
    response = {
        'page': page,
        'limit': limit,
        'total_count': total_count,
        'total_pages': (total_count + limit - 1) // limit,  # 총 페이지 수 계산
        'data': data
    }

    return jsonify(response)

# 시설 데이터를 필터링하여 로드
def load_filtered_facility_data():
    try:
        # CSV 파일 로드
        df = pd.read_csv(CSV_FILE_PATH_FACILITY)
        
        # 필요한 컬럼만 선택 및 NaN 처리
        facilities = df[['FCLTY_NM', 'FCLTY_LA', 'FCLTY_LO', 'INDUTY_NM', 'RDNMADR_NM']].fillna("").to_dict(orient="records")
        
        # NaN 값 처리
        facilities = [remove_nan_values(facility) for facility in facilities]
        return facilities
    except Exception as e:
        print(f"Error loading CSV: {e}")
        return []

@app.route('/api/facilities', methods=['GET'])
def get_facilities():
    """시설 데이터 반환"""
    facilities = load_filtered_facility_data()  # CSV 파일에서 데이터를 읽어옴
    return jsonify({'data': facilities})  # JSON 형태로 반환



if __name__ == '__main__':
    app.run(debug=True)
