import random
# 장비 목록
devices = ["R1", "R2", "SW1", "Server1"]

print("NetworkMonitor Started")
# 장비 상태 확인
for device in devices:
    status = random.choice(["UP", "DOWN"])
    # 정상 상태
    if status == "UP":
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
        print(device,
        ":",
        status,
        "| Latency: -"
        "| Packet Loss: 100%")
