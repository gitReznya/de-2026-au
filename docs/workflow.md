# Порядок выполнения ДЭ

## Перед началом

Проверь интерфейсы на каждой машине:

```bash
ip -br link
ip -br a
```

Если имена интерфейсов отличаются от примеров, меняй переменные в командных файлах.

## Модуль 1

Рекомендуемый порядок:

```text
1. ISP
2. HQ-RTR
3. BR-RTR
4. HQ-SW / VLAN на гипервизоре
5. HQ-SRV
6. BR-SRV
7. HQ-CLI
8. Проверки
```

## Модуль 2

```text
1. HQ-SRV: RAID, NFS, Web, MariaDB
2. BR-SRV: Samba DC, Ansible, Docker
3. HQ-RTR / BR-RTR: port forwarding
4. ISP: nginx reverse proxy + Basic Auth
5. HQ-CLI: домен, NFS, браузер
6. Проверки
```

## Модуль 3

```text
1. HQ-SRV: CA, сертификаты, rsyslog, fail2ban, CUPS, monitoring
2. ISP: HTTPS reverse proxy
3. BR-SRV: rsyslog client, Ansible inventory report
4. RTR: firewall, syslog, encrypted tunnel
5. HQ-CLI: CA trust, printer, HTTPS checks
```

## Главное правило

Не переходи к следующему модулю, пока не работают:

- маршрутизация;
- DNS;
- доступ между HQ и BR;
- доступ в интернет;
- hostname/FQDN.
