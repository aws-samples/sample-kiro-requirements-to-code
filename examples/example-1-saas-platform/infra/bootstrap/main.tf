#
# Terraform state bootstrap (story I1).
#
# Creates the remote state backend used by infra/terraform: a versioned,
# KMS-encrypted S3 bucket with public access blocked. Native S3 state locking
# (use_lockfile, DEC-101) needs no DynamoDB table, so none is created here.
#
# Run once per AWS account with LOCAL state. See README.md.
#

data "aws_caller_identity" "current" {}

locals {
  name_prefix = "${var.project_name}-${var.environment}"

  # Account ID suffix keeps the bucket name globally unique.
  state_bucket_name = "${var.project_name}-${var.environment}-tfstate-${data.aws_caller_identity.current.account_id}"

  common_tags = {
    Project     = var.project_name
    Environment = var.environment
    ManagedBy   = "terraform"
    Component   = "terraform-bootstrap"
  }
}

# ---------------------------------------------------------------------------
# KMS customer-managed key for state encryption
# ---------------------------------------------------------------------------

resource "aws_kms_key" "state" {
  description             = "CMK for the ${local.name_prefix} Terraform state bucket"
  enable_key_rotation     = true
  rotation_period_in_days = 365
  deletion_window_in_days = 30

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-tfstate"
  })
}

resource "aws_kms_alias" "state" {
  name          = "alias/${local.name_prefix}-tfstate"
  target_key_id = aws_kms_key.state.key_id
}

# ---------------------------------------------------------------------------
# State bucket
# ---------------------------------------------------------------------------

resource "aws_s3_bucket" "state" {
  bucket = local.state_bucket_name

  tags = merge(local.common_tags, {
    Name = local.state_bucket_name
  })

  # State loss is unrecoverable. Removing this guard must be deliberate.
  lifecycle {
    prevent_destroy = true
  }
}

resource "aws_s3_bucket_versioning" "state" {
  bucket = aws_s3_bucket.state.id

  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "state" {
  bucket = aws_s3_bucket.state.id

  rule {
    apply_server_side_encryption_by_default {
      kms_master_key_id = aws_kms_key.state.arn
      sse_algorithm     = "aws:kms"
    }
    bucket_key_enabled = true
  }
}

resource "aws_s3_bucket_public_access_block" "state" {
  bucket = aws_s3_bucket.state.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_ownership_controls" "state" {
  bucket = aws_s3_bucket.state.id

  rule {
    object_ownership = "BucketOwnerEnforced"
  }
}

# Deny any non-TLS access (TLS 1.2+ baseline).
resource "aws_s3_bucket_policy" "state" {
  bucket = aws_s3_bucket.state.id
  policy = data.aws_iam_policy_document.state.json

  depends_on = [aws_s3_bucket_public_access_block.state]
}

data "aws_iam_policy_document" "state" {
  statement {
    sid    = "DenyInsecureTransport"
    effect = "Deny"

    principals {
      type        = "AWS"
      identifiers = ["*"]
    }

    actions = ["s3:*"]

    resources = [
      aws_s3_bucket.state.arn,
      "${aws_s3_bucket.state.arn}/*",
    ]

    condition {
      test     = "Bool"
      variable = "aws:SecureTransport"
      values   = ["false"]
    }
  }
}
