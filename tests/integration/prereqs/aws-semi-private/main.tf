provider "aws" {
  // profile = var.profile
  region = var.region
}

// Create a SSH keypair from a local public key
resource "aws_key_pair" "deployment_keypair" {
  key_name   = var.public_keypair_name
  public_key = var.public_keypair_key_text
}

output "ssh" {
  value = {
    name        = aws_key_pair.deployment_keypair.key_name
    public_key  = var.public_keypair_key_text
    fingerprint = aws_key_pair.deployment_keypair.fingerprint
  }
  description = "Deployment SSH keypair"
}

output "identity" {
  value = {
    xaccount_role       = module.semi_private.aws_xaccount_role_arn
    datalake_admin_role = module.semi_private.aws_datalake_admin_role_arn
    idbroker_role       = module.semi_private.aws_idbroker_instance_profile_arn
    log_role            = module.semi_private.aws_log_instance_profile_arn
    ranger_audit_role   = module.semi_private.aws_ranger_audit_role_arn
  }
  description = "AWS Identities (ARN)"
}

output "storage" {
  value = {
    log_location      = module.semi_private.aws_log_location
    datalake_location = module.semi_private.aws_storage_location
  }
  description = "AWS Storage (S3)"
}

output "network" {
  value = {
    type            = module.semi_private.infra_type
    region          = module.semi_private.region
    vpc             = module.semi_private.aws_vpc_id
    private_subnets = module.semi_private.aws_private_subnet_ids
    public_subnets  = module.semi_private.aws_public_subnet_ids
  }
  description = "AWS Networking (ID)"
}

output "security" {
  value = {
    default_group = module.semi_private.aws_security_group_default_id
    knox_group    = module.semi_private.aws_security_group_knox_id
  }
  description = "AWS Security Groups (ID)"
}

output "cdp" {
  value = {
    xacccount_credential = module.semi_private.xacccount_credential_name
    environment          = module.semi_private.env_name
    datalake             = module.semi_private.datalake_name
    raz_enabled          = module.semi_private.enable_raz
    tunnel_enabled       = module.semi_private.tunnel
    analytics_enabled    = module.semi_private.workload_analytics
    endpoint_access      = module.semi_private.endpoint_access_scheme
    admin_group          = module.semi_private.cdp_iam_admin_group_name
    user_group           = module.semi_private.cdp_iam_user_group_name
    freeipa              = module.semi_private.env_freeipa
  }
  description = "CDP"
}

locals {
  test = {
    cdp = {
      xaccount_credential = module.semi_private.xacccount_credential_name
      environment         = module.semi_private.env_name
      datalake            = module.semi_private.datalake_name
      raz_enabled         = module.semi_private.enable_raz
      tunnel_enabled      = module.semi_private.tunnel
      analytics_enabled   = module.semi_private.workload_analytics
      endpoint_access     = module.semi_private.endpoint_access_scheme
      admin_group         = module.semi_private.cdp_iam_admin_group_name
      user_group          = module.semi_private.cdp_iam_user_group_name
      freeipa             = module.semi_private.env_freeipa
    }
    security = {
      default_group = module.semi_private.aws_security_group_default_id
      knox_group    = module.semi_private.aws_security_group_knox_id
    }
    network = {
      type            = module.semi_private.infra_type
      region          = module.semi_private.region
      vpc             = module.semi_private.aws_vpc_id
      private_subnets = module.semi_private.aws_private_subnet_ids
      public_subnets  = module.semi_private.aws_public_subnet_ids
    }
    storage = {
      log_location      = module.semi_private.aws_log_location
      datalake_location = module.semi_private.aws_storage_location
    }
    identity = {
      xaccount_role       = module.semi_private.aws_xaccount_role_arn
      datalake_admin_role = module.semi_private.aws_datalake_admin_role_arn
      idbroker_role       = module.semi_private.aws_idbroker_instance_profile_arn
      log_role            = module.semi_private.aws_log_instance_profile_arn
      ranger_audit_role   = module.semi_private.aws_ranger_audit_role_arn
    }
    ssh = {
      name        = aws_key_pair.deployment_keypair.key_name
      public_key  = var.public_keypair_key_text
      fingerprint = aws_key_pair.deployment_keypair.fingerprint
    }
  }
}

resource "local_file" "integration_config" {
  content  = yamlencode(local.test)
  filename = "integration_config.yml"
}

// Set up the infrastructure
module "semi_private" {
  source = "git::https://github.com/cloudera-labs/terraform-cdp-modules.git//modules/terraform-cdp-aws-pre-reqs?ref=v0.3.0"

  env_tags = {
    deploy-tool = "ansible-test"
    deployment  = var.prefix
  }

  // profile = var.profile
  region = var.region

  env_prefix = var.prefix

  // Reference the uploaded/generated keypair
  public_keypair = aws_key_pair.deployment_keypair.key_name

  deploy_cdp             = false
  deployment_type        = var.deployment_type
  lookup_cdp_account_ids = var.lookup_cdp_account_ids

  ingress_extra_cidrs_and_ports = var.ingress_extra_cidrs_and_ports

  random_id_for_bucket = var.random_id_for_bucket
}
