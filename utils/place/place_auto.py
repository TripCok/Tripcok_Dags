import subprocess

# 실행할 Python 파일 경로
python_file = "place_API.py"

# 100번 반복 실행
for _ in range(10):
    subprocess.run(["python", python_file])
