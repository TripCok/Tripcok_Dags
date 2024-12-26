import csv
import requests
import random
import logging
from user_API import UserAPI

# 로그 설정
logging.basicConfig(
    level=logging.INFO,  # 로그 레벨 설정 (INFO 이상 레벨에서 로그 기록)
    format='%(asctime)s - %(levelname)s - %(message)s',  # 로그 포맷
    handlers=[
        logging.StreamHandler(),  # 콘솔에 로그 출력
    ]
)

def read_csv_file(csv_file_path):
    """
    CSV 파일을 읽어 데이터 행을 반환합니다.
    """
    logging.info(f"Reading CSV file: {csv_file_path}")
    with open(csv_file_path, mode='r', encoding='utf-8') as file:
        reader = csv.reader(file)
        next(reader)  # 헤더 건너뛰기 (필요한 경우)
        rows = list(reader)
        logging.info(f"Loaded {len(rows)} rows from the CSV file.")
        return rows

def get_params(row):
    """
    데이터 행에서 필요한 값을 추출하여 request body를 생성합니다.
    """
    key1, key2 = row[0], row[1]
    body = {"email": key1, "password": key2}
    logging.info(f"Preparing request body for row: {row}")
    return body

### 세션 요청 함수 (쿠키 자동 관리)
def send_request_to_api(url, session):
    logging.info(f"Sending GET request to URL: {url}")
    response = session.get(url)  # 쿠키는 session이 자동 관리
    logging.info(f"Response: {response.status_code}, {response.text[:100]}...")  # 응답의 일부만 출력
    return response

def login_random():
    random_value = random.randint(1, 150)
    logging.info(f"Generated random value for login: {random_value}")
    return random_value

### 특정 값의 확률을 설정한 랜덤 값 반환
def place_random():
    if random.random() < 0.7:
        random_value = random.randint(30, 60)
        logging.info(f"Generated random value for place (30-60): {random_value}")
    else:
        random_value = random.randint(1, 179)
        logging.info(f"Generated random value for place (1-179): {random_value}")
    return random_value

if __name__ == "__main__":
    login_csv_file = "/home/ubuntu/airflow/dags/utils/place/user_data.csv"
    login_api_url = "http://52.79.199.83:9090/api/v1/member/login"

    # 세션 객체 생성
    session = requests.Session()

    logging.info("Reading login data from CSV and preparing request parameters.")
    row = read_csv_file(login_csv_file)
    random_value = login_random()
    data = get_params(row[random_value])

    logging.info("Sending login request.")
    # 로그인 요청
    login_response = session.put(login_api_url, json=data)
    if login_response.status_code == 200:
        logging.info("로그인 성공!")
    else:
        logging.error(f"로그인 실패: {login_response.status_code}")
        exit(1)  # 로그인 실패 시 종료

    logging.info("Generating random data for place request.")
    random_data = place_random()

    place_api_url = f"http://52.79.199.83:9090/api/v1/place/{random_data}"
    
    logging.info(f"Sending request to place API with value: {random_data}")
    # API 요청
    profile_response = send_request_to_api(place_api_url, session)

    if profile_response.status_code == 200:
        logging.info("Place request was successful.")
    else:
        logging.error(f"Place request failed: {profile_response.status_code}")
