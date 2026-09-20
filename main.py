import random
# 장비 목록
devices = ["R1", "R2", "SW1", "Server1"]

# 연속 실패 횟수
failure_counts = {}

for device in devices:
    failure_counts[device] = 0

print("NetworkMonitor Started")

# 모니터링 반복
for check in range(1, 6):
    print("\nCheck", check)
    # 정상 상태
    for device in devices:
        status = random.choice(["UP", "UP", "UP" "DOWN"])

        if status == "UP":
            failure_counts[device] = 0

            latency = random.randint(1, 100)
            packet_loss = random.choice([0, 0, 0, 5, 10])

            print(
                device,
                ":",
                status,
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
                print(
                    device,
                    ": DOWN",
                    "| Consecutive Failures:",
                    failure_counts[device]
                )
            
            else:
                print(
                    device,
                    ": WARNING",
                    "| Consecutive Failures:",
                    failure_counts[device]
                )