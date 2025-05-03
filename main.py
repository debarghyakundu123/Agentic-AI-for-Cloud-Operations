import traceback
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
import openstack
from dotenv import load_dotenv
import os
import json
from openstack.exceptions import NotFoundException

load_dotenv()

# Initialize Gemini model
llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-pro-latest",
    temperature=0.5,
    google_api_key=os.getenv("GOOGLE_API_KEY")
)

def parse_user_input(user_input):
    """Parse natural language into structured OpenStack commands"""
    prompt = ChatPromptTemplate.from_template("""
    Analyze this OpenStack request:
    {request}
    
    Return JSON with:
    - intent (create/delete/resize/query)
    - entity_type (VM/volume/network)
    - parameters (name, size, etc.)
    - needs_confirmation (true/false)
    
    Example:
    Input: "Create a medium VM named 'db-server' with 8GB RAM"
    Output: {{"intent":"create","entity_type":"VM","parameters":{{"name":"db-server","ram":"8GB"}},"needs_confirmation":false}}
    """)
    return (prompt | llm).invoke({"request": user_input})

import re
import json

def extract_json(gemini_response):
    """Extract JSON from Gemini's response, handling code blocks and explanations."""
    content = gemini_response.content.strip()
    # Try to extract JSON from a Markdown code block
    code_block = re.search(r"``````", content)
    if code_block:
        json_str = code_block.group(1).strip()
    else:
        # Fallback: try to find the first { ... } block
        json_match = re.search(r"(\{[\s\S]+\})", content)
        if json_match:
            json_str = json_match.group(1)
        else:
            json_str = content  # Last resort: use the whole content

    try:
        return json.loads(json_str)
    except Exception as e:
        print(f"Error parsing response: {e}")
        print("Raw content was:", content)
        return None

def map_to_openstack_actions(parsed_input):
    """Map parsed input to OpenStack API calls"""
    if not parsed_input:
        return None
        
    conn = openstack.connect(
        auth_url="https://api-ap-south-mum-1.openstack.acecloudhosting.com:5000",
        username="Hackathon_AIML_1",
        password="Hackathon_AIML_1@567",
        project_name="your_project",
        user_domain_name="Default",
        project_domain_name="Default"
    )
    
    actions = []
    
    if parsed_input["intent"] == "create" and parsed_input["entity_type"] == "VM":
        # Convert RAM to flavor
        ram_gb = int(parsed_input["parameters"]["ram"].replace("GB", ""))
        flavor = "S.4" if ram_gb == 4 else "M.8" if ram_gb == 8 else "L.16"
        
        actions.append({
            "api": "compute",
            "operation": "create_server",
            "params": {
                "name": parsed_input["parameters"]["name"],
                "flavor": flavor,
                "image": "ubuntu-20.04"
            }
        })
    
    return actions

if _name_ == "_main_":
    user_input = input("Enter your need:")
    
    try:
        # Step 1: Parse user input
        response = parse_user_input(user_input)
        print("Raw Gemini Response:", response.content)
        
        # Step 2: Extract JSON
        parsed = extract_json(response)
        
        if not parsed:
            print("Failed to parse the input")
            exit(1)
            
        print("Parsed Output:", parsed)
        name_value = parsed['parameters']['name']
        intent=parsed['intent']
        entity = parsed['entity_type']
    
        # Step 3: Map to OpenStack actions
        actions = map_to_openstack_actions(parsed)
        print("Generated Actions:", actions)
        
    except Exception as e:
        print(f"Error: {e}")
        

load_dotenv()

auth_token=os.getenv("token")

# Authentication and connection
def connect_openstack():
    try:
        conn = openstack.connection.Connection(
            auth_url='https://api-ap-south-mum-1.openstack.acecloudhosting.com:5000/v3',
            token=auth_token,
            project_id='a02b14bcfca64e44bd68f2d00d8555b5',
            region_name='ap-south-mum-1',
            identity_interface='public',
            auth_type='token'
        )
        print("✅ Connected to OpenStack successfully.")
        return conn
    except Exception as e:
        print(f"❌ Error connecting to OpenStack:\n{e}")
        traceback.print_exc()
        return None

