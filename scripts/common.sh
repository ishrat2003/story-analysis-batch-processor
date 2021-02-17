parentDirectory="$(dirname "$(PWD)")"
echo $parentDirectory
sourceDirectory="$parentDirectory/feed-data-generator/data"
destinationDirectory="$parentDirectory/story-analysis-data"
archieveDirectory="$parentDirectory/story-analysis-archieve"
backupZipName=$(date +'%Y_%m_%d_%H_%M_%S')
totalItems=0
archive=0
feed=0
story=0

helpFunction()
{
   echo ""
   echo "Usage: $0 -t totalItems -a 1 -f 1 -s 1"
   echo -e "\t-t: totalItems ex: 10"
   echo "Ex: ./scripts/process.sh -a 1 -f 1 -s 1"
   echo "Ex: ./scripts/process.sh -t 10 -s 1"
   exit 1 # Exit script after printing help
}

while [ "$#" -gt 0 ]; do
  case "$1" in
    -t ) totalItems="$2"; shift 2 ;;
    -a ) archive="$2"; shift 2 ;;
    -f ) feed="$2"; shift 2 ;;
    -s ) story="$2"; shift 2;;
    ? ) helpFunction ;; # Print helpFunction in case parameter is non-existent
  esac
done

echo "totalItems $totalItems"
echo "archive $archive"
echo "feed $feed"
echo "story $story"