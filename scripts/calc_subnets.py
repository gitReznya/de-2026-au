#!/usr/bin/env python3
import ipaddress

REQUIREMENTS = [
    ("HQ-SRV", 120, "192.168.120.0/27", "до 30 usable"),
    ("HQ-CLI", 220, "192.168.220.0/27", "не меньше 16 usable"),
    ("MGMT", 888, "192.168.88.0/29", "до 6 usable"),
    ("BR-SRV", None, "192.168.30.0/28", "до 14 usable"),
    ("GRE", None, "10.10.10.0/30", "2 адреса туннеля"),
    ("ISP-HQ", None, "172.16.1.0/28", "WAN"),
    ("ISP-BR", None, "172.16.2.0/28", "WAN"),
]

print("Расчёт подсетей ДЭ-2026\n")
print(f"{'Name':<10} {'VLAN':<6} {'Network':<18} {'Mask':<16} {'Usable':<7} {'First':<15} {'Last':<15} {'Broadcast':<15}  Note")
print("-" * 125)

nets = []
for name, vlan, cidr, note in REQUIREMENTS:
    net = ipaddress.ip_network(cidr, strict=True)
    hosts = list(net.hosts())
    first = str(hosts[0]) if hosts else "-"
    last = str(hosts[-1]) if hosts else "-"
    usable = len(hosts)
    nets.append(net)
    print(f"{name:<10} {str(vlan or '-'): <6} {str(net):<18} {str(net.netmask):<16} {usable:<7} {first:<15} {last:<15} {str(net.broadcast_address):<15}  {note}")

print("\nПроверка пересечений:")
ok = True
for i, a in enumerate(nets):
    for b in nets[i+1:]:
        if a.overlaps(b):
            print(f"ОШИБКА: {a} пересекается с {b}")
            ok = False
print("OK: пересечений нет" if ok else "Есть пересечения")
