# ------- Global settings -------
variable "profile" {
  type        = string
  description = "Profile for AWS cloud credentials"

  # Profile is default unless explicitly specified
  default = "default"
}

variable "region" {
  type        = string
  description = "Region which Cloud resources will be created"
}

variable "prefix" {
  type        = string
  description = "Shorthand name for the environment and other assets. Used in resource descriptions"
}

# ------- SSH keypair (requires local public key) -------
variable "public_keypair_name" {
  type        = string
  description = "Name of the Public SSH key for the CDP environment"
  validation {
    condition     = length(var.public_keypair_name) > 4
    error_message = "The SSH key pair name must be greater than 4 characters."
  }
}

variable "public_keypair_key_text" {
  type        = string
  description = "Text of the Public SSH key"
  validation {
    condition     = length(var.public_keypair_key_text) > 0
    error_message = "The SSH key pair public key text must not be empty."
  }
}

# ------- CDP Environment Deployment -------
variable "deployment_type" {
  type = string

}

variable "lookup_cdp_account_ids" {
  type = bool

  description = "Auto lookup CDP Acount and External ID using CDP CLI commands"

}

# ------- Network Resources -------
variable "ingress_extra_cidrs_and_ports" {
  type = object({
    cidrs = list(string)
    ports = list(number)
  })
  description = "List of extra CIDR blocks and ports to include in Security Group Ingress rules"
}

# ------- Storage Resources -------
variable "random_id_for_bucket" {
  type = bool

}
