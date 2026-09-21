# NetworkMonitor

> **NetFaultLab 실시간 모니터링 companion 프로젝트**
>
> 실제 Containerlab 상태와 Ping 결과를 확인하여 `WARNING`, `DOWN`, `RECOVERED` 이벤트를 감지합니다.

![Python](https://img.shields.io/badge/Python-3.x-blue)
![Docker](https://img.shields.io/badge/Docker-Monitoring-blue)
![Mode](https://img.shields.io/badge/Mode-Real%20Lab-brightgreen)
![Output](https://img.shields.io/badge/Output-JSON%20%7C%20Logs-lightgrey)

## 프로젝트 한눈에 보기

| 항목 | 내용 |
|---|---|
| 목적 | NetFaultLab 실시간 상태 감시 |
| 데이터 소스 | `lab_state.json` + Docker/Containerlab 직접 확인 |
| Client 검사 | Server까지 실제 Ping |
| Server 검사 | Default Gateway Ping |
| Router/Switch 검사 | Container 및 Lab-facing Interface 상태 |
| 상태 | `UP`, `WARNING`, `DOWN`, `RECOVERED` |

## 동작 예시

```text
[00:42:24] PC2       CLIENT   WARNING   | Failure 1/3
[00:42:26] PC2       CLIENT   WARNING   | Failure 2/3
[00:42:28] PC2       CLIENT   DOWN
[00:42:41] PC2       CLIENT   RECOVERED | Downtime: 13.02 seconds
```

## 목차

- [주요 기능](#주요-기능)
- [동작 구조](#동작-구조)
- [장비별 확인 방식](#장비별-확인-방식)
- [상태 판단 방식](#상태-판단-방식)
- [동적 토폴로지 갱신](#동적-토폴로지-갱신)
- [실행 방법](#실행-방법)
- [현재 한계](#현재-한계)

NetworkMonitor는 NetFaultLab과 연동되는 실시간 네트워크 모니터링 프로젝트입니다.

NetFaultLab이 생성한 현재 토폴로지를 읽고, 실제 Containerlab 환경의 컨테이너 상태, 인터페이스 상태, Ping 결과를 확인하여 장비 상태 변화를 감지합니다.

초기 버전은 랜덤 시뮬레이션 방식이었지만, 현재 버전은 실제 NetFaultLab Lab을 직접 확인하도록 변경되었습니다.

[English README](README.md)

## 주요 기능

- NetFaultLab의 `lab_state.json`에서 현재 토폴로지 읽기
- NetFaultLab 구성 변경 시 장비 목록 자동 갱신
- 사라진 장비 자동 제거
- 새로 생성된 장비 자동 추가
- 실제 Docker / Containerlab 상태 확인
- Client → Server 실제 Ping 모니터링
- Server → Gateway 실제 Ping 모니터링
- Router / Switch 인터페이스 상태 확인
- 연속 실패 횟수 기반 `WARNING`, `DOWN`
- 복구 시 `RECOVERED` 감지
- 장애 지속 시간 계산
- `logs.txt` 이벤트 로그 저장
- `status.json` 현재 상태 저장
- 평소에는 상태가 변한 장비만 출력하여 콘솔 로그 최소화

## 동작 구조

```text
NetFaultLab
    |
    | lab_state.json
    v
NetworkMonitor
    |
    +-- Docker Container 상태 확인
    +-- Client -> Server Ping
    +-- Server -> Gateway Ping
    +-- Router/Switch Interface 상태 확인
```

NetworkMonitor는 NetFaultLab에서 장애의 정답을 전달받지 않습니다.

토폴로지 정보만 읽고 실제 실행 중인 Lab을 직접 검사합니다.

## 장비별 확인 방식

### Client

현재 Server까지 실제 End-to-End Ping을 수행합니다.

이를 통해 다음 장애의 영향을 감지할 수 있습니다.

- Wrong IP
- Wrong Default Gateway
- Wrong Static Route
- Interface Down
- ACL Block

### Server

Server의 Default Gateway까지 Ping을 수행합니다.

### Router / Switch

다음을 확인합니다.

- Container 실행 여부
- 실제 Lab-facing 인터페이스의 UP/DOWN 상태

Containerlab 관리용 인터페이스인 `eth0`은 Lab 링크 검사 대상에서 제외합니다.

## 상태 판단 방식

한 번 실패했다고 바로 `DOWN`으로 처리하지 않습니다.

기본값:

```text
1회 실패 -> WARNING
2회 실패 -> WARNING
3회 실패 -> DOWN
```

기준값:

```python
down_threshold = 3
```

장애 확정 후 다시 정상 통신이 확인되면:

```text
RECOVERED
```

를 출력하고 장애 지속 시간을 계산합니다.

## 동적 토폴로지 갱신

모니터링 중에도 `lab_state.json`을 계속 다시 읽습니다.

예를 들어 NetFaultLab 구성이:

```text
R1 R2 R3 SW1 PC1 PC2 Server1
```

에서:

```text
R1 SW1 SW2 PC1 PC2 PC3 Server1
```

로 바뀌면 자동으로:

- R2/R3 모니터링 제거
- SW2/PC3 추가
- 사라진 장비의 실패 횟수 및 상태 제거
- 현재 장비만 `status.json`에 저장

하도록 구성되어 있습니다.

## 콘솔 출력

기본값:

```python
show_all_checks = False
```

상태가 변한 경우에만 출력합니다.

예시:

```text
NetworkMonitor Started
Topology: Branch Network
Devices: 8
Mode: STATE CHANGES

[00:42:10] R1        ROUTER   UP
[00:42:10] PC1       CLIENT   UP
[00:42:24] PC2       CLIENT   WARNING   | Failure 1/3
[00:42:26] PC2       CLIENT   WARNING   | Failure 2/3
[00:42:28] PC2       CLIENT   DOWN
[00:42:41] PC2       CLIENT   RECOVERED | Downtime: 13.02 seconds
```

모든 Check 결과를 보고 싶다면:

```python
show_all_checks = True
```

로 변경하면 됩니다.

## 생성 및 사용하는 파일

### `lab_state.json`

NetFaultLab이 생성하고 NetworkMonitor가 읽는 현재 Lab 구성 파일입니다.

### `status.json`

현재 실제로 존재하는 장비들의 최신 상태를 저장합니다.

예시:

```json
{
    "R1": "UP",
    "SW1": "UP",
    "PC1": "UP",
    "PC2": "DOWN",
    "Server1": "UP"
}
```

### `logs.txt`

중요 상태 변화만 기록합니다.

예시:

```text
PC2 192.168.10.11 DOWN | 00:42:28
PC2 192.168.10.11 RECOVERED | 00:42:41 | Downtime: 13.02 seconds
```

## 필요 환경

- Python 3
- Docker Engine
- 실행 중인 NetFaultLab
- `../NetFaultLab/lab_state.json`

## 실행 방법

먼저 NetFaultLab 실행:

```bash
cd ~/NetFaultLab
python3 main.py
```

다른 터미널에서 NetworkMonitor 실행:

```bash
cd ~/NetworkMonitor
python3 main.py
```

NetworkMonitor를 켜둔 상태에서 NetFaultLab에서:

```text
inject
configure
verify
```

등을 실행하면 상태 변화를 실시간으로 확인할 수 있습니다.

모니터링 종료:

```text
Ctrl + C
```

## 현재 한계

- 현재 NetFaultLab의 토폴로지 구조를 기준으로 설계되어 있습니다.
- Router/Switch 상태는 현재 Container/Interface 상태 중심이며 라우팅 프로토콜 수준의 Health Check는 아닙니다.
- Client End-to-End Ping은 현재 첫 번째 Server를 주 대상 서버로 사용합니다.
- SNMP, Streaming Telemetry, 외부 알림 연동은 아직 구현하지 않았습니다.
- 학습 및 포트폴리오용 프로젝트이며 실제 운영망 모니터링 도구를 목적으로 하지 않습니다.

## 관련 프로젝트

NetFaultLab은 네트워크를 생성하고 장애를 주입하며 사용자가 직접 복구할 수 있는 CLI를 제공합니다.

NetworkMonitor는 그 실제 Lab을 별도로 감시하여 `WARNING`, `DOWN`, `RECOVERED` 상태 변화를 확인합니다.
