
![ДЭ-2026](https://img.shields.io/badge/ДЭ-2026-blue)
![Домен](https://img.shields.io/badge/domain-au--team.irpo-success)
![VLAN](https://img.shields.io/badge/VLAN-120%20%7C%20220%20%7C%20888-orange)
![Назначение](https://img.shields.io/badge/purpose-learning-lightgrey)

## Быстрая навигация

| Раздел | Что внутри |
|---|---|
| [`TABLES.md`](./TABLES.md) | Машины, hostname, IP, VLAN, шлюзы, DNS, пользователи, порты |
| [`COMMAND_INDEX.md`](./COMMAND_INDEX.md) | Индекс команд по модулям и устройствам |
| [`docs/ip-calculation.md`](./docs/ip-calculation.md) | Как быстро считать IP и маски под другой вариант |
| [`docs/workflow.md`](./docs/workflow.md) | Рекомендуемый порядок выполнения |
| [`prompts/ip-calc-prompt.md`](./prompts/ip-calc-prompt.md) | Готовый промт для пересчёта IP |
| [`prompts/variant-adapter-prompt.md`](./prompts/variant-adapter-prompt.md) | Промт для адаптации команд под другой вариант |
| [`module-1`](./module-1/) | Сеть, VLAN, NAT, SSH, GRE, OSPF, DHCP, DNS |
| [`module-2`](./module-2/) | Samba DC, RAID, NFS, Chrony, Ansible, Docker, Web, Nginx |
| [`module-3`](./module-3/) | CA/HTTPS, IPsec, firewall, CUPS, rsyslog, fail2ban, monitoring |
| [`appendices/report-template.md`](./appendices/report-template.md) | Шаблон отчёта |
| [`DISCLAIMER.md`](./DISCLAIMER.md) | Важные ограничения и предупреждения |

## Принятая адресация

| Сегмент | VLAN | Подсеть | Шлюз |
|---|---:|---|---|
| HQ-SRV | `120` | `192.168.120.0/27` | `192.168.120.1` |
| HQ-CLI | `220` | `192.168.220.0/27` | `192.168.220.1` |
| MGMT | `888` | `192.168.88.0/29` | `192.168.88.1` |
| BR-SRV | — | `192.168.30.0/28` | `192.168.30.1` |
| GRE HQ-BR | — | `10.10.10.0/30` | `10.10.10.1 ↔ 10.10.10.2` |
| ISP-HQ | — | `172.16.1.0/28` | `172.16.1.1` |
| ISP-BR | — | `172.16.2.0/28` | `172.16.2.1` |

## Принятые hostname

| Машина | FQDN |
|---|---|
| ISP | `isp.au-team.irpo` |
| HQ-RTR | `hq-rtr.au-team.irpo` |
| BR-RTR | `br-rtr.au-team.irpo` |
| HQ-SRV | `hq-srv.au-team.irpo` |
| BR-SRV | `br-srv.au-team.irpo` |
| HQ-CLI | `hq-cli.au-team.irpo` |


## Структура

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

## Быстрые проверки

После **Модуля 1**:

```bash
ping -c 3 192.168.120.1
ping -c 3 192.168.30.2
ping -c 3 77.88.8.8
host web.au-team.irpo
host docker.au-team.irpo
```

После **Модуля 2**:

```bash
curl http://web.au-team.irpo
curl http://docker.au-team.irpo
ansible -i /etc/ansible/inventory all -m ping
exportfs -v
```

После **Модуля 3**:

```bash
curl -I https://web.au-team.irpo
curl -I https://docker.au-team.irpo
systemctl status rsyslog
systemctl status fail2ban
systemctl status cups
```

## Осторожно

Не запускай команды вслепую. Сначала смотри файл, потом проверяй синтаксис:

```bash
less module-1/commands/02-hq-rtr.sh
bash -n module-1/commands/02-hq-rtr.sh
```

Особенно опасны команды:

```bash
wipefs
mdadm --create
mkfs.ext4
iptables -F
```

Они могут уничтожить данные или отрезать доступ, если выполнить их не на той машине.

## Правовой статус

Репозиторий предназначен для обучения и тренировки. Он не является официальным экзаменационным материалом и не гарантирует совпадение с реальным вариантом ДЭ. Подробнее: [`DISCLAIMER.md`](./DISCLAIMER.md).
