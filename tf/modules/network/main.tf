terraform {
  required_version = ">= 1.16.4"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.0"
    }
  }
}

resource "aws_vpc" "main" {
  #checkov:skip=CKV2_AWS_11: VPC flow logs disabled to cut costs
  cidr_block = var.vpc_cidr
}

resource "aws_default_security_group" "default" {
  vpc_id = aws_vpc.main.id
}

resource "aws_internet_gateway" "igw" {
  vpc_id = aws_vpc.main.id
}

resource "aws_subnet" "public" {
  count = length(var.azs)

  vpc_id            = aws_vpc.main.id
  cidr_block        = cidrsubnet(var.vpc_cidr, 8, count.index)
  availability_zone = var.azs[count.index]
}

resource "aws_subnet" "private" {
  count             = length(var.azs)
  vpc_id            = aws_vpc.main.id
  cidr_block        = cidrsubnet(var.vpc_cidr, 8, count.index + 2)
  availability_zone = var.azs[count.index]
}

resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id
  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.igw.id
  }
}

resource "aws_route_table" "private" {
  vpc_id = aws_vpc.main.id
}

resource "aws_route_table_association" "public_route_table" {
  subnet_id      = aws_subnet.public[count.index].id
  route_table_id = aws_route_table.public.id
  count          = length(var.azs)
}

resource "aws_route_table_association" "private_route_table" {
  subnet_id      = aws_subnet.private[count.index].id
  route_table_id = aws_route_table.private.id
  count          = length(var.azs)
}