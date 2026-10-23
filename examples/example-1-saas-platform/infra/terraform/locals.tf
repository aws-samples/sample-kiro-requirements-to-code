locals {
  # Every resource name starts with this. Modules receive it as name_prefix.
  name_prefix = "${var.project_name}-${var.environment}"

  # Every taggable resource gets these, merged with a per-resource Name tag.
  common_tags = merge(
    {
      Project     = var.project_name
      Environment = var.environment
      ManagedBy   = "terraform"
    },
    var.extra_tags,
  )
}
