import csv
import subprocess
from datetime import datetime
 
def get_ansible_facts():
    cmd = [
        'ansible', 'rhel_servers', '-m', 'setup',
        '--tree', '/tmp/facts/', '-i', 'ansible/inventory/hosts.ini'
    ]
subprocess.run(cmd, check=True)
 
def parse_system_info(host):
    with open(f'/tmp/facts/{host}') as f:
        data = json.load(f)
        return {
            'hostname': data['ansible_facts']['ansible_hostname'],
            'os': data['ansible_facts']['ansible_distribution'] + ' ' +
                  data['ansible_facts']['ansible_distribution_version'],
            'kernel': data['ansible_facts']['ansible_kernel'],
            'packages': data['ansible_facts']['ansible_packages']
        }
 
def generate_csv():
    headers = [
        'Hostname', 'OS Version', 'Kernel Version',
        'Pending Updates', 'Reboot Required', 'Last Checked'
    ]
    
    with open('reports/patch_report.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(headers)
        
        # Get list of hosts from inventory
        with open('ansible/inventory/hosts.ini') as f:
            hosts = [line.split()[0] for line in f if line.strip() and not line.startswith('[')]
        
        for host in hosts:
            info = parse_system_info(host)
            writer.writerow([
                info['hostname'],
                info['os'],
                info['kernel'],
                len(info['packages']['security']),
                'Yes' if subprocess.check_output(
                    f"ansible {host} -m shell -a 'test -f /var/run/reboot-required && echo 1 || echo 0'",
                    shell=True).decode().strip() == '1' else 'No',
                datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            ])
 
if __name__ == "__main__":
    get_ansible_facts()
    generate_csv()