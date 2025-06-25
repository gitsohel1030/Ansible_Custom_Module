#!/usr/bin/python

from ansible.module_utils.basic import AnsibleModule
import subprocess
import socket
import platform


def check_service(name):
    try:
        system = platform.system()
        if system == 'Windows':
            result = subprocess.run(['sc', 'query', name],
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE,
                                    text=True)
            return "RUNNING" in result.stdout
        else:
            result = subprocess.run(['systemctl', 'is-active', name],
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE)
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
    system = platform.system()
    if system == "Windows":
        ping_cmd = ['ping', '-n', '1', host]
    else:
        ping_cmd = ['ping', '-c', '1', host]
    try:
        result = subprocess.run(ping_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return result.returncode == 0
    except Exception:
        return False


def run_module():
    module_args = dict(
        service=dict(type='str', required=True),
        dependencies=dict(type='list', required=True, elements='dict')
    )

    result = dict(
        changed=False,
        failed_dependencies=[],
        message="All dependencies are healthy."
    )

    module = AnsibleModule(argument_spec=module_args, supports_check_mode=True)

    failed = []

    for dep in module.params['dependencies']:
        dep_type = dep.get('type')
        if dep_type == 'service':
            if not check_service(dep['name']):
                failed.append(f"Service {dep['name']} is not active")
        elif dep_type == 'port':
            if not check_port(dep['host'], dep['port']):
                failed.append(f"Port {dep['port']} on {dep['host']} is not reachable")
        elif dep_type == 'ping':
            if not check_ping(dep['host']):
                failed.append(f"Host {dep['host']} is not pingable")
        else:
            failed.append(f"Unknown dependency type: {dep_type}")

    if failed:
        result['failed_dependencies'] = failed
        module.fail_json(msg="One or more dependencies failed", **result)

    module.exit_json(**result)


def main():
    run_module()


if __name__ == '__main__':
    main()
