import yaml
import json

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
                result['_meta']['hostvars'][host] = hostvars
    for group, group_data in data['all']['children'].items():
        parse_group(group, group_data)
    return result

if __name__ == "__main__":
    awx_inventory = build_awx_inventory(inventory)
    print(json.dumps(awx_inventory, indent=2))
