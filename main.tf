module "aws-nuke" {
  source                         = "./modules"
  cloudwatch_schedule_expression = "cron(0 00 ? * FRI *)"
  older_than                     = "0d"
  aws_regions                    = ["us-west-2"]
  include_resources              = "ec2"
  exclude_resources              = null
  required_tags                  = "env=dev"
}
