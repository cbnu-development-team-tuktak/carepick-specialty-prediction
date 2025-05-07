import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch.nn.functional as F
import pandas as pd
import numpy as np

# ✅ 모델 경로 설정 (Google Drive 기준)
MODEL_DIR = "/content/drive/MyDrive/kmbert_saved_model"

# ✅ 모델 및 토크나이저 불러오기
tokenizer = AutoTokenizer.from_pretrained(MODEL_DIR)
model = AutoModelForSequenceClassification.from_pretrained(MODEL_DIR)
model.eval()  # 평가 모드

# ✅ 학습 시 사용했던 LabelEncoder의 클래스 목록 (순서 중요)
label_classes = [
    '가정의학과', '감염내과', '내분비대사내과', '류마티스내과', '마취통증의학과', '비뇨의학과', '산부인과',
    '성형외과', '소아청소년과', '소화기내과', '순환기내과', '신경과', '신경외과', '신장내과', '안과',
    '영상의학과', '외과', '응급의학과', '이비인후과', '재활의학과', '정신건강의학과', '정형외과', '치과',
    '피부과', '혈액종양내과', '호흡기내과', '흉부외과'
]

# ✅ 예측 함수
def predict_department(text, top_k=3):
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True, max_length=512)
    with torch.no_grad():
        outputs = model(**inputs)
        logits = outputs.logits
        probs = F.softmax(logits, dim=1).squeeze()

    # 상위 K개 추출
    top_probs, top_indices = torch.topk(probs, k=top_k)
    top_probs = top_probs.numpy()
    top_labels = [label_classes[idx] for idx in top_indices]

    # 결과 출력
    print(f"📨 입력 문장: {text}\n")
    print("🔮 예측 결과 (Top 3):")
    for i in range(top_k):
        print(f"{i+1}. {top_labels[i]:<10} — 확률: {top_probs[i]*100:.2f}%")

    return list(zip(top_labels, top_probs))

# ✅ 예시 테스트
text = "요즘 정신이 흐릿한데 피곤한 걸까요? 뇌가 문제일까요?"
predict_department(text)
