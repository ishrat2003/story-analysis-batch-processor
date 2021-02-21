source "scripts/feed.sh"

processStory()
{
  echo "Processing contents:"
  cd "$parentDirectory/story-analysis-batch-processor"
  python3 code/scripts/documentProcessor.py --source_directory "$sourceDirectory/content" --destination_directory "$destinationDirectory" --total_items $totalItems
}

if [[ $story -eq 1 ]]
    then
        processStory
fi

# zip -r "$archieveDirectory/processed_data/SA_$backupZipName.zip" .
# rm -R "$destinationDirectory/words"
# rm -R "$destinationDirectory/gc"