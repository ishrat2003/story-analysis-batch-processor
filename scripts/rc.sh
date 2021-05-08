parentDirectory="$(dirname "$(pwd)")"
echo $parentDirectory
sourceDirectory="$parentDirectory/story-analysis-data/words"
destinationDirectory="$parentDirectory/story-analysis-data"

helpFunction()
{
   echo ""
   echo "Usage: $0 -s startDate -e endDate -w wordKey"
   echo -e "\t-s: startDate ex: 2020-09-01"
   echo -e "\t-e: endDate ex: 2021-03-01"
   echo -e "\t-w: wordKey ex: plastic"
   echo "Ex: ./scripts/rc.sh -s 2020-09-01 -e 2021-03-01 -w plastic"
   exit 1 # Exit script after printing help
}

while [ "$#" -gt 0 ]; do
  case "$1" in
    -s ) startDate="$2"; shift 2 ;;
    -e ) endDate="$2"; shift 2 ;;
    -w ) wordKey="$2"; shift 2 ;;
    ? ) helpFunction ;; # Print helpFunction in case parameter is non-existent
  esac
done

echo "startDate $startDate"
echo "endDate $endDate"
echo "wordKey $wordKey"

processRC()
{
  echo "Processing RC:"
  cd "$parentDirectory/story-analysis-batch-processor"
  python3 code/scripts/rcReconstruct.py --source_directory "$sourceDirectory" --destination_directory "$destinationDirectory" --start_date $startDate --end_date $endDate --word_key $wordKey
}


processRC

