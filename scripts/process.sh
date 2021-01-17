parentDirectory="$(dirname "$(PWD)")"
echo $parentDirectory
sourceDirectory="$parentDirectory/feed-data-generator/data"
destinationDirectory="$parentDirectory/story-analysis-data"
archieveDirectory="$parentDirectory/story-analysis-archieve"
backupZipName=$(date +'%Y_%m_%d_%H_%M_%S')

totalItems=0

# zip -r "$archieveDirectory/processed_data/SA_$backupZipName.zip" .
rm -R "$destinationDirectory/words"
rm -R "$destinationDirectory/gc"

python3 code/scripts/documentProcessor.py --source_directory "$sourceDirectory/content" --destination_directory $destinationDirectory --total_items $totalItems

# cd "$sourceDirectory/content"
# zip -r "$archieveDirectory/processed_feeds/CONTENT_$backupZipName.zip" .
# rm *.json
# cd "$sourceDirectory/rss"
# zip -r "$archieveDirectory/processed_feeds/RSS_$backupZipName.zip" .
# rm *.json