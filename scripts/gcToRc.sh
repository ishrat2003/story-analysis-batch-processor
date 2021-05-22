parentDirectory="$(dirname "$(pwd)")"
echo $parentDirectory
sourceDirectory="$parentDirectory/story-analysis-data/gc"
destinationDirectory="$parentDirectory/story-analysis-data"

helpFunction()
{
   echo ""
   echo "Usage: $0 -g topics.json"
   echo -e "\t-g: gcFileName ex: topics.json|person_topics.json|organization_topics.json|country_topics.json"
   echo "Ex: ./scripts/gcToRc.sh -g topics.json"
   exit 1 # Exit script after printing help
}

while [ "$#" -gt 0 ]; do
  case "$1" in
    -g ) gcFileName="$2"; shift 2 ;;
    ? ) helpFunction ;; # Print helpFunction in case parameter is non-existent
  esac
done

echo "gcFileName $gcFileName"

processGCToRC()
{
  echo "Processing GC to RC:"
  cd "$parentDirectory/story-analysis-batch-processor"
  python3 code/scripts/rcBatchReconstruct.py --source_directory "$sourceDirectory/$gcFileName" --destination_directory "$destinationDirectory"
}


processGCToRC

