# ДЭ-2026 AU — полный разбор на главной странице

> Учебная методичка для подготовки к демонстрационному экзамену по 09.02.06 «Сетевое и системное администрирование».  
> Вариант адаптирован под `au-team.irpo`, адресацию `192.168.*`, VLAN `120 / 220 / 888` и GRE `10.10.10.0/30`.

![ДЭ-2026](https://img.shields.io/badge/ДЭ-2026-blue)
![Домен](https://img.shields.io/badge/domain-au--team.irpo-success)
![VLAN](https://img.shields.io/badge/VLAN-120%20%7C%20220%20%7C%20888-orange)
![Назначение](https://img.shields.io/badge/purpose-learning-lightgrey)

---

## 0. Важно перед началом

Этот репозиторий — не официальный эталон, а учебный разбор. Перед выполнением команд сверяй:

- свой вариант задания;
- имена интерфейсов;
- VLAN;
- IP-адреса;
- порт SSH;
- домен;
- пароли;
- ОС: ALT Linux, Debian, EcoRouter или другая.

В публичной версии пароль заменён на переменную:

```text
CHANGE_ME_FROM_TASK
```

В своём стенде замени её на пароль из задания.

---

# 1. Таблица машин

| Машина | Hostname / FQDN | Роль |
|---|---|---|
| ISP | `isp.au-team.irpo` | провайдерский маршрутизатор, NAT, NTP, reverse proxy |
| HQ-RTR | `hq-rtr.au-team.irpo` | маршрутизатор HQ, VLAN, NAT, GRE, OSPF, DHCP |
| BR-RTR | `br-rtr.au-team.irpo` | маршрутизатор BR, NAT, GRE, OSPF |
| HQ-SRV | `hq-srv.au-team.irpo` | DNS, Web, NFS, CA, logs, monitoring |
| BR-SRV | `br-srv.au-team.irpo` | Samba DC, Docker, Ansible |
| HQ-CLI | `hq-cli.au-team.irpo` | клиентская машина офиса HQ |
| HQ-SW | `hq-sw.au-team.irpo` | виртуальный коммутатор, если нужен Open vSwitch |

---

# 2. Таблица адресации

| Сегмент | VLAN | Подсеть | Маска | Шлюз |
|---|---:|---|---|---|
| HQ-SRV | `120` | `192.168.120.0/27` | `255.255.255.224` | `192.168.120.1` |
| HQ-CLI | `220` | `192.168.220.0/27` | `255.255.255.224` | `192.168.220.1` |
| MGMT | `888` | `192.168.88.0/29` | `255.255.255.248` | `192.168.88.1` |
| BR-SRV | — | `192.168.30.0/28` | `255.255.255.240` | `192.168.30.1` |
| GRE | — | `10.10.10.0/30` | `255.255.255.252` | `10.10.10.1 ↔ 10.10.10.2` |
| ISP-HQ | — | `172.16.1.0/28` | `255.255.255.240` | `172.16.1.1` |
| ISP-BR | — | `172.16.2.0/28` | `255.255.255.240` | `172.16.2.1` |

Почему VLAN `888` не стал `192.168.888.0`: в IPv4 октет может быть только от 0 до 255. Поэтому VLAN 888 отражён как сеть `192.168.88.0/29`.

---

# 3. IP-адреса устройств

| Устройство | Интерфейс | IP | Gateway | DNS |
|---|---|---|---|---|
| ISP | external | DHCP | DHCP | DHCP |
| ISP | to HQ | `172.16.1.1/28` | — | — |
| ISP | to BR | `172.16.2.1/28` | — | — |
| HQ-RTR | WAN | `172.16.1.2/28` | `172.16.1.1` | `77.88.8.8` |
| HQ-RTR | VLAN120 | `192.168.120.1/27` | — | — |
| HQ-RTR | VLAN220 | `192.168.220.1/27` | — | — |
| HQ-RTR | VLAN888 | `192.168.88.1/29` | — | — |
| HQ-RTR | GRE | `10.10.10.1/30` | — | — |
| BR-RTR | WAN | `172.16.2.2/28` | `172.16.2.1` | `77.88.8.8` |
| BR-RTR | LAN | `192.168.30.1/28` | — | — |
| BR-RTR | GRE | `10.10.10.2/30` | — | — |
| HQ-SRV | LAN | `192.168.120.2/27` | `192.168.120.1` | `127.0.0.1`, `77.88.8.8` |
| BR-SRV | LAN | `192.168.30.2/28` | `192.168.30.1` | `192.168.120.2` |
| HQ-CLI | LAN | DHCP | `192.168.220.1` | `192.168.120.2` |

---

# 4. Как быстро рассчитать IP, если вариант другой

Формула usable-адресов:

```text
usable = 2^(32 - prefix) - 2
```

Шпаргалка:

| Нужно адресов | Prefix | Usable |
|---:|---:|---:|
| 2 | `/30` | 2 |
| до 6 | `/29` | 6 |
| до 14 | `/28` | 14 |
| до 30 | `/27` | 30 |
| до 62 | `/26` | 62 |
| до 126 | `/25` | 126 |
| до 254 | `/24` | 254 |

Алгоритм:

1. Смотришь, сколько адресов нужно по заданию.
2. Берёшь минимальную подходящую маску.
3. Первый usable адрес отдаёшь шлюзу.
4. Следующий адрес отдаёшь серверу.
5. Для DHCP оставляешь диапазон после статических адресов.
6. Проверяешь, что подсети не пересекаются.

## Промт для расчёта IP

```text
Ты сетевой инженер. Рассчитай IPv4-адресацию для ДЭ 09.02.06.

Домен: au-team.irpo
Базовый диапазон: 192.168.0.0/16

Требования:
- HQ-SRV VLAN: <вставь VLAN>, нужно <сколько адресов>
- HQ-CLI VLAN: <вставь VLAN>, нужно <сколько адресов>
- MGMT VLAN: <вставь VLAN>, нужно <сколько адресов>
- BR-SRV: нужно <сколько адресов>
- WAN ISP-HQ: 172.16.1.0/28
- WAN ISP-BR: 172.16.2.0/28
- GRE: нужна /30 сеть

Выдай:
1. Таблицу подсетей.
2. Таблицу устройств.
3. DNS-записи.
4. DHCP range.
5. OSPF network statements.
6. Проверку пересечений.
7. Объяснение выбора масок.
```

---

# 5. Общие переменные для команд

В командах ниже используются переменные. Перед выполнением подставь свои интерфейсы.

```bash
DOMAIN="au-team.irpo"
PASS="CHANGE_ME_FROM_TASK"
SSH_PORT="2026"

# ISP
ISP_EXT_IF="enp0s3"
ISP_HQ_IF="enp0s8"
ISP_BR_IF="enp0s9"

# HQ-RTR
HQ_WAN_IF="enp0s3"
HQ_TRUNK_IF="enp0s8"

# BR-RTR
BR_WAN_IF="enp0s3"
BR_LAN_IF="enp0s8"

# Servers
SRV_IF="enp0s3"
```

Проверка интерфейсов:

```bash
ip -br link
ip -br a
```

---

# Модуль 1 — Настройка сетевой инфраструктуры

## 1.1 Hostname

На каждой машине:

```bash
hostnamectl set-hostname isp.au-team.irpo
hostnamectl set-hostname hq-rtr.au-team.irpo
hostnamectl set-hostname br-rtr.au-team.irpo
hostnamectl set-hostname hq-srv.au-team.irpo
hostnamectl set-hostname br-srv.au-team.irpo
hostnamectl set-hostname hq-cli.au-team.irpo
exec bash
```

Проверка:

```bash
hostname
hostname -f
```

---

## 1.2 ISP: адресация и NAT

Пример логики для Linux-маршрутизатора:

```bash
# Включить маршрутизацию
sysctl -w net.ipv4.ip_forward=1

# Проверить интерфейсы
ip -br a

# Пример назначения адресов
ip addr add 172.16.1.1/28 dev "$ISP_HQ_IF"
ip addr add 172.16.2.1/28 dev "$ISP_BR_IF"
ip link set "$ISP_HQ_IF" up
ip link set "$ISP_BR_IF" up

# NAT наружу
iptables -t nat -A POSTROUTING -o "$ISP_EXT_IF" -s 172.16.1.0/28 -j MASQUERADE
iptables -t nat -A POSTROUTING -o "$ISP_EXT_IF" -s 172.16.2.0/28 -j MASQUERADE
```

Проверка:

```bash
ip route
iptables -t nat -L -n -v
ping -c 3 77.88.8.8
```

---

## 1.3 HQ-RTR: VLAN 120 / 220 / 888

```bash
sysctl -w net.ipv4.ip_forward=1

ip addr add 172.16.1.2/28 dev "$HQ_WAN_IF"
ip route add default via 172.16.1.1

ip link add link "$HQ_TRUNK_IF" name "$HQ_TRUNK_IF.120" type vlan id 120
ip link add link "$HQ_TRUNK_IF" name "$HQ_TRUNK_IF.220" type vlan id 220
ip link add link "$HQ_TRUNK_IF" name "$HQ_TRUNK_IF.888" type vlan id 888

ip addr add 192.168.120.1/27 dev "$HQ_TRUNK_IF.120"
ip addr add 192.168.220.1/27 dev "$HQ_TRUNK_IF.220"
ip addr add 192.168.88.1/29 dev "$HQ_TRUNK_IF.888"

ip link set "$HQ_TRUNK_IF.120" up
ip link set "$HQ_TRUNK_IF.220" up
ip link set "$HQ_TRUNK_IF.888" up

iptables -t nat -A POSTROUTING -o "$HQ_WAN_IF" -s 192.168.120.0/27 -j MASQUERADE
iptables -t nat -A POSTROUTING -o "$HQ_WAN_IF" -s 192.168.220.0/27 -j MASQUERADE
iptables -t nat -A POSTROUTING -o "$HQ_WAN_IF" -s 192.168.88.0/29 -j MASQUERADE
```

---

## 1.4 BR-RTR: LAN и NAT

```bash
sysctl -w net.ipv4.ip_forward=1

ip addr add 172.16.2.2/28 dev "$BR_WAN_IF"
ip addr add 192.168.30.1/28 dev "$BR_LAN_IF"
ip route add default via 172.16.2.1

ip link set "$BR_WAN_IF" up
ip link set "$BR_LAN_IF" up

iptables -t nat -A POSTROUTING -o "$BR_WAN_IF" -s 192.168.30.0/28 -j MASQUERADE
```

---

## 1.5 GRE между HQ-RTR и BR-RTR

На HQ-RTR:

```bash
ip tunnel add gre1 mode gre local 172.16.1.2 remote 172.16.2.2 ttl 255
ip addr add 10.10.10.1/30 dev gre1
ip link set gre1 up
```

На BR-RTR:

```bash
ip tunnel add gre1 mode gre local 172.16.2.2 remote 172.16.1.2 ttl 255
ip addr add 10.10.10.2/30 dev gre1
ip link set gre1 up
```

Проверка:

```bash
ping -c 3 10.10.10.1
ping -c 3 10.10.10.2
ip tunnel show
```

---

## 1.6 OSPF через FRR

На HQ-RTR и BR-RTR:

```bash
apt update
apt install -y frr
sed -i 's/ospfd=no/ospfd=yes/' /etc/frr/daemons
systemctl enable --now frr
```

HQ-RTR:

```bash
vtysh
configure terminal
router ospf
 passive-interface default
 no passive-interface gre1
 network 10.10.10.0/30 area 0
 network 192.168.120.0/27 area 0
 network 192.168.220.0/27 area 0
 network 192.168.88.0/29 area 0
exit
write memory
```

BR-RTR:

```bash
vtysh
configure terminal
router ospf
 passive-interface default
 no passive-interface gre1
 network 10.10.10.0/30 area 0
 network 192.168.30.0/28 area 0
exit
write memory
```

Проверка:

```bash
vtysh -c "show ip ospf neighbor"
vtysh -c "show ip route ospf"
```

---

## 1.7 DHCP для HQ-CLI

На HQ-RTR:

```bash
apt update
apt install -y isc-dhcp-server
```

Пример `/etc/dhcp/dhcpd.conf`:

```conf
option domain-name "au-team.irpo";
option domain-name-servers 192.168.120.2;
default-lease-time 600;
max-lease-time 7200;
authoritative;

subnet 192.168.220.0 netmask 255.255.255.224 {
  range 192.168.220.10 192.168.220.30;
  option routers 192.168.220.1;
  option broadcast-address 192.168.220.31;
}
```

В `/etc/default/isc-dhcp-server`:

```conf
INTERFACESv4="enp0s8.220"
```

Запуск:

```bash
dhcpd -t -cf /etc/dhcp/dhcpd.conf
systemctl enable --now isc-dhcp-server
```

---

## 1.8 HQ-SRV: IP, SSH и DNS

```bash
ip addr add 192.168.120.2/27 dev "$SRV_IF"
ip route add default via 192.168.120.1

apt update
apt install -y openssh-server bind9 bind9-utils

useradd -m -u 2026 -s /bin/bash sshuser
passwd sshuser
usermod -aG sudo sshuser
```

SSH-настройки в `/etc/ssh/sshd_config`:

```conf
Port 2026
AllowUsers sshuser
MaxAuthTries 2
Banner /etc/ssh/banner
```

```bash
echo "Authorized access only" > /etc/ssh/banner
systemctl restart ssh
```

DNS-зона `au-team.irpo` должна содержать записи:

```text
hq-rtr  A 192.168.120.1
hq-srv  A 192.168.120.2
hq-cli  A 192.168.220.10
br-rtr  A 192.168.30.1
br-srv  A 192.168.30.2
web     A 172.16.1.1
docker  A 172.16.2.1
mon     A 192.168.120.2
```

---

## 1.9 BR-SRV: IP и SSH

```bash
ip addr add 192.168.30.2/28 dev "$SRV_IF"
ip route add default via 192.168.30.1

apt update
apt install -y openssh-server

useradd -m -u 2026 -s /bin/bash sshuser
passwd sshuser
usermod -aG sudo sshuser
```

---

## 1.10 Проверки Модуля 1

```bash
ping -c 3 192.168.120.1
ping -c 3 192.168.120.2
ping -c 3 192.168.30.2
ping -c 3 10.10.10.1
ping -c 3 10.10.10.2
ping -c 3 77.88.8.8
host hq-srv.au-team.irpo 192.168.120.2
host web.au-team.irpo 192.168.120.2
host docker.au-team.irpo 192.168.120.2
```

---

# Модуль 2 — Организация сетевого администрирования

## 2.1 Samba DC на BR-SRV

Задача: поднять домен `au-team.irpo`, создать группу `hq`, пользователей `hquser1..hquser5`, ввести HQ-CLI в домен.

Общий порядок:

```bash
apt update
apt install -y samba winbind krb5-user smbclient
hostnamectl set-hostname br-srv.au-team.irpo
```

Дальше выполняется `samba-tool domain provision` с параметрами своего варианта. После provision:

```bash
systemctl enable --now samba-ad-dc
samba-tool group add hq
```

Создание пользователей:

```bash
for i in 1 2 3 4 5; do
  samba-tool user add hquser$i "$PASS"
  samba-tool user setexpiry hquser$i --noexpiry
  samba-tool group addmembers hq hquser$i
done
```

Проверка:

```bash
samba-tool user list
samba-tool group listmembers hq
```

---

## 2.2 RAID и NFS на HQ-SRV

Перед любыми действиями с дисками:

```bash
lsblk
```

В реальном варианте проверь:

- сколько дисков;
- какой RAID нужен;
- как называются диски;
- есть ли на них данные.

После подготовки массива создаётся точка монтирования:

```bash
mkdir -p /raid/nfs
chmod 777 /raid/nfs
apt update
apt install -y nfs-kernel-server
```

`/etc/exports`:

```conf
/raid/nfs 192.168.220.0/27(rw,sync,no_subtree_check)
```

```bash
exportfs -ra
systemctl enable --now nfs-server
```

Проверка:

```bash
exportfs -v
systemctl status nfs-server
```

---

## 2.3 Chrony

На ISP:

```bash
apt update
apt install -y chrony
```

В `chrony.conf` указывается внешний источник времени и разрешаются офисные сети.

На клиентах:

```bash
apt install -y chrony
chronyc sources
```

---

## 2.4 Ansible на BR-SRV

```bash
apt update
apt install -y ansible sshpass
mkdir -p /etc/ansible
```

Пример inventory:

```ini
[linux]
hq-srv ansible_host=192.168.120.2 ansible_user=sshuser ansible_port=2026
br-srv ansible_host=192.168.30.2 ansible_user=sshuser ansible_port=2026

[routers]
hq-rtr ansible_host=172.16.1.2
br-rtr ansible_host=172.16.2.2
```

Проверка:

```bash
ansible -i /etc/ansible/inventory linux -m ping
```

---

## 2.5 Docker-приложение на BR-SRV

```bash
apt update
apt install -y docker.io docker-compose-plugin
systemctl enable --now docker
```

После подключения `Additional.iso` импортируются образы из задания и создаётся compose-файл. Проверка:

```bash
docker images
docker ps
curl http://192.168.30.2:8080
```

---

## 2.6 Web на HQ-SRV

```bash
apt update
apt install -y apache2 mariadb-server php php-mysql
systemctl enable --now apache2 mariadb
```

После подключения `Additional.iso`:

- скопировать файлы web-приложения в web-root;
- импортировать dump SQL;
- создать базу и пользователя согласно заданию;
- проверить `curl http://192.168.120.2`.

---

## 2.7 Port forwarding на маршрутизаторах

Логика:

| Где | Внешний порт | Внутренний узел |
|---|---:|---|
| HQ-RTR | 8080 | `192.168.120.2:80` |
| HQ-RTR | 2026 | `192.168.120.2:2026` |
| BR-RTR | 8080 | `192.168.30.2:8080` |
| BR-RTR | 2026 | `192.168.30.2:2026` |

После настройки проверять с ISP/HQ-CLI:

```bash
curl http://172.16.1.2:8080
curl http://172.16.2.2:8080
```

---

## 2.8 Nginx reverse proxy на ISP

```bash
apt update
apt install -y nginx apache2-utils
systemctl enable --now nginx
```

Имена:

```text
web.au-team.irpo    -> HQ-SRV web
docker.au-team.irpo -> BR-SRV docker app
```

Basic Auth для `web.au-team.irpo`:

```bash
htpasswd -c /etc/nginx/.htpasswd WEB
nginx -t
systemctl reload nginx
```

---

## 2.9 Проверки Модуля 2

```bash
curl http://web.au-team.irpo
curl http://docker.au-team.irpo
samba-tool group listmembers hq
exportfs -v
chronyc sources
ansible -i /etc/ansible/inventory all -m ping
docker ps
nginx -t
```

---

# Модуль 3 — Эксплуатация объектов сетевой инфраструктуры

## 3.1 CA и HTTPS

На HQ-SRV создаётся центр сертификации и сертификаты для:

```text
web.au-team.irpo
docker.au-team.irpo
```

Общий порядок:

1. Создать CA.
2. Создать сертификаты web/docker.
3. Перенести сертификаты на ISP.
4. Настроить nginx на HTTPS.
5. Импортировать CA на HQ-CLI.
6. Проверить, что браузер не ругается.

Проверки:

```bash
curl -I https://web.au-team.irpo
curl -I https://docker.au-team.irpo
openssl x509 -in ca.crt -noout -text
```

---

## 3.2 Защищённый туннель

Варианты:

- IPsec поверх WAN;
- GRE over IPsec;
- другой вариант, если он разрешён заданием.

Цель: после включения защиты OSPF должен снова подняться через туннель.

Проверки:

```bash
ip a show gre1
ping -c 3 10.10.10.1
ping -c 3 10.10.10.2
vtysh -c "show ip ospf neighbor"
```

---

## 3.3 Firewall на HQ-RTR и BR-RTR

Нужно разрешить только необходимые протоколы:

- HTTP;
- HTTPS;
- DNS;
- NTP;
- ICMP;
- SSH на заданный порт;
- GRE/IPsec, если используется.

Остальной входящий трафик из внешней сети во внутреннюю сеть должен быть запрещён.

Проверка:

```bash
iptables -L -n -v
iptables -t nat -L -n -v
```

---

## 3.4 CUPS на HQ-SRV

```bash
apt update
apt install -y cups printer-driver-cups-pdf
systemctl enable --now cups
```

Задачи:

- опубликовать виртуальный PDF-принтер;
- подключить его на HQ-CLI;
- сделать принтером по умолчанию;
- выполнить пробную печать.

Проверка:

```bash
lpstat -p
systemctl status cups
```

---

## 3.5 Rsyslog и logrotate

HQ-SRV — сервер логов. Клиенты:

- HQ-RTR;
- BR-RTR;
- BR-SRV.

На HQ-SRV:

```bash
apt update
apt install -y rsyslog logrotate
mkdir -p /opt/logs
systemctl enable --now rsyslog
```

Проверка:

```bash
ss -tulpen | grep 514
ls -la /opt
```

---

## 3.6 Monitoring

Можно использовать Netdata, Zabbix или другое открытое ПО.

Цель:

```text
http://mon.au-team.irpo
```

Должны отображаться:

- CPU;
- RAM;
- disk usage;
- HQ-SRV;
- BR-SRV.

Проверка:

```bash
curl http://mon.au-team.irpo
```

---

## 3.7 Fail2ban

```bash
apt update
apt install -y fail2ban
systemctl enable --now fail2ban
```

Проверка:

```bash
fail2ban-client status
fail2ban-client status sshd
```

---

## 3.8 Ansible inventory report

На BR-SRV playbook должен собрать информацию о HQ-SRV и HQ-CLI:

- hostname;
- IP-address;
- сохранить отчёты в `/etc/ansible/PC-INFO/`.

Проверка:

```bash
ls -la /etc/ansible/PC-INFO
```

---

## 3.9 Backup

Если в задании требуется резервное копирование:

- определить, что именно копировать;
- где хранить;
- чем восстанавливать;
- сделать тест восстановления.

Минимальная проверка:

```bash
ls -la /backup
```

---

## 3.10 Проверки Модуля 3

```bash
curl -I https://web.au-team.irpo
curl -I https://docker.au-team.irpo
curl http://mon.au-team.irpo
systemctl status rsyslog
systemctl status fail2ban
systemctl status cups
lpstat -p
ls -la /etc/ansible/PC-INFO
vtysh -c "show ip ospf neighbor"
```

---

# Финальная проверка всего стенда

```bash
hostname -f
ip -br a
ip route
ping -c 3 192.168.120.2
ping -c 3 192.168.30.2
ping -c 3 10.10.10.1
ping -c 3 10.10.10.2
ping -c 3 77.88.8.8
host hq-srv.au-team.irpo
host br-srv.au-team.irpo
host web.au-team.irpo
host docker.au-team.irpo
curl http://web.au-team.irpo
curl http://docker.au-team.irpo
curl -I https://web.au-team.irpo
curl -I https://docker.au-team.irpo
```

---

# Структура репозитория

```text
.
├── README.md
├── TABLES.md
├── COMMAND_INDEX.md
├── DISCLAIMER.md
├── LICENSE.md
├── LOCAL_SETUP.md
├── docs/
├── prompts/
├── scripts/
├── module-1/
├── module-2/
├── module-3/
└── appendices/
```

---

# Дополнительные файлы

- [`TABLES.md`](./TABLES.md) — таблицы адресации.
- [`COMMAND_INDEX.md`](./COMMAND_INDEX.md) — индекс команд.
- [`docs/ip-calculation.md`](./docs/ip-calculation.md) — расчёт IP.
- [`docs/workflow.md`](./docs/workflow.md) — порядок выполнения.
- [`prompts/ip-calc-prompt.md`](./prompts/ip-calc-prompt.md) — промт для расчёта IP.
- [`scripts/calc_subnets.py`](./scripts/calc_subnets.py) — проверка подсетей.
- [`DISCLAIMER.md`](./DISCLAIMER.md) — ограничения.

---

# Правовой статус

Материал предназначен для обучения. Это не официальный экзаменационный пакет и не гарантированный ответ на реальный ДЭ. Все параметры нужно сверять со своим вариантом задания.
