module "network" {
  source   = "./modules/network"
  vpc_cidr = var.vpc_cidr
  azs      = var.azs
}

resource "aws_ecr_repository" "app" {
  #checkov:skip=CKV_AWS_136: Using default AES-256 encryption. KMS skipped — capstone project, nightly destroy, no compliance requirement
  name                 = "task_mgr"
  image_tag_mutability = "IMMUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }
  force_delete = true
}

resource "aws_iam_role" "exec_role" {
  name = "exec_role"

  # Terraform's "jsonencode" function converts a
  # Terraform expression result to valid JSON syntax.
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ecs-tasks.amazonaws.com"
        }
      },
    ]
  })
}

resource "aws_iam_role_policy_attachment" "exec-attach" {
  role       = aws_iam_role.exec_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

resource "aws_iam_role" "task_role" {
  name = "task_role"

  # Terraform's "jsonencode" function converts a
  # Terraform expression result to valid JSON syntax.
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ecs-tasks.amazonaws.com"
        }
      },
    ]
  })
}

resource "aws_iam_role_policy" "task_policy" {
  name = "task_policy"
  role = aws_iam_role.task_role.id

  # Terraform's "jsonencode" function converts a
  # Terraform expression result to valid JSON syntax.
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "dynamodb:GetItem",
          "dynamodb:PutItem",
          "dynamodb:UpdateItem",
          "dynamodb:DeleteItem",
          "dynamodb:Query",
          "dynamodb:Scan",
          "dynamodb:DescribeTable"
        ]
        Effect   = "Allow"
        Resource = aws_dynamodb_table.tasks-dynamodb-table.arn
      },
    ]
  })
}


resource "aws_dynamodb_table" "tasks-dynamodb-table" {
  #checkov:skip=CKV_AWS_119: Using default AES-256 encryption. KMS skipped — capstone project, nightly destroy, no compliance requirement
  #checkov:skip=CKV_AWS_28: Using default AES-256 encryption. KMS skipped — capstone project, nightly destroy, no compliance requirement
  name         = "tasks"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "task_id"

  attribute {
    name = "task_id"
    type = "S"
  }
}