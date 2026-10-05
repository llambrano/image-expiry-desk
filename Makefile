.PHONY: all data clean dashboard images

all: data clean dashboard

data:
	python scripts/generate_synthetic_data.py

clean:
	python pipeline/clean_reports.py

dashboard:
	python dashboard/build_dashboard.py

# optional: redraw the placeholder images (PNG export needs playwright)
images:
	python scripts/make_sample_images.py
