clean:
	@echo "=== removing old build dir ===="
	rm -rf build

image:
	make clean
	docker build -t gcr.io/zapdine/typeface-assignment-filenest-backend --no-cache .
	docker push gcr.io/zapdine/typeface-assignment-filenest-backend
	gcloud run deploy typeface-assignment-filenest-backend --region=us-east1 --project=zapdine --image gcr.io/zapdine/typeface-assignment-filenest-backend --allow-unauthenticated --port 8000
