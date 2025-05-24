import matplotlib.pyplot as plt
import numpy as np
import matplotlib.font_manager as fm

# ✅ 한글 폰트 설정 (Windows: 맑은 고딕 / Mac: AppleGothic)
import platform
if platform.system() == 'Windows':
    plt.rc('font', family='Malgun Gothic')
elif platform.system() == 'Darwin':
    plt.rc('font', family='AppleGothic')
else:
    plt.rc('font', family='DejaVu Sans')  # Ubuntu or fallback

# ✅ 예시 데이터
departments = [
    '산부인과', '치과', '정형외과', '안과', '영상의학과', '비뇨의학과', '혈액종양내과', '흉부외과',
    '순환기내과', '피부과', '정신건강의학과', '마취통증의학과', '류마티스내과', '신장내과', '소아청소년과', '신경외과', '성형외과',
    '응급의학과', '호흡기내과', '이비인후과', '소화기내과', '재활의학과', '신경과', '외과', '감염내과', '내분비대사내과', '가정의학과', '내과']

v1_f1 = [0.86, 0.93, 0.47, 0.92, 0.68, 0.81, 0.60, 0.57, 0.60, 0.79, 0.78, 0.57, 0.82, 0.72, 0.65, 0.45, 0.85, 0.38, 0.72, 0.72, 0.69, 0.54, 0.54, 0.44, 0.44, 0.53, 0.06, 0]
v2_f1 = [0.85, 0, 0.52, 0.92, 0.59, 0.86, 0, 0.56, 0, 0.67, 0.70, 0.52, 0, 0, 0.27, 0.45, 0.89, 0.11, 0, 0.72, 0, 0.42, 0.47, 0.48, 0, 0, 0.08, 0.63]
v1_top3 = [0.97, 0.97, 0.95, 0.95, 0.94, 0.93, 0.91, 0.90, 0.89, 0.88, 0.87, 0.86, 0.84, 0.80, 0.77, 0.75, 0.73, 0.69, 0.69, 0.61, 0.52, 0.49, 0.42, 0.27, 0.17, 0.06, 0.01, 0]
v2_top3 = [0.95, 0, 0.90, 0.98, 1, 0.97, 0, 0.58, 0, 0.91, 0.95, 0.86, 0, 0, 0.77, 0.80, 0.96, 0.31, 0, 0.87, 0, 0.66, 0.77, 0.73, 0, 0, 0.37, 0.89]

# ✅ x 좌표 및 막대 폭 설정
x = np.arange(len(departments))
width = 0.2

# ✅ 그래프 그리기
fig, ax = plt.subplots(figsize=(20, 6))
ax.bar(x - 1.5*width, v1_f1, width, label='v1 f1-score')
ax.bar(x - 0.5*width, v2_f1, width, label='v2 f1-score')
ax.bar(x + 0.5*width, v1_top3, width, label='v1 top3_acc')
ax.bar(x + 1.5*width, v2_top3, width, label='v2 top3_acc')

# ✅ 라벨 및 범례 설정
ax.set_ylabel('Score')
ax.set_title('진료과별 성능 비교')
ax.set_xticks(x)
ax.set_xticklabels(departments, rotation=45, ha='right')
ax.legend(loc='upper right')
ax.set_ylim(0, 1.0)

plt.tight_layout()
plt.grid(axis='y', linestyle='--', alpha=0.5)
plt.show()
