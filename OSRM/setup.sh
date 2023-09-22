# wget https://download.geofabrik.de/europe/norway-latest.osm.pbf

# valhalla
docker run -t --name valhalla_gis-ops -p 8002:8002 -v ${LOCAL_WORKSPACE_FOLDER}/custom_files:/custom_files -e tile_urls=https://download.geofabrik.de/europe/norway-latest.osm.pbf ghcr.io/gis-ops/docker-valhalla/valhalla:latest
