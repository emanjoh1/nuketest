# Terraform variables file

# Set cloudwatch events for shutingdown instances
# trigger lambda functuon every night at 22h00 from Monday to Friday
# cf doc : https://docs.aws.amazon.com/lambda/latest/dg/tutorial-scheduled-events-schedule-expressions.html
variable "cloudwatch_schedule_expression" {
  description = "Define the aws cloudwatch event rule schedule expression"
  type        = string
}

variable "name" {
  description = "Define name to use for lambda function, cloudwatch event and iam role"
  type        = string
  default     = "everything"
}

variable "custom_iam_role_arn" {
  description = "Custom IAM role arn for the scheduling lambda"
  type        = string
  default     = null
}

variable "kms_key_arn" {
  description = "The ARN for the KMS encryption key. If this configuration is not provided when environment variables are in use, AWS Lambda uses a default service key."
  type        = string
  default     = null
}

variable "aws_regions" {
  description = "A list of one or more aws regions where the lambda will be apply, default use the current region"
  type        = list(string)
}

variable "include_resources" {
  description = "Define the resources that will be destroyed"
  type        = string
}

variable "exclude_resources" {
  description = "Define the resources that will not be destroyed"
  type        = string
}

variable "older_than" {
  description = "Only destroy resources that were created before a certain period"
  type        = string
}

variable "tags" {
  description = "A map of tags to assign to the resources."
  type        = map(any)
  default     = null
}

variable "required_tags" {
  description = "Comma-separated list of required tags in the format key=value"
  type        = string
}
