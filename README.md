# EEMS — Edge Energy Management System

> 집 안의 라즈베리파이(Edge AI)가 **예측 → 최적화 → 안전 실행 → 학습**을 반복하며
> 생활을 해치지 않는 범위에서 가정의 전기요금·피크·수요반응(DR) 이행을 개선하는 시스템

<p align="center"><img src="docs/proposal/images/01_concept_loop.png" width="720" alt="EEMS 핵심 동작 루프"></p>

## 📄 문서

| 문서 | 상태 |
|---|---|
| [기획서](docs/proposal/README.md) | v1.0 초안 |
| 시스템 설계서 | 예정 |
| 실험 계획서 (E1~E6) | 예정 |

## 🧱 구성 (계획)

| 계층 | 장비 | 기술 |
|---|---|---|
| 디바이스 | MCU | C++ (PlatformIO), MQTT/Serial |
| 엣지 | Raspberry Pi | Python, Mosquitto, LightGBM/ONNX, HiGHS(MPC) |
| 플랫폼 | 서버/PC | Java 21, Spring Boot 3, PostgreSQL + TimescaleDB |
| 웹 | 브라우저/모바일 | React + TypeScript (PWA) |

## 🔗 이전 프로젝트

2024년 졸업프로젝트 [SmartHome-EdgeAI-EnergyManagement](https://github.com/dal-sj/SmartHome-EdgeAI-EnergyManagement)의 리뉴얼입니다. 핵심 아이디어만 유지하고 기획·실험·구현을 새로 진행합니다.
