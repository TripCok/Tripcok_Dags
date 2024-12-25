import random
import mysql.connector
import requests
from utils.db_config import DB_CONFIG
from utils.db_utils import fetch_random_group_id
from utils.generate_ import generate, generate_group

api = 'http://tr-sv-1:9090/api/v1'

session = requests.Session()

# 회원 가입 또는 로그인에서 받아오는 Response에서 member의 id를 추출 후 고정된 memberId를 사용
memberId = None


# 로그인
def login(email=None, password=None):
    connection = None  # connection 변수를 초기화
    try:
        if not email or not password:
            # 데이터베이스 연결 시도
            connection = mysql.connector.connect(
                host=DB_CONFIG['host'],
                port=DB_CONFIG['port'],
                user=DB_CONFIG['user'],
                password=DB_CONFIG['password'],
                database=DB_CONFIG['database']
            )
            cursor = connection.cursor(dictionary=True)

            # 데이터베이스에서 랜덤으로 사용자 선택
            cursor.execute("SELECT id, email, password FROM member ORDER BY RAND() LIMIT 1")
            user = cursor.fetchone()

            # 사용자가 없으면 로그인 실패 처리
            if not user:
                print("사용자를 찾을 수 없습니다.")
                return False

            # 사용자 이메일과 비밀번호 추출
            email, password = user['email'], user['password']
            # memberId = user['id']

        # API를 통해 로그인 요청
        response = session.put(api + '/member/login', json={'email': email, 'password': password})

        if response.status_code == 200:
            print(f"로그인 성공: {email}, memberId: {response.json()['id']}")
            # return memberId
            return response.json()

        else:
            print(f"로그인 실패: {email}")
            return False
    except mysql.connector.Error as err:
        # 데이터베이스 에러 발생 시 로그 출력
        print(f"DB 에러 발생: {err}")
        return False
    finally:
        # connection이 초기화된 경우에만 닫기 시도
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

    response = session.get(api + '/member/login', params={'email': email, 'password': password})
    if not response.status_code == 200:
        return False


# 회원가입
def register():
    #  사용자 정보 생성
    data = generate()
    print(f"생성된 사용자 데이터: {data}")

    # 회원가입 API 통신
    response = session.post(api + '/member/register', json=data, headers={'Content-Type': 'application/json'})
    print(f"회원가입 응답 코드: {response.status_code}")  # 응답 상태 코드 출력
    print(f"회원가입 응답 내용: {response.text}")  # 응답 본문 출력

    # 회원가입 API 통신을 성공 할 경우
    if response.status_code == 201:
        login_success = login(data['email'], data['password'])
        return data if login_success else None
    else:
        print(f"회원가입 실패: {response.status_code}, {response.text}")


# 모임 생성
def create_group(group_data):
    print(f"생성된 모임 데이터: {group_data}")
    headers = {
        'Content-Type': 'application/json',
    }
    response = session.post(api + '/group', json=group_data, headers=headers)
    print(f"모임 생성 응답 코드: {response.status_code}")
    print(f"모임 생성 응답 내용: {response.text}")

    if response.status_code == 201:
        return response.json()
    else:
        print(f"모임 생성 실패: {response.status_code}, {response.text}")
        return None


# 모임 신청
def create_application(memberId):
    headers = {
        'Content-Type': 'application/json',
    }
    try:
        groupId = fetch_random_group_id(memberId)
        if not groupId:
            print("모임을 찾을 수 없습니다")
            return None

        application_data = {
            "memberId": memberId,
            "groupId": groupId
        }

        # 모임 신청 API 호출
        response = session.post(api + '/application', json=application_data, headers=headers)
        print(f"모임 신청 응답 코드: {response.status_code}")
        print(f"모임 신청 응답 내용: {response.text}")

        if response.status_code == 201:
            return response.text
        else:
            print("모임 신청 실패: {response.status_code}, {response.text}")
            return None

    except Exception as e:
        print(f"모임 신청 중 예외 발생: {str(e)}")
        return None


# 모임 수락
def accept_application(groupAdminId, applicationId):
    headers = {'Content-Type': 'application/json'}
    try:
        # 수락 요청 데이터
        accept_data = {
            "groupAdminId": groupAdminId,
            "applicationId": applicationId
        }
        # API 호출
        response = session.put(api + '/application', json=accept_data, headers=headers)
        print(f"모임 신청 수락 응답 코드: {response.status_code}")

        if response.status_code == 200:
            return response.text
        else:
            print("모임 신청 수락 실패: 상태 코드가 200이 아닙니다.")
            return None
    except Exception as e:
        print(f"모임 신청 수락 중 예외 발생: {str(e)}")
        return None


def run():
    print("회원가입 후 로그인 및 모임 생성 or 신청을 실행합니다.")

    # 회원가입 및 로그인
    user_data = register()
    if user_data:
        email, password = user_data['email'], user_data['password']
        print(f"회원가입한 사용자 이메일: {email}, 비밀번호: {password}")

        login_response = login(email, password)
        if login_response:
            memberId = login_response.get('id')
            print(f"로그인 성공! memberId: {memberId}")

            # 랜덤으로 시나리오 선택
            scenario = random.choice([1, 2, 3, 4, 5, 6])

            if scenario in [1,2]:
                print("시나리오 1: 로그인 후 모임 생성 후 다른 모임 가입 신청")

                # 모임 생성
                group_data = generate_group(memberId)
                print(f"생성된 모임 데이터: {group_data}")
                group_response = create_group(group_data)

                if group_response:
                    groupId = group_response.get('id')  # 생성된 모임 ID
                    print(f"모임 생성 성공! groupId: {groupId}")

                    # 모임 신청
                    application_response = create_application(memberId)
                    if application_response:
                        print("모임 신청 완료!")
                    else:
                        print("모임 신청 실패!")
                else:
                    print("모임 생성 실패로 프로세스를 중단합니다.")

            elif scenario in [3,4,5,6]:
                print("시나리오 2: 로그인 후 다른 모임 가입 신청")

                # 다른 모임 가입 신청
                application_response = create_application(memberId)
                if application_response:
                    print(f"모임 신청 완료! 응답: {application_response}")
                else:
                    print("모임 신청 실패!")
            else:
                print("로그인 실패로 프로세스를 중단합니다.")
        else:
            print("회원가입 실패로 프로세스를 중단합니다.")