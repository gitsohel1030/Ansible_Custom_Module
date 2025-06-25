#!/usr/bin/python

from ansible.module_utils.basic import AnsibleModule
import subprocess
import socket
import platform
import time


def check_service(name):
    try:
        if platform.system() == 'Windows':
            result = subprocess.run(['sc', 'query', name], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            return any("STATE" in line and "RUNNING" in line for line in result.stdout.splitlines())
        else:
            result = subprocess.run(['systemctl', 'is-active', name], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            return result.returncode == 0
    except Exception:
        return False


def start_service(name):
    try:
        if platform.system() == 'Windows':
            result = subprocess.run(['sc', 'start', name], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            return result.returncode == 0
        else:
            result = subprocess.run(['systemctl', 'start', name], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            return result.returncode == 0
    except Exception:
        return False


def check_port(host, port):
    try:
        with socket.create_connection((host, port), timeout=3):
            return True
    except Exception:
        return False


def check_ping(host):
    cmd = ['ping', '-n', '1', host] if platform.system() == "Windows" else ['ping', '-c', '1', host]
    try:
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return result.returncode == 0
    except Exception:
        return False


def run_with_retry(check_func, *args, retries=1, delay=0):
    for attempt in range(retries):
        if check_func(*args):
            return True
        if attempt < retries - 1:
            time.sleep(delay)
    return False


def run_module():
    module_args = dict(
        service=dict(type='str', required=True),
        dependencies=dict(type='list', required=True, elements='dict')
    )

    result = dict(
        changed=False,
        results={},
        failed_dependencies=[],
        message="All dependencies are healthy."
    )

    module = AnsibleModule(argument_spec=module_args, supports_check_mode=True)

    for dep in module.params['dependencies']:
        dep_type = dep.get('type')
        retries = dep.get('retries', 1)
        delay = dep.get('delay', 0)
        auto_fix = dep.get('auto_fix', False)
        key = ""

        if dep_type == 'service':
            name = dep['name']
            key = f"{name} (service)"

            status = run_with_retry(check_service, name, retries=retries, delay=delay)

            if not status and auto_fix:
                started = start_service(name)
                if started:
                    status = run_with_retry(check_service, name, retries=retries, delay=delay)
                    if status:
                        result['results'][key] = "fixed"
                        continue  # skip to next dependency

            result['results'][key] = "healthy" if status else "unhealthy"
            if not status:
                result['failed_dependencies'].append(f"{key} check failed")

        elif dep_type == 'port':
            host = dep['host']
            port = dep['port']
            key = f"{host}:{port} (port)"
            status = run_with_retry(check_port, host, port, retries=retries, delay=delay)
            result['results'][key] = "healthy" if status else "unhealthy"
            if not status:
                result['failed_dependencies'].append(f"{key} check failed")

        elif dep_type == 'ping':
            host = dep['host']
            key = f"{host} (ping)"
            status = run_with_retry(check_ping, host, retries=retries, delay=delay)
            result['results'][key] = "healthy" if status else "unhealthy"
            if not status:
                result['failed_dependencies'].append(f"{key} check failed")

        else:
            key = f"unknown ({dep_type})"
            result['results'][key] = "invalid type"
            result['failed_dependencies'].append(f"Unknown dependency type: {dep_type}")

    if result['failed_dependencies']:
        module.fail_json(msg="One or more dependencies failed", **result)

    module.exit_json(**result)


def main():
    run_module()


if __name__ == '__main__':
    main()
