variable "aws_region" {
  description = "The AWS region where resources will be created"
  type        = string
  default     = "us-east-1" 
}


variable "enabled" {
  description = "Flag to enable or disable module resources"
  type        = bool
  default     = true
}

variable "storage_autoscaling_max_capacity" {
  description = "Maximum capacity for storage autoscaling"
  type        = number
  default     = null
}

variable "broker_volume_size" {
  description = "The size in GiB of the EBS volume for the data drive on each broker node"
  type        = number
  default     = 1000
}

variable "client_broker" {
  description = "Encryption type for data in transit between clients and brokers. Valid values: TLS, TLS_PLAINTEXT, and PLAINTEXT"
  type        = string
  default     = "TLS"
}

variable "client_sasl_scram_enabled" {
  description = "Flag to enable SASL/SCRAM client authentication"
  type        = bool
  default     = false
}

variable "client_sasl_iam_enabled" {
  description = "Flag to enable SASL/IAM client authentication"
  type        = bool
  default     = false
}

variable "jmx_exporter_enabled" {
  description = "Flag to enable JMX Exporter"
  type        = bool
  default     = false
}

variable "node_exporter_enabled" {
  description = "Flag to enable Node Exporter"
  type        = bool
  default     = false
}

variable "vpc_id" {
  description = "The VPC ID where the MSK cluster and other resources will be deployed"
  type        = string
}

variable "security_group_name" {
  description = "The name of the security group for the MSK cluster"
  type        = string
}

variable "create_security_group" {
  description = "Flag to enable creation of a new security group for the MSK cluster"
  type        = bool
  default     = true
}

variable "subnet_ids" {
  description = "A list of subnets to associate with the MSK cluster"
  type        = list(string)
}

variable "kafka_version" {
  description = "Kafka version to use for the cluster"
  type        = string
  default     = "2.6.1"
}

variable "broker_per_zone" {
  description = "Number of broker nodes per zone"
  type        = number
}

variable "broker_instance_type" {
  description = "The instance type to use for the MSK broker nodes"
  type        = string
  default     = "kafka.m5.large"
}

variable "associated_security_group_ids" {
  description = "List of additional security group IDs to associate with the MSK cluster"
  type        = list(string)
  default     = []
}

variable "public_access_enabled" {
  description = "Flag to enable public access to the MSK cluster"
  type        = bool
  default     = false
}

variable "enabled" {
  description = "Flag to enable or disable module resources"
  type        = bool
  default     = true
}

variable "enhanced_monitoring" {
  description = "The desired enhanced MSK monitoring level"
  type        = string
  default     = "DEFAULT"
}

variable "encryption_in_cluster" {
  description = "Whether data communication among broker nodes is encrypted"
  type        = bool
  default     = true
}

variable "encryption_at_rest_kms_key_arn" {
  description = "The ARN of the AWS KMS key for encrypting data at rest"
  type        = string
}

variable "client_allow_unauthenticated" {
  description = "Whether to allow unauthenticated access or not"
  type        = bool
  default     = false
}

variable "cloudwatch_logs_enabled" {
  description = "Flag to enable or disable CloudWatch logging"
  type        = bool
  default     = false
}

variable "cloudwatch_logs_log_group" {
  description = "The name of the CloudWatch log group"
  type        = string
}

variable "firehose_logs_enabled" {
  description = "Flag to enable or disable Firehose logging"
  type        = bool
  default     = false
}

variable "firehose_delivery_stream" {
  description = "The name of the Firehose delivery stream"
  type        = string
}

variable "s3_logs_enabled" {
  description = "Flag to enable or disable S3 logging"
  type        = bool
  default     = false
}

variable "s3_logs_bucket" {
  description = "The name of the S3 bucket for logs"
  type        = string
}

variable "s3_logs_prefix" {
  description = "The prefix applied to log files stored in S3"
  type        = string
}

