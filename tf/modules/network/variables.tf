variable "vpc_cidr" {
  description = "CIDR block for the VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "azs" {
  description = "AZs for "
  type        = list(string)
  default     = ["us-east-1a", "us-east-1f"]
}

variable "environment" {
  description = "Environment type for deployment"
  type        = string
  default     = "dev"
}

variable "enable_nat" {
  description = "Variable for NAT GW"
  type        = bool
  default     = false
}