# Create virtual machine with volume-backed instance
def create_vm(conn, vm_name, image_id, flavor_id, network_id):
    try:
        print(f"🚀 Creating VM: {vm_name}")
        
        # Create server with volume-backed boot device
        server = conn.compute.create_server(
            name=vm_name,
            flavor_id=flavor_id,
            networks=[{"uuid": network_id}],
            block_device_mapping_v2=[{
                'boot_index': 0,             # First boot device
                'uuid': image_id,            # Image to create volume from
                'source_type': 'image',      # Source is an image
                'destination_type': 'volume', # Create volume from image
                'volume_size': 10,           # Size in GB (minimum 10GB recommended)
                'delete_on_termination': True # Auto-delete volume when server is deleted
            }]
        )
        
        print("⏳ Waiting for VM to become active...")
        server = conn.compute.wait_for_server(server)
        
        print(f"✅ VM created successfully!")
        print(f"📛 Name: {server.name}")
        print(f"🆔 ID: {server.id}")
        print(f"🔌 IP Addresses: {server.addresses}")
        
        return server
        
    except Exception as e:
        print(f"❌ Failed to create VM: {e}")
        traceback.print_exc()
        return None
    
    

# Main execution

if intent == "create":
    # Initialize connection
    conn = connect_openstack()

    if conn:
        # Configuration - replace with your actual values
        image_id = 'b3f7de60-758e-46ce-a9f9-d6bfa51aa04f'
        flavor_id = '0003ee89-5d94-42f5-a331-85d2f838bd2e'
        network_id = '41e6e97b-b3fe-474e-bb74-dbc7943b1a6c'
        vm_name = name_value

        # Create the VM
        server = create_vm(conn, vm_name, image_id, flavor_id, network_id)
        
        if not server:
            print("🚫 VM creation failed")
    else:
        print("🚫 Aborting VM creation due to connection failure.")
        
        
# Feature 2:

def connect_openstack():
    try:
        conn = openstack.connection.Connection(
            auth_url='https://api-ap-south-mum-1.openstack.acecloudhosting.com:5000/v3',
            token=auth_token,
            project_id='a02b14bcfca64e44bd68f2d00d8555b5',
            region_name='ap-south-mum-1',
            identity_interface='public',
            auth_type='token'
        )
        print("✅ Connected to OpenStack successfully.")
        return conn
    except Exception as e:
        print(f"❌ Error connecting to OpenStack:\n{e}")
        traceback.print_exc()
        return None

def find_servers_by_name(conn, vm_name):
    try:
        servers = [server for server in conn.compute.servers() if server.name == vm_name]
        return servers
    except Exception as e:
        print(f"❌ Error retrieving servers:\n{e}")
        traceback.print_exc()
        return []

def resize_vm(conn, server_id, new_flavor_id):
    try:
        server = conn.compute.get_server(server_id)
        if not server:
            print(f"❌ VM with ID '{server_id}' not found.")
            return False

        print(f"🔄 Resizing VM '{server.name}' (ID: {server.id}) to flavor '{new_flavor_id}'...")
        conn.compute.resize_server(server, new_flavor_id)

        # Wait for the server to enter VERIFY_RESIZE status
        conn.compute.wait_for_status(
            conn.compute.get_server(server_id),
            status='VERIFY_RESIZE',
            failures=['ERROR'],
            interval=5,
            wait=300
        )

        # Confirm the resize by calling the API directly
        conn.compute.post(
            f'servers/{server_id}/action',
            json={"confirmResize": None}
        )

        print(f"✅ VM '{server.name}' resized successfully to flavor '{new_flavor_id}'.")
        return True
    except Exception as e:
        print(f"❌ Failed to resize VM: {e}")
        traceback.print_exc()
        return False

if intent=='resize':
    conn = connect_openstack()
    if not conn:
        print("🚫 Aborting VM resize due to connection failure.")
        exit(1)

    vm_name = name_value

    # Replace this with the flavor name or ID you want to resize to
    # Example flavor from your list:
    # new_flavor_id = "M.32"  # flavor name
    new_flavor_id = "316f94a3-c2b5-4068-8a71-1c61c901c0f7"  # flavor ID for M.32

    servers = find_servers_by_name(conn, vm_name)

    if not servers:
        print(f"❌ No VM found with the name '{vm_name}'.")
        exit(1)
    if len(servers) == 1:
        # Only one server found, proceed to resize
        server_id = servers[0].id
        success = resize_vm(conn, server_id, new_flavor_id)
        if not success:
            print("🚫 VM resize failed.")
    else:
        # Multiple servers found with the same name
        print(f"⚠ Multiple VMs found with the name '{vm_name}':")
        for idx, server in enumerate(servers, start=1):
            print(f"  {idx}. ID: {server.id}, Status: {server.status}, Name: {server.name}")

        # Ask user to select which VM to resize
        while True:
            try:
                choice = int(input(f"Enter the number (1-{len(servers)}) of the VM you want to resize: "))
                if 1 <= choice <= len(servers):
                    selected_server_id = servers[choice - 1].id
                    break
                else:
                    print("❌ Invalid choice. Please enter a valid number.")
            except ValueError:
                print("❌ Invalid input. Please enter a number.")

        success = resize_vm(conn, selected_server_id, new_flavor_id)
        if not success:
            print("🚫 VM resize failed.")
            
