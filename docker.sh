docker run -d --rm -p 80:80 -v $(pwd)/data:/app/data --env-file .env --name chlenomer chlenomer
