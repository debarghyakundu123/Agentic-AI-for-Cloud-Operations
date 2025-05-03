import openstack
import traceback

# Authentication and connection
def connect_openstack():
    try:
        conn = openstack.connection.Connection(
            auth_url='https://api-ap-south-mum-1.openstack.acecloudhosting.com:5000/v3',
            token='gAAAAABoFe1O_bq2pYiK7KCQhfQOlavJa8yBv_u1_gzzm1N6fOw2Rl1WjySv5EdX9W9IkSgjWD1ue3qK1saI-X0S2a6wtwXIzHOMn2o9GNX3he8_kF0netIad2xW4knBz3aTrua0bNA0ZMCHeAFzfEOphpLZHKCtHnSPCMvuoWLAlYtUyAUcpIE',
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
if _name_ == "_main_":
    # Initialize connection
    conn = connect_openstack()

    if conn:
        # Configuration - replace with your actual values
        image_id = 'b3f7de60-758e-46ce-a9f9-d6bfa51aa04f'
        flavor_id = '0003ee89-5d94-42f5-a331-85d2f838bd2e'
        network_id = '41e6e97b-b3fe-474e-bb74-dbc7943b1a6c'
        vm_name = "dev-box"

        # Create the VM
        server = create_vm(conn, vm_name, image_id, flavor_id, network_id)
        
        if not server:
            print("🚫 VM creation failed")
    else:
        print("🚫 Aborting VM creation due to connection failure.")
