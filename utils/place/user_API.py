import csv
import requests

class UserAPI:
    def __init__(self, csv_file_path, api_url):
        """
        CSV 파일 경로와 API URL을 초기화합니다.
        """
        self.csv_file_path = csv_file_path
        self.api_url = api_url

    def read_csv_file(self):
        """
        CSV 파일을 읽어 데이터 행을 반환합니다.
        """
        with open(self.csv_file_path, mode='r', encoding='utf-8') as file:
            reader = csv.reader(file)
            next(reader)  # 헤더 건너뛰기 (필요한 경우)
            return list(reader)

    def get_params(self, row):
        """
        데이터 행에서 필요한 값을 추출하여 request body를 생성합니다.
        """
        key1, key2 = row[0], int(row[1])
        body = {"email": key1, "password": key2}
        print(f"Preparing request body for row: {row}")
        return body

    def send_request_to_api(self, body):
        """
        API에 PUT 요청을 보내고 응답을 반환합니다.
        """
        response = requests.put(self.api_url, json=body)  # requestBody로 전달
        print(f"Response: {response.status_code}, {response.text}")
        return response

    def request2api(self, input_line):
        """
        특정 라인의 데이터를 사용하여 API 요청을 수행합니다.
        """
        rows = self.read_csv_file()
        body = self.get_params(rows[input_line])
        response = self.send_request_to_api(body)

        # 쿠키에서 세션 ID 추출
        session_id = response.cookies.get("SESSION")  # JSESSIONID라는 이름의 쿠키 추출
        if session_id:
            print(f"Extracted Session ID: {session_id}")
        else:
            print("Session ID not found in the response cookies.")

        print(f"결과 : {response.status_code}, {response.text}")
        return session_id
if __name__ == "__main__":
    csv_file = "./user_data.csv"
    api_url = "http://localhost:9090/api/v1/member/login"

    # 객체 생성
    api_requester = UserAPI(csv_file, api_url)

    # 특정 라인으로 API 요청
    api_requester.request2api(1)
