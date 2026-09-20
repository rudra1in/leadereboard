output "vpc_id" {
  description = "GameX VPC ID"
  value       = aws_vpc.gamex.id
}

output "vpc_cidr" {
  description = "GameX VPC CIDR block"
  value       = aws_vpc.gamex.cidr_block
}

output "public_subnet_ids" {
  description = "GameX public subnet IDs"
  value = [
    aws_subnet.public_a.id,
    aws_subnet.public_b.id
  ]
}

output "private_subnet_ids" {
  description = "GameX private subnet IDs"
  value = [
    aws_subnet.private_a.id,
    aws_subnet.private_b.id
  ]
}

output "availability_zones" {
  description = "Availability Zones used by GameX"
  value = [
    aws_subnet.public_a.availability_zone,
    aws_subnet.public_b.availability_zone
  ]
}

output "nat_gateway_id" {
  description = "GameX NAT Gateway ID"
  value       = aws_nat_gateway.gamex.id
}