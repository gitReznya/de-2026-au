wget -O 1.txt "https://raw.githubusercontent.com/0902066/111/main/1.txt"

![ДЭ-2026](https://img.shields.io/badge/ДЭ-2026-blue)
![Домен](https://img.shields.io/badge/domain-au--team.irpo-success)
![VLAN](https://img.shields.io/badge/VLAN-120%20%7C%20220%20%7C%20888-orange)
![Назначение](https://img.shields.io/badge/purpose-learning-lightgrey)



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

| Устройство | Интерфейс / логический интерфейс | IP | Gateway | DNS |
|---|---|---|---|---|
| ISP | external | DHCP | DHCP | DHCP |
| ISP | to HQ | `172.16.1.1/28` | — | — |
| ISP | to BR | `172.16.2.1/28` | — | — |
| HQ-RTR | ISP/WAN | `172.16.1.2/28` | `172.16.1.1` | `77.88.8.8` |
| HQ-RTR | VLAN120 | `192.168.120.1/27` | — | — |
| HQ-RTR | VLAN220 | `192.168.220.1/27` | — | — |
| HQ-RTR | VLAN888 | `192.168.88.1/29` | — | — |
| HQ-RTR | tunnel.1 / gre1 | `10.10.10.1/30` | — | — |
| BR-RTR | ISP/WAN | `172.16.2.2/28` | `172.16.2.1` | `77.88.8.8` |
| BR-RTR | LOCAL | `192.168.30.1/28` | — | — |
| BR-RTR | tunnel.1 / gre1 | `10.10.10.2/30` | — | — |
| HQ-SRV | LAN | `192.168.120.2/27` | `192.168.120.1` | `127.0.0.1`, `77.88.8.8` |
| BR-SRV | LAN | `192.168.30.2/28` | `192.168.30.1` | `192.168.120.2` |
| HQ-CLI | LAN | DHCP | `192.168.220.1` | `192.168.120.2` |

---

| Нужно адресов | Prefix | Usable |
|---:|---:|---:|
| 2 | `/30` | 2 |
| до 6 | `/29` | 6 |
| до 14 | `/28` | 14 |
| до 30 | `/27` | 30 |
| до 62 | `/26` | 62 |
| до 126 | `/25` | 126 |
| до 254 | `/24` | 254 |

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

На Linux/ALT:

```bash
ip -br link
ip -br a
```

На EcoRouter:

```text
show port brief
show ip interface brief
show running-config
```


# Модуль 1 

---

## 1.1 Hostname и домен

### Linux / ALT

На каждой машине выполняется только своя строка:

```bash
hostnamectl set-hostname isp.au-team.irpo; exec bash
hostnamectl set-hostname hq-srv.au-team.irpo; exec bash
hostnamectl set-hostname br-srv.au-team.irpo; exec bash
hostnamectl set-hostname hq-cli.au-team.irpo; exec bash
```

Проверка:

```bash
hostname
hostname -f
```

### EcoRouter HQ-RTR

```text
enable
configure terminal
hostname hq-rtr
ip domain-name au-team.irpo
write memory
```

### EcoRouter BR-RTR

```text
enable
configure terminal
hostname br-rtr
ip domain-name au-team.irpo
write memory
```

Проверка:

```text
show hostname
show running-config | include domain-name
```

---

## 1.2 ISP на Linux/ALT: три интерфейса и NAT

ISP обычно имеет:

| Интерфейс | Роль | Адрес |
|---|---|---|
| external | интернет от гипервизора / DHCP | DHCP |
| to HQ-RTR | сеть `172.16.1.0/28` | `172.16.1.1/28` |
| to BR-RTR | сеть `172.16.2.0/28` | `172.16.2.1/28` |

Пример через `/etc/net/ifaces` для ALT.

### Внешний интерфейс ISP по DHCP

```bash
mkdir -p /etc/net/ifaces/enp0s3
cat > /etc/net/ifaces/enp0s3/options << 'EOF'
TYPE=eth
CONFIG_IPV4=yes
BOOTPROTO=dhcp
SYSTEMD_BOOTPROTO=dhcp4
DISABLED=no
NM_CONTROLLED=no
SYSTEMD_CONTROLLED=no
EOF
```

### Интерфейс ISP в сторону HQ-RTR

```bash
mkdir -p /etc/net/ifaces/enp0s8
cat > /etc/net/ifaces/enp0s8/options << 'EOF'
TYPE=eth
CONFIG_IPV4=yes
BOOTPROTO=static
SYSTEMD_BOOTPROTO=static
DISABLED=no
NM_CONTROLLED=no
SYSTEMD_CONTROLLED=no
EOF

echo '172.16.1.1/28' > /etc/net/ifaces/enp0s8/ipv4address
```

### Интерфейс ISP в сторону BR-RTR

```bash
mkdir -p /etc/net/ifaces/enp0s9
cat > /etc/net/ifaces/enp0s9/options << 'EOF'
TYPE=eth
CONFIG_IPV4=yes
BOOTPROTO=static
SYSTEMD_BOOTPROTO=static
DISABLED=no
NM_CONTROLLED=no
SYSTEMD_CONTROLLED=no
EOF

echo '172.16.2.1/28' > /etc/net/ifaces/enp0s9/ipv4address
```

### Включить маршрутизацию на ISP

```bash
sed -i 's/^net.ipv4.ip_forward.*/net.ipv4.ip_forward = 1/' /etc/net/sysctl.conf || echo 'net.ipv4.ip_forward = 1' >> /etc/net/sysctl.conf
systemctl restart network
sysctl net.ipv4.ip_forward
```

### NAT на ISP

```bash
systemctl enable --now iptables
iptables -t nat -A POSTROUTING -s 172.16.1.0/28 -o enp0s3 -j MASQUERADE
iptables -t nat -A POSTROUTING -s 172.16.2.0/28 -o enp0s3 -j MASQUERADE
iptables-save > /etc/sysconfig/iptables
```

Проверка:

```bash
ip -br a
ip route
iptables -t nat -L -n -v
systemctl status iptables
ping -c 3 77.88.8.8
```

---

## 1.3 HQ-RTR на EcoRouter: WAN-порт ge0 в сторону ISP

Сначала создаём IP-интерфейс `ISP`, потом подключаем его к физическому порту `ge0` через untagged service-instance.

```text
enable
configure terminal
ip route 0.0.0.0/0 172.16.1.1

interface ISP
 description Connect-to-ISP
 ip address 172.16.1.2/28
 exit

port ge0
 service-instance ge0/ISP
  encapsulation untagged
  connect ip interface ISP
  exit
 exit

write memory
```

Проверка:

```text
show port brief
show ip interface brief
show ip route
ping 172.16.1.1
```

---

## 1.4 HQ-RTR на EcoRouter: VLAN 120 / 220 / 888 на trunk-порту ge1

На HQ-RTR нужно реализовать маршрутизацию нескольких VLAN через один порт. В типовом задании это называется «router-on-a-stick»: один физический порт несёт tagged VLAN-трафик.

### Создать IP-интерфейсы VLAN

```text
configure terminal

interface VLAN120
 description HQ-SRV
 ip address 192.168.120.1/27
 exit

interface VLAN220
 description HQ-CLI
 ip address 192.168.220.1/27
 exit

interface VLAN888
 description MGMT
 ip address 192.168.88.1/29
 exit
```

### Подключить VLAN к порту ge1

```text
port ge1
 service-instance ge1/VLAN120
  encapsulation dot1q 120 exact
  rewrite pop 1
  connect ip interface VLAN120
  exit

 service-instance ge1/VLAN220
  encapsulation dot1q 220 exact
  rewrite pop 1
  connect ip interface VLAN220
  exit

 service-instance ge1/VLAN888
  encapsulation dot1q 888 exact
  rewrite pop 1
  connect ip interface VLAN888
  exit
 exit

write memory
```

Проверка:

```text
show port brief
show ip interface brief
show running-config | include VLAN120
show running-config | include dot1q
```

---

## 1.5 BR-RTR на EcoRouter: WAN ge0 и LOCAL ge1

```text
enable
configure terminal
ip route 0.0.0.0/0 172.16.2.1

interface ISP
 description Connect-to-ISP
 ip address 172.16.2.2/28
 exit

port ge0
 service-instance ge0/ISP
  encapsulation untagged
  connect ip interface ISP
  exit
 exit

interface LOCAL
 description BR-SRV-LAN
 ip address 192.168.30.1/28
 exit

port ge1
 service-instance ge1/LOCAL
  encapsulation untagged
  connect ip interface LOCAL
  exit
 exit

write memory
```

Проверка:

```text
show port brief
show ip interface brief
show ip route
ping 172.16.2.1
```

---

## 1.6 HQ-SRV на ALT: статический IP через `/etc/net/ifaces`

```bash
mkdir -p /etc/net/ifaces/enp0s3
cat > /etc/net/ifaces/enp0s3/options << 'EOF'
TYPE=eth
DISABLED=no
BOOTPROTO=static
SYSTEMD_BOOTPROTO=static
CONFIG_IPV4=yes
SYSTEMD_CONTROLLED=no
NM_CONTROLLED=no
EOF

echo '192.168.120.2/27' > /etc/net/ifaces/enp0s3/ipv4address
echo 'default via 192.168.120.1' > /etc/net/ifaces/enp0s3/ipv4route
echo 'nameserver 77.88.8.8' > /etc/net/ifaces/enp0s3/resolv.conf
systemctl restart network
```

Проверка:

```bash
ip -br a
ip route
cat /etc/resolv.conf
ping -c 3 192.168.120.1
```

---

## 1.7 BR-SRV на ALT: статический IP через `/etc/net/ifaces`

```bash
mkdir -p /etc/net/ifaces/enp0s3
cat > /etc/net/ifaces/enp0s3/options << 'EOF'
TYPE=eth
DISABLED=no
BOOTPROTO=static
SYSTEMD_BOOTPROTO=static
CONFIG_IPV4=yes
SYSTEMD_CONTROLLED=no
NM_CONTROLLED=no
EOF

echo '192.168.30.2/28' > /etc/net/ifaces/enp0s3/ipv4address
echo 'default via 192.168.30.1' > /etc/net/ifaces/enp0s3/ipv4route
echo 'nameserver 192.168.120.2' > /etc/net/ifaces/enp0s3/resolv.conf
systemctl restart network
```

Проверка:

```bash
ip -br a
ip route
ping -c 3 192.168.30.1
```

---

## 1.8 Локальные пользователи

На HQ-SRV и BR-SRV:

```bash
useradd -m -u 2026 -s /bin/bash sshuser
passwd sshuser
usermod -aG wheel sshuser
echo 'sshuser ALL=(ALL:ALL) NOPASSWD: ALL' > /etc/sudoers.d/sshuser
chmod 0440 /etc/sudoers.d/sshuser
```

На EcoRouter:

```text
configure terminal
username net_admin
 password CHANGE_ME_FROM_TASK
 role admin
 exit
write memory
```

Проверка Linux:

```bash
id sshuser
sudo -l -U sshuser
```

---

## 1.9 SSH: порт, пользователь, баннер, MaxAuthTries

На HQ-SRV и BR-SRV:

```bash
apt-get update
apt-get install -y openssh-server
```

Файл SSH может называться по-разному:

| ОС | Путь |
|---|---|
| Debian/Ubuntu | `/etc/ssh/sshd_config` |
| ALT в некоторых сборках | `/etc/openssh/sshd_config` |

Пример настройки:

```bash
SSHD_CONFIG='/etc/ssh/sshd_config'
[ -f /etc/openssh/sshd_config ] && SSHD_CONFIG='/etc/openssh/sshd_config'

sed -i 's/^#*Port .*/Port 2026/' "$SSHD_CONFIG"
sed -i 's/^#*MaxAuthTries .*/MaxAuthTries 2/' "$SSHD_CONFIG"
grep -q '^AllowUsers' "$SSHD_CONFIG" && sed -i 's/^AllowUsers.*/AllowUsers sshuser/' "$SSHD_CONFIG" || echo 'AllowUsers sshuser' >> "$SSHD_CONFIG"
grep -q '^Banner' "$SSHD_CONFIG" && sed -i 's|^Banner.*|Banner /etc/openssh/banner|' "$SSHD_CONFIG" || echo 'Banner /etc/openssh/banner' >> "$SSHD_CONFIG"

mkdir -p /etc/openssh
echo 'Authorized access only' > /etc/openssh/banner
systemctl restart sshd || systemctl restart ssh
```

Проверка:

```bash
ss -tulpn | grep 2026
systemctl status sshd || systemctl status ssh
```

---

## 1.10 GRE-туннель на EcoRouter

### HQ-RTR

```text
configure terminal
interface tunnel.1
 description HQ-to-BR
 ip address 10.10.10.1/30
 ip tunnel 172.16.1.2 172.16.2.2 mode gre
 exit
write memory
```

### BR-RTR

```text
configure terminal
interface tunnel.1
 description BR-to-HQ
 ip address 10.10.10.2/30
 ip tunnel 172.16.2.2 172.16.1.2 mode gre
 exit
write memory
```

Проверка:

```text
show ip interface brief
show interface tunnel.1
ping 10.10.10.1
ping 10.10.10.2
```

---

## 1.11 OSPF на EcoRouter только через tunnel.1

### HQ-RTR

```text
configure terminal
router ospf 1
 ospf router-id 1.1.1.1
 passive-interface default
 no passive-interface tunnel.1
 network 10.10.10.0/30 area 0
 network 192.168.120.0/27 area 0
 network 192.168.220.0/27 area 0
 network 192.168.88.0/29 area 0
 exit

interface tunnel.1
 ip ospf authentication message-digest
 ip ospf message-digest-key 1 md5 CHANGE_ME_FROM_TASK
 exit
write memory
```

### BR-RTR

```text
configure terminal
router ospf 1
 ospf router-id 2.2.2.2
 passive-interface default
 no passive-interface tunnel.1
 network 10.10.10.0/30 area 0
 network 192.168.30.0/28 area 0
 exit

interface tunnel.1
 ip ospf authentication message-digest
 ip ospf message-digest-key 1 md5 CHANGE_ME_FROM_TASK
 exit
write memory
```

Проверка:

```text
show ip ospf neighbor
show ip route ospf
show ip ospf interface tunnel.1
```

---

## 1.12 NAT на HQ-RTR и BR-RTR через EcoRouter

### HQ-RTR

```text
configure terminal
interface ISP
 ip nat outside
 exit

interface VLAN120
 ip nat inside
 exit

interface VLAN220
 ip nat inside
 exit

interface VLAN888
 ip nat inside
 exit

ip nat pool HQ-SRV 192.168.120.1-192.168.120.30
ip nat pool HQ-CLI 192.168.220.1-192.168.220.30
ip nat pool HQ-MGMT 192.168.88.1-192.168.88.6

ip nat source dynamic inside-to-outside pool HQ-SRV overload interface ISP
ip nat source dynamic inside-to-outside pool HQ-CLI overload interface ISP
ip nat source dynamic inside-to-outside pool HQ-MGMT overload interface ISP
write memory
```

### BR-RTR

```text
configure terminal
interface ISP
 ip nat outside
 exit

interface LOCAL
 ip nat inside
 exit

ip nat pool BR-NET 192.168.30.1-192.168.30.14
ip nat source dynamic inside-to-outside pool BR-NET overload interface ISP
write memory
```

Проверка:

```text
show ip nat translations
show running-config | include nat
```

---

## 1.13 DHCP на HQ-RTR для VLAN 220

```text
configure terminal
ip pool VLAN220 192.168.220.10-192.168.220.30

dhcp-server 1
 pool VLAN220 1
  mask 27
  gateway 192.168.220.1
  dns 192.168.120.2
  domain-name au-team.irpo
  exit
 exit

interface VLAN220
 dhcp-server 1
 exit
write memory
```

Проверка на HQ-RTR:

```text
show running-config | include dhcp
show dhcp-server clients VLAN220
```

Проверка на HQ-CLI:

```bash
ip -br a
ip route
cat /etc/resolv.conf
ping -c 3 192.168.220.1
ping -c 3 192.168.120.2
```

---

## 1.14 DNS на HQ-SRV

Установить BIND:

```bash
apt-get update
apt-get install -y bind bind-utils || apt-get install -y bind9 bind9-utils
```

Прямая зона `au-team.irpo` должна содержать:

```zone
$TTL 1D
@       IN SOA  hq-srv.au-team.irpo. root.au-team.irpo. (
        2026060401 ; serial
        12H        ; refresh
        1H         ; retry
        1W         ; expire
        1H )       ; negative cache

        IN NS   hq-srv.au-team.irpo.

hq-rtr  IN A    192.168.120.1
hq-srv  IN A    192.168.120.2
hq-cli  IN A    192.168.220.10
br-rtr  IN A    192.168.30.1
br-srv  IN A    192.168.30.2
web     IN A    172.16.1.1
docker  IN A    172.16.2.1
mon     IN A    192.168.120.2
```

Обратные зоны минимум для HQ-SRV/HQ-CLI:

```zone
; 120.168.192.in-addr.arpa
1 IN PTR hq-rtr.au-team.irpo.
2 IN PTR hq-srv.au-team.irpo.
```

```zone
; 220.168.192.in-addr.arpa
1  IN PTR hq-rtr.au-team.irpo.
10 IN PTR hq-cli.au-team.irpo.
```

Проверка:

```bash
named-checkconf
named-checkconf -z
systemctl restart bind || systemctl restart bind9
host hq-srv.au-team.irpo 127.0.0.1
host web.au-team.irpo 127.0.0.1
host docker.au-team.irpo 127.0.0.1
```

---

## 1.15 Часовой пояс

На ALT/Linux:

```bash
timedatectl set-timezone Europe/Moscow
timedatectl
```

На EcoRouter:

```text
configure terminal
ntp timezone utc+3
write memory
show ntp timezone
```

---

## 1.16 Итоговые проверки Модуля 1

### ISP

```bash
ip -br a
ip route
iptables -t nat -L -n -v
ping -c 3 172.16.1.2
ping -c 3 172.16.2.2
```

### HQ-RTR

```text
show port brief
show ip interface brief
show ip route
show ip ospf neighbor
show ip nat translations
ping 172.16.1.1
ping 10.10.10.2
ping 192.168.30.2
```

### BR-RTR

```text
show port brief
show ip interface brief
show ip route
show ip ospf neighbor
show ip nat translations
ping 172.16.2.1
ping 10.10.10.1
ping 192.168.120.2
```

### HQ-SRV

```bash
hostname -f
ip -br a
ip route
ss -tulpn | grep 2026
host hq-srv.au-team.irpo 127.0.0.1
host web.au-team.irpo 127.0.0.1
ping -c 3 192.168.120.1
ping -c 3 192.168.30.2
```

### HQ-CLI

```bash
ip -br a
ip route
cat /etc/resolv.conf
ping -c 3 192.168.220.1
ping -c 3 192.168.120.2
ping -c 3 192.168.30.2
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

Проверь уровень RAID, количество дисков и их имена. После подготовки массива:

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
exportfs -v
```

---

## 2.3 Chrony

На ISP:

```bash
apt update
apt install -y chrony
```

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

| Где | Внешний порт | Внутренний узел |
|---|---:|---|
| HQ-RTR | 8080 | `192.168.120.2:80` |
| HQ-RTR | 2026 | `192.168.120.2:2026` |
| BR-RTR | 8080 | `192.168.30.2:8080` |
| BR-RTR | 2026 | `192.168.30.2:2026` |

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

Порядок:

1. Создать CA.
2. Создать сертификаты web/docker.
3. Перенести сертификаты на ISP.
4. Настроить nginx на HTTPS.
5. Импортировать CA на HQ-CLI.
6. Проверить отсутствие предупреждений браузера.

---

## 3.2 Защищённый туннель

Варианты:

- IPsec поверх WAN;
- GRE over IPsec;
- другой вариант, если он разрешён заданием.

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

## 3.8 Проверки Модуля 3

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

# Источники и адаптация

Логика Модуля 1 адаптирована под VLAN `120/220/888` на основе типового порядка задания: hostname, IPv4, настройка ISP, пользователи, коммутация HQ через service-instance, SSH, GRE, OSPF, NAT, DHCP, DNS и часовой пояс.

Дополнительные файлы:

- [`TABLES.md`](./TABLES.md) — таблицы адресации.
- [`COMMAND_INDEX.md`](./COMMAND_INDEX.md) — индекс команд.
- [`docs/ip-calculation.md`](./docs/ip-calculation.md) — расчёт IP.
- [`docs/workflow.md`](./docs/workflow.md) — порядок выполнения.
- [`prompts/ip-calc-prompt.md`](./prompts/ip-calc-prompt.md) — промт для расчёта IP.
- [`scripts/calc_subnets.py`](./scripts/calc_subnets.py) — проверка подсетей.
- [`DISCLAIMER.md`](./DISCLAIMER.md) — ограничения.
