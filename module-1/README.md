# Модуль 1 — Настройка сетевой инфраструктуры

Цель: поднять базовую сеть, VLAN, IP-адресацию, NAT, GRE, OSPF, DHCP, DNS, SSH и время.

## Порядок

1. [`commands/01-isp.md`](./commands/01-isp.md) — ISP, WAN-сети, NAT наружу.
2. [`commands/02-hq-rtr.md`](./commands/02-hq-rtr.md) — HQ-RTR, VLAN 120/220/888, NAT, GRE, OSPF, DHCP.
3. [`commands/03-br-rtr.md`](./commands/03-br-rtr.md) — BR-RTR, LAN, NAT, GRE, OSPF.
4. [`commands/04-hq-srv.md`](./commands/04-hq-srv.md) — HQ-SRV, IP, DNS, SSH, user.
5. [`commands/05-br-srv.md`](./commands/05-br-srv.md) — BR-SRV, IP, SSH, user.
6. [`commands/06-hq-cli.md`](./commands/06-hq-cli.md) — HQ-CLI через DHCP.
7. [`commands/07-hq-sw-ovs.md`](./commands/07-hq-sw-ovs.md) — Open vSwitch, если VLAN не задаются гипервизором.
8. [`commands/checks.md`](./commands/checks.md) — проверки.

## Что должно получиться

- HQ-SRV в VLAN 120: `192.168.120.2/27`.
- HQ-CLI в VLAN 220: DHCP из `192.168.220.10-30`.
- MGMT VLAN 888: `192.168.88.0/29`.
- BR-SRV: `192.168.30.2/28`.
- Между HQ и BR работает GRE `10.10.10.1/30 <-> 10.10.10.2/30`.
- OSPF обменивает маршруты только через GRE.
- Все офисные сети выходят в интернет через NAT.
- DNS-зона `au-team.irpo` резолвит основные имена.
