parentDirectory="$(dirname "$(PWD)")"
echo $parentDirectory
sourceDirectory="$parentDirectory/feed-data-generator/data/content"
destinationDirectory="$parentDirectory/story-analysis-data"
totalItems=1

python3 code/scripts/documentProcessor.py --source_directory $sourceDirectory --destination_directory $destinationDirectory --total_items $totalItems