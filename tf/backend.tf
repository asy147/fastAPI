terraform {
  backend "s3" {
    bucket       = "asy-bucket-for-tf"
    key          = "task-manager/dev/terraform.tfstate"
    region       = "us-east-1"
    use_lockfile = true
  }
}
