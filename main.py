import random
import time
import json

# 실행 모드
simulation_mode = True

# 체크 주기
check_interval = 2

# 장비 상태 확인
# 장비 상태 확인
def check_device(device_ip):
    if simulation_mode == True:
        status = random.choice(["UP", "UP", "UP", "DOWN"])

        if status == "UP":
            latency = random.randint(1, 100)
            packet_loss = random.choice([0, 0, 0, 5, 10])

        else:
            latency = None
            packet_loss = 100

        return status, latency, packet_loss


# 장비 목록 불러오기
with open("devices.json", "r") as file:
    device_data = json.load(file)

devices = {}

devices.update(device_data["routers"])
devices.update(device_data["switches"])
devices.update(device_data["clients"])
devices.update(device_data["servers"])

# 상태 정보
failure_counts = {}
down_times = {}
down_status = {}
current_status = {}

for device in devices:
    failure_counts[device] = 0
    down_times[device] = None
    down_status[device] = False
    current_status[device] = "UNKNOWN"
print("NetworkMonitor Started")

# 모니터링 반복
for check in range(1, 6):
    print("\nCheck", check)

    for device in devices:
        device_ip = devices[device]

        status, latency, packet_loss = check_device(device_ip)

        # 정상 상태
        if status == "UP":
            if down_status[device] == True:
                recovery_time = time.time()
                downtime = recovery_time - down_times[device]
                current_status[device] = "UP"

                print(
                    device,
                    ": RECOVERED",
                    "| Downtime:",
                    round(downtime, 2),
                    "seconds"
                )

                with open("logs.txt", "a") as log_file:
                    log_file.write(
                        device + " " +
                        device_ip +
                        " RECOVERED | " +
                        time.strftime("%H:%M:%S") +
                        " | Downtime: " +
                        str(round(downtime, 2)) +
                        " seconds\n"
                    )

            down_status[device] = False
            failure_counts[device] = 0

            # 품질 경고
            if packet_loss >= 10 or latency >= 80:
                
                current_status[device] = "WARNING"

                print(
                    device,
                    device_ip,
                    ": WARNING",
                    "| Latency:",
                    latency,
                    "ms",
                    "| Packet Loss:",
                    str(packet_loss) + "%"
                )

            else:
                current_status[device] = "UP"

                print(
                    device,
                    device_ip,
                    ": UP",
                    "| Latency:",
                    latency,
                    "ms",
                    "| Packet Loss:",
                    str(packet_loss) + "%"
                )

        # 장애 상태
        else:
            failure_counts[device] += 1

            if failure_counts[device] >= 3:
                current_status[device] = "DOWN"

                if down_status[device] == False:
                    down_times[device] = time.time()

                    with open("logs.txt", "a") as log_file:
                        log_file.write(
                            device + " " +
                            device_ip +
                            " DOWN | " +
                            time.strftime("%H:%M:%S") +
                            "\n"
                        )

                down_status[device] = True

                print(
                    device,
                    ": DOWN",
                    "| Consecutive Failures:",
                    failure_counts[device]
                )

            else:

                current_status[device] = "WARNING"

                print(
                    device,
                    ": WARNING",
                    "| Consecutive Failures:",
                    failure_counts[device]
                )

    time.sleep(check_interval)

# 현재 상태 출력
print("\n=== Current Status ===")

for device in devices:
    print(
        device,
        devices[device],
        ":",
        current_status[device]
    )


# 현재 상태 저장
with open("status.json", "w") as file:
    json.dump(current_status, file, indent=4)
