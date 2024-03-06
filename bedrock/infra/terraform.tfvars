enabled = true
vpc_id = "vpc-123abc"
subnet_ids = ["subnet-abc123", "subnet-def456", "subnet-ghi789"]
create_security_group = true
security_group_name = "my-msk-security-group"
kafka_version = "2.6.1"
broker_per_zone = 1
broker_instance_type = "kafka.m5.large"
client_broker = "TLS"
public_access_enabled = false
# Set other variables as needed
