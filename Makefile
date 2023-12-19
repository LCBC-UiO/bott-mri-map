.PHONY: all valhalla
# ROUTING ENGINE
VALHALLA_SENTINEL=.valhalla_updated

valhalla: ${VALHALLA_SENTINEL}
${VALHALLA_SENTINEL}:
	@if [ $$(docker ps -aq -f name=valhalla) ]; then \
		if [ ! $$(docker ps -q -f name=valhalla) ]; then \
			docker start valhalla; \
		fi \
	else \
		docker run -t --name valhalla -p 8002:8002 -v ${PWD}/VALHALLA/custom_files:/custom_files --env-file ${PWD}/valhalla.env ghcr.io/gis-ops/docker-valhalla/valhalla:latest; \
	fi
	touch ${VALHALLA_SENTINEL}

# GENERATE AND SAVE ISOCHRONES
data/output/isochrones.shp: ${VALHALLA_SENTINEL}
	@echo "Generating isochrones..."
	python src/isochrones.py

isochrones: data/output/isochrones.shp

# GENERATE AND SAVE POPULATION_MATRIX
data/output/population.shp: ${POPULATION_FILES} ${RUTER_FILES}
	@echo "Generating population matrix..."
	python src/population.py

population: data/output/population.shp

# MATRIX
RUTER_URL=https://www.ssb.no/natur-og-miljo/_attachment/375078?_ts=1685c0d0258
RUTER_ZIP=data/input/ruter/rute_1km_Norge.zip
RUTER_FILES=data/input/ruter/ruter1000m_Norge.shp

download_ruter: ${RUTER_FILES}

${RUTER_ZIP}:
	mkdir -p data/input/ruter
	curl -L ${RUTER_URL} -o $@

${RUTER_FILES}: ${RUTER_ZIP}
	unzip -o $< -d data/input/ruter && touch ${RUTER_FILES}

# POPULATION DATA
POPULATION_URL=https://www.ssb.no/natur-og-miljo/_attachment/389480?_ts=16b45e3cef0
POPULATION_ZIP=data/input/population/NOR1000M_POP_2019.zip
POPULATION_FILES=data/input/population/NOR1000M_POP_2019.csv

download_population: ${POPULATION_FILES}

${POPULATION_ZIP}:
	mkdir -p data/input/population
	curl -L ${POPULATION_URL} -o $@

${POPULATION_FILES}: ${POPULATION_ZIP}
	unzip -o $< -d data/input/population && touch ${POPULATION_FILES}


COUNTRIES_URL=https://www.naturalearthdata.com/http//www.naturalearthdata.com/download/10m/cultural/ne_10m_admin_0_map_units.zip
COUNTRIES_ZIP=data/input/countries/ne_10m_admin_0_map_units.zip
COUNTRIES_FILES=data/input/countries/ne_10m_admin_0_map_units.shp

download_countries: ${COUNTRIES_FILES}

${COUNTRIES_ZIP}:
	mkdir -p data/input/countries
	curl -L ${COUNTRIES_URL} -o $@

${COUNTRIES_FILES}: ${COUNTRIES_ZIP}
	unzip -o $< -d data/input/countries && touch ${COUNTRIES_FILES}

# Rule for creating bottmap.png from running src/bottmap.py
data/output/norway_map_with_isochrones.png: data/output/population.shp data/output/isochrones.shp ${COUNTRIES_FILES} ${RUTER_FILES} ${POPULATION_FILES}
	python src/bottmap.py

bottmap: data/output/norway_map_with_isochrones.png

########################################################################################
all: bottmap