# Feature 3:

def connect_openstack():
    try:
        conn = openstack.connection.Connection(
            auth_url='https://api-ap-south-mum-1.openstack.acecloudhosting.com:5000/v3',
            token=auth_token,
            project_id='a02b14bcfca64e44bd68f2d00d8555b5',
            region_name='ap-south-mum-1',
            identity_interface='public',
            auth_type='token'
        )
        print("✅ Connected to OpenStack successfully.")
        return conn
    except Exception as e:
        print(f"❌ Error connecting to OpenStack:\n{e}")
        traceback.print_exc()
        return None

def delete_vm(conn, vm_name):
    try:
        # List all servers with the matching name
        servers = [server for server in conn.compute.servers() if server.name == vm_name]
        
        if not servers:
            print(f"❌ VM '{vm_name}' not found.")
            return False
        
        for server in servers:
            print(f"🗑 Deleting VM '{server.name}' with ID {server.id}...")
            conn.compute.delete_server(server, ignore_missing=False)
            conn.compute.wait_for_delete(server)
            print(f"✅ VM '{server.name}' with ID {server.id} deleted successfully.")
        
        return True
    except Exception as e:
        print(f"❌ Failed to delete VM(s): {e}")
        traceback.print_exc()
        return False

if intent=='delete':
    conn = connect_openstack()
    if conn:
        vm_name = name_value
        success = delete_vm(conn, vm_name)
        if not success:
            print("🚫 VM deletion failed.")
    else:
        print("🚫 Aborting VM deletion due to connection failure.")
        

# Feature 4:

def connect_openstack():
    try:
        conn = openstack.connection.Connection(
            auth_url='https://api-ap-south-mum-1.openstack.acecloudhosting.com:5000/v3',
            token=auth_token,
            project_id='a02b14bcfca64e44bd68f2d00d8555b5',
            region_name='ap-south-mum-1',
            identity_interface='public',
            auth_type='token'
        )
        print("✅ Connected to OpenStack successfully.")
        return conn
    except Exception as e:
        print(f"❌ Error connecting to OpenStack:\n{e}")
        traceback.print_exc()
        return None

def create_network(conn, parameters, subnet_cidr="192.168.0.0/24"):
    try:
        print(f"🌐 Creating network '{parameters['name']}'...")
        network = conn.network.create_network(
            name=parameters['name'],
            admin_state_up=parameters.get('admin_state_up', True),
            shared=parameters.get('shared', False),
            is_router_external=parameters.get('external', False)
        )
        print(f"🔹 Network '{network.name}' created with ID: {network.id}")

        print(f"🌐 Creating subnet for network '{network.name}' with CIDR {subnet_cidr}...")
        subnet = conn.network.create_subnet(
            network_id=network.id,
            ip_version='4',
            cidr=subnet_cidr,
            name=f"{network.name}-subnet"
        )
        print(f"🔹 Subnet '{subnet.name}' created with ID: {subnet.id}")

        print(f"✅ Network '{network.name}' and subnet created successfully.")
        return network, subnet
    except Exception as e:
        print(f"❌ Failed to create network and subnet: {e}")
        traceback.print_exc()
        return None, None

if entity == 'network':
    conn = connect_openstack()
    if conn:
        network_name = name_value
        network, subnet = create_network(conn, network_name)
        if not network:
            print("🚫 Network creation failed.")
    else:
        print("🚫 Aborting network creation due to connection failure.")
        

# Feature 5:

def connect_openstack():
    try:
        conn = openstack.connection.Connection(
            auth_url='https://api-ap-south-mum-1.openstack.acecloudhosting.com:5000/v3',
            token=auth_token,
            region_name='ap-south-mum-1',
            identity_interface='public',
            auth_type='token'
        )
        conn.authorize()  # Force authentication to verify credentials
        print("✅ Connected to OpenStack successfully.")
        return conn
    except Exception as e:
        print(f"❌ Error connecting to OpenStack:\n{e}")
        traceback.print_exc()
        return None

