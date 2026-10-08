module "network" {
  source      = "./modules/network"
  vpc_cidr    = var.vpc_cidr
  azs         = var.azs
  environment = var.environment
  enable_nat  = var.enable_nat
}