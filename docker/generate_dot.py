import yaml
import sys

def sanitize_name(name):
    return name.replace('-', '_').replace(':', '_').replace('\\', '_').replace('/', '_')

def generate_dot(compose_file):
    with open(compose_file, 'r') as file:
        compose_config = yaml.safe_load(file)

    services = compose_config.get('services', {})
    networks = compose_config.get('networks', {})
    volumes = compose_config.get('volumes', {})

    dot_content = "digraph G {\n"

    for service, config in services.items():
        safe_service = sanitize_name(service)
        dot_content += f'  {safe_service} [label="{service}"];\n'
        for network in config.get('networks', []):
            safe_network = sanitize_name(network)
            dot_content += f'  {safe_service} -> {safe_network};\n'
        for volume in config.get('volumes', []):
            if isinstance(volume, dict):
                source = sanitize_name(volume.get('source', ''))
                target = volume.get('target', '')
                dot_content += f'  {safe_service} -> "{source}" [label="{target}"];\n'
            else:
                safe_volume = sanitize_name(volume)
                dot_content += f'  {safe_service} -> {safe_volume};\n'

    for network in networks:
        safe_network = sanitize_name(network)
        dot_content += f'  {safe_network} [label="{network}", shape=ellipse];\n'

    for volume in volumes:
        safe_volume = sanitize_name(volume)
        dot_content += f'  {safe_volume} [label="{volume}", shape=box];\n'

    dot_content += "}\n"

    with open('docker-compose.dot', 'w') as file:
        file.write(dot_content)

if __name__ == "__main__":
    generate_dot(sys.argv[1])
