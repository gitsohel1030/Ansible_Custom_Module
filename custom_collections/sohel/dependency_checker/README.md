# sohel.dependency_checker

A custom Ansible module to check service, port, and ping dependencies before restarting a service.

## Features
- Works on Linux and Windows
- Retry and delay support
- Optional auto-fix for services
- Logging to file

## Usage

```yaml
- name: Check dependencies
  sohel.dependency_checker.service_dependency_checker:
    service: nginx
    log_file: /tmp/dep_check.log
    dependencies:
      - type: service
        name: redis
        auto_fix: true
        retries: 3
        delay: 5
      - type: port
        host: 127.0.0.1
        port: 3306
