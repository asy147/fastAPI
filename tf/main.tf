module "network" {
  source   = "./modules/network"
  vpc_cidr = var.vpc_cidr
  azs      = var.azs
}

#Using default AES-256 encryption. KMS skipped — capstone project, nightly destroy, no compliance requirement.
resource "aws_ecr_repository" "app" {
  name                 = "task_mgr"
  image_tag_mutability = "IMMUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }
  force_delete = true
}