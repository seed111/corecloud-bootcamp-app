resource "aws_dynamodb_table" "registrations" {
  name         = "${var.app_name}-registrations"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "id"

  attribute {
    name = "id"
    type = "S"
  }

  tags = {
    Name        = "${var.app_name}-registrations"
    Environment = var.environment
  }
}

output "dynamodb_table_name" {
  value = aws_dynamodb_table.registrations.name
}
