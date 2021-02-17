source "scripts/common.sh"

archieveFunction()
{
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
}

processFeed()
{
    echo "Getting feeds:"
    cd "$parentDirectory/feed-data-generator"
    python3 feed.py
}

if [[ $archive -eq 1 ]]
    then
        archieveFunction
fi
if [[ $feed -eq 1 ]]
    then
        processFeed
fi




