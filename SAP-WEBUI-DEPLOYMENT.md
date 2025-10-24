# SAP WebUI AWS Fargate Deployment

This repository contains everything needed to deploy your SAP WebUI application on AWS Fargate with an Application Load Balancer.

## Architecture Overview

The deployment creates:
- **ECS Fargate Cluster**: Serverless container hosting
- **Application Load Balancer**: High availability and SSL termination
- **ECR Repository**: Container image storage
- **CloudWatch Logs**: Application logging
- **Security Groups**: Network security
- **IAM Roles**: Secure access permissions

## Prerequisites

1. **AWS CLI configured** with appropriate permissions
2. **Docker installed** and running
3. **Sufficient AWS permissions** for:
   - ECS, ECR, EC2, CloudFormation
   - IAM role creation
   - VPC and networking resources

## Quick Start

### 1. Deploy the Application

```bash
./deploy-sap-webui.sh
```

This script will:
- Create ECR repository
- Build and push Docker image
- Deploy CloudFormation infrastructure
- Configure load balancer and ECS service

### 2. Access Your Application

After deployment completes, you'll see output like:
```
Application URL: http://sap-webui-alb-123456789.us-east-1.elb.amazonaws.com
```

Visit this URL to access your SAP WebUI application.

### 3. Update the Application

When you make changes to your application:

```bash
./update-sap-webui.sh
```

This will build a new image and trigger a rolling deployment.

### 4. Clean Up Resources

To remove all AWS resources:

```bash
./cleanup-sap-webui.sh
```

## Configuration Options

### Environment Variables

You can modify these in the deployment script:

- `REGION`: AWS region (default: us-east-1)
- `STACK_NAME`: CloudFormation stack name
- `ECR_REPO_NAME`: ECR repository name

### Scaling

To change the number of running tasks, update the CloudFormation stack:

```bash
aws cloudformation update-stack \
  --stack-name sap-webui-stack \
  --use-previous-template \
  --parameters ParameterKey=DesiredCount,ParameterValue=4 \
  --capabilities CAPABILITY_NAMED_IAM
```

### SSL Certificate

To enable HTTPS, add an SSL certificate ARN:

```bash
aws cloudformation update-stack \
  --stack-name sap-webui-stack \
  --use-previous-template \
  --parameters ParameterKey=CertificateArn,ParameterValue=arn:aws:acm:region:account:certificate/cert-id \
  --capabilities CAPABILITY_NAMED_IAM
```

## Monitoring and Troubleshooting

### View Logs

```bash
# View ECS service logs
aws logs tail /ecs/sap-webui --follow

# Check ECS service status
aws ecs describe-services --cluster sap-webui-cluster --services sap-webui-service
```

### Health Check

The application includes a health endpoint at `/health` that returns:
```json
{
  "status": "healthy",
  "service": "SAP Multi-Tenant Web UI",
  "timestamp": "2025-08-08T06:00:00.000Z"
}
```

### Common Issues

1. **Service not starting**: Check CloudWatch logs for container errors
2. **Load balancer 503 errors**: Verify security groups allow traffic on port 8080
3. **Image pull errors**: Ensure ECR permissions are correct

## Cost Optimization

- **Fargate Spot**: The template uses 80% Spot capacity for cost savings
- **Log retention**: CloudWatch logs are retained for 30 days
- **Image lifecycle**: ECR keeps only the last 10 images

## Security Features

- **Non-root container**: Application runs as non-privileged user
- **Security groups**: Restrictive network access
- **IAM roles**: Least privilege access
- **VPC**: Private networking with public load balancer

## File Structure

```
├── sap-webui/
│   ├── Dockerfile              # Container definition
│   ├── .dockerignore          # Docker build exclusions
│   ├── index.html             # Main application
│   ├── server.js              # Node.js server
│   └── package.json           # Dependencies
├── sap-webui-infrastructure.yaml  # CloudFormation template
├── sap-webui-task-definition.json # ECS task definition
├── deploy-sap-webui.sh           # Main deployment script
├── update-sap-webui.sh           # Update script
└── cleanup-sap-webui.sh          # Cleanup script
```

## Support

For issues or questions:
1. Check CloudWatch logs for application errors
2. Verify AWS service limits and quotas
3. Review security group and network configuration
4. Check ECS service events for deployment issues

## Next Steps

Consider these enhancements:
- **Custom domain**: Add Route 53 DNS and SSL certificate
- **Auto-scaling**: Configure ECS auto-scaling based on CPU/memory
- **CI/CD**: Integrate with AWS CodePipeline for automated deployments
- **Monitoring**: Add CloudWatch dashboards and alarms
- **Database**: Connect to RDS or other AWS data services
