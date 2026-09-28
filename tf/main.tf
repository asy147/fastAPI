module "network" {
  source      = "./modules/network"
  vpc_cidr    = "10.0.0.0/16"
  azs         = ["us-east-1a", "us-east-1f"]
  environment = "dev"
  enable_nat  = false
}