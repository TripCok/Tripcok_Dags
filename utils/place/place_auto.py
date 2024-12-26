import subprocess

def run_place_api():
    # 실행할 Python 파일 경로
    python_file = "utils/place/place_API.py"

    # 10번 반복 실행
    for _ in range(300):
        subprocess.run(["python", python_file])

