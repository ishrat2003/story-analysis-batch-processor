parentDirectory="$(dirname "$(PWD)")"
echo $parentDirectory
sourceDirectory="$parentDirectory/feed-data-generator/data"
destinationDirectory="$parentDirectory/story-analysis-data"
archieveDirectory="$parentDirectory/story-analysis-archieve"
backupZipName=$(date +'%Y_%m_%d_%H_%M_%S')

cd "$sourceDirectory/content"
totalFiles=`ls -1 | wc -l`
if [[ $totalFiles -gt 0 ]]
then
  echo "Total content files: $totalFiles"
  zip -r "$archieveDirectory/processed_content/CONTENT_$backupZipName.zip" .
  echo "Archieved content: $archieveDirectory/processed_content/CONTENT_$backupZipName.zip"
  rm *.json
  remainingTotals=`ls -1 | wc -l`
  echo "Total content files moved: $remainingTotals"
fi


cd "$sourceDirectory/rss"
totalRssFiles=`ls -1 | wc -l`
if [[ $totalRssFiles -gt 0 ]]
then
  echo "Total rss files: $totalRssFiles"
  zip -r "$archieveDirectory/processed_feeds/RSS_$backupZipName.zip" .
  echo "Archieved content: $archieveDirectory/processed_feeds/RSS_$backupZipName.zip"
  rm *.json
  remainingTotals=`ls -1 | wc -l`
  echo "Total rss files moved: $remainingTotals"
fi

echo "Archieved files:"
cd "$archieveDirectory/processed_feeds"
ls -latr
echo "Getting feeds:"
cd "$parentDirectory/feed-data-generator"
python3 feed.py

echo "Getting feeds:"
cd "$parentDirectory/story-analysis-batch-processor"
totalItems=0

echo "Processing contents:"
python3 code/scripts/documentProcessor.py --source_directory "$sourceDirectory/content" --destination_directory $destinationDirectory --total_items $totalItems


# zip -r "$archieveDirectory/processed_data/SA_$backupZipName.zip" .
# rm -R "$destinationDirectory/words"
# rm -R "$destinationDirectory/gc"