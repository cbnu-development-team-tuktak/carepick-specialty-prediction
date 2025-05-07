import os
import json
import pandas as pd
from sklearn.preprocessing import LabelEncoder
import shutil
import numpy as np
from sklearn.metrics import classification_report, confusion_matrix
import matplotlib.pyplot as plt
import seaborn as sns

import torch
from datasets import Dataset
from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
    Trainer,
    TrainingArguments
)
from sklearn.metrics import accuracy_score, f1_score
from sklearn.metrics import top_k_accuracy_score

# ⚙️ 설정
MODEL_NAME = "madatnlp/km-bert"
TRAIN_DIR = "./drive/MyDrive/train_data"
TEST_DIR = "./drive/MyDrive/test_data"
BATCH_SIZE = 32
EPOCHS = 5

# ✅ 1. 데이터 로딩 함수
def load_data(data_dir):
    texts, labels = [], []
    for fname in os.listdir(data_dir):
        if not fname.endswith(".json"):
            continue
        with open(os.path.join(data_dir, fname), encoding="utf-8") as f:
            docs = json.load(f)
            for doc in docs:
                text = doc["title"] + " " + doc["content"]
                label = doc["department"].strip()
                texts.append(text)
                labels.append(label)
    return pd.DataFrame({"text": texts, "label": labels})

# ✅ 2. 데이터 불러오기
train_df = load_data(TRAIN_DIR)
test_df = load_data(TEST_DIR)

# ✅ 3. 라벨 인코딩
le = LabelEncoder()
train_df["label_id"] = le.fit_transform(train_df["label"])
test_df["label_id"] = le.transform(test_df["label"])
NUM_LABELS = len(le.classes_)

# ✅ 4. Dataset 변환 및 토크나이징
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)

def tokenize(example):
    return tokenizer(example["text"], truncation=True, padding="max_length", max_length=256)

train_dataset = Dataset.from_pandas(train_df[["text", "label_id"]])
test_dataset = Dataset.from_pandas(test_df[["text", "label_id"]])
train_dataset = train_dataset.map(tokenize, batched=True)
test_dataset = test_dataset.map(tokenize, batched=True)

train_dataset = train_dataset.rename_column("label_id", "labels")
test_dataset = test_dataset.rename_column("label_id", "labels")
train_dataset.set_format(type="torch", columns=["input_ids", "attention_mask", "labels"])
test_dataset.set_format(type="torch", columns=["input_ids", "attention_mask", "labels"])

# ✅ 5. 모델 로딩
model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME, num_labels=NUM_LABELS)

# ✅ 6. 평가 메트릭
def compute_metrics(p):
    preds = torch.tensor(p.predictions)
    top1_preds = torch.argmax(preds, dim=1)
    labels = torch.tensor(p.label_ids)
    top3_acc = top_k_accuracy_score(labels.numpy(), preds.numpy(), k=3)

    return {
        "accuracy": accuracy_score(labels, top1_preds),
        "f1_macro": f1_score(labels, top1_preds, average="macro"),
        "top3_accuracy": top3_acc
    }

# ✅ 7. 학습 인자
training_args = TrainingArguments(
    output_dir="./results",
    eval_strategy="epoch",
    save_strategy="steps",
    save_steps=500,
    save_total_limit=2,
    learning_rate=2e-5,
    per_device_train_batch_size=BATCH_SIZE,
    per_device_eval_batch_size=BATCH_SIZE,
    num_train_epochs=EPOCHS,
    weight_decay=0.01,
    logging_dir="./logs",
    logging_steps=100,
    disable_tqdm=False,
    load_best_model_at_end=False,
    report_to="none"
)

# ✅ 8. Trainer 생성
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=test_dataset,
    compute_metrics=compute_metrics,
    tokenizer=tokenizer
)

# ✅ 9. 학습 및 저장
if __name__ == "__main__":
    resume_path = "./results/checkpoint-6000" if os.path.exists("./results/checkpoint-6000") else None
    trainer.train(resume_from_checkpoint=resume_path)

    local_output_dir = "./trained_kmbert_model"
    trainer.save_model(local_output_dir)
    tokenizer.save_pretrained(local_output_dir)

    print("✅ 학습 완료 및 로컬 저장 완료")

    # ✅ Google Drive 저장
    drive_output_dir = "/content/drive/MyDrive/kmbert_saved_model"
    os.makedirs(drive_output_dir, exist_ok=True)

    for file_name in os.listdir(local_output_dir):
      src = os.path.join(local_output_dir, file_name)
      dst = os.path.join(drive_output_dir, file_name)
      if os.path.isfile(src):
          shutil.copy2(src, dst)  # ✅ 안전하게 복사

    print(f"✅ 모델이 Google Drive에 저장되었습니다: {drive_output_dir}")

    # ✅ 최종 성능 평가
    metrics = trainer.evaluate()
    print("\n📊 최종 성능 지표:")
    for key, value in metrics.items():
        print(f"{key:<15}: {value:.4f}")

    # ✅ 예측 결과 추출
    predictions = trainer.predict(test_dataset)
    preds = np.argmax(predictions.predictions, axis=1)
    labels = predictions.label_ids

    # ✅ 진료과별 성능 지표 출력
    print("\n📋 진료과별 성능 보고서 (classification_report):")
    print(classification_report(labels, preds, target_names=le.classes_))

    # ✅ Confusion Matrix 출력
    cm = confusion_matrix(labels, preds)
    plt.figure(figsize=(12, 10))
    sns.heatmap(cm, annot=True, fmt="d", xticklabels=le.classes_, yticklabels=le.classes_, cmap="Blues")
    plt.xlabel("Predicted Label")
    plt.ylabel("True Label")
    plt.title("Confusion Matrix")
    plt.xticks(rotation=90)
    plt.yticks(rotation=0)
    plt.tight_layout()
    plt.show()
