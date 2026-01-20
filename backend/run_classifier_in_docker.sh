USE_LLM_CLASSIFIER=""
if [ "$1" = "--use-llm-classifier" ]; then
  USE_LLM_CLASSIFIER="-e USE_LLM_CLASSIFIER=true"
fi

docker build . -t aerooffers-local:latest
docker run \
  --env-file ./.env \
  $USE_LLM_CLASSIFIER \
  aerooffers-local:latest \
  sh ./run_classifier.sh
