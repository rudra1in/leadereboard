# ==========================================
# GameX SQS Queues
# ==========================================

# ------------------------------------------
# Registration FIFO Queue
# ------------------------------------------

resource "aws_sqs_queue" "registration_fifo" {
  name                        = "registration_fifo.fifo"
  fifo_queue                  = true
  content_based_deduplication = true

  visibility_timeout_seconds = 60
  message_retention_seconds  = 345600

  tags = {
    Name        = "registration_fifo"
    Environment = var.environment
    Project     = "GameX"
  }
}


# ------------------------------------------
# AI Inference FIFO Queue
# ------------------------------------------

resource "aws_sqs_queue" "ai_inference_fifo" {
  name                        = "ai_inference_fifo.fifo"
  fifo_queue                  = true
  content_based_deduplication = true

  visibility_timeout_seconds = 300
  message_retention_seconds  = 345600

  tags = {
    Name        = "ai_inference_fifo"
    Environment = var.environment
    Project     = "GameX"
  }
}


# ------------------------------------------
# Reconnect Synchronization Queue
# ------------------------------------------

resource "aws_sqs_queue" "sync_reconnect_std" {
  name = "sync_reconnect_std"

  visibility_timeout_seconds = 120
  message_retention_seconds  = 345600

  tags = {
    Name        = "sync_reconnect_std"
    Environment = var.environment
    Project     = "GameX"
  }
}


# ------------------------------------------
# Notification Dispatch Queue
# ------------------------------------------

resource "aws_sqs_queue" "notification_dispatch_std" {
  name = "notification_dispatch_std"

  visibility_timeout_seconds = 120
  message_retention_seconds  = 345600

  tags = {
    Name        = "notification_dispatch_std"
    Environment = var.environment
    Project     = "GameX"
  }
}