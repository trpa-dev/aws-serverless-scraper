# aws-serverless-scraper
Cloud-based Web Scraper project. Entirely serverless

## About
A Python web scraper in the cloud that runs daily. Tries to commit to Free tier as much as 
possible, so the architecture may be bare bones for now. Current scope limited to Data Extraction.

### Implementation
Uses EventBridge Scheduler to set a CRON schedule to run a Lambda function daily. Docker is used to
generate an image that supports the external dependencies. For now, it uses BeautifulSoup as a 
lighter HTML scraper compared to Selenium. Selenium makes use of web browser drivers which 
inflate the image size but I'm still considering it for future enhancements. Storing scrapped data
into a Parquet format which is then published to S3. 
(add diagrams)

## Getting Started
To get a local copy up and running follow these simple example steps.

### Prerequisites
* Python 3.7+
* Docker
* NodeJS
* AWS CLI

### Installation
* Create an S3 bucket for storage (skip if you already have another one free)
* Clone the repo
* Modify S3 bucket details (bucket_name and s3_path) in the app.py script to your own S3 details
* Open a console/terminal in the project folder
* Link your console/terminal to AWS ECR
* Build the Docker image
  * Optionally, run the Docker image to test locally
* Push Docker image to AWS ECR (push commands also available in AWS ECR page)
* Create a Lambda function based on the pushed ECR image
  * Make sure to allow PutObject permissions with S3 on your Lambda role
  * Optionally, run the Lambda function to test. A file should be uploaded in your S3
* Setup EventBridge Scheduler to your liking and set your Lambda function as a target
* (add specific commands later)

## Usage
* Run app.py to test the scrape output locally
* Otherwise, just check your S3 from time to time for the outputs

## Roadmap
* Initial MVP - X
* Code Cleanup/Refactoring
* Selenium integration option to handle more complex scrapping logic
* Lambda Layers as an alternative to relying on Docker images for the module dependencies
* Config based scrapping logic to allow for modular scrapping inputs
  * Allows for different scrape targets based on environment variables or event data
  * Possibly allows for partitioned scrapping as well, to reduce memory costs in Lambda
* CFT or Terraform to handle allocation of resources

## License
Licensed under GPL-3.0.

## Contact

## Acknowledgements