def create_volume(conn, volume_name, size_gb):
    try:
        print(f"💾 Creating volume '{volume_name}' of size {size_gb} GB...")
        volume = conn.block_storage.create_volume(
            name=volume_name,
            size=size_gb
        )
        conn.block_storage.wait_for_status(volume, status='available', failures=['error'], interval=5, wait=300)
        print(f"✅ Volume '{volume_name}' created successfully with ID: {volume.id}")
        return volume
    except Exception as e:
        print(f"❌ Failed to create volume: {e}")
        traceback.print_exc()
        return None

def delete_volume(conn, volume_name):
    try:
        volume = conn.block_storage.find_volume(volume_name)
        if not volume:
            print(f"❌ Volume '{volume_name}' not found.")
            return False

        print(f"🗑 Deleting volume '{volume_name}'...")
        conn.block_storage.delete_volume(volume, ignore_missing=False)
        conn.block_storage.wait_for_delete(volume)
        print(f"✅ Volume '{volume_name}' deleted successfully.")
        return True
    except Exception as e:
        print(f"❌ Failed to delete volume: {e}")
        traceback.print_exc()
        return False

if entity=="volume" & intent=="create":
    conn = connect_openstack()
    if conn:
        volume_name = name_value
        size_gb = 100

        vol = create_volume(conn, volume_name, size_gb)
        if not vol:
            print("🚫 Volume creation failed.")
            
    else:
        print("🚫 Aborting volume operation due to connection failure.")
        
if entity=="volume" & intent=='delete':
    conn = connect_openstack()
    if conn:
        volume_name = name_value

        success = delete_volume(conn, volume_name)
        if not success:
             print("🚫 Volume deletion failed.")
    else:
        print("🚫 Aborting volume operation due to connection failure.")
        
# Feature 6:


def connect_openstack():
    try:
        conn = openstack.connection.Connection(
            auth_url='https://api-ap-south-mum-1.openstack.acecloudhosting.com:5000/v3',
            token= auth_token,
            region_name='ap-south-mum-1',
            identity_interface='public',
            auth_type='token'
        )
        print("✅ Connected to OpenStack successfully.")
        return conn
    except Exception as e:
        print(f"❌ Error connecting to OpenStack:\n{e}")
        traceback.print_exc()
        return None

def get_project_usage(conn):
    try:
        print("📊 Gathering project usage...")

        # Aggregate vCPU and RAM from servers
        servers = list(conn.compute.servers(all_projects=False))
        total_vcpus = 0
        total_ram_mb = 0
        total_gpus = 0  # Assuming GPU info is available via flavor extra specs or metadata

        for server in servers:
            flavor_id = server.flavor.get('id')
            try:
                flavor = conn.compute.get_flavor(flavor_id)
            except NotFoundException:
                print(f"⚠ Flavor '{flavor_id}' not found for server '{server.id}', skipping this server.")
                continue
            except Exception as e:
                print(f"⚠ Unexpected error fetching flavor '{flavor_id}' for server '{server.id}': {e}")
                continue

            total_vcpus += flavor.vcpus
            total_ram_mb += flavor.ram

            # GPU counting depends on flavor extra_specs or metadata
            gpu_count = 0
            try:
                extra_specs = flavor.extra_specs if hasattr(flavor, 'extra_specs') else {}
                gpu_count = int(extra_specs.get('resources:VGPU', 0))
            except Exception:
                # If any error parsing GPU count, just ignore and assume 0
                gpu_count = 0
            total_gpus += gpu_count

        # Aggregate volume size in GB
        volumes = list(conn.block_storage.volumes(details=True))
        total_volume_gb = sum(volume.size for volume in volumes if volume.status in ['available', 'in-use'])

        print(f"✅ Usage Summary:")
        print(f"   - Total vCPUs: {total_vcpus}")
        print(f"   - Total RAM (MB): {total_ram_mb}")
        print(f"   - Total GPUs: {total_gpus}")
        print(f"   - Total Volume Size (GB): {total_volume_gb}")

        return {
            "vcpus": total_vcpus,
            "ram_mb": total_ram_mb,
            "gpus": total_gpus,
            "volume_gb": total_volume_gb
        }
    except Exception as e:
        print(f"❌ Failed to get usage: {e}")
        traceback.print_exc()
        return None

if entity == "project" :
    conn = connect_openstack()
    if conn:
        usage = get_project_usage(conn)
        if not usage:
            print("🚫 Usage query failed.")
    else:
        print("🚫 Aborting usage query due to connection failure.")
