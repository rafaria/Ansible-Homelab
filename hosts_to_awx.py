import yaml
import json
import argparse

# Carrega o inventário YAML
with open('hosts.yml', 'r') as f:
    inventory = yaml.safe_load(f)

def build_awx_inventory(data):
    """
    Converte o inventário YAML para o formato dinâmico JSON esperado pelo AWX.
    """
    result = {"_meta": {"hostvars": {}}}
    def parse_group(group, group_data):
        hosts = list(group_data.get('hosts', {}).keys()) if 'hosts' in group_data else []
        children = list(group_data.get('children', {}).keys()) if 'children' in group_data else []
        vars_ = group_data.get('vars', {})
        result[group] = {}
        if hosts:
            result[group]['hosts'] = hosts
        if children:
            result[group]['children'] = children
        if vars_:
            result[group]['vars'] = vars_
        # Adiciona hostvars
        for host, hostvars in group_data.get('hosts', {}).items():
            if isinstance(hostvars, dict):
                result['_meta']['hostvars'].setdefault(host, {}).update(hostvars)

    for group, group_data in data.get('all', {}).get('children', {}).items():
        parse_group(group, group_data)
        # Adiciona o grupo 'all' que contém todos os outros grupos como filhos
    result['all'] = {'children': list(data.get('all', {}).get('children', {}).keys())}
    return result

def get_host_vars(inventory, hostname):
    """
    Retorna as variáveis para um host específico.
    """
    return inventory.get('_meta', {}).get('hostvars', {}).get(hostname, {})

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--list', action='store_true')
    parser.add_argument('--host', type=str)
    args = parser.parse_args()

    awx_inventory = build_awx_inventory(inventory)

    if args.list:
        print(json.dumps(awx_inventory, indent=2))
    elif args.host:
        host_vars = get_host_vars(awx_inventory, args.host)
        print(json.dumps(host_vars, indent=2))
    else:
        # Comportamento padrão: exibir o inventário completo
        print(json.dumps(awx_inventory, indent=2))
