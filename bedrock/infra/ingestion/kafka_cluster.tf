resource "aws_msk_cluster" "default" {
  count = local.enabled ? 1 : 0

  cluster_name           = module.this.id
  kafka_version          = var.kafka_version
  number_of_broker_nodes = var.broker_per_zone * length(var.subnet_ids)
  enhanced_monitoring    = var.enhanced_monitoring

  broker_node_group_info {
    instance_type   = var.broker_instance_type
    client_subnets  = var.subnet_ids
    security_groups = var.create_security_group ? concat(var.associated_security_group_ids, [module.security_group.id]) : var.associated_security_group_ids

    storage_info {
      ebs_storage_info {
        volume_size = var.broker_volume_size
      }
    }

    connectivity_info {
      public_access {
        type = var.public_access_enabled ? "SERVICE_PROVIDED_EIPS" : "DISABLED"
      }
    }
  }

  configuration_info {
    arn      = aws_msk_configuration.config[0].arn
    revision = aws_msk_configuration.config[0].latest_revision
  }

  encryption_info {
    encryption_in_transit {
      client_broker = var.client_broker
      in_cluster    = var.encryption_in_cluster
    }
    encryption_at_rest_kms_key_arn = var.encryption_at_rest_kms_key_arn
  }

  client_authentication {
    unauthenticated = var.client_allow_unauthenticated
    sasl {
      scram = var.client_sasl_scram_enabled
      iam   = var.client_sasl_iam_enabled
    }
  }

  open_monitoring {
    prometheus {
      jmx_exporter {
        enabled_in_broker = var.jmx_exporter_enabled
      }
      node_exporter {
        enabled_in_broker = var.node_exporter_enabled
      }
    }
  }

  logging_info {
    broker_logs {
      cloudwatch_logs {
        enabled   = var.cloudwatch_logs_enabled
        log_group = var.cloudwatch_logs_log_group
      }
      firehose {
        enabled         = var.firehose_logs_enabled
        delivery_stream = var.firehose_delivery_stream
      }
      s3 {
        enabled = var.s3_logs_enabled
        bucket  = var.s3_logs_bucket
        prefix  = var.s3_logs_prefix
      }
    }
  }

  lifecycle {
    ignore_changes = [
      broker_node_group_info[0].storage_info[0].ebs_storage_info[0].volume_size,
    ]
  }
  

  tags = module.this.tags
}


resource "aws_lambda_event_source_mapping" "example_kafka" {
  event_source_arn  = var.msk_cluster_arn # The ARN of your MSK cluster
  function_name     = aws_lambda_function.example.arn
  topics            = ["your-kafka-topic-name"] # Name of your Kafka topic
  starting_position = "TRIM_HORIZON"
}
