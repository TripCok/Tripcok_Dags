import csv
import requests
import random
from user_API import UserAPI


def read_csv_file(csv_file_path):
    """
    CSV 파일을 읽어 데이터 행을 반환합니다.
    """
    with open(csv_file_path, mode='r', encoding='utf-8') as file:
        reader = csv.reader(file)
        next(reader)  # 헤더 건너뛰기 (필요한 경우)
        return list(reader)

def get_params(row):
    """
    데이터 행에서 필요한 값을 추출하여 request body를 생성합니다.
    """
    key1, key2 = row[0], row[1]
    body = {"email": key1, "password": key2}
    print(f"Preparing request body for row: {row}")
    return body

### 세션 요청 함수 (쿠키 자동 관리)
def send_request_to_api(url, session):
    response = session.get(url)  # 쿠키는 session이 자동 관리
    print(f"Response: {response.status_code}, {response.text}")
    return response

def login_random():
    return random.randint(5,9)


### 특정 값의 확률을 설정한 랜덤 값 반환
def place_random():
    # 특정 값 (예: 180)의 선택 확률을 80%로 설정
    return random.randint(1, 30500)  # 나머지 값은 1~179에서 랜덤

if __name__ == "__main__":

    login_csv_file = "./user_data.csv"
    login_api_url = "http://52.79.199.83:9090/api/v1/member/login"
    
    
    # 세션 객체 생성
    session = requests.Session()

    row = read_csv_file(login_csv_file)
    random_value = login_random()
    data = get_params(row[random_value])
    
    # 로그인 요청
    login_response = session.put(login_api_url, json=data)
    if login_response.status_code == 200:
        print("로그인 성공!")
    else:
        print("로그인 실패:", login_response.status_code)
        exit(1)  # 로그인 실패 시 종료

    
    random_data = place_random()
    
    # 카테고리 API URL 및 CSV 파일 경로
    place_api_url = f"http://52.79.199.83:9090/api/v1/place/{random_data}"

    # API 요청
    profile_response = send_request_to_api(place_api_url, session)
