
# Deployment to AWS S3

1. Build the project:
   ```bash
   npm run build
   ```

2. Upload the contents of the `build` folder to your S3 bucket.

3. Enable static website hosting in the S3 bucket settings.

4. Set the index document to `index.html` and error document to `index.html`.

5. Make the bucket public or use CloudFront for secure access.
