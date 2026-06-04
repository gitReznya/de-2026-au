# Таблицы варианта

## 1. Машины и hostname

| Машина | FQDN | Роль |
|---|---|---|
| ISP | `isp.au-team.irpo` | провайдерский маршрутизатор, NAT, NTP, reverse proxy |
| HQ-RTR | `hq-rtr.au-team.irpo` | маршрутизатор HQ, VLAN, NAT, GRE/OSPF |
| BR-RTR | `br-rtr.au-team.irpo` | маршрутизатор BR, NAT, GRE/OSPF |
| HQ-SRV | `hq-srv.au-team.irpo` | DNS, NFS, Web, CA, logs, monitoring |
| BR-SRV | `br-srv.au-team.irpo` | Samba DC, Docker, Ansible |
| HQ-CLI | `hq-cli.au-team.irpo` | клиентская машина HQ |
| HQ-SW | `hq-sw.au-team.irpo` | виртуальный коммутатор Open vSwitch, если нужен |

## 2. VLAN и подсети

| Назначение | VLAN | Подсеть | Маска | Шлюз | Почему так |
|---|---:|---|---|---|---|
| HQ-SRV | 120 | `192.168.100.0/27` | `255.255.255.224` | `192.168.120.1` | до 30 usable-адресов |
| HQ-CLI | 220 | `192.168.200.0/27` | `255.255.255.224` | `192.168.220.1` | не меньше 16 usable-адресов |
| MGMT | 888 | `192.168.88.0/29` | `255.255.255.248` | `192.168.88.1` | до 6 usable-адресов |
| BR-SRV | — | `192.168.30.0/28` | `255.255.255.240` | `192.168.30.1` | до 14 usable-адресов |
| GRE HQ-BR | — | `10.10.10.0/30` | `255.255.255.252` | — | 2 адреса для туннеля |
| ISP-HQ | — | `172.16.1.0/28` | `255.255.255.240` | — | WAN-сеть |
| ISP-BR | — | `172.16.2.0/28` | `255.255.255.240` | — | WAN-сеть |

> VLAN `888` нельзя напрямую превратить в сеть `192.168.888.0`, потому что октет IPv4 не может быть больше 255. Поэтому VLAN управления `888` логично маппится в `192.168.88.0/29`.

## 3. IP-адреса устройств

| Устройство | Интерфейс | IP | Gateway | DNS |
|---|---|---|---|---|
| ISP | external `enp0s3` | DHCP | DHCP | DHCP |
| ISP | to HQ `enp0s8` | `172.16.1.1/28` | — | — |
| ISP | to BR `enp0s9` | `172.16.2.1/28` | — | — |
| HQ-RTR | WAN `enp0s3` | `172.16.1.2/28` | `172.16.1.1` | `77.88.8.8` |
| HQ-RTR | VLAN120 `enp0s8.120` | `192.168.120.1/27` | — | — |
| HQ-RTR | VLAN220 `enp0s8.220` | `192.168.220.1/27` | — | — |
| HQ-RTR | VLAN888 `enp0s8.888` | `192.168.88.1/29` | — | — |
| HQ-RTR | GRE `gre1` | `10.10.10.1/30` | — | — |
| BR-RTR | WAN `enp0s3` | `172.16.2.2/28` | `172.16.2.1` | `77.88.8.8` |
| BR-RTR | LAN `enp0s8` | `192.168.30.1/28` | — | — |
| BR-RTR | GRE `gre1` | `10.10.10.2/30` | — | — |
| HQ-SRV | LAN `enp0s3` | `192.168.120.2/27` | `192.168.120.1` | `127.0.0.1`, `77.88.8.8` |
| HQ-CLI | LAN `enp0s3` | DHCP: `192.168.220.10-30` | `192.168.220.1` | `192.168.120.2` |
| BR-SRV | LAN `enp0s3` | `192.168.30.2/28` | `192.168.30.1` | `192.168.120.2` |

## 4. DNS-записи

| Имя | Тип | Адрес |
|---|---|---|
| `hq-rtr.au-team.irpo` | A/PTR | `192.168.120.1` |
| `hq-srv.au-team.irpo` | A/PTR | `192.168.120.2` |
| `hq-cli.au-team.irpo` | A/PTR | `192.168.220.10` |
| `br-rtr.au-team.irpo` | A | `192.168.30.1` |
| `br-srv.au-team.irpo` | A | `192.168.30.2` |
| `web.au-team.irpo` | A | `172.16.1.1` |
| `docker.au-team.irpo` | A | `172.16.2.1` |
| `mon.au-team.irpo` | A | `192.168.120.2` |

## 5. Учётные записи

| Где | Пользователь | UID | Пароль | Права |
|---|---|---:|---|---|
| HQ-SRV, BR-SRV | `sshuser` | `2026` | `CHANGE_ME_FROM_TASK` | sudo без пароля |
| HQ-RTR, BR-RTR | `net_admin` | — | `CHANGE_ME_FROM_TASK` | администратор |
| Samba DC | `Administrator` | — | `CHANGE_ME_FROM_TASK` | администратор домена |
| Samba DC | `hquser1..hquser5` | — | `CHANGE_ME_FROM_TASK` | группа `hq` |
| nginx Basic Auth | `WEB` | — | `CHANGE_ME_FROM_TASK` | доступ к `web.au-team.irpo` |
| monitoring | `admin` | — | `CHANGE_ME_FROM_TASK` | доступ к мониторингу |

## 6. Порты

| Сервис | Порт |
|---|---:|
| SSH на серверах | `2026/tcp` |
| HTTP web | `80/tcp` |
| HTTPS web | `443/tcp` |
| Docker testapp | `8080/tcp` |
| DNS | `53/tcp`, `53/udp` |
| NTP | `123/udp` |
| CUPS | `631/tcp` |
| rsyslog | `514/udp`, `514/tcp` |
| Monitoring | `19999/tcp` для Netdata или порт выбранного решения |
