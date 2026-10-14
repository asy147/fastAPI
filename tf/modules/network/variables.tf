variable "vpc_cidr" {
  description = "CIDR block for the VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "azs" {
  description = "AZs for "
  type        = list(string)
  default     = ["us-east-1a", "us-east-1f"]
  validation {
    condition     = length(var.azs) >= 2
    error_message = "Not enough AZs for ALB"
  }
}