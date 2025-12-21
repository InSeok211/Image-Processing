# Image Processing Studio
> **레이어 기반의 실시간 영상처리 및 화질 개선 시스템**

**Image Processing Studio**는 다양한 영상처리 알고리즘을 레이어 방식으로 적층하여 실시간으로 결과를 확인하고 조합할 수 있는 고성능 이미지 편집 소프트웨어입니다. 
단순한 단일 필터 적용에서 벗어나, 복무적인 효과를 체계적으로 관리할 수 있는 **레이어 시스템**을 핵심으로 설계되었습니다.

---

## 핵심 기능 (Core Features)

### 1. 화질 개선 및 분석 (Quality Improvement & Analysis)
* **기본 보정**: 화소값 연산을 통한 밝기(Brightness) 및 명암 대비(Contrast) 조절
* **히스토그램 처리**: 명암 분포를 확장하는 스트레칭(Stretching) 및 분포를 균일하게 재배치하는 평활화(Equalization) 기능을 제공합니다

### 2. 공간 필터링 연산 (Spatial Filtering)
* **블러링(Blurring)**: Gaussian 및 Mean 필터를 활용한 노이즈 제거 및 영상 부드럽게 처리
* **샤프닝(Sharpening)**: 언샤프 마스크(Unsharp Mask) 기법을 통한 경계선 강조
* **에지 검출(Edge Detection)**: Sobel, Canny 알고리즘을 이용한 객체 외곽선 추출
* **모폴로지(Morphology)**: 침식 및 팽창 연산을 통한 잡음 제거 및 형태학적 구조 분석

### 3. 기하학적 변환 (Geometric Transformation)
* **Scaling**: Bilinear 보간법을 적용하여 화질 저하를 최소화한 확대/축소 구현
* **Translation**: X, Y 좌표축 기반의 자유로운 영상 평행 이동
* **Rotation**: 중심점 기준 임의 각도 회전 변환

---

## 차별점: 레이어 시스템 (Layer System)
본 프로그램의 가장 큰 기술적 특징은 **레이어 적층 방식**입니다
* 여러 필터와 효과를 레이어 형태로 쌓아 올릴 수 있어, 각 효과 간의 상관관계를 실시간으로 테스트할 수 있습니다
* 예를 들어, **Brightness -> Gaussian Blur -> Sharpening** 순으로 레이어를 구성하여 복합적인 화질 개선 결과를 도출할 수 있습니다

---

## 사용자 작업 흐름 (Workflow)
사용자가 직관적으로 영상 처리를 수행할 수 있도록 4단계 프로세스를 구축하였습니다
1. **이미지 로드**: 파일을 열고 초기 히스토그램을 분석합니다
2. **효과 선택**: 좌측 패널에서 원하는 필터 및 알고리즘을 선택합니다
3. **레이어 적층**: 효과의 순서를 변경하거나 조합하여 최적의 결과를 테스트합니다
4. **결과 저장**: 처리된 영상을 최종 파일로 내보냅니다

---

## 구현 기술
* **핵심 알고리즘**: 화소 기반 연산, 공간 도메인 필터링, 기하학적 변환 알고리즘 직접 구현.
* **보간법**: 영상 확대 시 화질 유지를 위한 Bilinear Interpolation 적용

---

## 실행 화면
<img width="2168" height="1185" alt="image" src="https://github.com/user-attachments/assets/45f1e3e0-b80a-46af-9725-be3bb4a0612d" />
