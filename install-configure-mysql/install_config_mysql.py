#!/usr/bin/python3

import json
import subprocess
from ansible.module_utils.basic import AnsibleModule

def run_command(command):
    """Run a shell command and return the output, error and return code."""
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    return result.stdout, result.stderr, result.returncode

def main():
    module = AnsibleModule(
        argument_spec=dict(
            max_connections=dict(required=False, type='int', default=151),
            bind_address=dict(required=False, type='str', default='0.0.0.0')
        )
    )

    max_connections = module.params['max_connections']
    bind_address = module.params['bind_address']

    result = {
        'changed': False,
        'msg': ''
    }

    try:
        # Install MySQL
        install_commands = [
            "sudo apt-get update",
            "sudo apt-get install -y mysql-server",
            "sudo systemctl start mysql",
            "sudo systemctl enable mysql"
        ]

        for cmd in install_commands:
            out, err, rc = run_command(cmd)
            if rc != 0:
                module.fail_json(msg=f"Failed to execute: {cmd}, Error: {err}")

        result['changed'] = True

        # Configure MySQL
        config_commands = [
            f"sudo sed -i \"s/bind-address\\s*=\\s*127.0.0.1/bind-address = {bind_address}/\" /etc/mysql/mysql.conf.d/mysqld.cnf",
            f"sudo sed -i \"s/^max_connections.*/max_connections = {max_connections}/\" /etc/mysql/mysql.conf.d/mysqld.cnf",
            "sudo systemctl restart mysql"
        ]

        for cmd in config_commands:
            out, err, rc = run_command(cmd)
            if rc != 0:
                module.fail_json(msg=f"Failed to execute: {cmd}, Error: {err}")

        result['msg'] = f"MySQL installed and configured with bind_address={bind_address} and max_connections={max_connections}."
    
    except Exception as e:
        module.fail_json(msg=f"An error occurred: {str(e)}")

    module.exit_json(**result)

if __name__ == '__main__':
    main()

