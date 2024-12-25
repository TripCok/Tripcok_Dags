import random
import mysql.connector
import requests
from utils.db_utils import fetch_random_group_id
from utils.generate_ import generate, generate_group
from faker import Faker


class AutoWorkByGroup:
    def __init__(self, **kwargs):
        self.server_host = kwargs.get('server_host', 'localhost')
        self.server_port = kwargs.get('server_port', '8000')
        self.db_host = kwargs.get('db_host', 'localhost')
        self.db_port = kwargs.get('db_port', 3306)
        self.db_user = kwargs.get('db_user', 'root')
        self.db_password = kwargs.get('db_password', '')
        self.db_database = kwargs.get('db_database', 'test')
        self.api = f'http://{self.server_host}:{self.server_port}/api/v1'
        self.session = requests.Session()
        self.fake = Faker('ko_KR')
        self.member_id = None

    def _get_db_connection(self):
        return mysql.connector.connect(
            host=self.db_host,
            port=self.db_port,
            user=self.db_user,
            password=self.db_password,
            database=self.db_database
        )

    # 로그인
    def login(self, email=None, password=None):
        connection = None
        try:
            if not email or not password:
                connection = self._get_db_connection()
                cursor = connection.cursor(dictionary=True)
                cursor.execute("SELECT id, email, password FROM member ORDER BY RAND() LIMIT 1")
                user = cursor.fetchone()

                if not user:
                    print("사용자를 찾을 수 없습니다.")
                    return False

                email, password = user['email'], user['password']

            response = self.session.put(f"{self.api}/member/login", json={'email': email, 'password': password})

            if response.status_code == 200:
                self.member_id = response.json()['id']
                print(f"로그인 성공: {email}, memberId: {self.member_id}")
                return response.json()
            else:
                print(f"로그인 실패: {email}")
                return False

        except mysql.connector.Error as err:
            print(f"DB 에러 발생: {err}")
            return False
        finally:
            if connection and connection.is_connected():
                cursor.close()
                connection.close()

    # 회원가입
    def register(self):
        data = generate()
        print(f"생성된 사용자 데이터: {data}")

        response = self.session.post(f"{self.api}/member/register", json=data,
                                     headers={'Content-Type': 'application/json'})
        print(f"회원가입 응답 코드: {response.status_code}")
        print(f"회원가입 응답 내용: {response.text}")

        if response.status_code == 201:
            login_success = self.login(data['email'], data['password'])
            return data if login_success else None
        else:
            print(f"회원가입 실패: {response.status_code}, {response.text}")

    # 모임 생성
    def create_group(self, group_data):
        print(f"생성된 모임 데이터: {group_data}")
        headers = {'Content-Type': 'application/json'}
        response = self.session.post(f"{self.api}/group", json=group_data, headers=headers)
        print(f"모임 생성 응답 코드: {response.status_code}")
        print(f"모임 생성 응답 내용: {response.text}")

        if response.status_code == 201:
            return response.json()
        else:
            print(f"모임 생성 실패: {response.status_code}, {response.text}")
            return None

    # 모임 신청
    def create_application(self):
        headers = {'Content-Type': 'application/json'}
        try:
            group_id = fetch_random_group_id(self.member_id)
            if not group_id:
                print("모임을 찾을 수 없습니다")
                return None

            application_data = {
                "memberId": self.member_id,
                "groupId": group_id
            }

            response = self.session.post(f"{self.api}/application", json=application_data, headers=headers)
            print(f"모임 신청 응답 코드: {response.status_code}")
            print(f"모임 신청 응답 내용: {response.text}")

            if response.status_code == 201:
                return response.text
            else:
                print(f"모임 신청 실패: {response.status_code}, {response.text}")
                return None

        except Exception as e:
            print(f"모임 신청 중 예외 발생: {str(e)}")
            return None

    def run(self):
        print("회원가입 후 로그인 및 모임 생성 or 신청을 실행합니다.")

        # 회원가입 및 로그인
        user_data = self.register()
        if user_data:
            email, password = user_data['email'], user_data['password']
            print(f"회원가입한 사용자 이메일: {email}, 비밀번호: {password}")

            login_response = self.login(email, password)
            if login_response:
                self.member_id = login_response.get('id')
                print(f"로그인 성공! memberId: {self.member_id}")

                # 랜덤으로 시나리오 선택
                scenario = random.choice([1, 2, 3, 4])

                if scenario in [1, 2]:
                    print("시나리오 1: 로그인 후 모임 생성 후 다른 모임 가입 신청")

                    # 모임 생성
                    group_data = generate_group(self.member_id)
                    print(f"생성된 모임 데이터: {group_data}")
                    group_response = self.create_group(group_data)

                    if group_response:
                        group_id = group_response.get('id')  # 생성된 모임 ID
                        print(f"모임 생성 성공! groupId: {group_id}")

                        # 모임 신청
                        application_response = self.create_application()
                        if application_response:
                            print("모임 신청 완료!")
                        else:
                            print("모임 신청 실패!")
                    else:
                        print("모임 생성 실패로 프로세스를 중단합니다.")

                elif scenario in [3, 4]:
                    print("시나리오 2: 로그인 후 다른 모임 가입 신청")

                    # 다른 모임 가입 신청
                    application_response = self.create_application()
                    if application_response:
                        print(f"모임 신청 완료! 응답: {application_response}")
                    else:
                        print("모임 신청 실패!")
            else:
                print("로그인 실패로 프로세스를 중단합니다.")
        else:
            print("회원가입 실패로 프로세스를 중단합니다.")
