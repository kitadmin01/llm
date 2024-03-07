resource "aws_vpc" "kafka_vpc" {
  cidr_block = "10.0.0.0/16"
  enable_dns_support = true
  enable_dns_hostnames = true
  tags = {
    Name = "kafka_vpc"
  }
}

# Create three subnets in different AZs for high availability
resource "aws_subnet" "kafka_subnet" {
  count = 3
  vpc_id     = aws_vpc.kafka_vpc.id
  cidr_block = cidrsubnet(aws_vpc.kafka_vpc.cidr_block, 8, count.index)
  availability_zone = element(var.availability_zones, count.index)
  tags = {
    Name = "kafka_subnet_${count.index}"
  }
}

variable "availability_zones" {
  description = "List of availability zones in the region"
  type        = list(string)
}
