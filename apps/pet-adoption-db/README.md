## Pet Adoption DB

A project for collecting and processing pet adoption data. This project aims to discover any trends in successful pet adoptions

### Start the service

Run the command below then navigate to http://localhost:8080

```sh
docker-compose up -d
```

#### Note

- When signing in, look for `Login with username` in the container logs for sign in details.

### Restart the container

If you add new DAGs, restart the container to reload them

```sh
docker restart pet-adoption-db
```

### Deploying your project

1. **Install Terraform**: Ensure Terraform is installed on your system.

2. **Install Astronomer Terraform Provider**: Follow the Astronomer Terraform Provider documentation to set up the provider.

3. **Set Up Variables**:
    - Replace var.astro_api_key with your Astronomer API key.
    - Replace var.workspace_id with your Astronomer workspace ID.

4. **Initialize Terraform**:
```sh
terraform init
```

5. **Apply the configuration**:
```sh
terraform apply
```

6. **Verify Deployment**: Once the deployment is complete, the output will include the deployment URL. You can access your Airflow instance using this URL.
