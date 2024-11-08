import g4f

def print_available_models():
    
    # provider가 제공하는 모델 리스트 가져오기
    models = g4f.models._all_models  # 리스트를 직접 사용
    
    # 모델 출력
    for model in models:
        print(model)

if __name__ == "__main__":
    print_available_models()
