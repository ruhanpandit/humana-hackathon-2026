export PROJECT_ID=$(gcloud config get-value project)
mkdir data
cd data
gsutil cp gs://${PROJECT_ID}-static-assets-bucket/hackathon_data.zip .
unzip hackathon_data.zip
gsutil cp -r unstructured/*.* gs://${PROJECT_ID}-static-assets-bucket/unstructured/
gsutil cp -r unstructured/call_transcripts/*.* gs://${PROJECT_ID}-static-assets-bucket/unstructured/call_transcripts/
git init
git add .
git commit -m "first commit"
git config --global user.email "ruhanpan@gmail.com"
git init
